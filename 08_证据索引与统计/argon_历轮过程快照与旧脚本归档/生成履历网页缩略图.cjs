const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('C:/Users/GW/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

async function main() {
  const root = path.resolve(__dirname, '..');
  const manifestPath = path.join(__dirname, '简历视觉材料_整理清单.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8').replace(/^\uFEFF/, ''));
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
    args: ['--allow-file-access-from-files'],
  });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1300 }, deviceScaleFactor: 1.25 });
  try {
    for (const asset of manifest.assets.filter(a => a.local_file.endsWith('.html'))) {
      await page.goto(pathToFileURL(path.join(root, asset.local_file)).href, { waitUntil: 'load' });
      const contactCount = await page.locator('body').evaluate(el => (el.innerText.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)/g) || []).length);
      if (contactCount) throw new Error('Existing HTML contact-pattern screen blocked capture');
      const target = page.locator('main').first();
      const full = `03_简历与候选人案例/简历预览/${asset.candidate_id}_网页履历完整截图.png`;
      const thumb = `03_简历与候选人案例/简历预览/${asset.candidate_id}_网页履历缩略图.png`;
      await target.screenshot({ path: path.join(root, full), animations: 'disabled' });
      const box = await target.boundingBox();
      await page.screenshot({ path: path.join(root, thumb), clip: { x: box.x, y: box.y, width: box.width, height: Math.min(box.height, 1150) }, animations: 'disabled' });
      asset.thumbnail_file = thumb;
      asset.preview_files = [full];
      asset.image_size = [Math.round(box.width * 1.25), Math.round(box.height * 1.25)];
      asset.web_capture = { source: asset.local_file, format: '网页脱敏转录截图，不是原始PDF', thumbnail_scope: 'main开头1150 CSS像素；全文打开原HTML或完整截图', contact_pattern_count: contactCount, captured_on: '2026-10-24' };
      console.log(`${asset.candidate_id}: existing HTML profile captured; no new original PDF`);
    }
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2).replace(/\n/g, '\r\n') + '\r\n', 'utf8');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error.message); process.exit(1); });
