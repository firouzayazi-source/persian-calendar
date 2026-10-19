const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [f, w, h] of [['poster-a4', 1240, 1754], ['story', 1080, 1920]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + __dirname + '/' + f + '.html');
    await p.waitForTimeout(1500);
    await p.screenshot({ path: __dirname + '/' + f + '.png' });
  }
  await b.close();
})();
