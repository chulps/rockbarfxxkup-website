"""One collector, one immutable run, one atomic latest pointer. No LLM calls."""
import argparse
import datetime as dt
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
import pilot
from bigquery_events import export
from decision import evaluate
from site_pages import pages, audit_page

ROOT=Path(__file__).resolve().parents[1]

def write_json(path,data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.writing-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
            f.write('\n')
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def technical_checks(evidence):
    return not evidence['blockers'] and all(
        'error' not in a and all(a.get('checks',{}).values())
        for a in evidence['audit'].values())

def collect_run(report_root, offline=False):
    now=dt.datetime.now(dt.timezone.utc)
    run_id=now.astimezone(ZoneInfo('Asia/Tokyo')).strftime('%Y%m%dT%H%M%S%f%z')
    run_dir=report_root/'runs'/run_id
    run_dir.mkdir(parents=True)
    snapshot=report_root/'gbp-performance-import.json'
    if snapshot.exists(): shutil.copy2(snapshot,run_dir/snapshot.name)
    # Refresh access in memory: unattended runs need read access to saved credentials,
    # not write access to the global config directory.
    pilot.save_credentials=lambda *args:None
    evidence=pilot.run(not offline,run_dir)
    discovered=pages(ROOT)
    home_routes=set(pilot.ROUTES.values())
    for page in discovered:
        if page['route'] in home_routes: continue
        key=page['route']
        try:
            if offline:
                body=page['path'].read_text(); status=None
            else: body,status,_=pilot.public_get(page['url'])
            evidence['audit'][key]={'checks':audit_page(body,page),'status':status}
        except Exception as exc:
            evidence['audit'][key]={'error':type(exc).__name__}
            evidence['blockers'].append('page read failed: '+key)
    evidence['page_coverage']={'total':len(discovered),'routes':[p['route'] for p in discovered]}
    # A source/live mismatch is visible, rather than silently skipping new routes.
    if not offline:
        import xml.etree.ElementTree as ET
        from site_pages import NS
        try:
            live_urls={n.text for n in ET.fromstring(evidence['sitemap.xml']).findall('s:url/s:loc',NS)}
            if live_urls!={p['url'] for p in discovered}:
                evidence['blockers'].append('live sitemap differs from current source')
        except (KeyError,ET.ParseError): evidence['blockers'].append('live sitemap unavailable or invalid')
    plan=json.loads((ROOT/'automation/experiment-plan.json').read_text())
    events=[]
    coverage={'ok':False,'complete_through':None,'error':'offline mode'}
    if not offline:
        try: events,coverage=export(plan,now)
        except Exception as exc:
            coverage={'ok':False,'complete_through':None,'error':type(exc).__name__}
            if isinstance(exc,RuntimeError): coverage['error']=str(exc)
    evidence['cohort_coverage']=coverage
    ok=technical_checks(evidence)
    evidence['experiment']=evaluate(events,plan,coverage,now,checks_ok=ok)
    evidence['guardrail_events']={name:sum(e['event']==name and not e.get('qa') for e in events)
                                  for name in ('menu_open','instagram_click','phone_click')}
    evidence['business_profile_native']={
        'status':'not_connected','last_known_access':'Performance API application rejected; no business.manage authorization',
        'source':'Project SEO research dated 2026-10-30; not a fresh quota check',
        'website_campaign_available':bool((evidence.get('analytics') or {}).get('gbp_website')),
        'snapshot_available':bool(evidence.get('gbp_performance_snapshot')),
        'does_not_block_website_experiments':True}
    warnings=[]
    if not coverage.get('ok'): warnings.append('experiment export incomplete')
    if not ok: warnings.append('collection or technical checks failed')
    analytics=evidence.get('analytics') or {}
    for key in ('all_traffic','named_events','landing_pages','ga4_organic'):
        r=analytics.get(key,{})
        if r.get('rowCount',0)>len(r.get('rows',[])):
            warnings.append(key+' truncated')
        meta=r.get('metadata',{})
        if meta.get('subjectToThresholding') or meta.get('samplingMetadatas'):
            warnings.append(key+' thresholded or sampled')
    if warnings and evidence['experiment']['action']!='none':
        evidence['experiment'].update(action='none',status='data_hold')
        evidence['experiment']['reasons']+=warnings
    status='offline' if offline else ('ready' if not warnings else 'degraded')
    summary={'run_id':run_id,'generated_at':now.isoformat(),'status':status,
        'warnings':warnings,'experiment':evidence['experiment'],
        'evidence_path':str(run_dir/'evidence.json'),
        'native_business_profile':'unavailable; GA4 tagged website activity collected separately',
        'ai_model':'gpt-6-luna','ai_reasoning_effort':'high'}
    write_json(run_dir/'evidence.json',evidence)
    write_json(run_dir/'summary.json',summary)
    (run_dir/'weekly.md').write_text('# Weekly optimization evidence\n\n'+
        json.dumps(summary,indent=2,ensure_ascii=False)+'\n\n'+
        'Detailed source data: evidence.json. Raw visitor identities were processed in memory only.\n')
    # Never let an unsuccessful run erase a successful one.
    write_json(report_root/'last-attempt.json',summary)
    if status=='ready': write_json(report_root/'latest.json',summary)
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--offline',action='store_true')
    p.add_argument('--reports',type=Path,default=ROOT/'reports')
    a=p.parse_args()
    a.reports.mkdir(parents=True,exist_ok=True)
    with (a.reports/'.weekly.lock').open('a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another collector is running; no duplicate run started.');return 3
        try: result=collect_run(a.reports,a.offline)
        except Exception as exc:
            result={'status':'failed','error':type(exc).__name__,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat()}
            write_json(a.reports/'last-attempt.json',result)
        print(json.dumps(result,indent=2))
        return 0 if result['status']=='ready' else 2

if __name__=='__main__': sys.exit(main())
