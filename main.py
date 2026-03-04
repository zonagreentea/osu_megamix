from osu_mix.rulesets.osu_ruleset import OsuRuleset
from osu_mix.rulesets.taiko_ruleset import TaikoRuleset
from osu_mix.rulesets.catch_ruleset import CatchRuleset
from osu_mix.rulesets.mania_ruleset import ManiaRuleset
from osu_mix.scoring import Score
from osu_mix.death_handler import trigger_death
import time

# choose modes
modes = [OsuRuleset(), TaikoRuleset(), CatchRuleset(), ManiaRuleset()]

score = Score()

for mode in modes:
    mode.start()
    # simulate some hits
    for i in range(5):
        score.hit()
        time.sleep(0.1)
    score.miss()
    if trigger_death(score):
        break

