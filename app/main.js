import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

const $ = (s) => document.querySelector(s);
const params = new URLSearchParams(location.search);
const DATA_URL = 'data/' + (params.get('d') || 'ruins') + '.json';
const HOLO = new THREE.Color('#62f0ff');
const BOSS = new THREE.Color('#ffb54a');
const QUEST = new THREE.Color('#ffe066');
const DANGER = new THREE.Color('#ff5a5a');

// ---------- renderer ----------
const canvas = $('#stage');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: params.has('shot') });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x03060a, 1);
renderer.localClippingEnabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);
const clock = new THREE.Clock();
const uTime = { value: 0 };

// ---------- hologram materials ----------
function holoMaterial(color, opts = {}) {
  return new THREE.ShaderMaterial({
    uniforms: { uColor: { value: color.clone() }, uTime, uBase: { value: opts.base ?? 0.10 }, uRim: { value: opts.rim ?? 0.95 },
      uLow: { value: opts.low ?? -1e9 }, uHigh: { value: opts.high ?? 1e9 } },
    vertexShader: `
      varying vec3 vN; varying vec3 vV; varying vec3 vW;
      #include <clipping_planes_pars_vertex>
      void main(){
        vec4 wp = modelMatrix * vec4(position,1.0); vW = wp.xyz;
        vec4 mvPosition = viewMatrix * wp;
        vN = normalize(normalMatrix * normal); vV = normalize(-mvPosition.xyz);
        gl_Position = projectionMatrix * mvPosition;
        #include <clipping_planes_vertex>
      }`,
    fragmentShader: `
      uniform vec3 uColor; uniform float uTime; uniform float uBase; uniform float uRim; uniform float uLow; uniform float uHigh;
      varying vec3 vN; varying vec3 vV; varying vec3 vW;
      #include <clipping_planes_pars_fragment>
      void main(){
        #include <clipping_planes_fragment>
        float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
        float rim = pow(f, 2.2) * uRim;
        float up = clamp(normalize(vN).y, 0.0, 1.0);
        float scan = 0.5 + 0.5 * sin(vW.y * 1.4 - uTime * 2.2);
        float a = uBase + rim + up * 0.05 + scan * 0.03;
        gl_FragColor = vec4(uColor * (0.55 + rim * 1.6), clamp(a, 0.0, 1.0));
      }`,
    transparent: true, depthWrite: false, depthFunc: THREE.LessEqualDepth, blending: THREE.AdditiveBlending, clipping: true,
    side: THREE.FrontSide,
  });
}
const depthOnly = new THREE.MeshBasicMaterial({ colorWrite: false, polygonOffset: true, polygonOffsetFactor: 2, polygonOffsetUnits: 2 });

function hologramize(root, color, opts = {}) {
  const groups = [];
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isMesh) return;
    if (!o.geometry.attributes.normal) o.geometry.computeVertexNormals();
    const pre = new THREE.Mesh(o.geometry, depthOnly); pre.renderOrder = 0;
    const holo = new THREE.Mesh(o.geometry, holoMaterial(color, opts)); holo.renderOrder = 2;
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, opts.edgeAngle ?? 38),
      new THREE.LineBasicMaterial({ color: color.clone().multiplyScalar(opts.edgeBoost ?? 1.0), transparent: true, opacity: opts.edgeOpacity ?? 0.45, depthWrite: false, blending: THREE.AdditiveBlending }));
    edges.renderOrder = 3;
    const g = new THREE.Group(); g.name = o.name;
    g.add(pre, holo, edges);
    g.applyMatrix4(o.matrixWorld);
    groups.push(g);
  });
  const out = new THREE.Group();
  groups.forEach((g) => out.add(g));
  return out;
}

function setClip(group, planes) {
  group.traverse((o) => { if (o.material) { o.material.clippingPlanes = planes; o.material.needsUpdate = true; } });
}

// ---------- marker sprites ----------
const glyphCache = {};
function glyphTexture(kind) {
  if (glyphCache[kind]) return glyphCache[kind];
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d');
  const col = { boss: '#ffb54a', quest: '#ffe066', hazard: '#ff5a5a', entrance: '#9dffb0', tank: '#62f0ff', party: '#b9a2ff' }[kind] || '#62f0ff';
  g.translate(64, 64);
  g.shadowColor = col; g.shadowBlur = 14;
  g.strokeStyle = col; g.lineWidth = 6;
  g.fillStyle = 'rgba(3,10,16,0.85)';
  if (kind === 'boss') { g.beginPath(); for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i - Math.PI / 2; g.lineTo(Math.cos(a) * 46, Math.sin(a) * 46); } g.closePath(); g.fill(); g.stroke(); }
  else if (kind === 'quest' || kind === 'hazard') { g.beginPath(); g.moveTo(0, -48); g.lineTo(46, 0); g.lineTo(0, 48); g.lineTo(-46, 0); g.closePath(); g.fill(); g.stroke(); }
  else { g.beginPath(); g.arc(0, 0, 40, 0, Math.PI * 2); g.fill(); g.stroke(); }
  g.shadowBlur = 0; g.fillStyle = col; g.font = 'bold 50px system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  const sym = { boss: '☠', quest: '!', hazard: '⚠', entrance: '▲', tank: '⛨', party: '✦', pack: '' }[kind] ?? '';
  if (sym) g.fillText(sym, 0, 3);
  else { g.beginPath(); g.arc(0, 0, 13, 0, Math.PI * 2); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return (glyphCache[kind] = t);
}
function numberTexture(n, kind) {
  const c = document.createElement('canvas'); c.width = 128; c.height = 64;
  const g = c.getContext('2d');
  g.font = 'bold 40px system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = kind === 'boss' ? '#ffb54a' : '#bff8ff'; g.shadowColor = g.fillStyle; g.shadowBlur = 10;
  g.fillText(String(n), 64, 34);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function makeMarker(stop, idx) {
  const grp = new THREE.Group();
  const kind = stop.kind;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glyphTexture(kind), depthTest: false, transparent: true, sizeAttenuation: false }));
  const base = kind === 'boss' ? 0.075 : 0.05;
  s.scale.setScalar(base); s.position.y = 9; s.renderOrder = 10; s.userData = { stop, idx, base };
  const num = new THREE.Sprite(new THREE.SpriteMaterial({ map: numberTexture(idx + 1, kind), depthTest: false, transparent: true, sizeAttenuation: false }));
  num.scale.set(0.05, 0.025, 1); num.center.set(-0.35, -0.1); num.position.y = 9; num.renderOrder = 11;
  const col = kind === 'boss' ? BOSS : kind === 'quest' ? QUEST : kind === 'hazard' ? DANGER : HOLO;
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 9, 6, 1, true),
    new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false }));
  beam.position.y = 4.5;
  const ring = new THREE.Mesh(new THREE.RingGeometry(2.2, 2.8, 40), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  ring.rotation.x = -Math.PI / 2; ring.position.y = 0.3;
  grp.add(beam, ring, s, num);
  grp.position.fromArray(stop.pos);
  grp.userData = { sprite: s, ring, stop, idx };
  return grp;
}

// ---------- route line ----------
function makeRoute(points) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(p[0], p[1] + 1.2, p[2])), false, 'catmullrom', 0.2);
  const len = curve.getLength();
  const geo = new THREE.TubeGeometry(curve, Math.max(64, Math.floor(len / 3)), 0.55, 6, false);
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTime, uLen: { value: len }, uProg: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);} `,
    fragmentShader: `uniform float uTime; uniform float uLen; uniform float uProg; varying vec2 vUv;
      void main(){ float d = vUv.x * uLen; float dash = smoothstep(0.35, 0.5, fract(d / 9.0 - uTime * 0.9));
        float done = step(vUv.x, uProg);
        vec3 c = mix(vec3(0.25,0.95,1.0), vec3(1.0,0.82,0.45), done * 0.0);
        float a = 0.28 + dash * 0.55 + done * 0.25;
        gl_FragColor = vec4(c * (0.8 + dash), a); }`,
    transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  });
  const m = new THREE.Mesh(geo, mat); m.renderOrder = 5;
  m.userData = { curve, mat };
  return m;
}

// ---------- shared scene plumbing ----------
function makeStage() {
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x03060a, 0.0012);
  const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.5, 6000);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = 0.08;
  controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };
  controls.enabled = false;
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth / 2, innerHeight / 2), 0.55, 0.45, 0.22);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  return { scene, camera, controls, composer, bloom };
}
function gridFloor(size, y, color = HOLO) {
  const g = new THREE.PolarGridHelper(size, 16, 12, 96, color, color);
  g.material.transparent = true; g.material.opacity = 0.12; g.material.depthWrite = false; g.position.y = y;
  return g;
}

// ---------- camera flight ----------
let flight = null;
function flyTo(st, pos, target, ms = 900) {
  flight = { st, p0: st.camera.position.clone(), t0: st.controls.target.clone(), p1: pos.clone(), t1: target.clone(), start: performance.now(), ms };
}
function stepFlight() {
  if (!flight) return;
  const k = Math.min(1, (performance.now() - flight.start) / flight.ms);
  const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
  flight.st.camera.position.lerpVectors(flight.p0, flight.p1, e);
  flight.st.controls.target.lerpVectors(flight.t0, flight.t1, e);
  if (k >= 1) flight = null;
}

// ---------- app state ----------
let D; // data
let view = 'map';
let active; // active stage
const map = makeStage();
const beast = makeStage();
let mapRoot, route, markers = [], stopIdx = -1, part = 0;
const partClip = [new THREE.Plane(new THREE.Vector3(0, -1, 0), 0)];

function esc(s) { return String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function enemyBy(slug) { return D.enemies.find((e) => e.slug === slug); }

async function boot() {
  D = await (await fetch(DATA_URL)).json();
  $('#dname').textContent = D.dungeon.name;
  document.title = D.dungeon.name + ' · Atlas';
  // parts toggle
  const parts = $('#parts');
  D.parts.forEach((p, i) => {
    const b = document.createElement('button'); b.textContent = p.short; b.onclick = () => setPart(i, true);
    parts.appendChild(b);
  });
  // map
  const gltf = await loader.loadAsync(D.map.model);
  mapRoot = new THREE.Group();
  const layerColor = { terrain: new THREE.Color('#1f6f86'), undercity: HOLO, ruins: new THREE.Color('#9ff6ff') };
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse((o) => { if (o.isMesh) o.name = o.name || o.parent?.name; });
  for (const child of [...gltf.scene.children]) {
    const name = child.name || '';
    const col = layerColor[name] || HOLO;
    const opts = name === 'terrain' ? { base: 0.012, rim: 0.16, edgeOpacity: 0.07, edgeAngle: 55 } : { base: 0.025, rim: 0.55, edgeOpacity: 0.32 };
    const h = hologramize(child, col, opts); h.name = name; mapRoot.add(h);
  }
  map.scene.add(mapRoot);
  map.scene.add(gridFloor(D.map.gridRadius || 420, D.map.floorY ?? -90));
  // markers + route
  D.stops.forEach((s, i) => { const m = makeMarker(s, i); markers.push(m); map.scene.add(m); });
  route = makeRoute(D.route || D.stops.map((s) => s.pos));
  map.scene.add(route);
  const c = new THREE.Vector3().fromArray(D.map.center);
  map.controls.target.copy(c);
  map.camera.position.copy(c).add(new THREE.Vector3().fromArray(D.map.camOffset));
  map.controls.maxDistance = 1400; map.controls.minDistance = 25;
  map.controls.maxPolarAngle = Math.PI * 0.49;
  setPart(D.map.startPart ?? 1, false);
  if (params.has('cam')) { const v = params.get('cam').split(',').map(Number); map.camera.position.set(v[0], v[1], v[2]); map.controls.target.set(v[3], v[4], v[5]); }
  if (params.has('part')) setPart(+params.get('part'), false);
  buildBestiary();
  buildBossList();
  setView(params.get('v') || 'map');
  if (params.has('stop')) gotoStop(+params.get('stop'));
  if (params.has('beast')) openBeast(params.get('beast'));
  if (params.has('boss')) openBoss(params.get('boss'));
  $('#loading').style.opacity = 0; setTimeout(() => $('#loading').classList.add('hidden'), 500);
  window.__ready = true;
}

function setPart(i, fly) {
  part = i;
  [...$('#parts').children].forEach((b, j) => b.classList.toggle('on', j === i));
  const p = D.parts[i];
  if (p.clipAbove != null) { partClip[0].constant = p.clipAbove; setClip(mapRoot, partClip); }
  else setClip(mapRoot, null);
  markers.forEach((m) => { m.visible = (m.userData.stop.part ?? i) === i || p.showAll; });
  if (fly && p.cam) flyTo(map, new THREE.Vector3().fromArray(p.cam.pos), new THREE.Vector3().fromArray(p.cam.target));
}

// ---------- map: walk the route ----------
function gotoStop(i) {
  i = Math.max(0, Math.min(D.stops.length - 1, i));
  stopIdx = i;
  const s = D.stops[i];
  if ((s.part ?? part) !== part) setPart(s.part, false);
  const target = new THREE.Vector3().fromArray(s.pos);
  const dir = map.camera.position.clone().sub(map.controls.target);
  const want = s.kind === 'boss' ? 95 : 120;
  dir.setLength(want); if (dir.y < want * 0.55) dir.y = want * 0.55; dir.setLength(want);
  flyTo(map, target.clone().add(dir), target);
  $('#stopn').textContent = `Stop ${i + 1} of ${D.stops.length}`;
  $('#stopname').textContent = s.title;
  route.userData.mat.uniforms.uProg.value = (i + 0.5) / D.stops.length;
  markers.forEach((m, j) => { m.userData.sprite.userData.on = j === i; });
  const card = $('#stopcard');
  const tagCls = s.kind === 'boss' ? 'boss' : s.kind === 'quest' ? 'quest' : s.kind === 'hazard' ? 'hazard' : '';
  const tag = { boss: 'Boss', quest: 'Quest', hazard: 'Hazard', pack: 'Pull', entrance: 'Start', event: 'Event' }[s.kind] || 'Stop';
  let h = `<span class="tag ${tagCls}">${tag} · ${esc(D.parts[s.part ?? part].name)}</span><h2>${esc(s.title)}</h2>`;
  for (const para of s.text || []) h += `<p>${esc(para)}</p>`;
  if (s.say) h += `<div class="say"><b>Say</b>${esc(s.say)}</div>`;
  const chips = (s.enemies || []).map((sl) => { const e = enemyBy(sl); return e ? `<button class="chip ${e.boss ? 'boss' : ''}" data-beast="${sl}">${esc(e.name)}</button>` : ''; }).join('');
  if (s.kind === 'boss' && s.boss) h += `<div class="chips"><button class="chip boss" data-boss="${s.boss}">Open the fight ›</button>${chips}</div>`;
  else if (chips) h += `<div class="chips">${chips}</div>`;
  card.innerHTML = h; card.classList.remove('hidden'); card.scrollTop = 0;
}
$('#prev').onclick = () => gotoStop(stopIdx < 0 ? 0 : stopIdx - 1);
$('#next').onclick = () => gotoStop(stopIdx + 1);
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-beast]'); if (b) { setView('beasts'); openBeast(b.dataset.beast); return; }
  const o = e.target.closest('[data-boss]'); if (o) { setView('bosses'); openBoss(o.dataset.boss); return; }
  const bk = e.target.closest('[data-back]'); if (bk) { if (bk.dataset.back === 'beasts') closeBeast(); else closeBoss(); }
  const t = e.target.closest('#tabs button'); if (t) setView(t.dataset.view);
});

// tap on markers
const ray = new THREE.Raycaster();
let downAt = null;
canvas.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY, performance.now()]; });
canvas.addEventListener('pointerup', (e) => {
  if (!downAt) return;
  const moved = Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]);
  if (moved > 8 || performance.now() - downAt[2] > 400) return;
  if (view !== 'map' && !(view === 'bosses' && bossOpen)) return;
  const v = new THREE.Vector2((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  // screen-space pick on sprites (they are fixed pixel size)
  let best = null, bestD = 34;
  for (const m of markers) {
    if (!m.visible) continue;
    const p = new THREE.Vector3(); m.userData.sprite.getWorldPosition(p); p.project(map.camera);
    if (p.z > 1) continue;
    const dx = (p.x - v.x) * innerWidth / 2, dy = (p.y - v.y) * innerHeight / 2;
    const d = Math.hypot(dx, dy); if (d < bestD) { bestD = d; best = m; }
  }
  if (best && view === 'map') gotoStop(best.userData.idx);
});

// ---------- bestiary ----------
let beastModel = null, mixer = null, clips = {};
const beastScene = beast.scene;
beastScene.fog = null;
beastScene.add(new THREE.HemisphereLight(0xbfefff, 0x0a1a22, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(3, 6, 4); beastScene.add(key);
const rimL = new THREE.DirectionalLight(0x62f0ff, 2.2); rimL.position.set(-4, 3, -5); beastScene.add(rimL);
const pad = new THREE.Group();
{
  for (let i = 0; i < 3; i++) {
    const r = new THREE.Mesh(new THREE.RingGeometry(1.0 + i * 0.32, 1.04 + i * 0.32, 96), new THREE.MeshBasicMaterial({ color: HOLO, transparent: true, opacity: 0.55 - i * 0.15, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false }));
    r.rotation.x = -Math.PI / 2; pad.add(r);
  }
  const disc = new THREE.Mesh(new THREE.CircleGeometry(1.0, 64), new THREE.MeshBasicMaterial({ color: HOLO, transparent: true, opacity: 0.08, blending: THREE.AdditiveBlending, depthWrite: false }));
  disc.rotation.x = -Math.PI / 2; pad.add(disc);
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 2.2, 64, 1, true), new THREE.ShaderMaterial({
    uniforms: { uTime }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: 'uniform float uTime; varying vec2 vUv; void main(){ float a = (1.0 - vUv.y) * 0.07 * (0.7 + 0.3*sin(vUv.y*40.0 - uTime*3.0)); gl_FragColor = vec4(0.38,0.94,1.0,a);}',
  }));
  cone.position.y = 1.1; pad.add(cone);
  beastScene.add(pad);
}
beast.camera.position.set(0, 1.6, 5.2); beast.controls.target.set(0, 1, 0);
beast.controls.enablePan = false; beast.controls.minDistance = 1.5; beast.controls.maxDistance = 14;
beast.bloom.strength = 0.25; beast.bloom.threshold = 0.85;

function buildBestiary() {
  const grid = $('#grid'); grid.innerHTML = '';
  const secs = [['Bosses', D.enemies.filter((e) => e.boss)], ['Trash', D.enemies.filter((e) => !e.boss)]];
  for (const [title, list] of secs) {
    const h = document.createElement('div'); h.className = 'gsec'; h.textContent = title; grid.appendChild(h);
    for (const e of list) {
      const b = document.createElement('button'); b.className = 'cell' + (e.boss ? ' boss' : ''); b.dataset.beast = e.slug;
      b.innerHTML = `<img loading="lazy" alt="" src="thumbs/${e.slug}.webp"><span>${esc(e.name)}</span>`;
      grid.appendChild(b);
    }
  }
}
async function openBeast(slug) {
  const e = enemyBy(slug); if (!e) return;
  $('#grid').classList.add('hidden'); $('#beast').classList.remove('hidden');
  const card = $('#beastcard');
  let h = `<span class="tag ${e.boss ? 'boss' : ''}">${e.boss ? 'Boss' : 'Enemy'}${e.level ? ' · Level ' + esc(e.level) : ''}${e.type ? ' · ' + esc(e.type) : ''}</span><h2>${esc(e.name)}</h2>`;
  if (e.where) h += `<p><b>Where:</b> ${esc(e.where)}</p>`;
  if (e.tank) h += `<div class="role">You, the tank</div><p>${esc(e.tank)}</p>`;
  if (e.group) h += `<div class="role">The group</div><p>${esc(e.group)}</p>`;
  for (const a of e.abilities || []) h += `<div class="ab"><img alt="" src="icons/${a.icon}.png"><div><b>${esc(a.name)}.</b> ${esc(a.line)}</div></div>`;
  if (e.say) h += `<div class="say"><b>Say</b>${esc(e.say)}</div>`;
  card.innerHTML = h; card.scrollTop = 0;
  if (beastModel) { beastScene.remove(beastModel); beastModel = null; mixer = null; }
  const gltf = await loader.loadAsync(`models/creatures/${e.model || e.slug}.glb`);
  if (enemyBy(slug) !== e || $('#beast').classList.contains('hidden')) return;
  const m = gltf.scene;
  m.traverse((o) => { if (o.isMesh) { o.frustumCulled = false; if (o.material) { o.material.side = THREE.DoubleSide; if (o.material.map) o.material.alphaTest = 0.4; } } });
  mixer = new THREE.AnimationMixer(m); clips = {};
  for (const c of gltf.animations) clips[c.name] = c;
  playClip('idle');
  mixer.update(0.01);
  // frame the model on the pad
  const box = new THREE.Box3().setFromObject(m);
  const size = box.getSize(new THREE.Vector3()); const ctr = box.getCenter(new THREE.Vector3());
  const s = 2.2 / Math.max(size.y, size.x * 0.8, size.z * 0.8);
  m.scale.setScalar(s); m.position.set(-ctr.x * s, -box.min.y * s, -ctr.z * s);
  beastModel = new THREE.Group(); beastModel.add(m); beastScene.add(beastModel);
  const ang = e.view ?? 0.6;
  beast.camera.position.set(Math.sin(ang) * 5.4, 1.9, Math.cos(ang) * 5.4); beast.controls.target.set(0, 1.05, 0); beast.controls.update();
  const bar = $('#clipbar'); bar.innerHTML = '';
  for (const n of ['idle', 'attack', 'cast']) if (clips[n]) { const b = document.createElement('button'); b.textContent = n[0].toUpperCase() + n.slice(1); b.onclick = () => playClip(n); bar.appendChild(b); }
  [...bar.children].forEach((b) => b.classList.toggle('on', b.textContent.toLowerCase() === 'idle'));
  window.__beastReady = slug;
}
function playClip(n) {
  if (!mixer || !clips[n]) return;
  mixer.stopAllAction();
  const a = mixer.clipAction(clips[n]); a.reset(); a.setLoop(THREE.LoopRepeat); a.play();
  [...$('#clipbar').children].forEach((b) => b.classList.toggle('on', b.textContent.toLowerCase() === n));
}
function closeBeast() { $('#beast').classList.add('hidden'); $('#grid').classList.remove('hidden'); window.__beastReady = null; }

// ---------- bosses ----------
let bossOpen = null, bossDeco = null, stepTimer = null;
function buildBossList() {
  const list = $('#bosslist'); list.innerHTML = '';
  D.bosses.forEach((b, i) => {
    const r = document.createElement('button'); r.className = 'brow'; r.dataset.boss = b.slug;
    r.innerHTML = `<img alt="" src="thumbs/${b.enemy || b.slug}.webp"><div><div class="n">${esc(b.name)}</div><div class="s">${esc(b.sub || '')}</div></div><div class="o">${i + 1}</div>`;
    list.appendChild(r);
  });
}
function floorShape(sh) {
  const col = sh.color === 'safe' ? new THREE.Color('#62f0ff') : sh.color === 'party' ? new THREE.Color('#b9a2ff') : DANGER;
  let geo;
  if (sh.type === 'circle') geo = new THREE.CircleGeometry(sh.r, 64);
  else if (sh.type === 'ring') geo = new THREE.RingGeometry(sh.r0, sh.r, 64);
  else if (sh.type === 'cone') geo = new THREE.CircleGeometry(sh.r, 48, -sh.angle / 2, sh.angle);
  else if (sh.type === 'line') geo = new THREE.PlaneGeometry(sh.w, sh.r).translate(0, sh.r / 2, 0);
  else if (sh.type === 'arrow') { const s = new THREE.Shape(); s.moveTo(-0.6, 0); s.lineTo(0.6, 0); s.lineTo(0.6, sh.r - 2.5); s.lineTo(1.8, sh.r - 2.5); s.lineTo(0, sh.r); s.lineTo(-1.8, sh.r - 2.5); s.lineTo(-0.6, sh.r - 2.5); s.closePath(); geo = new THREE.ShapeGeometry(s); }
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTime, uCol: { value: col }, uPulse: { value: sh.pulse ?? 1 }, uOn: { value: 0 } },
    transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: 'varying vec2 vUv; varying vec3 vP; void main(){vUv=uv; vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader: `uniform float uTime; uniform vec3 uCol; uniform float uPulse; uniform float uOn; varying vec2 vUv; varying vec3 vP;
      void main(){ float r = length(vP.xy); float wave = fract(r*0.08 - uTime*0.6*uPulse);
        float edge = smoothstep(0.92, 1.0, vUv.x) + smoothstep(0.92,1.0,1.0-vUv.x) + smoothstep(0.92,1.0,vUv.y)+smoothstep(0.92,1.0,1.0-vUv.y);
        float a = (0.12 + 0.22*smoothstep(0.7,1.0,wave)) * (0.45 + 0.55*uOn);
        gl_FragColor = vec4(uCol*(1.0+uOn), a); }`,
  });
  const m = new THREE.Mesh(geo, mat); m.rotation.x = -Math.PI / 2; m.renderOrder = 6;
  const g = new THREE.Group(); g.add(m);
  g.position.fromArray(sh.at); g.position.y += 0.4; if (sh.dir != null) g.rotation.y = sh.dir;
  g.userData = { mat, step: sh.step };
  return g;
}
function openBoss(slug) {
  const b = D.bosses.find((x) => x.slug === slug); if (!b) return;
  bossOpen = b;
  $('#bosslist').classList.add('hidden'); $('#boss').classList.remove('hidden');
  if (bossDeco) map.scene.remove(bossDeco);
  bossDeco = new THREE.Group();
  for (const sh of b.shapes || []) bossDeco.add(floorShape(sh));
  for (const [kind, p] of [['tank', b.tankSpot], ['party', b.partySpot]]) {
    if (!p) continue;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glyphTexture(kind), depthTest: false, transparent: true, sizeAttenuation: false }));
    s.scale.setScalar(0.06); s.position.fromArray(p); s.position.y += 4; s.renderOrder = 12; bossDeco.add(s);
    const ring = new THREE.Mesh(new THREE.RingGeometry(2.6, 3.4, 40), new THREE.MeshBasicMaterial({ color: kind === 'tank' ? HOLO : new THREE.Color('#b9a2ff'), transparent: true, opacity: 0.9, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
    ring.rotation.x = -Math.PI / 2; ring.position.fromArray(p); ring.position.y += 0.5; ring.renderOrder = 7; bossDeco.add(ring);
  }
  map.scene.add(bossDeco);
  // cut the room out of the map
  const c = new THREE.Vector3().fromArray(b.room.center); const r = b.room.radius; const top = c.y + (b.room.up ?? 14);
  const planes = [
    new THREE.Plane(new THREE.Vector3(1, 0, 0), -(c.x - r)), new THREE.Plane(new THREE.Vector3(-1, 0, 0), c.x + r),
    new THREE.Plane(new THREE.Vector3(0, 0, 1), -(c.z - r)), new THREE.Plane(new THREE.Vector3(0, 0, -1), c.z + r),
    new THREE.Plane(new THREE.Vector3(0, -1, 0), top), new THREE.Plane(new THREE.Vector3(0, 1, 0), -(c.y - (b.room.down ?? 6))),
  ];
  setClip(mapRoot, planes);
  markers.forEach((m) => { m.visible = false; }); route.visible = false;
  const ang = b.room.view ?? 0.0;
  const dist = r * 2.3;
  map.camera.position.set(c.x + Math.sin(ang) * dist * 0.55, c.y + dist * 0.85, c.z + Math.cos(ang) * dist * 0.55);
  map.controls.target.copy(c);
  flight = null;
  const card = $('#bosscard');
  let h = `<span class="tag boss">Boss ${D.bosses.indexOf(b) + 1} of ${D.bosses.length}${b.level ? ' · Level ' + esc(b.level) : ''}</span><h2>${esc(b.name)}</h2>`;
  if (b.intro) h += `<p>${esc(b.intro)}</p>`;
  h += `<div class="legend"><span><i style="background:#62f0ff"></i>Tank holds here</span><span><i style="background:#b9a2ff"></i>Group stands here</span><span><i style="background:#ff5a5a"></i>Danger</span></div>`;
  h += `<ol class="steps">${(b.steps || []).map((s, i) => `<li data-step="${i}">${esc(s)}</li>`).join('')}</ol>`;
  if (b.say) h += `<div class="say"><b>Say before the pull</b>${esc(b.say)}</div>`;
  if (b.loot?.length) h += `<div class="role">Loot</div><ul class="loot">${b.loot.map((l) => `<li class="${l.mine ? 'mine' : ''}">${esc(l.name)}${l.slot ? ' · ' + esc(l.slot) : ''}</li>`).join('')}</ul>`;
  h += `<div class="chips"><button class="chip boss" data-beast="${b.enemy || b.slug}">Turn the model ›</button></div>`;
  card.innerHTML = h; card.scrollTop = 0;
  card.querySelectorAll('[data-step]').forEach((li) => li.addEventListener('click', () => lightStep(+li.dataset.step)));
  lightStep(0);
  clearInterval(stepTimer);
  stepTimer = setInterval(() => { if (bossOpen === b) lightStep(((window.__step ?? 0) + 1) % (b.steps?.length || 1)); }, 4200);
  window.__bossReady = slug;
}
function lightStep(i) {
  window.__step = i;
  document.querySelectorAll('#bosscard [data-step]').forEach((li) => li.classList.toggle('on', +li.dataset.step === i));
  bossDeco?.children.forEach((g) => { if (g.userData.mat) g.userData.mat.uniforms.uOn.value = (g.userData.step == null || g.userData.step === i) ? 1 : 0; });
}
function closeBoss() {
  bossOpen = null; clearInterval(stepTimer);
  if (bossDeco) { map.scene.remove(bossDeco); bossDeco = null; }
  $('#boss').classList.add('hidden'); $('#bosslist').classList.remove('hidden');
  route.visible = true; setPart(part, false);
}

// ---------- views ----------
function setView(v) {
  view = v;
  document.querySelectorAll('#tabs button').forEach((b) => b.classList.toggle('on', b.dataset.view === v));
  $('#v-map').classList.toggle('hidden', v !== 'map');
  $('#v-beasts').classList.toggle('hidden', v !== 'beasts');
  $('#v-bosses').classList.toggle('hidden', v !== 'bosses');
  $('#parts').classList.toggle('hidden', v !== 'map');
  if (v !== 'bosses' && bossOpen) closeBoss();
  if (v === 'map' && !bossOpen) { route.visible = true; setPart(part, false); }
}
function currentStage() {
  if (view === 'beasts' && !$('#beast').classList.contains('hidden')) return beast;
  return map;
}

// ---------- loop ----------
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  for (const st of [map, beast]) { st.camera.aspect = w / h; st.camera.updateProjectionMatrix(); st.composer.setSize(w, h); st.composer.setPixelRatio(Math.min(devicePixelRatio, 2)); }
  if (w < 900) beast.camera.setViewOffset(w, h, 0, h * 0.2, w, h); else beast.camera.setViewOffset(w, h, -w * 0.16, 0, w, h);
  if (w >= 900) map.camera.setViewOffset(w, h, w * 0.12, 0, w, h); else map.camera.setViewOffset(w, h, 0, h * 0.12, w, h);
}
addEventListener('resize', resize); resize();
function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  uTime.value += dt;
  const st = currentStage();
  if (active !== st) { if (active) active.controls.enabled = false; st.controls.enabled = true; active = st; }
  stepFlight();
  st.controls.update();
  if (st === beast && mixer) mixer.update(dt);
  if (st === map) for (const m of markers) {
    const sp = m.userData.sprite; const on = sp.userData.on;
    const k = on ? 1.35 + 0.12 * Math.sin(uTime.value * 5) : 1;
    sp.scale.setScalar(sp.userData.base * k);
    m.userData.ring.scale.setScalar(1 + 0.25 * Math.sin(uTime.value * 2 + m.userData.idx));
  }
  st.composer.render();
}
tick();
boot().catch((err) => { $('#loading span').textContent = 'Failed: ' + err.message; console.error(err); });
