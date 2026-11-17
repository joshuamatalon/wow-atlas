const core = require_core();
const mvu = require_model_viewer_utils();
const ExportHelper = require_export_helper();
const listfile = require_listfile();
const cfg = core.view.config;
cfg.exportCreatureFormat = 'GLB'; cfg.exportModelFormat = 'GLB'; cfg.modelsExportAnimations = true; cfg.overwriteFiles = true;
const jobs = JSON.parse(fs.readFileSync('C:/Users/joshu/wow-atlas/work/creature_jobs.json', 'utf8'));
const out = [];
const helper = new ExportHelper(jobs.length, 'creature'); helper.start();
for (const j of jobs) {
  try {
    const data = await core.view.casc.getFile(j.fdid);
    const export_path = 'C:/Users/joshu/wow-atlas/work/export/creatures/' + j.slug + '.m2';
    const r = await mvu.export_model({ core, data, file_data_id: j.fdid, file_name: listfile.getByID(j.fdid) || ('unknown_' + j.fdid + '.m2'),
      format: 'GLB', export_path, helper, file_manifest: [], variant_textures: j.tex, geoset_mask: null, wmo_group_mask: null, wmo_set_mask: null,
      active_renderer: null, export_paths: null });
    out.push([j.slug, 'ok', r]);
  } catch (e) { out.push([j.slug, 'ERR', String(e.stack || e).slice(0, 400)]); }
}
helper.finish();
return { cfg: { anims: cfg.modelsExportAnimations, fmt: cfg.exportModelFormat }, out };
