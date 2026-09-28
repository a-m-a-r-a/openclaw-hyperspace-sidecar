import tempfile
import unittest
from pathlib import Path
from bridge import apply_curated_write, probe_readback

class FakeProvider:
    def __init__(self): self.calls=[]
    def _apply_memory_event(self,*args): self.calls.append(args)

class CuratedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"ledger.sqlite3"
        self.provider=FakeProvider()
    def tearDown(self): self.tmp.cleanup()
    def test_add_routes_to_curated_event_with_provenance(self):
        result=apply_curated_write(self.provider,{"content":"durable fact","metadata":{"source_ref":"synthetic"}},self.path)
        self.assertTrue(result["ok"])
        call=self.provider.calls[0]
        self.assertEqual(call[:3],("add","openclaw-curated","durable fact"))
        self.assertEqual(call[3]["curator"],"owner")
    def test_replace_remove_require_exact_old_content(self):
        for op in ["replace","remove"]:
            with self.assertRaises(ValueError): apply_curated_write(self.provider,{"operation":op,"content":"new"},self.path)
        apply_curated_write(self.provider,{"operation":"replace","content":"new","oldContent":"old"},self.path)
        self.assertEqual(self.provider.calls[0][3]["old_text"],"old")
    def test_byte_budget_never_truncates(self):
        with self.assertRaises(ValueError): apply_curated_write(self.provider,{"content":"ą"*241},self.path)
        self.assertEqual(self.provider.calls,[])
    def test_errors_not_reported_as_success(self):
        self.provider._apply_memory_event=lambda *args: (_ for _ in ()).throw(RuntimeError("backend failed"))
        with self.assertRaises(RuntimeError): apply_curated_write(self.provider,{"content":"fact"},self.path)

    def test_readback_probe_never_claims_verified_write(self):
        calls=[]
        self.provider._call=lambda *args,**kwargs: calls.append((args,kwargs)) or []
        self.assertEqual(probe_readback(self.provider,"synthetic"),
                         {"readback_available":True,"write_verification":"not_tested"})
        self.assertEqual(calls,[(('get_points',[]),{'collection':'synthetic'})])

    def test_readback_error_is_visible_without_error_payload(self):
        self.provider._call=lambda *args,**kwargs: (_ for _ in ()).throw(RuntimeError("private backend payload"))
        self.assertEqual(probe_readback(self.provider,"synthetic"),
                         {"readback_available":False,"write_verification":"blocked","readback_error":"RuntimeError"})
