---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md"
---
# 实施计划：Frontend P3 Modern Provider Expansion Baseline

**编号**：`151-frontend-p3-modern-provider-expansion-baseline` | **日期**：2026-04-16 | **规格**：specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md

## 概述

本计划先完成 docs-only planning freeze，把顶层前端设计里的 Track E `modern provider expansion` 一次性 materialize 成 canonical child truth；当前已继续进入 runtime slices 1-3，并落地 `provider admission models + provider expansion artifacts + validator/policy + ProgramService/verify/CLI + global truth proof`。现阶段交付物包括 formal docs、provider expansion models、artifact generator、validation helpers、`verify_constraints` 接线、`ProgramService` handoff、CLI handoff 与 truth snapshot regression；当前不再需要继续做 Track E capability census。

## 技术背景

**语言/版本**：Python 3.11 + Markdown；运行时实现继续使用 `ai_sdlc` 现有 Pydantic model / artifact generator 模式
**主要依赖**：`ai_sdlc workitem init` 生成的 canonical scaffold、顶层设计文档、`073/150` formal truth  
**存储**：`specs/151-frontend-p3-modern-provider-expansion-baseline/`  
**测试**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**目标平台**：Ai_AutoSDLC 仓库的 formal truth / global truth / downstream workitem planning  
**约束**：
- 当前只允许落地 Track E runtime slice 1 所需的 `models / generators / focused unit tests`
- 不重写 `073` provider/style 第一阶段 truth 或 `150` consistency gate truth
- 不把 Track E 与真实 provider runtime/adapter 落地混写
- 必须固定 artifact root、truth surfacing record 与 close-out truth sync 门禁

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 所有 formal docs 只落在 `specs/151-frontend-p3-modern-provider-expansion-baseline/`，外部 design docs 只作为 reference-only 输入 |
| 先 formalize 再实现 | formal baseline 已先冻结；当前实现只进入 runtime slice 1，不越过后续 validator / program surfacing slice |
| 诚实区分 delivered / deferred | `151` 明确隔离已落地的 models/artifacts 与仍待实现的 validator / ProgramService / verify / truth sync 接入 |
| 有界变更 | 当前批次只新增 provider expansion models / generators / focused tests，不改 adapter/runtime UI |

## 项目结构

### 文档结构

```text
specs/151-frontend-p3-modern-provider-expansion-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
src/ai_sdlc/models/frontend_provider_expansion.py
src/ai_sdlc/generators/frontend_provider_expansion_artifacts.py
src/ai_sdlc/core/frontend_provider_expansion.py
src/ai_sdlc/core/verify_constraints.py
src/ai_sdlc/core/program_service.py
tests/unit/test_frontend_provider_expansion_models.py
tests/unit/test_frontend_provider_expansion_artifacts.py
future runtime slices
└── none within 151 planned decomposition
```

### 计划中的 canonical artifact roots

```text
governance/frontend/provider-expansion/
├── provider-expansion.manifest.yaml
├── handoff.schema.yaml
├── truth-surfacing.yaml
├── choice-surface-policy.yaml
├── react-exposure-boundary.yaml
└── providers/
    └── <provider_id>/
        ├── admission.yaml
        ├── roster-state.yaml
        ├── certification-ref.yaml
        └── provider-certification-aggregate.yaml
```

## 阶段计划

### Phase 0：Track E positioning 与 upstream gate freeze

**目标**：把顶层设计里 Track E 的问题定义、顺序与上游 gate 一次性拉平成 formal planning truth，并明确 Track E 不等于真实 provider runtime 落地。  
**产物**：`spec.md` 的问题定义、范围、FR/SC 与 capability decomposition  
**验证方式**：顶层设计、`145/073/150` 对账 review  
**回退方式**：仅回退 `spec.md / plan.md / tasks.md` 的当前 planning truth 改动。  

### Phase 1：provider admission / choice-surface / react boundary freeze

**目标**：冻结 provider certification aggregation、admission states、choice-surface visibility、React stack/binding visibility、artifact root、truth surfacing 与 Track E handoff 的 canonical boundary。  
**产物**：`spec.md` 的 admission/choice-surface/react model、`plan.md` 的 runtime slices 与 artifact/truth-surface/consumer contract、`tasks.md` 的 docs-only freeze batch  
**验证方式**：Track E decomposition review；是否出现 gate bypass / runtime leakage 检查  
**回退方式**：仅回退 `151` 文档中的 Track E 模型与 handoff 描述，不影响既有 runtime truth。  

### Phase 2：docs-only verification 与 truth handoff readiness

**目标**：完成当前 planning baseline 的验证、归档与 close-ready summary，使全局真值可以把 Track E 视为 canonical planning input。  
**产物**：`task-execution-log.md`、`development-summary.md`  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline`、`git diff --check`、`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`  
**回退方式**：仅回退 `151` 文档与可选 truth snapshot 改动。  

### Phase 3：runtime slice 1 - admission models 与 artifact materialization

**目标**：把 `151` 冻结的 provider admission / certification aggregation / truth surfacing / React boundary contract materialize 成可测试的 Pydantic models 与 artifact generator。
**产物**：`src/ai_sdlc/models/frontend_provider_expansion.py`、`src/ai_sdlc/generators/frontend_provider_expansion_artifacts.py`、对应 unit tests
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_frontend_provider_expansion_models.py tests/unit/test_frontend_provider_expansion_artifacts.py`、`git diff --check`
**回退方式**：仅回退 provider expansion runtime slice 1 的代码与测试，不影响已冻结 formal baseline。

### Phase 4：runtime slice 2 - validator/policy 与 ProgramService/verify hookup

**目标**：将 provider expansion truth 接入独立 validation helper、`verify_constraints` scoped verification、`ProgramService` handoff，使 `151` 的 consumer contract 不再只停留在 artifact 层。
**产物**：`src/ai_sdlc/core/frontend_provider_expansion.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/program_service.py`、对应 unit tests
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/test_program_service.py::test_build_frontend_provider_expansion_handoff_blocks_when_solution_snapshot_missing tests/unit/test_program_service.py::test_build_frontend_provider_expansion_handoff_uses_latest_solution_snapshot_and_provider_diagnostics tests/unit/test_verify_constraints.py::test_151_frontend_provider_expansion_verification_surfaces_missing_provider_admission_artifact tests/unit/test_verify_constraints.py::test_151_frontend_provider_expansion_verification_blocks_react_snapshot_while_boundary_hidden`、`git diff --check`
**回退方式**：仅回退 runtime slice 2 的校验与 handoff 接线，不影响已落地 models/artifacts。

### Phase 5：runtime slice 3 - CLI handoff 与 global truth proof

**目标**：把 provider expansion handoff 暴露到 CLI，并用 truth snapshot regression 证明 `151` verify blockers 会进入 global truth release gating。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`tests/unit/test_program_service.py`
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_cli_program.py::test_program_provider_expansion_handoff_blocks_without_solution_snapshot tests/integration/test_cli_program.py::test_program_provider_expansion_handoff_surfaces_provider_and_react_visibility_diagnostics tests/unit/test_program_service.py::test_build_truth_snapshot_blocks_release_scope_on_151_provider_expansion_verify_gap`、`git diff --check`
**回退方式**：仅回退 runtime slice 3 的 CLI/proof 接线，不影响已落地 runtime truth。

## 工作流计划

### 工作流 A：Track E positioning 与 boundary honesty

**范围**：明确顶层设计中 Track E 的独立职责，以及与 `073/150` 的边界。  
**影响范围**：`151/spec.md` 的问题定义、范围、FR/SC 与 decomposition。  
**验证方式**：design/source cross-check。  
**回退方式**：回退 `151/spec.md` 的 positioning 段落。  

### 工作流 B：admission / choice-surface / react handoff

**范围**：冻结 provider certification aggregation、admission states、choice-surface visibility、React stack/binding visibility、artifact root、truth surfacing 与最小 consumer contract。  
**影响范围**：`151/spec.md`、`151/plan.md`、`151/tasks.md`。  
**验证方式**：Track E policy review；是否出现 gate bypass / scope leakage 检查。  
**回退方式**：回退 Track E handoff 与 runtime slice 描述，不影响既有 workitem。  

### 工作流 C：verification 与 truth handoff

**范围**：完成 docs-only verification、execution log、expert review 结论与 development summary，确保 `151` 可以被 global truth 诚实消费。  
**影响范围**：`151/task-execution-log.md`、`151/development-summary.md`。  
**验证方式**：`verify constraints`、`workitem close-check`、`git diff --check`、`program truth sync --dry-run`、`program truth sync --execute --yes`、`program truth audit`。  
**回退方式**：回退 execution log / development summary，不影响 spec truth。  

### 工作流 D：runtime slice 1 materialization

**范围**：实现 provider certification aggregation、provider admission bundle、truth surfacing record、React exposure boundary 与 artifact generator。
**影响范围**：`src/ai_sdlc/models/frontend_provider_expansion.py`、`src/ai_sdlc/generators/frontend_provider_expansion_artifacts.py`、对应 tests。
**验证方式**：focused unit tests + `git diff --check`。
**回退方式**：回退 runtime slice 1 代码，不影响 docs-only baseline。

### 工作流 E：runtime slice 2 consumer hookup

**范围**：实现 provider expansion validation helper，并接入 `verify_constraints` 与 `ProgramService` 的最小消费链路。
**影响范围**：`src/ai_sdlc/core/frontend_provider_expansion.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/program_service.py`、对应 tests。
**验证方式**：focused unit tests + `git diff --check` + `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`。
**回退方式**：回退 runtime slice 2 代码，不影响 slices 0-1 truth。

### 工作流 F：runtime slice 3 CLI and truth proof

**范围**：新增 `program provider-expansion-handoff` CLI surface，并用 truth snapshot regression 证明 verify blockers 会进入 release capability blocking refs。
**影响范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`tests/unit/test_program_service.py`。
**验证方式**：focused integration/unit tests + `git diff --check`。
**回退方式**：回退 runtime slice 3 CLI/proof 代码，不影响 slices 0-2 truth。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Track E 与 Track D / 073 边界清晰 | design/source cross-check | `151/spec.md` scope / non-goals review |
| provider admission / choice-surface / React boundary 语义清晰 | `151/spec.md` decomposition review | UX / AI-Native expert review |
| provider-level aggregation / artifact root / truth surfacing contract 已冻结 | artifact root review | `program-manifest.yaml` + truth handoff review |
| ProgramService / CLI / verify 最小 consumer contract 已冻结 | `151/spec.md` FR review | handoff consumer review |
| 当前 planning baseline 可被 close-check 与 global truth 消费 | `python -m ai_sdlc workitem close-check --wi ...` | `python -m ai_sdlc program truth sync --execute --yes` + `python -m ai_sdlc program truth audit` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 首批 modern provider roster 是否只允许 advanced-only 扩张 | 当前先冻结状态机与聚合规则，不指定具体 provider 名单 | 不阻塞 `151` |
| public-visible provider 在 chooser 中的呈现样式是否需要额外 badge 文案 | 当前先冻结状态与 consumer contract，不冻结 UI copy | 不阻塞 `151` |
| React exposure 是否在 Track E runtime 中先走 advanced-only 试点 | 当前先冻结升级路径，不在本工单决定真实 rollout 批次 | 不阻塞 `151` |

## 实施顺序建议

1. 先 formalize Track E positioning、provider aggregation/admission states、choice-surface visibility 与 React stack/binding boundary
2. 再落地 Track E runtime models 与 roster/choice-surface artifacts
3. 然后接入 validator/policy、ProgramService/CLI/verify/global truth surfacing
4. 最后再进入真实 provider runtime / adapter 扩张
