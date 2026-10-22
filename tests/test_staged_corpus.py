"""Synthetic fixtures only: no restricted source inventory is embedded in tests."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools.staged_corpus import (ROOT, check_corpus, json_bytes, load_corpus, main,
                                 merge_taxonomy, read_json, render_outputs, sha256, verify_pilot)


class StagedCorpusChecks(unittest.TestCase):
    def setUp(self):
        self.sources = {
            't1': {'target_id': 't1', 'lemma': 'stand', 'pos': 'v.', 'source_commit': 'pinned'},
            't2': {'target_id': 't2', 'lemma': 'stand', 'pos': 'n.', 'source_commit': 'pinned'},
            't3': {'target_id': 't3', 'lemma': 'bank', 'pos': 'n.', 'source_commit': 'pinned'},
            't4': {'target_id': 't4', 'lemma': 'zebra', 'pos': 'n.', 'source_commit': 'pinned'}}
        self.inventory = {'source_commit': 'pinned', 'pilot_forms': ['bank'],
                          'phases': [{'id': 'phase-01', 'forms': ['stand']},
                                     {'id': 'phase-02', 'forms': ['zebra']}], 'deferred': []}
        self.taxonomy = {'schema_version': 1,
                         'topics': [{'id': 'home', 'label_zh': '居家', 'scope_zh': '居家事务'}],
                         'scenarios': [{'id': 'move-chair', 'topic_id': 'home', 'label_zh': '移动椅子',
                                        'goal_zh': '确定摆放位置'}]}
        self.doc = {'id': 'p01-test', 'title_zh': '移开椅子', 'author': 'writer-A',
                    'topic_id': 'home', 'scenario': {'id': 'move-chair', 'label_zh': '移动椅子', 'goal_zh': '确定摆放位置'},
                    'participants': ['A', 'B'], 'context_zh': '两人挪动椅子。',
                    'sentences': [{'id': 's1', 'speaker': 'A', 'text': 'Please stand here.'},
                                  {'id': 's2', 'speaker': 'B', 'text': 'Is this far enough?'}],
                    'targets': [{'target_id': 't1', 'lemma': 'stand', 'pos': 'v.', 'sense_id': 'sense-standing',
                                 'sense_zh': '站立', 'sentence_ids': ['s1'], 'forms': ['stand']}]}
        self.documents = {'phase-01': [self.doc]}
        self.review = {'dialogue_id': self.doc['id'], 'reviewer': 'reviewer-B',
                       'dialogue_sha256': sha256(json_bytes(self.doc)), 'status': 'accepted',
                       'rationale': '请求站在指定位置，回复确认距离，沟通任务自然。',
                       'targets': [{'target_id': 't1', 'status': 'accepted',
                                    'rationale': 's1 的 stand 是祈使句动词，表示站立。', 'sentence_ids': ['s1']}]}
        self.reviews = {'phase-01': [self.review]}
        self.hashes = {self.doc['id']: self.review['dialogue_sha256']}
        self.deferrals = {}

    def refresh_hash(self):
        self.hashes[self.doc['id']] = sha256(json_bytes(self.doc))
        self.review['dialogue_sha256'] = self.hashes[self.doc['id']]

    def check(self, required=()):
        return check_corpus(self.inventory, self.sources, self.documents, self.reviews,
                            self.taxonomy, self.hashes, self.deferrals,
                            expected_commit='pinned', expected_pilot_forms=['bank'], require_phases=required)

    def test_acceptance_is_distinct_from_source_records_and_full_scope(self):
        result = self.check(['phase-01'])
        self.assertTrue(result['passed'], result)
        self.assertTrue(result['phases'][0]['complete'])
        self.assertFalse(result['phases'][1]['complete'])
        self.assertEqual(result['counts']['source_form_count'], 3)
        self.assertEqual(result['counts']['source_target_record_count'], 4)
        self.assertEqual(result['counts']['staged_accepted_form_count'], 1)
        self.assertEqual(result['counts']['staged_accepted_source_target_count'], 1)
        self.assertEqual(result['phases'][0]['source_records_without_accepted_usage_count'], 1)
        self.assertIn('NOT CERTIFIED', result['semantic_status'])

    def test_no_review_is_valid_partial_not_coverage(self):
        self.reviews = {}
        result = self.check()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['phases'][0]['formal_form_count'], 1)
        self.assertEqual(result['phases'][0]['accepted_form_count'], 0)
        self.assertEqual(result['phases'][0]['unreviewed_dialogue_count'], 1)
        self.assertFalse(self.check(['phase-01'])['passed'])

    def test_rejection_never_counts_as_coverage(self):
        self.review['status'] = 'rejected'
        self.review['targets'][0]['status'] = 'rejected'
        result = self.check()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['phases'][0]['rejected_dialogue_count'], 1)
        self.assertEqual(result['counts']['staged_accepted_form_count'], 0)
        self.assertFalse(result['phases'][0]['complete'])

    def test_whole_dialogue_rejection_blocks_accepted_target(self):
        self.review['status'] = 'rejected'
        self.assertEqual(self.check()['counts']['staged_accepted_form_count'], 0)

    def test_whole_dialogue_acceptance_cannot_hide_rejected_target(self):
        self.review['targets'][0]['status'] = 'rejected'
        self.assertFalse(self.check()['passed'])
        self.assertEqual(self.check()['counts']['staged_accepted_form_count'], 0)

    def test_stale_hash_and_false_reviewer_are_invalid(self):
        for key, value in [('dialogue_sha256', '0' * 64), ('reviewer', ' WRITER-a '), ('reviewer', '')]:
            with self.subTest(key=key, value=value):
                before = self.review[key]
                self.review[key] = value
                self.assertFalse(self.check()['passed'])
                self.assertEqual(self.check()['counts']['staged_accepted_form_count'], 0)
                self.review[key] = before

    def test_review_requires_complete_explicit_target_verdicts(self):
        variants = [[], [{}], [dict(self.review['targets'][0], target_id='missing')],
                    [dict(self.review['targets'][0], rationale=' ')],
                    [dict(self.review['targets'][0], sentence_ids=['s2'])],
                    [dict(self.review['targets'][0], sentence_ids=['s1', 's1'])],
                    [dict(self.review['targets'][0], status=True)]]
        for rows in variants:
            with self.subTest(rows=rows):
                self.review['targets'] = rows
                self.assertFalse(self.check()['passed'])

    def test_duplicate_reviews_and_target_verdicts_fail_closed(self):
        self.reviews['phase-01'].append(copy.deepcopy(self.review))
        result = self.check()
        self.assertFalse(result['passed'])
        self.assertEqual(result['counts']['staged_accepted_form_count'], 0)
        self.setUp()
        self.review['targets'] *= 2
        self.assertFalse(self.check()['passed'])

    def test_missing_and_unknown_review_dialogue(self):
        for row in [{}, dict(self.review, dialogue_id='missing')]:
            self.reviews['phase-01'] = [row]
            self.assertFalse(self.check()['passed'])

    def test_every_evidence_sentence_needs_bounded_form(self):
        self.doc['targets'][0]['sentence_ids'] = ['s1', 's2']
        self.review['targets'][0]['sentence_ids'] = ['s1', 's2']
        self.refresh_hash()
        result = self.check()
        self.assertFalse(result['passed'])
        self.assertTrue(any('evidence s2' in error for error in result['errors']))

    def test_substring_is_not_evidence(self):
        self.doc['sentences'][0]['text'] = 'I understand you.'
        self.refresh_hash()
        self.assertFalse(self.check()['passed'])

    def test_case_sensitive_source_form_is_preserved(self):
        self.sources['t1']['lemma'] = self.sources['t2']['lemma'] = 'May'
        self.inventory['phases'][0]['forms'] = ['May']
        self.doc['targets'][0].update(lemma='May', forms=['May'])
        self.doc['sentences'][0]['text'] = 'It may work.'
        self.refresh_hash()
        self.assertFalse(self.check()['passed'])
        self.doc['sentences'][0]['text'] = 'It starts in May.'
        self.refresh_hash()
        self.assertTrue(self.check()['passed'])

    def test_exact_source_target_lemma_and_pos_are_required(self):
        for field, value in [('target_id', 'made-up'), ('lemma', 'standing'), ('pos', 'n.')]:
            with self.subTest(field=field):
                before = self.doc['targets'][0][field]
                self.doc['targets'][0][field] = value
                self.refresh_hash()
                self.assertFalse(self.check()['passed'])
                self.doc['targets'][0][field] = before

    def test_morphology_requires_explicit_rationale_and_reviewer_forms(self):
        self.doc['targets'][0]['forms'] = ['standing']
        self.doc['sentences'][0]['text'] = 'I am standing here.'
        self.refresh_hash()
        self.assertFalse(self.check()['passed'])
        self.doc['targets'][0]['forms_rationale_zh'] = '动词 stand 的现在分词，用于进行时。'
        self.refresh_hash()
        self.assertFalse(self.check()['passed'])
        self.review['targets'][0]['forms'] = ['standing']
        self.assertTrue(self.check()['passed'], self.check())
        self.review['targets'][0]['forms'] = ['stand']
        self.assertFalse(self.check()['passed'])
        self.assertNotIn('approved_forms', self.sources['t1'])

    def test_explicit_forms_on_lemma_verdict_cannot_disagree(self):
        self.review['targets'][0]['forms'] = ['standing']
        self.assertFalse(self.check()['passed'])

    def test_inventory_exhaustiveness_overlap_and_unknown(self):
        mutations = [lambda: self.inventory['phases'].pop(),
                     lambda: self.inventory['phases'][1]['forms'].append('bank'),
                     lambda: self.inventory['phases'][1]['forms'].append('made-up'),
                     lambda: self.inventory['phases'][0]['forms'].append('stand'),
                     lambda: self.inventory['phases'].append(copy.deepcopy(self.inventory['phases'][0])),
                     lambda: self.inventory['pilot_forms'].append('stand')]
        for mutate in mutations:
            self.setUp()
            mutate()
            self.assertFalse(self.check()['passed'])

    def test_pinned_source_and_pilot_cannot_be_redefined(self):
        self.inventory['source_commit'] = 'new'
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.sources['t1']['source_commit'] = 'new'
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.inventory['pilot_forms'] = []
        self.inventory['phases'][0]['forms'].append('bank')
        self.assertFalse(self.check()['passed'])

    def test_phase_deferral_closes_disposition_not_coverage(self):
        self.deferrals['phase-02'] = [{'lemma': 'zebra', 'reason': 'Await a suitable animal observation scene.',
                                       'reason_category': 'needs-scene', 'source_target_ids': ['t4']}]
        result = self.check(['phase-02'])
        self.assertTrue(result['passed'], result)
        self.assertTrue(result['phases'][1]['complete'])
        self.assertEqual(result['phases'][1]['accepted_form_count'], 0)
        self.assertEqual(result['phases'][1]['deferred_form_count'], 1)
        self.assertEqual(result['phases'][1]['deferred_reason_counts'], {'needs-scene': 1})
        self.assertEqual(result['counts']['source_form_count'], 3)

    def test_deferred_word_must_account_for_all_source_records(self):
        self.documents = {}
        self.reviews = {}
        self.deferrals['phase-01'] = [{'lemma': 'stand', 'reason': 'Not resolved.', 'source_target_ids': ['t1']}]
        self.assertFalse(self.check()['passed'])
        self.deferrals['phase-01'][0]['source_target_ids'].append('t2')
        self.assertTrue(self.check(['phase-01'])['passed'])

    def test_invalid_duplicate_and_authored_deferrals_rejected(self):
        bad_rows = [{'lemma': 'zebra', 'reason': '', 'source_target_ids': ['t4']},
                    {'lemma': 'zebra', 'reason': 'Later', 'source_target_ids': ['t1']},
                    {'lemma': 'zebra', 'reason': 'Later', 'source_target_ids': ['t4'], 'reason_category': []},
                    {'lemma': 'bank', 'reason': 'Later', 'source_target_ids': ['t3']}]
        for row in bad_rows:
            self.deferrals = {'phase-02': [row]}
            self.assertFalse(self.check()['passed'])
        self.deferrals = {'phase-01': [{'lemma': 'stand', 'reason': 'Later', 'source_target_ids': ['t1', 't2']}]}
        self.assertFalse(self.check()['passed'])
        self.deferrals = {'phase-02': [{'lemma': 'zebra', 'reason': 'Later', 'source_target_ids': ['t4']}] * 2}
        self.assertFalse(self.check()['passed'])

    def test_global_deferral_keeps_denominator_and_requires_reason(self):
        self.inventory['phases'].pop()
        self.inventory['deferred'] = [{'lemma': 'zebra', 'reason': 'Explicitly out of this production scope.'}]
        result = self.check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['counts']['source_form_count'], 3)
        self.assertEqual(result['counts']['inventory_deferred_form_count'], 1)
        self.assertEqual(result['counts']['staged_accepted_form_count'], 1)
        self.inventory['deferred'][0]['reason'] = ''
        self.assertFalse(self.check()['passed'])

    def test_unknown_phase_and_unallocated_lemma(self):
        self.documents['phase-99'] = []
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.assertFalse(self.check(['phase-99'])['passed'])
        self.documents = {'phase-02': [self.doc]}
        self.reviews = {'phase-02': [self.review]}
        self.assertFalse(self.check()['passed'])

    def test_unknown_or_mismatched_taxonomy(self):
        mutations = [lambda: self.doc.update(topic_id='unknown'),
                     lambda: self.doc['scenario'].update(id='unknown'),
                     lambda: self.doc['scenario'].update(label_zh='Different'),
                     lambda: self.doc['scenario'].update(goal_zh='Different'),
                     lambda: self.taxonomy['scenarios'][0].update(topic_id='unknown')]
        for mutate in mutations:
            self.setUp()
            mutate()
            self.assertFalse(self.check()['passed'])

    def test_taxonomy_extension_is_additive_not_silent_override(self):
        extension = {'schema_version': 1, 'topics': [], 'scenarios': [
            {'id': 'new', 'topic_id': 'home', 'label_zh': '新情景', 'goal_zh': '新任务'}]}
        merged, errors = merge_taxonomy(self.taxonomy, extension)
        self.assertFalse(errors)
        self.assertEqual(len(merged['scenarios']), 2)
        extension['scenarios'][0]['id'] = 'move-chair'
        self.assertTrue(merge_taxonomy(self.taxonomy, extension)[1])

    def test_sense_identity_required_and_global_conflict_rejected(self):
        del self.doc['targets'][0]['sense_id']
        self.assertFalse(self.check()['passed'])
        self.setUp()
        doc2 = copy.deepcopy(self.doc)
        doc2['id'] = 'p01-second'
        doc2['targets'][0]['sense_zh'] = '经受得住'
        self.documents['phase-01'].append(doc2)
        self.assertFalse(self.check()['passed'])

    def test_same_sense_may_naturally_recur_without_inflating_coverage(self):
        doc2 = copy.deepcopy(self.doc)
        doc2['id'] = 'p01-second'
        self.documents['phase-01'].append(doc2)
        review2 = copy.deepcopy(self.review)
        review2['dialogue_id'] = doc2['id']
        review2['dialogue_sha256'] = sha256(json_bytes(doc2))
        self.hashes[doc2['id']] = review2['dialogue_sha256']
        self.reviews['phase-01'].append(review2)
        result = self.check(['phase-01'])
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['phases'][0]['accepted_dialogue_count'], 2)
        self.assertEqual(result['counts']['staged_accepted_form_count'], 1)
        self.assertEqual(result['counts']['staged_accepted_source_target_count'], 1)

    def test_duplicate_dialogue_ids_rejected(self):
        self.documents['phase-01'].append(copy.deepcopy(self.doc))
        self.assertFalse(self.check()['passed'])

    def test_malformed_dialogues_fail_without_exception(self):
        invalids = [None, [], {}, dict(self.doc, targets=None), dict(self.doc, targets=[None]),
                    dict(self.doc, sentences=None), dict(self.doc, participants=['A', 'A']),
                    dict(self.doc, participants=[{}]), dict(self.doc, scenario=None),
                    dict(self.doc, topic_id=[])]
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                self.documents = {'phase-01': [invalid]}
                self.assertFalse(self.check()['passed'])

    def test_malformed_inventory_fails_without_exception(self):
        invalids = [None, [], {}, dict(self.inventory, phases=[None]),
                    dict(self.inventory, phases=[{'id': {}, 'forms': []}]),
                    dict(self.inventory, pilot_forms=[{}]), dict(self.inventory, deferred=[None])]
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                self.inventory = invalid
                self.assertFalse(self.check()['passed'])

    def test_undeclared_speaker_and_duplicate_sentence_ids(self):
        self.doc['sentences'][0]['speaker'] = 'Unlisted'
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.doc['sentences'][1]['id'] = 's1'
        self.assertFalse(self.check()['passed'])

    def test_render_full_dialogue_and_only_accepted_original_words(self):
        result = self.check()
        outputs = render_outputs(result, self.documents, self.reviews, self.taxonomy)
        self.assertIn(b'Is this far enough?', outputs['phase-01/dialogues.md'])
        self.assertIn(b'sense-standing', outputs['phase-01/words.md'])
        self.assertNotIn(b'zebra', b'\n'.join(outputs.values()))
        self.assertNotIn(b'"source_record"', outputs['coverage.json'])
        self.reviews = {}
        outputs = render_outputs(self.check(), self.documents, self.reviews, self.taxonomy)
        self.assertNotIn(b'stand', outputs['phase-01/words.md'])
        self.assertIn(b'Please stand here.', outputs['phase-01/dialogues.md'])

    def test_scene_index_links_accepted_uses_only_across_phases(self):
        outputs = render_outputs(self.check(), self.documents, self.reviews, self.taxonomy)
        index = outputs['scene-index.md'].decode()
        self.assertIn('居家', index)
        self.assertIn('move-chair', index)
        self.assertIn('phase-01/dialogues.md#dialogue-p01-test', index)
        self.assertIn('scene-index.md', outputs['README.md'].decode())
        self.assertIn('id="dialogue-p01-test"', outputs['phase-01/dialogues.md'].decode())
        self.reviews = {}
        index = render_outputs(self.check(), self.documents, self.reviews, self.taxonomy)['scene-index.md'].decode()
        self.assertNotIn('p01-test', index)
        self.assertNotIn('move-chair', index)

    def test_private_deferral_details_not_published(self):
        self.deferrals = {'phase-02': [{'lemma': 'zebra', 'reason': 'PRIVATE DETAIL zebra', 'source_target_ids': ['t4']}]}
        result = self.check()
        outputs = render_outputs(result, self.documents, self.reviews, self.taxonomy)
        rendered = b'\n'.join(outputs.values())
        self.assertNotIn(b'PRIVATE DETAIL', rendered)
        self.assertNotIn(b'zebra', rendered)
        self.assertEqual(result['phases'][1]['deferred_reason_counts'], {'uncategorized': 1})

    def test_source_record_partition_counts_sum_to_denominator(self):
        result = self.check()
        c = result['counts']
        self.assertEqual(c['staged_accepted_source_target_count'] + c['staged_selected_without_accepted_usage_count'] +
                         c['source_records_not_selected_in_staged_count'], c['source_target_record_count'])
        self.reviews = {}
        result = self.check()
        self.assertEqual(result['counts']['staged_selected_without_accepted_usage_count'], 1)


class StagedCorpusFiles(unittest.TestCase):
    def prepare_files(self, folder):
        fixture = StagedCorpusChecks()
        fixture.setUp()
        commit = json.loads((ROOT / 'provenance/wordlists.json').read_text())['commit']
        fixture.inventory['source_commit'] = commit
        for source in fixture.sources.values():
            source['source_commit'] = commit
        corpus = folder / 'corpus'
        phase = corpus / 'phase-01'
        phase.mkdir(parents=True)
        deferrals = folder / 'private-deferrals'
        deferrals.mkdir()
        (phase / 'p01-test.json').write_bytes(json_bytes(fixture.doc))
        (phase / 'reviews.json').write_bytes(json_bytes([fixture.review]))
        (folder / 'inventory.json').write_bytes(json_bytes(fixture.inventory))
        (folder / 'targets.jsonl').write_text(''.join(json.dumps(v) + '\n' for v in fixture.sources.values()))
        (folder / 'taxonomy.json').write_bytes(json_bytes(fixture.taxonomy))
        (folder / 'pilot.json').write_bytes(json_bytes([{'lemma': 'bank'}]))
        arguments = ['--corpus-dir', str(corpus), '--inventory', str(folder / 'inventory.json'),
                     '--targets', str(folder / 'targets.jsonl'), '--taxonomy', str(folder / 'taxonomy.json'),
                     '--pilot-selection', str(folder / 'pilot.json'), '--deferrals-dir', str(deferrals)]
        return corpus, arguments

    def invoke(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(args)
        return status, json.loads(output.getvalue())

    def test_cli_generation_is_byte_reproducible_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, arguments = self.prepare_files(Path(temp))
            status, report = self.invoke(arguments + ['--write', '--require-phase', 'phase-01'])
            self.assertEqual(status, 0, report)
            initial = {p.relative_to(corpus): p.read_bytes() for p in corpus.rglob('*') if p.is_file()}
            self.assertEqual(self.invoke(arguments)[0], 0)
            self.assertEqual(self.invoke(arguments + ['--write'])[0], 0)
            self.assertEqual(initial, {p.relative_to(corpus): p.read_bytes() for p in corpus.rglob('*') if p.is_file()})
            (corpus / 'phase-01/words.md').write_text('tampered')
            self.assertEqual(self.invoke(arguments)[0], 1)
            self.assertEqual(self.invoke(arguments + ['--write'])[0], 0)
            doc = corpus / 'phase-01/p01-test.json'
            doc.write_bytes(doc.read_bytes() + b'\n')
            status, report = self.invoke(arguments)
            self.assertEqual(status, 1)
            self.assertTrue(any('sha256' in error for error in report['errors']))

    def test_empty_unstarted_phase_has_no_empty_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, args = self.prepare_files(Path(temp))
            self.assertEqual(self.invoke(args + ['--write'])[0], 0)
            self.assertFalse((corpus / 'phase-02').exists())

    def test_selection_without_pilot_review_bundle_never_counts_as_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, args = self.prepare_files(Path(temp))
            status, report = self.invoke(args + ['--write'])
            self.assertEqual(status, 0)
            self.assertFalse(report['pilot_validation']['passed'])
            self.assertNotIn('combined_accepted_form_count', report['counts'])

    def test_manifest_has_only_hash_of_private_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, args = self.prepare_files(Path(temp))
            self.assertEqual(self.invoke(args + ['--write'])[0], 0)
            manifest = read_json(corpus / 'manifest.json')
            self.assertEqual(len(manifest['local_input_sha256']['stage_inventory']), 64)
            self.assertNotIn('zebra', (corpus / 'manifest.json').read_text())
            self.assertNotIn('manifest.json', manifest['generated_output_sha256'])
            self.assertIn('scene-index.md', manifest['generated_output_sha256'])

    def test_duplicate_source_ids_and_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            corpus, args = self.prepare_files(folder)
            path = folder / 'targets.jsonl'
            path.write_text(path.read_text() * 2)
            self.assertEqual(self.invoke(args + ['--write'])[0], 1)
            path = folder / 'duplicate.json'
            path.write_text('{"status":"accepted", "status":"rejected"}')
            with self.assertRaises(ValueError):
                read_json(path)

    def test_receipts_ignored_but_malformed_dialogues_not_silently_lost(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, args = self.prepare_files(Path(temp))
            (corpus / 'phase-01/classification-author.json').write_bytes(json_bytes({'note': 'authorship receipt'}))
            self.assertEqual(self.invoke(args + ['--write'])[0], 0)
            (corpus / 'phase-01/p01-invalid.json').write_text('{}')
            self.assertEqual(self.invoke(args + ['--write'])[0], 1)

    def test_require_incomplete_phase_does_not_publish_false_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus, args = self.prepare_files(Path(temp))
            status, report = self.invoke(args + ['--write', '--require-phase', 'phase-02'])
            self.assertEqual(status, 1)
            self.assertFalse((corpus / 'manifest.json').exists())
            self.assertEqual(self.invoke(args + ['--write'])[0], 0)


class StagedIntegrationChecks(unittest.TestCase):
    def setUp(self):
        from tools.integrate_staged_phase import prepare_documents
        self.prepare = prepare_documents
        fixture = StagedCorpusChecks()
        fixture.setUp()
        self.docs = {'p01-test.json': fixture.doc}
        self.rows = [dict(row, cefr='A1', list='Synthetic') for row in fixture.sources.values()]
        self.base = fixture.taxonomy
        self.extension = {'schema_version': 1, 'topics': [], 'scenarios': []}

    def integrate(self):
        return self.prepare(self.docs, self.rows, self.base, self.extension)

    def test_enrichment_is_pure_idempotent_and_preserves_existing_identity(self):
        before = copy.deepcopy((self.docs, self.rows, self.base, self.extension))
        self.docs['p01-test.json']['content_version'] = 4
        before = copy.deepcopy((self.docs, self.rows, self.base, self.extension))
        docs, extension = self.integrate()
        doc = docs['p01-test.json']
        self.assertEqual(doc['targets'][0]['sense_id'], 'sense-standing')
        self.assertEqual(doc['content_version'], 4)
        self.assertEqual(doc['author'], 'writer-A')
        self.assertEqual(doc['targets'][0]['source_commit'], 'pinned')
        self.assertNotIn('reviews', doc)
        self.assertEqual(before, (self.docs, self.rows, self.base, self.extension))
        self.assertEqual((docs, extension), self.prepare(docs, self.rows, self.base, extension))

    def test_missing_sense_gets_stable_id_without_changing_meaning(self):
        del self.docs['p01-test.json']['targets'][0]['sense_id']
        docs, extension = self.integrate()
        target = docs['p01-test.json']['targets'][0]
        self.assertEqual(target['sense_id'], 'sense-staged-t1-p01-test')
        self.assertEqual(target['sense_zh'], '站立')
        self.assertEqual(target['target_id'], 't1')

    def test_failure_later_in_batch_does_not_mutate_inputs(self):
        new = copy.deepcopy(self.docs['p01-test.json'])
        new['id'] = 'p01-second'
        new['scenario']['id'] = 'new-scenario'
        self.docs['p01-test.json']['scenario']['id'] = 'first-new-scenario'
        new['targets'][0]['lemma'] = 'incorrect'
        self.docs['p01-second.json'] = new
        before = copy.deepcopy((self.docs, self.rows, self.base, self.extension))
        with self.assertRaises(ValueError):
            self.integrate()
        self.assertEqual(before, (self.docs, self.rows, self.base, self.extension))

    def test_conflicting_source_metadata_is_not_silently_overwritten(self):
        for key in ('lemma', 'pos', 'source_commit', 'cefr', 'list'):
            self.setUp()
            self.docs['p01-test.json']['targets'][0][key] = 'wrong'
            before = copy.deepcopy(self.docs)
            with self.assertRaises(ValueError):
                self.integrate()
            self.assertEqual(before, self.docs)

    def test_duplicate_sources_and_conflicting_taxonomy_rejected(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        with self.assertRaises(ValueError):
            self.integrate()
        self.setUp()
        conflicting = dict(self.base['scenarios'][0], goal_zh='Different task')
        self.extension['scenarios'].append(conflicting)
        with self.assertRaises(ValueError):
            self.integrate()
        self.setUp()
        self.base['topics'].append(copy.deepcopy(self.base['topics'][0]))
        with self.assertRaises(ValueError):
            self.integrate()

    def test_invalid_versions_are_rejected_not_reset(self):
        for key, value in [('scope_version', 'other'), ('content_version', 0),
                           ('content_version', True), ('content_version', '2')]:
            self.setUp()
            self.docs['p01-test.json'][key] = value
            with self.assertRaises(ValueError):
                self.integrate()

    def test_new_scenario_added_once_and_existing_conflicts_rejected(self):
        doc2 = copy.deepcopy(self.docs['p01-test.json'])
        doc2['id'] = 'p01-second'
        self.docs['p01-test.json']['scenario']['id'] = 'new-scenario'
        doc2['scenario']['id'] = 'new-scenario'
        self.docs['p01-second.json'] = doc2
        _, extension = self.integrate()
        self.assertEqual(len(extension['scenarios']), 1)
        doc2['scenario']['goal_zh'] = 'Conflicting task'
        with self.assertRaises(ValueError):
            self.integrate()

    def test_candidate_order_is_reproducible_for_reordered_sources(self):
        from tools.prepare_staged_inventory import allocate, SOURCE_COMMIT
        rows = [dict(row, source_commit=SOURCE_COMMIT) for row in self.rows]
        self.assertEqual(allocate(rows, [], phase_count=2, part_count=2),
                         allocate(list(reversed(rows)), [], phase_count=2, part_count=2))


class FrozenPilotVerificationChecks(unittest.TestCase):
    def test_combined_counts_require_separate_successful_frozen_pilot_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'dialogues').mkdir()
            sources, selection, reviews, targets, sentences = {}, [], [], [], []
            for i in range(100):
                tid, lemma, sid, pid = f't{i}', f'word{i}', f's{i}', f'p{i}'
                source = {'target_id': tid, 'lemma': lemma, 'pos': 'n.', 'list': 'Synthetic',
                          'cefr': 'A1', 'source_commit': 'pinned', 'approved_forms': [lemma]}
                sources[tid] = source
                row = {**{k: v for k, v in source.items() if k != 'approved_forms'},
                       'pilot_id': pid, 'sense_zh': '测试义项', 'selection_reason': 'Test fixture',
                       'usage_note_zh': '测试用法', 'scene_id': 'pilot', 'sentence_ids': [sid],
                       'selected': True, 'assigned': True, 'written': True,
                       'formal_checked': True, 'semantic_reviewed': True, 'return_reason': ''}
                selection.append(row)
                targets.append({'target_id': tid, 'lemma': lemma, 'forms': [lemma], 'sentence_ids': [sid]})
                sentences.append({'id': sid, 'speaker': 'A', 'text': f'The label is {lemma}.'})
                reviews.append({'pilot_id': pid, 'status': 'pass', 'note': 'Synthetic evidence test.'})
            (root / 'selection.json').write_bytes(json_bytes(selection))
            (root / 'reviews.json').write_bytes(json_bytes(reviews))
            (root / 'dialogues/pilot.json').write_bytes(json_bytes({'id': 'pilot', 'targets': targets, 'sentences': sentences}))
            report = {'counts': {'staged_accepted_form_count': 1, 'staged_accepted_source_target_count': 1,
                                 'source_records_not_selected_in_staged_count': 105}, 'passed': True, 'errors': []}
            hashes = verify_pilot(report, sources, root / 'selection.json')
            self.assertTrue(report['pilot_validation']['passed'], report)
            self.assertEqual(report['counts']['combined_accepted_form_count'], 101)
            self.assertEqual(report['counts']['other_unselected_source_target_count'], 5)
            self.assertIn('reviews.json', hashes)
            (root / 'reviews.json').write_bytes(json_bytes(reviews[:-1]))
            report = {'counts': {}, 'passed': True, 'errors': []}
            verify_pilot(report, sources, root / 'selection.json')
            self.assertFalse(report['passed'])
            self.assertNotIn('combined_accepted_form_count', report['counts'])


if __name__ == '__main__':
    unittest.main()
