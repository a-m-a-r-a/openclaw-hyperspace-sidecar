import json
import unittest
from bridge import analyze_curated_memories

class Provider:
    def __init__(self): self.calls=[]; self.missing=False; self.failed=False; self.ambiguous=False
    def handle_tool_call(self,name,args):
        self.calls.append((name,args))
        if name == 'hyperspace_search':
            if self.failed: return json.dumps({'ok':False,'error':'BACKEND_UNAVAILABLE'})
            result={'content':args['query'],'handle':'cap-'+args['query']}
            return json.dumps({'ok':True,'results':[] if self.missing else [result]*(2 if self.ambiguous else 1)})
        return json.dumps({'ok':True,'result':{'delta':0}})

class Cognitive(unittest.TestCase):
    def test_same_session_order_and_no_writes(self):
        p=Provider(); r=analyze_curated_memories(p,{'operation':'analyze_thought_stability','memories':['third','first','second']})
        self.assertTrue(r['ok']); self.assertEqual(p.calls[-1],('hyperspace_geometry',{'operation':'analyze_thought_stability','handles':['cap-third','cap-first','cap-second']}))
        self.assertEqual([n for n,a in p.calls],['hyperspace_search']*3+['hyperspace_geometry'])
    def test_missing_and_ambiguous_fail_closed(self):
        for flag in ['missing','ambiguous']:
            p=Provider(); setattr(p,flag,True)
            with self.assertRaises(ValueError): analyze_curated_memories(p,{'operation':'predict_momentum','memories':['a','b']})
            self.assertEqual(len(p.calls),1)
    def test_backend_error_not_geometry(self):
        p=Provider(); p.failed=True
        self.assertFalse(analyze_curated_memories(p,{'operation':'predict_momentum','memories':['a','b']})['ok'])
        self.assertEqual(len(p.calls),1)
    def test_invalid_input_before_search(self):
        for args in [dict(operation='trust_score',memories=['a','b','c']),dict(operation='analyze_geometry',memories=['a','b','c']),dict(operation='predict_momentum',memories=['a','a']),dict(operation='predict_relation',memories=['a','b'],steps=1),dict(operation='predict_relation',memories=['ą'*241,'b'])]:
            p=Provider()
            with self.assertRaises(ValueError): analyze_curated_memories(p,args)
            self.assertEqual(p.calls,[])
    def test_steps_passed_only_for_momentum(self):
        p=Provider(); analyze_curated_memories(p,dict(operation='predict_momentum',memories=['a','b'],steps=2))
        self.assertEqual(p.calls[-1][1]['steps'],2)
