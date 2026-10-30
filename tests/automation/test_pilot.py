import importlib.util
import datetime as dt
import json
import sys
import types
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from io import BytesIO
from unittest.mock import patch, MagicMock
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
    def test_gbp_website_separates_campaign_and_referral_diagnostics(self):
        calls = []
        def fake(url, body):
            calls.append(body)
            return {'rows': [], 'rowCount': 10001}
        result = p.collect_gbp_website('2026-09-29', '2026-10-26', fake)
        self.assertEqual(len(calls), 3)
        self.assertTrue(result['truncated'])
        self.assertEqual(calls[0]['dimensionFilter']['filter']['fieldName'], 'sessionCampaignName')
        self.assertEqual(calls[0]['dimensionFilter']['filter']['stringFilter']['value'], 'google_business_profile')
        self.assertEqual(calls[1]['metrics'], [{'name': 'eventCount'}, {'name': 'keyEvents'}])
        self.assertEqual(calls[2]['dimensionFilter']['filter']['fieldName'], 'sessionSourceMedium')
        self.assertNotIn('userId', str(calls))
        self.assertNotIn('pageLocation', str(calls))

    def test_gbp_snapshot_validation_and_freshness(self):
        good = dict(schema_version=1, source='ga4_business_profile_ui',
            scope='rock_bar_fxxk_up_only', period={'start':'2026-09-29', 'end':'2026-10-26'},
            observed_at='2026-10-27T08:00:00+09:00', metrics={'calls':1, 'directions':99})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'snapshot.json'
            def read(data):
                path.write_text(json.dumps(data))
                return p.read_gbp_import(path, dt.date(2026,10,28))
            self.assertEqual(read(good)['snapshot_age_days'], 1)
            for change in [dict(metrics={'calls':True}), dict(metrics={'calls':-1}),
                dict(metrics={'calls':'***'}), dict(metrics={'visitor_id':1}),
                dict(observed_at='2026-10-27T08:00:00'), dict(scope='unknown'),
                dict(secret='reject unknown fields'),
                dict(period={'start':'2026-10-28','end':'2026-10-26'})]:
                with self.assertRaises(ValueError): read(dict(good, **change))

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
    def test_http_permission_errors_are_actionable_without_logging_bodies(self):
        def fake(url,body):
            if 'analyticsdata' in url: raise HTTPError(url,403,'Forbidden',None,BytesIO(b'{"private":"not retained"}'))
            return {'rows':[]}
        result=p.collect('2026-10-01','2026-10-24',fake)
        self.assertEqual(result['api_errors'],['ga4: HTTP 403'])
    def test_oauth_requires_explicit_authorization(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict('os.environ', {'FXXKUP_OAUTH_TOKEN_FILE':str(Path(temp)/'missing.json')}, clear=False):
                with self.assertRaisesRegex(ValueError,'use --authorize'):
                    p.google_credentials()
    def test_oauth_token_is_saved_owner_only(self):
        with tempfile.TemporaryDirectory() as temp:
            token=Path(temp)/'private'/'google-token.json'
            credential=MagicMock();credential.to_json.return_value='{}'
            p.save_credentials(credential,token)
            self.assertEqual(token.read_text(),'{}')
            self.assertEqual(token.stat().st_mode & 0o777,0o600)
            self.assertEqual(token.parent.stat().st_mode & 0o777,0o700)
    def test_oauth_reuses_saved_valid_token(self):
        credentials=MagicMock(valid=True)
        with tempfile.TemporaryDirectory() as temp:
            token=Path(temp)/'token.json';token.write_text('{}')
            with patch('google.oauth2.credentials.Credentials.from_authorized_user_file',return_value=credentials) as load:
                self.assertIs(p.google_credentials(token_file=token),credentials)
            load.assert_called_once_with(str(token),p.SCOPES)
    def test_oauth_browser_flow_only_runs_when_authorized(self):
        with tempfile.TemporaryDirectory() as temp:
            client=Path(temp)/'desktop-client.json';client.write_text('{"installed":{}}')
            token=Path(temp)/'private'/'token.json'
            credentials=MagicMock();credentials.to_json.return_value='{"refresh_token":"test-only"}'
            flow=MagicMock();flow.run_local_server.return_value=credentials
            package=types.ModuleType('google_auth_oauthlib');module=types.ModuleType('google_auth_oauthlib.flow')
            flow_class=MagicMock();flow_class.from_client_secrets_file.return_value=flow
            module.InstalledAppFlow=flow_class
            with patch.dict(sys.modules,{'google_auth_oauthlib':package,'google_auth_oauthlib.flow':module}):
                self.assertIs(p.google_credentials(authorize=True,token_file=token,client_file=client),credentials)
            flow_class.from_client_secrets_file.assert_called_once_with(str(client),p.SCOPES)
            flow.run_local_server.assert_called_once_with(port=0,access_type='offline',prompt='consent')
            self.assertEqual(token.stat().st_mode & 0o777,0o600)
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
