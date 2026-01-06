# LAIN Skin System (drag-and-drop UI)

Goal: one drag-and-drop of a skin provides the entire UI.

Skin package:
- skin.json (manifest + mappings)
- assets/ui (images/css/layout)
- assets/fonts
- assets/sfx

Load order:
1) read skin.json
2) apply vars + theme css
3) load fonts
4) resolve images + layout
5) rerender UI root

No hard-coding: UI references must resolve through the skin asset map.
