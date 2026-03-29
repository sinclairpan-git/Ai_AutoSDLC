# 003 release gate evidence

- release_gate_evidence: present
- PASS: supported
- WARN: supported
- BLOCK: supported

## Evidence Notes

- `recoverability`：聚焦 `resume-pack` rebuild / recover path 的读写与重建行为。
- `portability`：聚焦 `python -m ai_sdlc` 这类不依赖 PATH 的调用路径。
- `multi_ide`：聚焦状态面与 IDE 适配边界，不把特定 IDE 的行为写死成唯一路径。
- `stability`：聚焦 release 前最小测试集合和 lint 结果。

```json
{
  "release_gate_evidence": {
    "overall_verdict": "PASS",
    "checks": [
      {
        "name": "recoverability",
        "verdict": "PASS",
        "evidence_source": "uv run pytest tests/integration/test_cli_recover.py tests/unit/test_p1_artifacts.py -q",
        "reason": "resume-pack rebuild, artifact persistence, and recover flows are covered by focused regression tests"
      },
      {
        "name": "portability",
        "verdict": "PASS",
        "evidence_source": "uv run pytest tests/integration/test_cli_module_invocation.py -q",
        "reason": "module invocation path proves the CLI remains usable without relying on a PATH-installed entrypoint"
      },
      {
        "name": "multi_ide",
        "verdict": "PASS",
        "evidence_source": "uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_workitem_link.py -q",
        "reason": "status and linked work-item surfaces keep IDE-adaptation behavior bounded while exposing reviewer/release state"
      },
      {
        "name": "stability",
        "verdict": "PASS",
        "evidence_source": "uv run pytest -q && uv run ruff check src tests",
        "reason": "release candidate is gated on a clean focused regression set plus repository lint"
      }
    ]
  }
}
```
