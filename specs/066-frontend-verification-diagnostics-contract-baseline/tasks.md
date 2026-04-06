---
related_doc:
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/plan.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/plan.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/plan.md"
---
# 任务分解：Frontend Verification Diagnostics Contract Baseline

**编号**：`066-frontend-verification-diagnostics-contract-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-066-001 ~ FR-066-030 / SC-066-001 ~ SC-066-006）

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: diagnostics core entity and frontend status resolution
Batch 3: verification / gate consumer convergence
Batch 4: surface adapter convergence
Batch 5: fresh verification and archive
```

---

## 执行护栏

- `Batch 1` 只允许推进 `spec.md`、`plan.md`、`tasks.md` 与 `task-execution-log.md`。
- `Batch 2` 只允许写入 `src/ai_sdlc/core/frontend_contract_observation_provider.py`、`src/ai_sdlc/core/frontend_contract_verification.py`、`tests/unit/test_frontend_contract_verification.py`、必要的 `tasks.md / plan.md / task-execution-log.md` 同步。
- `Batch 3` 只允许写入 `src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/gates/frontend_contract_gate.py`、`tests/unit/test_frontend_contract_gate.py`、`tests/unit/test_frontend_gate_verification.py`、`tests/unit/test_verify_constraints.py`、必要的文档同步。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、必要时 `src/ai_sdlc/cli/verify_cmd.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_verify_constraints.py`、必要的文档同步。
- `066` 不得改写 `012 / 013 / 014 / 065 / 018` 已冻结的 formal truth。
- `066` 不得引入新的平行 verify stage、gate family、runner truth model 或第二套 diagnostics pipeline。
- `066` 不得实现 remediation / recheck / visual-a11y 检查本体，只能冻结这些下游消费者的 handoff 边界。
- `066` 不得允许 `verify constraints`、gate、CLI、runner、`ProgramService` 通过空列表、异常字符串、路径缺失或局部上下文自行重算 `missing / invalid / empty / drift` 语义。
- `policy_projection` 只能由 status resolution 单向导出；任何 surface 不得跳过 projection 直接产出 verdict、severity、report family 或 readiness。
- 只有在用户明确要求进入实现，且 `066` formal docs 已通过 docs-only 门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 diagnostics contract 的 scope、truth order 与非目标

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `Layer A / Layer B / Layer C` 的分层关系与 truth order
  2. `spec.md` 明确五类状态集与 `status -> projection` 的正式规则
  3. `spec.md` 明确 `066` 不引入新的平行 verify stage、gate family 或 runner truth model
- **验证**：文档对账

### Task 1.2 冻结推荐文件面、owner boundary 与验证矩阵

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出 diagnostics core、verification/gate consumer、surface adapter 的推荐文件面
  2. `plan.md` 明确 owner boundary、阻断决策与关键路径验证矩阵
  3. `plan.md` 明确 frontend 是首个 source family，但 `Layer B` 保持 source-agnostic
- **验证**：file-map review

### Task 1.3 冻结批次边界与 implementation handoff

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 将 docs freeze、core status resolution、consumer convergence、surface adapter convergence 与 fresh verification 切成独立批次
  2. `tasks.md` 明确不得重算语义、不得跳过 projection、不得实现 downstream checks 本体
  3. 后续实现团队可直接按批次推进，不需再次回到对话重新拆分
- **验证**：tasks review

### Task 1.4 收紧 execution log 初始化状态

- **任务编号**：T14
- **优先级**：P1
- **依赖**：T13
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `task-execution-log.md` 不再保留与 `066` 无关的 scaffold 模板批次
  2. 当前状态被明确为“Batch 1 docs-only freeze 已完成，后续实现待 execute 授权”
  3. execution log 可在后续实现批次 append-only 归档
- **验证**：文档对账

### Task 1.5 运行 docs-only 门禁

- **任务编号**：T15
- **优先级**：P1
- **依赖**：T14
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/spec.md`, `specs/066-frontend-verification-diagnostics-contract-baseline/plan.md`, `specs/066-frontend-verification-diagnostics-contract-baseline/tasks.md`, `specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check` 无格式问题
  3. `066` formal docs 对分层、status、projection、adapter boundary 保持单一真值
- **验证**：`uv run ai-sdlc verify constraints`, `git diff --check`

---

## Batch 2：diagnostics core entity and frontend status resolution

### Task 2.1 先写 failing tests 固定五类状态与短路决议语义

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T15
- **文件**：`tests/unit/test_frontend_contract_verification.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `missing_artifact`、`invalid_artifact`、`valid_empty`、`drift`、`clean`
  2. 单测明确覆盖 `missing -> invalid -> valid_empty -> drift -> clean` 的短路与互斥顺序
  3. 首次运行定向测试时必须出现预期失败，证明 status resolution 尚未完全按 `066` 冻结
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`

### Task 2.2 实现最小 diagnostics core entity 与 frontend status normalizer

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/frontend_contract_observation_provider.py`, `src/ai_sdlc/core/frontend_contract_verification.py`
- **可并行**：否
- **验收标准**：
  1. `Layer B` core entity 至少暴露 `source_family`、`source_key`、`diagnostic_status`、`evidence`、`policy_projection`
  2. 实现明确区分 absence、presence-but-broken、normalized-empty、drift、clean
  3. `policy_projection` 由 status resolution 单向导出，不引入 gate / CLI / program 私有逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`

### Task 2.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_verification.py -q` 通过
  2. `git diff --check -- src/ai_sdlc/core tests/unit specs/066-frontend-verification-diagnostics-contract-baseline` 无格式问题
  3. execution log 追加记录本批 touched files、命令、结果与对账结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`, `git diff --check -- src/ai_sdlc/core tests/unit specs/066-frontend-verification-diagnostics-contract-baseline`

---

## Batch 3：verification / gate consumer convergence

### Task 3.1 先写 failing tests 固定 projection 消费与 blocker / gap 分类

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T23
- **文件**：`tests/unit/test_frontend_contract_gate.py`, `tests/unit/test_frontend_gate_verification.py`, `tests/unit/test_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `missing_artifact` 投影为 gap，而不是 drift
  2. 单测明确覆盖 `valid_empty` 不计 gap、不升级 drift
  3. 单测明确覆盖 `invalid_artifact` 与 `drift` 的独立 blocker / report member 语义
- **验证**：`uv run pytest tests/unit/test_frontend_contract_gate.py tests/unit/test_frontend_gate_verification.py tests/unit/test_verify_constraints.py -q`

### Task 3.2 实现 verification / gate consumer 的统一 projection 消费

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`src/ai_sdlc/core/frontend_gate_verification.py`, `src/ai_sdlc/core/verify_constraints.py`, `src/ai_sdlc/gates/frontend_contract_gate.py`
- **可并行**：否
- **验收标准**：
  1. `verify_constraints`、gate-facing helper 与 `frontend_contract_gate` 都只消费 `policy_projection` 与 `diagnostic_status`
  2. 实现不再从空 observation 列表、路径缺失或 parse 异常字符串局部重算语义
  3. 保持 `012 / 018` 的 verification/gate 主链结构不变，不新增平行 stage 或 gate family
- **验证**：`uv run pytest tests/unit/test_frontend_contract_gate.py tests/unit/test_frontend_gate_verification.py tests/unit/test_verify_constraints.py -q`

### Task 3.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T33
- **优先级**：P0
- **依赖**：T32
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. 定向 unit tests 通过
  2. `uv run ai-sdlc verify constraints` 通过
  3. execution log 追加记录 projection 消费切片的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_gate.py tests/unit/test_frontend_gate_verification.py tests/unit/test_verify_constraints.py -q`, `uv run ai-sdlc verify constraints`

---

## Batch 4：surface adapter convergence

### Task 4.1 先写 failing tests 固定 CLI / ProgramService 不重算语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`, `tests/integration/test_cli_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 单测/集成测试明确覆盖同一输入在 CLI 与 `ProgramService` 上给出相同 `diagnostic_status` / projection 摘要
  2. 测试明确断言 `valid_empty` 不被 CLI 或 `ProgramService` 误报为 gap
  3. 测试明确断言任何 surface 不得把 `missing_artifact` 或 `invalid_artifact` 伪装成 drift
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_verify_constraints.py -q`

### Task 4.2 实现 surface adapter 的统一 diagnostics 消费

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`, `src/ai_sdlc/cli/verify_cmd.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService` 只消费 `policy_projection` 与 `diagnostic_status`
  2. 如果需要触碰 `verify_cmd.py`，改动也只限于暴露既有 diagnostics truth，不引入新规则
  3. CLI terminal / JSON、runner 与 `ProgramService` 对同一输入产生确定性、可重复的结果
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_verify_constraints.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. CLI / `ProgramService` 相关定向回归通过
  2. `uv run ai-sdlc verify constraints` 与 `git diff --check` 通过
  3. execution log 追加记录 surface adapter convergence 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_verify_constraints.py -q`, `uv run ai-sdlc verify constraints`, `git diff --check`

---

## Batch 5：fresh verification and archive

### Task 5.1 执行 focused verification

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`src/ai_sdlc/core/frontend_contract_observation_provider.py`, `src/ai_sdlc/core/frontend_contract_verification.py`, `src/ai_sdlc/core/frontend_gate_verification.py`, `src/ai_sdlc/core/verify_constraints.py`, `src/ai_sdlc/core/program_service.py`, `src/ai_sdlc/gates/frontend_contract_gate.py`, `tests/unit/test_frontend_contract_gate.py`, `tests/unit/test_frontend_contract_verification.py`, `tests/unit/test_frontend_gate_verification.py`, `tests/unit/test_program_service.py`, `tests/unit/test_verify_constraints.py`, `tests/integration/test_cli_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. diagnostics core、verification/gate consumer、CLI/program surface 的定向测试通过
  2. `uv run ai-sdlc verify constraints` 通过
  3. `git diff --check` 无格式问题
- **验证**：`uv run pytest tests/unit/test_frontend_contract_gate.py tests/unit/test_frontend_contract_verification.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`, `uv run ai-sdlc verify constraints`, `git diff --check`

### Task 5.2 追加 execution log 并同步批次状态

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`specs/066-frontend-verification-diagnostics-contract-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 追加记录 latest batch 的 touched files、命令、结果与结论
  2. `tasks.md` 与 execution log 的 batch 状态一致
  3. 归档顺序符合“先验证，再归档，再提交”
- **验证**：execution log review
