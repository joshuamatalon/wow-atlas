// Command reader for headless use. Runs each *.js in CMD_DIR once as an async function body,
// writes the JSON result (or error) to OUT_DIR/<name>.json, then deletes the command file.
(function () {
	const fs = require('fs');
	const path = require('path');
	const CMD_DIR = 'C:/Users/joshu/wow-atlas/work/we-cmd';
	const OUT_DIR = 'C:/Users/joshu/wow-atlas/work/we-out';
	fs.mkdirSync(CMD_DIR, { recursive: true });
	fs.mkdirSync(OUT_DIR, { recursive: true });
	fs.writeFileSync(path.join(OUT_DIR, '_alive.json'), JSON.stringify({ t: Date.now() }));
	const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
	let busy = false;
	window.__drv = { state: {} };
	setInterval(async () => {
		if (busy) return;
		let files;
		try { files = fs.readdirSync(CMD_DIR).filter(f => f.endsWith('.js')).sort(); } catch (e) { return; }
		if (!files.length) return;
		busy = true;
		const f = files[0];
		const full = path.join(CMD_DIR, f);
		const body = fs.readFileSync(full, 'utf8');
		fs.unlinkSync(full);
		const out = path.join(OUT_DIR, f.replace(/\.js$/, '.json'));
		const t0 = Date.now();
		try {
			const fn = new AsyncFunction('fs', 'path', 'S', body);
			const r = await fn(fs, path, window.__drv.state);
			fs.writeFileSync(out, JSON.stringify({ ok: true, ms: Date.now() - t0, result: r }, null, 1));
		} catch (e) {
			fs.writeFileSync(out, JSON.stringify({ ok: false, ms: Date.now() - t0, error: String(e && e.stack || e) }, null, 1));
		}
		busy = false;
	}, 300);
})();
