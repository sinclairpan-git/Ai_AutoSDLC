---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
---
# 实施计划：Frontend P2 Multi Theme Token Governance Baseline

**编号**：`148-frontend-p2-multi-theme-token-governance-baseline` | **日期**：2026-04-16 | **规格**：specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md

## 概述

`148` 的目标是把前端后续主线的第二条 child formalize 为 Track B baseline：先冻结 single-truth boundary 与 implementation decomposition，再在后续批次把 theme governance runtime 物化为 models、artifacts、validator/guardrails、ProgramService/CLI handoff。顺序保持为：先 formalize Track B truth 并通过对抗专家评审，再进入 runtime 切片，最后把 theme truth 接入 program/global truth 与 Track C/D。

## 技术背景

**语言/版本**：当前批次为 Markdown formal docs；后续 runtime 仍基于 Python 3.11 与 `ai_sdlc` CLI  
**主要依赖**：`017` generation constraints、`073` solution/style truth、`145` Track B planning boundary、`147` page-ui schema handoff、`ProgramService` / `verify constraints` / CLI surfaced diagnostics  
**存储**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/*`；后续 runtime 计划写入 `src/ai_sdlc/models/`、`src/ai_sdlc/generators/`、`src/ai_sdlc/core/`、`src/ai_sdlc/cli/` 与 `tests/`  
**测试**：当前批次使用 `python -m ai_sdlc adapter status`、`python -m ai_sdlc run --dry-run`、`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/148-frontend-p2-multi-theme-token-governance-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`；其中 `close-check / truth sync` 在本批只刷新 planning-layer baseline，不代表 runtime 已落地；后续 runtime 批次补 `pytest` / `ruff` / CLI integration  
**目标平台**：frontend theme/token governance truth、AI-SDLC program truth、Track C/D shared handoff surface  
**约束**：

- 当前批次只允许 docs-only formal freeze 与对抗专家评审，不进入 `src/` / `tests/`
- `073` 的 `style_pack_manifest` 与 `provider_manifest.style_support_matrix` 仍是上游 style truth，不得复制
- `147` 的 schema anchor 仍是结构锚点，不得重新定义
- `017` 的 token floor 仍生效，不得通过 custom theme token 绕开
- 不提前混入 `quality platform`、`cross-provider consistency`、`provider expansion`
- 不开放自由样式编辑器或 prompt-only theme override

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值分层 | `017` 负责 token floor，`073` 负责 provider/style truth，`147` 负责 schema truth，`148` 只负责 theme/token governance |
| 先 formalize 再实现 | 当前批次先冻结 Track B baseline 与 expert-review gate，再进入 runtime |
| AI-SDLC 主链接入 | runtime 切片必须进入 `models -> generators -> core -> ProgramService/CLI -> verify constraints -> truth sync`，不得另起平行流水线 |
| UX 诚实边界 | style editor 只允许受控操作面；不得把自由 CSS/裸值输入包装成“主题治理” |
| 范围收口 | 当前批次不改 provider roster、不跑 quality execution、不做 cross-provider certification |

## 项目结构

### 文档结构

```text
specs/148-frontend-p2-multi-theme-token-governance-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 计划中的源码结构

```text
src/ai_sdlc/models/
├── frontend_theme_token_governance.py
└── __init__.py
src/ai_sdlc/generators/
├── frontend_theme_token_governance_artifacts.py
└── __init__.py
src/ai_sdlc/core/
├── frontend_theme_token_governance.py
├── program_service.py
└── verify_constraints.py
src/ai_sdlc/cli/
├── sub_apps.py
└── program_cmd.py
tests/unit/
├── test_frontend_theme_token_governance_models.py
├── test_frontend_theme_token_governance_artifacts.py
├── test_frontend_theme_token_governance.py
├── test_program_service.py
└── test_verify_constraints.py
tests/integration/
├── test_cli_rules.py
└── test_cli_program.py
USER_GUIDE.zh-CN.md
```

### 计划中的 canonical artifact roots

```text
governance/frontend/theme-token-governance/
├── theme-governance.manifest.yaml
├── handoff.schema.yaml
├── style-editor-boundary.yaml
├── override-policy.yaml
└── token-mappings/
    └── <mapping_id>.yaml
```

## 阶段计划

### Phase 0：Track B truth freeze 与对抗专家评审

**目标**：冻结 `148` 的问题定义、single-truth boundary、runtime decomposition，并通过 UX / AI-Native framework 两类对抗评审。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`development-summary.md`。  
**验证方式**：formal docs review、专家评审结论、`adapter status`、`run --dry-run`、`verify constraints`、`close-check`、`truth sync`、`git diff --check`。  
**回退方式**：仅回退 `specs/148/...` 与 `program-manifest.yaml` 的当前 planning 改动。  

### Phase 1：theme governance model baseline slice

**目标**：建立 Track B 的最小结构化模型，承载 theme governance set、token mapping、custom override envelope 与 style editor boundary contract。  
**产物**：`src/ai_sdlc/models/frontend_theme_token_governance.py`、`tests/unit/test_frontend_theme_token_governance_models.py`、`src/ai_sdlc/models/__init__.py`。  
**验证方式**：model-focused unit tests。  
**回退方式**：回退 theme governance models 增量，不影响 `073/147` 既有 runtime。  

### Phase 2：artifact materialization 与 validator/guardrails slice

**目标**：把 Track B 结构 truth 物化为 canonical artifacts，并对 schema anchor、provider support、override boundary 与 token floor 进行 machine-verifiable 校验。  
**产物**：`frontend_theme_token_governance_artifacts.py`、`frontend_theme_token_governance.py` core validator、对应 unit tests。  
**验证方式**：artifact + validator focused unit tests、`verify constraints`。  
**回退方式**：回退 generators/core validator 增量，不回退上游 truth。  

### Phase 3：ProgramService / CLI / program truth handoff

**目标**：让 ProgramService 与 CLI 能 surfaced theme governance handoff，并将 Track B 真值接入后续 program/global truth 与 downstream Track C/D。  
**产物**：`ProgramService` handoff methods、CLI commands、`verify_constraints` integration、文档更新。  
**验证方式**：ProgramService unit tests、CLI integration tests、`truth sync`、`close-check`。  
**回退方式**：回退 handoff/CLI/verify 增量，不影响 models/artifacts core。  

## 工作流计划

### 工作流 A：single-truth boundary freeze

**范围**：定义 `017/073/147/148` 各自负责的 truth layer，避免 style/theme/schema/generation 互相吞并。  
**影响范围**：`148/spec.md` 的问题定义、FR/SC、实体与 non-goals。  
**验证方式**：上游文档对账 review + 对抗专家评审。  
**回退方式**：回退 `148/spec.md` 中的边界描述。  

### 工作流 B：theme mapping model 与 custom override policy

**范围**：定义 theme governance set、token mapping、custom override envelope、style editor boundary contract。  
**影响范围**：后续 Track B models 与 artifacts 的字段语义。  
**验证方式**：model unit tests + boundary wording review。  
**回退方式**：回退 models/plan 中的字段定义，不影响 `073/147` 原 truth。  

### 工作流 C：artifact / validator / guardrails

**范围**：把 Track B truth materialize 到固定 artifact root，校验 schema anchor、provider style support、override legality 与 token floor。  
**影响范围**：`governance/frontend/theme-token-governance/theme-governance.manifest.yaml`、`governance/frontend/theme-token-governance/handoff.schema.yaml`、`governance/frontend/theme-token-governance/style-editor-boundary.yaml`、`governance/frontend/theme-token-governance/override-policy.yaml`、`governance/frontend/theme-token-governance/token-mappings/*.yaml`、`verify constraints`、validator diagnostics。  
**验证方式**：artifact/validator tests + `verify constraints`。  
**回退方式**：回退 generators/core/verify 增量。  

### 工作流 D：ProgramService / CLI / downstream handoff

**范围**：为 Track C/D 暴露 theme governance handoff，并为 operator 提供只读 diagnostics 与受控执行入口。  
**影响范围**：`ProgramService`、CLI、`USER_GUIDE.zh-CN.md`、program truth writeback。  
**验证方式**：ProgramService unit tests、CLI integration tests、`truth sync`。  
**回退方式**：回退 CLI / handoff 增量，不回退 Track B core data models。  

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
|------------|----------------|------------------------------|
| `017` generation floor | minimal token / naked-value rules、generation exceptions 的底线控制面 | 不得升级成完整 theme governance；不得直接定义 provider style support |
| `073` solution truth | style pack inventory、provider style support、requested/effective solution snapshot | 不得重新定义 schema anchor；不得承载 Track B custom override 规则全集 |
| `147` schema truth | page/ui schema、render slot、section anchor、schema versioning | 不得定义 theme pack、style support 或 custom token override policy |
| `148` theme governance | token mapping、custom override boundary、style editor boundary、theme handoff surface | 不得重写 `073` style support matrix；不得吞并 quality execution 或 provider expansion |
| Track C `quality platform` | visual/a11y/interaction execution 与质量证据 | 不得回写 theme truth；不得另建 style editor boundary |
| Track D `cross-provider consistency` | shared verdict、diff surface、consistency certification | 不得重写 schema/theme/generation floor；不得顺手扩 provider roster |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `017/073/147/148` 边界清晰 | formal docs consistency review | 对抗专家评审 |
| style support 唯一真值来源保持不变 | future validator tests | `verify constraints` |
| token mapping 必须绑定 schema anchor | future model/validator tests | ProgramService handoff review |
| style editor 边界保持受控 | CLI/program diagnostics review | UX 专家评审 |
| Track B planning layer 可进入 global truth | `program truth sync --execute --yes`（Phase 0，仅刷新 formal baseline） | `workitem close-check` |
| Track B runtime 可进入 global truth | `program truth sync --execute --yes`（Batch 7 之后，再次按 runtime 口径刷新） | `workitem close-check`（Batch 7 之后） |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 首批 style editor surface 是否允许直接写入 | 已决议：v1 只允许只读诊断 + 结构化 proposal；直接写入面后移 | 不阻塞 |
| Track B 首批是否引入额外 theme variant 概念 | 已决议：v1 仅复用 `073` 的五套 style pack，不新增 variant truth | 不阻塞 |
| custom override precedence 是否采用 `global -> page -> section -> slot` | 已决议：采用该顺序，并作为 Track C/D 直接消费的默认规则 | 不阻塞 |

## 实施顺序建议

1. 先 formalize `148`，并完成 UX / AI-Native framework 对抗评审
2. 再进入 theme governance model slice，冻结 token mapping 与 custom override envelope
3. 然后实现 artifact materialization、validator 与 `verify constraints` 接入
4. 最后接 ProgramService / CLI handoff、truth refresh 与 downstream Track C/D consumption
