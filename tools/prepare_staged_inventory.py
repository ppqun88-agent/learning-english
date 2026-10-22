#!/usr/bin/env python3
"""Rebuild private stage allocation from the verified local source and frozen pilot.

This is an allocation, not semantic classification or coverage. Detailed source
inventories stay under ignored build/; original authored usages are published
only as reviewed corpus artifacts.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = '3043da14627ed3c6168b598479bc110ce6b34736'
LEVELS = {level: i for i, level in enumerate(('A1', 'A2', 'B1', 'B2', 'C1', 'C2'))}


def allocate(rows, pilot, phase_count=12, part_count=3):
    if phase_count < 1 or part_count < 1:
        raise ValueError('Phase and part counts must be positive')
    groups = defaultdict(list)
    ids = set()
    for row in rows:
        if row['source_commit'] != SOURCE_COMMIT:
            raise ValueError('Source commit mismatch; reimport the pinned source')
        if row['target_id'] in ids:
            raise ValueError('Duplicate source target ID')
        ids.add(row['target_id'])
        if row['cefr'] not in LEVELS:
            raise ValueError('Unknown CEFR: ' + row['cefr'])
        groups[row['lemma']].append(row)
    pilot_forms = {r['lemma'] for r in pilot}
    if len(pilot_forms) != len(pilot) or not pilot_forms <= set(groups):
        raise ValueError('Pilot forms must be unique and present in source')
    source_by_id = {r['target_id']: r for r in rows}
    for row in pilot:
        source = source_by_id.get(row['target_id'])
        if not source or any(source[k] != row[k] for k in ('lemma', 'pos', 'source_commit')):
            raise ValueError('Pilot provenance mismatch')
    remaining = sorted(set(groups) - pilot_forms, key=lambda w: (
        min(LEVELS[r['cefr']] for r in groups[w]), w.lower(), w))
    phases, parts = [], {}
    for i in range(phase_count):
        chunk = remaining[i * len(remaining) // phase_count:(i + 1) * len(remaining) // phase_count]
        pid = f'phase-{i + 1:02}'
        phases.append({'id': pid, 'forms': chunk})
        for j in range(part_count):
            forms = chunk[j * len(chunk) // part_count:(j + 1) * len(chunk) // part_count]
            parts[(pid, j + 1)] = [
                {'lemma': w, 'candidates': [
                    {k: r[k] for k in ('target_id', 'pos', 'cefr')} for r in sorted(groups[w], key=lambda r: r['target_id'])]}
                for w in forms]
    return {'source_commit': SOURCE_COMMIT, 'pilot_forms': sorted(pilot_forms),
            'phases': phases, 'deferred': []}, parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--targets', type=Path, default=ROOT / 'build/targets.jsonl')
    parser.add_argument('--pilot', type=Path, default=ROOT / 'pilots/oxford-100-v1/selection.json')
    parser.add_argument('--build-dir', type=Path, default=ROOT / 'build')
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.targets.read_text().splitlines() if line.strip()]
    inventory, parts = allocate(rows, json.loads(args.pilot.read_text()))
    if len(rows) != 6187 or len({r['lemma'] for r in rows}) != 5062 or len(inventory['pilot_forms']) != 100:
        raise ValueError('Pinned full-source/pilot counts changed; do not silently reallocate')
    args.build_dir.mkdir(parents=True, exist_ok=True)
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    write(args.build_dir / 'staged-inventory.json', inventory)
    for (pid, part), value in parts.items():
        write(args.build_dir / 'staged-assignments' / pid / f'part-{part}.json', value)
    print(json.dumps({'source_forms': 5062, 'source_records': 6187, 'pilot_forms': 100,
        'remaining_forms': sum(len(p['forms']) for p in inventory['phases']),
        'phase_sizes': {p['id']: len(p['forms']) for p in inventory['phases']}}))


if __name__ == '__main__':
    main()
