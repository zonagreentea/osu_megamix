#!/bin/sh
set -eu
export OSU_MEGAMIX_BUILDER=1
echo "[builder] ON (OSU_MEGAMIX_BUILDER=1)"
exec "$@"
