# Assets

Policy:
- Ship only original assets created for osu!megamix (no lazer art/audio in repo).
- Support user-provided external skin folders (optional) via an adapter/mapping layer.

Asset Contract (v0):
Required:
- hitcircle (image)
- approachcircle (image)
- cursor (image)
- hitsound-normal (audio)

Optional:
- sliders (images/audio)
- UI panels/buttons
- fonts/colors via metadata

Loading rules:
- Prefer external skin folder if configured
- Fall back to assets/default
