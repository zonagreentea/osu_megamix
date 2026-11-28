"""Discover osu!megamix chapters from Git history."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


CHAPTERS: tuple[tuple[str, str, str, str], ...] = (
    ("1a", "visual", "1a-visual", "access gift, premades, love, and the original vision"),
    ("1b", "Kintoki", "1b-ball", "collab art, skill, and composition"),
    ("1c", "pet", "1c-pet", "fun time, creativity, and care"),
    ("1d", "tease", "1d-tease", "meta awareness, reliability, and kindness"),
    ("1e", "gromp", "1e-gromp", "referential status, morality, and virtue"),
    ("1f", "final", "1f-final", "fuss: full integrity, status, and respect"),
    ("2a", "true love", "2a-true-love", "true love chapter"),
    ("2b", "remembrance", "2b-remembrance", "final Remembrance Day splash page push"),
    ("2c", "play", "2c-play", "experiments to add bust-to-mix"),
    ("2d", "reverse", "2d-reverse", "transition from boss battles to the ARG"),
)


@dataclass(frozen=True)
class Chapter:
    code: str
    name: str
    tag: str
    title: str
    description: str
    commit: str | None


class ChapterHistory:
    """Point the game at chapter commits in a local GitHub checkout."""

    def __init__(self, repository: str | Path = ".", remote: str = "origin") -> None:
        self.repository = Path(repository).resolve()
        self.remote = remote

    def _git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def remote_url(self) -> str:
        return self._git("remote", "get-url", self.remote)

    def fetch(self) -> None:
        """Refresh chapter history from GitHub without changing the checkout."""
        subprocess.run(
            ["git", "-C", str(self.repository), "fetch", self.remote, "--tags"],
            check=True,
        )

    def chapters(self) -> tuple[Chapter, ...]:
        commits = {
            code: self._find_commit(code, name, tag)
            for code, name, tag, _ in CHAPTERS
        }
        return tuple(
            Chapter(code, name, tag, f"osu!megamix {code} - {name}", description, commits[code])
            for code, name, tag, description in CHAPTERS
        )

    def _find_commit(self, code: str, name: str, tag: str) -> str | None:
        tag_result = subprocess.run(
            [
                "git", "-C", str(self.repository), "rev-list", "-n", "1", tag,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if tag_result.returncode == 0 and tag_result.stdout.strip():
            return tag_result.stdout.strip()

        needles = (f"osu!megamix {code} - {name}", f"{code} - {name}", tag, code)
        for needle in needles:
            result = subprocess.run(
                [
                    "git", "-C", str(self.repository), "log", "--all",
                    "--format=%H", "--fixed-strings", "--grep", needle,
                    "-n", "1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                return result.stdout.strip().splitlines()[0]
        return None

    def checkout(self, chapter: str) -> Chapter:
        """Check out a known chapter commit by code, such as ``2d``."""
        selected = next((item for item in self.chapters() if item.code == chapter), None)
        if selected is None or selected.commit is None:
            raise ValueError(f"Chapter has no Git commit: {chapter}")
        self._git("checkout", selected.commit)
        return selected
