"""Validate the exact experiment configuration in every published language."""
import json
import sys
from pathlib import Path
from lxml import html
from experiments import validate_copy
from decision import timestamp

ROOT=Path(__file__).resolve().parents[1]

def validate(root=ROOT):
    config=json.loads((root/'source/experiments.json').read_text())
    exp=config['firstVisit']
    validate_copy(exp['copy'])
    if exp.get('controlCopy'): validate_copy(exp['controlCopy'])
    assert exp['allocation']==.5
    assert exp.get('rolloutVariant','A') in ('A','B')
    if exp.get('enabled'):
        assert exp.get('endsAt'), 'an active experiment must expire automatically'
        end=timestamp(exp['endsAt'])
        if exp.get('startsAt'): assert timestamp(exp['startsAt'])<end
    runtime=(root/'dist/experiments.js').read_text()
    for lang,route in [('en',''),('ja','ja'),('ko','ko'),('th','th'),('zh-Hans','zh-hans')]:
        doc=html.fromstring((root/'dist'/route/'index.html').read_text())
        assert doc.get('lang')==lang
        assert doc.get('data-directions-version')=='B'
        assert doc.get('data-footer-version')=='B'
        values=doc.xpath('//script[starts-with(text(),"window.FXXKUP_EXPERIMENT_CONFIG=")]/text()')
        assert len(values)==1
        embedded=json.loads(values[0].split('=',1)[1].rstrip(';').replace('<\\/','</'))
        assert embedded==config, (lang,'configuration drift')
        assert doc.xpath('//script[@data-site-module="experiments"]/text()')==[runtime.replace('</','<\\/')]
        assert len(doc.xpath('//script[@src="/analytics.js"]'))==1
        assert not doc.xpath('//*[@data-directions-version="A" or @data-footer-version="A"]')
    assert not list((root/'dist').rglob('*.jsonl'))
    assert not (root/'dist/reports').exists()
    print('PASS: five-language configuration, runtime, deadlines, permanent rollouts and private-data exclusion.')

if __name__=='__main__': validate()
