import unittest
from tools.prepare_staged_inventory import allocate, SOURCE_COMMIT


def row(lemma, tid, level='A1', pos='n.'):
    return {'lemma': lemma, 'target_id': tid, 'cefr': level, 'pos': pos, 'source_commit': SOURCE_COMMIT}


class StagedInventoryTests(unittest.TestCase):
    def test_partition_is_complete_deterministic_and_form_based(self):
        rows = [row('beta', 'b'), row('alpha', 'a'), row('alpha', 'a2', 'B2', 'v.'), row('gamma', 'g', 'C1')]
        inv, parts = allocate(rows, [rows[0]], 2, 2)
        self.assertEqual(inv['pilot_forms'], ['beta'])
        self.assertEqual([p['forms'] for p in inv['phases']], [['alpha'], ['gamma']])
        self.assertEqual(sum(len(x) for x in parts.values()), 2)
        self.assertEqual(len(parts[('phase-01', 2)][0]['candidates']), 2)
        self.assertEqual(inv, allocate(list(reversed(rows)), [rows[0]], 2, 2)[0])

    def test_untrusted_source_fails(self):
        r = row('word', 'a'); r['source_commit'] = 'changed'
        with self.assertRaises(ValueError): allocate([r], [])

    def test_duplicate_ids_fail(self):
        with self.assertRaises(ValueError): allocate([row('a', 'x'), row('b', 'x')], [])

    def test_unknown_level_fails(self):
        with self.assertRaises(ValueError): allocate([row('a', 'x', 'B3')], [])

    def test_unknown_or_wrong_pilot_fails(self):
        with self.assertRaises(ValueError): allocate([row('a', 'x')], [row('b', 'y')])
        with self.assertRaises(ValueError): allocate([row('a', 'x')], [row('a', 'y')])

    def test_duplicate_pilot_fails(self):
        r = row('a', 'x')
        with self.assertRaises(ValueError): allocate([r], [r, r])

    def test_empty_is_explicit(self):
        inv, parts = allocate([], [], 2, 3)
        self.assertEqual(sum(len(p['forms']) for p in inv['phases']), 0)
        self.assertEqual(len(parts), 6)

    def test_invalid_partition_fails(self):
        with self.assertRaises(ValueError): allocate([], [], 0, 3)
        with self.assertRaises(ValueError): allocate([], [], 1, 0)


if __name__ == '__main__': unittest.main()
