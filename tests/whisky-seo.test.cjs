const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const langs=[['','en','whisky-inventory.md'],['ja/','ja','whisky-inventory-ja.md'],['ko/','ko','whisky-inventory-ko.md'],['th/','th','whisky-inventory-th.md'],['zh-hans/','zh-Hans','whisky-inventory-zh-hans.md']];
test('localized whisky pages keep inventory, valid section links and canonical metadata',()=>{
  for(const [dir,lang,file] of langs){
    const html=fs.readFileSync(path.join(root,'dist',dir,'whisky/index.html'),'utf8');
    const source=fs.readFileSync(path.join(root,'source/whisky',file),'utf8');
    const rows=(html.match(/<li class="whisky-item"/g)||[]).length;
    assert.ok(rows>0,lang);
    assert.match(html,new RegExp('<p class="whisky-intro">[^<]*'+rows));
    const nav=html.match(/<nav class="whisky-visit-links"[^>]*>([\s\S]*?)<\/nav>/)[1];
    const refs=[...nav.matchAll(/href="#(category-(?:\d+|lottery))"/g)].map(x=>x[1]);
    assert.equal(refs.length,6,lang);
    assert.ok(refs.includes("category-lottery"));
    for(const ref of refs) assert.ok(html.includes('id="'+ref+'"'),lang+': '+ref);
    assert.ok(html.includes('rel="canonical" href="https://www.rockbarfxxkup.com/'+dir+'whisky/"'));
    assert.ok(source.includes('## '));
    assert.equal((html.match(/rel="alternate" hreflang=/g)||[]).length,6);
  }
});
