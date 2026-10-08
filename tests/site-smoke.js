// Run through playwright-cli run-code with a local preview at port 4173.
async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const check = (value, message) => { if (!value) throw new Error(message); };
  const overflow = async () => page.evaluate(() => ({width: innerWidth, content: document.documentElement.scrollWidth}));
  await page.goto('http://127.0.0.1:4173/');
  await page.setViewportSize({width:1440,height:1000});
  await page.getByRole('link', {name:'Film', exact:true}).click();
  await page.waitForTimeout(1300);
  await page.locator('#upon-film').scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  check(await page.locator('#upon-film').evaluate(v => v.duration === 30 && v.readyState >= 2), 'Film metadata or decode failed');
  await page.locator('#film-sound').click();
  check(await page.locator('#upon-film').evaluate(v => !v.muted), 'Sound did not enable');
  await page.locator('[data-time="13"]').click();
  await page.waitForFunction(() => {const v=document.querySelector('#upon-film'); return !v.seeking && v.currentTime >= 12.9 && v.currentTime < 16;}, undefined, {timeout:10000});
  await page.locator('#film-sound').click();
  check(await page.locator('#upon-film').evaluate(v => v.muted), 'Sound did not mute');
  await page.locator('#film-play').click();
  check(await page.locator('#upon-film').evaluate(v => v.paused), 'Manual pause failed');
  await page.screenshot({path:'output/playwright/upon-aaa-film.png'});
  await page.getByRole('link', {name:'UpOn 2.1', exact:true}).click();
  await page.waitForTimeout(1100);
  await page.getByRole('link', {name:'Film', exact:true}).click();
  await page.waitForTimeout(1100);
  check(await page.locator('#upon-film').evaluate(v => v.paused), 'User pause was not respected');
  await page.locator('#tab-action').click();
  check(await page.locator('#panel-action').isVisible(), 'Action panel failed');
  await page.keyboard.press('ArrowLeft');
  check(await page.locator('#panel-intelligence').isVisible(), 'Keyboard tab navigation failed');
  await page.keyboard.press('Home');
  check(await page.locator('#panel-records').isVisible(), 'Home tab navigation failed');
  for (const id of ['vision', 'company', 'journey']) {
    await page.locator('#'+id).scrollIntoViewIfNeeded();
    await page.waitForTimeout(1100);
    await page.screenshot({path:'output/playwright/upon-aaa-'+id+'.png'});
  }
  check((await overflow()).content === 1440, 'Desktop horizontal overflow');
  await page.setViewportSize({width:375,height:812});
  await page.evaluate(() => scrollTo({top:0,behavior:'instant'}));
  await page.waitForTimeout(1100);
  check((await overflow()).content === 375, 'Mobile horizontal overflow');
  await page.screenshot({path:'output/playwright/upon-aaa-mobile.png'});
  await page.getByRole('button', {name:'Menu', exact:true}).click();
  check(await page.locator('#mobile-nav').isVisible(), 'Mobile menu failed');
  await page.keyboard.press('Escape');
  check(!(await page.locator('#mobile-nav').isVisible()), 'Escape did not close menu');
  await page.getByRole('button', {name:'Menu', exact:true}).click();
  await page.getByRole('link', {name:'Our vision', exact:true}).first().click();
  await page.waitForTimeout(1100);
  check(!(await page.locator('#mobile-nav').isVisible()), 'Navigation did not close menu');
  await page.screenshot({path:'output/playwright/upon-aaa-mobile-vision.png'});
  for (const id of ['journey','download']) {
    await page.locator('#'+id).scrollIntoViewIfNeeded();
    await page.waitForTimeout(1100);
    await page.screenshot({path:'output/playwright/upon-aaa-mobile-'+id+'.png'});
  }
  await page.setViewportSize({width:320,height:740});
  check((await overflow()).content === 320, '320px horizontal overflow');
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.reload();
  await page.locator('#upon-film').scrollIntoViewIfNeeded();
  await page.waitForTimeout(700);
  check(await page.locator('#upon-film').evaluate(v => v.paused), 'Reduced-motion setting did not suppress autoplay');
  check(errors.length === 0, 'Browser errors: '+errors.join('; '));
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.setViewportSize({width:1440,height:1000});
  await page.goto('http://127.0.0.1:4173/');
  return {desktop:'1440px: passed',mobile:'375px and 320px: passed',film:'30s decode, sound, chapter and pause: passed',tabs:'mouse and keyboard: passed',navigation:'mobile + Escape: passed',reducedMotion:'passed',pageErrors:errors};
}
