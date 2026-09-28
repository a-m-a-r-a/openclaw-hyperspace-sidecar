import unittest
from recall_query import prepare_recall_query, QUERY_MAX_BYTES


class RecallQueryTests(unittest.TestCase):
    def test_short_query_preserved(self):
        query, info = prepare_recall_query('Pamięć o Hyperspace')
        self.assertEqual(query, 'Pamięć o Hyperspace')
        self.assertFalse(info['shortened'])

    def test_multilingual_byte_budget_and_intent(self):
        original = 'Hyperspace ' + 'żółć 猫 🙂 ' * 900 + ' napraw recall'
        query, info = prepare_recall_query(original)
        self.assertLessEqual(len(query.encode()), QUERY_MAX_BYTES)
        self.assertTrue(query.startswith('Hyperspace'))
        self.assertTrue(query.endswith('napraw recall'))
        self.assertNotIn('\ufffd', query)
        self.assertTrue(info['shortened'])

    def test_prefetch_keeps_recent_input(self):
        query, info = prepare_recall_query('old context ' * 900 + 'current request', prefetch=True)
        self.assertTrue(query.endswith('current request'))
        self.assertLessEqual(info['sentBytes'], QUERY_MAX_BYTES)

    def test_whitespace_does_not_consume_budget(self):
        query, info = prepare_recall_query('memory' + ' \n' * 1000 + 'search')
        self.assertEqual(query, 'memory search')
        self.assertFalse(info['shortened'])


if __name__ == '__main__':
    unittest.main()
