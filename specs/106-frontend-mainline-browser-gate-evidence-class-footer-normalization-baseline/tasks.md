# 任务分解：Frontend Mainline Browser Gate Evidence Class Footer Normalization Baseline

**编号**：`106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-106-001` ~ `FR-106-007` / `SC-106-001` ~ `SC-106-004`）

---

## 分批策略

```text
Batch 1: footer normalization and governance sync
Batch 2: verification and close-out
```

---

## 执行护栏

- `106` 只允许修改 `100`~`104` 的 `spec.md` footer、`program-manifest.yaml`、`project-state.yaml` 与 `specs/106/...`
- `106` 不得修改 `src/`、`tests/` 或运行时行为
- `106` 不得补造 `frontend_contract_observations`、browser evidence 或 policy artifacts
- `106` 不得把真实剩余 blocker 伪装成“全部完成”

---

## Batch 1：footer normalization and governance sync

### Task 1.1 为 100-104 补齐 canonical footer

- [x] 为 `100` 的 `spec.md` 补 `related_doc` 与 `frontend_evidence_class`
- [x] 为 `101` 的 `spec.md` 补 `related_doc` 与 `frontend_evidence_class`
- [x] 为 `102` 的 `spec.md` 补 `related_doc` 与 `frontend_evidence_class`
- [x] 为 `103` 的 `spec.md` 补 `related_doc` 与 `frontend_evidence_class`
- [x] 为 `104` 的 `spec.md` 补 `related_doc` 与 `frontend_evidence_class`

**完成标准**

- `100`~`104` 的 footer 与 manifest mirror 对齐，不再缺 `missing_footer_key`

### Task 1.2 创建 normalization carrier 并推进治理状态

- [x] 创建 `106` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 注册 `106`
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `106` 推进到 `107`

**完成标准**

- 本次治理归并有合法 carrier，program registry 与 project state 同步

## Batch 2：verification and close-out

### Task 2.1 回放约束与状态验证

- [x] 运行 verify-constraints 相关回归
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc program status`

**完成标准**

- `missing_footer_key` 消失，真实 blocker 仍继续暴露

### Task 2.2 完成 diff hygiene 与 close-check

- [x] 运行 `git diff --check`
- [x] 运行 `uv run ai-sdlc workitem close-check --wi specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline`
- [x] 完成本批提交并回填 execution log

**完成标准**

- `106` 可作为 canonical normalization work item 收口
