// Export character-model creatures (humans, goblins, tauren) WITH their helm and shoulder models and the right geosets.
// wow.export only dresses a creature it is previewing, so this opens the Creatures tab in the hidden window, previews
// each one, then exports it while it is the active preview. The helm and shoulders ride the body's attachment bones.
// ARGS: {chars: PATH to creature_chars.json, out: export DIR (files land in DIR/creatures/SLUG.glb)}
const core = require_core();
const modules = require_modules();
const tab = require_tab_creatures();
const L = require_DBCreatureList();
const M2Exporter = require_M2Exporter();
const CharacterExporter = require_CharacterExporter();
const IM = require_DBItemModels();
const X = require_DBCreatureDisplayExtra();
const T = require_DBItemCharTextures();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (fn()) return true; await sleep(100); } return false; };

if (!S.patchedTex) {
  for (const k of ['getItemTextures', 'getTexturesByDisplayId']) {
    const orig = T[k];
    T[k] = function (...a) { const r = orig.apply(this, a); return r ? r.filter((t) => t && t.fileDataID > 0) : r; };
  }
  S.patchedTex = true;
}
if (!S.patchedList) {
  const orig = L.get_creature_by_id; S.fake = new Map();
  L.get_creature_by_id = (id) => S.fake.get(id) || orig(id);
  S.patchedList = true;
}
if (!S.patchedExp) {
  const orig = M2Exporter.prototype.exportAsGLTF;
  M2Exporter.prototype.exportAsGLTF = async function (...a) { if (S.pendingEquip) this.setEquipmentModelsGLTF(S.pendingEquip); return orig.apply(this, a); };
  S.patchedExp = true;
}

if (!S.patchedToast) {
  const orig = core.setToast; S.toasts = [];
  core.setToast = function (type, msg, ...r) { if (type !== 'progress') S.toasts.push([type, String(msg).slice(0, 200)]); return orig.call(this, type, msg, ...r); };
  S.patchedToast = true;
}
const cfg = core.view.config;
const oldDir = cfg.exportDirectory;
cfg.exportCreatureFormat = 'GLB'; cfg.modelsExportAnimations = true; cfg.modelsExportTextures = true; cfg.overwriteFiles = true; cfg.creatureAutoPreview = true;
cfg.exportDirectory = ARGS.out;

if (!(core.view.activeModule && core.view.activeModule.__name === 'tab_creatures')) modules.set_active('tab_creatures');
const gotGL = await until(() => core.view.creatureViewerContext && core.view.creatureViewerContext.gl_context && !core.view.isBusy, 120000);
if (!gotGL) { cfg.exportDirectory = oldDir; return { error: 'no GL context in the creatures tab', mod: core.view.activeModule && core.view.activeModule.__name, busy: core.view.isBusy }; }
const ctx = core.view.creatureViewerContext;
const chars = JSON.parse(fs.readFileSync(ARGS.chars, 'utf8')).filter((c) => !ARGS.only || ARGS.only.includes(c.slug));
const out = [];
for (const c of chars) {
  const rec = { slug: c.slug };
  try {
    S.fake.set(c.npc, { id: c.npc, name: c.slug, displayID: c.display, always_items: [] });
    const before = ctx.getActiveRenderer();
    core.view.selectionCreatures = [`${c.slug} [${c.npc}]`];
    await sleep(400);
    const ok = await until(() => !core.view.isBusy && ctx.getActiveRenderer() && ctx.getActiveRenderer() !== before, 90000);
    if (!ok) { rec.err = 'preview did not load'; out.push(rec); continue; }
    await sleep(300);
    const ar = ctx.getActiveRenderer();
    const ex = X.get_extra(c.extra);
    // wow.export 0.2.21 skips the gear on a first preview (it tests is_character_model before setting it), and only the
    // checklist watcher dresses the creature. Untick and retick one slot to run that watcher.
    const list = core.view.creatureViewerEquipment || [];
    if (list.length) {
      const want = list.filter((it) => { const d = IM.getDisplayData(+String(it.label).match(/\((\d+)\)$/)[1], ex.DisplayRaceID, ex.DisplaySexID); return d && d.models && d.models.length; }).map((it) => it.id);
      list[0].checked = false; await sleep(2500);
      list[0].checked = true; await sleep(1500);
      const dressed = await until(() => want.every((id) => ctx.getEquipmentRenderers().has(id) || ctx.getCollectionRenderers().has(id)), 30000);
      await sleep(1200);
      rec.want = want; rec.dressed = dressed;
    }
    // A robe skirt can ride on the legs item while the chest item says "no skirt". 0.2.21 lets the chest win; Wowhead's
    // render of the Defias Wizard shows the skirt, so take the larger of the two.
    if (!S.idi) S.idi = await require_db2().ItemDisplayInfo.getAllRows();
    const gg = (slot) => { const it = list.find((x) => x.id === slot); const r = it && S.idi.get(+String(it.label).match(/\((\d+)\)$/)[1]); return (r && r.GeosetGroup && r.GeosetGroup[2]) || 0; };
    const skirt = Math.max(gg(5), gg(7));
    if (skirt > 0) {
      const gs = core.view.creatureViewerGeosets || [];
      if (gs.some((g) => g.id === 1301 + skirt)) {
        for (const g of gs) if (g.id > 1300 && g.id < 1400) g.checked = g.id === 1301 + skirt;
        if (ar.updateGeosets) ar.updateGeosets();
        rec.skirt = 1301 + skirt;
      }
    }
    const ce = new CharacterExporter(ar, ctx.getEquipmentRenderers(), ctx.getCollectionRenderers(), new Map());
    const equip = [];
    const seen = {};
    rec.geosets = (core.view.creatureViewerGeosets || []).filter((g) => g.checked).map((g) => g.id);
    rec.items = [];
    for (const g of ce.get_equipment_geometry(false)) {
      const entry = (g.is_collection_style ? ctx.getCollectionRenderers() : ctx.getEquipmentRenderers()).get(g.slot_id);
      const disp = IM.getDisplayData(entry.display_id, ex.DisplayRaceID, ex.DisplaySexID) || {};
      const key = g.slot_id + (g.is_collection_style ? 'c' : 'a');
      const i = seen[key] = (seen[key] ?? -1) + 1;
      let vertices = g.vertices, boneIndices = g.boneIndices, boneWeights = g.boneWeights, tex;
      // 0.2.21 knows one attachment point for the shoulder slot, so the right shoulder arrives as a body-skinned
      // "collection" model. It is a plain attachment model: point 5 is the right shoulder.
      const rightShoulder = g.is_collection_style && g.slot_id === 3;
      if (rightShoulder) { g.is_collection_style = false; g.attachment_id = 5; seen[key] = 1; }
      if (g.is_collection_style) {
        const first = Math.min((disp.models || []).length, (ctx.getEquipmentRenderers().get(g.slot_id)?.renderers || []).length);
        const ti = first + i < (disp.textures || []).length ? first + i : 0;
        tex = [(disp.textures || [])[ti]];
      } else {
        tex = [(disp.textures || [])[rightShoulder ? 1 : i] || (disp.textures || [])[0]];
        const att = ar.m2.getAttachmentById(g.attachment_id) || (ar.skelLoader && ar.skelLoader.getAttachmentById && ar.skelLoader.getAttachmentById(g.attachment_id));
        if (!att || att.bone < 0 || att.bone > 255) { rec.items.push({ slot: g.slot_id, skip: 'no attachment bone', att: g.attachment_id }); continue; }
        // bind pose: the item sits at the attachment point; one bone at full weight carries it through every clip
        const p = att.position; const dx = p[0], dy = p[2], dz = -p[1];
        vertices = new Float32Array(g.vertices.length);
        for (let v = 0; v < vertices.length; v += 3) { vertices[v] = g.vertices[v] + dx; vertices[v + 1] = g.vertices[v + 1] + dy; vertices[v + 2] = g.vertices[v + 2] + dz; }
        const n = vertices.length / 3;
        boneIndices = new Uint8Array(n * 4); boneWeights = new Uint8Array(n * 4);
        for (let v = 0; v < n; v++) { boneIndices[v * 4] = att.bone; boneWeights[v * 4] = 255; }
        rec.items.push({ slot: g.slot_id, att: g.attachment_id, bone: att.bone, at: [dx, dy, dz].map((x) => +x.toFixed(3)), verts: n, tex });
      }
      equip.push({ slot_id: g.slot_id, item_id: entry.display_id, renderer: g.renderer, vertices, normals: g.normals, uv: g.uv, uv2: g.uv2,
        boneIndices, boneWeights, textures: tex, is_collection_style: true });
      if (g.is_collection_style) rec.items.push({ slot: g.slot_id, collection: true, verts: vertices.length / 3, tex });
    }
    S.pendingEquip = equip.length ? equip : null;
    core.view.selectionCreatures = [S.fake.get(c.npc)];   // an object, so the preview watcher leaves it alone
    await tab.methods.export_creatures.call({ $core: core });
    S.pendingEquip = null;
    rec.toasts = S.toasts.splice(0);
    const f = ARGS.out + '/creatures/' + c.slug + '.glb';
    rec.bytes = fs.existsSync(f) ? fs.statSync(f).size : 0;
  } catch (e) { S.pendingEquip = null; rec.err = String(e.stack || e).slice(0, 500); }
  out.push(rec);
}
cfg.exportDirectory = oldDir;
return out;
