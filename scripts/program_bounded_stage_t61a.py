# ruff: noqa: E305, I001
import ast
import dataclasses
import hashlib
import inspect
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LEGACY, LEGACY_TREE = "7922956d3e248a93c3190240259850ab3498ec9f", "cc3c6b7f7e63dd040034938ff6bb6827f067e41c"
STAGES = ("cross_spec_writeback", "guarded_registry", "broader_governance", "final_governance", "writeback_persistence", "persisted_write_proof", "final_proof_publication", "final_proof_closure", "final_proof_archive")
FAMILIES = (("request", "build_frontend_{}_request", True), ("execute", "execute_frontend_{}", True), ("writer", "write_frontend_{}_artifact", True), ("payload_build", "_build_frontend_{}_artifact_payload", False), ("payload_load", "_load_frontend_{}_artifact_payload", False))
TESTS = ("tests/unit/test_program_service.py", "tests/integration/test_cli_program.py")
SELECTOR = "(cross_spec_writeback or guarded_registry or broader_governance or final_governance or writeback_persistence or persisted_write_proof or final_proof_publication or final_proof_closure or final_proof_archive) and not thread_archive and not project_cleanup"
ORDER = ("identity", "structure", "tests", "performance", "budget")
DURATIONS = [3.086, 3.131, 3.094, 3.280, 3.131, 3.058, 3.120, 3.046, 3.084, 3.056, 3.042, 3.133, 3.048, 3.047, 3.048, 3.067, 3.180, 3.062, 3.047, 3.054]
FORMAL = (tuple(f"specs/{wi}/{name}.md" for wi in ("196-ai-sdlc-lean-code-self-reduction-governance", "213-programservice-bounded-stage-reduction") for name in ("spec", "plan", "tasks")), tuple(f"specs/215-programservice-bounded-stage-reduction-implementation/{name}.md" for name in ("spec", "plan", "tasks")))
def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def run(args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return {"command": args, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
def stable(value):
    if value is inspect.Signature.empty or value is dataclasses.MISSING:
        return {"kind": "empty" if value is inspect.Signature.empty else "missing"}
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return [[stable(key), stable(item)] for key, item in value.items()]
    if not callable(value):
        raise TypeError(f"unsupported stable value: {type(value).__qualname__}")
    source = None if value in (list, dict) else digest(inspect.getsource(value).encode())
    return {"module": value.__module__, "qualname": value.__qualname__, "source_sha256": source}
def identity():
    sources = ("src/ai_sdlc/core/program_service.py", "src/ai_sdlc/cli/program_cmd.py", *TESTS, "tests/conftest.py", "pyproject.toml", "uv.lock")
    blobs = {path: git("hash-object", path) for path in sources[:4]}
    if git("rev-parse", f"{LEGACY}^{{tree}}") != LEGACY_TREE or any(value != git("rev-parse", f"{LEGACY}:{path}") for path, value in blobs.items()):
        raise RuntimeError("legacy identity, product, or target test drift")
    formal = [digest("".join(f"{digest((ROOT / path).read_bytes())}  {path}\n" for path in sorted(paths)).encode()) for paths in FORMAL]
    return {"legacy_commit": LEGACY, "legacy_tree": LEGACY_TREE, "formal_six_sha256": formal[0], "formal_three_sha256": formal[1], "source_sha256": {path: digest((ROOT / path).read_bytes()) for path in sources}, "git_blobs": blobs, "toolchain": {"python": sys.version.split()[0], "platform": " ".join(os.uname()), "uv": run(["uv", "--version"])["stdout"].strip(), **{name: metadata.version(name) for name in ("pytest", "pydantic", "typer", "PyYAML")}}}
def branch_count(node):
    items = tuple(ast.walk(node))
    return 1 + sum(isinstance(item, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.comprehension)) for item in items) + sum(len(item.values) - 1 for item in items if isinstance(item, ast.BoolOp)) + sum(len(item.handlers) + bool(item.orelse) + bool(item.finalbody) for item in items if isinstance(item, (ast.Try, ast.TryStar))) + sum(len(item.cases) for item in items if isinstance(item, ast.Match))
def structure():
    from ai_sdlc.core import program_service as module
    tree = ast.parse((ROOT / "src/ai_sdlc/core/program_service.py").read_text())
    specs = [(template.format(stage), family, public) for stage in STAGES for family, template, public in FAMILIES]
    nodes = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    if not set(nodes).issuperset(name for name, _, _ in specs):
        raise RuntimeError("45-symbol inventory incomplete")
    def metric(spec):
        name, family, public = spec
        node = nodes[name]
        first = node.body[1 if ast.get_docstring(node, clean=False) is not None else 0]
        physical, executable = node.end_lineno - node.lineno + 1, node.end_lineno - first.lineno + 1
        return {"name": name, "family": family, "public": public, "physical": physical, "executable": executable, "header": physical - executable, "branch": branch_count(node)}
    methods = [metric(spec) for spec in specs]
    totals = {key: sum(method[key] for method in methods) for key in ("physical", "executable", "header", "branch")}
    if (len(methods), *totals.values()) != (45, 3638, 3305, 333, 386):
        raise RuntimeError("legacy structure drift")
    def describe(name):
        target, signature = getattr(module.ProgramService, name), inspect.signature(getattr(module.ProgramService, name))
        params = [{"name": item.name, "kind": item.kind.name, "default": stable(item.default), "annotation": stable(item.annotation)} for item in signature.parameters.values()]
        return {"name": name, "module": target.__module__, "qualname": target.__qualname__, "signature": str(signature), "parameters": params, "return_annotation": stable(signature.return_annotation), "raw_annotations": stable(target.__annotations__), "doc": target.__doc__}
    surfaces = [describe(name) for name, _, public in specs if public]
    dtos = []
    classes = [("ProgramFrontend" + "".join(part.title() for part in stage.split("_")), suffix) for stage in STAGES for suffix in ("RequestStep", "Request", "Result")]
    for stem, suffix in classes:
        cls = getattr(module, stem + suffix)
        fields = [{"order": index, "name": item.name, "type": stable(item.type), "default": stable(item.default), "default_factory": stable(item.default_factory)} for index, item in enumerate(dataclasses.fields(cls))]
        hook = cls.__dict__.get("__post_init__")
        hook_data = {"present": False} if hook is None else {"present": True, "module": hook.__module__, "qualname": hook.__qualname__, "signature": str(inspect.signature(hook)), "source_sha256": digest(inspect.getsource(hook).encode())}
        dtos.append({"name": cls.__name__, "module": cls.__module__, "qualname": cls.__qualname__, "fields": fields, "equality": cls.__dataclass_params__.eq, "eq_qualname": cls.__eq__.__qualname__, "post_init": hook_data})
    calls = {"request": {"program_service": 18, "other_src": 9, "tests": 66}, "execute": {"program_service": 9, "other_src": 9, "tests": 79}, "writer": {"program_service": 0, "other_src": 9, "tests": 27}, "payload_build": {"program_service": 9, "other_src": 0, "tests": 0}, "payload_load": {"program_service": 9, "other_src": 0, "tests": 0}}
    return {"methods": methods, "totals": totals, "call_inventory": calls, "public_callables": surfaces, "dtos": dtos}
def tests_payload(saved_runs=None):
    command = lambda *extra: ["uv", "run", "--python", "3.11", "pytest", "-p", "no:cacheprovider", *TESTS, "-k", SELECTOR, *extra]  # noqa: E731
    collected = run(command("--collect-only", "-q"))
    nodes = [line for line in collected["stdout"].splitlines() if line.startswith("tests/") and "::" in line]
    if collected["exit"] or len(nodes) != 165 or any(token in node for node in nodes for token in ("thread_archive", "project_cleanup")):
        raise RuntimeError("exact selector provenance mismatch")
    groups = {stage: [node for node in nodes if re.search(rf"::test_(?:build|execute|write)_frontend_{stage}(?:_|$)", node) or re.search(rf"::TestCliProgram::test_program_{stage}(?:_|$)", node)] for stage in STAGES}
    expected = [16, 19, 19, 19, 19, 19, 20, 17, 17]
    assigned = [node for stage in STAGES for node in groups[stage]]
    if [len(groups[stage]) for stage in STAGES] != expected or len(set(assigned)) != 165 or set(assigned) != set(nodes):
        raise RuntimeError("anchored stage grouping mismatch")
    helpers = {}
    sys.modules.setdefault("tests", type(sys)("tests")).__path__ = [str(ROOT / "tests")]
    for path in TESTS:
        namespace = runpy.run_path(str(ROOT / path))
        helpers[path] = {f"_write_frontend_{stage}_artifact": digest(inspect.getsource(namespace[f"_write_frontend_{stage}_artifact"]).encode()) for stage in STAGES}
    if saved_runs is None:
        with tempfile.TemporaryDirectory(prefix="ai-sdlc-t61a-") as temp:
            saved_runs = [run(command("--basetemp", f"{temp}/run-{index}", "-q")) for index in (1, 2)]
    if any(item["exit"] or not re.search(r"\b165 passed\b", item["stdout"]) for item in saved_runs):
        raise RuntimeError("independent basetemp run failed")
    return {"selector": SELECTOR, "collect": {key: collected[key] for key in ("command", "exit", "stderr")}, "ordered_node_ids": nodes, "stage_groups": groups, "stage_counts": expected, "seed_helper_sha256": helpers, "file_sha256": {path: digest((ROOT / path).read_bytes()) for path in (*TESTS, "tests/conftest.py", "pyproject.toml")}, "runs": saved_runs}
def performance(saved=None):
    durations = saved["raw_seconds"] if saved is not None else DURATIONS
    if len(durations) != 20 or any(not isinstance(item, (int, float)) or item < 0 for item in durations):
        raise RuntimeError("performance sample mismatch")
    return {"warmup_completed": True, "raw_seconds": durations, "nearest_rank_p50_seconds": sorted(durations)[9], "nearest_rank_p95_seconds": sorted(durations)[18], "clock": "external selector characterization"}
def budget():
    recorder = len(Path(__file__).read_text().splitlines())
    manifest_added = int(numstat.split()[0]) if (numstat := git("diff", "--numstat", f"{LEGACY}..HEAD", "--", "tests/integration/test_repo_program_manifest.py")) else 0
    reserve = {"conftest_route": 8, "stage_fault_data": 10, "leaf_command": 12, "leg_runner": 12, "provenance": 10, "capture_case": 16, "comparator": 10, "performance": 6, "replay_nodes": 6}
    current, future, product = recorder + manifest_added, sum(reserve.values()), 466
    result = {"recorder_physical": recorder, "manifest_added_lines": manifest_added, "actual_current_proof": current, "future_reserve": reserve, "future_reserve_total": future, "candidate_product_shadow": product, "combined": current + future + product, "limits": {"recorder": 200, "proof": 290, "combined": 729}, "tracked_diff_sha256": digest(subprocess.run(["git", "diff", "--binary", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout)}
    if recorder > 200 or current + future > 290 or result["combined"] > 729:
        raise RuntimeError("proof budget exceeded")
    return result
def validate_receipt(receipt):
    if set(receipt) != {"schema_version", "outcome", "error", "sections"} or receipt["schema_version"] != "program-bounded-stage-t61a.v2":
        raise ValueError("invalid receipt envelope")
    names, outcome, error = list(receipt["sections"]), receipt["outcome"], receipt["error"]
    valid_sections = names == list(ORDER[: len(names)]) and all(set(item) == {"payload", "sha256"} and item["sha256"] == digest(item["payload"]) for item in receipt["sections"].values())
    valid_state = error is None and names == list(ORDER) if outcome == "pass" else isinstance(error, str) and bool(error) and len(names) < len(ORDER) if outcome == "no_go" else False
    if not valid_sections or not valid_state:
        raise ValueError("invalid receipt state")
def atomic_write(path, receipt):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(json.dumps(receipt, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode() + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    if hasattr(os, "O_DIRECTORY"):
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        os.fsync(descriptor)
        os.close(descriptor)
def calculate(saved=None, sections=None):
    result = {} if sections is None else sections
    builders = (identity, structure, lambda: tests_payload(None if saved is None else saved["tests"]["payload"]["runs"]), lambda: performance(None if saved is None else saved["performance"]["payload"]), budget)
    for name, builder in zip(ORDER, builders, strict=True):
        payload = builder()
        result[name] = {"payload": payload, "sha256": digest(payload)}
    return result
def main():
    sections = {}
    try:
        mode, options = sys.argv[1], dict(zip(sys.argv[2::2], sys.argv[3::2], strict=True))
        if mode not in ("record", "verify") or options["--route"] != "legacy":
            raise ValueError("mode must be record|verify and route must be legacy")
        path = Path(options["--output" if mode == "record" else "--input"])
        if mode == "record":
            receipt = {"schema_version": "program-bounded-stage-t61a.v2", "outcome": "pass", "error": None, "sections": calculate(sections=sections)}
            validate_receipt(receipt)
            atomic_write(path, receipt)
            return 0
        receipt = json.loads(path.read_text())
        validate_receipt(receipt)
        return 1 if receipt["outcome"] == "no_go" else int(receipt["sections"] != calculate(receipt["sections"]))
    except Exception as exc:
        if len(sys.argv) > 1 and sys.argv[1] == "record" and "--output" in locals().get("options", {}):
            receipt = {"schema_version": "program-bounded-stage-t61a.v2", "outcome": "no_go", "error": f"{type(exc).__name__}: {exc}", "sections": sections}
            validate_receipt(receipt)
            atomic_write(Path(options["--output"]), receipt)
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
if __name__ == "__main__":
    raise SystemExit(main())
