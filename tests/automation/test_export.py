import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'automation'))
from bigquery_events import export

class Response:
    ok=True
    def __init__(self,data):self.data=data
    def json(self):return self.data

class Session:
    def __init__(self,tables):self.tables=tables;self.calls=[]
    def get(self,url,**kwargs):
        self.calls.append((url,kwargs))
        if url.endswith('/tables'):
            return Response({'tables':[{'tableReference':{'tableId':t}} for t in self.tables]})
        return Response({'jobComplete':True,'rows':[]})
    def post(self,url,**kwargs):
        self.calls.append((url,kwargs))
        return Response({'jobComplete':False,'jobReference':{'jobId':'test'}})

class ExportTests(unittest.TestCase):
    def test_gap_and_async_query(self):
        session=Session(['events_20261026','events_20261028'])
        events,coverage=export({'enrollment_start':'2026-10-26T00:00:00+09:00','id':'x','primary_event':'directions_click'},
            now=dt.datetime.fromisoformat('2026-11-01T12:00:00+09:00'),session=session)
        self.assertFalse(coverage['ok']);self.assertEqual(coverage['missing_dates'],['2026-10-27'])
        self.assertEqual(coverage['complete_through'],'2026-10-29T00:00:00+09:00')
        query=[c[1]['json'] for c in session.calls if 'json' in c[1]][0]
        self.assertTrue(query['query'].lstrip().startswith('SELECT'))
        self.assertEqual(query['maximumBytesBilled'],'1000000000')
        self.assertIn('debug_mode',query['query'])
    def test_no_tables_is_not_zero_traffic(self):
        _,coverage=export({'enrollment_start':'2026-10-26T00:00:00+09:00','id':'x','primary_event':'directions_click'},
          now=dt.datetime.fromisoformat('2026-10-31T12:00:00+09:00'),session=Session([]))
        self.assertFalse(coverage['ok'])

if __name__=='__main__':unittest.main()
