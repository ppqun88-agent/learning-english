import copy
import unittest
from tools.check_pilot import check_pilot


class PilotChecks(unittest.TestCase):
    def setUp(self):
        self.targets = {'t1': {'target_id': 't1', 'lemma': 'stand', 'list': 'Oxford3000',
                              'cefr': 'A1', 'pos': 'v.', 'source_commit': 'abc',
                              'approved_forms': ['stand']}}
        self.rows = [{**{k: v for k, v in self.targets['t1'].items() if k != 'approved_forms'},
                      'pilot_id': 'p1', 'sense_zh': '站立', 'selection_reason': '常用动作',
                      'usage_note_zh': '表示站立', 'scene_id': 'scene1', 'sentence_ids': ['s1'],
                      'selected': True, 'assigned': True, 'written': True,
                      'formal_checked': False, 'semantic_reviewed': False, 'return_reason': ''}]
        self.docs = [{'id': 'scene1', 'sentences': [{'id': 's1', 'speaker': 'A', 'text': 'Stand here.'}],
                      'targets': [{'target_id': 't1', 'lemma': 'stand', 'forms': ['stand'],
                                   'sentence_ids': ['s1']}]}]
        self.reviews = [{'pilot_id': 'p1', 'status': 'pass', 'note': '动词义项与句子相符。'}]

    def check(self, expected_count=1):
        return check_pilot(self.rows, self.docs, self.targets, self.reviews, expected_count)

    def test_valid_and_flags_do_not_certify(self):
        result = self.check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['stored_formal_checked_count'], 0)
        self.assertEqual(result['semantic_review_pass_count'], 1)
        self.assertIn('NOT CERTIFIED', result['semantic_status'])

    def test_false_evidence_even_with_good_evidence(self):
        self.docs[0]['sentences'].append({'id': 's2', 'speaker': 'B', 'text': 'I understand.'})
        self.docs[0]['targets'][0]['sentence_ids'].append('s2')
        self.rows[0]['sentence_ids'].append('s2')
        self.rows[0]['formal_checked'] = True
        result = self.check()
        self.assertFalse(result['formal_pass'])
        self.assertTrue(any('evidence s2' in e for e in result['errors']))

    def test_source_mismatch(self):
        for key in ('lemma', 'list', 'cefr', 'pos', 'source_commit'):
            with self.subTest(key=key):
                original = self.rows[0][key]
                self.rows[0][key] = 'wrong'
                self.assertFalse(self.check()['formal_pass'])
                self.rows[0][key] = original

    def test_duplicate_words(self):
        row = copy.deepcopy(self.rows[0])
        row.update(pilot_id='p2', target_id='t2')
        self.rows.append(row)
        self.targets['t2'] = {**self.targets['t1'], 'target_id': 't2'}
        self.docs[0]['targets'].append({**self.docs[0]['targets'][0], 'target_id': 't2'})
        self.reviews.append({'pilot_id': 'p2', 'status': 'pass', 'note': 'reviewed'})
        self.assertTrue(any('distinct lemma' in e for e in self.check(2)['errors']))

    def test_missing_review_does_not_erase_formal_pass(self):
        self.reviews = []
        self.rows[0]['semantic_reviewed'] = True
        result = self.check()
        self.assertTrue(result['formal_pass'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['semantic_review_pass_count'], 0)
        self.assertTrue(any('review missing' in e for e in result['review_errors']))

    def test_revision_is_separate(self):
        self.reviews[0]['status'] = 'revise'
        result = self.check()
        self.assertTrue(result['formal_pass'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['semantic_review_revise_count'], 1)

    def test_duplicate_assignment(self):
        doc = copy.deepcopy(self.docs[0])
        doc['id'] = 'scene2'
        self.docs.append(doc)
        self.assertTrue(any('exactly once' in e for e in self.check()['errors']))

    def test_boolean_status_and_notes_required(self):
        self.rows[0]['selected'] = 'yes'
        self.assertFalse(self.check()['formal_pass'])
        self.rows[0]['selected'] = True
        self.rows[0]['usage_note_zh'] = ''
        self.assertFalse(self.check()['formal_pass'])

    def test_invalid_inputs_report_failure(self):
        for rows in (None, [None], [{}]):
            self.assertFalse(check_pilot(rows, [], {}, [], expected_count=1)['passed'])
        self.rows[0]['sentence_ids'] = [{}]
        self.assertFalse(self.check()['passed'])

    def test_explicit_regular_plural_approval(self):
        self.targets['t1'].update(lemma='nut', pos='n.', approved_forms=['nut'])
        self.rows[0].update(lemma='nut', pos='n.')
        self.docs[0]['targets'][0].update(lemma='nut', forms=['nuts'])
        self.docs[0]['sentences'][0]['text'] = 'Avoid nuts.'
        self.assertFalse(self.check()['formal_pass'])
        approval = {'target_id': 't1', 'lemma': 'nut', 'forms': ['nuts'], 'reason': 'Regular noun plural.'}
        result = check_pilot(self.rows, self.docs, self.targets, self.reviews,
                             expected_count=1, form_approvals=[approval])
        self.assertTrue(result['passed'])
        self.assertEqual(self.targets['t1']['approved_forms'], ['nut'])
        for field, wrong in [('lemma', 'ingredient'), ('forms', ['peanuts']), ('reason', '')]:
            with self.subTest(field=field):
                bad = {**approval, field: wrong}
                self.assertFalse(check_pilot(self.rows, self.docs, self.targets, self.reviews,
                                            expected_count=1, form_approvals=[bad])['formal_pass'])

    def test_duplicate_review(self):
        self.reviews *= 2
        self.assertFalse(self.check()['review_records_complete'])


if __name__ == '__main__':
    unittest.main()
