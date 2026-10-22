const { chromium } = require(process.env.MTG_PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto((process.env.MTG_SITE_URL || 'http://127.0.0.1:8771/') + 'sets/reality-fracture/Reality-Fracture-Draft.html#draft-combos');
    assert.equal(await page.locator('.draft-package').count(),20);
    await page.locator('#combo-search').fill('Kiora');
    assert.equal(await page.locator('.draft-package:visible').count(),1);
    await page.locator('#combo-colors').selectOption('WB');
    assert.equal(await page.locator('.draft-package:visible').count(),0);
    assert.match(await page.locator('#combo-count').innerText(),/Nessun/);
    await page.locator('#combo-reset').click();
    await page.locator('#combo-colors').selectOption('WB');
    for (const colors of await page.locator('.draft-package:visible').evaluateAll(rows=>rows.map(r=>r.dataset.colors))) {
      assert.ok([...colors].every(c=>'WB'.includes(c)));
    }
    await page.locator('#combo-role').selectOption('Chiusura');
    assert.ok(await page.locator('.draft-package:visible').count()>0);
    await page.locator('#combo-reset').click();
    await page.locator('#combo-search').fill('proft');
    const card = page.locator('.draft-package:visible [data-card-preview="Proft, Consulting Detective"]').first();
    await card.hover();
    await page.locator('#mtg-card-preview').waitFor({state:'visible'});
    await page.keyboard.press('Escape');
    await card.focus();
    await page.locator('#mtg-card-preview').waitFor({state:'visible'});
    await page.keyboard.press('Escape');
    for (const width of [360,768,1440]) {
      await page.setViewportSize({width,height:950});
      await page.locator('#combo-reset').click();
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1), 'Horizontal overflow: '+width);
    }
    await page.setViewportSize({width:1440,height:1000});
    await page.locator('#draft-combos').scrollIntoViewIfNeeded();
    await page.screenshot({path:'draft-combos-desktop-qa.png'});
    await page.setViewportSize({width:390,height:844});
    await page.locator('#draft-combos').evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
    await page.screenshot({path:'draft-combos-mobile-qa.png'});
    const touch = await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,reducedMotion:'reduce'});
    const mobile = await touch.newPage();
    await mobile.goto(page.url());
    const touchCard = mobile.locator('#draft-combos [data-card-preview]').first();
    await touchCard.tap();
    await mobile.locator('#mtg-card-preview').waitFor({state:'visible'});
    await touchCard.tap();
    await mobile.locator('#mtg-card-preview').waitFor({state:'hidden'});
    await touch.close();
    assert.deepEqual(errors,[]);
    console.log('PASS: 20 pacchetti, filtri combinati/reset, anteprime mouse/tastiera/tocco, nessun overflow a 360/768/1440px.');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1);});
