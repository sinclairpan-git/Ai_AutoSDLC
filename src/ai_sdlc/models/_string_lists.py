from __future__ import annotations


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique
