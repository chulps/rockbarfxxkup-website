"""Post-deployment readback. Never executes page JS or sends analytics events."""
import json
from pathlib import Path
from lxml import html
import pilot

def verify():
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/'source/experiments.json').read_text())
    runtime=(root/'dist/experiments.js').read_text().replace('</','<\\/')
    results=[]
    for lang,route in pilot.ROUTES.items():
        for suffix in ('','whisky/'):
            body,status,url=pilot.public_get(pilot.ORIGIN+route+suffix)
            assert status==200,(lang,suffix,status)
            doc=html.fromstring(body)
            assert doc.get('lang')==lang
            if not suffix:
                values=doc.xpath('//script[starts-with(text(),"window.FXXKUP_EXPERIMENT_CONFIG=")]/text()')
                assert len(values)==1
                actual=json.loads(values[0].split('=',1)[1].rstrip(';').replace('<\\/','</'))
                assert actual==config,(lang,'live experiment configuration mismatch')
                assert doc.xpath('//script[@data-site-module="experiments"]/text()')==[runtime],(lang,'live runtime mismatch')
            results.append({'language':lang,'route':route+suffix,'status':status})
    print(json.dumps({'status':'verified','pages':results},indent=2))
    return results

if __name__=='__main__':verify()
