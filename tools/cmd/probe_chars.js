// Read what the client says each character-model creature wears. ARGS: {chars: PATH}
const core = require_core();
const X = require_DBCreatureDisplayExtra();
const E = require_DBNpcEquipment();
const IM = require_DBItemModels();
const CC = require_DBCharacterCustomization();
const C = require_DBCreatures();
const listfile = require_listfile();
for (const m of [X, E, IM, CC, C]) for (const k of ['ensureInitialized', 'ensure_initialized', 'initialize']) if (typeof m[k] === 'function') { try { await m[k](); } catch (e) {} break; }
const chars = JSON.parse(fs.readFileSync(ARGS.chars, 'utf8'));
const out = [];
for (const c of chars) {
  const di = C.getDisplayInfo ? C.getDisplayInfo(c.display) : null;
  const ex = X.get_extra(c.extra);
  const eq = E.get_equipment(c.extra);
  const items = [];
  if (eq) for (const [slot, disp] of eq) {
    const d = IM.getDisplayData ? IM.getDisplayData(disp, ex && ex.DisplayRaceID, ex && ex.DisplaySexID) : null;
    items.push({ slot, disp, models: d && d.models, tex: d && d.textures, names: d && d.models ? d.models.map(f => listfile.getByID(f)) : null });
  }
  let model = null;
  try { const id = CC.get_chr_model_id(ex.DisplayRaceID, ex.DisplaySexID); const f = CC.get_model_file_data_id(id); model = [id, f, listfile.getByID(f)]; } catch (e) { model = String(e); }
  const bake = ex && (ex.HDBakeMaterialResourcesID || ex.BakeMaterialResourcesID);
  out.push({ slug: c.slug, di: di && { ext: di.extendedDisplayInfoID }, ex, model, bake, bakeFile: bake ? CC.get_texture_file_data_id(bake) : null, choices: X.get_customization_choices(c.extra).length, items });
}
return { ctx: !!core.view.creatureViewerContext, gl: !!(core.view.creatureViewerContext && core.view.creatureViewerContext.gl_context), mod: core.view.activeModule && core.view.activeModule.__name, out };
