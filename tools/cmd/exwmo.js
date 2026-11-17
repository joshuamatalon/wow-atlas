const core = require_core();
const mvu = require_model_viewer_utils();
const ExportHelper = require_export_helper();
const listfile = require_listfile();
const cfg = core.view.config;
cfg.modelsExportTextures = S.wmoTex === undefined ? false : S.wmoTex;
cfg.overwriteFiles = true;
const fdid = 114612;
const data = await core.view.casc.getFile(fdid);
const helper = new ExportHelper(1, 'model'); helper.start();
const r = await mvu.export_model({ core, data, file_data_id: fdid, file_name: listfile.getByID(fdid), format: 'GLB',
  export_path: 'C:/Users/joshu/wow-atlas/work/export/wmo/undercity.wmo', helper, file_manifest: [], variant_textures: [],
  geoset_mask: null, wmo_group_mask: null, wmo_set_mask: null, active_renderer: null, export_paths: null });
helper.finish();
return { r, name: listfile.getByID(fdid) };
