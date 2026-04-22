import json
from pathlib import Path

_PATTERNS = None


def _load():
    global _PATTERNS
    if _PATTERNS is None:
        p = Path(__file__).parent.parent / "references" / "patterns.json"
        with open(p) as f:
            data = json.load(f)
        _PATTERNS = data.get("patterns", [])
    return _PATTERNS


def get_all_patterns() -> list[dict]:
    return _load()


def get_patterns_summary() -> str:
    """Return a compact text summary of all patterns for embedding in Claude prompts."""
    patterns = _load()
    lines = []
    for p in patterns:
        lines.append(
            f"- {p['id']}: {p['name']} | Criteria: {p['criteria']} | Mgmt: {p['management']}"
        )
    return "\n".join(lines)
