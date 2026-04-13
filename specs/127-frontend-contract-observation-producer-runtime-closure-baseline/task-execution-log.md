# Task Execution Log — 127 Frontend Contract Observation Producer Runtime Closure

## Batch 2026-04-14-001 | source profile runtime split closure

- **任务来源**：`120/T21 Contract Scanner And Observation Producer`
- **目标**：补齐 observation producer 的 runtime source profile、sample self-check / consumer evidence split，以及 verify/program 的诚实回退

### 本批改动

- 新增 `src/ai_sdlc/core/frontend_contract_observation_runtime_policy.py`，统一判定 observation source profile
- 更新 `frontend_contract_runtime_attachment.py`，挂接 `source_profile / requirement / issue`
- 更新 `frontend_contract_verification.py` 与 `frontend_gate_verification.py`，将 sample/profile mismatch 投影为 `frontend_contract_observations` gap
- 更新 `program_service.py`，让普通 spec 遇到 sample artifact 时重新回到 scan remediation 主线
- 更新 `cli/commands.py`，在 `scan` 成功导出后打印 source profile
- 补充 runtime/verify/program/scan 定向测试

### 定向验证

- `uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py tests/unit/test_frontend_contract_verification.py tests/unit/test_program_service.py tests/integration/test_cli_scan.py tests/integration/test_cli_program.py tests/integration/test_cli_verify_constraints.py -q`

### 结论

- `scan -> artifact -> active contract/gate self-check surface / program` 现在已能在 runtime 中区分 `sample_selfcheck` 与 `consumer_evidence`
- 普通 spec 不再会把 sample self-check artifact 误当成真实 close evidence
- `012/018` 的 framework self-check 主线保持可运行
