import unittest
import tempfile
from pathlib import Path
from tools.pipeline import contains, validate, import_source
class Checks(unittest.TestCase):
    def test_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data/en"; p.mkdir(parents=True)
            (p/"categories.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                import_source(d,Path(d)/"out")
    def test_boundaries(self):
        self.assertFalse(contains('understand','stand'))
        self.assertTrue(contains('Stand here.','stand'))
        self.assertFalse(contains('I may go.','May'))
        self.assertTrue(contains('In May.','May'))
        self.assertFalse(contains('standing','stand'))
    def setUp(self):
        self.targets={'t1':{'lemma':'stand','approved_forms':['stand']}}
        self.doc={'id':'s1','sentences':[{'id':'1','speaker':'A','text':'Stand here.'}],'targets':[{'target_id':'t1','lemma':'stand','forms':['stand'],'sentence_ids':['1']}]}
    def test_valid_not_semantic(self):
        r=validate(self.doc,self.targets)
        self.assertTrue(r['formal_pass']); self.assertIn('NOT VERIFIED',r['semantic_status'])
    def test_bad_reference(self):
        self.doc['targets'][0]['sentence_ids']=['x']; self.assertFalse(validate(self.doc,self.targets)['formal_pass'])
    def test_unapproved(self):
        self.doc['targets'][0]['forms']=['standing']; self.assertFalse(validate(self.doc,self.targets)['formal_pass'])
    def test_unknown_target(self):
        self.doc['targets'][0]['target_id']='fake'; self.assertFalse(validate(self.doc,self.targets)['formal_pass'])
    def test_bad_schema(self):
        self.assertFalse(validate([],self.targets)["formal_pass"])
        self.doc["sentences"][0]["speaker"]=""
        self.assertFalse(validate(self.doc,self.targets)["formal_pass"])
    def test_duplicate(self):
        self.doc['sentences']*=2; self.assertFalse(validate(self.doc,self.targets)['formal_pass'])
    def test_no_substring_coverage(self):
        self.doc['sentences'][0]['text']='I understand.'; self.assertFalse(validate(self.doc,self.targets)['formal_pass'])
if __name__=='__main__': unittest.main()
