#!/usr/bin/env bash
# Rename the app brand across the site, e.g. if you change the OAuth consent
# screen's "App name" in Google Cloud.
#
#   ./tools/rename-brand.sh "Home Assistant" "Home Hariki"
#
# It rewrites page titles, the top bar, the hero heading and the logo alt text.
# Review `git diff` afterwards: the pages also mention Home Assistant as the
# open-source software they run, and those mentions should probably stay.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <old name> <new name>" >&2
  exit 2
fi

old=$1
new=$2
cd "$(dirname "$0")/.."

files=(index.html privacy.html terms.html)
sed -i "s|${old}|${new}|g" "${files[@]}"
echo "replaced '${old}' -> '${new}' in: ${files[*]}"
grep -c "$new" "${files[@]}" || true
