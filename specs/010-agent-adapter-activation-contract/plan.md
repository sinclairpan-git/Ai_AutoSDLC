---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/USER_GUIDE.zh-CN.md"
---
# 实施计划：Agent Adapter Activation Contract

**编号**：`010-agent-adapter-activation-contract` | **日期**：2026-04-02 | **规格**：specs/010-agent-adapter-activation-contract/spec.md

## 概述

本计划处理的是框架入口层的 P0 缺陷，而不是单一 adapter 模板或 IDE 检测顺序的小修补。当前实现只具备“自动探测 IDE + 落盘 Markdown 提示文件 + 记录 `adapter_applied`”的能力，但不具备“选择真实 AI 代理入口”“证明约束已激活”“在未激活时阻断误导性成功语义”的正式合同。

因此，本计划的目标是建立统一的 `Agent Adapter Activation Contract`：

- 先区分 `Editor Host` 与 `Agent Target`
- 再引入交互式 target 选择与显式参数选择
- 再引入 activation state / evidence / support tier
- 再引入 activation gate，避免把 `installed` 误报成 `activated`

该计划不是直接实现全部代码，而是先把后续实现必须遵守的产品合同、状态模型、CLI 入口和测试基线正式写入 `specs/010/...`。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Pydantic models、Markdown adapter templates  
**主要依赖**：现有 `ai-sdlc` CLI、project config/state 落盘机制、adapter template bundle、用户指南与 backlog  
**现有基础**：

- [`src/ai_sdlc/integrations/ide_adapter.py`](../../src/ai_sdlc/integrations/ide_adapter.py) 当前负责 auto-detect + 写入 adapter 模板 + 更新 `project-config.yaml`
- [`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py) 当前在 `init` 与部分入口中调用 adapter apply，但没有 activation contract
- [`src/ai_sdlc/cli/cli_hooks.py`](../../src/ai_sdlc/cli/cli_hooks.py) 当前只负责已初始化项目上的 adapter 幂等 apply
- [`src/ai_sdlc/models/project.py`](../../src/ai_sdlc/models/project.py) 当前只持有 `detected_ide / adapter_applied / adapter_version / adapter_applied_at`
- `src/ai_sdlc/adapters/*/AI-SDLC.md` 当前只是提示代理执行 `run --dry-run`

**目标平台**：AI-SDLC 框架仓库自身，面向 `Codex / Claude Code / Cursor / VS Code / generic` 的入口接入合同  
**主要约束**：

- 选择器目标必须是 `Agent Target`，不是 `Editor Host`
- 交互式选择只允许默认聚焦，不允许自动确认
- 非交互环境必须 deterministic，不允许卡死等待交互
- `installed != activated` 必须成为单一真值
- 当前 file-based adapter 场景不应被冒充为原生强验证接入
- backward compatibility 只能保守迁移，不能误判旧项目已激活

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前先锁定入口层 activation contract，不顺手扩张到其他框架能力 |
| MUST-2 关键路径可验证 | 所有状态、提示与 gate 都必须可测试，重点覆盖 mixed host、installed-only、non-interactive |
| MUST-3 范围声明与回退 | 明确只处理 adapter target / activation / gate 的 formal 基线，不引入插件原生 API 假承诺 |
| MUST-4 状态落盘 | activation state、evidence、support tier 必须进入项目配置或等价 formal 状态面 |
| MUST-5 产品代码与开发框架隔离 | 此 work item 只处理框架入口合同，不改写前端治理、UI Kernel 等其他产品域规则 |

## 项目结构

### 文档结构

```text
specs/010-agent-adapter-activation-contract/
├── spec.md
├── plan.md
└── tasks.md
```

### 主要实现触点

```text
src/ai_sdlc/
├── integrations/
│   └── ide_adapter.py
├── cli/
│   ├── commands.py
│   ├── cli_hooks.py
│   └── main.py
├── models/
│   └── project.py
├── core/
│   └── config.py
└── adapters/
    ├── codex/AI-SDLC.md
    ├── claude_code/AI-SDLC.md
    ├── vscode/AI-SDLC.md
    ├── cursor/rules/ai-sdlc.md
    └── generic/ide-hint.md

tests/
├── unit/test_ide_adapter.py
└── integration/test_cli_run.py
```

### 推荐新增的内聚代码面

```text
src/ai_sdlc/
├── integrations/
│   ├── agent_target.py          # target choice / detection / mapping
│   └── adapter_activation.py    # activation state / evidence / gate helpers
├── cli/
│   └── adapter_cmd.py           # select / status / activate CLI surface
└── models/
    └── project.py               # activation-related config extensions
```

## 开始执行前必须锁定的阻断决策

- `Editor Host != Agent Target`
- `adapter installed != governance activated`
- `run --dry-run` 成功不等于 activation 成功
- adapter 模板只是 activation surface 的一部分，不是接管成功的证据
- mixed host 场景必须优先选择插件代理，而不是外层编辑器
- 非交互环境必须通过显式参数或 deterministic fallback 决定 target

未锁定上述决策前，不得进入代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| selection contract | 定义 host/target 分离、选择器列表、显式参数与 fallback 语义 | 不得把编辑器宿主误写成最终约束消费目标 |
| activation model | 定义 state/evidence/tier/gate | 不得把文件存在、文件读取、dry-run 成功混写成同一状态 |
| CLI surface | 暴露 `select / status / activate` 与更正后的 `init / run / status` 口径 | 不得继续沿用误导性“已接管”表述 |
| adapter templates | 提供激活提示与 target-specific guidance | 不得继续把 `run --dry-run` 视为唯一前置动作 |
| migration path | 保守迁移旧项目配置 | 不得把历史 adapter 元数据直接升级成 activated |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：把入口层 P0 问题正式冻结为 `010` canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/010/...` 文档改动。

### Phase 1：Selection and state model freeze

**目标**：锁定 `Editor Host / Agent Target / Activation State / Support Tier` 的正式模型。  
**产物**：state model、selection contract、migration baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现，仅回退 formal baseline。

### Phase 2：CLI surface and activation handshake design

**目标**：锁定 `init` 选择器、`adapter select/status/activate` 以及 activation handshake 的 CLI 合同。  
**产物**：CLI surface baseline、interaction rules、non-interactive fallback baseline。  
**验证方式**：命令语义对账。  
**回退方式**：不触发代码实现。

### Phase 3：Activation gate, templates, and migration baseline

**目标**：锁定 activation gate、adapter 模板重写、旧项目保守迁移与测试面。  
**产物**：gate baseline、template rewrite baseline、tests matrix。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Selection contract freeze

**范围**：固定列表、交互聚焦、显式参数、mixed host 判定。  
**影响范围**：`ide_adapter` 检测逻辑、`init` 交互、project config target truth。  
**验证方式**：文档对账 + mixed host case review。  
**回退方式**：不影响现有产品数据结构。

### 工作流 B：Activation state and gate freeze

**范围**：`selected / installed / acknowledged / activated`、support tier、activation gate。  
**影响范围**：`status / run --dry-run / doctor / adapter status` 的状态语义。  
**验证方式**：状态表与门禁语义对账。  
**回退方式**：不进入实现。

### 工作流 C：Migration and template rewrite freeze

**范围**：旧项目迁移规则、adapter 模板重写、installed-only 语义、回归矩阵。  
**影响范围**：`project-config.yaml` 迁移、adapter bundle、USER_GUIDE。  
**验证方式**：兼容性规则审阅。  
**回退方式**：不写入新配置字段。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| mixed host target correctness | 设计对账 | 单元/集成测试矩阵 |
| installed vs activated truth | 状态模型审阅 | `status/run/doctor` 文案回归 |
| non-interactive determinism | CLI 合同对账 | 集成测试 |
| old project migration conservatism | 配置迁移审阅 | 回归测试 |
| activation gate honesty | 门禁语义对账 | 人工复核 + 测试 |

## 已锁定决策

- 当前问题是入口层 P0 缺陷，不是 adapter 模板文案小问题
- 必须新增 activation contract，不能继续只靠 Markdown 文件
- 交互选择器的列表固定为五项，不再按“编辑器 + 插件”做笛卡尔组合枚举
- Compatibility / legacy 口径不在本 work item 内扩展为第二套规则；本 work item 只关注 adapter activation 真值
- 旧项目迁移默认从 `installed` 起步，严禁误推断 `activated`

## 实施顺序建议

1. 先冻结 `010` formal spec/plan/tasks，明确当前要修的是“入口接管合同”，不是“adapter 文件再多装一个”。
2. 再冻结 `Editor Host / Agent Target / Activation State / Support Tier / Gate Policy` 的正式对象模型。
3. 再冻结 `init` 交互选择、显式参数、non-interactive fallback 与 activation handshake 的 CLI 合同。
4. 最后再冻结 adapter 模板重写、旧项目迁移与 mixed host / installed-only / non-interactive 的回归矩阵。
