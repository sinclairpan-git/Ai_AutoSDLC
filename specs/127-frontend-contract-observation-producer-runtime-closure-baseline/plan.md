# 实施计划：127 Frontend Contract Observation Producer Runtime Closure

## 1. 目标

把 `T21` 当前已经存在但尚未闭环的 scanner / producer runtime 补成一条诚实主线：

1. `scan` 导出能显式说明 observation source profile
2. runtime attachment 能携带 source profile / requirement / issue
3. active contract/gate self-check surface 与普通 `program` surface 在普通 spec 上拒绝 sample self-check artifact
4. `012/018` 自检链路保持可运行

## 2. 实施分解

### Batch A | Source Profile Runtime Policy

- 新增 observation runtime policy helper
- 基于已有 provenance/source_ref 判定 `sample_selfcheck / consumer_evidence / opaque`
- 约束 sample self-check 只在显式 self-check work item 中允许

### Batch B | Verify/Gate/Program Wiring

- runtime attachment 暴露 source profile / requirement / issue
- verify report 将 sample/profile mismatch 投影为 `frontend_contract_observations` gap
- program readiness / remediation 继承该 gap，不再把 sample artifact 当成普通 ready evidence

### Batch C | CLI And Verification

- `scan` 成功导出后打印 source profile
- 补单测/集成测试覆盖：
  - `scan` 导出 profile
  - runtime attachment source profile
  - verify diagnostic source_profile_mismatch
  - program remediation 对 sample artifact 的诚实回退

## 3. 验证策略

- `uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py tests/unit/test_frontend_contract_verification.py tests/unit/test_program_service.py tests/integration/test_cli_scan.py tests/integration/test_cli_program.py tests/integration/test_cli_verify_constraints.py -q`
- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`

## 4. 风险与护栏

- 不修改 canonical artifact schema，避免把 `127` 扩张成 schema migration
- 只输出抽象 source profile，不泄漏 sample fixture 实际路径
- sample self-check allowlist 保持窄范围，只覆盖现有 framework self-check 主线
