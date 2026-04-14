---
related_doc:
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "program-manifest.yaml"
---
# 实施计划：Frontend Mainline Browser Gate Real Probe Runtime Baseline

**功能编号**：`143-frontend-mainline-browser-gate-real-probe-runtime-baseline`
**日期**：2026-04-14

## 实施批次

1. 定义 `143` formal carrier，并把 `frontend-mainline-delivery` 的当前真实 blocker收敛到 browser gate 真探测主链
2. 先写 red tests，锁定 shared trace/screenshot capture、interaction probe capture 与 execute-state binding
3. 扩展 `frontend_browser_gate_runtime`、`ProgramService` 与 CLI，引入 bounded real runner contract 与真实 artifact materialization
4. 做 focused verification、对抗评审与 root truth 回写，为后续 `workspace integration` tranche 留出干净边界

## 技术背景

**语言/版本**：Python 3.11、Node.js（作为 default Playwright runner substrate）
**主要依赖**：`pyyaml`、现有 `ProgramService` / browser gate models；default runner 走预置 Node/Playwright substrate，不新增 Python-side Playwright dependency
**存储**：`.ai-sdlc/memory/frontend-browser-gate/latest.yaml`、`.ai-sdlc/artifacts/frontend-browser-gate/<gate_run_id>/`
**测试**：`pytest` unit/integration；runner tests 通过 injected stub 保持离线稳定
**目标平台**：已通过 `096` mainline host readiness 的本地/CI 环境
**约束**：只补 browser gate 真探测；假设 host 已满足 `096` 最低 browser runtime 前提；default runner 必须 hard-timeout 并对 local path 自动尝试 `<target>/index.html` 入口；不碰 `workspace_integration`、root takeover、多浏览器矩阵、auto-fix

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 先文档后实现 | `143` 先冻结 spec/plan/tasks，再进入 tests-first implementation |
| truth order 不反写上游 | 继续只消费 `125` apply artifact 与 `073` solution snapshot，不重写 solution/apply truth |
| fail-closed 优先 | artifact 缺失、runtime failure、scope/linkage drift 均保持结构化 fail-closed |
| 小白可用 | CLI failure surface 必须输出 plain-language 原因与单一下一步命令 |

## 项目结构

```text
specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
src/ai_sdlc/core/frontend_browser_gate_runtime.py
src/ai_sdlc/core/frontend_gate_verification.py
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
src/ai_sdlc/models/frontend_browser_gate.py
tests/unit/test_frontend_browser_gate_runtime.py
tests/unit/test_frontend_gate_verification.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
scripts/frontend_browser_gate_probe_runner.mjs
```

## 实施路径

### Phase 0：Gap freeze 与 red fixtures

**目标**：把 `125/126` 当前 placeholder gap 明确锁定为 real probe runtime 缺口
**产物**：`143` formal docs、runner stdout JSON contract、real probe success / incomplete / transient failure red tests
**验证方式**：相关 unit tests 在现状下失败或暴露 placeholder 行为
**回退方式**：只回退 `143` carrier 与对应 red fixtures

### Phase 1：Real probe runtime

**目标**：为 browser gate execute path 引入 bounded real runner contract，并 materialize 真实 smoke / interaction artifacts
**产物**：runner contract、default runner、真实 Playwright trace archive + screenshot + interaction snapshot、artifact records / receipts / bundle materialization 更新
**验证方式**：`tests/unit/test_frontend_browser_gate_runtime.py`、相关 `ProgramService` tests
**回退方式**：保留 `125` 既有 models/CLI surface，回退 default runner wiring

### Phase 2：Execute truth binding 与 CLI

**目标**：确保 real probe 结果稳定驱动 `ProgramService`、status、CLI 与 remediation/recheck handoff
**产物**：`ProgramService` execute/read path 调整、CLI 输出更新、focused integration coverage、plain-language failure surface
**验证方式**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`
**回退方式**：回退 `143` 新增 truth fields 和 runner wiring，不动 `126` 既有 fallback semantics

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| shared trace / screenshot capture | `tests/unit/test_frontend_browser_gate_runtime.py` | `tests/unit/test_program_service.py` |
| transient failure / evidence missing taxonomy | `tests/unit/test_frontend_browser_gate_runtime.py` | `tests/unit/test_frontend_gate_verification.py` |
| execute gate binding | `tests/unit/test_program_service.py` | `tests/integration/test_cli_program.py` |

## 边界

- 只补真实 browser probe runtime 与 execute truth
- 只允许当前 `gate_run_id` artifact namespace
- 不补 `workspace_integration`、root takeover、browser dependency auto-provision；缺少 Playwright 前提时只允许 fail-closed 并给出清晰下一步
- 不扩张到多浏览器矩阵或完整 visual regression 平台
