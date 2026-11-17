const WDT = require_WDTLoader();
const casc = require_core().view.casc;
const data = await casc.getFile(7255103);
const w = new WDT(data); w.load();
const tiles = [];
if (w.entries) w.entries.forEach((e, i) => { if (e && (e.rootADT || e.obj0ADT)) tiles.push({ i, x: i % 64, y: Math.floor(i / 64), ...e }); });
const lf = require_listfile();
return { flags: w.flags, worldModel: w.worldModel, place: w.worldModelPlacement, ntiles: tiles.length, tiles: tiles.slice(0, 20),
  lfKeys: Object.keys(lf) };
