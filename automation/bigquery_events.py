"""Bounded read-only GA4 export; only aggregate diagnostics leave this module."""
import datetime as dt
import os
import re
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession

PROJECT='chuck-tech'
DATASET='analytics_559070143'
LOCATION='asia-northeast1'

def export(plan, now=None, session=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    # Allow three full days for late arrivals, and use property calendar dates.
    last=now.astimezone(ZoneInfo('Asia/Tokyo')).date()-dt.timedelta(days=4)
    start=dt.datetime.fromisoformat(plan['enrollment_start']).astimezone(ZoneInfo('Asia/Tokyo')).date()
    through=dt.datetime.combine(last+dt.timedelta(days=1),dt.time(),ZoneInfo('Asia/Tokyo'))
    coverage={'ok':False,'complete_through':through.isoformat(),'missing_dates':[]}
    if session is None:
        token=Path(os.environ.get('FXXKUP_BIGQUERY_TOKEN_FILE','~/.config/fxxkup-seo/bigquery-token.json')).expanduser()
        credentials=Credentials.from_authorized_user_file(str(token),['https://www.googleapis.com/auth/bigquery.readonly'])
        session=AuthorizedSession(credentials)
    base=f'https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}'
    def read(response):
        if not response.ok:
            raise RuntimeError(f'BigQuery HTTP {response.status_code}')
        return response.json()
    tables=set(); page=None
    for _ in range(50):
        payload=read(session.get(f'{base}/datasets/{DATASET}/tables',params={'pageToken':page} if page else {},timeout=30))
        tables.update(t['tableReference']['tableId'] for t in payload.get('tables',[]))
        page=payload.get('nextPageToken')
        if not page: break
    else: raise RuntimeError('table pagination exceeded budget')
    expected=[start+dt.timedelta(days=i) for i in range(max(0,(last-start).days+1))]
    coverage['missing_dates']=[str(d) for d in expected if 'events_'+d.strftime('%Y%m%d') not in tables]
    coverage['ok']=bool(expected) and not coverage['missing_dates']
    if not expected or not any('events_'+d.strftime('%Y%m%d') in tables for d in expected):
        return [],coverage
    sql=f"""SELECT user_pseudo_id,
 (SELECT value.string_value FROM UNNEST(event_params) WHERE key='experiment_id' LIMIT 1) experiment_id,
 (SELECT value.string_value FROM UNNEST(event_params) WHERE key='experiment_variant' LIMIT 1) variant,
 event_name,
 FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%E6SZ', TIMESTAMP_MICROS(event_timestamp)) timestamp,
 EXISTS(SELECT 1 FROM UNNEST(event_params) WHERE key IN ('qa','debug_mode')
 AND (value.int_value=1 OR LOWER(value.string_value) IN ('true','1','yes'))) qa
FROM `{PROJECT}.{DATASET}.events_*`
WHERE _TABLE_SUFFIX BETWEEN @start AND @end
AND user_pseudo_id IS NOT NULL
AND COALESCE(privacy_info.analytics_storage,'Unset') != 'No'
AND event_name IN ('experiment_view',@primary,'menu_open','instagram_click','phone_click')
AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key='experiment_id' LIMIT 1)=@experiment
ORDER BY event_timestamp
"""
    params={'start':start.strftime('%Y%m%d'),'end':last.strftime('%Y%m%d'),
            'primary':plan['primary_event'],'experiment':plan['id']}
    payload=read(session.post(f'{base}/queries',json={'query':sql,'useLegacySql':False,
        'location':LOCATION,'timeoutMs':10000,'maxResults':10000,'maximumBytesBilled':'1000000000',
        'parameterMode':'NAMED','queryParameters':[{'name':k,'parameterType':{'type':'STRING'},'parameterValue':{'value':v}} for k,v in params.items()]},timeout=45))
    job=payload.get('jobReference',{}).get('jobId')
    for _ in range(6):
        if payload.get('jobComplete'): break
        if not job: raise RuntimeError('query returned no job ID')
        payload=read(session.get(f'{base}/queries/{job}',params={'location':LOCATION,'timeoutMs':10000,'maxResults':10000},timeout=30))
    if not payload.get('jobComplete'): raise RuntimeError('query did not finish within budget')
    rows=list(payload.get('rows',[]))
    for _ in range(20):
        page=payload.get('pageToken')
        if not page: break
        payload=read(session.get(f'{base}/queries/{job}',params={'location':LOCATION,'pageToken':page,'maxResults':10000},timeout=30))
        rows.extend(payload.get('rows',[]))
    else: raise RuntimeError('event pagination exceeded budget')
    result=[]
    for row in rows:
        v,e,a,event,t,qa=[f.get('v') for f in row['f']]
        result.append({'visitor_id':v,'experiment_id':e,'variant':a,'event':event,'timestamp':t,'qa':str(qa).lower()=='true'})
    coverage['event_count']=len(result)
    coverage['query_job_id']=job
    return result,coverage
