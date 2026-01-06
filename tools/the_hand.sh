#!/bin/sh
set -eu

say(){ printf "%s\n" "$*"; }
die(){ say "✋ The Hand: $*"; exit 1; }

# mascots
lain(){ say "🖤 lain-tan: $*"; }
bosu(){ say "⚡ bosu lazer-chan: $*"; }
peppy(){ say "🧠 peppy-senpai: $*"; }

need_repo(){
  git rev-parse --show-toplevel >/dev/null 2>&1 || die "not in a git repo. cd into ~/osu_megamix"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  help)
    say "✋ The Hand — room-service for the build"
    say ""
    say "Commands:"
    say "  the_hand status           # repo + freeze + mascots"
    say "  the_hand lain             # ensure lain-tan skin scaffold exists"
    say "  the_hand run-ultra        # run cat_ultra with Builder Mode"
    say "  the_hand share            # 'Send this build to your friends!'"
    say ""
    ;;

  status)
    need_repo
    say "✋ The Hand: status"
    say "Repo: $(git rev-parse --show-toplevel)"
    if git tag --list | grep -q '^jit-2\.2\.2\.2\.2\.2\.2\.2\.2$'; then
      peppy "JIT freeze detected: 2.2.2.2.2.2.2.2.2"
    else
      peppy "No JIT freeze tag found (optional)."
    fi
    lain "skins/lain-tan is where I live."
    bosu "BOSU is the reroute state (bust-to-osu) — audio timeline stays Megamix."
    ;;

  lain)
    need_repo
    mkdir -p skins/lain-tan
    [ -f skins/lain-tan/manifest.json ] || cat > skins/lain-tan/manifest.json <<'JSON'
{ "name":"lain-tan","ui":"ui.html","style":"ui.css","script":"ui.js" }
JSON

    [ -f skins/lain-tan/ui.html ] || cat > skins/lain-tan/ui.html <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="ui.css"></head>
<body id="lain"><div id="root"></div><script src="ui.js"></script></body></html>
HTML

    [ -f skins/lain-tan/ui.css ] || cat > skins/lain-tan/ui.css <<'CSS'
body#lain{background:#000;color:#9cf;font-family:monospace}
CSS

    [ -f skins/lain-tan/ui.js ] || cat > skins/lain-tan/ui.js <<'JS'
window.LAIN=true; document.getElementById('root').textContent='lain online';
JS

    lain "skin scaffold ready: skins/lain-tan/"
    say "Next: wire your HTML UI loader to accept drag-and-drop and point it at this manifest."
    ;;

  run-ultra)
    need_repo
    [ -x tools/builder_on.sh ] || die "tools/builder_on.sh missing (Builder Mode wrapper)"
    [ -x ultra/build/cat_ultra ] || die "ultra/build/cat_ultra missing — build ultra first"
    bosu "running cat_ultra in Builder Mode"
    exec ./tools/builder_on.sh ./ultra/build/cat_ultra
    ;;

  upkeep)
    need_repo
    say "✋ The Hand: upkeep (observe-only)"
    say ""

    lain "checking skins/"
    [ -d skins ] || mkdir -p skins
    [ -d skins/lain-tan ] && lain "lain-tan present" || lain "lain-tan missing (ok)"

    bosu "checking ultra/"
    if [ -d ultra ] && [ -f ultra/CMakeLists.txt ]; then
      peppy "ultra present"
      if [ -x ultra/build/cat_ultra ]; then
        peppy "ultra/build/cat_ultra present"
      else
        peppy "ultra/build/cat_ultra missing (build when ready)"
      fi
    else
      peppy "ultra missing (skipping)"
    fi

    peppy "freeze tag:"
    if git tag --list | grep -q '^jit-2\.2\.2\.2\.2\.2\.2\.2\.2$'; then
      say "  jit-2.2.2.2.2.2.2.2.2 ✓"
    else
      say "  (none)"
    fi

    say ""
    say "✓ upkeep pass complete"
    ;;
  share)
    need_repo
    say "📦 Send this build to your friends!"
    say ""
    say "Option A (easy):"
    say "  zip -r osu_megamix.zip osu_megamix"
    say ""
    say "Option B (developer):"
    say "  send them this commit:"
    say "  $(git rev-parse --short HEAD)"
    say ""
    say "Option C (skin):"
    say "  share skins/lain-tan/ as a folder"
    ;;

  *)
    die "unknown command '$cmd' (try: the_hand help)"
    ;;
esac
