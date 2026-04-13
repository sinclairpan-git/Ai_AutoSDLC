# 执行计划：Frontend Mainline Browser Gate Evidence Class Footer Normalization Baseline

**功能编号**：`106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline`  
**创建日期**：2026-04-13  
**状态**：footer normalization baseline 已落地；close-out verification 进行中  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`106` 的目标不是新增 runtime feature，而是把 `100`~`104` 已存在的 manifest evidence-class truth 对账回 authored spec footer，消除 `missing_footer_key` 噪声，让 browser gate 主线只剩真实外部缺口。

## 2. 范围

### 2.1 In Scope

- 创建 `106` formal docs 与 execution log
- 为 `100`~`104` 的 `spec.md` 补 canonical footer
- 在 `program-manifest.yaml` 注册 `106`
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `106` 推进到 `107`
- 回放 `verify constraints`、`program status`、`program validate` 与 diff hygiene

### 2.2 Out Of Scope

- 修改 `verify_constraints.py`、`program_cmd.py` 或其他运行时代码
- 补造 `frontend_contract_observations`、browser evidence 或 policy artifacts
- 改写 `100`~`105` 的合同正文
- 扩张为新的 evidence-class 规则设计工作项

## 3. 变更文件面

`106` 允许改动的文件面如下：

- `specs/100-frontend-mainline-action-plan-binding-baseline/spec.md`
- `specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`
- `specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md`
- `specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`
- `specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md`
- `specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/plan.md`
- `specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/tasks.md`
- `specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/task-execution-log.md`

## 4. 实施规则

### 4.1 Authoring honesty

- footer normalization 只补 `related_doc` 与 `frontend_evidence_class`
- 不修改 `100`~`104` 的正文合同语义
- `related_doc` 必须锚定各自已声明输入，不能凭空扩张依赖

### 4.2 Runtime truth preservation

- `106` 不能通过改状态面文案掩盖真实 blocker
- `frontend_contract_observations` 等外部缺口必须继续保留
- `missing_footer_key` 消除后，剩余状态面应更接近真实问题

### 4.3 Scope discipline

- `106` 不触碰 `src/`、`tests/`
- `106` 不新增 CLI surface 或 diagnostics family
- `106` 只承担 browser gate mainline 的 authoring normalization 收口

## 5. 分批计划

### Batch 1：footer normalization

- 为 `100`~`104` 补 canonical footer
- 创建 `106` formal docs
- 注册 `106` manifest entry 并推进 project state

### Batch 2：verification and close-out

- 运行 `verify constraints`、`program validate`、`program status`
- 确认 `missing_footer_key` 已清除而真实 blocker 仍保留
- 运行 `git diff --check` 与 `workitem close-check`

## 6. 最小验证策略

- `uv run pytest tests/integration/test_cli_verify_constraints.py -k 'missing_footer_key' -q`
- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program status`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/100-frontend-mainline-action-plan-binding-baseline/spec.md specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline`
- `uv run ai-sdlc workitem close-check --wi specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline`

## 7. 回滚原则

- 如果 `100`~`104` footer 与正文输入不一致，必须回退
- 如果 `106` 误宣称真实 blocker 已解决，必须回退
- 如果 `106` 不小心触及 `src/` / `tests/` 或运行时行为，必须回退
