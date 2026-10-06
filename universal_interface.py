from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class Attachment:
    name: str
    capabilities: frozenset[str] = frozenset()
    metadata: dict[str, Any] = field(default_factory=dict)


PLAYER_COLOURS = (
    "red",
    "blue",
    "green",
    "yellow",
)


@dataclass(frozen=True)
class PlayerContext:
    player: int
    colour: str


def player_context(player: int, colour: str | None = None) -> PlayerContext:
    if player < 1:
        raise ValueError("player numbers start at 1")

    if colour is None:
        colour = PLAYER_COLOURS[(player - 1) % len(PLAYER_COLOURS)]

    return PlayerContext(player=player, colour=colour)


class UniversalInterface:
    """
    Hardware-agnostic attachment interface.

    Things attach by capability, never by hardware identity.
    The mech rises to whatever arrangement is attached.
    """

    def __init__(self) -> None:
        self._attachments: dict[str, Attachment] = {}
        self._inputs: list[str] = []
        self._outputs: list[str] = []
        self._views: list[str] = []

    def attach(
        self,
        name: str,
        *capabilities: str,
        metadata: dict[str, Any] | None = None,
    ) -> Attachment:
        attachment = Attachment(
            name=name,
            capabilities=frozenset(capabilities),
            metadata=dict(metadata or {}),
        )
        self._attachments[name] = attachment

        if "input" in attachment.capabilities and name not in self._inputs:
            self._inputs.append(name)

        if "output" in attachment.capabilities and name not in self._outputs:
            self._outputs.append(name)

        if "view" in attachment.capabilities and name not in self._views:
            self._views.append(name)

        return attachment

    def attach_player(
        self,
        player: int,
        *capabilities: str,
        colour: str | None = None,
        name: str | None = None,
    ) -> Attachment:
        context = player_context(player, colour)
        attachment_name = name or f"player-{player}"

        metadata = {
            "player": context.player,
            "colour": context.colour,
        }

        return self.attach(
            attachment_name,
            *capabilities,
            metadata=metadata,
        )

    def player_colour(self, player: int) -> str:
        attachment = self._attachments.get(f"player-{player}")
        if attachment is None:
            return player_context(player).colour
        return str(attachment.metadata["colour"])

    def detach(self, name: str) -> Attachment | None:
        attachment = self._attachments.pop(name, None)
        if attachment is None:
            return None

        for group in (self._inputs, self._outputs, self._views):
            if name in group:
                group.remove(name)

        return attachment

    def attached(self) -> tuple[Attachment, ...]:
        return tuple(self._attachments.values())

    def has(self, capability: str) -> bool:
        return any(
            capability in attachment.capabilities
            for attachment in self._attachments.values()
        )

    def sources(self, capability: str) -> tuple[Attachment, ...]:
        return tuple(
            attachment
            for attachment in self._attachments.values()
            if capability in attachment.capabilities
        )

    def inputs(self) -> tuple[Attachment, ...]:
        return self.sources("input")

    def outputs(self) -> tuple[Attachment, ...]:
        return self.sources("output")

    def views(self) -> tuple[Attachment, ...]:
        return self.sources("view")

    def route(self, capability: str, value: Any) -> list[tuple[str, Any]]:
        """
        Route a value to every attached thing providing the capability.
        The interface does not interpret the value.
        """
        return [
            (attachment.name, value)
            for attachment in self.sources(capability)
        ]

    def snapshot(self) -> dict[str, tuple[str, ...]]:
        return {
            "attachments": tuple(self._attachments),
            "inputs": tuple(self._inputs),
            "outputs": tuple(self._outputs),
            "views": tuple(self._views),
        }


class Mech:
    """The execution body that rises to the attached arrangement."""

    def __init__(self, interface: UniversalInterface | None = None) -> None:
        self.interface = interface or UniversalInterface()

    def attach(self, name: str, *capabilities: str, metadata=None) -> Attachment:
        return self.interface.attach(
            name,
            *capabilities,
            metadata=metadata,
        )

    def attach_player(
        self,
        player: int,
        *capabilities: str,
        colour: str | None = None,
        name: str | None = None,
    ) -> Attachment:
        context = player_context(player, colour)
        attachment_name = name or f"player-{player}"

        metadata = {
            "player": context.player,
            "colour": context.colour,
        }

        return self.attach(
            attachment_name,
            *capabilities,
            metadata=metadata,
        )

    def player_colour(self, player: int) -> str:
        attachment = self._attachments.get(f"player-{player}")
        if attachment is None:
            return player_context(player).colour
        return str(attachment.metadata["colour"])

    def detach(self, name: str) -> Attachment | None:
        return self.interface.detach(name)

    def arrange(self) -> dict[str, tuple[str, ...]]:
        return self.interface.snapshot()

    def rise(self, value: Any) -> dict[str, list[tuple[str, Any]]]:
        return {
            capability: self.interface.route(capability, value)
            for capability in ("input", "output", "view")
            if self.interface.has(capability)
        }


def test_single_player() -> None:
    mech = Mech()
    mech.attach("player", "input")
    mech.attach("screen", "view", "output")

    assert len(mech.interface.inputs()) == 1
    assert len(mech.interface.views()) == 1


def test_player_colours() -> None:
    mech = Mech()

    mech.interface.attach_player(1, "input")
    mech.interface.attach_player(2, "input")
    mech.interface.attach_player(3, "input")
    mech.interface.attach_player(4, "input")

    assert mech.interface.player_colour(1) == "red"
    assert mech.interface.player_colour(2) == "blue"
    assert mech.interface.player_colour(3) == "green"
    assert mech.interface.player_colour(4) == "yellow"

    mech.interface.detach("player-1")
    mech.interface.attach_player(1, "input", colour="purple")

    assert mech.interface.player_colour(1) == "purple"


def test_couch_coop() -> None:
    mech = Mech()
    mech.attach("player-1", "input")
    mech.attach("player-2", "input")
    mech.attach("screen", "view", "output")

    assert len(mech.interface.inputs()) == 2
    assert len(mech.interface.views()) == 1


def test_split_screen() -> None:
    mech = Mech()

    mech.attach("player-1", "input", "view")
    mech.attach("player-2", "input", "view")

    assert len(mech.interface.inputs()) == 2
    assert len(mech.interface.views()) == 2


def test_separate_monitors() -> None:
    mech = Mech()

    mech.attach("player-1", "input")
    mech.attach("player-2", "input")
    mech.attach("monitor-1", "view", "output")
    mech.attach("monitor-2", "view", "output")

    assert len(mech.interface.inputs()) == 2
    assert len(mech.interface.views()) == 2
    assert len(mech.interface.outputs()) == 2


def test_arbitrary_attachment() -> None:
    mech = Mech()

    mech.attach("tablet", "input", "view")
    mech.attach("keyboard", "input")
    mech.attach("microphone", "input")
    mech.attach("remote", "input", "output")
    mech.attach("file", "input")

    assert len(mech.interface.inputs()) == 5
    assert len(mech.interface.views()) == 1
    assert len(mech.interface.outputs()) == 1


def test_detach() -> None:
    mech = Mech()

    mech.attach("player-1", "input")
    mech.attach("player-2", "input")
    mech.detach("player-2")

    assert len(mech.interface.inputs()) == 1


if __name__ == "__main__":
    test_single_player()
    test_player_colours()
    test_couch_coop()
    test_split_screen()
    test_separate_monitors()
    test_arbitrary_attachment()
    test_detach()

    mech = Mech()
    mech.attach("player-1", "input", "view")
    mech.attach("player-2", "input", "view")
    mech.attach("monitor-1", "view", "output")
    mech.attach("monitor-2", "view", "output")

    print("universal interface: PASS")
    print(mech.arrange())
    print(mech.rise({"tick": 1}))
