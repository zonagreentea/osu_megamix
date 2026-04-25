ø#!/bin/zsh

case "$1" in
  1a) echo "Building VISUAL layer..." ;;
  1b) echo "Building BALL layer..." ;;
  1c) echo "Building CAT layer..." ;;
  1d) echo "Building TEASE release..." ;;
  *) echo "usage: ./build.sh [1a|1b|1c|1d]" ;;
esac
