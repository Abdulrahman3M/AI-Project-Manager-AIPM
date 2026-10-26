/* Controlled rendering/diagnostic integration; not a model reconstruction benchmark. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const skill = path.resolve(__dirname, '..');
const out = path.resolve(process.argv[2] || path.join(process.cwd(), '.test-workspace', 'screenshot-browser'));
fs.mkdirSync(out, {recursive:true});
function compare(a,b,dir,regions){
  const result = spawnSync(process.env.PYTHON || 'python', ['-B',path.join(skill,'scripts','compare.py'),a,b,'--out',dir,'--regions',regions],{encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);
  return JSON.parse(result.stdout);
}
(async()=>{
  const browser = await chromium.launch({headless:true});
  try {
    const context = await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,locale:'ar-AE',colorScheme:'light',reducedMotion:'reduce'});
    const page = await context.newPage();
    const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.join(__dirname,'fixtures','lesson.html')).href);
    await page.evaluate(()=>document.fonts.ready);
    const ref=path.join(out,'reference.png'), bad=path.join(out,'changed.png'), repaired=path.join(out,'repaired.png');
    await page.screenshot({path:ref});
    const box=await page.locator('#toggle').boundingBox();
    const regions=path.join(out,'regions.json');
    fs.writeFileSync(regions,JSON.stringify([{id:'primary-action',box:[Math.floor(box.x),Math.floor(box.y),Math.ceil(box.x+box.width),Math.ceil(box.y+box.height)]}]));
    const style=await page.addStyleTag({content:'#toggle{background:#e33a40}'});
    await page.screenshot({path:bad});
    const changed=compare(ref,bad,path.join(out,'changed-diff'),regions);
    assert(changed.regions[0].changed_percent>20);
    assert(changed.global.changed_percent<5);
    await style.evaluate(el=>el.remove());
    await page.screenshot({path:repaired});
    const fixed=compare(ref,repaired,path.join(out,'repaired-diff'),regions);
    assert.equal(fixed.global.changed_percent,0);
    await page.locator('#toggle').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#toggle').getAttribute('aria-expanded'),'true');
    assert.equal(await page.locator('#answer').isVisible(),true);
    await page.screenshot({path:path.join(out,'interaction.png')});
    const viewports=[];
    for(const width of [390,700,701,1024,1440]){
      await page.setViewportSize({width,height:900});
      const dims=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,dir:document.documentElement.dir}));
      assert(dims.scroll<=dims.client,`horizontal overflow at ${width}`);
      assert.equal(dims.dir,'rtl');
      viewports.push({width,...dims});
      await page.screenshot({path:path.join(out,`rtl-${width}.png`)});
    }
    const dprContext=await browser.newContext({viewport:{width:720,height:450},deviceScaleFactor:2});
    const dprPage=await dprContext.newPage();
    await dprPage.goto(pathToFileURL(path.join(__dirname,'fixtures','lesson.html')).href);
    await dprPage.screenshot({path:path.join(out,'dpr-2.png')});
    const scale=await dprPage.evaluate(()=>window.devicePixelRatio);
    assert.equal(scale,2);
    assert.equal(errors.length,0,errors.join('\n'));
    const summary={status:'PASS',scope:'Controlled fixture rendering, real keyboard outcome, RTL overflow checks and diagnostic regression/repair; NOT a held-out agent benchmark',browser:browser.version(),viewports,changed:changed.global,changedRegion:changed.regions[0],repaired:fixed.global,consoleErrors:errors,dpr:{css:[720,450],dpr:scale,expectedRaster:[1440,900]}};
    fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
    console.log(JSON.stringify(summary,null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
