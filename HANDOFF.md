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

## The Deadmines: bestiary only (2026-11-22)
Live at https://joshuamatalon.github.io/wow-atlas/?d=deadmines. The switch in the header moves between the two dungeons
(`site/data/index.json` lists them). `site/data/deadmines.json` has no `map`, so the page opens on the grid and hides
the Map and Bosses tabs. Models and thumbnails sit in `dm/` subfolders, named by the file's `assets` field.

The build holds these parts.
- 25 creatures from the Wowhead Forever zone 1581 list, which has 28 rows; Target Dummy, Rat and Hawk are left out.
- Nine plain models from `tools/cmd/ex1.js`. Sixteen character models (humans, goblins, Mr. Smite) from
  `tools/cmd/exchar3.js`, which exports each one dressed: baked skin, the right geosets, the Defias mask, shoulders and
  Greenskin's hat. The mask and shoulders are bound to their attachment bones, so they follow every clip.
- Every ability line is worded from the live client's spell row (`work/dm/spells_live.json`, build 1.60.1.71037). Which
  spells a creature has comes from its Wowhead page, the rows above "Dazed"; the rows below it are same-name variants.
- `work/shots/compare_deadmines.png` lays all 25 beside Wowhead's renders. All 25 match in body and outfit.

Four faults in wow.export 0.2.21 that `exchar3.js` and `opt_dm.txt` work around:
1. A first preview never dresses the creature. The script unticks and reticks one gear slot to run the dressing code.
2. The right shoulder loads as a body-skinned model. The script binds it to attachment point 5.
3. A chest item with no skirt hides the skirt that the legs item carries (Defias Wizard). The script takes the larger.
4. The export keeps three things the game does not draw: the opaque eye overlay (`EyeGlowB1`), the goblin's emote rag
   (`Geoset1`) and Mr. Smite's default jewelry. `tools/opt_dm.txt` drops them.
Also: `modelsExportTextures` was off in the saved wow.export settings, and both export scripts now set it on.

Rebuild, with wow.export started hidden and `load.js` run as described above:
`python -I tools/wh_npcs.py work/dm/wh/roster_npcs.json work/dm/wh/npc`, `python -I tools/wh_abilities.py work/dm/wh/npc`,
`python -I tools/creature_jobs.py dm`, `we.py tools/cmd/ex1.js 600 ARGS`, `we.py tools/cmd/exchar3.js 1500 ARGS`,
`we.py tools/cmd/spells.js 900 ARGS` (each script's first lines name its ARGS), `sh tools/opt_all.sh dm`,
`python -I tools/make_deadmines.py`, `sh tools/build.sh`, `python -I tools/thumbs.py BASE_URL deadmines`,
`python -I tools/compare_sheet.py deadmines`, `python -I tools/check_copy.py deadmines`, then `sh tools/publish.sh`.

These items stay open for the Deadmines.
- No creature holds a weapon. The client has no table of what each NPC wields, and Wowhead's renders have none either.
- Cards hold the name, rank, level and abilities. They have no "where" or tank lines, because Josh asked for the
  bestiary alone.
- The boss order on the grid is the Classic order from memory. Nothing in the Forever data confirms it.
- `exchar3.js` should also repair the three Ruins character models in open item 1 above. It has not been run on them.

## Shadowfang Keep: bestiary only (2026-11-23)
Live at https://joshuamatalon.github.io/wow-atlas/?d=shadowfang. Josh typed "silvering keep"; no dungeon has that name,
and Shadowfang Keep was his next dungeon, so that is what was built. The build follows the Deadmines one in the work
subfolder `work/sfk` with assets in `sfk/`.

- 35 creatures from the Wowhead Forever zone 209 list, which has 41 rows. Six are left out: Black Rat, Hawk, Crimson
  Cannon and Arcane Elemental (no level on their rows), Arugal (npc 10000, the courtyard double of the Archmage) and
  Sever (the Scourge event boss in Classic; whether Forever spawns him is not known).
- 23 plain models from `ex1.js` and 12 character models from `exchar3.js`. `work/shots/compare_shadowfang.png` lays
  all 35 beside Wowhead's renders, and all 35 match in body and outfit.
- `tools/opt_sfk.txt` drops the Voidwalker's glow quads (they drew as black squares) and the Haunting Spirit's flare
  quads and two loose parts that sit behind the body, and it makes the spirit's skin alpha-tested for her hair.
- New helpers: `tools/export_all.sh SUB` runs the three client steps with ARGS from `tools/we_args.py`,
  `tools/live_dump.py SUB` prints each creature's rows above Dazed with the live spell facts, `tools/glb_bbox.py`
  finds a part that sits away from the body, and `tools/closeup.py` renders large views beside Wowhead's.

Rebuild: fetch the zone page with `pw_get.py`, `wh_listview.py PAGE npcs work/sfk/wh/zone_npcs.json`, write
`roster_npcs.json` without the six, then `wh_npcs.py`, `wh_abilities.py`, `creature_jobs.py sfk`, `sh tools/export_all.sh sfk`,
`sh tools/opt_all.sh sfk`, `python -I tools/make_shadowfang.py`, then build, thumbs, compare, check and publish as above.
Wowhead served a "confirm you are human" page for the last four NPC fetches; deleting those files and running
`wh_npcs.py` again fetched them.

Skull marks (2026-11-23, his ask): an enemy in a data file may carry `skull` (1 to 3) and `why` (one sentence). The
grid sorts the trash with the most skulls first and draws them on the tile, the card shows them above the abilities,
and `skullNote` is the caption under the Trash heading. A data file without those fields draws nothing, so the
Deadmines and the Ruins are unchanged. The Shadowfang tiers sit in `SKULLS` in `tools/make_shadowfang.py`, with the
rule in the comment above them. They are judged from the ability rows alone, because the pack make-up in Forever is
not known and he has not run the keep. Correct them from Scribe after his first run.

## Blackfathom Deeps: bestiary with skull marks (2026-11-23)
Live at https://joshuamatalon.github.io/wow-atlas/?d=blackfathom, built the same way in `work/bfd` with assets in `bfd/`.

- 33 creatures from the Wowhead Forever zone 719 list, which has 69 rows. 34 rows with ids above 200000 are left out:
  they are a second, raid-sized set (bosses at level 9999, Blackfathom Elite, Tide Priestess, totems, Phantasmal
  creatures). ForeverDB's file for dungeon 48 records Forever kills on the old ids (Ghamoo-ra 4887 and the rest), so
  the old set is the one in the game. Baron Aquanis (hostile to the Horde only) and Hawk are left out too.
- `tools/opt_bfd.txt` alpha-tests the naga and water elemental skins (their fin and splash cards drew black edges) and
  drops the Voidwalker Minion's glow quads.
- Mind Blast for Kelris comes from ForeverDB's boss list, not from Wowhead's rows; its facts are the live spell row in
  `work/bfd/spells_extra.json`. Twilight Shadowmage's Wowhead list holds player debuffs, so its card keeps Shadow Bolt
  and Summon Voidwalker by judgement. Aku'mai Fisher's only row is a pet skill, so its card has none.
- Skull tiers sit in `SKULLS` in `tools/make_blackfathom.py`, judged from ability rows as for Shadowfang.
- The water elementals lack the splash that Wowhead draws at their base.

The header switch now holds four dungeons. On a phone it takes at most 62 percent of the row, scrolls sideways, and
opens with the current dungeon in sight; the labels are Ruins, Deadmines, SFK and BFD (`short` in `index.json`).
A card with no ability rows prints "It only swings in melee." unless the data gives `plain`; Razorclaw the Butcher and
the friendly NPCs now carry their own `plain` lines.

These items stay open for Shadowfang Keep.
- The "rows above Dazed" rule failed on two pages. Archmage Arugal's list holds player debuffs (Faerie Fire, Hunter's
  Mark, Judgements), so his card keeps only Void Bolt, Arugal's Curse and Thundershock by judgement. Slavering Worg's
  list is the tameable wolf's pet skills, so its card has none.
- Razorclaw the Butcher, Shadow Charger, Gemela and Deathstalker Vincent have no ability rows on Wowhead Forever.
- The two prisoner lines (who opens the courtyard door for which side) come from Classic memory plus the client's
  `Ashcrombe's Unlock` spell row. Nothing in the Forever data confirms them.
- Arugal's shoulder spikes lack the green glow that Wowhead draws. No creature holds a weapon, as in the Deadmines.
- The boss order is ForeverDB's list for dungeon 33, with the rare Deathsworn Captain placed after Odo by judgement.
