class HitObject:
    def __init__(self, conditions, inputs):
        self.conditions = conditions
        self.inputs = inputs

    def hit(self, abilities=None):
        abilities = abilities or set()

        for condition, required in self.conditions.items():
            if self.inputs.get(condition) != required:
                if condition not in abilities:
                    return False

        return True


def test_ability():
    hitobject = HitObject(
        conditions={
            "timing": "perfect",
            "cursor": "target",
            "input": "tap",
        },
        inputs={
            "timing": "late",
            "cursor": "target",
            "input": "tap",
        },
    )

    without_ability = hitobject.hit()
    with_ability = hitobject.hit({"timing"})

    print("without ability:", "PASS" if without_ability else "FAIL")
    print("with ability:   ", "PASS" if with_ability else "FAIL")

    assert not without_ability
    assert with_ability


test_ability()
