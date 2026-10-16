"""Privacy-first narrative portrayal policy."""


class PortrayalPolicyError(ValueError):
    pass


def validate_portrayal(content):
    """Reject real-life event portrayals and invalid classifications."""
    if not isinstance(content, dict):
        raise PortrayalPolicyError("Content metadata must be a dictionary.")

    event = content.get("real_life_event")

    if event is True:
        raise PortrayalPolicyError(
            "Real-life event portrayals are prohibited."
        )

    if event is not False:
        raise PortrayalPolicyError(
            "Explicit real-life-event classification is required."
        )

    classification = content.get("event_classification")

    if classification != "fictional":
        raise PortrayalPolicyError(
            "Character narratives must be explicitly fictional."
        )

    return True
