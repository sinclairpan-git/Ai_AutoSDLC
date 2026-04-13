# Tasks — 127 Frontend Contract Observation Producer Runtime Closure

## Batch A：Source profile runtime policy

### Task 127.1 新增 observation source profile 判定

- 为 canonical observation artifact 增加 runtime source profile helper
- 保持 schema 不变，仅消费现有 provenance/source_ref
- 允许 profile：
  - `sample_selfcheck`
  - `consumer_evidence`
  - `opaque`

## Batch B：Verify/gate/program 接线

### Task 127.2 将 sample self-check 与真实 consumer evidence 做 runtime split

- runtime attachment 暴露 source profile / requirement / issue
- verify 将 `sample_selfcheck` mismatch 投影为 `frontend_contract_observations` gap
- program readiness / remediation 对普通 spec 重新要求真实 consumer evidence

## Batch C：CLI 与测试闭环

### Task 127.3 补 scan/profile 输出与定向测试

- `scan` CLI 成功导出后打印 source profile
- 新增/更新测试：
  - `tests/unit/test_frontend_contract_runtime_attachment.py`
  - `tests/unit/test_frontend_contract_verification.py`
  - `tests/unit/test_program_service.py`
  - `tests/integration/test_cli_scan.py`
  - `tests/integration/test_cli_program.py`
  - `tests/integration/test_cli_verify_constraints.py`
