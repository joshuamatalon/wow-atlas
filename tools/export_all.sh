#!/bin/sh
# Run the three client export steps for one dungeon subfolder, with wow.export already started hidden and load.js run.
# sh export_all.sh SUB      (logs land in work/SUB/*.out)
R=/c/Users/joshu/wow-atlas
SUB=$1
cd "$R"
mkdir -p "work/$SUB/export/creatures"
WE_MAX=200000 python -I tools/we.py tools/cmd/spells.js 900 "$(python -I tools/we_args.py $SUB spells)" > "work/$SUB/spells.out" 2>&1
echo "spells $?"
WE_MAX=200000 python -I tools/we.py tools/cmd/ex1.js 1500 "$(python -I tools/we_args.py $SUB ex1)" > "work/$SUB/ex1.out" 2>&1
echo "ex1 $?"
WE_MAX=400000 python -I tools/we.py tools/cmd/exchar3.js 2400 "$(python -I tools/we_args.py $SUB exchar3)" > "work/$SUB/exchar3.out" 2>&1
echo "exchar3 $?"
