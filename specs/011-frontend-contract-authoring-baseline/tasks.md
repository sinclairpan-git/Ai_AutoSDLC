---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Contract Authoring Baseline

**编号**：`011-frontend-contract-authoring-baseline` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-011-001 ~ FR-011-015 / SC-011-001 ~ SC-011-006）

---

## 分批策略

```text
Batch 1: contract truth surface freeze
Batch 2: artifact chain and legacy extension baseline
Batch 3: implementation handoff and first-slice gate freeze
Batch 4: contract model slice
Batch 5: contract artifact instantiation slice
Batch 6: contract drift helper slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_contracts.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_contract_models.py` 与 append-only `task-execution-log.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/generators/frontend_contract_artifacts.py`、可选 `src/ai_sdlc/generators/__init__.py`、`tests/unit/test_frontend_contract_artifacts.py`、`specs/011-frontend-contract-authoring-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 6` 只允许写入 `src/ai_sdlc/core/frontend_contract_drift.py`、`tests/unit/test_frontend_contract_drift.py`、`specs/011-frontend-contract-authoring-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `011` 不得把 UI Kernel、Provider、Gate 或 runtime 代码混入当前 child work item 的 formal baseline。
- 当前首批实现只放行 Contract models / serialization；`generators / core / gates` 仍属于后续批次。
- 当前下一批实现只放行 Contract artifact instantiation；`core / gates` 仍属于后续批次。
- 当前 drift 批次只放行只读 helper，不放行 gate verdict、自动回写或源码扫描器。
- 只有在用户明确要求进入实现，且 `011` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：contract truth surface freeze

### Task 1.1 冻结 Contract 范围与非目标

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `011` 是 `009` 下游的 `Contract` child work item
  2. `spec.md` 明确覆盖对象与非目标，包括 Kernel / Provider / Gate / runtime 不属于当前 work item
  3. `spec.md` 不再依赖临时对话才能解释 `011` 的边界
- **验证**：文档对账

### Task 1.2 冻结 Contract 对象边界与 recipe declaration 归属

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `page/module contract`、`Contract Rule Bundle`、`Contract Legacy Context` 等关键实体可被直接引用
  2. `recipe declaration` 归 Contract、`recipe standard body` 归 UI Kernel 的边界被明确写死
  3. `i18n / validation / hard rules / whitelist / token rules` 被明确纳入 MVP 首批 Contract 对象
- **验证**：文档交叉引用检查

### Task 1.3 冻结 Contract 是实例化 artifact 的单一口径

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Contract 是实例化 artifact，不是补充文档
  2. formal docs 明确 Contract 同时服务于生成、检查与修复
  3. formal docs 明确 Contract 不得退化为 prompt 注释或散落 Markdown
- **验证**：术语一致性检查

---

## Batch 2：artifact chain and legacy extension baseline

### Task 2.1 冻结 Contract 的 stage / artifact 链路

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Contract 在 `refine / design / decompose / verify / execute / close` 中的落位
  2. formal docs 明确 `decompose / verify` 与后续 Gate 以 Contract 和代码对照，不以 prompt 为准
  3. 不再出现“Contract 只是设计阶段一次性产物”的表述
- **验证**：stage relationship review

### Task 2.2 冻结 Contract drift 处理口径

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确发现漂移后只能 `回写 Contract` 或 `修正实现代码`
  2. formal docs 明确不允许长期 Contract 失真
  3. formal docs 明确“先写代码后补 Contract”不属于允许路径
- **验证**：文档对账

### Task 2.3 冻结 legacy 扩展字段承载路径

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `compatibility_profile / migration_level / legacy_boundary_ref / migration_scope` 被明确收敛为 Contract 扩展字段
  2. formal docs 明确 MVP 不引入第二套迁移专用 artifact 系统
  3. legacy 口径与 `009` 母规格保持一致
- **验证**：全文术语检查

---

## Batch 3：implementation handoff and first-slice gate freeze

### Task 3.1 冻结后续实现文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 Contract 模型、artifact 实例化、drift 检查和 Gate 接入的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的后续实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖模型形状、序列化、stage integration、legacy 扩展字段和 drift 正反向场景
  2. `tasks.md` 明确 formal baseline 完成后当前只放行 `models + serialization` 首切片
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 Contract 边界、artifact 链路、legacy 扩展字段和 handoff 口径保持单一真值
  3. 当前分支上的 `011` formal docs 可作为后续进入 `models + serialization` 首切片的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：contract model slice

### Task 4.1 先写 failing tests 固定最小 Contract 模型形状

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_contract_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `FrontendContractSet / PageContract / ModuleContract / ContractRuleBundle / ContractLegacyContext` 的最小 roundtrip shape
  2. 单测明确覆盖 `page metadata`、`recipe declaration`、legacy 扩展字段与 `i18n / validation` 关键校验关系
  3. 首次运行定向测试时必须出现预期失败，证明当前能力尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_models.py -q`

### Task 4.2 实现最小 Contract models 与导出面

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_contracts.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. `frontend_contracts.py` 提供 `Frontend Contract Set`、`Page/Module Contract`、`Contract Rule Bundle`、`Contract Legacy Context` 及其最小子对象模型
  2. `PageContract` 的 `page metadata` 与 `recipe declaration` 为必备结构，且 `requires_validation / uses_i18n` 与规则对象的关系可被模型校验
  3. 相关模型可同时从 `ai_sdlc.models.frontend_contracts` 与 `ai_sdlc.models` 稳定导入
- **验证**：`uv run pytest tests/unit/test_frontend_contract_models.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/011-frontend-contract-authoring-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_models.py -q` 通过
  2. `git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/models tests/unit` 无输出，且 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_models.py -q`, `git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：contract artifact instantiation slice

### Task 5.1 先写 failing tests 固定 artifact 文件布局与 YAML 形状

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_contract_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 page/module contract 的最小 artifact 文件集与目录布局
  2. 单测明确覆盖 `page.metadata.yaml`、`page.recipe.yaml`、`page.i18n.yaml`、`form.validation.yaml`、`frontend.rules.yaml`、`component-whitelist.ref.yaml`、`token-rules.ref.yaml` 的 YAML shape
  3. 首次运行定向测试时必须出现预期失败，证明 generator 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_artifacts.py -q`

### Task 5.2 实现最小 frontend_contract_artifacts generator

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/generators/frontend_contract_artifacts.py`, `src/ai_sdlc/generators/__init__.py`
- **可并行**：否
- **验收标准**：
  1. `frontend_contract_artifacts.py` 可将 `FrontendContractSet` 物化为 `contracts/frontend/pages/<page_id>/...` 与 `contracts/frontend/modules/<module_id>/...` 下的最小 artifact 集
  2. generator 生成的 YAML payload 保留 `recipe declaration`、`legacy_context`、`i18n / validation / hard_rules / whitelist_ref / token_rules_ref` 的结构化语义
  3. 相关入口可被测试与后续 stage 集成稳定导入
- **验证**：`uv run pytest tests/unit/test_frontend_contract_artifacts.py -q`

### Task 5.3 Fresh verify 并追加 artifact batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/011-frontend-contract-authoring-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_models.py tests/unit/test_frontend_contract_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/generators tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 artifact instantiation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_models.py tests/unit/test_frontend_contract_artifacts.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/generators tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 6：contract drift helper slice

### Task 6.1 先写 failing tests 固定 drift record 与 observation 语义

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T53
- **文件**：`tests/unit/test_frontend_contract_drift.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 page artifact 与 observation 匹配时的无漂移场景
  2. 单测明确覆盖 recipe mismatch、缺失 i18n key、缺失 validation field、增量治理下 legacy 扩散等正向漂移场景
  3. 首次运行定向测试时必须出现预期失败，证明 drift helper 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_drift.py -q`

### Task 6.2 实现最小 frontend_contract_drift helper

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T61
- **文件**：`src/ai_sdlc/core/frontend_contract_drift.py`
- **可并行**：否
- **验收标准**：
  1. `frontend_contract_drift.py` 提供结构化 observation 输入、drift record 输出和 page/root 级检测入口
  2. 每条 drift record 明确 `field_path`、`expected`、`actual` 与 `update_contract / fix_implementation` 二选一处理口径
  3. helper 只做只读判定，不引入 gate verdict、自动修复或源码扫描
- **验证**：`uv run pytest tests/unit/test_frontend_contract_drift.py -q`

### Task 6.3 Fresh verify 并追加 drift batch 归档

- **任务编号**：T63
- **优先级**：P0
- **依赖**：T62
- **文件**：`specs/011-frontend-contract-authoring-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_models.py tests/unit/test_frontend_contract_artifacts.py tests/unit/test_frontend_contract_drift.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 drift helper batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_models.py tests/unit/test_frontend_contract_artifacts.py tests/unit/test_frontend_contract_drift.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/011-frontend-contract-authoring-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`
