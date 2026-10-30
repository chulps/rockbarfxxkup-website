"""Code-owned experiment registration, bounded configuration edits and decisions."""
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo
from decision import sample_size, timestamp
from weekly import write_json

ROOT=Path(__file__).resolve().parents[1]
LANGUAGES={'en','ja','ko','th','zh-Hans'}

def config_hash(config):
    return hashlib.sha256(json.dumps(config,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def validate_copy(copy):
    if set(copy)!=LANGUAGES: raise ValueError('all five languages required')
    for language,c in copy.items():
        if set(c)!={'headline','lines','supporting'}: raise ValueError('copy keys must match runtime contract')
        if not isinstance(c['lines'],list) or not 1<=len(c['lines'])<=4: raise ValueError('one to four headline lines required')
        values=[c['headline'],c['supporting'],*c['lines']]
        if any(not isinstance(v,str) or not v.strip() or len(v)>280 or '<' in v or '>' in v for v in values):
            raise ValueError('copy must be bounded plain text')
        if len(c['headline'])>160 or any(len(v)>80 for v in c['lines']):
            raise ValueError('headline too long')

def sync_runtime(root=ROOT):
    config=json.loads((root/'source/experiments.json').read_text())
    runtime=(root/'dist/experiments.js').read_text().replace('</','<\\/')
    encoded=json.dumps(config,ensure_ascii=False).replace('</','<\\/')
    for route in ('','ja','ko','th','zh-hans'):
        path=root/'dist'/route/'index.html'
        body=path.read_text()
        body,n=re.subn(r'(<script>\s*window\.FXXKUP_EXPERIMENT_CONFIG=).*?(</script>)',
                       lambda m:m[1]+encoded+';'+m[2],body,flags=re.S)
        if n!=1: raise ValueError('missing or duplicate experiment configuration: '+route)
        body,n=re.subn(r'(<script data-site-module="experiments">).*?(</script>)',
                       lambda m:m[1]+runtime+m[2],body,flags=re.S)
        if n!=1: raise ValueError('missing or duplicate runtime: '+route)
        path.write_text(body)

def register(proposal, summary, now=None, root=ROOT):
    now=now or dt.datetime.now(dt.timezone.utc)
    plan=json.loads((root/'automation/experiment-plan.json').read_text())
    config=json.loads((root/'source/experiments.json').read_text())
    current=config['firstVisit']
    if current.get('enabled'): raise ValueError('an experiment is already active; do not overlap tests')
    if summary['status']!='ready' or now-timestamp(summary['generated_at'])>dt.timedelta(hours=24):
        raise ValueError('fresh healthy evidence required')
    if not re.fullmatch(r'[a-z][a-z0-9_]{5,90}',proposal['id']): raise ValueError('invalid experiment ID')
    history_path=root/'automation/lifecycle.json'
    history=json.loads(history_path.read_text()) if history_path.exists() else []
    if proposal['id']==plan['id'] or any(h.get('id')==proposal['id'] for h in history):
        raise ValueError('experiment ID already used')
    for key in ('hypothesis','evidence','predicted_outcome','rollback'):
        if not isinstance(proposal.get(key),str) or not proposal[key].strip(): raise ValueError(key+' is required')
    validate_copy(proposal['copy'])
    # Planning inputs come from the actual previous mature cohort, not LLM estimates.
    counts=summary['experiment']['counts']
    n=sum(c['exposed'] for c in counts.values())
    k=sum(c['converted'] for c in counts.values())
    prior_start=timestamp(plan['enrollment_start'])
    prior_end=min(timestamp(plan['enrollment_end']),now)
    days=max(1,(prior_end-prior_start).total_seconds()/86400)
    if n<100 or k<5 or k>=n: raise ValueError('insufficient measured baseline for a powered test')
    mde=float(proposal['minimum_absolute_lift'])
    if not 0<mde<1: raise ValueError('invalid minimum lift')
    needed=sample_size(k/n,mde)
    projected_days=needed*2/(n/days)
    if projected_days>84: raise ValueError('test is not feasible within 84 days at measured enrollment rate')
    duration=max(14,min(84,int(projected_days*1.2)+1))
    start=(now.astimezone(ZoneInfo('Asia/Tokyo'))+dt.timedelta(days=2)).replace(hour=0,minute=0,second=0,microsecond=0)
    end=start+dt.timedelta(days=duration)
    new_plan={'schema_version':2,'id':proposal['id'],'primary_event':'directions_click',
        'conversion_hours':24,'sample_per_arm':needed,'minimum_absolute_lift':mde,'alpha':.05,
        'preregistered':True,'registered_at':now.isoformat(),'enrollment_start':start.isoformat(),
        'enrollment_end':end.isoformat(),'analysis_at':(end+dt.timedelta(days=5)).isoformat(),
        'baseline':{'exposed':n,'converted':k,'rate':k/n,'observed_days':days},
        'planning_method':'equal-allocation two-proportion normal approximation, 80% power; final two-sided Fisher exact test',
        'mode':'fixed_horizon','proposal':proposal,'min_days':14}
    if current.get('rolloutVariant')=='B': current['controlCopy']=current['copy']
    current.update(id=proposal['id'],storageKey='fxxkup_'+proposal['id'],enabled=True,
        allocation=.5,copy=proposal['copy'],rolloutVariant='A',startsAt=start.isoformat(),endsAt=end.isoformat())
    new_plan['configuration_sha256']=config_hash(current)
    history.append({'id':proposal['id'],'status':'registered_pending_deployment','at':now.isoformat(),
                    'previous_plan':plan,'previous_configuration':json.loads((root/'source/experiments.json').read_text())})
    write_json(root/'automation/experiment-plan.json',new_plan)
    write_json(root/'source/experiments.json',config)
    write_json(history_path,history)
    sync_runtime(root)
    return new_plan

def apply_decision(summary,root=ROOT,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    if summary['status']!='ready' or now-timestamp(summary['generated_at'])>dt.timedelta(hours=24):
        raise ValueError('fresh healthy evidence required')
    decision=summary['experiment']
    if decision['action'] not in ('promote_B','retain_A'): return {'changed':False,'reason':'no terminal decision'}
    plan=json.loads((root/'automation/experiment-plan.json').read_text())
    config=json.loads((root/'source/experiments.json').read_text())
    current=config['firstVisit']
    if decision['experiment_id']!=plan['id'] or current['id']!=plan['id']:
        raise ValueError('decision does not match current experiment')
    if plan.get('configuration_sha256') and config_hash(current)!=plan['configuration_sha256']:
        if not current.get('enabled'): return {'changed':False,'reason':'already completed'}
        raise ValueError('configuration changed during experiment')
    if not current.get('enabled'): return {'changed':False,'reason':'already completed'}
    current.update(enabled=False,rolloutVariant='B' if decision['action']=='promote_B' else 'A')
    history_path=root/'automation/lifecycle.json'
    history=json.loads(history_path.read_text()) if history_path.exists() else []
    history.append({'id':plan['id'],'status':decision['status'],'at':now.isoformat(),
                    'run_id':summary['run_id'],'decision':decision,'pending_deployment':True})
    write_json(root/'source/experiments.json',config)
    write_json(history_path,history)
    sync_runtime(root)
    return {'changed':True,'rollout':current['rolloutVariant']}

def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['sync','register','apply'])
    p.add_argument('--proposal',type=Path);p.add_argument('--summary',type=Path,default=ROOT/'reports/latest.json')
    a=p.parse_args()
    if a.command=='sync': sync_runtime();return
    summary=json.loads(a.summary.read_text())
    if a.command=='register': result=register(json.loads(a.proposal.read_text()),summary)
    else: result=apply_decision(summary)
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
