"""
imagination.py

Syntactic markers for an intensive interpreter dialect.

This module establishes a compact set of tokens that can be used to
annotate structured expressions, blocks, and directives for an
interpreter-oriented imaginative grammar.
"""

BEGIN = "⟪"
END = "⟫"
SEPARATOR = "::"
ASSIGN = "=>"
COMMENT = "#"
BLOCK = "BLOCK"
CLAUSE = "CLAUSE"
DIRECTIVE = "DIRECTIVE"


def marker(name: str, value: str = "") -> str:
    """Build a syntactic marker for a named component."""
    if value:
        return f"{BEGIN}{name}{SEPARATOR}{value}{END}"
    return f"{BEGIN}{name}{END}"


def parse_markers(tokens):
    """Wrap a token list with clause markers."""
    return [marker(CLAUSE, token) for token in tokens]


if __name__ == "__main__":
    sample = ["input", "transform", "output"]
    print(parse_markers(sample))
