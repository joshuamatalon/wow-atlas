#!/bin/sh
# Build, commit main, and push site/ to the gh-pages branch that GitHub Pages serves.
set -e
R=/c/Users/joshu/wow-atlas
sh "$R/tools/build.sh" > /dev/null
cd "$R"
git add -A
git -c user.name="joshuamatalon" -c user.email="joshuamatalon@gmail.com" commit -qm "${1:-Update atlas}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
git push -q origin main
git branch -D gh-pages > /dev/null 2>&1 || true
git subtree split --prefix site -b gh-pages > /dev/null
git push -qf origin gh-pages
gh api -X POST repos/joshuamatalon/wow-atlas/pages/builds --jq .status || true
