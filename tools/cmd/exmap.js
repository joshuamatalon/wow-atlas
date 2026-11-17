const core = require_core();
const ADTExporter = require_ADTExporter();
const ExportHelper = require_export_helper();
const cfg = core.view.config;
cfg.mapsIncludeFoliage = false; cfg.mapsIncludeLiquid = true; cfg.overwriteFiles = true;
const tiles = [1947,1948,1949,2011,2012,2013,2075,2076,2077];
const dir = 'C:/Users/joshu/wow-atlas/work/export/maps/2999';
const helper = new ExportHelper(tiles.length, 'tile'); helper.start();
const res = [];
for (const t of tiles) {
  const adt = new ADTExporter(2999, '2999', t);
  try { const out = await adt.export(dir, 512, undefined, helper); res.push([t, out]); }
  catch (e) { res.push([t, 'ERR ' + e.message + ' ' + (e.stack||'').split('\n').slice(0,3).join('|')]); }
}
helper.finish();
return res;
