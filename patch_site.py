from pathlib import Path
import zlib

data = Path('payload.gz').read_bytes()
if data[:2] != b'\x1f\x8b':
    raise SystemExit('Not gzip data')
pos = 10
flg = data[3]
if flg & 4:
    n = int.from_bytes(data[pos:pos+2], 'little')
    pos += 2 + n
if flg & 8:
    pos = data.index(b'\0', pos) + 1
if flg & 16:
    pos = data.index(b'\0', pos) + 1
if flg & 2:
    pos += 2
html = zlib.decompress(data[pos:-8], -15).decode('utf-8')
patch = r'''<script>
(function(){
  const EDIT_KEY = 'rimsko_pravo_izmenjena_pitanja_v1';
  let edits = {};
  try { edits = JSON.parse(localStorage.getItem(EDIT_KEY) || '{}') || {}; } catch(e) { edits = {}; }
  const originals = ALL.map(c => ({q:c.q, a:c.a}));
  ALL.forEach((c,i) => {
    c.id = i;
    if (edits[i]) {
      if (typeof edits[i].q === 'string') c.q = edits[i].q;
      if (typeof edits[i].a === 'string') c.a = edits[i].a;
    }
  });
  function persist(){ localStorage.setItem(EDIT_KEY, JSON.stringify(edits)); }
  function editCurrent(){
    const c = deck[index];
    if (!c) return;
    const q = prompt('Измени питање:', c.q);
    if (q === null) return;
    const a = prompt('Измени одговор:', c.a);
    if (a === null) return;
    c.q = q.trim() || c.q;
    c.a = a.trim() || c.a;
    edits[c.id] = {q:c.q, a:c.a};
    persist();
    render();
  }
  function resetCurrent(){
    const c = deck[index];
    if (!c || !edits[c.id]) return;
    if (!confirm('Врати ово питање и одговор на оригинал?')) return;
    c.q = originals[c.id].q;
    c.a = originals[c.id].a;
    delete edits[c.id];
    persist();
    render();
  }
  const baseRender = render;
  render = function(){
    baseRender();
    const actions = document.querySelector('.card-actions');
    if (!actions || !deck[index]) return;
    const edit = document.createElement('button');
    edit.className = 'btn';
    edit.textContent = '✎ Измени';
    edit.style.marginLeft = '8px';
    edit.onclick = editCurrent;
    actions.appendChild(edit);
    if (edits[deck[index].id]) {
      const reset = document.createElement('button');
      reset.className = 'btn';
      reset.textContent = '↺ Оригинал';
      reset.style.marginLeft = '8px';
      reset.onclick = resetCurrent;
      actions.appendChild(reset);
    }
  };
  render();
})();
</script>'''
html = html.replace('</body>', patch + '\n</body>')
Path('index.html').write_text(html, encoding='utf-8')
