---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend enterprise-vue2 Provider Baseline

**编号**：`016-frontend-enterprise-vue2-provider-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-016-001 ~ FR-016-015 / SC-016-001 ~ SC-016-005）

---

## 分批策略

```text
Batch 1: provider truth freeze
Batch 2: mapping / whitelist / isolation freeze
Batch 3: implementation handoff and verification freeze
Batch 4: provider profile models slice
Batch 5: provider profile artifact slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `016` 不得重新定义 `015` 已冻结的 UI Kernel truth 或 `011` 已冻结的 Contract truth。
- `016` 不得在当前 child work item 中直接进入 business project runtime 包、完整 Vue2 wrapper、generation 约束、gate diagnostics 或 modern provider 实现。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_provider_profile.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_provider_profile_models.py`、`specs/016-frontend-enterprise-vue2-provider-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`tests/unit/test_frontend_provider_profile_artifacts.py`、`specs/016-frontend-enterprise-vue2-provider-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `016` 只冻结 Provider profile baseline，不默认决定任何 `src/` / `tests/` runtime side effect。
- 当前首批实现只放行 Provider profile 模型/标准体，不放行 runtime wrapper、generation 或 gate 实现。
- 当前第二批实现只放行 Provider profile artifact instantiation，不放行 runtime wrapper、generation runtime 或 gate 实现。
- 只有在用户明确要求进入实现，且 `016` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：provider truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `016` 是 `009` 下游的 `enterprise-vue2 Provider` child work item
  2. `spec.md` 明确 Provider 位于 UI Kernel 与 generation / gate / runtime 之间
  3. `spec.md` 不再依赖临时对话或设计稿才能解释 `016` 的边界
- **验证**：文档对账

### Task 1.2 冻结 Provider 与 Kernel / 公司组件库边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `Provider != UI Kernel != 公司组件库`
  2. formal docs 明确公司组件库只能作为 Provider 能力来源
  3. 不再出现 Provider 或公司组件库可反向定义 Kernel 的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 modern provider、完整 runtime 包、generation 与 gate 不属于当前 work item
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 Provider profile / wrapper contract，而不是直接写业务项目 runtime
- **验证**：scope review

---

## Batch 2：mapping / whitelist / isolation freeze

### Task 2.1 冻结 `Ui* -> 企业实现` 映射原则与 MVP 首批映射建议

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确映射总原则、稳定性要求与 MVP 首批映射建议
  2. formal docs 明确映射必须向上对齐 UI Kernel
  3. formal docs 明确首批映射对象与 `015` MVP `Ui*` 协议保持单一真值
- **验证**：mapping review

### Task 2.2 冻结白名单包装与危险能力隔离

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确白名单包装至少包括 API、能力和依赖收口
  2. formal docs 明确危险能力默认关闭，不因底层已有能力而默认开放
  3. formal docs 明确 Provider 不允许以全量 `Vue.use` 作为默认入口
- **验证**：语义对账

### Task 2.3 冻结 Legacy Adapter 与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Legacy Adapter 是受控桥接层，不是长期默认入口
  2. formal docs 明确 legacy 用法不得在新增代码中继续扩散
  3. formal docs 明确 Provider baseline 与 `015` UI Kernel baseline 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `models / runtime profile / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖映射边界、白名单包装、危险能力隔离与 Legacy Adapter 场景
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 runtime / gate / generation 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/plan.md`, `specs/016-frontend-enterprise-vue2-provider-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 Provider truth、mapping、whitelist / isolation 与 handoff 保持单一真值
  3. 当前分支上的 `016` formal docs 可作为后续进入 Provider profile 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：provider profile models slice

### Task 4.1 先写 failing tests 固定 Provider profile / MVP builder 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_provider_profile_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 MVP `Ui* -> 企业实现` 映射集合、白名单包装范围、危险能力隔离与 Legacy Adapter policy
  2. 单测明确覆盖重复 mapping / whitelist component id 的失败语义
  3. 首次运行定向测试时必须出现预期失败，证明 Provider profile models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`

### Task 4.2 实现最小 Provider profile models / MVP builder

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_provider_profile.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型明确承载 `Ui* -> 企业实现` 映射、白名单包装范围、危险能力隔离与 Legacy Adapter policy
  2. 提供 MVP baseline builder，并落实首批映射建议与 `no full Vue.use` 边界
  3. 实现只停留在结构化模型层，不引入 runtime wrapper、generation 或 gate 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_provider_profile_models.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/016-frontend-enterprise-vue2-provider-baseline src/ai_sdlc/models tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/016-frontend-enterprise-vue2-provider-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：provider profile artifact slice

### Task 5.1 先写 failing tests 固定 Provider artifact file set 与 payload 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_provider_profile_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `providers/frontend/enterprise-vue2/**` 的最小 artifact 文件集合
  2. 单测明确覆盖 mappings、whitelist、risk isolation 与 legacy adapter 的 artifact payload
  3. 首次运行定向测试时必须出现预期失败，证明 Provider artifact instantiation 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py -q`

### Task 5.2 实现最小 Provider artifact instantiation

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`, `src/ai_sdlc/generators/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 提供 Provider artifact root 与 materialize helper，并把 `EnterpriseVue2ProviderProfile` 物化为 canonical artifact tree
  2. artifact file set 至少覆盖 manifest、mappings、whitelist、risk isolation 与 legacy adapter
  3. 实现只停留在 artifact instantiation 层，不引入 runtime wrapper、generation runtime 或 gate 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py -q`

### Task 5.3 Fresh verify 并追加 artifact batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/016-frontend-enterprise-vue2-provider-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/016-frontend-enterprise-vue2-provider-baseline src/ai_sdlc/generators tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 artifact batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/016-frontend-enterprise-vue2-provider-baseline src/ai_sdlc/generators tests/unit`, `uv run ai-sdlc verify constraints`
