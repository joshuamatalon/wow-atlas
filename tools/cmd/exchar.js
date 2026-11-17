const core = require_core();
const tab = require_tab_creatures();
const self = { $core: core };
if (!S.creaturesInit) { await tab.methods.initialize.call(self); S.creaturesInit = true; }
core.view.config.exportCreatureFormat = 'GLB';
const chars = JSON.parse(fs.readFileSync('C:/Users/joshu/wow-atlas/work/creature_chars.json', 'utf8'));
core.view.selectionCreatures = chars.map(c => ({ id: c.npc, name: c.slug, displayID: c.display, always_items: [] }));
await tab.methods.export_creatures.call(self);
return fs.readdirSync('C:/Users/joshu/wow-atlas/work/export/creatures');
