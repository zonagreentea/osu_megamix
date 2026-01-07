#!/bin/sh
set -eu
BAND="${1:-ball}"
[ -f VERSION ] || printf "0.0.0\n" > VERSION
[ -f BUILD ]   || printf "0\n" > BUILD
BUILD=$(cat BUILD)
BUILD=$((BUILD + 1))
printf "%s\n" "$BUILD" > BUILD
printf "%s\n" "$BAND" > BAND
echo "band=$BAND version=$(cat VERSION) build=$BUILD"
