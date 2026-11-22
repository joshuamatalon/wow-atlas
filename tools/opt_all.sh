#!/bin/sh
# Slim every exported creature GLB of one dungeon for the web.
# sh opt_all.sh SUB   (SUB is the work subfolder and the asset folder, e.g. dm)
# Per-model extras live in tools/opt_SUB.txt, one line each: SLUG|flags for opt_creature.mjs. The slug * applies to all.
R=/c/Users/joshu/wow-atlas
SUB=$1
OUT=$R/site/models/creatures/$SUB
RULES=$R/tools/opt_$SUB.txt
mkdir -p "$OUT"
cp "$R/tools/opt_creature.mjs" "$R/work/node/opt_creature.mjs"   # node resolves packages from the script's own folder
cd "$R/work/node"
for f in "$R/work/$SUB/export"/*.glb "$R/work/$SUB/export/creatures"/*.glb; do
  [ -f "$f" ] || continue
  n=$(basename "$f"); slug=${n%.glb}
  extra=""
  if [ -f "$RULES" ]; then
    extra=$(grep -E "^(\*|$slug)\|" "$RULES" | cut -d'|' -f2- | tr '\n' ' ')
  fi
  node --max-old-space-size=6000 opt_creature.mjs "$f" "$OUT/$n" 512 $extra 2>&1 | tail -1
done
ls -la "$OUT"
