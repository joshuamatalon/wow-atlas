// Slim a wow.export creature GLB for the web: keep idle/attack/cast clips, WebP textures, meshopt.
// node opt_creature.mjs IN.glb OUT.glb [maxTex=512] [--drop=Part1,Part2] [--cutout=material1,material2]
//   --drop    removes mesh nodes whose name ends in _PartN (geosets the game would not show)
//   --cutout  makes those materials alpha-tested, for cloth cards drawn on a see-through texture
//   --dropmat removes mesh nodes drawn with those materials (glow and flare cards that would draw as black squares)
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup, resample, textureCompress, meshopt, weld } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';

const flags = process.argv.slice(2).filter((a) => a.startsWith('--'));
const [inp, out, maxTexArg] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const maxTex = Number(maxTexArg || 512);
const flag = (k) => flags.filter((f) => f.startsWith(`--${k}=`)).flatMap((f) => f.split('=')[1].split(',')).filter(Boolean);
const DROP = flag('drop'), CUTOUT = flag('cutout'), DROPMAT = flag('dropmat');
await MeshoptEncoder.ready; await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
const doc = await io.read(inp);
const root = doc.getRoot();

const anims = root.listAnimations();
const pick = (re) => anims.find((a) => re.test(a.getName()));
const keep = new Set([
  pick(/^Stand \(ID 0 variation 0\)/) || pick(/^Stand/) || pick(/Hover|Idle/) || anims[0],
  pick(/^(Attack1H|AttackUnarmed|Attack2H|Attack2HL|AttackFist1H)\b/) || pick(/^Attack/),
  pick(/^SpellCast(Directed|Omni)?\b/) || pick(/^Spell/),
].filter(Boolean));
for (const a of anims) if (!keep.has(a)) {
  for (const s of a.listSamplers()) { const i = s.getInput(), o = s.getOutput(); s.dispose(); }
  for (const c of a.listChannels()) c.dispose();
  a.dispose();
}
const dropped = [], cut = [];
for (const n of root.listNodes()) if (n.getMesh() && DROP.some((d) => n.getName().endsWith('_' + d))) { dropped.push(n.getName()); n.dispose(); }
for (const n of root.listNodes()) { const me = n.getMesh(); if (me && me.listPrimitives().some((pr) => pr.getMaterial() && DROPMAT.includes(pr.getMaterial().getName()))) { dropped.push(n.getName()); n.dispose(); } }
for (const m of root.listMaterials()) if (CUTOUT.includes(m.getName())) { m.setAlphaMode('MASK').setAlphaCutoff(0.5); cut.push(m.getName()); }
const names = { };
for (const a of root.listAnimations()) {
  const n = a.getName();
  a.setName(/^Stand|Hover|Idle/.test(n) ? 'idle' : /^Attack/.test(n) ? 'attack' : /^Spell/.test(n) ? 'cast' : n);
  names[a.getName()] = n;
}
await doc.transform(
  resample(),
  prune({ keepAttributes: false }),
  dedup(),
  textureCompress({ encoder: sharp, targetFormat: 'webp', resize: [maxTex, maxTex], quality: 82 }),
  meshopt({ encoder: MeshoptEncoder, level: 'medium' }),
);
await io.write(out, doc);
console.log(JSON.stringify({ out, clips: names, dropped, cut }));
