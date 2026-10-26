import importlib.util
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('pilot',Path(__file__).resolve().parents[2]/'automation/pilot.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PilotTests(unittest.TestCase):
    def plan(self,**kw):
        plan=dict(id='test',primary_event='directions_click',conversion_hours=24,sample_per_arm=100,minimum_absolute_lift=.01,min_days=14,elapsed_days=14,preregistered=True,guardrails_reviewed=True,window_mature=True)
        plan.update(kw);return plan
    def events(self,n=100,ka=5,kb=50):
        out=[]
        for arm,k in [('A',ka),('B',kb)]:
            for i in range(n):
                e=dict(visitor_id=f'{arm}{i}',variant=arm,experiment_id='test',timestamp='2026-10-01T00:00:00+00:00',event='experiment_view');out.append(e)
                if i<k: out.append(dict(e,event='directions_click',timestamp='2026-10-01T00:01:00+00:00'))
        return out
    def test_empty(self): self.assertIsNone(p.analyze([],self.plan())['winner'])
    def test_duplicates_and_pre_exposure(self):
        e=self.events(); e.append(dict(e[1]));e.append(dict(e[1],visitor_id='unexposed'))
        r=p.analyze(e,self.plan());self.assertEqual(r['counts']['A']['converted'],5);self.assertEqual(r['winner'],'B')
    def test_no_winner_gates(self):
        for kw in [dict(preregistered=False),dict(window_mature=False),dict(guardrails_reviewed=False),dict(elapsed_days=1),dict(sample_per_arm=1000)]:
            self.assertIsNone(p.analyze(self.events(),self.plan(**kw))['winner'])
    def test_null(self): self.assertIsNone(p.analyze(self.events(100,5,5),self.plan())['winner'])
    def test_srm(self):
        e=self.events()+[dict(visitor_id=str(i),variant='A',experiment_id='test',timestamp='2026-10-01T00:00:00+00:00',event='experiment_view') for i in range(500)]
        self.assertIn('sample ratio mismatch',p.analyze(e,self.plan())['reasons'])
    def test_crossovers(self):
        e=self.events();e.append(dict(e[0],variant='B'))
        self.assertIn('cross-arm contamination',p.analyze(e,self.plan())['reasons'])
    def test_late_conversion(self):
        e=self.events(100,0,0);e.append(dict(e[0],event='directions_click',timestamp='2026-10-03T00:00:00+00:00'))
        self.assertEqual(p.analyze(e,self.plan())['counts']['A']['converted'],0)
    def test_language(self):
        for q,l in [('札幌 ロックバー','ja'),('삿포로 록바','ko'),('บาร์ร็อก','th'),('rock bar sapporo','en')]: self.assertEqual(p.language(q),l)
    def test_window(self): self.assertEqual(p.window(dt.date(2026,10,27)),(dt.date(2026,9,27),dt.date(2026,10,24)))
    def test_source_audit(self):
        for l,r in p.ROUTES.items(): self.assertTrue(all(p.audit((p.ROOT/'dist'/r.lstrip('/')/'index.html').read_text(),l,p.ORIGIN+r).values()))
    def test_collect_separate_totals(self):
        calls=[]
        def fake(url,body):
            calls.append(body)
            return {'rows':[]} if 'dimensions' in body else {'rows':[{'clicks':14}]}
        r=p.collect('2026-10-01','2026-10-24',fake)
        self.assertEqual(r['gsc_totals']['rows'][0]['clicks'],14)
        self.assertEqual(calls[2]['startRow'],0)
        self.assertEqual(calls[3]['dimensionFilter']['filter']['stringFilter']['value'],'Organic Search')
    def test_partial_api_denial(self):
        def fake(url,body):
            if 'analyticsdata' in url: raise PermissionError('denied')
            return {'rows':[]}
        r=p.collect('2026-10-01','2026-10-24',fake)
        self.assertEqual(r['gsc_totals'],{'rows':[]})
        self.assertEqual(r['api_errors'],['ga4: PermissionError'])
    def test_runtime_to_analysis(self):
        import subprocess
        js = """
const {page,link}=require('./tests/experiment-rollout.cjs');
const p=page({enabled:true,random:.9});
p.observe(.25);p.observe(.8);p.click(link('directions_click','hero',{hero:true}));
console.log(JSON.stringify(p.events.map((e,i)=>({visitor_id:'test-only',experiment_id:e[2].experiment_id,variant:e[2].experiment_variant,event:e[1],timestamp:'2026-10-01T00:00:0'+i+'+00:00'}))));
"""
        out=subprocess.check_output(['node','-e',js],cwd=p.ROOT,text=True)
        events=json.loads(out.strip().splitlines()[-1])
        plan=self.plan(id='first_visit_confidence_2026_10_v1')
        result=p.analyze(events,plan)
        self.assertEqual(result['counts']['B']['exposed'],1)
        self.assertEqual(result['counts']['B']['converted'],1)
        self.assertIsNone(result['winner'])
    def test_workflow_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            r=p.run(output=Path(temp));self.assertTrue((Path(temp)/'weekly.md').exists());self.assertIsNone(r['experiment']['winner'])

if __name__=='__main__': unittest.main()
