# 任务分解：Frontend Mainline Browser Gate Recheck Remediation Runtime Implementation Baseline

**编号**：`105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-105-001` ~ `FR-105-010` / `SC-105-001` ~ `SC-105-004`）

---

## 分批策略

```text
Batch 1: execute decision runtime cut
Batch 2: ProgramService and CLI handoff propagation
Batch 3: runbook regression, registry sync, verification
```

---

## 执行护栏

- `105` 只允许修改 `frontend_gate_verification.py`、`program_service.py`、`program_cmd.py`、对应 tests、`program-manifest.yaml`、`project-state.yaml` 与 `specs/105/...`
- `105` 不得改写 `104` 的 docs-only result-binding truth
- `105` 不得实现 browser gate replay runtime、auto-fix engine、后台循环或 program aggregation
- `105` 不得把 fail-closed `blocked` 重新包装成 `recheck_required`
- `105` 不得把 remediation runbook 中的 policy artifact gaps 丢弃或误导成 replay 请求

---

## Batch 1：execute decision runtime cut

### Task 1.1 收敛 frontend gate decision mapping

- [x] 在 `frontend_gate_verification.py` 将纯 visual/a11y evidence 缺口映射到 `recheck_required`
- [x] 在 `frontend_gate_verification.py` 将 policy artifact 缺失、scope/linkage 不可信与结果不自洽保持为 fail-closed `blocked`
- [x] 在 `frontend_gate_verification.py` 将 evidence-backed `actual_quality_blocker` 映射到 `needs_remediation`

**完成标准**

- execute decision runtime 与 `104` 的映射 truth 对齐，不再把 recheck 与 remediation 混成单一 blocker

### Task 1.2 固定定向单元回归

- [x] 在 `tests/unit/test_frontend_gate_verification.py` 补 `recheck_required` 回归
- [x] 在 `tests/unit/test_frontend_gate_verification.py` 补 policy artifact fail-closed 回归
- [x] 在 `tests/unit/test_frontend_gate_verification.py` 补 evidence-backed remediation 回归

**完成标准**

- unit regression 能稳定证明 browser gate mapping honesty

## Batch 2：ProgramService and CLI handoff propagation

### Task 2.1 在 ProgramService 分离 recheck 与 remediation 路径

- [x] 在 `program_service.py` 只为 `recheck_required` materialize recheck handoff
- [x] 在 `program_service.py` 为 `blocked` / `needs_remediation` 输出 remediation runbook
- [x] 保持 `frontend_visual_a11y_policy_artifacts` 等 gap 继续进入 remediation path

**完成标准**

- ProgramService 不再把 recheck gap 与 remediation gap 混在同一 handoff 中

### Task 2.2 在 CLI surface 呈现 execute gate truth

- [x] 在 `program_cmd.py` 呈现 frontend `recheck_required`
- [x] 在 `program_cmd.py` 呈现 frontend `blocked` / `needs_remediation`
- [x] 在 `tests/integration/test_cli_program.py` 锁定 status / execute surface 的回归

**完成标准**

- operator 从 CLI 即可判断当前应该重跑、修复还是停在 fail-closed `blocked`

## Batch 3：runbook regression, registry sync, verification

### Task 3.1 补 remediation runbook 回归

- [x] 在 `tests/unit/test_program_service.py` 增加 policy artifact remediation runbook 回归
- [x] 确认 remediation input 不丢失 `frontend_visual_a11y_policy_artifacts`

**完成标准**

- remediation runbook 能稳定保留非 replay gap

### Task 3.2 创建 implementation carrier 并同步治理状态

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 增加 `105` canonical entry
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `105` 推进到 `106`

**完成标准**

- 已完成实现拥有合法 work item 载体，program registry 与 project-state 同步到位

### Task 3.3 运行验证

- [x] 运行 targeted unit / integration regression
- [x] 运行 `ruff check`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`

**完成标准**

- implementation carrier 与当前代码事实一致，fresh verification 通过
