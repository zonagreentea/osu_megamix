"""Explicit consent is required to portray any real person."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Consent:
    person: str
    scope: str
    explicit: bool
    revoked: bool = False


def authorize_portrayal(
    real_people: tuple[str, ...],
    scope: str,
    consents: tuple[Consent, ...] = (),
) -> bool:
    """Deny real-person portrayals unless every person explicitly consents."""
    if not real_people:
        return True

    if not scope or not scope.strip():
        return False

    for person in real_people:
        if not person or not person.strip():
            return False

        matching = [
            consent for consent in consents
            if consent.person == person
            and consent.scope == scope
            and consent.explicit
            and not consent.revoked
        ]

        if not matching:
            return False

    return True
