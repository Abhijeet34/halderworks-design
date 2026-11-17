// Attack harness for PR 49: renders hostile .hw-row inputs against a tree's components.css
// and reports overlaps, escapes and widths. Usage: node attack.js <tree-root>
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(process.argv[2]);
const css = ['exports/variables.css', 'fonts/fonts.css', 'components/components.css']
  .map(f => `<link rel="stylesheet" href="file://${root}/${f}">`).join('');
const m = i => `<span class="hw-row-meta">meta ${i}</span>`;
const CASES = {
  zero: `<li class="hw-row" id="t"></li>`,
  one_text: `<li class="hw-row" id="t"><p>Only text</p></li>`,
  one_meta: `<li class="hw-row" id="t"><span class="hw-row-meta">Only meta</span></li>`,
  twelve_text_first: `<li class="hw-row" id="t"><p>staging.atlas.dev</p>${[...Array(11)].map((_, i) => m(i + 1)).join('')}</li>`,
  twelve_metas: `<li class="hw-row" id="t">${[...Array(12)].map((_, i) => m(i + 1)).join('')}</li>`,
  twelve_lead: `<li class="hw-row hw-row--lead" id="t"><span class="hw-row-meta">12:30 pm</span><p>Text</p>${[...Array(10)].map((_, i) => m(i + 1)).join('')}</li>`,
  nested: `<li class="hw-row" id="t"><p>Outer text</p><div class="hw-row"><p>Inner text that is long enough</p><span class="hw-row-meta">inner meta</span></div><span class="hw-row-meta">outer meta</span></li>`,
  nested_in_lead: `<li class="hw-row hw-row--lead" id="t"><span class="hw-row-meta">12:30 pm</span><div class="hw-row"><p>Inner text</p><span class="hw-row-meta">inner meta</span></div><span class="hw-row-meta">outer</span></li>`,
  text_own_width: `<li class="hw-row" id="t"><p style="width:120px" id="w">Fixed width text</p><span class="hw-row-meta">2 days ago</span></li>`,
  text_own_width_class: `<li class="hw-row" id="t"><p class="own-w" id="w">Fixed width text</p><span class="hw-row-meta">2 days ago</span></li>`,
  meta_own_width: `<li class="hw-row" id="t"><p>Text</p><span class="hw-row-meta" style="width:200px;display:inline-block" id="w">wide meta</span></li>`,
  wide_child_overflow: `<li class="hw-row" id="t"><p>Text</p><span class="hw-row-meta" style="width:400px;display:inline-block" id="w">400px meta</span></li>`,
};
const MEASURE = `(() => {
  const ext = el => { if (el.classList.contains('hw-row-actions') || el.classList.contains('hw-row') || el.style.width || el.classList.contains('own-w')) return el.getBoundingClientRect();
    const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect(); };
  const row = document.getElementById('t'), rb = row.getBoundingClientRect();
  const kids = [...row.children], boxes = kids.map(ext), hits = [];
  boxes.forEach((a, i) => {
    if (a.width && (a.left < rb.left - 0.5 || a.right > rb.right + 0.5)) hits.push(i + ' leaves row');
    boxes.slice(i + 1).forEach((b, k) => {
      if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0.5 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0.5)
        hits.push(i + ' over ' + (i + 1 + k)); }); });
  for (const inner of row.querySelectorAll('.hw-row')) {
    const ib = inner.getBoundingClientRect(), ik = [...inner.children].map(ext);
    ik.forEach((a, i) => { if (a.left < ib.left - 0.5 || a.right > ib.right + 0.5) hits.push('inner ' + i + ' leaves inner row');
      ik.slice(i + 1).forEach((b, k) => { if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0.5 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0.5) hits.push('inner ' + i + ' over ' + (i + 1 + k)); }); });
  }
  const w = document.getElementById('w');
  return { rowH: Math.round(rb.height), rowW: Math.round(rb.width), display: getComputedStyle(row).display,
    lines: new Set(boxes.map(b => Math.round(b.top))).size,
    widths: kids.map(k => Math.round(k.getBoundingClientRect().width)).join(','),
    ownWidth: w ? Math.round(w.getBoundingClientRect().width) : null, hits };
})()`;
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const width of [180, 300, 1440]) {
    const p = await b.newPage({ viewport: { width: width < 300 ? 300 : width, height: 900 } });
    for (const [name, html] of Object.entries(CASES)) {
      const file = path.join(root, '.attack-49.html');
      require('fs').writeFileSync(file, `<!doctype html><html><head>${css}<style>.own-w{width:120px}</style></head><body style="margin:24px"><ul class="hw-list" style="width:${width === 180 ? '180px' : 'auto'}">${html}</ul></body></html>`);
      await p.goto('file://' + file, { waitUntil: 'load' });
      await p.evaluate(() => document.fonts.ready);
      out[`${name} @${width}`] = await p.evaluate(MEASURE);
    }
    await p.close();
  }
  await b.close();
  require('fs').unlinkSync(path.join(root, '.attack-49.html'));
  for (const [k, v] of Object.entries(out))
    console.log(`${k.padEnd(28)} ${v.display.padEnd(5)} h=${v.rowH} w=${v.rowW} lines=${v.lines} kids=[${v.widths}]${v.ownWidth !== null ? ' own=' + v.ownWidth : ''} hits=${v.hits.length ? v.hits.join('; ') : 'none'}`);
})();
