# osu!megamix (web)

> no ball. python-powered. browser-hosted.

This is a **quiet, minimal web version of osu!megamix**.
It runs in a browser, is hosted for free on GitHub Pages, and can optionally be backed by Python later.

No launcher. No installer. Click → play.

---

## What this is

- A browser-based osu!-style prototype
- Zero dependencies for players
- Designed to stay **downlow**
- Extensible into full osu!megamix continuity later

Right now:
- Circles spawn
- You click them
- Score goes up

That’s enough. It breathes.

---

## Hosting (free, GitHub Pages)

This repo is meant to be hosted directly by GitHub.

### Folder layout

```
/
├── index.html
├── README.md
```

GitHub Pages serves `index.html` automatically.

---

## Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Source: `Deploy from a branch`
3. Branch: `main`
4. Folder: `/ (root)`
5. Save

After ~1 minute, your site is live at:

```
https://<username>.github.io/<repo-name>/
```

This is your **free, real, HTTPS website**.

---

## Local preview (optional)

You can run it locally with Python if you want:

```zsh
python3 -m http.server 8000
```

Then open:

```
http://localhost:8000
```

Same site. Same game.

---

## Subtle zsh flex

Print a clickable link in terminal:

```zsh
print -Pn '\e]8;;https://<username>.github.io/<repo-name>/\aosu!megamix\e]8;;\a\n'
```

Terminal → click → browser → game.

---

## Philosophy

- no ball, no rules
- continuity over completion
- fun > correctness
- if it runs, it exists

This is not a finished product.
It’s a **living link**.

---

## Next (optional, not required)

- Audio sync
- Mode switching (osu / taiko / mania)
- Megamix continuity timer
- Bust-to-mix logic
- Python backend (FastAPI) for scores

None of this is urgent.

Let it live first.

