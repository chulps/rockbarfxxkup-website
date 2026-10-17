const {readFileSync}=require('node:fs');
const {runInNewContext}=require('node:vm');
const assert=require('node:assert/strict');
const script=readFileSync('dist/analytics.js','utf8');
for(const variant of ['A','B']) for(const destination of ['bar','chuck']) {
 const events=[];let click,observe;
 const footer={contains:link=>link.footer};
 const ctx={window:{siteExperiment:{id:'directions_button_test_2026_10',variant:'B'},footerExperiment:{id:'footer_contact_test_2026_10',variant},gtag:(...args)=>events.push(args),IntersectionObserver:true},document:{documentElement:{lang:'en'},getElementById:()=>footer,addEventListener:(_,handler)=>click=handler},IntersectionObserver:class{constructor(fn){observe=fn}observe(){}disconnect(){}}};
 runInNewContext(script,ctx);
 assert.equal(events.length,1,'footer exposure must wait until seen');
 observe([{isIntersecting:true}]);observe([{isIntersecting:true}]);
 const link={footer:true,dataset:{trackEvent:'instagram_click',trackDestination:destination,trackPlacement:'footer-contact'},href:`https://www.instagram.com/${destination==='bar'?'rockbar_fxxkup':'chakkufxxkupu'}/`};
 click({target:{closest:()=>link}});
 const event=events.at(-1);
 assert.equal(event[1],'instagram_click');assert.equal(event[2].experiment_variant,variant);assert.equal(event[2].experiment_id,'footer_contact_test_2026_10');assert.equal(event[2].link_destination,destination);assert.equal(event[2].link_url,link.href);
 assert.equal(events.filter(e=>e[1]==='experiment_view'&&e[2].experiment_id==='footer_contact_test_2026_10').length,1);
 click({target:{closest:()=>({footer:false,dataset:{trackEvent:'directions_click',trackPlacement:'hero'}})}});
 assert.equal(events.at(-1)[2].experiment_id,'directions_button_test_2026_10');assert.equal(events.at(-1)[2].experiment_variant,'B');
}
console.log('Passed: A/B × bar/Chuck clicks, destination URLs, visible exposure deduplication, and preserved directions attribution.');
