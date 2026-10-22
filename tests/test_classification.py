import copy
import unittest
from tools.classify_pilot import load, render, validate_classification, PILOT


class ClassificationChecks(unittest.TestCase):
    def setUp(self):
        self.taxonomy, self.classification, self.selection, self.dialogues = load()

    def check(self):
        return validate_classification(self.taxonomy, self.classification, self.selection, self.dialogues)

    def test_current_pilot_and_generated_index(self):
        report = self.check()
        self.assertTrue(report['passed'], report)
        self.assertEqual(report['selected_sense_count'], 100)
        self.assertEqual(report['dialogue_count'], 10)
        self.assertEqual(report['attested_evidence_link_count'], 100)
        self.assertEqual(report['suggested_link_count'], 8)
        self.assertEqual(render(self.taxonomy, self.classification, self.dialogues),
                         (PILOT/'classification.md').read_text(encoding='utf-8'))

    def test_suggestion_does_not_count_as_attested(self):
        sense = self.classification['senses'][0]
        sense['scenario_links'].append({'scenario_id':'home-repair','status':'suggested','rationale_zh':'Potential future use.'})
        report = self.check()
        self.assertTrue(report['passed'], report)
        self.assertEqual(report['attested_evidence_link_count'], 100)
        self.assertEqual(report['suggested_link_count'], 9)

    def test_many_to_many_without_repetition_requirement(self):
        sense = self.classification['senses'][0]
        occurrence = sense['scenario_links'][0]['evidence'][0]
        old = next(d for d in self.dialogues if d['id'] == occurrence['dialogue_id'])
        new = copy.deepcopy(old)
        new['id'] = 'test-second-dialogue'
        self.dialogues.append(new)
        self.classification['dialogues'].append({'dialogue_id':new['id'], 'scenario_ids':['accommodation-change','home-repair']})
        sense['scenario_links'][0]['evidence'].append({'dialogue_id':new['id'],'sentence_ids':occurrence['sentence_ids'][:]})
        sense['scenario_links'].append({'scenario_id':'home-repair','status':'attested',
                                       'evidence':[{'dialogue_id':new['id'],'sentence_ids':occurrence['sentence_ids'][:]}]})
        report = self.check()
        self.assertTrue(report['passed'], report)
        # Only synthetic structural fixtures: no new pedagogical evidence is shipped.
        self.assertEqual(report['attested_evidence_link_count'], 102)

    def test_distinct_sense_for_same_target(self):
        sense = copy.deepcopy(self.classification['senses'][0])
        del sense['pilot_id']
        sense['sense_id'] = 'test-other-sense'
        sense['sense_zh'] = '保留意见（仅结构测试，不写入教材）'
        sense['scenario_links'] = [{'scenario_id':'survey-evidence','status':'suggested','rationale_zh':'Fixture only.'}]
        self.classification['senses'].append(sense)
        self.assertTrue(self.check()['passed'])
        self.assertEqual(self.check()['selected_sense_count'], 100)

    def test_new_sense_cannot_reuse_existing_sense_evidence(self):
        sense = copy.deepcopy(next(s for s in self.classification['senses'] if s['lemma'] == 'bank'))
        del sense['pilot_id']
        sense['sense_id'] = 'test-river-bank'
        sense['sense_zh'] = '河岸'
        self.classification['senses'].append(sense)
        self.assertFalse(self.check()['passed'])

    def test_missing_selected_sense(self):
        self.classification['senses'].pop()
        self.assertFalse(self.check()['passed'])

    def test_preserve_original_sense(self):
        self.classification['senses'][0]['sense_zh'] = 'different'
        self.assertFalse(self.check()['passed'])

    def test_duplicate_identifiers(self):
        for key in ('senses','dialogues'):
            with self.subTest(key=key):
                self.classification[key].append(copy.deepcopy(self.classification[key][0]))
                self.assertFalse(self.check()['passed'])
                self.classification[key].pop()

    def test_unknown_references(self):
        mutations = [lambda: self.taxonomy['scenarios'][0].update(topic_id='missing'),
                     lambda: self.classification['senses'][0].update(target_id='missing'),
                     lambda: self.classification['senses'][0]['scenario_links'][0].update(scenario_id='missing'),
                     lambda: self.classification['senses'][0]['scenario_links'][0]['evidence'][0].update(dialogue_id='missing')]
        for mutate in mutations:
            self.setUp()
            mutate()
            self.assertFalse(self.check()['passed'])

    def test_wrong_evidence_and_wrong_scenario(self):
        link = self.classification['senses'][0]['scenario_links'][0]
        link['evidence'][0]['sentence_ids'] = ['pilot01-booking-s06']
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.classification['senses'][0]['scenario_links'][0]['scenario_id'] = 'home-repair'
        self.assertFalse(self.check()['passed'])

    def test_suggested_cannot_replace_existing_evidence(self):
        self.classification['senses'][0]['scenario_links'] = [{'scenario_id':'accommodation-change','status':'suggested','rationale_zh':'Not evidence'}]
        self.assertFalse(self.check()['passed'])

    def test_suggestion_cannot_claim_evidence(self):
        self.classification['senses'][0]['scenario_links'][0]['status'] = 'suggested'
        self.classification['senses'][0]['scenario_links'][0]['rationale_zh'] = 'Potential use'
        self.assertFalse(self.check()['passed'])

    def test_schema_rejects_malformed_inputs(self):
        for value in (None, [], {}, {'schema_version':True}, {'unexpected':1}):
            self.classification = value
            self.assertFalse(self.check()['passed'])
        self.setUp()
        self.classification['dialogues'][0]['scenario_ids'] = 'accommodation-change'
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.classification['senses'][0]['scenario_links'][0]['evidence'][0]['sentence_ids'] = []
        self.assertFalse(self.check()['passed'])

    def test_unknown_fields_and_empty_text(self):
        self.classification['senses'][0]['meaning'] = 'typo'
        self.assertFalse(self.check()['passed'])
        self.setUp()
        self.taxonomy['topics'][0]['label_zh'] = ' '
        self.assertFalse(self.check()['passed'])


if __name__ == '__main__':
    unittest.main()
