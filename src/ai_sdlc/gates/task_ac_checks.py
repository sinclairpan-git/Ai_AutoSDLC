"""Task-level acceptance checks (FR-090 / SC-014).

Rules match ``DecomposeGate`` check ``task_acceptance_present``: each ``### Task`` block
must include 「验收标准」, a standalone ``AC`` token, or 「验证」.
"""

from __future__ import annotations

import re


def first_task_missing_acceptance(tasks_md: str) -> str | None:
    """Return the first Task id missing acceptance markers, else ``None``."""
    parts = re.split(r"(?m)^###\s+Task\s+", tasks_md)
    for part in parts[1:]:
        m = re.match(r"(?P<id>\d+\.\d+)", part.strip())
        task_id = m.group("id") if m else "unknown"
        block = part

        has_acceptance = (
            "验收标准" in block
            or re.search(r"(?m)\bAC\b", block) is not None
            or "验证" in block
        )
        if not has_acceptance:
            return task_id
    return None
