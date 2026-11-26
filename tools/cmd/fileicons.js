// Save icon files (by file data id) as PNG. ARGS: {ids: [file data ids], out: DIR}
const core = require_core();
const BLP = require_blp();
const B = BLP.BLPFile || BLP;
fs.mkdirSync(ARGS.out, { recursive: true });
const done = [], failed = [];
for (const id of ARGS.ids) {
  const f = ARGS.out + '/' + id + '.png';
  try { if (!fs.existsSync(f)) await new B(await core.view.casc.getFile(id)).saveToPNG(f); done.push(id); } catch (e) { failed.push([id, String(e).slice(0, 120)]); }
}
return { done, failed };
