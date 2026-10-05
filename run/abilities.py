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


def generate_ability(name, condition, conditions, inputs, mode="osu!"):
    hitobject = HitObject(conditions, inputs)

    without = hitobject.hit()
    with_ability = hitobject.hit({condition})

    if without or not with_ability:
        raise ValueError(
            f"{name} failed balance test: "
            f"without={without}, with={with_ability}"
        )

    return {
        "name": name,
        "mode": mode,
        "bypass": condition,
    }
