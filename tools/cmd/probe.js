const core = require_core();
const mods = (typeof require_modules === 'function') ? Object.keys(require_modules()) : null;
return { coreKeys: Object.keys(core), viewKeys: Object.keys(core.view || {}).slice(0, 400).join(','), mods,
  hasModules: typeof require_modules, cfg: core.view && core.view.config ? { allow: core.view.config.allowCacheCollection, fmt: core.view.config.exportCreatureFormat, dir: core.view.config.exportDirectory } : null };
