"""Deterministic, fixed-horizon experiment decisions. No LLM or network calls."""
import datetime as dt
import math
from statistics import NormalDist

UTC = dt.timezone.utc

def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timezone required')
    return parsed.astimezone(UTC)

def sample_size(baseline, mde, power=.8, alpha=.05):
    """Prospective two-proportion normal approximation, equal allocation."""
    p, q = baseline, baseline + mde
    if not 0 < p < q < 1:
        raise ValueError('baseline and baseline + MDE must be between zero and one')
    pooled = (p+q)/2
    z = NormalDist().inv_cdf(1-alpha/2)
    zp = NormalDist().inv_cdf(power)
    return math.ceil((z*math.sqrt(2*pooled*(1-pooled)) +
                      zp*math.sqrt(p*(1-p)+q*(1-q)))**2 / mde**2)

def fisher(a, na, b, nb):
    """Two-sided Fisher exact p-value, conditional on margins."""
    def choose(n,k):
        return math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)
    total = a+b
    def logprob(k):
        return choose(na,k)+choose(nb,total-k)-choose(na+nb,total)
    observed = logprob(a)
    return min(1., sum(math.exp(logprob(k)) for k in
                      range(max(0,total-nb), min(na,total)+1)
                      if logprob(k) <= observed+1e-10))

def evaluate(events, plan, coverage, now=None, checks_ok=True):
    now = now or dt.datetime.now(UTC)
    start, end = timestamp(plan['enrollment_start']), timestamp(plan['enrollment_end'])
    final = timestamp(plan['analysis_at'])
    watermark = timestamp(coverage['complete_through']) if coverage.get('complete_through') else start
    hours = dt.timedelta(hours=plan.get('conversion_hours',24))
    seen, converted, crossovers = {}, set(), set()
    excluded = {'qa':0, 'immature':0, 'outside_enrollment':0, 'invalid':0}
    valid = []
    for event in events:
        if event.get('experiment_id') != plan['id']:
            continue
        if event.get('qa'):
            excluded['qa'] += 1
            continue
        try:
            t=timestamp(event['timestamp'])
            if not event.get('visitor_id') or event.get('variant') not in ('A','B'):
                raise ValueError('invalid identity/arm')
            valid.append((t,event))
        except (KeyError,ValueError,TypeError):
            excluded['invalid'] += 1
    # Exposure before conversion at identical timestamps (GA4 batches can tie).
    valid.sort(key=lambda item:(item[0],item[1]['event']!='experiment_view'))
    for t,e in valid:
        v,arm=e['visitor_id'],e['variant']
        if e['event']=='experiment_view':
            if v in seen and seen[v][0]!=arm:
                crossovers.add(v)
            if start <= t < end:
                seen.setdefault(v,(arm,t))
            else:
                excluded['outside_enrollment']+=1
        elif e['event']==plan['primary_event'] and v in seen:
            first_arm,first=seen[v]
            if arm != first_arm:
                crossovers.add(v)
            elif first <= t <= first+hours and t < watermark:
                converted.add(v)
    mature={v:(a,t) for v,(a,t) in seen.items() if t+hours < watermark}
    excluded['immature']=len(seen)-len(mature)
    counts={a:{'exposed':sum(arm==a for arm,t in mature.values()),
               'converted':sum(v in converted and arm==a for v,(arm,t) in mature.items())}
            for a in ('A','B')}
    reasons=[]
    n=sum(c['exposed'] for c in counts.values())
    srm=math.erfc(math.sqrt(sum((c['exposed']-n/2)**2/(n/2) for c in counts.values())/2)) if n else None
    if not coverage.get('ok'): reasons.append('export coverage incomplete')
    if crossovers: reasons.append('cross-arm contamination')
    if excluded['invalid']: reasons.append('invalid cohort events')
    if srm is not None and srm<.01: reasons.append('sample ratio mismatch')
    if not checks_ok: reasons.append('technical validation failed')
    result={'experiment_id':plan['id'],'status':'collecting','action':'none',
            'counts':counts,'excluded':excluded,'srm_p':srm,'reasons':reasons,
            'analysis_at':plan['analysis_at'],'winner':None}
    for c in counts.values():
        c['rate']=c['converted']/c['exposed'] if c['exposed'] else None
    # No repeated significance decisions. Only a technical failure can stop early.
    if now < final:
        if not checks_ok:
            result.update(status='technical_stop',action='retain_A')
        elif reasons:
            result['status']='data_hold'
        return result
    if watermark < end+hours:
        reasons.append('conversion follow-up incomplete')
    if reasons:
        result['status']='data_hold'
        return result
    if not plan.get('preregistered'):
        result.update(status='completed_descriptive',action='retain_A')
        return result
    if any(c['exposed'] < plan['sample_per_arm'] for c in counts.values()):
        result.update(status='completed_inconclusive',action='retain_A')
        reasons.append('planned sample not reached by fixed deadline')
        return result
    a,b=counts['A'],counts['B']
    p=fisher(a['converted'],a['exposed'],b['converted'],b['exposed'])
    lift=b['rate']-a['rate']
    result.update(p_value=p,absolute_lift=lift)
    if p <= plan.get('alpha',.05) and lift >= plan['minimum_absolute_lift']:
        result.update(status='completed_B',action='promote_B',winner='B')
    elif p <= plan.get('alpha',.05) and lift <= -plan['minimum_absolute_lift']:
        result.update(status='completed_A',action='retain_A',winner='A')
    else:
        result.update(status='completed_inconclusive',action='retain_A')
    return result
