const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [dir, outDir, ...names] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (const n of names) {
    await p.goto('file://' + path.join(dir, n + '.html'));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    const over = await p.evaluate(() => { const f = document.querySelector('.foot').getBoundingClientRect().top; let m = 0; document.querySelectorAll('.page *').forEach(e => { const r = e.getBoundingClientRect(); if (r.height > 0) m = Math.max(m, r.bottom); }); return [Math.round(m), Math.round(f)]; });
    console.log(n, 'content bottom', over[0], 'footer top', over[1]);
    await p.screenshot({ path: path.join(outDir, n + '@2x.png') });
  }
  await b.close();
})();
