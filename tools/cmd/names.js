const lf = require_listfile();
const ids = JSON.parse(fs.readFileSync('C:/Users/joshu/wow-atlas/work/roster_seed.json','utf8'));
return ids.map(r => [r.name, r.fdid, lf.getByID(r.fdid)]);
