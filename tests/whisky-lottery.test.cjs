const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
test('every whisky page links to the wheel after the bottle list and excludes it from the count',()=>{
  const data=JSON.parse(fs.readFileSync(path.join(root,'source/menu/menu-data.json')));
  const prices=[297,299].map(id=>data.find(x=>x.id===id).prices.standard);
  assert.deepEqual(prices,[1000,1000]);
  for(const locale of ['','ja/','ko/','th/','zh-hans/']){
    const html=fs.readFileSync(path.join(root,'dist',locale,'whisky/index.html'),'utf8');
    const jumpLink = html.indexOf('href="#category-lottery"');
    const firstBottle = html.indexOf('<li class="whisky-item"');
    const lastBottle = html.lastIndexOf('<li class="whisky-item"');
    const wheelHeading = html.indexOf('id="category-lottery"');
    assert.ok(jumpLink >= 0 && jumpLink < firstBottle);
    assert.ok(wheelHeading > lastBottle);
    assert.ok(html.indexOf('class="whisky-wheel-demo"', wheelHeading) > wheelHeading);
    assert.doesNotMatch(html, /<option value="lottery">/);
    assert.match(html, /<p id="whisky-count"[^>]*>\(173 /);
  }
});
test('the existing category filter isolates lottery and searches its rows',()=>{
  const code=fs.readFileSync(path.join(root,'source/whisky.js'),'utf8');
  const el=(extra={})=>({hidden:false,value:'',style:{},dataset:{},listeners:{},addEventListener(k,f){this.listeners[k]=f},...extra});
  const makeGroup=(id,title,names)=>{const items=names.map(name=>el({textContent:name,dataset:{search:name.toLowerCase()},querySelector:()=>null}));return el({dataset:{categoryId:id},querySelector:q=>q==='h2'?{textContent:title}:null,querySelectorAll:q=>q==='.whisky-name'?items:q==='.whisky-item'?items:[],items});};
  const lottery=makeGroup('lottery','Whisky lottery',['Japanese Lottery','Islay whisky lottery']);
  const whisky=makeGroup('1','Japanese Whisky',['Nikka Frontier']);
  const groups=[lottery,whisky], controls=el(), search=el({focus(){}}), category=el({value:'all',options:[{textContent:'All'}],selectedIndex:0,clientWidth:300}), clear=el({focus(){}}), count=el({dataset:{suffix:'results'},textContent:'',getBoundingClientRect:()=>({width:30})}), empty=el(), categoryControl=el();
  const byId={'whisky-search':search,'whisky-category':category,'whisky-clear':clear,'whisky-count':count,'whisky-empty':empty};
  const document={documentElement:{lang:'en'},fonts:{ready:Promise.resolve()},getElementById:id=>byId[id]||null,querySelector:q=>q==='.whisky-controls'?controls:q==='.whisky-category-control'?categoryControl:null,querySelectorAll:q=>q==='[data-whisky-group]'?groups:q==='.whisky-item'?groups.flatMap(g=>g.items):[],createElement:()=>({getContext:()=>({measureText:()=>({width:10})})})};
  const window={addEventListener(){},getComputedStyle:()=>({font:'12px sans',paddingLeft:'0',borderLeftWidth:'0',borderRightWidth:'0'}),setTimeout:()=>0,clearTimeout(){}};
  vm.runInNewContext(code,{document,window,Number,Array,Map,String,Math});
  category.value='lottery';category.listeners.change();
  assert.equal(lottery.hidden,false);assert.equal(whisky.hidden,true);assert.equal(count.textContent,'(2)');
  search.value='islay';search.listeners.input();assert.equal(lottery.items[0].hidden,true);assert.equal(lottery.items[1].hidden,false);assert.equal(count.textContent,'(1)');
  clear.listeners.click();assert.equal(lottery.hidden,false);assert.equal(whisky.hidden,false);assert.equal(count.textContent,'(3 results)');
});
