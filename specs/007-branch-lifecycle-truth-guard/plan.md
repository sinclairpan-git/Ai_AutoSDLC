# 实施计划：Branch Lifecycle Truth Guard

**编号**：`007-branch-lifecycle-truth-guard` | **日期**：2026-03-31 | **规格**：specs/007-branch-lifecycle-truth-guard/spec.md

## 概述

本计划承接 `FD-2026-03-31-002`。实现目标不是“自动清理旧分支”，而是先把 branch/worktree lifecycle 变成仓库的正式真值面：先补 inventory 与分类，再补 close-out disposition truth，再把 branch lifecycle 接到 `verify constraints`、`status --json` 与 `doctor`，最后收紧规则、模板和用户文档。

本计划默认保持 **read-only first**。任何自动 merge / delete / prune / archive 都不在首期范围内。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Git CLI、Typer、Rich、pytest、JSON  
**现有基础**：`GitClient` 已有 Git 写命令互斥与基础 branch 操作；`close_check.py`、`verify_constraints.py`、`telemetry/readiness.py`、`doctor_cmd.py` 已分别提供 close、verify、status/doctor 的 bounded surface 基础  
**目标平台**：框架仓库自迭代主路径  
**主要约束**：
- 先落 formal `spec.md / plan.md / tasks.md`，再讨论实施
- branch inventory 默认 read-only
- disposition 必须显式，不得从聊天结论推断
- `status --json` / `doctor` 不得引入新写副作用

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 首期只做 inventory、close truth、bounded read surfaces，不做自动清理 |
| MUST-2 关键路径可验证 | inventory、close-check、verify、status/doctor 都要求 unit/integration 正反测试 |
| MUST-3 范围声明与回退 | branch inventory、close surface、verify surface、bounded reads、rules/docs 分阶段推进 |
| MUST-4 状态落盘 | 不依赖聊天结论，branch disposition 真值回到 execution-log / work item close-out |
| MUST-5 产品代码隔离 | 规则、模板、CLI、core helper 各自落位，不混成临时脚本 |

## 项目结构

### 文档结构

```text
specs/007-branch-lifecycle-truth-guard/
├── spec.md
├── plan.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/
├── branch/
│   └── git_client.py                 # branch/worktree inventory primitives
├── core/
│   ├── branch_inventory.py           # lifecycle-aware branch inventory (new)
│   ├── workitem_traceability.py      # WI <-> branch association reuse
│   ├── close_check.py                # close blockers for unresolved WI branches
│   └── verify_constraints.py         # branch lifecycle governance surface
├── telemetry/
│   └── readiness.py                  # bounded branch inventory summary
└── cli/
    ├── commands.py                   # status --json
    ├── doctor_cmd.py                 # doctor readiness rows
    └── workitem_cmd.py               # read-only branch-check
```

## 开始编码前必须锁定的阻断决策

- `scratch` 分支允许存在，但必须有 disposition
- `archived` 是正式 disposition，不等于 `merged`
- 只有当前 work item 关联分支可形成 close blocker
- `status --json` / `doctor` 只读，不做 Git 清理动作

未锁定上述决策前，不得进入 inventory 之后的 implementation task。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| branch inventory | 列 branch/worktree、算 divergence、做 lifecycle classification | 不得 auto-delete / auto-merge |
| close truth | work-item branch association、disposition parsing、close blockers | 不得用聊天或计划文本推断“已 merged” |
| governance/readiness | verify constraints、status --json、doctor 的 bounded branch surface | 不得触发 fetch/prune/rebuild |
| rules/templates/docs | lifecycle kinds、disposition policy、execution-log close markers、用户文档 | 不得把 branch close-out 继续写成“可选清理” |

## 阶段计划

### Phase 0：Formal work item freeze

**目标**：把 backlog 缺陷与 superpowers plan 收敛成正式 `007` work item 真值。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `verify constraints`。  
**回退方式**：只改文档，不进入实现。

### Phase 1：Read-only inventory baseline

**目标**：补齐 branch/worktree 读取、分类和 divergence 计算。  
**产物**：`git_client.py`、`branch_inventory.py`、对应 unit tests。  
**验证方式**：inventory unit tests。  
**回退方式**：保持 read-only，不接 close surface。

### Phase 2：Close-out disposition truth

**目标**：把 work item 关联 branch/worktree 的 disposition 与 close truth 接到 `close-check` / `branch-check`。  
**产物**：`close_check.py`、`workitem_traceability.py`、`workitem_cmd.py`、execution-log template。  
**验证方式**：close-check unit/integration tests。  
**回退方式**：只在 close surface 阻断，不影响 execute。

### Phase 3：Governance + bounded read surfaces

**目标**：把 branch lifecycle 接到 `verify constraints`、`status --json`、`doctor`，形成常态可见的只读库存。  
**产物**：`verify_constraints.py`、`readiness.py`、`commands.py`、`doctor_cmd.py`。  
**验证方式**：verify/status/doctor integration tests。  
**回退方式**：不引入任何 Git 写操作。

### Phase 4：Rules/docs/template close-out

**目标**：收紧 `git-branch.md`、`pipeline.md`、自迭代约定、execution-log 模板与用户文档。  
**产物**：规则、模板、用户手册更新。  
**验证方式**：`verify constraints` + 文档相关测试。  
**回退方式**：只改规则文本，不扩展产品行为。

## 工作流计划

### 工作流 A：Inventory first

**范围**：branch/worktree listing、classification、divergence  
**影响范围**：`git_client.py`、`branch_inventory.py`  
**验证方式**：`tests/unit/test_git_client.py`、`tests/unit/test_branch_inventory.py`  
**回退方式**：未完成 inventory 前，不开始 close truth

### 工作流 B：Close truth before broad surfacing

**范围**：close-check、branch-check、execution-log disposition markers  
**影响范围**：`close_check.py`、`workitem_traceability.py`、`workitem_cmd.py`、templates  
**验证方式**：`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`  
**回退方式**：先 close，再 verify/status/doctor

### 工作流 C：Governance and bounded visibility

**范围**：verify surface、status/doctor summary、rules/docs  
**影响范围**：`verify_constraints.py`、`readiness.py`、`commands.py`、`doctor_cmd.py`、规则与用户文档  
**验证方式**：verify/status/doctor integration + full regression  
**回退方式**：read-only baseline 不动摇

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| inventory primitives | `tests/unit/test_git_client.py` | `tests/unit/test_branch_inventory.py` |
| close disposition truth | `tests/unit/test_close_check.py` | `tests/integration/test_cli_workitem_close_check.py` |
| verify branch governance | `tests/unit/test_verify_constraints.py` | `tests/integration/test_cli_verify_constraints.py` |
| bounded status/doctor | `tests/integration/test_cli_status.py` | `tests/integration/test_cli_doctor.py` |
| rules/templates close-out | `uv run ai-sdlc verify constraints` | targeted doc/rule assertions |

## 已锁定决策

- inventory read-only first
- `archived != merged`
- 仅当前 WI 关联 branch 可形成 close blocker
- 历史无关分支只警告，不默认阻断
- 不自动清理 branch/worktree

## 实施顺序建议

1. 先冻结 `007` 正式文档和 disposition 语义。
2. 再做 read-only inventory 与 lifecycle classification。
3. 然后把 disposition truth 接到 close-check / branch-check。
4. 最后接 verify、status/doctor 与规则/模板/文档收口。
