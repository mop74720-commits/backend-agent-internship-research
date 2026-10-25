const { chromium } = require('C:/Users/GW/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path = require('path');
(async()=>{
 const browser = await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 try {
  const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
  const response=await page.goto('https://cyc2018.github.io/page.html',{waitUntil:'networkidle',timeout:45000});
  await page.screenshot({path:path.resolve('03_简历与候选人案例/公开简历原件/CV15_CyC2018_作者网页履历_浏览器截图.png'),fullPage:true});
  await page.pdf({path:path.resolve('03_简历与候选人案例/公开简历原件/CV15_CyC2018_作者网页履历_浏览器导出.pdf'),format:'A4',printBackground:true});
  console.log(JSON.stringify({candidate_id:'CV15',status:response.status(),url:page.url(),title:await page.title(),height:await page.evaluate(()=>document.body.scrollHeight)}));
 } finally {await browser.close();}
})();
