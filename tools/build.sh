#!/bin/sh
# Bundle app/ into site/. Node modules live in work/node (git-ignored).
set -e
R=/c/Users/joshu/wow-atlas
cd "$R/work/node"
NODE_PATH="$R/work/node/node_modules" ./node_modules/.bin/esbuild "$R/app/main.js" --bundle --format=esm --minify --outfile="$R/site/app.js" --log-level=warning
cp "$R/app/index.html" "$R/app/style.css" "$R/site/"
ls -la "$R/site/app.js"
