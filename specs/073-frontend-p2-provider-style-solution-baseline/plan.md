---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P2 Provider Style Solution Baseline

**编号**：`073-frontend-p2-provider-style-solution-baseline` | **日期**：2026-04-07 | **规格**：`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`

## 1. 目标与定位

本计划处理的是 `009-frontend-governance-ui-kernel` 下游的 P2 formal baseline：`Frontend P2 Provider Style Solution Baseline`。它不是继续膨胀 `016` 的企业 Vue2 provider 映射，也不是直接进入外部前端 runtime/npm 安装执行，而是在现有：

- `015` / `016` 的 UI Kernel 与 enterprise-vue2 Provider truth
- `017` 的 generation governance truth
- `018` 的 gate / compatibility / verify truth

之上，补齐一条新的 framework 主线：

- 在“需求确认完成之后、技术设计拆分之前”提供技术方案确认
- 将前端 Provider 从单一企业库映射升级为可扩展的多 Provider 交付单元
- 将 Style Pack 作为独立于 Provider 的视觉语义层纳入 canonical truth
- 用 `solution_snapshot` 承接推荐、请求、生效、预检、fallback 与审计链路

当前 plan 的目标不是直接实现完整产品 UI，而是先把核心 truth 与实现切片拆清楚，使后续实现批次可以稳定落在 `models / generators / core / cli / tests` 的现有骨架上。P2 第一阶段仍只开放：

- `Vue2 -> enterprise-vue2`
- `Vue3 -> public-primevue`

并保持 `react` 只作为内部可建模值，不进入当前 UI、推荐器与 provider 计算。

## 2. 范围与约束

### In Scope

- 将现有 enterprise-only provider truth 扩展为多 Provider manifest 真值面，同时保留 `enterprise-vue2`
- 新增 `solution_snapshot`、`style_pack_manifest`、`install_strategy` 的结构化模型
- 定义并物化 P2 第一阶段的 5 套内置 Style Pack
- 在 `ProgramService` 中实现简单模式推荐、可用性判定、最终预检与显式跨栈 fallback 组装
- 为 `program` CLI 提供结构化的“技术方案确认”交互面
- 将 `requested_* / effective_*`、风格支持矩阵与降级审计纳入 verify / tests

### Out Of Scope

- 不在本批执行真实 `npm/pnpm/yarn` 安装、真实 registry 登录或外网依赖下载
- 不在本批开放第二个公开 Vue3 Provider 或 React Provider
- 不在本批实现开放式风格编辑器或可视化主题设计器
- 不在本批交付完整 Web 图形界面；第一实现面以 CLI / artifact / program orchestration 为主
- 不把 provider runtime / adapter 安装执行逻辑直接塞进 `ProgramService` 主链

## 3. 当前激活的实现触点

当前仓库的实现承接面应沿用现有 baseline 文件组织，不新开一套体系。建议触点如下：

```text
src/ai_sdlc/
├── models/
│   ├── frontend_provider_profile.py
│   │   # 扩展为多 Provider manifest 真值，新增 public-primevue
│   ├── frontend_solution_confirmation.py
│   │   # 新增：solution_snapshot / style_pack_manifest / install_strategy
│   └── __init__.py
├── generators/
│   ├── frontend_provider_profile_artifacts.py
│   │   # 扩展 provider manifest/style support materialization
│   ├── frontend_solution_confirmation_artifacts.py
│   │   # 新增：style packs / install strategies / snapshot artifacts
│   └── __init__.py
├── core/
│   ├── program_service.py
│   │   # recommendation / preflight / fallback / snapshot orchestration
│   └── verify_constraints.py
│       # provider/style/solution truth consistency verification
└── cli/
    └── program_cmd.py
        # program solution-confirm（推荐命名）结构化确认入口

tests/
├── unit/
│   ├── test_frontend_provider_profile_models.py
│   ├── test_frontend_provider_profile_artifacts.py
│   ├── test_frontend_solution_confirmation_models.py
│   ├── test_frontend_solution_confirmation_artifacts.py
│   ├── test_program_service.py
│   └── test_verify_constraints.py
└── integration/
    ├── test_cli_program.py
    └── test_cli_verify_constraints.py
```

建议的最小 artifact 落点也应在 plan 中一起锁定：

- `providers/frontend/<provider_id>/provider.manifest.yaml`
- `providers/frontend/<provider_id>/style-support.yaml`
- `governance/frontend/solution/style-packs/<style_pack_id>.yaml`
- `governance/frontend/solution/install-strategies/<install_strategy_id>.yaml`
- `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml`

其中：

- Provider 是否支持某个 Style Pack、支持等级是多少，统一从 `providers/frontend/<provider_id>/...` 物化
- `solution_snapshot` 走 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml` 与版本链路
- 实际外部项目中的 adapter/npm 安装执行不在当前批次实现

## 4. 分阶段安排

### Phase 0：Formal baseline freeze and planning alignment

**目标**：冻结 `073` 的 canonical spec 与 implementation plan，并把二次评审结论和非阻塞修订反映到正式真值。  
**产物**：`spec.md`、`plan.md`。  
**验证方式**：formal review 结论对账、`git diff --check`。  
**回退方式**：仅回退 `specs/073/...` 文档改动。  

### Phase 1：Provider manifest model slice

**目标**：把当前 enterprise-only provider profile 扩展为 P2 可用的多 Provider manifest 真值层，并保留向后兼容。  
**产物**：

- `src/ai_sdlc/models/frontend_provider_profile.py`
- `src/ai_sdlc/models/__init__.py`
- `tests/unit/test_frontend_provider_profile_models.py`

**实现重点**：

- 保留 `enterprise-vue2` builder 与现有语义组件映射
- 新增 `public-primevue` Provider 真值
- 把 `style_support_matrix`、`access_mode`、`install_strategy_ids`、`availability_prerequisites`、`cross_stack_fallback_targets` 纳入统一模型
- 避免新旧 Provider truth 双轨并存

**验证方式**：

- `uv run pytest tests/unit/test_frontend_provider_profile_models.py -q`
- `git diff --check`

**回退方式**：仅回退 Provider model/export 与对应测试。  

### Phase 2：Solution snapshot / style pack / install strategy model slice

**目标**：新增 `073` 的核心结构化对象，使 `solution_snapshot`、Style Pack 与安装策略拥有独立模型与 builder。  
**产物**：

- `src/ai_sdlc/models/frontend_solution_confirmation.py`
- `src/ai_sdlc/models/__init__.py`
- `tests/unit/test_frontend_solution_confirmation_models.py`

**实现重点**：

- 固化 `decision_status`
- 固化 `requested_* / effective_*`
- 固化 `availability_summary` 的机器可消费结构
- 固化 5 套内置 Style Pack 与统一支持等级枚举：`full/partial/degraded/unsupported`
- 明确 `react` 只存在于内部枚举与模型，不进入当前 UI 选择

**验证方式**：

- `uv run pytest tests/unit/test_frontend_solution_confirmation_models.py -q`
- `git diff --check`

**回退方式**：仅回退新增模型文件、导出与对应测试。  

### Phase 3：Artifact materialization slice

**目标**：将 Provider / Style Pack / Install Strategy / Solution Snapshot 真值物化为稳定 artifact，形成可被 verify/program 消费的文件面。  
**产物**：

- `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`
- `src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py`
- 可选 `src/ai_sdlc/generators/__init__.py`
- `tests/unit/test_frontend_provider_profile_artifacts.py`
- `tests/unit/test_frontend_solution_confirmation_artifacts.py`

**实现重点**：

- 扩展 provider artifact，增加 `style-support.yaml`
- 物化 5 套 Style Pack 与 install strategy artifact
- 物化 `solution_snapshot` 的最小输出，包括：
  - `effective_style_pack_id`
  - `resolved_style_tokens`
  - `provider_theme_adapter_config`
  - `style_fidelity_status`
  - `style_degradation_reason_codes`
- 保持 artifact root 稳定，不引入多套平行落点

**验证方式**：

- `uv run pytest tests/unit/test_frontend_provider_profile_artifacts.py -q`
- `uv run pytest tests/unit/test_frontend_solution_confirmation_artifacts.py -q`
- YAML payload / path layout review
- `git diff --check`

**回退方式**：仅回退 generators 与对应测试。  

### Phase 4：Recommendation / preflight / fallback orchestration slice

**目标**：在 `ProgramService` 中落下简单模式推荐、企业 Provider 可用性判定、最终预检与显式跨栈 fallback orchestration。  
**产物**：

- `src/ai_sdlc/core/program_service.py`
- `tests/unit/test_program_service.py`

**实现重点**：

- 前端、后端、API 协作推荐分层输出
- 简单模式默认不推荐 `degraded` 风格
- 企业 Provider 失败时只输出：
  - `fallback_required`
  - 或 `blocked`
- 且退路明确为：
  - `vue2 + enterprise-vue2`
  - 切换到
  - `vue3 + public-primevue`
- 不执行真实安装，只输出 preflight 结果、推荐结果、预期 `effective_*` 与审计对象

**验证方式**：

- `uv run pytest tests/unit/test_program_service.py -q`
- `git diff --check`

**回退方式**：仅回退 `program_service.py` 与对应测试。  

### Phase 5：CLI solution confirmation slice

**目标**：为当前 CLI/program 主链提供结构化技术方案确认入口，使简单模式与高级模式都能在命令面落地。  
**产物**：

- `src/ai_sdlc/cli/program_cmd.py`
- `tests/integration/test_cli_program.py`
- 可选 `USER_GUIDE.zh-CN.md`

**实现重点**：

- 建议新增命令：`program solution-confirm`
- 简单模式：
  - 输出单套主推荐
  - 展示推荐理由、通过前提、未通过前提、风格支持等级
- 高级模式：
  - 通过显式选项而不是自由输入承接 7 步向导
  - 当前仅开放 `Vue2`、`Vue3`
- 最终确认页必须展示：
  - `requested_*`
  - `effective_*`
  - `preflight_status`
  - `will_change_on_confirm`
  - `fallback_required`
- `will_change_on_confirm` 只作为 UI/CLI 预检派生字段，不写成独立快照真值

**验证方式**：

- `uv run pytest tests/integration/test_cli_program.py -q`
- CLI snapshot/report fixture review
- `git diff --check`

**回退方式**：仅回退 CLI、guide 和对应集成测试。  

### Phase 6：Verify / consistency / regression slice

**目标**：将新的 Provider/Style/Snapshot truth 纳入 verify 与 consistency check，避免“模型能表达、artifact 缺失、CLI 能吐、verify 不知道”的断层。  
**产物**：

- `src/ai_sdlc/core/verify_constraints.py`
- `tests/unit/test_verify_constraints.py`
- `tests/integration/test_cli_verify_constraints.py`

**实现重点**：

- 校验 `provider_manifest.style_support_matrix` 是否是唯一支持真值来源
- 校验 Style Pack 引用是否存在悬空项
- 校验 `requested_* / effective_*` 差异是否与 `decision_status`、fallback 字段一致
- 校验简单模式不会默认推荐 `degraded`
- 校验 `react` 不被当前 UI/provider 计算暴露

**验证方式**：

- `uv run pytest tests/unit/test_verify_constraints.py -q`
- `uv run pytest tests/integration/test_cli_verify_constraints.py -q`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

**回退方式**：仅回退 verify / tests 改动。  

## 5. Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| Provider manifest slice | 统一 provider 真值、P2 第一阶段双 Provider、风格支持矩阵 | 不得把 style 真值再写回 `style_pack_manifest`；不得偷偷引入第二公开 Provider |
| Solution snapshot slice | 冻结推荐/请求/生效/审计对象与版本链 | 不得覆盖 `requested_*`；不得把 `will_change_on_confirm` 写成独立真值 |
| Recommendation / preflight slice | 输出规则推荐、企业可用性判定与 fallback requirement | 不得执行真实 npm 安装；不得把跨栈 fallback 降格成“只切 provider” |
| CLI solution-confirm slice | 提供结构化确认入口与最终预检展示 | 不得退回自由文本手打方案；不得在确认后静默改写 `effective_*` |
| Verify / consistency slice | 校验 artifact、truth-order 与一致性 | 不得重新定义推荐规则；不得成为第二套 provider/style 真值来源 |
| Downstream provider runtime | 后续真正承接 adapter 安装、外部项目接入与网络侧执行 | 不得在当前 work item 中被提前塞入 `program_service` 主链 |

## 6. 关键路径验证策略

1. `solution_snapshot` 必须保持“版本化审计快照”定位，不覆盖旧值。
2. 任何 fallback 只能改 `effective_*`，不得改 `requested_*`。
3. `enterprise-vue2` 不可用时，系统必须要求显式确认“切换前端技术栈与 Provider”。
4. `provider_manifest.style_support_matrix` 必须是唯一风格支持真值来源。
5. 简单模式默认不得推荐 `degraded` 风格。
6. `react` 只能存在于内部枚举，不得进入当前 UI、推荐结果或 Provider 选择列表。
7. `will_change_on_confirm` 只能是确认前派生字段，确认后的真值必须回到 `solution_snapshot`。
8. 当前批次不得承诺真实 npm/registry 安装执行，preflight 只负责“能否走通”的判定与审计。

## 7. 最小测试矩阵（未来实现批次）

1. Provider models 能同时构建 `enterprise-vue2` 与 `public-primevue`，并稳定暴露风格支持矩阵。
2. Style Pack models 能稳定暴露 5 套内置风格，且统一使用 `full/partial/degraded/unsupported`。
3. 简单模式在 `enterprise_provider_eligible = true` 且需求强指向企业方案时，输出 `vue2 + enterprise-vue2 + enterprise-default`。
4. 简单模式在企业条件不满足时，输出 `vue3 + public-primevue`，并展示未通过前提。
5. 企业 Provider preflight 失败时，`requested_frontend_stack/requested_provider_id` 保持用户原始意图，`effective_*` 只在显式确认后变化。
6. 最终确认页若存在 `requested_* != effective_*`，CLI 必须显式展示差异，且 snapshot 落盘后可追溯原因。
7. `provider_manifest.style_support_matrix` 若引用未知 Style Pack、或与 artifact 不一致，`verify constraints` 必须失败。
8. `program solution-confirm` 简单模式接受推荐时，snapshot 中 `requested_* = effective_*`；高级模式显式 fallback 时，`decision_status = fallback_confirmed`。
9. 风格生成产物必须同时包含：
   - `effective_style_pack_id`
   - `resolved_style_tokens`
   - `provider_theme_adapter_config`
   - `style_fidelity_status`
   - `style_degradation_reason_codes`

## 8. 执行前置条件与回退

- `073` 的 spec 必须保持 accepted/frozen 后才能进入实现批次。
- 后续实现建议使用独立 worktree 承接，不直接在 formal baseline 会话里混入实现代码。
- 如果执行中发现需要真实 npm/registry 安装、真实企业权限验证或外部网络依赖，必须拆成 downstream child，不得在当前 plan 下静默扩 scope。
- 若实现过程中出现以下任何一种越界，必须立即回退到本 plan 的边界重收口：
  - 试图在 CLI 中开放 React
  - 试图在简单模式默认推荐 degraded 风格
  - 试图把 `will_change_on_confirm` 当持久化真值
  - 试图把跨栈 fallback 偷换成“只切 Provider”
