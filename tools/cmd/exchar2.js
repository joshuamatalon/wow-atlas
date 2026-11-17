const core = require_core();
const tab = require_tab_creatures();
const T = require_DBItemCharTextures();
if (!S.patchedTex) {
  for (const k of ['getItemTextures', 'getTexturesByDisplayId']) {
    const orig = T[k];
    T[k] = function (...a) { const r = orig.apply(this, a); return r ? r.filter(t => t && t.fileDataID > 0) : r; };
  }
  S.patchedTex = true;
}
const self = { $core: core };
const chars = JSON.parse(fs.readFileSync('C:/Users/joshu/wow-atlas/work/creature_chars.json', 'utf8'));
core.view.selectionCreatures = chars.map(c => ({ id: c.npc, name: c.slug, displayID: c.display, always_items: [] }));
await tab.methods.export_creatures.call(self);
return fs.readdirSync('C:/Users/joshu/wow-atlas/work/export/creatures').filter(f => /citizen|captain/.test(f));
