#!/usr/bin/env python3
"""Validate staged original dialogues, recorded reviews and source dispositions.

Offline and deterministic. A valid review is an attributed claim, not a machine
proof of meaning, naturalness, reviewer independence or language mastery.
The complete source inventory stays in ignored build/; output is aggregate-only
except for the source references attached to original authored uses.
"""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import quote

try:
    from .pipeline import contains, validate
    from .check_pilot import check_pilot
except ImportError:
    from pipeline import contains, validate
    from check_pilot import check_pilot

ROOT = Path(__file__).resolve().parents[1]
NOTICE = ('NOT CERTIFIED: source identity, lexical evidence and review-record bindings '
          'are checked mechanically; semantic judgments and reviewer independence '
          'are recorded claims, not proven by this checker.')
PHASE_ID = re.compile(r'phase-[0-9]{2,}\Z')
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, nonempty=True):
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(text(v) for v in value) and len(set(value)) == len(value))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    # Duplicate JSON keys can conceal a changed review or target and are rejected.
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'{path}: duplicate JSON key {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)


def merge_taxonomy(base, extension=None):
    """Merge an additive taxonomy without silently replacing existing meanings."""
    errors, merged = [], {'schema_version': 1, 'topics': [], 'scenarios': []}
    indexes = {'topics': {}, 'scenarios': {}}
    for name, taxonomy in [('base', base), ('extension', extension)]:
        if taxonomy is None and name == 'extension':
            continue
        if not isinstance(taxonomy, dict) or type(taxonomy.get('schema_version')) is not int or taxonomy['schema_version'] != 1:
            errors.append(f'{name} taxonomy: expected schema_version 1 object')
            continue
        for kind, fields in [('topics', ('id', 'label_zh', 'scope_zh')),
                             ('scenarios', ('id', 'topic_id', 'label_zh', 'goal_zh'))]:
            values = taxonomy.get(kind)
            if not isinstance(values, list):
                errors.append(f'{name} taxonomy: {kind} must be an array')
                continue
            seen = set()
            for row in values:
                if not isinstance(row, dict) or any(not text(row.get(k)) for k in fields):
                    errors.append(f'{name} taxonomy: invalid {kind} entry')
                    continue
                key = row['id']
                if key in seen:
                    errors.append(f'{name} taxonomy: duplicate {kind} ID {key}')
                seen.add(key)
                if key in indexes[kind] and indexes[kind][key] != row:
                    errors.append(f'{name} taxonomy: conflicting {kind} definition {key}')
                else:
                    indexes[kind][key] = row
    for scenario in indexes['scenarios'].values():
        if scenario['topic_id'] not in indexes['topics']:
            errors.append(f"taxonomy: unknown topic for {scenario['id']}")
    for kind in indexes:
        merged[kind] = [indexes[kind][key] for key in sorted(indexes[kind])]
    return merged, errors


def check_inventory(inventory, source_targets, expected_commit=None, expected_pilot_forms=None):
    """Check a disjoint, exhaustive partition of exact source spellings."""
    errors, sources = [], {}
    if not isinstance(source_targets, dict) or not source_targets:
        errors.append('source targets must be a nonempty target_id mapping')
        source_targets = {}
    for key, row in source_targets.items():
        if (not text(key) or not isinstance(row, dict)
                or any(not text(row.get(k)) for k in ('target_id', 'lemma', 'pos', 'source_commit'))
                or row.get('target_id') != key):
            errors.append('source targets: invalid identity, lemma, POS or source_commit')
            continue
        sources[key] = row
    source_forms = {row['lemma'] for row in sources.values()}
    source_commits = {row['source_commit'] for row in sources.values()}
    if not isinstance(inventory, dict):
        return {}, {}, ['inventory must be an object'] + errors
    if (not text(inventory.get('source_commit')) or source_commits != {inventory.get('source_commit')}
            or (expected_commit is not None and inventory.get('source_commit') != expected_commit)):
        errors.append('inventory source_commit must match the pinned source and every source record')
    pilot = inventory.get('pilot_forms')
    if not strings(pilot, False):
        errors.append('inventory pilot_forms must be unique nonempty strings')
        pilot = []
    if expected_pilot_forms is not None and set(pilot) != set(expected_pilot_forms):
        errors.append('inventory pilot_forms differs from the preserved pilot selection')
    owners = {lemma: 'pilot' for lemma in pilot}
    phase_forms = {}
    phases = inventory.get('phases')
    if not isinstance(phases, list) or not phases:
        errors.append('inventory phases must be a nonempty array')
        phases = []
    for row in phases:
        if not isinstance(row, dict) or not text(row.get('id')) or not PHASE_ID.fullmatch(row['id']):
            errors.append('inventory: invalid phase ID')
            continue
        pid, forms = row['id'], row.get('forms')
        if pid in phase_forms:
            errors.append(f'{pid}: duplicate inventory phase')
        if not strings(forms):
            errors.append(f'{pid}: forms must be a nonempty array of unique strings')
            forms = []
        phase_forms[pid] = set(forms)
        for lemma in forms:
            if lemma in owners:
                errors.append(f'inventory partition overlap: {lemma}')
            owners[lemma] = pid
    deferred = inventory.get('deferred')
    if not isinstance(deferred, list):
        errors.append('inventory deferred must be an array')
        deferred = []
    for row in deferred:
        if not isinstance(row, dict) or not text(row.get('lemma')) or not text(row.get('reason')):
            errors.append('inventory deferrals require lemma and nonempty reason')
            continue
        lemma = row['lemma']
        if lemma in owners:
            errors.append(f'inventory partition overlap: {lemma}')
        owners[lemma] = 'deferred'
    if set(owners) != source_forms:
        errors.append('inventory is not an exhaustive exact source partition '
                      f'(missing {len(source_forms - set(owners))}, unknown {len(set(owners) - source_forms)})')
    counts = {'source_commit': inventory.get('source_commit'), 'source_form_count': len(source_forms),
              'source_target_record_count': len(sources), 'pilot_reserved_form_count': len(pilot),
              'phase_allocated_form_count': sum(map(len, phase_forms.values())),
              'inventory_deferred_form_count': len(deferred)}
    return phase_forms, counts, errors


def check_document(doc, sources, allowed_forms, taxonomy):
    errors = []
    if not isinstance(doc, dict):
        return ['dialogue must be an object']
    for key in ('id', 'title_zh', 'topic_id', 'context_zh', 'author'):
        if not text(doc.get(key)):
            errors.append(f'dialogue requires nonempty {key}')
    participants = doc.get('participants')
    if not strings(participants):
        errors.append('participants must be unique nonempty speaker-name strings')
        participants = []
    scenario = doc.get('scenario')
    topics = {v['id']: v for v in taxonomy['topics']}
    scenarios = {v['id']: v for v in taxonomy['scenarios']}
    if not text(doc.get('topic_id')) or doc['topic_id'] not in topics:
        errors.append('unknown topic_id')
    if not isinstance(scenario, dict) or any(not text(scenario.get(k)) for k in ('id', 'label_zh', 'goal_zh')):
        errors.append('scenario requires id, label_zh and goal_zh')
    elif scenario['id'] not in scenarios:
        errors.append('unknown scenario ID')
    else:
        registered = scenarios[scenario['id']]
        if registered['topic_id'] != doc.get('topic_id'):
            errors.append('scenario belongs to a different topic')
        if any(scenario[k] != registered[k] for k in ('label_zh', 'goal_zh')):
            errors.append('scenario label/goal differs from taxonomy')
    evidence_sources = {}
    for tid, source in sources.items():
        if isinstance(source, dict) and text(source.get('lemma')):
            evidence_sources[tid] = {**source, 'approved_forms': [source['lemma']]}
    targets = doc.get('targets') if isinstance(doc.get('targets'), list) else []
    for target in targets:
        if not isinstance(target, dict):
            continue
        tid = target.get('target_id')
        if not text(tid):
            continue
        source = sources.get(tid)
        if not isinstance(source, dict):
            continue  # pipeline.validate supplies the exact identity error.
        if target.get('pos') != source.get('pos'):
            errors.append(f'{tid}: source POS mismatch')
        for field in ('source_commit', 'list', 'cefr'):
            if field in target and target[field] != source.get(field):
                errors.append(f'{tid}: source {field} mismatch')
        if not text(target.get('sense_zh')):
            errors.append(f'{tid}: selected sense_zh is required')
        if not text(target.get('sense_id')):
            errors.append(f'{tid}: stable sense_id is required')
        if not text(target.get('lemma')) or target['lemma'] not in allowed_forms:
            errors.append(f'{tid}: target lemma is not allocated to this phase')
        forms = target.get('forms')
        if strings(forms) and any(form != source.get('lemma') for form in forms):
            if not text(target.get('forms_rationale_zh')):
                errors.append(f'{tid}: non-lemma forms require explicit forms_rationale_zh')
            else:
                # This records explicit approval, not automatic morphology or
                # semantic proof. An independent verdict must bind exact forms.
                evidence_sources[tid]['approved_forms'] = forms[:]
        for field in ('forms', 'sentence_ids'):
            if not strings(target.get(field)):
                errors.append(f'{tid}: {field} must be nonempty unique strings')
    report = validate(doc, evidence_sources)
    errors.extend(report['errors'])
    if report['formal_pass']:
        sentences = {s['id']: s for s in doc['sentences']}
        for sentence in sentences.values():
            if sentence['speaker'] not in participants:
                errors.append(f"{sentence['id']}: speaker is not a declared participant")
        for target in targets:
            for sid in target['sentence_ids']:
                if not any(contains(sentences[sid]['text'], form) for form in target['forms']):
                    errors.append(f"{target['target_id']}: evidence {sid} has no bounded approved form")
    return errors


def check_review(review, doc, expected_hash):
    errors = []
    if not isinstance(review, dict):
        return ['review must be an object']
    if not text(review.get('reviewer')):
        errors.append('reviewer must be nonempty')
    elif text(doc.get('author')) and review['reviewer'].strip().casefold() == doc['author'].strip().casefold():
        errors.append('reviewer must differ from dialogue author')
    if review.get('dialogue_id') != doc.get('id'):
        errors.append('review dialogue_id mismatch')
    digest = review.get('dialogue_sha256')
    if not isinstance(digest, str) or not SHA256.fullmatch(digest) or digest != expected_hash:
        errors.append('review dialogue_sha256 differs from the exact dialogue file bytes')
    if review.get('status') not in ('accepted', 'rejected') or not text(review.get('rationale')):
        errors.append('review requires accepted/rejected status and nonempty rationale')
    rows = review.get('targets')
    if not isinstance(rows, list):
        errors.append('review targets must be an array')
        rows = []
    expected = {t['target_id']: t for t in doc.get('targets', [])
                if isinstance(t, dict) and text(t.get('target_id'))}
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not text(row.get('target_id')):
            errors.append('target verdict requires target_id')
            continue
        tid = row['target_id']
        if tid in seen:
            errors.append(f'{tid}: duplicate target verdict')
        seen.add(tid)
        if tid not in expected:
            errors.append(f'{tid}: unknown target verdict')
            continue
        target = expected[tid]
        if row.get('status') not in ('accepted', 'rejected') or not text(row.get('rationale')):
            errors.append(f'{tid}: verdict requires accepted/rejected status and rationale')
        if not strings(row.get('sentence_ids')) or set(row['sentence_ids']) != set(target.get('sentence_ids', [])):
            errors.append(f'{tid}: verdict evidence must match every target sentence reference')
        # Regular lemma-only uses retain the minimal original review contract;
        # explicit variants need exact form acknowledgement by the reviewer.
        if ('forms' in row or any(f != target.get('lemma') for f in target.get('forms', []))):
            if not strings(row.get('forms')) or set(row['forms']) != set(target.get('forms', [])):
                errors.append(f'{tid}: verdict forms must match exact approved forms')
        if review.get('status') == 'accepted' and row.get('status') != 'accepted':
            errors.append(f'{tid}: accepted dialogue cannot contain a rejected target verdict')
    if seen != set(expected):
        errors.append('review target verdicts must cover exactly every dialogue target')
    return errors


def check_corpus(inventory, sources, documents, reviews, taxonomy, dialogue_hashes,
                 deferrals=None, expected_commit=None, expected_pilot_forms=None,
                 require_phases=()):
    """Return aggregate counts; missing/rejected reviews are valid partial work.

    documents/reviews/deferrals are phase-ID mappings. dialogue_hashes is keyed
    by dialogue ID, computed from the actual file bytes by the CLI loader.
    Completion means processed allocation, never accepted coverage of deferrals.
    """
    phase_forms, counts, errors = check_inventory(inventory, sources, expected_commit, expected_pilot_forms)
    if not isinstance(sources, dict):
        sources = {}
    sources = {tid: row for tid, row in sources.items() if isinstance(row, dict)}
    taxonomy, taxonomy_errors = merge_taxonomy(taxonomy)
    errors.extend(taxonomy_errors)
    deferrals = {} if deferrals is None else deferrals
    if not isinstance(dialogue_hashes, dict):
        errors.append('dialogue_hashes must be an exact-byte hash mapping')
        dialogue_hashes = {}
    for name, value in [('documents', documents), ('reviews', reviews), ('deferrals', deferrals)]:
        if not isinstance(value, dict):
            return {'passed': False, 'errors': errors + [f'{name} must be a phase mapping'], 'semantic_status': NOTICE}
        if set(value) - set(phase_forms):
            errors.append(f'{name} contains phases not allocated in the inventory')
    seen_documents, accepted_global, accepted_ids, selected_ids, reports = set(), set(), set(), set(), []
    sense_definitions = {}
    for pid, allocated in phase_forms.items():
        phase_errors, document_map, valid_documents = [], {}, set()
        docs, phase_reviews = documents.get(pid, []), reviews.get(pid, [])
        if not isinstance(docs, list):
            phase_errors.append('documents must be an array')
            docs = []
        if not isinstance(phase_reviews, list):
            phase_errors.append('reviews must be an array')
            phase_reviews = []
        written_forms, formal_forms, formal_ids, phase_selected_ids = set(), set(), set(), set()
        for index, doc in enumerate(docs):
            label = doc.get('id') if isinstance(doc, dict) and text(doc.get('id')) else f'document-{index + 1}'
            doc_errors = check_document(doc, sources, allocated, taxonomy)
            if isinstance(doc, dict) and isinstance(doc.get('targets'), list):
                local_senses = set()
                for target in doc['targets']:
                    if not isinstance(target, dict) or not text(target.get('sense_id')):
                        continue
                    sense_id = target['sense_id']
                    meaning = tuple(target.get(k) for k in ('target_id', 'lemma', 'pos', 'sense_zh'))
                    if sense_id in local_senses:
                        doc_errors.append(f'{sense_id}: duplicate sense ID within dialogue')
                    if sense_id in sense_definitions and sense_definitions[sense_id] != meaning:
                        doc_errors.append(f'{sense_id}: conflicting global sense identity')
                    local_senses.add(sense_id)
                    sense_definitions[sense_id] = meaning
            if label in seen_documents:
                doc_errors.append('duplicate dialogue ID across corpus')
            seen_documents.add(label)
            if isinstance(doc, dict) and text(doc.get('id')):
                document_map[label] = doc
                target_rows = doc.get('targets') if isinstance(doc.get('targets'), list) else []
                written_forms.update(t['lemma'] for t in target_rows
                                     if isinstance(t, dict) and text(t.get('lemma')) and t['lemma'] in allocated)
                phase_selected_ids.update(t['target_id'] for t in target_rows
                                          if isinstance(t, dict) and text(t.get('target_id')) and t['target_id'] in sources)
            if doc_errors:
                phase_errors.extend(f'{label}: {error}' for error in doc_errors)
            else:
                valid_documents.add(label)
                formal_forms.update(t['lemma'] for t in doc['targets'])
                formal_ids.update(t['target_id'] for t in doc['targets'])
        review_map, valid_reviews = {}, set()
        duplicate_reviews = set()
        for review in phase_reviews:
            if not isinstance(review, dict) or not text(review.get('dialogue_id')):
                phase_errors.append('review requires dialogue_id')
                continue
            did = review['dialogue_id']
            if did in review_map:
                phase_errors.append(f'{did}: duplicate review; retain only the current verdict')
                duplicate_reviews.add(did)
            review_map[did] = review
            if did not in document_map:
                phase_errors.append(f'{did}: review references an unknown dialogue')
                continue
            if did not in valid_documents:
                phase_errors.append(f'{did}: review cannot validate a formally invalid dialogue')
                continue
            review_errors = check_review(review, document_map[did], dialogue_hashes.get(did))
            if review_errors:
                phase_errors.extend(f'{did}: {error}' for error in review_errors)
            else:
                valid_reviews.add(did)
        valid_reviews -= duplicate_reviews
        accepted_docs = {did for did in valid_documents & valid_reviews if review_map[did]['status'] == 'accepted'}
        accepted_forms, phase_ids = set(), set()
        for did in accepted_docs:
            accepted_forms.update(t['lemma'] for t in document_map[did]['targets'])
            phase_ids.update(t['target_id'] for t in document_map[did]['targets'])
        deferred_forms = set()
        deferred_rows = deferrals.get(pid, [])
        if not isinstance(deferred_rows, list):
            phase_errors.append('phase deferrals must be an array')
            deferred_rows = []
        for row in deferred_rows:
            if not isinstance(row, dict) or not text(row.get('lemma')) or not text(row.get('reason')):
                phase_errors.append('phase deferrals need lemma and explicit reason')
                continue
            lemma = row['lemma']
            expected_ids = {tid for tid, source in sources.items() if source.get('lemma') == lemma}
            if 'reason_category' in row and not text(row['reason_category']):
                phase_errors.append(f'{lemma}: reason_category must be nonempty text')
                continue
            if (lemma not in allocated or lemma in deferred_forms or lemma in written_forms
                    or not strings(row.get('source_target_ids')) or set(row['source_target_ids']) != expected_ids):
                phase_errors.append(f'{lemma}: invalid, duplicate, authored or incomplete source-record deferral')
                continue
            deferred_forms.add(lemma)
        unresolved = allocated - accepted_forms - deferred_forms
        complete = (not phase_errors and not unresolved and len(accepted_docs) == len(docs))
        report = {'id': pid, 'status': 'processed' if complete else 'partial', 'complete': complete,
                  'allocated_form_count': len(allocated), 'dialogue_count': len(docs),
                  'formal_dialogue_count': len(valid_documents), 'accepted_dialogue_count': len(accepted_docs),
                  'written_form_count': len(written_forms), 'formal_form_count': len(formal_forms),
                  'accepted_form_count': len(accepted_forms), 'accepted_source_target_count': len(phase_ids),
                  'deferred_form_count': len(deferred_forms), 'unresolved_form_count': len(unresolved),
                  'unreviewed_dialogue_count': len(set(document_map) - valid_reviews),
                  'rejected_dialogue_count': sum(review_map[did]['status'] == 'rejected' for did in valid_reviews),
                  'allocated_source_target_count': sum(s.get('lemma') in allocated for s in sources.values()),
                  'formal_source_target_count': len(formal_ids),
                  'selected_source_target_count': len(phase_selected_ids),
                  'selected_without_accepted_usage_count': len(phase_selected_ids - phase_ids),
                  'deferred_reason_counts': dict(sorted(Counter(r.get('reason_category', 'uncategorized') for r in deferred_rows
                      if isinstance(r, dict) and r.get('lemma') in deferred_forms).items())),
                  'accepted_dialogue_ids': sorted(accepted_docs)}
        report['unselected_source_target_count'] = report['allocated_source_target_count'] - len(phase_selected_ids)
        report['source_records_without_accepted_usage_count'] = report['allocated_source_target_count'] - len(phase_ids)
        reports.append(report)
        accepted_global.update(accepted_forms)
        accepted_ids.update(phase_ids)
        selected_ids.update(phase_selected_ids)
        errors.extend(f'{pid}: {error}' for error in phase_errors)
    for pid in require_phases:
        if pid not in phase_forms:
            errors.append(f'required phase not allocated: {pid}')
        elif not next(r for r in reports if r['id'] == pid)['complete']:
            errors.append(f'{pid}: required phase is not fully processed with accepted uses or explicit deferrals')
    counts.update({'staged_selected_source_target_count': len(selected_ids),
                   'staged_selected_without_accepted_usage_count': len(selected_ids - accepted_ids),
                   'source_records_not_selected_in_staged_count': len(sources) - len(selected_ids),
                   'staged_accepted_form_count': len(accepted_global), 'staged_accepted_source_target_count': len(accepted_ids),
                   'source_records_without_staged_accepted_usage_count': len(sources) - len(accepted_ids),
                   'staged_deferred_form_count': sum(r['deferred_form_count'] for r in reports),
                   'staged_unresolved_form_count': sum(r['unresolved_form_count'] for r in reports),
                   'completed_phase_count': sum(r['complete'] for r in reports), 'phase_count': len(reports)})
    return {'passed': not errors, 'semantic_status': NOTICE, 'counts': counts, 'phases': reports, 'errors': errors}


def render_outputs(report, documents, reviews, taxonomy):
    """Render all authored text, not just the words that happened to pass."""
    outputs = {'coverage.json': json_bytes(report)}
    topics = {t['id']: t for t in taxonomy['topics']}
    lines = ['# 分阶段情景对话', '',
             '阶段性原创文本；“处理完毕”包含有理由的暂缓，不等于这些词已经覆盖。', '',
             '形式校验与独立审阅记录分别统计。程序不能证明语义正确、审阅者真实独立或学习者已掌握。', '',
             '完整受限来源词表、未写候选及详细分配保留在本地 build/；此目录只发布统计与原创用例的来源引用。', '',
             '旧 100 词试验保持独立：[原试验](../../pilots/oxford-100-v1/README.md)。其保留词形数不混入本批接受数；合并数仅在单独校验旧试验通过后显示。', '',
             '[按主题和情景浏览已接受对话](scene-index.md)。阶段目录用于进度管理，不代替情景分类。', '',
             '## 范围统计', '']
    count = report['counts']
    labels = [('source_form_count', '来源词形'), ('source_target_record_count', '来源词性/等级记录'),
              ('pilot_reserved_form_count', '旧试验保留词形'), ('phase_allocated_form_count', '分阶段分配词形'),
              ('staged_accepted_form_count', '本批有审阅接受用例的不同词形'),
              ('staged_accepted_source_target_count', '本批有接受用例的来源目标记录'),
              ('staged_deferred_form_count', '阶段内暂缓词形（不计覆盖）'),
              ('inventory_deferred_form_count', '总范围暂缓词形（不计覆盖）'),
              ('staged_unresolved_form_count', '阶段内尚未处理词形')]
    lines += [f'- {label}：{count[key]}' for key, label in labels]
    pilot_status = report.get('pilot_validation', {})
    if pilot_status.get('passed'):
        lines += ['', f"冻结旧试验的结构与审阅记录另行校验通过：{count['pilot_accepted_form_count']} 词形。", '',
                  f"全库当前有接受记录的词形：{count['pilot_accepted_form_count']}（旧试验） + {count['staged_accepted_form_count']}（新阶段） = {count['combined_accepted_form_count']} / {count['source_form_count']}。暂缓不计入分子。", '',
                  '来源目标记录分区：' + '；'.join([
                      f"旧试验接受 {count['pilot_accepted_source_target_count']}",
                      f"新阶段接受 {count['staged_accepted_source_target_count']}",
                      f"新阶段已选但未接受 {count['staged_selected_without_accepted_usage_count']}",
                      f"其他未选记录 {count['other_unselected_source_target_count']}"]) + '。']
    else:
        lines += ['', '此运行未验证旧试验的完整结构与审阅记录，因此不声称合并接受覆盖数。']
    lines += ['', '每个来源目标可能还有未选义项。接受一个词形的一条用例，不代表完成该词全部词性或义项。', '', '## 阶段入口', '']
    for phase in report['phases']:
        pid = phase['id']
        if not documents.get(pid) and not phase['deferred_form_count']:
            lines.append(f"- {pid}：尚未开始；分配 {phase['allocated_form_count']}，接受 0，未决 {phase['unresolved_form_count']}。")
            continue
        lines.append(f"- [{pid} 对话]({pid}/dialogues.md) · [单词反查]({pid}/words.md)："
                     f"分配 {phase['allocated_form_count']}，接受 {phase['accepted_form_count']}，"
                     f"暂缓 {phase['deferred_form_count']}，未决 {phase['unresolved_form_count']}；"
                     + ('本阶段处理完毕。' if phase['complete'] else '阶段未完成。'))
        docs = sorted(documents.get(pid, []), key=lambda d: d['id'])
        review_map = {r['dialogue_id']: r for r in reviews.get(pid, [])}
        body = [f'# {pid} 完整对话', '',
                f"分配 {phase['allocated_form_count']} 词形；已接受 {phase['accepted_form_count']}，暂缓 {phase['deferred_form_count']}，未决 {phase['unresolved_form_count']}。", '',
                '“已接受”仅指本版本存在完整、绑定文本哈希的独立署名审阅记录，不是程序证明语义正确。', '']
        words = [f'# {pid} 单词与具体用法反查', '', '仅列已获得本版本整篇及逐目标审阅接受的原创用例；未审、拒绝、暂缓和未写词表不在此重发。', '']
        usages = []
        for doc in docs:
            did = doc['id']
            accepted = did in phase['accepted_dialogue_ids']
            review = review_map.get(did)
            status = '审阅接受' if accepted else ('审阅拒绝，待修订' if review and review['status'] == 'rejected' else '待审')
            body += [f'<a id="{html.escape("dialogue-" + did, quote=True)}"></a>', '',
                     f'## {doc["title_zh"]} · {did}', '',
                     f"主题：{topics[doc['topic_id']]['label_zh']}；情景：{doc['scenario']['label_zh']}（{doc['scenario']['id']}）。", '',
                     f"沟通目标：{doc['scenario']['goal_zh']}", '', f"背景：{doc['context_zh']}", '',
                     '人物：' + '、'.join(doc['participants']) + '。', '',
                     f"起草：{doc['author']}；状态：{status}。", '']
            body.extend(f"- {s['id']} · {s['speaker']}: {s['text']}" for s in doc['sentences'])
            body += ['', '目标用法：', '']
            sm = {s['id']: s['text'] for s in doc['sentences']}
            for target in doc['targets']:
                body += [f"- {target['lemma']} · {target['pos']} · {target['sense_zh']}；义项 {target['sense_id']}；来源 {target['target_id']}；证据 "
                         + '、'.join(target['sentence_ids']) + '；词形 ' + ' / '.join(target['forms']) + '。']
                if text(target.get('forms_rationale_zh')):
                    body.append('  - 词形依据：' + target['forms_rationale_zh'])
                if accepted:
                    usages.append((target, doc, status, sm))
            if review:
                body += ['', f"审阅者：{review['reviewer']}；整篇结论：{review['status']}。", '', review['rationale'], '',
                         f"绑定文件 SHA-256：{review['dialogue_sha256']}", '']
                body.extend(f"- {r['target_id']}：{r['status']}；{r['rationale']}（" + '、'.join(r['sentence_ids']) + '）。' for r in review['targets'])
            body += ['']
        for target, doc, status, sm in sorted(usages, key=lambda row: (row[0]['lemma'].casefold(), row[0]['pos'], row[1]['id'])):
            words += [f"## {target['lemma']} · {target['pos']} · {target['sense_zh']}", '',
                      f"对话：[{doc['title_zh']}](dialogues.md#{quote('dialogue-' + doc['id'], safe='')})（{doc['id']}）；情景：{doc['scenario']['label_zh']}；{status}。", '',
                      f"义项：{target['sense_id']}；来源目标：{target['target_id']}；词形：" + ' / '.join(target['forms']) + '。', '']
            words.extend(f'- {sid}：{sm[sid]}' for sid in target['sentence_ids'])
            words += ['']
        if not usages:
            words += ['尚无审阅接受的原创目标用例。', '']
        if not docs:
            body += ['尚未提交本阶段对话；不能视为已覆盖。', '']
        outputs[f'{pid}/dialogues.md'] = ('\n'.join(body) + '\n').encode('utf-8')
        outputs[f'{pid}/words.md'] = ('\n'.join(words) + '\n').encode('utf-8')
    lines += ['', '## 复现', '',
              '在仓库根目录先从固定来源导入 build/targets.jsonl，并准备本地 build/staged-inventory.json。', '',
              '运行 python3 tools/staged_corpus.py --write 重新生成；不带 --write 校验已有输出和 SHA-256 清单。', '',
              '使用 --require-phase phase-01 可要求该阶段所有分配都有接受用例或明确暂缓记录；暂缓始终不计接受覆盖。', '',
              'manifest.json 固定输入及输出的 SHA-256，不包含运行时间，因此同一输入得到相同输出。', '']
    outputs['README.md'] = ('\n'.join(lines) + '\n').encode('utf-8')
    outputs['scene-index.md'] = render_scene_index(report, documents, taxonomy).encode('utf-8')
    return outputs


def render_scene_index(report, documents, taxonomy):
    """Cross-phase topic → scenario → accepted, version-bound original uses."""
    groups = {}
    for phase in report['phases']:
        accepted = set(phase['accepted_dialogue_ids'])
        for doc in documents.get(phase['id'], []):
            if doc['id'] in accepted:
                groups.setdefault(doc['scenario']['id'], []).append((phase['id'], doc))
    lines = ['# 跨阶段主题与情景索引', '',
             '这里只列整篇与逐目标审阅均接受、且记录绑定当前文件版本的新增对话。未审、拒绝、暂缓和建议关联不混入本索引。', '',
             '主题是领域，情景是沟通任务，义项由 sense_id 标识。一个义项可以在多个情景自然复用；关联数不等于不同词形覆盖数。', '',
             '本索引不重发未写的来源候选词表，也不代表其他词性或义项已经覆盖。', '',
             '[阶段总览](README.md) · [旧 100 词试验情景索引](../../pilots/oxford-100-v1/classification.md)', '']
    if not groups:
        lines += ['尚无满足本版本整篇及逐目标审阅条件的新增对话。', '']
    for topic in taxonomy['topics']:
        scenarios = [s for s in taxonomy['scenarios'] if s['topic_id'] == topic['id'] and s['id'] in groups]
        if not scenarios:
            continue
        lines += [f"## {topic['label_zh']}", '', topic['scope_zh'], '']
        for scenario in sorted(scenarios, key=lambda s: s['id']):
            uses = sorted(groups[scenario['id']], key=lambda item: (item[0], item[1]['id']))
            senses = {target['sense_id'] for _, doc in uses for target in doc['targets']}
            lines += [f"### {scenario['label_zh']} · {scenario['id']}", '',
                      f"沟通目标：{scenario['goal_zh']}", '',
                      f"{len(uses)} 篇已接受对话，{len(senses)} 个不同已选义项。", '']
            for pid, doc in uses:
                link = f"{pid}/dialogues.md#{quote('dialogue-' + doc['id'], safe='')}"
                lines.append(f"- [{doc['title_zh']} · {doc['id']}]({link})：{pid}，{len(doc['targets'])} 条已审目标用法；[词语与证据反查]({pid}/words.md)。")
            lines += ['']
    return '\n'.join(lines) + '\n'


def load_corpus(corpus, inventory_path, targets_path, taxonomy_path, pilot_path, deferrals_dir=None):
    inventory = read_json(inventory_path)
    rows = []
    for number, line in enumerate(targets_path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict) or not text(row.get('target_id')):
                raise ValueError(f'targets line {number}: missing target_id')
            rows.append(row)
    sources = {r['target_id']: r for r in rows}
    if len(sources) != len(rows):
        raise ValueError('Duplicate source target IDs')
    extension_path = corpus / 'taxonomy.json'
    taxonomy, errors = merge_taxonomy(read_json(taxonomy_path), read_json(extension_path) if extension_path.exists() else None)
    if errors:
        raise ValueError('; '.join(errors))
    documents, reviews, deferrals, hashes, public_inputs = {}, {}, {}, {}, {}
    for phase_path in sorted(corpus.glob('phase-*')):
        if not phase_path.is_dir():
            continue
        pid = phase_path.name
        documents[pid] = []
        for path in sorted(phase_path.glob('*.json')):
            if path.name in ('reviews.json', 'deferred.json') or path.name.startswith('classification-'):
                continue
            value = read_json(path)
            # Auxiliary author receipts are not dialogue documents. A pNN- file
            # always is, so a malformed intended dialogue cannot silently vanish.
            if not (re.match(r'p[0-9]+-', path.name) or isinstance(value, dict) and {'id', 'sentences', 'targets'} <= set(value)):
                raise ValueError(f'Unrecognized phase JSON file: {path.name}; use classification- prefix for receipts')
            documents[pid].append(value)
            if isinstance(value, dict) and text(value.get('id')):
                hashes[value['id']] = sha256(path.read_bytes())
            public_inputs[path.relative_to(corpus).as_posix()] = sha256(path.read_bytes())
        review_path = phase_path / 'reviews.json'
        reviews[pid] = read_json(review_path) if review_path.exists() else []
        if review_path.exists():
            public_inputs[review_path.relative_to(corpus).as_posix()] = sha256(review_path.read_bytes())
        defer_path = deferrals_dir / (pid + '.json') if deferrals_dir else phase_path / 'deferred.json'
        deferrals[pid] = read_json(defer_path) if defer_path.exists() else []
    # Private deferrals may exist for allocated phases with no public files yet.
    if deferrals_dir:
        for path in sorted(deferrals_dir.glob('phase-*.json')):
            deferrals[path.stem] = read_json(path)
    private_hashes = {'source_targets': sha256(targets_path.read_bytes()), 'stage_inventory': sha256(inventory_path.read_bytes())}
    if deferrals_dir:
        private_hashes['phase_deferrals'] = {p.name: sha256(p.read_bytes()) for p in sorted(deferrals_dir.glob('phase-*.json'))}
    else:
        public_inputs.update({p.relative_to(corpus).as_posix(): sha256(p.read_bytes()) for p in corpus.glob('phase-*/deferred.json')})
    if extension_path.exists():
        public_inputs['taxonomy.json'] = sha256(extension_path.read_bytes())
    pilot = read_json(pilot_path)
    if not isinstance(pilot, list) or any(not isinstance(row, dict) or not text(row.get('lemma')) for row in pilot):
        raise ValueError('Invalid preserved pilot selection')
    metadata = {'public_input_sha256': public_inputs, 'local_input_sha256': private_hashes,
                'base_taxonomy_sha256': sha256(taxonomy_path.read_bytes()), 'pilot_selection_sha256': sha256(pilot_path.read_bytes()),
                'tool_sha256': sha256(Path(__file__).read_bytes()),
                'lexical_checker_sha256': sha256((ROOT / 'tools/pipeline.py').read_bytes())}
    return inventory, sources, documents, reviews, taxonomy, hashes, deferrals, [r['lemma'] for r in pilot], metadata


def verify_pilot(report, sources, pilot_path):
    """Verify the frozen pilot separately; never silently count a reservation.

    A custom selection-only fixture has no pilot review bundle and is therefore
    reported unverified, not counted as accepted. The frozen real bundle must
    pass its existing 100-item checker before combined counts are published.
    """
    pilot_dir = pilot_path.parent
    required = [pilot_dir / 'reviews.json', pilot_dir / 'dialogues']
    if not all(path.exists() for path in required):
        report['pilot_validation'] = {'passed': False, 'status': 'not-verified',
                                      'reason': 'No complete frozen pilot review bundle beside selection.'}
        return {}
    selection = read_json(pilot_path)
    doc_paths = sorted((pilot_dir / 'dialogues').glob('*.json'))
    approval_path = pilot_dir / 'form-approvals.json'
    result = check_pilot(selection, [read_json(p) for p in doc_paths], sources,
                         read_json(pilot_dir / 'reviews.json'),
                         form_approvals=read_json(approval_path) if approval_path.exists() else [])
    report['pilot_validation'] = {key: result[key] for key in
                                 ('passed', 'formal_pass', 'review_records_complete', 'semantic_status')}
    if not result['passed']:
        report['errors'].extend('frozen pilot: ' + error for error in result['errors'] + result['review_errors'])
        report['passed'] = False
    else:
        counts = report['counts']
        pilot_forms = {row['lemma'] for row in selection}
        pilot_ids = {row['target_id'] for row in selection}
        counts.update({'pilot_accepted_form_count': len(pilot_forms),
                       'pilot_accepted_source_target_count': len(pilot_ids),
                       'combined_accepted_form_count': len(pilot_forms) + counts['staged_accepted_form_count'],
                       'combined_accepted_source_target_count': len(pilot_ids) + counts['staged_accepted_source_target_count'],
                       'other_unselected_source_target_count': counts['source_records_not_selected_in_staged_count'] - len(pilot_ids)})
    paths = [pilot_path, pilot_dir / 'reviews.json', *doc_paths]
    if approval_path.exists():
        paths.append(approval_path)
    return {path.relative_to(pilot_dir).as_posix(): sha256(path.read_bytes()) for path in paths}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus-dir', type=Path, default=ROOT / 'corpus/staged-v1')
    parser.add_argument('--targets', type=Path, default=ROOT / 'build/targets.jsonl')
    parser.add_argument('--inventory', type=Path, default=ROOT / 'build/staged-inventory.json')
    parser.add_argument('--taxonomy', type=Path, default=ROOT / 'data/scene-taxonomy.json')
    parser.add_argument('--pilot-selection', type=Path, default=ROOT / 'pilots/oxford-100-v1/selection.json')
    parser.add_argument('--deferrals-dir', type=Path, default=ROOT / 'build/staged-deferrals',
                        help='private phase deferrals directory (phase-NN.json); never rendered as a word list')
    parser.add_argument('--require-phase', action='append', default=[], help='require processed allocation; repeat for multiple phases')
    parser.add_argument('--write', action='store_true', help='render readable pages, aggregate coverage and reproducible manifest')
    args = parser.parse_args(argv)
    try:
        loaded = load_corpus(args.corpus_dir, args.inventory, args.targets, args.taxonomy, args.pilot_selection, args.deferrals_dir)
        inventory, sources, docs, reviews, taxonomy, hashes, deferrals, pilot, metadata = loaded
        pinned = read_json(ROOT / 'provenance/wordlists.json')['commit']
        report = check_corpus(inventory, sources, docs, reviews, taxonomy, hashes, deferrals,
                              expected_commit=pinned, expected_pilot_forms=pilot, require_phases=args.require_phase)
        if report['passed']:
            metadata['frozen_pilot_input_sha256'] = verify_pilot(report, sources, args.pilot_selection)
            metadata['pilot_checker_sha256'] = sha256((ROOT / 'tools/check_pilot.py').read_bytes())
        if report['passed']:
            outputs = render_outputs(report, docs, reviews, taxonomy)
            manifest = {'schema_version': 1, 'source_commit': inventory['source_commit'],
                        'hash_policy': 'SHA-256 of exact bytes; manifest does not hash itself', **metadata,
                        'generated_output_sha256': {name: sha256(data) for name, data in sorted(outputs.items())}}
            outputs['manifest.json'] = json_bytes(manifest)
            for relative, data in outputs.items():
                path = args.corpus_dir / relative
                if args.write:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                elif not path.exists() or path.read_bytes() != data:
                    report['errors'].append(f'Stale or missing generated output: {relative}; run with --write')
            report['passed'] = not report['errors']
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        report = {'passed': False, 'errors': [str(exc)], 'semantic_status': NOTICE}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
