---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
---
# 任务分解：Frontend Contract Observation Provider Baseline

**编号**：`013-frontend-contract-observation-provider-baseline` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-013-001 ~ FR-013-016 / SC-013-001 ~ SC-013-005）

---

## 分批策略

```text
Batch 1: provider truth freeze
Batch 2: artifact envelope and provenance baseline
Batch 3: implementation handoff and verification freeze
Batch 4: provider contract / artifact IO slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/frontend_contract_observation_provider.py`、`tests/unit/test_frontend_contract_observation_provider.py`、`specs/013-frontend-contract-observation-provider-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `013` 不得把 scanner runtime、provider runtime、verify mainline、registry attachment、auto-fix 或 remediation workflow 混入当前 child work item 的 formal baseline。
- `013` 不得改写 `011` 已冻结的 contract artifact truth 或 `012` 已冻结的 verify integration truth。
- `013` 只冻结 observation provider baseline，不默认决定 active consumer path 或新的 CLI command surface。
- 当前首批实现只放行 provider contract / artifact IO，不放行 scanner candidate、CLI、registry 或 `012` verify mainline。
- 只有在用户明确要求进入实现，且 `013` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：provider truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `013` 是 `012` 下游的 observation provider child work item
  2. `spec.md` 明确 provider 位于 `011` contract truth 与 `012` verify consumption 之间
  3. `spec.md` 不再依赖临时对话才能解释 `013` 的边界
- **验证**：文档对账

### Task 1.2 冻结 provider 与 scanner 的角色边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 scanner 只是 candidate provider，不是 provider baseline 本体
  2. formal docs 明确 manual/export provider 同样合法
  3. 不再出现“scanner 等于全部 provider 合同”的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`, `specs/013-frontend-contract-observation-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 verify mainline、registry、auto-fix 与 remediation 不属于当前 work item
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 provider contract / artifact IO / scanner candidate，而不是继续改 `012`
- **验证**：scope review

---

## Batch 2：artifact envelope and provenance baseline

### Task 2.1 冻结 observation artifact envelope

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `frontend-contract-observations.json` 的 canonical naming 与最小 envelope
  2. formal docs 明确 provider 输出必须可映射到 `PageImplementationObservation` 或兼容 JSON 结构
  3. 不再出现 scanner 私有内部格式直接冒充 artifact contract 的表述
- **验证**：artifact contract review

### Task 2.2 冻结 provenance / freshness 语义

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 artifact 至少包含来源信息与 freshness 证据
  2. formal docs 明确来源不明或 freshness 不可判断时，下游必须可诚实识别
  3. formal docs 明确 provenance/freshness 是结构化字段，不是自由文本备注
- **验证**：语义对账

### Task 2.3 冻结 downstream consumer handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`, `specs/013-frontend-contract-observation-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider artifact 供下游 verify integration 消费，但当前 work item 不重写 `012` attachment
  2. formal docs 明确 consumer path / registry attachment 需要由下游工单显式决定
  3. formal docs 明确 provider baseline 与 verify baseline 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / scanners / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `012` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/plan.md`, `specs/013-frontend-contract-observation-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 manual provider、scanner provider、artifact 缺字段、provenance/freshness 缺失与 downstream handoff 场景
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 verify mainline、registry 或 remediation 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/spec.md`, `specs/013-frontend-contract-observation-provider-baseline/plan.md`, `specs/013-frontend-contract-observation-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 provider truth、artifact envelope、scanner separation 与 handoff 保持单一真值
  3. 当前分支上的 `013` formal docs 可作为后续进入 provider/scanner 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：provider contract / artifact IO slice

### Task 4.1 先写 failing tests 固定 artifact contract / round-trip 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_contract_observation_provider.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 canonical file naming、artifact envelope、provenance/freshness 与 observation round-trip
  2. 单测明确覆盖 provenance 缺失、freshness 缺失与 observation payload 非法时的失败语义
  3. 首次运行定向测试时必须出现预期失败，证明 provider helper 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_observation_provider.py -q`

### Task 4.2 实现最小 provider contract / artifact IO helper

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/frontend_contract_observation_provider.py`
- **可并行**：否
- **验收标准**：
  1. helper 提供 canonical artifact path、provider artifact dataclass 与 JSON read/write round-trip
  2. helper 明确输出/读取 provenance、freshness 与 `PageImplementationObservation` payload
  3. helper 只负责 provider contract / artifact IO，不引入 scanner candidate、CLI 或 `012` verify mainline 改动
- **验证**：`uv run pytest tests/unit/test_frontend_contract_observation_provider.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/013-frontend-contract-observation-provider-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_observation_provider.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/013-frontend-contract-observation-provider-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_observation_provider.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/013-frontend-contract-observation-provider-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`
