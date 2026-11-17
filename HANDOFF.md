# HANDOFF: Ruins of Lordaeron atlas

Live: https://joshuamatalon.github.io/wow-atlas/ (gh-pages branch, built from `site/` by `tools/publish.sh`).
Brief: the prompt Josh pasted on 2026-11-17 (it is reproduced in the session that built this; his request is quoted in it).
State at 2026-11-17 12:35, stage 6 of 6 reached once, with the open items below.

## What is done
- Map: the dungeon's real geometry (terrain, the Undercity WMO with the surface ruins, small ruin WMOs) exported from the
  local `wowf` client by wow.export 0.2.21, assembled by its own Blender add-on, cropped to the city, decimated and
  meshopt-compressed (`site/models/map.glb`, 2.75 MB). Drawn as a hologram (depth pre-pass, fresnel rim, edge lines, bloom).
  The underground rings are clipped away (the dungeon is the surface city, one floor). 23 route stops, numbered, walked by
  Next and Previous buttons; a tap on a marker flies there.
- Bestiary: all 32 creatures on the Wowhead Forever zone list (bosses, trash, the quest giver) with their real models,
  textures and three clips (idle, attack, cast), each under 2 MB, loaded only when opened. Cards follow the 50-word limit.
- Fight views for all seven encounters: the room cut from the map, tank spot, group spot, animated floor shapes from the
  spell radius table, at most six one-sentence steps, a line to say, loot with his pieces marked.
- Checks run on the live address: WebKit at iPhone size and Chromium at desktop, no console errors; first view 3.6 MB;
  a drag turns the model (shots `L_wk_beast_a.png` and `L_wk_beast.png`); `tools/check_copy.py` passes (limits, one
  sentence per step, no em dash, no source marks, no damage figures); `prose_check.py` reports 0 banned words and 0 em
  dashes, and its 39 "fragments" are imperatives and verbs outside its word list.

## Open, in order of value
1. Three human-model NPCs are wrong: Lordaeron Captain (no helmet or shoulders), Ghostly Citizen and Captain Truman
   (wrong hair and robe geosets, no armor models). wow.export's creature export skips NPC equipment models and the
   preview geoset mask when no preview is active. Routes to try: drive wow.export's character tab
   (`require_tab_characters`, `CharacterExporter`) with the NPC's race, customization and `DBNpcEquipment` items;
   or the fallback from the brief, a spin of frames from Wowhead's model viewer (display ids 139050, 10478, 5711).
   See `work/shots/compare.png` for all 32 against Wowhead.
2. Pack positions are judgement along streets, from the guides' route text. Boss positions come from Warcraft Tavern's
   portrait map registered to the geometry. Replace both with what a video or his own run shows. After his first run
   read Scribe `--part mobs`, `visits`, `encounters`, `fights`.
3. Only one of the five Crest of Lordaeron spots has a marker.
4. Lordaeron Captain's loot is from Icy Veins only.

## How to rebuild
- Data and copy: edit `tools/make_data.py`, then `python -I tools/make_data.py`, `python -I tools/check_copy.py`,
  `sh tools/publish.sh "message"`. Positions are pixels on `work/shots/ortho.png`; heights come from
  `python -I tools/bake_heights.py http://127.0.0.1:8765/` (serve `site/` first with `python -I -m http.server 8765`).
- Page code: `app/main.js`, `app/style.css`, `app/index.html`; `tools/build.sh` bundles three.js with esbuild from
  `work/node/node_modules` (git-ignored; `npm i three esbuild @gltf-transform/core @gltf-transform/functions
  @gltf-transform/extensions meshoptimizer sharp gltfpack --legacy-peer-deps`).
- Screenshots: `python -I tools/shot.py BASE_URL work/shots SPEC.json`. Thumbnails: `tools/thumbs.py`. Model check
  sheet: `tools/compare_sheet.py`.
- Client export: unzip wow.export portable to `work/dl/wowexport/app`, run `tools/we_patch.py APP OUT_DIR` (hidden window,
  no cache upload to its author's server, GLB), copy `tools/wowexport/driver.js` into `app/src` and add it after `app.js`
  in `index.html`. Start `wow.export.exe` hidden. `python -I tools/we.py tools/cmd/load.js 600` loads the `wowf` build;
  `exmap.js` exports the nine map tiles, `ex1.js` the creatures listed in `work/creature_jobs.json`, `exchar2.js` the
  character-model creatures, `icons.js` the ability icons. Blender: `tools/bl_assemble.py` then `tools/bl_crop.py`.
- Another dungeon: a new data file in `site/data/NAME.json` and a map GLB; open it with `?d=NAME`.

## Facts kept out of the page
`work/ledger.md` (one line per fact and its source) and `work/research/fights.md` (every claim tagged with its source).

## Changes after the first handoff
- 2026-11-17 13:45: a tap on empty map space (or Escape) closes the stop card and flies back to the overview. A drag still turns the map. `python -I tools/tap_test.py BASE_URL` checks it in Chromium and WebKit.
