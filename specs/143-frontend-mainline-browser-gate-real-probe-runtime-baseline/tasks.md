---
related_doc:
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md"
  - "src/ai_sdlc/models/frontend_browser_gate.py"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "program-manifest.yaml"
---
# 任务分解：Frontend Mainline Browser Gate Real Probe Runtime Baseline

**编号**：`143-frontend-mainline-browser-gate-real-probe-runtime-baseline` | **日期**：2026-04-14
**来源**：plan.md + spec.md

## Batch 1：Red tests 与 runtime contract 冻结

### Task 1.1 锁定 real probe success / failure fixtures

- **任务编号**：T143-11
- **优先级**：P0
- **状态**：已完成
- **文件**：`tests/unit/test_frontend_browser_gate_runtime.py`, `tests/unit/test_program_service.py`, `tests/integration/test_cli_program.py`
- **验收标准**：
  1. shared trace / screenshot 成功时不再落成 placeholder `missing`
  2. runner launch/nav failure 时稳定映射为 `transient_run_failure`
  3. runner success 但 raw artifact 缺失时，Python 侧必须 fail-closed 为 `evidence_missing` 或 `blocked`
  4. current gate run artifact namespace 与 execute gate binding 被红灯锁定

## Batch 2：Real probe runtime

### Task 2.1 引入 bounded runner contract 与真实 artifact materialization

- **任务编号**：T143-21
- **优先级**：P0
- **状态**：已完成
- **文件**：`src/ai_sdlc/models/frontend_browser_gate.py`, `src/ai_sdlc/core/frontend_browser_gate_runtime.py`, `scripts/frontend_browser_gate_probe_runner.mjs`
- **验收标准**：
  1. default runner stdout JSON contract 固定，raw artifact layout 固定在当前 artifact root 下
  2. `playwright_smoke` 能写出真实 trace / navigation screenshot 或真实 `capture_failed`
  3. `interaction_anti_pattern_checks` 能执行一次 bounded real interaction probe
  4. bundle 只引用当前 `gate_run_id` artifacts

### Task 2.2 接入 ProgramService / gate decision

- **任务编号**：T143-22
- **优先级**：P0
- **状态**：已完成
- **文件**：`src/ai_sdlc/core/frontend_gate_verification.py`, `src/ai_sdlc/core/program_service.py`, `tests/unit/test_program_service.py`
- **验收标准**：
  1. real probe `pass / evidence_missing / transient_run_failure / actual_quality_blocker` 能按 spec 既定 precedence 稳定投影到 execute gate truth
  2. latest browser gate artifact 继续对 scope/linkage drift fail-closed

## Batch 3：CLI 与收口验证

### Task 3.1 更新 CLI surface 并完成 focused verification

- **任务编号**：T143-31
- **优先级**：P1
- **状态**：已完成（`truth-check` 通过，classification=`branch_only_implemented`）
- **文件**：`src/ai_sdlc/cli/program_cmd.py`, `tests/integration/test_cli_program.py`, `task-execution-log.md`
- **验收标准**：
  1. `program browser-gate-probe` 能直出 real probe execute gate state、plain-language 原因与下一步命令
  2. Playwright 缺失、browser launch failed、artifact missing 三类场景都有明确新手向提示
  3. focused verification、`program validate`、`verify constraints` 与 `workitem truth-check` 通过
