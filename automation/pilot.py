"""Read-only SEO + conversion pilot. No traffic generation or site mutations."""
import argparse
import datetime as dt
import json
import math
import os
import ssl
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.rockbarfxxkup.com'
ROUTES = {'en': '/', 'ja': '/ja/', 'ko': '/ko/', 'th': '/th/'}
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly', 'https://www.googleapis.com/auth/webmasters.readonly']

def window(today=None):
    end = (today or dt.datetime.now(ZoneInfo('Asia/Tokyo')).date()) - dt.timedelta(days=3)
    return end-dt.timedelta(days=27), end

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

def audit(text, lang, url):
    doc = Document(text)
    attrs = lambda tag: [a for t,a in doc.tags if t == tag]
    canon = [a.get('href') for a in attrs('link') if a.get('rel') == 'canonical']
    alternate = {a.get('hreflang'):a.get('href') for a in attrs('link') if a.get('rel') == 'alternate'}
    checks = {
        'canonical': canon == [url],
        'language': any(a.get('lang') == lang for a in attrs('html')),
        'title': len(attrs('title')) == 1,
        'description': any(a.get('name') == 'description' and a.get('content') for a in attrs('meta')),
        'h1': len(attrs('h1')) == 1,
        'hreflang': all(alternate.get(l) == ORIGIN+r for l,r in ROUTES.items()),
        'indexable': not any(a.get('name') == 'robots' and 'noindex' in a.get('content','').lower() for a in attrs('meta')),
        'local_schema': 'BarOrPub' in text and 'PostalAddress' in text and 'openingHoursSpecification' in text,
        'maps_link': 'maps.app.goo.gl/95hYVdZMdPot4WQy5' in text,
        'instagram_link': 'instagram.com/rockbar_fxxkup' in text,
    }
    return checks

def public_get(url):
    req = Request(url, headers={'User-Agent':'FxxkupSEOAudit/0.1 (read-only weekly audit)'})
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    with urlopen(req, timeout=25, context=context) as response:
        if response.url.split('/')[2] not in ('rockbarfxxkup.com','www.rockbarfxxkup.com'):
            raise ValueError('unexpected redirect host')
        return response.read(2_000_000).decode('utf-8'), response.status, response.url

def api(url, body, credentials):
    from google.auth.transport.requests import Request as AuthRequest
    if not credentials.valid: credentials.refresh(AuthRequest())
    request = Request(url, data=json.dumps(body).encode(), headers={
        'Authorization':'Bearer '+credentials.token, 'Content-Type':'application/json'})
    import certifi
    with urlopen(request, timeout=45, context=ssl.create_default_context(cafile=certifi.where())) as response: return json.load(response)

def collect(start, end, request):
    """Paginate query opportunities separately from property totals (privacy limits apply)."""
    original_request=request
    errors=[]
    def request(url, body):
        try: return original_request(url,body)
        except Exception as exc:
            errors.append(('ga4' if 'analyticsdata' in url else 'gsc')+': '+type(exc).__name__)
            return {'unavailable':True}
    gsc_url = 'https://www.googleapis.com/webmasters/v3/sites/'+quote('sc-domain:rockbarfxxkup.com',safe='')+'/searchAnalytics/query'
    dates = {'startDate':str(start),'endDate':str(end),'dataState':'final','type':'web'}
    totals = request(gsc_url, dates)
    previous_end=dt.date.fromisoformat(str(start))-dt.timedelta(days=1)
    previous_start=previous_end-dt.timedelta(days=27)
    previous_totals=request(gsc_url,dict(dates,startDate=str(previous_start),endDate=str(previous_end)))
    rows=[]
    for offset in ([] if totals.get('unavailable') else range(0,100000,25000)):
        page=request(gsc_url, dict(dates, dimensions=['query','page','country','device'], rowLimit=25000,startRow=offset))
        batch=page.get('rows',[]); rows.extend(batch)
        if len(batch)<25000: break
    ga_url='https://analyticsdata.googleapis.com/v1beta/properties/559070143:runReport'
    ga=request(ga_url, {'dateRanges':[{'startDate':str(start),'endDate':str(end)}],
        'dimensions':[{'name':'sessionDefaultChannelGroup'},{'name':'language'}],
        'metrics':[{'name':x} for x in ['sessions','engagedSessions','keyEvents']],
        'dimensionFilter':{'filter':{'fieldName':'sessionDefaultChannelGroup','stringFilter':{'matchType':'EXACT','value':'Organic Search'}}},'limit':'10000'})
    return {'period':{'start':str(start),'end':str(end),'gsc_timezone':'America/Los_Angeles','ga_timezone':'property setting; verify'},
            'api_errors':errors,'gsc_totals':totals,'previous_gsc_period':[str(previous_start),str(previous_end)],'previous_gsc_totals':previous_totals,'gsc_rows':rows,'ga4_organic':ga,
            'ga4_truncated':ga.get('rowCount',0)>len(ga.get('rows',[])),
            'limits':'GSC top rows omit anonymized queries; GA4 metadata retained; never sum query rows as total.'}

def language(query):
    if any('\u0e00' <= c <= '\u0e7f' for c in query): return 'th'
    if any('\uac00' <= c <= '\ud7af' for c in query): return 'ko'
    if any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in query): return 'ja'
    return 'en'  # heuristic, not a user-language assertion

def opportunities(rows):
    grouped={}
    for r in rows:
        q=r['keys'][0]; g=grouped.setdefault(q,{'query':q,'language_hint':language(q),'clicks':0,'impressions':0,'weighted_position':0})
        g['clicks']+=r['clicks']; g['impressions']+=r['impressions']; g['weighted_position']+=r['position']*r['impressions']
    result=[]
    for g in grouped.values():
        n=g['impressions']; g['position']=g.pop('weighted_position')/n if n else None
        g['ctr']=g['clicks']/n if n else None
        if n >= 8 and g['ctr'] < .05:
            g['recommendation']='Review relevance and localized title/snippet; low volume, not proof of a problem. Verify query intent before changing copy.'
            result.append(g)
    return sorted(result,key=lambda x:x['impressions'],reverse=True)

def wilson(k,n):
    z=1.95996398454; p=k/n; d=1+z*z/n
    mid=(p+z*z/(2*n))/d
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return mid-half,mid+half

def analyze(events, plan):
    """One visitor, one exposure, one binary primary outcome; exports stay local."""
    seen={}; conversion={}; crossover=False
    for e in sorted(events,key=lambda e:dt.datetime.fromisoformat(e['timestamp'])):
        if e['experiment_id']!=plan['id'] or e.get('qa',False): continue
        v=e['visitor_id']; arm=e['variant']; t=dt.datetime.fromisoformat(e['timestamp'])
        if arm not in ('A','B') or t.tzinfo is None: raise ValueError('invalid arm or naive timestamp')
        if e['event']=='experiment_view':
            if v in seen and seen[v][0]!=arm: crossover=True
            seen.setdefault(v,(arm,t))
        elif e['event']==plan['primary_event'] and v in seen:
            first_arm,first=seen[v]
            if arm!=first_arm: crossover=True
            elif 0 <= (t-first).total_seconds() <= plan['conversion_hours']*3600: conversion[v]=True
    counts={arm:{'exposed':sum(a==arm for a,t in seen.values()),'converted':sum(v in conversion for v,(a,t) in seen.items() if a==arm)} for arm in ('A','B')}
    result={'status':'insufficient_evidence','counts':counts,'winner':None,'reasons':[]}
    n=sum(x['exposed'] for x in counts.values())
    if crossover: result['reasons'].append('cross-arm contamination')
    if not n: result['reasons'].append('no eligible visitor-level data'); return result
    chi=sum((x['exposed']-n/2)**2/(n/2) for x in counts.values())
    result['srm_p']=math.erfc(math.sqrt(chi/2))
    if result['srm_p'] < .01: result['reasons'].append('sample ratio mismatch')
    for arm,c in counts.items():
        if c['exposed']:
            c['rate']=c['converted']/c['exposed']; c['wilson95']=wilson(c['converted'],c['exposed'])
        if c['exposed']<plan['sample_per_arm']: result['reasons'].append('planned sample not reached: '+arm)
    if not plan['preregistered']: result['reasons'].append('prospective plan not registered; historical analysis descriptive only')
    if not plan['guardrails_reviewed']: result['reasons'].append('guardrails not reviewed')
    if plan['elapsed_days']<plan['min_days']: result['reasons'].append('minimum duration not reached')
    if not plan['window_mature']: result['reasons'].append('conversion window incomplete')
    if all(counts[a]['exposed'] for a in ('A','B')):
        a,b=counts['A'],counts['B']; result['absolute_lift']=b['rate']-a['rate']
        result['relative_lift']=b['rate']/a['rate']-1 if a['rate'] else None
        # Conservative interval from marginal Wilson bounds. Fixed-horizon only.
        result['lift95']=[b['wilson95'][0]-a['wilson95'][1],b['wilson95'][1]-a['wilson95'][0]]
        if not result['reasons'] and result['lift95'][0]>plan['minimum_absolute_lift']:
            result.update(status='recommend_B_for_review',winner='B')
    return result

def run(live=False, output=Path('reports'), events=None):
    output.mkdir(parents=True,exist_ok=True); start,end=window(); evidence={'run_at':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':'live-read-only' if live else 'offline-source','audit':{},'blockers':[]}
    for lang,route in ROUTES.items():
        try:
            if live: text,status,final=public_get(ORIGIN+route)
            else: text=(ROOT/'dist'/route.lstrip('/')/'index.html').read_text(); status,final=None,None
            evidence['audit'][lang]={'checks':audit(text,lang,ORIGIN+route),'status':status,'final_url':final}
        except Exception as exc: evidence['audit'][lang]={'error':type(exc).__name__}; evidence['blockers'].append('page read failed: '+lang)
    for name in ['robots.txt','sitemap.xml']:
        try:
            text=public_get(ORIGIN+'/'+name)[0] if live else (ROOT/'dist'/name).read_text()
            evidence[name]=text
        except Exception as exc: evidence['blockers'].append(name+': '+type(exc).__name__)
    evidence['experiment_history']=json.loads((ROOT/'automation/experiment-history.json').read_text())
    evidence['analytics']=None
    if live:
        try:
            import google.auth
            credentials,_=google.auth.default(scopes=SCOPES)
            evidence['analytics']=collect(start,end,lambda url,body:api(url,body,credentials))
            evidence['blockers'].extend(evidence['analytics']['api_errors'])
        except Exception as exc: evidence['blockers'].append('Google API baseline unavailable: '+type(exc).__name__+'; browser observations are separate')
    else: evidence['blockers'].append('Offline mode: no Google APIs called')
    plan=json.loads((ROOT/'automation/experiment-plan.json').read_text())
    evidence['experiment']=analyze([json.loads(l) for l in events.read_text().splitlines() if l.strip()] if events else [],plan)
    evidence['opportunities']=opportunities(evidence['analytics']['gsc_rows']) if evidence['analytics'] else []
    snapshot=json.loads((ROOT/'automation/baseline-observed.json').read_text())
    evidence['historical_browser_snapshot']=snapshot
    evidence['historical_opportunities']=opportunities(snapshot['gsc']['visible_rows'])
    (output/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
    lines=['# Weekly SEO + conversion pilot', '', 'Mode: '+evidence['mode'],'Generated: '+evidence['run_at'],'','## Technical evidence']
    for lang,a in evidence['audit'].items(): lines.append(f"- {lang}: "+(', '.join(k for k,v in a.get('checks',{}).items() if not v) or ('read failed' if 'error' in a else 'all implemented checks passed')))
    lines+=['','## Fresh API baseline',json.dumps({k:v for k,v in (evidence['analytics'] or {}).items() if k!='gsc_rows'},ensure_ascii=False,indent=2) if evidence['analytics'] else 'Unavailable; see blockers.','','## Search opportunities',json.dumps(evidence['opportunities'],ensure_ascii=False,indent=2) if evidence['opportunities'] else 'No fresh API query evidence. Do not invent keyword demand.', '', '## Historical browser evidence (not refreshed by this job)',json.dumps(evidence['historical_browser_snapshot'],ensure_ascii=False,indent=2),'## Historical query recommendations',json.dumps(evidence['historical_opportunities'],ensure_ascii=False,indent=2),'## Conversion experiment',json.dumps(evidence['experiment'],indent=2),'','## Blockers']+['- '+b for b in evidence['blockers']]
    lines+=['','## Required review','- Compare visible name, address, phone, hours and map destination with the verified Business Profile. No profile access was assumed.','- Review EN/JA evidence first; KO/TH hypotheses require observed queries or qualitative research.','- Keep existing B rollouts and current experiment ID/storage key. No ranking claim from visitor randomization.','- No automatic changes, merge, deployment, review solicitation, fabricated traffic or link creation.']
    (output/'weekly.md').write_text('\n'.join(lines)+'\n')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--live',action='store_true');p.add_argument('--output',type=Path,default=Path('reports'));p.add_argument('--events',type=Path)
    a=p.parse_args(); run(a.live,a.output,a.events)
