#!/bin/zsh

set -e

source="$1"

if [[ -z "$source" ]]; then
    print "usage: open.zsh <source>"
    exit 1
fi

if [[ "$source" == http://* || "$source" == https://* ]]; then
    curl -fsSL "$source"
elif [[ -f "$source" ]]; then
    cat "$source"
elif [[ -d "$source" ]]; then
    find "$source" -type f -print
else
    print -u2 "open.zsh: source not found: $source"
    exit 1
fi
