---
related_doc:
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/core/program_service.py"
  - "tests/integration/test_cli_program.py"
  - "tests/unit/test_program_service.py"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/plan.md"
---
# 实施计划：Frontend Solution Confirm Continue Apply Orchestration Baseline

**编号**：`165-frontend-solution-confirm-continue-apply-orchestration-baseline` | **日期**：2026-04-19 | **规格**：`specs/165-frontend-solution-confirm-continue-apply-orchestration-baseline/spec.md`

## 概述

`165` 的目标是在不污染 `solution_snapshot` 真值的前提下，把 `solution-confirm` 和现有 managed delivery apply 链路串成显式组合流，并让 truth-derived `managed-delivery-apply` 入口继承同样的 effective-change 二次确认门槛。实现保持窄边界：CLI 负责编排与文案，`ProgramService` 只补受控的二次确认入参，不重写 executor。

## 约束

- 不改变 `solution-confirm --execute` 的默认语义
- 不把 apply result 回写到 solution snapshot
- 不把 `adapter_packages` 从空数组升级为独立安装包 truth
- `--ack-effective-change` 只在 `requested_* != effective_*` 时生效

## 阶段计划

### Phase 0：Red tests

**目标**：先锁定组合流的外部行为与二次确认语义  
**产物**：focused unit + integration tests  
**验证方式**：targeted pytest  
**回退方式**：仅回退测试

### Phase 1：Service / CLI wiring

**目标**：补 `second_confirmation_acknowledged` 的编排入口，并在 CLI 中串起 confirm -> apply request -> apply result  
**产物**：`program_cmd.py`、`program_service.py`  
**验证方式**：focused pytest  
**回退方式**：独立回退 service/CLI 改动

### Phase 2：Formal truth freeze

**目标**：新增 `165` spec/plan/tasks，记录 `adapter_packages` 继续为空的边界决策  
**产物**：`specs/165-.../*`  
**验证方式**：人工对账 + targeted pytest  
**回退方式**：仅回退 docs truth

## 验收重点

1. confirm-only 旅程保持不变
2. confirm + continue success 能写出 apply artifact
3. confirm + continue 在 effective change 未确认时 fail-closed
4. confirm + continue 在 registry blocker 下诚实返回 blocked
5. truth-derived `managed-delivery-apply --execute` 在 effective change 未确认时 fail-closed
