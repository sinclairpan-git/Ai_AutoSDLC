# Tasks — 128 Frontend Runtime Attachment Verify Gate Readiness Closure

## Batch A：Attachment truth 接线

### Task 128.1 将 verify constraints 改为消费 runtime attachment helper

- active `012/018` scope 不再直接拼本地 observation 路径
- unresolved scope 必须能 fail-closed 地进入 verify gate
- frontend gate prerequisite 继续复用同一份 attachment input

## Batch B：CLI / context 闭环

### Task 128.2 输出 runtime attachment summary

- `build_verification_gate_context()` 暴露 `frontend_contract_runtime_attachment`
- `verify constraints --json` 输出同名字段
- 保持既有 `verification_gate.sources` 与 PASS 语义稳定

## Batch C：验证与评审

### Task 128.3 Focused verification + adversarial review

- 新增/更新测试：
  - `tests/unit/test_verify_constraints.py`
  - `tests/integration/test_cli_verify_constraints.py`
  - `tests/integration/test_cli_program.py`
- 运行 focused verification 与对抗评审，吸收 fail-closed / UX / truth-order 反馈
