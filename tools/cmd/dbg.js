const core = require_core();
const EH = require_export_helper();
const DBC = require_DBCreatures();
const DX = require_DBCreatureDisplayExtra();
const di = DBC.getDisplayInfo(139050);
return { dir: core.view.config.exportDirectory, p: EH.getExportPath('creatures/x.m2'), di, extra: di && DX.get_extra(di.extendedDisplayInfoID) };
