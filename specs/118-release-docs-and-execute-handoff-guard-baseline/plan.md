---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "README.md"
  - "packaging/offline/README.md"
  - "docs/releases/v0.6.0.md"
  - "docs/pull-request-checklist.zh.md"
---
# 实施计划：Release Docs And Execute Handoff Guard Baseline

**编号**：`118-release-docs-and-execute-handoff-guard-baseline` | **日期**：2026-04-13 | **规格**：specs/118-release-docs-and-execute-handoff-guard-baseline/spec.md

## 概述

`118` 的交付目标是把两类仍停留在规则文本与 backlog 里的缺口，收敛为 repo 内可复核的 bounded guard surface：一类是 `tasks.md` 缺失 / 阶段未进入 execute 时的 execute handoff guard；另一类是 `v0.6.0` release 入口文档一致性 sweep。推荐做法是尽量复用现有 `execute_authorization` 与 `verify_constraints` 入口，而不是引入新的大块命令。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：现有 `execute_authorization`、`verify_constraints`、`status` CLI 与 repo Markdown docs  
**存储**：`specs/<WI>/`、`docs/framework-defect-backlog.zh-CN.md`、固定 release entry docs  
**测试**：`pytest` unit + integration  
**目标平台**：bounded status / verification surfaces  
**约束**：
- execute handoff guard 不做聊天意图推断，只做 repo-truth preflight
- release sweep 固定核对 6 个入口文件，不扩成全文索引器
- backlog 回填必须与本次实现同条收口链完成

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | execute handoff 只看 `tasks.md` 与阶段真值；release sweep 只看固定入口文档 |
| 流程违约必须可审计 | `FD-2026-04-07-002` 在本批正式回填 closed，并更新 backlog 顶部摘要 |
| 最小改动面 | 只触达 `execute_authorization`、`verify_constraints`、`status` 与 release 文档入口 |

## 项目结构

### 文档结构

```text
specs/118-release-docs-and-execute-handoff-guard-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/
├── execute_authorization.py      # 现有 execute truth，补更明确的 handoff detail
└── verify_constraints.py         # 新增 release docs consistency sweep

src/ai_sdlc/telemetry/
└── readiness.py                  # 若需补 status --json surface

src/ai_sdlc/cli/
└── commands.py                   # status text surface

tests/unit/
├── test_execute_authorization.py
└── test_verify_constraints.py

tests/integration/
└── test_cli_status.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 `118` formal docs 与 `FD-2026-04-07-001/002/003` 对齐  
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `118` formal carrier  

### Phase 1：Execute handoff guard

**目标**：让 `tasks.md` 缺失 / 未进入 execute 的 active work item 稳定暴露 docs-only / review-to-decompose truth  
**产物**：`execute_authorization` detail / reason surface 更新 + tests  
**验证方式**：focused unit/integration tests  
**回退方式**：回退 execute handoff detail，不影响 `117` 的 artifact target / backlog breach guard  

### Phase 2：Release docs consistency sweep + backlog backfill

**目标**：让 release 入口文档一致性进入 `verify constraints`，并回填 `FD-2026-04-07-002` 为 closed  
**产物**：release docs sweep、README / 发布约定 / checklist 对齐、backlog 状态回填  
**验证方式**：focused unit tests + `verify constraints`  
**回退方式**：回退 sweep 与文档入口改动；保留 execute handoff guard  

## 工作流计划

### 工作流 A：Execute Handoff Truth

**范围**：`tasks.md` 存在性、阶段真值、bounded detail wording  
**影响范围**：`execute_authorization`、`status`  
**验证方式**：unit + integration  
**回退方式**：helper/detail 独立回退  

### 工作流 B：Release Entry Consistency

**范围**：固定 release 入口文档的版本号与平台资产分工  
**影响范围**：`verify_constraints` + README / 发布约定 / checklist / backlog  
**验证方式**：unit + `verify constraints`  
**回退方式**：独立回退，不影响 execute handoff truth  

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| 缺 `tasks.md` 时必须停在 docs-only / review | `test_execute_authorization.py` | `test_cli_status.py` |
| 未进入 execute 时不得被视为 ready | `test_execute_authorization.py` | `test_cli_status.py` |
| release 入口文档缺失 `v0.6.0` / 资产口径时阻断 | `test_verify_constraints.py` | `uv run ai-sdlc verify constraints` |
| `FD-2026-04-07-002` backlog 真值回填 | 文档 diff 对账 | `verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| release sweep 是否需要抽独立 helper | 不阻塞；先直接落在 `verify_constraints` | Phase 2 |

## 实施顺序建议

1. 先冻结 `118` formal docs
2. 先写 execute handoff guard 与 release sweep 的失败测试
3. 实现最小 guard 与文档对齐
4. 回填 backlog 状态并完成 focused verification
