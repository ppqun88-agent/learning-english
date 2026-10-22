#!/usr/bin/env python3
"""Attach source/sense identities and merge authored scenarios BEFORE review.

Never invent review verdicts. Any change invalidates exact-byte review hashes.
Validate the entire intended batch before writing any changed artifacts.
"""
import argparse
import json
from pathlib import Path
try:
    from .staged_corpus import merge_taxonomy, read_json
except ImportError:
    from staged_corpus import merge_taxonomy, read_json

ROOT = Path(__file__).resolve().parents[1]

def write(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)

def prepare_documents(documents, source_rows, base, extension):
    sources = {}
    for row in source_rows:
        tid = row['target_id']
        if tid in sources:
            raise ValueError(f'Duplicate source target ID {tid}')
        sources[tid] = row
    merged, errors = merge_taxonomy(base, extension)
    if errors:
        raise ValueError('; '.join(errors))
    # Work on independent copies; the caller can safely abandon a failed plan.
    extension = json.loads(json.dumps(extension))
    scenarios = {s['id']: s for s in merged['scenarios']}
    topics = {t['id'] for t in merged['topics']}
    prepared = {}
    for name, original in documents.items():
        d = json.loads(json.dumps(original))
        if d['topic_id'] not in topics:
            raise ValueError(f'Unknown topic {d["topic_id"]}')
        s = dict(d['scenario'], topic_id=d['topic_id'])
        old = scenarios.get(s['id'])
        if old is not None and old != s:
            raise ValueError(f'Conflicting scenario {s["id"]}; reconcile explicitly')
        if old is None:
            extension['scenarios'].append(s)
            scenarios[s['id']] = s
        for t in d['targets']:
            src = sources[t['target_id']]
            if (t['lemma'], t['pos']) != (src['lemma'], src['pos']):
                raise ValueError(f'Source mismatch {t["target_id"]}')
            t.setdefault('sense_id', f'sense-staged-{t["target_id"]}-{d["id"]}')
            for key in ('cefr', 'list', 'source_commit'):
                if key in t and t[key] != src[key]:
                    raise ValueError(f'Conflicting {key} provenance for {t["target_id"]}')
                t[key] = src[key]
        scope = 'oxford-remaining-staged-v1'
        if 'scope_version' in d and d['scope_version'] != scope:
            raise ValueError('Conflicting scope version')
        d['scope_version'] = scope
        if 'content_version' in d and (type(d['content_version']) is not int or d['content_version'] < 1):
            raise ValueError('Invalid content version')
        d.setdefault('content_version', 1)
        prepared[name] = d
    extension['scenarios'].sort(key=lambda s:s['id'])
    return prepared, extension

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase')
    args = p.parse_args()
    root = ROOT / 'corpus/staged-v1'
    if not args.phase.startswith('phase-') or not args.phase[6:].isdigit():
        raise ValueError('Expected phase-NN')
    rows = [json.loads(line) for line in (ROOT/'build/targets.jsonl').read_text().splitlines() if line.strip()]
    files = sorted((root/args.phase).glob('p*.json'))
    if not files:
        raise ValueError('No authored dialogue files')
    prepared, taxonomy = prepare_documents(
        {path: read_json(path) for path in files}, rows,
        read_json(ROOT/'data/scene-taxonomy.json'), read_json(root/'taxonomy.json'))
    for path, d in prepared.items():
        write(path, d)
    write(root/'taxonomy.json', taxonomy)
    print(f'Integrated {len(files)} dialogues; independent review still required')

if __name__ == '__main__': main()
