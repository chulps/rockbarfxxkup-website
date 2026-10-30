"""Post-deployment readback. Never executes page JS or sends analytics events."""
import json
from pathlib import Path
from lxml import html
import pilot
from site_pages import pages, audit_page, NS
import xml.etree.ElementTree as ET

def verify():
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/'source/experiments.json').read_text())
    runtime=(root/'dist/experiments.js').read_text().replace('</','<\\/')
    results=[]
    discovered=pages(root)
    sitemap,status,_=pilot.public_get(pilot.ORIGIN+'/sitemap.xml')
    assert status==200
    live_urls={n.text for n in ET.fromstring(sitemap).findall('s:url/s:loc',NS)}
    assert live_urls=={p['url'] for p in discovered}, 'live sitemap/source mismatch'
    for page in discovered:
        body,status,url=pilot.public_get(page['url'])
        assert status==200,(page['route'],status)
        assert all(audit_page(body,page).values()),(page['route'],'page audit failed')
        doc=html.fromstring(body)
        if page['route'] in pilot.ROUTES.values():
            values=doc.xpath('//script[starts-with(text(),"window.FXXKUP_EXPERIMENT_CONFIG=")]/text()')
            assert len(values)==1
            actual=json.loads(values[0].split('=',1)[1].rstrip(';').replace('<\\/','</'))
            assert actual==config,(page['route'],'live experiment configuration mismatch')
            assert doc.xpath('//script[@data-site-module="experiments"]/text()')==[runtime],(page['route'],'live runtime mismatch')
        results.append({'language':page['language'],'route':page['route'],'status':status})
    print(json.dumps({'status':'verified','pages':results},indent=2))
    return results

if __name__=='__main__':verify()
