"""Discover audit coverage from the sitemap; validate it against built pages."""
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import pilot

NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
ROOT=Path(__file__).resolve().parents[1]

def pages(root=ROOT):
    dist=root/'dist'
    entries=ET.fromstring((dist/'sitemap.xml').read_text()).findall('s:url',NS)
    if not entries or len(entries)>1000: raise ValueError('invalid sitemap size')
    result=[]; seen=set()
    for entry in entries:
        url=entry.findtext('s:loc',namespaces=NS)
        u=urlsplit(url)
        if u.scheme!='https' or u.netloc!='www.rockbarfxxkup.com' or u.query or u.fragment or '..' in u.path.split('/'):
            raise ValueError('invalid sitemap URL')
        if u.path in seen: raise ValueError('duplicate sitemap URL')
        seen.add(u.path)
        path=dist/u.path.lstrip('/')
        if u.path.endswith('/'): path=path/'index.html'
        if not path.is_file(): raise ValueError('sitemap page missing from build: '+u.path)
        doc=pilot.Document(path.read_text())
        lang=next((a.get('lang') for t,a in doc.tags if t=='html'),None)
        if not lang: raise ValueError('page language missing: '+u.path)
        alternates={e.get('hreflang'):e.get('href') for e in entry.findall('x:link',NS)}
        result.append({'url':url,'route':u.path,'path':path,'language':lang,'alternates':alternates})
    built={'/'+str(p.relative_to(dist)).removesuffix('index.html') for p in dist.rglob('*.html')}
    if seen!=built:
        raise ValueError('sitemap/build mismatch: '+str(sorted(seen^built)))
    return result

def audit_page(body,page):
    checks=pilot.audit(body,page['language'],page['url'])
    for key in ('local_schema','instagram_link','maps_link','hreflang'):checks.pop(key,None)
    if page['alternates']:
        doc=pilot.Document(body)
        alts={a.get('hreflang'):a.get('href') for t,a in doc.tags if t=='link' and a.get('rel')=='alternate'}
        checks['hreflang']=all(alts.get(k)==v for k,v in page['alternates'].items())
    return checks

if __name__=='__main__':
    items=pages()
    print(f'PASS: sitemap contains all {len(items)} built HTML pages, with no duplicate or missing URLs.')
