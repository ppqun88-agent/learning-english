#!/usr/bin/env python3
"""Check a pilot offline. Review records are claims, never semantic certification."""
import argparse
from collections import Counter
import json
from pathlib import Path

try:
    from .pipeline import contains, validate
except ImportError:
    from pipeline import contains, validate

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIELDS = ('lemma', 'list', 'cefr', 'pos', 'source_commit')
TEXT_FIELDS = ('pilot_id', 'target_id', *SOURCE_FIELDS, 'sense_zh',
               'selection_reason', 'usage_note_zh', 'scene_id')
FLAGS = ('selected', 'assigned', 'written', 'formal_checked', 'semantic_reviewed')


def check_pilot(selection, dialogues, targets, reviews, expected_count=100, form_approvals=None):
    """Return separate computed formal checks and recorded semantic-review status."""
    errors, review_errors = [], []
    rows = selection if isinstance(selection, list) else []
    if not isinstance(selection, list):
        errors.append('selection must be an array')
    if len(rows) != expected_count:
        errors.append(f'Expected {expected_count} selection rows, found {len(rows)}')
    if not isinstance(targets, dict):
        errors.append('targets must be an inventory keyed by target_id')
        targets = {}
    # Keep the imported source immutable. Only explicit, checked regular noun
    # plurals may extend the evidence inventory for this pilot.
    evidence_targets = {k: dict(v) for k, v in targets.items() if isinstance(v, dict)}
    approvals = [] if form_approvals is None else form_approvals
    if not isinstance(approvals, list):
        errors.append('form approvals must be an array')
        approvals = []
    approved_ids = set()
    for approval in approvals:
        if not isinstance(approval, dict) or not isinstance(approval.get('target_id'), str):
            errors.append('Each form approval needs a source target_id')
            continue
        tid = approval['target_id']
        source = targets.get(tid)
        if tid in approved_ids:
            errors.append(f'{tid}: duplicate form approval')
        approved_ids.add(tid)
        if (not isinstance(source, dict) or approval.get('lemma') != source.get('lemma') or
                source.get('pos') not in ('n.', 'n', 'noun') or
                not isinstance(approval.get('reason'), str) or not approval['reason'].strip() or
                not isinstance(source.get('lemma'), str) or
                approval.get('forms') != [source['lemma'] + 's']):
            errors.append(f'{tid}: invalid form approval; requires matching source noun, lemma+s, and reason')
            continue
        evidence_targets[tid]['approved_forms'] = list(dict.fromkeys(
            list(source.get('approved_forms', [])) + approval['forms']))
    valid_rows = []
    for index, row in enumerate(rows):
        label = f'row {index + 1}'
        if not isinstance(row, dict):
            errors.append(f'{label}: must be an object')
            continue
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in TEXT_FIELDS):
            errors.append(f'{label}: missing/non-string identity, source, or notes field')
            continue
        valid_rows.append(row)
        label = row['pilot_id']
        for flag in FLAGS:
            if type(row.get(flag)) is not bool:
                errors.append(f'{label}: {flag} must be boolean')
        for flag in ('selected', 'assigned', 'written'):
            if row.get(flag) is not True:
                errors.append(f'{label}: {flag} is not complete')
        if not isinstance(row.get('return_reason'), str):
            errors.append(f'{label}: return_reason must be a string (empty when not returned)')
        evidence = row.get('sentence_ids')
        if (not isinstance(evidence, list) or not evidence or
                any(not isinstance(s, str) or not s.strip() for s in evidence) or
                len(set(evidence)) != len(evidence)):
            errors.append(f'{label}: invalid/duplicate sentence_ids')
        source = targets.get(row['target_id'])
        if not isinstance(source, dict):
            errors.append(f'{label}: unknown source target_id')
        else:
            for field in SOURCE_FIELDS:
                if row[field] != source.get(field):
                    errors.append(f'{label}: source mismatch in {field}')
    for field in ('pilot_id', 'target_id', 'lemma'):
        values = [r[field].casefold() if field == 'lemma' else r[field] for r in valid_rows]
        if len(set(values)) != expected_count or len(set(values)) != len(values):
            errors.append(f'Expected {expected_count} distinct {field} values; duplicates or missing values')

    if not isinstance(dialogues, list):
        errors.append('dialogues must be an array of documents')
        dialogues = []
    scene_ids, assignments, doc_reports = [], {}, []
    for doc in dialogues:
        report = validate(doc, evidence_targets)
        doc_reports.append(report)
        errors.extend(f"scene {report['document_id']}: {e}" for e in report['errors'])
        if not isinstance(doc, dict) or not report['formal_pass']:
            continue
        scene = doc['id']
        scene_ids.append(scene)
        sentences = {s['id']: s['text'] for s in doc['sentences']}
        for target in doc['targets']:
            tid = target['target_id']
            assignments.setdefault(tid, []).append((scene, target['sentence_ids']))
            if len(set(target['sentence_ids'])) != len(target['sentence_ids']):
                errors.append(f'{tid}: duplicate evidence sentence IDs')
            for sid in target['sentence_ids']:
                if not any(contains(sentences[sid], form) for form in target['forms']):
                    errors.append(f'{tid}: evidence {sid} contains no approved bounded form')
    if len(set(scene_ids)) != len(scene_ids):
        errors.append('Duplicate scene IDs')
    selected_ids = {r['target_id'] for r in valid_rows}
    for tid in assignments.keys() - selected_ids:
        errors.append(f'{tid}: assigned but not selected')
    for row in valid_rows:
        assigned = assignments.get(row['target_id'], [])
        if len(assigned) != 1:
            errors.append(f"{row['pilot_id']}: target must be assigned exactly once")
        elif (assigned[0][0] != row['scene_id'] or
              assigned[0][1] != row.get('sentence_ids')):
            errors.append(f"{row['pilot_id']}: scene/evidence mapping mismatch")

    if not isinstance(reviews, list):
        review_errors.append('reviews must be an independent array of records')
        reviews = []
    review_map = {}
    pilot_ids = {r['pilot_id'] for r in valid_rows}
    for review in reviews:
        if (not isinstance(review, dict) or
                not isinstance(review.get('pilot_id'), str) or
                review.get('status') not in ('pass', 'revise') or
                not isinstance(review.get('note'), str) or not review['note'].strip()):
            review_errors.append('Each review needs pilot_id, pass/revise status, and a nonempty note')
            continue
        pid = review['pilot_id']
        if pid in review_map:
            review_errors.append(f'{pid}: duplicate review')
        review_map[pid] = review
        if pid not in pilot_ids:
            review_errors.append(f'{pid}: review does not match a selected pilot ID')
    for row in valid_rows:
        pid = row['pilot_id']
        if pid not in review_map:
            review_errors.append(f'{pid}: independent review missing')
        elif review_map[pid]['status'] == 'revise':
            review_errors.append(f'{pid}: review requests revision')
        if row.get('semantic_reviewed') is True and pid not in review_map:
            review_errors.append(f'{pid}: semantic_reviewed flag has no independent record')
    counts = Counter(r['status'] for pid, r in review_map.items() if pid in pilot_ids)
    formal_pass = not errors
    review_complete = not review_errors and len(review_map) == expected_count
    return {
        'passed': formal_pass and review_complete,
        'formal_pass': formal_pass,
        'formal_document_count': sum(r['formal_pass'] for r in doc_reports),
        'document_count': len(doc_reports),
        'selected_count': len(rows),
        'distinct_lemma_count': len({r['lemma'].casefold() for r in valid_rows}),
        'assigned_once_count': sum(len(v) == 1 for k, v in assignments.items() if k in selected_ids),
        'stored_formal_checked_count': sum(r.get('formal_checked') is True for r in valid_rows),
        'review_record_count': len(review_map),
        'semantic_review_pass_count': counts['pass'],
        'semantic_review_revise_count': counts['revise'],
        'review_records_complete': review_complete,
        'semantic_status': 'NOT CERTIFIED: independent review records are reported claims; this checker only validates structure, source identity, assignment and lexical evidence.',
        'errors': errors,
        'review_errors': review_errors,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot-dir', type=Path, default=ROOT/'pilots/oxford-100-v1')
    parser.add_argument('--targets', type=Path, default=ROOT/'build/targets.jsonl')
    args = parser.parse_args(argv)
    try:
        def read(path):
            return json.loads(path.read_text(encoding='utf-8'))
        inventory = [json.loads(line) for line in args.targets.read_text(encoding='utf-8').splitlines() if line.strip()]
        targets = {r['target_id']: r for r in inventory}
        if len(targets) != len(inventory):
            raise ValueError('Duplicate source target IDs')
        selection = read(args.pilot_dir/'selection.json')
        dialogues = [read(p) for p in sorted((args.pilot_dir/'dialogues').glob('*.json'))]
        review_path = args.pilot_dir/'reviews.json'
        reviews = read(review_path) if review_path.exists() else []
        approval_path = args.pilot_dir/'form-approvals.json'
        approvals = read(approval_path) if approval_path.exists() else []
        result = check_pilot(selection, dialogues, targets, reviews, form_approvals=approvals)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'passed': False, 'formal_pass': False, 'errors': [str(exc)], 'semantic_status': 'NOT CERTIFIED'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
