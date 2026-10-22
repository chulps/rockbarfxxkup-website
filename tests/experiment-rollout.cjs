const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const assert = require('node:assert/strict');
const runtime = readFileSync('dist/experiments.js', 'utf8');
const analytics = readFileSync('dist/analytics.js', 'utf8');
const shippedConfig = JSON.parse(readFileSync('source/experiments.json', 'utf8'));
assert.equal(shippedConfig.firstVisit.enabled, true, 'the approved confidence test must be enabled');
assert.equal(shippedConfig.firstVisit.allocation, .5);
assert.equal(shippedConfig.firstVisit.copy.en.headline, 'Your music. Your whisky. Your night.');
assert.equal(shippedConfig.firstVisit.copy.en.supporting, 'Song requests welcome. Great whisky, rock music, and a friendly place to spend your night in Susukino.');

function page({language='en', enabled=false, random=.1, store=new Map(), blocked=false, observer=true}={}) {
  const config = JSON.parse(JSON.stringify(shippedConfig));
  config.firstVisit.enabled = enabled;
  const events=[];let handler, seen, randomCalls=0, writes=0;
  const headline={textContent:'CONTROL HEADLINE',replaceChildren(...nodes){this.textContent=nodes.map(n=>n.textContent).join('')}};
  const supporting={textContent:'CONTROL SUPPORTING'};
  const hero={contains:link=>!!link.hero};
  const footer={contains:link=>!!link.footer};
  const window={FXXKUP_EXPERIMENT_CONFIG:config,gtag:(...args)=>events.push(args)};
  if(observer)window.IntersectionObserver=true;
  const context={window,Math:Object.assign(Object.create(Math),{random:()=>{randomCalls++;return random}}),
    localStorage:{getItem:key=>{if(blocked)throw Error('blocked');return store.get(key)??null},setItem:(key,value)=>{if(blocked)throw Error('blocked');writes++;store.set(key,value)}},
    location:{search:'?experiment=B&enabled=true'},
    document:{documentElement:{lang:language},querySelector:selector=>({'.hero-copy':hero,'.hero-line':headline,'.hero-desc':supporting}[selector]),getElementById:()=>footer,
      createTextNode:text=>({textContent:text}),createElement:()=>({textContent:''}),addEventListener:(name,fn)=>{if(name==='click')handler=fn}},
    IntersectionObserver:class{constructor(fn){seen=fn}observe(){}disconnect(){}}
  };
  runInNewContext(runtime,context);
  window.fxxkupFirstVisit?.applyCopy();
  runInNewContext(analytics,context);
  return {window,events,headline,supporting,store,
    observe:ratio=>seen?.([{isIntersecting:ratio>0,intersectionRatio:ratio}]),
    click:link=>handler({target:{closest:()=>link}}),
    counts:()=>({randomCalls,writes})};
}
function link(event,placement,extra={}) {
  return {href:'https://maps.app.goo.gl/95hYVdZMdPot4WQy5',dataset:{trackEvent:event,trackPlacement:placement},...extra};
}
for(const language of Object.keys(shippedConfig.firstVisit.copy)) {
  // Visitors who previously drew A still see the permanent B content. Neither
  // old assignment is overwritten, and no retired-test exposure is emitted.
  for(const oldVariant of ['A','B']) {
    const old=new Map([['fxxkup_directions_button_test_2026_10',oldVariant],['fxxkup_footer_contact_test_2026_10',oldVariant]]);
    const p=page({language,store:old});
    assert.equal(p.window.firstVisitExperiment,undefined);
    assert.deepEqual(p.counts(),{randomCalls:0,writes:0});
    assert.equal(p.events.length,0);
    for(const placement of ['hero','visit','mobile_bar']) {
      const a=link('directions_click',placement,{hero:placement==='hero'});p.click(a);
      const e=p.events.at(-1);
      assert.equal(e[1],'directions_click');assert.equal(e[2].page_language,language);
      assert.equal(e[2].link_url,a.href);assert.equal(e[2].link_destination,'google_maps');assert.equal(e[2].rollout_variant,'B');
      assert.equal(e[2].experiment_id,undefined);assert.equal(e[2].experiment_variant,undefined);
    }
    for(const destination of ['bar','chuck']) {
      const a=link('instagram_click','footer-contact',{footer:true,href:`https://www.instagram.com/${destination==='bar'?'rockbar_fxxkup':'chakkufxxkupu'}/`});
      a.dataset.trackDestination=destination;p.click(a);const e=p.events.at(-1);
      assert.equal(e[1],'instagram_click');assert.equal(e[2].link_destination,destination);
      assert.equal(e[2].link_url,a.href);assert.equal(e[2].link_placement,'footer_contact');
      assert.equal(e[2].rollout_id,'footer_contact_test_2026_10');assert.equal(e[2].rollout_variant,'B');
      assert.equal(e[2].experiment_id,undefined);
    }
    for(const action of ['menu_open','phone_click','language_select']) {
      const a=link(action,'content');a.dataset.language='ja';p.click(a);assert.equal(p.events.at(-1)[1],action);
    }
    assert.equal(p.events.filter(e=>e[1]==='experiment_view').length,0);
    assert.equal(old.size,2);assert.equal(old.get('fxxkup_directions_button_test_2026_10'),oldVariant);
  }
  // Enabling is simulated in memory only. A and B have identical links and
  // event paths; only the localized headline/supporting copy can differ.
  for(const [random,variant] of [[.49,'A'],[.5,'B']]) {
    const p=page({language,enabled:true,random});
    assert.equal(p.window.firstVisitExperiment.variant,variant);
    assert.equal(p.store.get(shippedConfig.firstVisit.storageKey),variant);
    assert.equal(p.headline.textContent,variant==='A'?'CONTROL HEADLINE':shippedConfig.firstVisit.copy[language].lines.join(' '));
    assert.equal(p.supporting.textContent,variant==='A'?'CONTROL SUPPORTING':shippedConfig.firstVisit.copy[language].supporting);
    p.observe(.1);assert.equal(p.events.length,0);
    const unexposed=link('instagram_click','footer-contact',{footer:true});p.click(unexposed);
    assert.equal(p.events.at(-1)[2].experiment_id,undefined);
    p.observe(.25);p.observe(.8);
    assert.equal(p.events.filter(e=>e[1]==='experiment_view').length,1);
    const directions=link('directions_click','hero',{hero:true});p.click(directions);
    const e=p.events.at(-1);assert.equal(e[2].experiment_id,shippedConfig.firstVisit.id);assert.equal(e[2].experiment_variant,variant);
    assert.equal(e[2].link_url,directions.href);assert.equal(e[2].rollout_variant,'B');
    const nextLanguage=page({language:language==='en'?'ja':'en',enabled:true,random:variant==='A'?.9:.1,store:p.store});
    assert.equal(nextLanguage.window.firstVisitExperiment.variant,variant);assert.equal(nextLanguage.counts().randomCalls,0);
  }
}
const immediate=page({enabled:true,random:.9,observer:false});immediate.click(link('directions_click','hero',{hero:true}));
assert.deepEqual(immediate.events.map(e=>e[1]),['experiment_view','directions_click']);
immediate.click(link('directions_click','hero',{hero:true}));assert.equal(immediate.events.filter(e=>e[1]==='experiment_view').length,1);
const blocked=page({enabled:true,blocked:true});assert.equal(blocked.window.firstVisitExperiment,undefined);assert.equal(blocked.headline.textContent,'CONTROL HEADLINE');
console.log('PASS: rollout clicks and destinations in 5 locales; no retired or disabled exposures; persistent 50/50 A/B, localization, visibility/click exposure deduplication, and blocked-storage fallback.');
