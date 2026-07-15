"""WI-204 program finalization legacy characterization gate."""

# ruff: noqa: E401, I001
import ast, hashlib, inspect, io, json, os, re, statistics, subprocess, tempfile, time
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rich.console import Console
from typer.main import get_command
from typer.testing import CliRunner

import ai_sdlc.cli.main as main_module
import ai_sdlc.cli.program_cmd as program_cmd
import ai_sdlc.core.program_service as program_service_module
from ai_sdlc.cli.main import app
from ai_sdlc.cli.program_cmd import program_app
from ai_sdlc.core.program_service import ProgramService
from ai_sdlc.routers.bootstrap import init_project
from tests.integration.test_cli_program import (
    _write_frontend_provider_patch_apply_artifact,
    _write_manifest,
)

REPO = Path(__file__).resolve().parents[2]
EVIDENCE, ACTIVATION = (REPO / ".ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate" / name for name in ("t61a-evidence.json", "sponsor-activation.yaml"))
SOURCE = REPO / "src/ai_sdlc/cli/program_cmd.py"
STAGES = (
    "cross-spec-writeback", "guarded-registry", "broader-governance", "final-governance", "writeback-persistence",
    "persisted-write-proof", "final-proof-publication", "final-proof-closure", "final-proof-archive",
)
ACTIVATION_COMMIT, ACTIVATION_SHA, LEGACY_SOURCE_SHA = "c78414b969bcb3eb4b2ac10fccc7da2e64059e64", "79d07b2d39af7e9a4f36252ca594a67fe7bec6eb363bc30b94378cdcba75c1be", "6a101662f01e11f3e6f9963860b0589a1dabd2ec604d82ad1cfc2d6636729bed"
ALLOWLIST = ["temporary-clone-absolute-root", "mapping-value-whose-exact-key-is-generated_at"]
RUNNER = CliRunner()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _normalize(raw: bytes, root: Path) -> bytes:
    raw = re.sub(rb"(?m)^(\s*generated_at:\s*).+$", rb"\1<generated_at>", raw.replace(os.fsencode(root), b"<TEMP_ROOT>"))
    return re.sub(rb'("generated_at"\s*:\s*)"(?:[^"\\]|\\.)*"', rb'\1"<generated_at>"', raw)


def _tree(root: Path) -> dict[str, list[object]]:
    rows: dict[str, list[object]] = {}
    for item in sorted(root.rglob("*")):
        if item.is_file():
            rows[item.relative_to(root).as_posix()] = [item.stat().st_mode & 0o777, len(raw := _normalize(item.read_bytes(), root)), _sha(raw)]
    return rows


def _record_gate(receipt: Path = ACTIVATION, source: Path = SOURCE) -> None:
    valid = receipt.is_file() and source.is_file() and _sha(receipt.read_bytes()) == ACTIVATION_SHA and _sha(source.read_bytes()) == LEGACY_SOURCE_SHA
    if not valid or subprocess.run(["git", "merge-base", "--is-ancestor", ACTIVATION_COMMIT, "origin/main"], cwd=REPO).returncode:
        raise RuntimeError("T61A record requires the exact active mainline legacy baseline")


def _seed(root: Path) -> str:
    with patch("ai_sdlc.routers.bootstrap.now_iso", return_value="2026-07-15T17:30:00+00:00"), patch("ai_sdlc.integrations.ide_adapter.now_iso", return_value="2026-07-15T17:30:00+00:00"):
        init_project(root)
    _write_manifest(root)
    old_spec, new_spec = root / "specs/001-auth", root / "specs/001-课程-é"
    old_spec.rename(new_spec)
    source = root / "program-manifest.yaml"
    manifest = root / "配置/程序清单.yaml"
    manifest.parent.mkdir()
    manifest.write_text(source.read_text().replace("specs/001-auth", "specs/001-课程-é"), encoding="utf-8")
    source.unlink()
    _write_frontend_provider_patch_apply_artifact(
        root, apply_result="applied", patch_apply_state="completed", remaining_blockers=[],
        steps=[{"spec_id": "001-auth", "path": "specs/001-课程-é", "patch_availability_state": "patches_generated", "pending_inputs": ["frontend_contract_observations"], "suggested_next_actions": ["materialize frontend contract observations"], "plain_language_blockers": ["frontend contract evidence is still missing"], "recommended_next_steps": ["materialize evidence"], "source_linkage": {}}],
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return "配置/程序清单.yaml"


def _wrap(events: list[str], label: str, original: object, fault: str = "", signal: type[BaseException] = KeyboardInterrupt) -> object:
    def call(*args: object, **kwargs: object) -> object:
        events.append(label)
        if label == fault:
            raise signal(label)
        return original(*args, **kwargs)  # type: ignore[operator]

    return call


def _chain(base: Path, *, ordered: bool = False) -> dict[str, object]:
    root = (base / "项目-é-測試").resolve()
    root.mkdir(parents=True)
    manifest = _seed(root)
    (sentinel := root.parent / "external-sentinel.bin").write_bytes(b"outside-unchanged\x00")
    results: dict[str, object] = {}
    events: list[str] = []
    with ExitStack() as stack:
        stack.enter_context(patch.object(program_cmd, "find_project_root", return_value=root))
        stack.enter_context(patch.object(program_service_module, "utc_now_z", return_value="2026-07-15T17:30:00Z"))
        if ordered:
            for stage in STAGES:
                key = stage.replace("-", "_")
                for label, owner, name in (("executor", ProgramService, f"execute_frontend_{key}"), ("writer", ProgramService, f"write_frontend_{key}_artifact"), ("renderer", program_cmd, f"_render_frontend_{key}_result")):
                    stack.enter_context(patch.object(owner, name, _wrap(events, f"{stage}:{label}", getattr(owner, name))))
            original_write = Path.write_text
            stack.enter_context(patch.object(Path, "write_text", lambda path, *a, **k: (events.append(f"{path.stem}:report") if "报告" in path.parts else None) or original_write(path, *a, **k)))
        for stage in STAGES:
            started = time.perf_counter_ns()
            result = RUNNER.invoke(program_app, [stage, "--manifest", manifest, "--execute", "--yes", "--report", f"报告/{stage}.md"])
            results[stage] = {"exit": result.exit_code, "stdout": [len(result.stdout_bytes), _sha(_normalize(result.stdout_bytes, root))], "stderr": [len(result.stderr_bytes), _sha(_normalize(result.stderr_bytes, root))], "ns": time.perf_counter_ns() - started}
            assert result.exit_code == 0, result.output
    stable_results = {stage: {k: v for k, v in row.items() if k != "ns"} for stage, row in results.items()}
    digest = _sha(json.dumps({"results": stable_results, "tree": _tree(root)}, sort_keys=True, ensure_ascii=False).encode())
    return {"root": root, "results": results, "digest": digest, "events": events, "sentinel": _sha(sentinel.read_bytes())}


def _fault(root: Path, stage: str, point: str, signal: type[BaseException]) -> tuple[object, list[str]]:
    key, events = stage.replace("-", "_"), []
    with ExitStack() as stack:
        stack.enter_context(patch.object(program_cmd, "find_project_root", return_value=root))
        for label, owner, name in (("executor", ProgramService, f"execute_frontend_{key}"), ("writer", ProgramService, f"write_frontend_{key}_artifact"), ("renderer", program_cmd, f"_render_frontend_{key}_result")):
            stack.enter_context(patch.object(owner, name, _wrap(events, f"{stage}:{label}", getattr(owner, name), f"{stage}:{point}", signal)))
        result = RUNNER.invoke(program_app, [stage, "--manifest", "配置/程序清单.yaml", "--execute", "--yes"])
    return result, events


def _renderers() -> dict[str, object]:
    values = SimpleNamespace(confirmed=True, written_paths=["specs/001-课程-é/结果.md"], remaining_blockers=["blocker"], warnings=["warning"], orchestration_result="completed", writeback_state="completed", orchestration_summaries=["重复", "[markup]", "x" * 120], registry_result="completed", registry_state="completed", registry_summaries=["重复"], governance_result="completed", governance_state="completed", governance_summaries=["重复"], final_governance_result="completed", final_governance_state="completed", final_governance_summaries=["重复"], persistence_result="completed", persistence_state="completed", persistence_summaries=["重复"], proof_result="completed", proof_state="completed", proof_summaries=["重复"], publication_result="completed", publication_state="completed", publication_summaries=["重复"], closure_result="completed", closure_state="completed", closure_summaries=["重复"], archive_result="completed", archive_state="completed", archive_summaries=["重复"])
    rows: dict[str, object] = {}
    for stage in STAGES:
        renderer = getattr(program_cmd, f"_render_frontend_{stage.replace('-', '_')}_result")
        item = {"source": _sha(inspect.getsource(renderer).encode()), "widths": {}}
        for width in (40, 80, 120):
            stream = io.StringIO()
            with patch.object(program_cmd, "console", Console(file=stream, width=width, color_system=None)):
                renderer(values)
            raw = stream.getvalue().encode()
            item["widths"][str(width)] = [len(raw), _sha(raw)]
        rows[stage] = item
    return rows


def _surface() -> dict[str, object]:
    helps = {}
    for stage in STAGES:
        result = RUNNER.invoke(program_app, [stage, "--help"])
        assert result.exit_code == 0 and "--json" not in result.output
        helps[stage] = [len(result.stdout_bytes), _sha(result.stdout_bytes)]
    return {"commands": len(get_command(program_app).commands) - 1, "targets": len(STAGES), "help": helps}


def _ledger() -> dict[str, int]:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    names = {f"program_{stage.replace('-', '_')}" for stage in STAGES}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    retained = sum(node.body[0].lineno - min([node.lineno, *[d.lineno for d in node.decorator_list]]) + 1 for node in nodes)
    return {"handlers": len(nodes), "loc": sum(node.end_lineno - min([node.lineno, *[d.lineno for d in node.decorator_list]]) + 1 for node in nodes if node.end_lineno), "retained": retained}


def runtime_baseline(samples: int = 30, warmup: int = 5) -> dict[str, object]:
    totals: list[int] = []
    for index in range(samples + warmup):
        with tempfile.TemporaryDirectory(prefix=f"wi204-{index}-") as temp:
            capture = _chain(Path(temp))
            if index >= warmup:
                totals.append(sum(row["ns"] for row in capture["results"].values()))
    quantiles = statistics.quantiles(totals, n=100, method="inclusive")
    return {"warmup": warmup, "samples": samples, "algorithm": "statistics.quantiles-inclusive", "p50_ns": int(statistics.median(totals)), "p95_ns": int(quantiles[94])}


def test_t61a_evidence_contract() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["state"] == "verified" and evidence["actual_protection_loc"] <= 180
    assert evidence["normalizer_allowlist"] == ALLOWLIST
    assert evidence["surface"] == _surface() and evidence["renderers"] == _renderers()
    ledger = _ledger()
    assert (ledger["handlers"], ledger["retained"]) == (evidence["legacy_ast"]["handlers"], evidence["legacy_ast"]["retained"])


def test_t61a_full_chain_order_and_raw_side_effects(tmp_path: Path) -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    capture = _chain(tmp_path, ordered=True)
    assert capture["digest"] == evidence["chain_digest"]
    assert capture["sentinel"] == _sha(b"outside-unchanged\x00")
    assert capture["events"] == [f"{stage}:{point}" for stage in STAGES for point in ("executor", "writer", "renderer", "report")]


def test_t61a_failure_interrupt_and_retry(tmp_path: Path) -> None:
    root = _chain(tmp_path)["root"]
    for stage in STAGES:
        for point, signal in (("executor", RuntimeError), ("writer", KeyboardInterrupt), ("renderer", SystemExit)):
            result, events = _fault(root, stage, point, signal)
            assert result.exit_code != 0 and events == [f"{stage}:{item}" for item in ("executor", "writer", "renderer")[: ("executor", "writer", "renderer").index(point) + 1]]
        assert _fault(root, stage, "", RuntimeError)[0].exit_code == 0


def test_t61a_record_gate_and_normalizer_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="exact active mainline"):
        _record_gate(tmp_path / "missing")
    raw = b"generated_at: now\nartifact_generated_at: keep\nwarning: keep 2026-01-01\n"
    assert _normalize(raw, tmp_path) == b"generated_at: <generated_at>\nartifact_generated_at: keep\nwarning: keep 2026-01-01\n"


def test_t61a_outer_hook_connects_update_adapter_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []
    monkeypatch.setattr(main_module, "maybe_render_update_notice", lambda: events.append("update"))
    monkeypatch.setattr(main_module, "run_ide_adapter_if_initialized", lambda **_: events.append("adapter"))
    monkeypatch.setattr(program_cmd, "ProgramService", lambda *_: events.append("handler") or (_ for _ in ()).throw(RuntimeError("stop")))
    result = RUNNER.invoke(app, ["program", STAGES[0]])
    assert isinstance(result.exception, RuntimeError) and events == ["update", "adapter", "handler"]
    events.clear()
    with patch.object(main_module.sys, "argv", ["ai-sdlc", "program", STAGES[0], "--help"]):
        assert RUNNER.invoke(app, ["program", STAGES[0], "--help"]).exit_code == 0 and events == ["adapter"]
