const core = require_core();
const BLP = require_blp();
const B = BLP.BLPFile || BLP;
const icons = JSON.parse(fs.readFileSync('C:/Users/joshu/wow-atlas/work/spell_icons.json', 'utf8'));
const dir = 'C:/Users/joshu/wow-atlas/site/icons'; fs.mkdirSync(dir, { recursive: true });
const done = [];
for (const fdid of new Set(Object.values(icons))) {
  const blp = new B(await core.view.casc.getFile(fdid));
  await blp.saveToPNG(dir + "/" + fdid + ".png");
  done.push(fdid);
}
return done.length;
