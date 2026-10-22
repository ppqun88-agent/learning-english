#!/usr/bin/env python3
"""Validate and render sense-specific navigation; never certify semantic coverage."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'pilots/oxford-100-v1'


def check_shape(value, schema, path='$'):
    """Validate the small JSON Schema vocabulary used by our two checked-in schemas.

    This is not a general-purpose JSON Schema engine. No network or dependencies.
    """
    errors = []
    if 'oneOf' in schema:
        if sum(not check_shape(value, option, path) for option in schema['oneOf']) != 1:
            errors.append(f'{path}: must match exactly one link shape')
        return errors
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        errors.append(f'{path}: incorrect constant')
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str}
    if kind and not isinstance(value, types[kind]):
        return errors + [f'{path}: expected {kind}']
    if kind == 'string' and len(value.strip()) < schema.get('minLength', 0):
        errors.append(f'{path}: empty text')
    if kind == 'object':
        if set(schema.get('required', [])) - set(value):
            errors.append(f'{path}: missing required fields')
        if schema.get('additionalProperties') is False and set(value) - set(schema['properties']):
            errors.append(f'{path}: unknown fields')
        for key, child in schema['properties'].items():
            if key in value:
                errors.extend(check_shape(value[key], child, path+'.'+key))
    if kind == 'array':
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{path}: empty array')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errors.append(f'{path}: duplicate array items')
        for i, item in enumerate(value):
            errors.extend(check_shape(item, schema['items'], f'{path}[{i}]'))
    return errors


def validate_classification(taxonomy, classification, selection, dialogues):
    """Relational checks after the JSON Schema shape contract. No repetition quota."""
    errors = []
    for name, value in [('scene-taxonomy', taxonomy), ('classification', classification)]:
        schema = json.loads((ROOT/'schemas'/f'{name}.schema.json').read_text(encoding='utf-8'))
        errors.extend(check_shape(value, schema, name))
    if errors:
        return {'passed': False, 'errors': errors}
    def require(condition, message):
        if not condition:
            errors.append(message)
    def index(items, key, label):
        result = {}
        for item in items:
            require(item[key] not in result, f'duplicate {label}: {item[key]}')
            result[item[key]] = item
        return result
    try:
        require(taxonomy['schema_version'] == classification['schema_version'] == 1, 'unsupported version')
        require(classification['scope'] == 'oxford-100-v1', 'incorrect pilot scope')
        topics = index(taxonomy['topics'], 'id', 'topic')
        scenarios = index(taxonomy['scenarios'], 'id', 'scenario')
        docs = index(dialogues, 'id', 'dialogue')
        rows = index(selection, 'pilot_id', 'selection')
        targets = {r['target_id']: r for r in selection}
        assignments = index(classification['dialogues'], 'dialogue_id', 'dialogue assignment')
        senses = index(classification['senses'], 'sense_id', 'sense')
        require(set(assignments) == set(docs), 'dialogue assignments must cover exactly the pilot documents')
        for topic in topics.values():
            require(all(isinstance(topic[k], str) and topic[k].strip() for k in ('id','label_zh','scope_zh')), 'invalid topic text')
        for scenario in scenarios.values():
            require(scenario['topic_id'] in topics, 'unknown topic')
            require(all(isinstance(scenario[k], str) and scenario[k].strip() for k in ('id','label_zh','goal_zh')), 'invalid scenario text')
        for assignment in assignments.values():
            ids = assignment['scenario_ids']
            require(bool(ids) and len(ids) == len(set(ids)) and set(ids) <= set(scenarios), 'invalid dialogue scenarios')
        selected_senses = {}
        evidence_count = 0
        suggested_count = 0
        for sense in senses.values():
            tid = sense['target_id']
            require(tid in targets, 'unknown source target')
            require(all(isinstance(sense[k], str) and sense[k].strip() for k in ('sense_id','target_id','lemma','pos','sense_zh')), 'invalid sense text')
            if tid in targets:
                require(all(sense[k] == targets[tid][k] for k in ('lemma','pos')), 'source lemma/pos mismatch')
            pid = sense.get('pilot_id')
            if pid is not None:
                require(pid in rows and pid not in selected_senses, 'unknown or duplicate selected sense')
                selected_senses[pid] = sense
                if pid in rows:
                    require(all(sense[k] == rows[pid][k] for k in ('target_id','lemma','pos','sense_zh')), 'selected sense mismatch')
            links = sense['scenario_links']
            require(bool(links), 'sense needs a scenario link')
            require(len({l['scenario_id'] for l in links}) == len(links), 'duplicate sense-scenario link')
            baseline_found = False
            for link in links:
                sid = link['scenario_id']
                require(sid in scenarios, 'unknown scenario')
                if link['status'] == 'suggested':
                    suggested_count += 1
                    require(isinstance(link.get('rationale_zh'), str) and bool(link['rationale_zh'].strip()), 'suggestion needs rationale')
                    require('evidence' not in link, 'suggested link cannot claim evidence')
                    continue
                require(link['status'] == 'attested', 'invalid link status')
                require(pid in rows, 'additional senses are suggested-only until sense-specific evidence is reviewed')
                require('rationale_zh' not in link, 'attested link cannot use suggestion rationale')
                evidence = link['evidence']
                require(bool(evidence), 'attested link needs evidence')
                seen_docs = set()
                for occurrence in evidence:
                    did = occurrence['dialogue_id']
                    require(did not in seen_docs, 'duplicate dialogue evidence')
                    seen_docs.add(did)
                    require(did in docs and did in assignments, 'unknown evidence dialogue')
                    sentence_ids = occurrence['sentence_ids']
                    require(bool(sentence_ids) and len(sentence_ids) == len(set(sentence_ids)), 'invalid evidence sentence IDs')
                    if did not in docs or did not in assignments:
                        continue
                    require(sid in assignments[did]['scenario_ids'], 'evidence scenario not assigned to dialogue')
                    mapped = [t for t in docs[did]['targets'] if t['target_id'] == tid]
                    require(len(mapped) == 1 and set(sentence_ids) <= set(mapped[0]['sentence_ids']), 'evidence missing from original target mapping')
                    require(set(sentence_ids) <= {s['id'] for s in docs[did]['sentences']}, 'unknown evidence sentence')
                    if pid in rows and did == rows[pid]['scene_id'] and set(sentence_ids) == set(rows[pid]['sentence_ids']):
                        baseline_found = True
                    evidence_count += 1
            if pid is not None:
                require(baseline_found, f'{pid}: original selected evidence not preserved')
        require(set(selected_senses) == set(rows), 'every selected sense must be classified exactly once')
        return {'passed': not errors, 'selected_sense_count': len(selected_senses), 'dialogue_count': len(assignments),
                'topic_count': len(topics), 'scenario_count': len(scenarios), 'attested_evidence_link_count': evidence_count,
                'suggested_link_count': suggested_count, 'errors': errors,
                'semantic_status': 'NOT CERTIFIED: suggested links are planning only; attested references preserve existing mappings, not new semantic review.'}
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        return {'passed': False, 'errors': errors + ['Malformed classification: ' + str(exc)]}


def render(taxonomy, classification, dialogues):
    topics = {t['id']: t for t in taxonomy['topics']}
    scenarios = {s['id']: s for s in taxonomy['scenarios']}
    docs = {d['id']: d for d in dialogues}
    def doc_link(did):
        return f"[{docs[did]['title_zh']}](dialogues.md#{docs[did]['title_zh']}-{did})"
    lines = ['# 首批情景分类与单词反查', '',
             '范围：现有 100 个目标词形、100 个已选义项、10 篇对话。不是全量 5,000 词分类。', '',
             '按主题找情景；按单词找具体义项和原句。建议关联不是已有用例，不计覆盖，不要求补写或重复。', '',
             '结构与扩展规则见 [分类规范](../../docs/scene-classification.md)。本页由 tools/classify_pilot.py 生成。', '',
             '## 主题与具体情景', '']
    for topic in taxonomy['topics']:
        lines += ['### ' + topic['label_zh'], '', topic['scope_zh'], '']
        for scenario in taxonomy['scenarios']:
            if scenario['topic_id'] != topic['id']:
                continue
            matches = [a['dialogue_id'] for a in classification['dialogues'] if scenario['id'] in a['scenario_ids']]
            lines += [f"- {scenario['label_zh']}（{scenario['id']}）：{scenario['goal_zh']}。", '  - 对话：' + '、'.join(doc_link(did) for did in matches)]
        lines += ['']
    lines += ['## 单词 → 义项 → 情景 → 对话原句', '', '按字母排序；来源目标 ID 保留在 classification.json 和 selection.json 中。', '']
    for sense in sorted(classification['senses'], key=lambda s: (s['lemma'].casefold(),s['pos'],s['sense_id'])):
        lines += [f"### {sense['lemma']} · {sense['pos']} · {sense['sense_zh']}", '', f"义项 ID：{sense['sense_id']}；来源目标：{sense['target_id']}。"]
        for link in sense['scenario_links']:
            scenario = scenarios[link['scenario_id']]
            category = topics[scenario['topic_id']]['label_zh'] + ' / ' + scenario['label_zh']
            if link['status'] == 'suggested':
                lines += [f"- 建议关联（未覆盖）：{category}。{link['rationale_zh']}"]
            else:
                for occurrence in link['evidence']:
                    did = occurrence['dialogue_id']
                    lines += [f"- 已有目标用例：{category} → {doc_link(did)}。"]
                    sentences = {s['id']:s for s in docs[did]['sentences']}
                    lines += [f"  - {sid}：{sentences[sid]['text']}" for sid in occurrence['sentence_ids']]
        lines += ['']
    return '\n'.join(lines) + '\n'


def load():
    def read(p): return json.loads(p.read_text(encoding='utf-8'))
    return (read(ROOT/'data/scene-taxonomy.json'), read(PILOT/'classification.json'),
            read(PILOT/'selection.json'), [read(p) for p in sorted((PILOT/'dialogues').glob('*.json'))])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the readable index after validation')
    args = parser.parse_args()
    try:
        taxonomy, classification, selection, dialogues = load()
        result = validate_classification(taxonomy, classification, selection, dialogues)
        if result['passed']:
            rendered = render(taxonomy, classification, dialogues)
            path = PILOT/'classification.md'
            if args.write:
                path.write_text(rendered, encoding='utf-8')
            elif not path.exists() or path.read_text(encoding='utf-8') != rendered:
                result['errors'].append('Readable index is stale; run with --write')
                result['passed'] = False
    except (OSError, ValueError) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
