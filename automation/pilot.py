"""Read-only SEO + conversion pilot. No traffic generation or site mutations."""
import argparse
import datetime as dt
import json
import math
import os
import tempfile
import ssl
from pathlib import Path
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.rockbarfxxkup.com'
ROUTES = {'en': '/', 'ja': '/ja/', 'ko': '/ko/', 'th': '/th/', 'zh-Hans': '/zh-hans/'}
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

def save_credentials(credentials, token_file):
    """Atomically save refresh credentials outside the source tree, owner-only."""
    token_file = Path(token_file).expanduser()
    token_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(token_file.parent, 0o700)
    fd, temporary = tempfile.mkstemp(prefix='.google-token-', dir=token_file.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(credentials.to_json())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, token_file)
        os.chmod(token_file, 0o600)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def google_credentials(authorize=False, token_file=None, client_file=None):
    """Use installed-app OAuth only; --authorize is the sole browser-launch path."""
    from google.auth.transport.requests import Request as AuthRequest
    from google.oauth2.credentials import Credentials

    token_file = Path(token_file or os.environ.get(
        'FXXKUP_OAUTH_TOKEN_FILE', '~/.config/fxxkup-seo/google-token.json')).expanduser()
    client_file = client_file or os.environ.get('FXXKUP_OAUTH_CLIENT_FILE')

    if token_file.is_file():
        credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        if credentials.valid:
            return credentials
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(AuthRequest())
                save_credentials(credentials, token_file)
                return credentials
            except Exception:
                if not authorize:
                    raise ValueError('Saved Google access could not be refreshed; rerun with --authorize to sign in again')
        if not authorize:
            raise ValueError('Saved Google access expired; rerun with --authorize to sign in again')

    if not authorize:
        raise ValueError('Google OAuth token missing; use --authorize with your Desktop OAuth client JSON')
    if not client_file or not Path(client_file).expanduser().is_file():
        raise ValueError('Set FXXKUP_OAUTH_CLIENT_FILE or pass --oauth-client with the downloaded Desktop client JSON')

    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(Path(client_file).expanduser()), SCOPES)
    credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    save_credentials(credentials, token_file)
    return credentials

def collect_gbp_website(start, end, request):
    """Aggregate on-site behavior only. This never calls the restricted GBP API."""
    url = 'https://analyticsdata.googleapis.com/v1beta/properties/559070143:runReport'
    dates = [{'startDate': str(start), 'endDate': str(end)}]
    campaign = {'filter': {'fieldName': 'sessionCampaignName', 'stringFilter': {
        'matchType': 'EXACT', 'value': 'google_business_profile', 'caseSensitive': True}}}
    def query(dimensions, metrics, dimension_filter):
        return request(url, {'dateRanges': dates,
            'dimensions': [{'name': n} for n in dimensions],
            'metrics': [{'name': n} for n in metrics],
            'dimensionFilter': dimension_filter, 'limit': '10000'})
    sessions = query(['sessionCampaignName', 'sessionSourceMedium', 'sessionManualAdContent'],
                     ['sessions', 'engagedSessions', 'keyEvents'], campaign)
    events = query(['sessionCampaignName', 'sessionSourceMedium', 'eventName'],
                   ['eventCount', 'keyEvents'], campaign)
    referrals = query(['sessionSourceMedium'], ['sessions'], {'filter': {
        'fieldName': 'sessionSourceMedium', 'stringFilter': {'matchType': 'FULL_REGEXP',
        'value': r'(.*\.)?(google\.[^ ]+|googleusercontent\.com|goo\.gl) / referral',
        'caseSensitive': False}}})
    reports = {'campaign_sessions': sessions, 'campaign_events': events,
               'google_referral_diagnostic': referrals}
    return {'source': 'GA4 Data API; session-scoped campaign attribution',
            'period': {'start': str(start), 'end': str(end)},
            'reports': reports,
            'truncated': any(r.get('rowCount', 0) > len(r.get('rows', [])) for r in reports.values()),
            'limitations': [
                'Campaign labels identify tagged sessions, not verified human GBP clicks.',
                'google / organic without the GBP campaign is not identifiable as GBP.',
                'Google referrals are diagnostic candidates only; they do not prove GBP origin.',
                'directions_click opens Maps from the website; it is not a Maps directions request or a visit.',
                'Key events are session-attributed here, not an advertising attribution-model report.',
                'Maps/Search views, profile calls and profile directions require separate GBP evidence.']}


def read_gbp_import(path, today=None):
    """Accept a small, explicitly sourced aggregate snapshot; reject ambiguous inputs."""
    data = json.loads(Path(path).read_text())
    required = {'schema_version', 'source', 'scope', 'period', 'observed_at', 'metrics'}
    if set(data) != required or type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('invalid GBP snapshot schema')
    if data['source'] not in ('ga4_business_profile_ui', 'gbp_performance_export'):
        raise ValueError('unsupported GBP source')
    if data['scope'] not in ('rock_bar_fxxk_up_only', 'all_linked_profiles_unverified'):
        raise ValueError('invalid profile scope')
    if set(data['period']) != {'start', 'end'}:
        raise ValueError('invalid date range')
    start, end = (dt.date.fromisoformat(data['period'][k]) for k in ('start', 'end'))
    observed = dt.datetime.fromisoformat(data['observed_at'])
    if observed.tzinfo is None or start > end or end > observed.date():
        raise ValueError('invalid snapshot dates')
    allowed = {'interactions', 'website_clicks', 'calls', 'directions', 'views', 'menus'}
    if not data['metrics'] or not set(data['metrics']) <= allowed:
        raise ValueError('invalid GBP metrics')
    if any(type(n) is not int or n < 0 for n in data['metrics'].values()):
        raise ValueError('metrics must be nonnegative integers; omit unavailable values')
    age = ((today or dt.datetime.now(ZoneInfo('Asia/Tokyo')).date()) - observed.date()).days
    if age < 0:
        raise ValueError('future snapshot')
    return dict(data, snapshot_age_days=age, period_end_age_days=((today or dt.datetime.now(ZoneInfo('Asia/Tokyo')).date()) - end).days, freshness='historical snapshot; never auto-refreshed',
                caveat='Do not sum with website events or infer person-level journeys.')


def collect(start, end, request):
    """Paginate query opportunities separately from property totals (privacy limits apply)."""
    original_request=request
    errors=[]
    def request(url, body):
        try: return original_request(url,body)
        except Exception as exc:
            detail='HTTP '+str(exc.code) if isinstance(exc,HTTPError) else type(exc).__name__
            errors.append(('ga4' if 'analyticsdata' in url else 'gsc')+': '+detail)
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
    all_traffic=request(ga_url, {'dateRanges':[{'startDate':str(start),'endDate':str(end)}],
        'dimensions':[{'name':'sessionDefaultChannelGroup'}],
        'metrics':[{'name':x} for x in ['sessions','totalUsers','engagedSessions','keyEvents']], 'limit':'10000'})
    named_events=request(ga_url, {'dateRanges':[{'startDate':str(start),'endDate':str(end)}],
        'dimensions':[{'name':'eventName'},{'name':'pagePath'}],
        'metrics':[{'name':'eventCount'}], 'limit':'10000'})
    landing_pages=request(ga_url, {'dateRanges':[{'startDate':str(start),'endDate':str(end)}],
        'dimensions':[{'name':'landingPage'},{'name':'sessionDefaultChannelGroup'}],
        'metrics':[{'name':'sessions'},{'name':'engagedSessions'},{'name':'keyEvents'}], 'limit':'10000'})
    gbp_website = collect_gbp_website(start, end, request)
    return {'period':{'start':str(start),'end':str(end),'gsc_timezone':'America/Los_Angeles','ga_timezone':'property setting; verify'},
            'all_traffic':all_traffic,'named_events':named_events,'landing_pages':landing_pages,
            'gbp_website':gbp_website,'api_errors':list(dict.fromkeys(errors)),'gsc_totals':totals,'previous_gsc_period':[str(previous_start),str(previous_end)],'previous_gsc_totals':previous_totals,'gsc_rows':rows,'ga4_organic':ga,
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
    if not plan.get('guardrails_reviewed',False): result['reasons'].append('guardrails not reviewed')
    if plan.get('elapsed_days',0)<plan['min_days']: result['reasons'].append('minimum duration not reached')
    if not plan.get('window_mature',False): result['reasons'].append('conversion window incomplete')
    if all(counts[a]['exposed'] for a in ('A','B')):
        a,b=counts['A'],counts['B']; result['absolute_lift']=b['rate']-a['rate']
        result['relative_lift']=b['rate']/a['rate']-1 if a['rate'] else None
        # Conservative interval from marginal Wilson bounds. Fixed-horizon only.
        result['lift95']=[b['wilson95'][0]-a['wilson95'][1],b['wilson95'][1]-a['wilson95'][0]]
        if not result['reasons'] and result['lift95'][0]>plan['minimum_absolute_lift']:
            result.update(status='recommend_B_for_review',winner='B')
        elif not result['reasons'] and result['lift95'][1]<-plan['minimum_absolute_lift']:
            result.update(status='recommend_A_for_review',winner='A')
        elif not result['reasons']:
            result['status']='completed_inconclusive'
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
            credentials=google_credentials()
            evidence['analytics']=collect(start,end,lambda url,body:api(url,body,credentials))
            evidence['blockers'].extend(evidence['analytics']['api_errors'])
        except Exception as exc: evidence['blockers'].append('Google API baseline unavailable: '+type(exc).__name__+'; browser observations are separate')
    else: evidence['blockers'].append('Offline mode: no Google APIs called')
    evidence['gbp_performance_snapshot'] = None
    snapshot_path = output/'gbp-performance-import.json'
    if snapshot_path.is_file():
        try:
            evidence['gbp_performance_snapshot'] = read_gbp_import(snapshot_path)
            evidence['gbp_performance_snapshot']['matches_website_report_period'] = (
                evidence['gbp_performance_snapshot']['period'] == {'start': str(start), 'end': str(end)})
        except (ValueError, TypeError, KeyError, OSError):
            evidence['blockers'].append('GBP snapshot import invalid; excluded from report')
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
    lines += ['', '## Separate GBP performance snapshot (not website events)',
        json.dumps(evidence['gbp_performance_snapshot'], ensure_ascii=False, indent=2)
        if evidence['gbp_performance_snapshot'] else 'Unavailable: import a validated GBP export or UI snapshot. Never infer Maps actions from website events.']
    lines+=['','## Required review','- Compare visible name, address, phone, hours and map destination with the verified Business Profile. No profile access was assumed.','- Review EN/JA evidence first; KO/TH hypotheses require observed queries or qualitative research.','- Keep existing B rollouts and current experiment ID/storage key. No ranking claim from visitor randomization.','- No automatic changes, merge, deployment, review solicitation, fabricated traffic or link creation.']
    (output/'weekly.md').write_text('\n'.join(lines)+'\n')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--live',action='store_true');p.add_argument('--authorize',action='store_true',help='perform the one-time local Google read-only OAuth consent flow');p.add_argument('--oauth-client',help='path to downloaded Desktop OAuth client JSON');p.add_argument('--output',type=Path,default=Path(os.environ.get('FXXKUP_REPORT_DIR','reports')).expanduser());p.add_argument('--events',type=Path)
    a=p.parse_args()
    if a.authorize:
        google_credentials(authorize=True,client_file=a.oauth_client)
        print('Google read-only access saved in the private local token file.')
    else:
        run(a.live,a.output,a.events)
        print((a.output/'weekly.md').read_text())
