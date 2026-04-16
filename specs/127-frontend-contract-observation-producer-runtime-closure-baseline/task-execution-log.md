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

### Batch 2026-04-16-002 | close-out normalization for S2 cluster reconciliation

#### 2.1 批次范围

- 覆盖目标：将 `127` 的 latest close evidence 升级为 current `workitem close-check` grammar，可被 `154` 的 `frontend-contract-foundation` cluster reconciliation 直接消费
- 预读范围：`specs/120-open-capability-tranche-backlog-baseline/tasks.md`、`specs/154-frontend-contract-foundation-closure-audit-reconciliation-baseline/spec.md`
- 激活的规则：truth-only normalization、no-runtime-drift、single-source close evidence

#### 2.2 统一验证命令

- `V1`（规则门禁）
  - 命令：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
  - 结果：通过；输出 `verify constraints: no BLOCKERs.`
- `V2`（self close-check）
  - 命令：`python -m ai_sdlc workitem close-check --wi specs/127-frontend-contract-observation-producer-runtime-closure-baseline`
  - 结果：通过；latest batch `ready for completion`
- `V3`（truth freshness）
  - 命令：`python -m ai_sdlc program truth sync --dry-run`
  - 结果：由 `154` final close-out 统一触发 latest truth refresh；最终 `program truth audit` 为 `ready / fresh`
- `V4`（diff hygiene）
  - 命令：`git diff --check`
  - 结果：通过；无输出

#### 2.3 任务记录

##### T127-N1 | latest batch normalization

- 改动范围：`specs/127-frontend-contract-observation-producer-runtime-closure-baseline/task-execution-log.md`
- 改动内容：
  - 追加 current close-check grammar 所需的 latest batch 结构
  - 保持 `127` 既有 runtime 结论不变，只补齐 latest close-out 元数据
- 新增/调整的测试：无
- 执行的命令：`V1`、`V2`、`V3`、`V4`
- 测试结果：通过；`127` latest batch 已进入 current close-check grammar
- 是否符合任务目标：是

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：本批只做 close-out normalization，不重写 `127` runtime scope
- 代码质量：不适用（execution log normalization）
- 测试质量：`verify constraints`、`workitem close-check`、`git diff --check` 与 root truth fresh audit 已纳入当前 close-out 证据
- 结论：`127` 已具备进入 current close-check grammar 的前置条件

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：不涉及
- `related_plan`（如存在）同步状态：`154` 仅将本批作为 `S2` cluster close evidence 的 normalization 输入
- 关联 branch/worktree disposition 计划：与 `154` 同批 truth-only close-out
- 说明：本批不宣称新增 runtime，只补齐 latest close evidence

#### 2.6 批次结论

- `127` 现在拥有一条 current close-check grammar 可消费的 latest batch，可直接进入 `frontend-contract-foundation` cluster reconciliation

#### 2.7 归档后动作

- **验证画像**：`truth-only`
- **改动范围**：`specs/127-frontend-contract-observation-producer-runtime-closure-baseline/task-execution-log.md`
- **已完成 git 提交**：是
- **提交哈希**：`HEAD`（与 `154` 同批 close-out）
