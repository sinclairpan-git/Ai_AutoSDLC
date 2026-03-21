"""API scanner — detect API endpoints/routes in source files."""

from __future__ import annotations

import re
from pathlib import Path

from ai_sdlc.models.scanner import ApiEndpoint, FileInfo

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

PYTHON_ROUTE_PATTERNS = [
    # FastAPI: @app.get("/path") or @router.get("/path")
    re.compile(
        r"@\w+\.(?P<method>"
        + "|".join(HTTP_METHODS)
        + r")\s*\(\s*['\"](?P<path>[^'\"]+)['\"]"
    ),
    # Flask: @app.route("/path", methods=["GET"])
    re.compile(
        r"@\w+\.route\s*\(\s*['\"](?P<path>[^'\"]+)['\"]"
        r"(?:.*?methods\s*=\s*\[(?P<method>[^\]]+)\])?"
    ),
]

JS_ROUTE_PATTERNS = [
    # Express: router.get("/path", handler) or app.post("/path", handler)
    re.compile(
        r"\w+\.(?P<method>"
        + "|".join(HTTP_METHODS)
        + r")\s*\(\s*['\"`](?P<path>[^'\"`]+)['\"`]"
    ),
]


def scan_apis(root: Path, files: list[FileInfo]) -> list[ApiEndpoint]:
    """Scan source files for API route declarations."""
    endpoints: list[ApiEndpoint] = []

    for fi in files:
        if fi.category != "source":
            continue
        path = root / fi.path
        if fi.language == "python":
            endpoints.extend(_scan_python_routes(path, fi.path))
        elif fi.language in ("javascript", "typescript"):
            endpoints.extend(_scan_js_routes(path, fi.path))

    return endpoints


def _scan_python_routes(path: Path, rel_path: str) -> list[ApiEndpoint]:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    endpoints: list[ApiEndpoint] = []
    lines = source.splitlines()

    for i, line in enumerate(lines, 1):
        for pattern in PYTHON_ROUTE_PATTERNS:
            m = pattern.search(line)
            if m:
                method_raw = (
                    m.group("method") if "method" in pattern.groupindex else "GET"
                )
                if method_raw and method_raw not in HTTP_METHODS:
                    methods = [
                        m2.strip().strip("'\"").upper() for m2 in method_raw.split(",")
                    ]
                    method_raw = methods[0] if methods else "GET"
                handler = ""
                if i < len(lines):
                    next_line = lines[i].strip()
                    func_match = re.match(r"(?:async\s+)?def\s+(\w+)", next_line)
                    if func_match:
                        handler = func_match.group(1)
                endpoints.append(
                    ApiEndpoint(
                        method=method_raw.upper() if method_raw else "GET",
                        path=m.group("path"),
                        handler=handler,
                        source_file=rel_path,
                        line_number=i,
                        framework="fastapi"
                        if "@" in line and "route" not in line.lower()
                        else "flask",
                    )
                )
    return endpoints


def _scan_js_routes(path: Path, rel_path: str) -> list[ApiEndpoint]:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    endpoints: list[ApiEndpoint] = []
    for i, line in enumerate(source.splitlines(), 1):
        for pattern in JS_ROUTE_PATTERNS:
            m = pattern.search(line)
            if m:
                endpoints.append(
                    ApiEndpoint(
                        method=m.group("method").upper(),
                        path=m.group("path"),
                        source_file=rel_path,
                        line_number=i,
                        framework="express",
                    )
                )
    return endpoints
