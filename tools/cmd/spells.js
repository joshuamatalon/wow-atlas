// Read spell facts straight from the loaded client build, and save each spell's icon as PNG.
// ARGS: {ids: [spell ids], out: JSON path, icons: DIR}
const core = require_core();
const db2 = require_db2();
const BLP = require_blp();
const B = BLP.BLPFile || BLP;
const want = new Set(ARGS.ids);
const byId = async (t) => await db2[t].getAllRows();
const bySpell = async (t) => { const m = new Map(); for (const [id, r] of await db2[t].getAllRows()) if (want.has(r.SpellID)) { if (!m.has(r.SpellID)) m.set(r.SpellID, []); m.get(r.SpellID).push({ id, ...r }); } return m; };
const name = await byId('SpellName'), spell = await byId('Spell'), dur = await byId('SpellDuration'), cast = await byId('SpellCastTimes'),
  range = await byId('SpellRange'), radius = await byId('SpellRadius');
const misc = await bySpell('SpellMisc'), cat = await bySpell('SpellCategories'), cd = await bySpell('SpellCooldowns'), eff = await bySpell('SpellEffect');
const first = (v) => Array.isArray(v) ? v[0] : v;
const out = {};
fs.mkdirSync(ARGS.icons, { recursive: true });
for (const id of ARGS.ids) {
  const m = (misc.get(id) || [])[0] || {}, c = (cat.get(id) || [])[0] || {}, k = (cd.get(id) || [])[0] || {};
  const rg = range.get(m.RangeIndex) || {};
  const icon = m.SpellIconFileDataID || 0;
  if (icon && !fs.existsSync(ARGS.icons + '/' + icon + '.png')) { try { await new B(await core.view.casc.getFile(icon)).saveToPNG(ARGS.icons + '/' + icon + '.png'); } catch (e) {} }
  out[id] = {
    name: (name.get(id) || {}).Name_lang, text: (spell.get(id) || {}).Description_lang, aura: (spell.get(id) || {}).AuraDescription_lang,
    cast_ms: (cast.get(m.CastingTimeIndex) || {}).Base || 0, dur_ms: (dur.get(m.DurationIndex) || {}).Duration || 0,
    cd_ms: Math.max(k.RecoveryTime || 0, k.CategoryRecoveryTime || 0), range: [first(rg.RangeMin), first(rg.RangeMax)], school: m.SchoolMask,
    dispel: c.DispelType || 0, mechanic: c.Mechanic || 0, icon,
    effects: (eff.get(id) || []).sort((a, b) => a.EffectIndex - b.EffectIndex).map((e) => ({ eff: e.Effect, aura: e.EffectAura, base: e.EffectBasePointsF, period: e.EffectAuraPeriod,
      radius: (radius.get(first(e.EffectRadiusIndex)) || {}).Radius || 0, trigger: e.EffectTriggerSpell, misc: first(e.EffectMiscValue), chain: e.EffectChainTargets })),
  };
}
fs.writeFileSync(ARGS.out, JSON.stringify(out, null, 1));
return { n: Object.keys(out).length, build: core.view.casc.build && core.view.casc.build.Version, missingName: ARGS.ids.filter((i) => !out[i].name), noIcon: ARGS.ids.filter((i) => !out[i].icon) };
