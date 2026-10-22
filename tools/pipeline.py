#!/usr/bin/env python3
"""Offline deterministic import and form evidence checks. No model calls."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def contains(text, form):
    # Capitalized lexical forms remain case-sensitive (May != may).
    flags = 0 if any(c.isupper() for c in form) else re.IGNORECASE
    return bool(re.search(r'(?<!\w)'+re.escape(form)+r'(?!\w)', text, flags))

def import_source(source, output):
    manifest = read(ROOT/'provenance/wordlists.json')
    source, output = Path(source), Path(output)
    for path, expected in manifest['files'].items():
        actual = hashlib.sha256((source/path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Source hash mismatch: '+path)
    defs = read(ROOT/'data/reference/ecdict-definitions.json')
    if hashlib.sha256((ROOT/'data/reference/ecdict-definitions.json').read_bytes()).hexdigest() != manifest['files']['data/en/definitions.json']:
        raise ValueError('Vendored definitions hash mismatch')
    raw = read(source/'data/en/archive/Oxford.json')
    rows=[]
    for group in ('Oxford3000','Oxford5000'):
        for lemma, levels in raw[group].items():
            for level, records in levels.items():
                for rec in records:
                    key=[group,lemma,level,rec]
                    rows.append({'target_id':'ox-'+hashlib.sha256(json.dumps(key,ensure_ascii=False).encode()).hexdigest()[:16], 'lemma':lemma,'list':group,'cefr':level,'source_record':rec,'pos':rec[0], 'sense':None,'sense_status':'pending','approved_forms':[lemma], 'phonetic_raw':defs.get(lemma,[''])[0], 'definition_raw':defs.get(lemma,['',[]])[1], 'source_commit':manifest['commit']})
    rows.sort(key=lambda r:r['target_id'])
    assert len({r['target_id'] for r in rows}) == len(rows)
    output.mkdir(parents=True,exist_ok=True)
    (output/'targets.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    summary={'source_commit':manifest['commit'],'unique_lemmas':len({r['lemma'] for r in rows}),'source_target_records':len(rows),'missing_phonetics':len({r['lemma'] for r in rows if not r['phonetic_raw']}),'scope_status':'provisional UK/US union, not learner-approved scope','sense_status':'all pending; raw gloss is not a selected sense'}
    write(output/'import-report.json',summary)
    return summary

def validate(doc, targets):
    errors=[]
    def invalid(message):
        return {'document_id':None,'formal_pass':False,'errors':[message],'semantic_status':'NOT VERIFIED'}
    if not isinstance(doc,dict): return invalid('Document must be an object')
    if not isinstance(doc.get('id'),str) or not doc['id'].strip(): return invalid('Document id must be a nonempty string')
    if not isinstance(doc.get('sentences'),list) or not isinstance(doc.get('targets'),list): return invalid('sentences and targets must be arrays')
    sentences=doc['sentences']
    for sentence in sentences:
        if not isinstance(sentence,dict) or any(not isinstance(sentence.get(k),str) or not sentence[k].strip() for k in ('id','speaker','text')):
            return invalid('Each sentence needs nonempty string id, speaker, text')
    for target in doc['targets']:
        if not isinstance(target,dict) or any(not isinstance(target.get(k),str) or not target[k].strip() for k in ('target_id','lemma')):
            return invalid('Each target needs nonempty string target_id and lemma')
        if any(not isinstance(target.get(k),list) or any(not isinstance(x,str) or not x.strip() for x in target[k]) for k in ('forms','sentence_ids')):
            return invalid('forms and sentence_ids must be arrays of nonempty strings')
    ids=[s.get('id') for s in sentences]
    if not doc.get('id') or not ids or None in ids or len(set(ids))!=len(ids): errors.append('Missing/duplicate document or sentence IDs')
    sm={s.get('id'):s.get('text','') for s in sentences}
    tids=[t.get('target_id') for t in doc.get('targets',[])]
    if not tids or len(tids)!=len(set(tids)): errors.append('Empty/duplicate target IDs')
    for t in doc.get('targets',[]):
        tid=t.get('target_id'); ref=targets.get(tid)
        if ref is None:
            errors.append(f'{tid}: unknown target ID'); continue
        if t.get('lemma')!=ref['lemma']: errors.append(f'{tid}: lemma mismatch')
        forms=t.get('forms',[])
        if not forms or any(not f or f not in ref['approved_forms'] for f in forms): errors.append(f'{tid}: unapproved/empty forms')
        evidence=t.get('sentence_ids',[])
        if not evidence or any(i not in sm for i in evidence): errors.append(f'{tid}: invalid sentence references')
        elif not any(contains(sm[i],f) for i in evidence for f in forms if f): errors.append(f'{tid}: no bounded form in evidence')
    return {'document_id':doc.get('id'),'formal_pass':not errors,'errors':errors,'semantic_status':'NOT VERIFIED: independent reviewer must check POS, sense, naturalness and evidence. Reviews in this file are claims, not certification.'}

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('import'); i.add_argument('--source-dir',required=True); i.add_argument('--output',default='build')
    v=sub.add_parser('validate'); v.add_argument('--dialogues',required=True); v.add_argument('--targets',default='build/targets.jsonl')
    a=p.parse_args()
    if a.cmd=='import': result=import_source(a.source_dir,a.output)
    else:
        rows=[json.loads(l) for l in Path(a.targets).read_text().splitlines() if l.strip()]
        if len({r['target_id'] for r in rows})!=len(rows): raise ValueError('Duplicate target IDs in inventory')
        result=validate(read(a.dialogues),{r['target_id']:r for r in rows})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if a.cmd=='validate' and not result['formal_pass']: raise SystemExit(1)
if __name__=='__main__': main()
