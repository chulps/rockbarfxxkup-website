import copy
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'automation'))
import experiments as e
from decision import timestamp

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'source').mkdir();(self.root/'automation').mkdir()
        self.config=json.loads((e.ROOT/'source/experiments.json').read_text())
        self.config['firstVisit']['enabled']=False
        self.plan=dict(id=self.config['firstVisit']['id'],enrollment_start='2026-10-01T00:00:00+00:00',enrollment_end='2026-10-15T00:00:00+00:00')
        (self.root/'source/experiments.json').write_text(json.dumps(self.config))
        (self.root/'automation/experiment-plan.json').write_text(json.dumps(self.plan))
        self.now=timestamp('2026-10-21T12:00:00+00:00')
        self.summary={'status':'ready','generated_at':self.now.isoformat(),'run_id':'test',
            'experiment':{'experiment_id':self.plan['id'],'status':'completed_B','action':'promote_B',
                'counts':{'A':{'exposed':5000,'converted':500},'B':{'exposed':5000,'converted':500}}}}
        self.proposal={'id':'next_test','hypothesis':'Clearer welcome','evidence':'test data',
            'predicted_outcome':'More directions clicks','rollback':'Retain A',
            'minimum_absolute_lift':.05,'copy':self.config['firstVisit']['copy']}
    def tearDown(self):self.temp.cleanup()
    def test_registration_is_future_and_prospective(self):
        with patch.object(e,'sync_runtime'):
            plan=e.register(self.proposal,self.summary,self.now,self.root)
        self.assertTrue(plan['preregistered'])
        self.assertGreater(timestamp(plan['enrollment_start']),self.now)
        self.assertGreater(timestamp(plan['analysis_at']),timestamp(plan['enrollment_end']))
        self.assertIn('configuration_sha256',plan)
    def test_low_volume_cannot_force_launch(self):
        for c in self.summary['experiment']['counts'].values():c.update(exposed=10,converted=0)
        with self.assertRaisesRegex(ValueError,'insufficient measured baseline'):
            e.register(self.proposal,self.summary,self.now,self.root)
    def test_overlap_rejected(self):
        self.config['firstVisit']['enabled']=True
        (self.root/'source/experiments.json').write_text(json.dumps(self.config))
        with self.assertRaisesRegex(ValueError,'already active'):
            e.register(self.proposal,self.summary,self.now,self.root)
    def test_stale_report_rejected(self):
        self.summary['generated_at']='2026-10-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'fresh healthy'):
            e.register(self.proposal,self.summary,self.now,self.root)
    def test_apply_once_and_preserve_b(self):
        self.config['firstVisit']['enabled']=True
        (self.root/'source/experiments.json').write_text(json.dumps(self.config))
        with patch.object(e,'sync_runtime'):
            first=e.apply_decision(self.summary,self.root,self.now)
            second=e.apply_decision(self.summary,self.root,self.now)
        self.assertEqual(first,{'changed':True,'rollout':'B'})
        self.assertFalse(second['changed'])
    def test_wrong_experiment_never_applies(self):
        self.summary['experiment']['experiment_id']='other'
        with self.assertRaisesRegex(ValueError,'does not match'):
            e.apply_decision(self.summary,self.root,self.now)

if __name__=='__main__':unittest.main()
