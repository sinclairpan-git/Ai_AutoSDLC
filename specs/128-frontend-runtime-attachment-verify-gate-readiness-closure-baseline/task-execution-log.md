# 执行记录：Frontend Runtime Attachment Verify Gate Readiness Closure Baseline

**功能编号**：`128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`
**日期**：2026-04-14
**状态**：已完成首批闭环

## Batch 2026-04-14-001 | Verify/runtime attachment truth wiring

- `verify_constraints` 现在通过 runtime attachment helper 解析 active `012/018` 的 observation attachment
- unresolved `spec_dir` 会进入 `frontend_contract_runtime_scope`，并 fail-closed 地投影进 verify gate
- verify context 与 `verify constraints --json` 现在会输出 `frontend_contract_runtime_attachment`
- frontend gate prerequisite 继续通过 shared attachment input 消费同一份 observation truth，不再在 verify 层重复 loader

## Batch 2026-04-14-002 | Focused verification

- `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_program.py -q`
  - `242 passed in 17.50s`
- `uv run ai-sdlc verify constraints`
  - `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program validate`
  - `program validate: PASS`
- `git diff --check`
  - 通过

## Batch 2026-04-14-003 | Adversarial review hardening

- Avicenna 指出 `120/T22` 的 formal 验证命令仍引用不存在的 `tests/integration/test_cli_verify.py`
- Feynman 指出两处 truth mismatch：
  - runtime work item 识别顺序不能绕过 `linked_wi_id`
  - `128/spec.md` 的 truth-order 说明必须与实现一致
- 同步修复：
  - `120/tasks.md` 的验证命令改为 `tests/integration/test_cli_verify_constraints.py`
  - `_frontend_runtime_attachment_work_item_id()` 恢复 `linked_wi_id -> feature.id/spec_dir` 顺序
  - verify context / JSON 对 runtime attachment provenance 做 `source_ref` 脱敏
  - `128/spec.md` 的输入链接与 truth-order 说明改为与仓库现状一致
- 修复后复验：
  - `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_program.py -q`
    - `242 passed in 17.50s`
  - `uv run ai-sdlc verify constraints`
    - `verify constraints: no BLOCKERs.`
  - `uv run ai-sdlc program validate`
    - `program validate: PASS`
- 最终 reviewer 结论：
  - Avicenna：无高/中风险问题；残余风险是不要把 `128` 误读为 `T23/T25/T33` 已完成
  - Feynman：无高/中风险问题；残余风险是后续若 attachment payload 新增路径字段，需要同步纳入脱敏测试

## 本批结论

- `128` 已把 runtime attachment 从 program/frontend readiness 的局部真值推进为 verify/gate/readiness 共用的 attachment truth
- 当前切片不宣称 `T23/T25/T33` 已关闭；它只补齐 `T22` 在 verify/runtime summary 上的首批闭环
