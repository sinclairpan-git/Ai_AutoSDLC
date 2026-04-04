---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md"
  - "specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Mutation Execution Baseline

**编号**：`064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline` | **日期**：2026-04-04 | **规格**：specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md

## 概述

`064` 是一个 test-first 的 real mutation work item。它建立在 `063` 已完成的 execution gating consumption 之上，把 canonical `cleanup_mutation_execution_gating` 从“已被消费、但仍 `deferred`”推进到“在显式确认下执行 bounded cleanup mutation，并诚实回报真实结果”。本项只实现 baseline action matrix，不扩张为通用 cleanup engine。

## 技术背景

**语言/版本**：Python 3.12  
**主要依赖**：Typer、PyYAML、pytest、ruff  
**存储**：项目内 canonical YAML artifact（`.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`）  
**测试**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints`、`uv run ruff check src tests`  
**目标平台**：本地 CLI 驱动的 framework workflow  
**约束**：
- 只消费 canonical `cleanup_mutation_execution_gating`，不新增 execution-only truth
- 只允许 baseline action matrix：`thread_archive/archive_thread_report` 与 `spec_dir/remove_spec_dir`
- 所有真实 mutation 都必须受工作区根目录边界保护
- 不得从 `--yes`、approval truth、report 文本、`written_paths` 或 working tree 状态推断执行资格
- 先写 failing tests，再补 service/CLI 最小实现

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一事实源 | 只消费 canonical project cleanup artifact 中已 formalize 的 `cleanup_mutation_execution_gating` |
| bounded mutation | 仅执行冻结 action matrix 与 canonical target path，禁止工作区扫描式 cleanup |
| 诚实结果 | 真实 mutation 发生后停止使用 `deferred`，改为按 per-target outcome 汇总 aggregate result |
| test-first | 先扩展 unit/integration failing tests，再做 `ProgramService` / CLI 最小落地 |

## 项目结构

### 文档结构

```text
specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：formal boundary freeze

**目标**：把 `064` 锁定为 separate execution child work item，并冻结 baseline action matrix、路径边界与 honest result semantics  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：对账 `049/050/062/063` 与当前 `ProgramService` cleanup execute 行为  
**回退方式**：仅回退 `specs/064-.../` 文档内容

### Phase 1：red tests for real mutation semantics

**目标**：通过 failing tests 固定真实 cleanup mutation 的路径安全、动作矩阵与 aggregate result 语义  
**产物**：更新后的 `tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py -q` 与 `uv run pytest tests/integration/test_cli_program.py -q` 先出现与 real mutation execution 相关的失败  
**回退方式**：回退新增 execution tests

### Phase 2：ProgramService mutation execution

**目标**：在 `ProgramService` 中实现 canonical gated target 的真实 mutation、per-target outcome 与 aggregate result 计算  
**产物**：更新后的 `src/ai_sdlc/core/program_service.py`  
**验证方式**：unit tests 由红转绿，并在 artifact payload 中可观测到真实 execution evidence  
**回退方式**：局部回退 cleanup execute implementation

### Phase 3：CLI/report exposure alignment

**目标**：让 dry-run / execute / report 暴露真实 execution outcome、aggregate result 与 written paths  
**产物**：更新后的 `src/ai_sdlc/cli/program_cmd.py`  
**验证方式**：integration tests 断言 execute 输出和 report 不再停留在 `deferred` 语义  
**回退方式**：回退 CLI/report 输出调整

### Phase 4：focused verification

**目标**：确认 `064` 在真实 mutation baseline 内满足边界约束，并留下可审计验证记录  
**产物**：更新后的 `task-execution-log.md`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ruff check src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`  
**回退方式**：根据失败点只调整 `064` 文档、实现或测试

## 工作流计划

### 工作流 A：Execution target validation

**范围**：在 `ProgramService` 中把 execution gating items 与 target / eligibility / preview / proposal / approval truth 重新对齐，并拒绝 unsupported action、越界路径、重复 target 或类型不匹配  
**影响范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`  
**验证方式**：unit tests 覆盖 missing target、unsupported action、duplicate target、path traversal、kind/action mismatch  
**回退方式**：回退 target validation 相关逻辑

### 工作流 B：Bounded mutation execution

**范围**：为 `archive_thread_report` 与 `remove_spec_dir` 实现最小真实 mutation，并记录 per-target outcome / written paths  
**影响范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`  
**验证方式**：unit tests 断言文件/目录真实变化与 aggregate result 计算  
**回退方式**：回退 mutation execution 相关逻辑

### 工作流 C：CLI/report honesty

**范围**：让 execute 输出与 markdown report 展示 aggregate result、per-target outcome、warnings 与 written paths  
**影响范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`  
**验证方式**：integration tests 断言 execute 输出/report 不再使用误导性的 `deferred` 文案  
**回退方式**：回退 CLI/report 文案和结构

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| canonical gated target 才能进入真实执行 | unit tests 断言只有 listed 且对齐的 target 会被尝试执行 | 审阅 warnings / blockers 是否保留对齐失败原因 |
| baseline action matrix 不越界 | unit tests 断言仅 `archive_thread_report`、`remove_spec_dir` 被支持 | 检查 unsupported action 不会触发文件系统副作用 |
| 路径安全边界成立 | unit tests 断言越界 path、类型不匹配或缺失 target 会返回 non-success | 检查 written paths 不包含工作区外路径 |
| CLI/report 诚实呈现真实执行结果 | integration tests 断言 aggregate result、per-target outcome 与 written paths 可见 | 审阅 artifact payload 与 report 摘要一致性 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `archive_thread_report` 在未来是否需要支持“移动到 archive”而非删除 archive 副产物 | 当前基线已冻结为只操作 canonical target `path`，后续如需扩张必须新建 child work item | 不阻塞 `064` |
| aggregate result 的精确枚举是否需要进一步收窄 | 当前冻结为 `completed` / `partial` / `failed` / `blocked` 的诚实语义，后续实现按最小集合落地 | 不阻塞 `064` |

## 实施顺序建议

1. 先补 unit/integration failing tests，固定 action matrix、路径边界与 aggregate result honesty。
2. 再在 `ProgramService` 中实现 canonical gated target 的真实 mutation 与 per-target outcome。
3. 补齐 CLI/report 输出，使真实结果与 artifact payload 一致。
4. 跑 focused verification，并把证据追加到 `task-execution-log.md`。
