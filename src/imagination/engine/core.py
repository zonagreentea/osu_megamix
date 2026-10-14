"""Imagination engine with synthetic real-world image generation disabled."""

BLOCKED_OPERATIONS = frozenset({
    "autography",
    "photorealistic_generation",
    "real_world_image_synthesis",
})


def authorize(operation: str) -> None:
    """Reject prohibited synthetic real-world image generation."""
    normalized = operation.strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in BLOCKED_OPERATIONS:
        raise PermissionError(
            "Autography is disabled in osu!megamix."
        )


def run():
    print("[imagination*] boot OK (autography disabled).")
