// Slim a wow.export creature GLB for the web: keep idle/attack/cast clips, WebP textures, meshopt.
// node opt_creature.mjs IN.glb OUT.glb [maxTex=512]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup, resample, textureCompress, meshopt, weld } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';

const [inp, out, maxTexArg] = process.argv.slice(2);
const maxTex = Number(maxTexArg || 512);
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
console.log(JSON.stringify({ out, clips: names }));
