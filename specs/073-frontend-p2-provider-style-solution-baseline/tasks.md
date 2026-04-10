---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P2 Provider Style Solution Baseline

**编号**：`073-frontend-p2-provider-style-solution-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（已冻结 formal baseline / 第 4 ~ 15 节）

---

## 分批策略

```text
Batch 1: solution confirmation truth freeze
Batch 2: provider / style / fallback boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: provider manifest models slice
Batch 5: solution snapshot / style pack / install strategy models slice
Batch 6: artifact materialization slice
Batch 7: recommendation / preflight / fallback orchestration slice
Batch 8: CLI solution-confirm slice
Batch 9: verify / consistency / regression slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `073` 不得重新定义 `009` 的 UI Kernel truth、`016` 的 enterprise-vue2 Provider truth、`017` 的 generation governance truth 或 `018` 的 gate / compatibility truth。
- `073` 不得在当前 child work item 中直接进入真实 npm / pnpm / yarn 安装、真实 registry 登录、真实企业权限验证、第二公开 Provider、React UI 开放或开放式风格编辑器实现。
- `073` 不得把 `docs/superpowers/*` 当成 canonical formal 输出目录；formal true source 只允许落在 `specs/073-frontend-p2-provider-style-solution-baseline/`。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_provider_profile.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_provider_profile_models.py`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/models/frontend_solution_confirmation.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_solution_confirmation_models.py`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 6` 只允许写入 `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`、`src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`tests/unit/test_frontend_provider_profile_artifacts.py`、`tests/unit/test_frontend_solution_confirmation_artifacts.py`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 7` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 8` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`USER_GUIDE.zh-CN.md`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 9` 只允许写入 `src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`、`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `073` 只冻结并分解“技术方案确认 / Provider 选择 / Style Pack”formal baseline，不默认决定任何 business project runtime side effect。
- 只有在用户明确要求进入实现，且 `spec.md / plan.md / tasks.md` 三件套已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：solution confirmation truth freeze

### Task 1.1 冻结 work item 范围、时机与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `073` 是 `009` 下游的 P2 formal baseline，而不是 `docs/superpowers/*` 设计参考稿
  2. `spec.md` 明确技术方案确认位于 `需求确认完成 -> 技术方案确认 -> 技术设计拆分 -> 开发任务生成`
  3. `spec.md` 不再依赖临时对话才能解释 `073` 的边界与真值顺序
- **验证**：文档对账

### Task 1.2 冻结 `solution_snapshot` 的 requested/effective 审计语义

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `solution_snapshot` 是“技术方案定版快照 + 审计快照”
  2. formal docs 明确任何可被系统重写的字段都采用 `requested_* / effective_*` 成对建模
  3. formal docs 明确 fallback 只允许改写 `effective_*`，不得覆盖 `requested_*`
- **验证**：术语一致性检查

### Task 1.3 冻结 `decision_status`、预检结果与版本化行为

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`, `specs/073-frontend-p2-provider-style-solution-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `decision_status` 的固定枚举与含义
  2. formal docs 明确 `availability_summary` 是机器可消费结构，不是纯自然语言摘要
  3. formal docs 明确每次最终确认与显式 fallback 都通过新 snapshot 版本或新审计事件表达，不覆盖旧值
- **验证**：snapshot-review

---

## Batch 2：provider / style / fallback boundary freeze

### Task 2.1 冻结 Provider / Style Pack / Adapter 的四层边界

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `frontend_stack -> provider -> style_pack -> adapter` 的四层关系
  2. formal docs 明确 `provider` 是正式交付单元，不是简单组件映射
  3. formal docs 明确 `style pack` 是独立于 Provider 的视觉语义层
- **验证**：boundary review

### Task 2.2 冻结风格支持真值来源、统一枚举与默认推荐边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `provider_manifest.style_support_matrix` 是风格支持等级唯一真值来源
  2. formal docs 明确全链路只使用 `full / partial / degraded / unsupported`
  3. formal docs 明确简单模式主推荐默认不得推荐 `degraded`
- **验证**：style-support review

### Task 2.3 冻结当前阶段的 fallback、React 与公开路径边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`, `specs/073-frontend-p2-provider-style-solution-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确当前阶段只有 `Vue2 -> enterprise-vue2` 与 `Vue3 -> public-primevue`
  2. formal docs 明确 `enterprise-vue2` 不可用时，允许的退路是“切换前端技术栈与 Provider”，不是“只切 Provider”
  3. formal docs 明确 `react` 只作为内部可建模值，不进入当前 UI、推荐与 Provider 计算
- **验证**：fallback-boundary review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `models / generators / core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `009/016/017/018` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵、预检展示与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/plan.md`, `specs/073-frontend-p2-provider-style-solution-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 Provider 双路径、5 套 Style Pack、requested/effective、显式跨栈 fallback 与 verify consistency
  2. `tasks.md` 明确最终确认页必须展示 `requested_* / effective_* / preflight_status / will_change_on_confirm / fallback_required`
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`, `specs/073-frontend-p2-provider-style-solution-baseline/plan.md`, `specs/073-frontend-p2-provider-style-solution-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 solution confirmation、Provider truth、Style Pack truth 与 handoff 保持单一真值
  3. 当前分支上的 `073` formal docs 可作为后续进入实现批次的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：provider manifest models slice

### Task 4.1 先写 failing tests 固定双 Provider manifest 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_provider_profile_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `enterprise-vue2` 与 `public-primevue` 的最小 manifest 集合
  2. 单测明确覆盖 `style_support_matrix`、`availability_prerequisites`、`install_strategy_ids`、`cross_stack_fallback_targets`
  3. 首次运行定向测试时必须出现预期失败，证明多 Provider manifest 真值尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`

### Task 4.2 实现最小 Provider manifest models / builders

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_provider_profile.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型明确承载双 Provider 真值、风格支持矩阵、安装策略引用与跨栈 fallback 声明
  2. 保留 `enterprise-vue2` 现有 baseline builder，并新增 `public-primevue`
  3. 实现只停留在结构化模型层，不引入真实安装、CLI 或 verify 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`

### Task 4.3 Fresh verify 并追加 provider model batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_provider_profile_models.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/models/frontend_provider_profile.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_provider_profile_models.py`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/models tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 provider model batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`, `uv run ruff check src/ai_sdlc/models/frontend_provider_profile.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_provider_profile_models.py`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：solution snapshot / style pack / install strategy models slice

### Task 5.1 先写 failing tests 固定 snapshot / style pack / install strategy 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_solution_confirmation_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `decision_status`、`requested_* / effective_*`、`availability_summary` 与版本化审计行为
  2. 单测明确覆盖新 snapshot 生成时版本递增、`changed_from_snapshot_id` 正确串联且旧 snapshot 不被覆盖
  3. 单测明确覆盖 5 套内置 Style Pack、统一支持等级枚举与 `react` 隐藏边界
  4. 首次运行定向测试时必须出现预期失败，证明 solution confirmation models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_solution_confirmation_models.py -q`

### Task 5.2 实现最小 solution confirmation / style pack / install strategy models

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/models/frontend_solution_confirmation.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型明确承载 `solution_snapshot`、Style Pack manifest 与 install strategy 真值
  2. 固化 `decision_status`、结构化 `availability_summary` 与 `requested_* / effective_*` 成对建模
  3. `solution_snapshot` 必须支持版本链、`changed_from_snapshot_id` 串联与旧值保留，不得以原地覆盖表达确认或 fallback
  4. 实现只停留在结构化模型层，不引入 ProgramService orchestration 或 CLI 交互逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_solution_confirmation_models.py -q`

### Task 5.3 Fresh verify 并追加 solution model batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_solution_confirmation_models.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/models/frontend_solution_confirmation.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_solution_confirmation_models.py`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/models tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 solution model batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_solution_confirmation_models.py -q`, `uv run ruff check src/ai_sdlc/models/frontend_solution_confirmation.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_solution_confirmation_models.py`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 6：artifact materialization slice

### Task 6.1 先写 failing tests 固定 Provider / Style / Snapshot artifact 语义

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T53
- **文件**：`tests/unit/test_frontend_provider_profile_artifacts.py`, `tests/unit/test_frontend_solution_confirmation_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `providers/frontend/<provider_id>/provider.manifest.yaml`、`style-support.yaml` 与 5 套 Style Pack artifact 文件集合
  2. 单测明确覆盖 `effective_style_pack_id`、`resolved_style_tokens`、`provider_theme_adapter_config`、`style_fidelity_status`、`style_degradation_reason_codes`
  3. 首次运行定向测试时必须出现预期失败，证明 artifact materialization 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py -q`

### Task 6.2 实现最小 Provider / Style / Snapshot artifact materialization

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T61
- **文件**：`src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`, `src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py`, `src/ai_sdlc/generators/__init__.py`
- **可并行**：否
- **验收标准**：
  1. artifact 文件面稳定落在 `providers/frontend/*`、`governance/frontend/solution/*` 与 `.ai-sdlc/memory/frontend-solution-confirmation/*`
  2. `provider_manifest.style_support_matrix` 被物化为唯一风格支持真值文件，不引入第二套矩阵来源
  3. 实现只停留在 artifact instantiation 层，不引入 ProgramService 或真实安装执行逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py -q`

### Task 6.3 Fresh verify 并追加 artifact batch 归档

- **任务编号**：T63
- **优先级**：P0
- **依赖**：T62
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/generators tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 artifact batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/generators tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 7：recommendation / preflight / fallback orchestration slice

### Task 7.1 先写 failing tests 固定 recommendation / preflight / fallback 语义

- **任务编号**：T71
- **优先级**：P0
- **依赖**：T63
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖简单模式推荐、企业可用性判定、显式跨栈 fallback requirement 与 `blocked` 路径
  2. 单测明确覆盖简单模式默认不推荐 `degraded` 风格
  3. 首次运行定向测试时必须出现预期失败，证明 orchestration 尚未实现
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 7.2 实现最小 recommendation / preflight / fallback orchestration

- **任务编号**：T72
- **优先级**：P0
- **依赖**：T71
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. 输出分层推荐：前端、后端、API 协作分开建模
  2. 企业 Provider 失败时只输出 `fallback_required` 或 `blocked`，且退路明确为 `vue2 + enterprise-vue2 -> vue3 + public-primevue`
  3. 实现不执行真实安装，只输出 preflight 结果、候选 `effective_*` 与审计对象
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 7.3 Fresh verify 并追加 orchestration batch 归档

- **任务编号**：T73
- **优先级**：P0
- **依赖**：T72
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 orchestration batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 8：CLI solution-confirm slice

### Task 8.1 先写 failing tests 固定 CLI 简单模式 / 高级模式 / 最终确认页语义

- **任务编号**：T81
- **优先级**：P0
- **依赖**：T73
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖简单模式单套主推荐输出
  2. 集成测试明确覆盖高级模式 7 步结构化向导与最终预检结果区
  3. 首次运行定向测试时必须出现预期失败，证明 CLI solution-confirm 尚未实现
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 8.2 实现最小 CLI solution-confirm 入口

- **任务编号**：T82
- **优先级**：P0
- **依赖**：T81
- **文件**：`src/ai_sdlc/cli/program_cmd.py`, `USER_GUIDE.zh-CN.md`
- **可并行**：否
- **验收标准**：
  1. CLI 提供结构化技术方案确认入口，不回退到自由文本手打方案
  2. 最终确认页必须展示 `requested_* / effective_* / preflight_status / will_change_on_confirm / fallback_required`
  3. `will_change_on_confirm` 只作为确认前派生字段，不落成独立 snapshot 真值
  4. 确认后落盘的 snapshot artifact 不得包含 `will_change_on_confirm` 字段
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 8.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T83
- **优先级**：P0
- **依赖**：T82
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/cli USER_GUIDE.zh-CN.md tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/cli USER_GUIDE.zh-CN.md tests/integration`, `uv run ai-sdlc verify constraints`

---

## Batch 9：verify / consistency / regression slice

### Task 9.1 先写 failing tests 固定 verify / consistency / regression 语义

- **任务编号**：T91
- **优先级**：P0
- **依赖**：T83
- **文件**：`tests/unit/test_verify_constraints.py`, `tests/integration/test_cli_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 单测与集成测试明确覆盖 `provider_manifest.style_support_matrix` 唯一真值、Style Pack 引用完整性、requested/effective 与 `decision_status` 一致性
  2. 测试明确覆盖简单模式不得默认推荐 `degraded`、`react` 不进入当前 UI/provider 计算
  3. 测试明确覆盖确认后落盘的 snapshot artifact 不得包含 `will_change_on_confirm` 字段
  4. 首次运行定向测试时必须出现预期失败，证明 verify / regression attachment 尚未实现
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`

### Task 9.2 实现最小 verify / consistency / regression attachment

- **任务编号**：T92
- **优先级**：P0
- **依赖**：T91
- **文件**：`src/ai_sdlc/core/verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. `verify_constraints` 能校验 Provider / Style / Snapshot 真值一致性与最小 regression 边界
  2. `verify_constraints` 必须校验持久化 snapshot 中不存在 `will_change_on_confirm` 这类确认前派生字段
  3. `verify_constraints` 不成为第二套 provider/style 真值来源
  4. 实现只停留在 scoped verify attachment 层，不引入新规则系统或真实安装副作用
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`, `uv run ai-sdlc verify constraints`

### Task 9.3 Fresh verify 并追加 verify batch 归档

- **任务编号**：T93
- **优先级**：P0
- **依赖**：T92
- **文件**：`specs/073-frontend-p2-provider-style-solution-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`、`uv run ai-sdlc verify constraints` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/core tests` 通过
  3. `task-execution-log.md` 追加记录当前 verify batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`, `uv run ai-sdlc verify constraints`, `uv run ruff check src tests`, `git diff --check -- specs/073-frontend-p2-provider-style-solution-baseline src/ai_sdlc/core tests`
