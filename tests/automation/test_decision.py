import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'automation'))
import decision as d
import weekly
from experiments import register,apply_decision

class Decisions(unittest.TestCase):
    def plan(self,**overrides):
        p=dict(id='example',enrollment_start='2026-10-01T00:00:00+00:00',
          enrollment_end='2026-10-15T00:00:00+00:00',analysis_at='2026-10-20T00:00:00+00:00',
          primary_event='directions_click',conversion_hours=24,preregistered=True,
          sample_per_arm=100,minimum_absolute_lift=.01,alpha=.05)
        return dict(p,**overrides)
    def events(self,ka=5,kb=50,n=100):
        events=[]
        for arm,k in [('A',ka),('B',kb)]:
            for i in range(n):
                e=dict(visitor_id=f'{arm}{i}',variant=arm,experiment_id='example',
                    timestamp='2026-10-02T00:00:00+00:00',event='experiment_view')
                events.append(e)
                if i<k:events.append(dict(e,event='directions_click',timestamp='2026-10-02T01:00:00+00:00'))
        return events
    def evaluate(self,events=None,plan=None,**kw):
        options=dict(coverage={'ok':True,'complete_through':'2026-10-19T00:00:00+00:00'},now=d.timestamp('2026-10-21T00:00:00+00:00'))
        options.update(kw)
        return d.evaluate(events if events is not None else self.events(),plan or self.plan(),**options)
    def test_b_wins(self):self.assertEqual(self.evaluate()['winner'],'B')
    def test_a_wins(self):self.assertEqual(self.evaluate(self.events(100,0))['winner'],'A')
    def test_null_finishes(self):self.assertEqual(self.evaluate(self.events(5,5))['status'],'completed_inconclusive')
    def test_no_weekly_significance_peeking(self):
        r=self.evaluate(now=d.timestamp('2026-10-10T00:00:00+00:00'))
        self.assertEqual(r['action'],'none');self.assertNotIn('p_value',r)
    def test_late_followup_holds(self):
        r=self.evaluate(coverage={'ok':True,'complete_through':'2026-10-15T00:00:00+00:00'})
        self.assertEqual(r['status'],'data_hold')
    def test_immature_visitors_not_denominator(self):
        r=self.evaluate(coverage={'ok':True,'complete_through':'2026-10-02T12:00:00+00:00'})
        self.assertEqual(r['counts']['A']['exposed'],0)
    def test_no_retroactive_registration(self):
        r=self.evaluate(plan=self.plan(preregistered=False))
        self.assertEqual(r['status'],'completed_descriptive');self.assertIsNone(r['winner'])
    def test_sample_shortfall_closes(self):
        r=self.evaluate(plan=self.plan(sample_per_arm=1000))
        self.assertEqual(r['status'],'completed_inconclusive')
    def test_missing_export_holds(self):
        self.assertEqual(self.evaluate(coverage={'ok':False,'complete_through':'2026-10-19T00:00:00+00:00'})['action'],'none')
    def test_crossovers_hold(self):
        events=self.events();events.append(dict(events[0],variant='B'))
        self.assertIn('cross-arm contamination',self.evaluate(events)['reasons'])
    def test_qa_excluded(self):
        r=self.evaluate([dict(e,qa=True) for e in self.events()]);self.assertEqual(r['counts']['A']['exposed'],0)
    def test_conversion_order_ties(self):
        events=self.events(1,1)
        for e in events:e['timestamp']='2026-10-02T00:00:00+00:00'
        r=self.evaluate(list(reversed(events)));self.assertEqual(r['counts']['A']['converted'],1)
    def test_conversions_late_and_before_exposure_ignored(self):
        events=self.events(0,0)
        events.extend([dict(events[0],event='directions_click',timestamp=t) for t in ['2026-10-01T23:00:00+00:00','2026-10-04T00:00:00+00:00']])
        self.assertEqual(self.evaluate(events)['counts']['A']['converted'],0)
    def test_fisher_reference(self):
        self.assertAlmostEqual(d.fisher(1,10,11,14),.0027594561852200836,places=10)
    def test_sample_plan(self):
        self.assertTrue(2200<d.sample_size(.05,.02)<2300)
    def test_failed_collection_preserves_last_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);weekly.write_json(root/'latest.json',{'run_id':'previous'})
            fake={'blockers':['API failed'],'audit':{},'analytics':None}
            with patch.object(weekly.pilot,'run',return_value=fake),patch.object(weekly.pilot,'public_get',side_effect=RuntimeError),patch.object(weekly,'export',side_effect=RuntimeError('BigQuery HTTP 403')):
                result=weekly.collect_run(root)
            self.assertEqual(result['status'],'degraded')
            self.assertEqual(json.loads((root/'latest.json').read_text())['run_id'],'previous')
            self.assertTrue(Path(result['evidence_path']).exists())

if __name__=='__main__':unittest.main()
