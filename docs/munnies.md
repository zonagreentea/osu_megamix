# munnies (Ball Economy)

## Status
**Hard invariant — locked**

## Definition
munnies are a temporary, non-transferable economic pressure used only during a defined window.
They exist only inside osu!megamix and cannot be traded, exported, or persisted as value.

## Smart Car Override (Authoritative)
**If *Smart Car* is purchased, munnies are no longer required for victory.**

Hard consequences:
- `smart_car_purchased == true` => `munnies_required == false`
- `smart_car_purchased == true` => `munnies_expected = 0`
- `smart_car_purchased` is sticky and must never reset

## Red-Charizard Rule
If the game reports "munnies expected" after Smart Car purchase, the system is broken.
