---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P1 Recheck Remediation Feedback Baseline

## 1. 目标与定位

本计划处理的是 `066` 下游的第四条 P1 child baseline：`Frontend P1 Recheck Remediation Feedback Baseline`。它不是 diagnostics child，不是 visual / a11y child，也不是 provider/runtime 实现切片。当前仓库已经在上游锁定了：

- `017` generation control plane truth
- `018` gate matrix / compatibility / report / recheck-fix boundary
- `065` sample source self-check 的显式 observation 输入边界
- `067` expanded kernel truth
- `068` page recipe expansion truth
- `069` diagnostics coverage matrix、gap / empty / drift classification 与 compatibility feedback boundary

`070` 的职责是在这些 truth 之上，正式冻结 P1 的 frontend recheck handoff、bounded remediation feedback、writeback artifact 与作者体验闭环。

## 2. 范围与约束

### In Scope

- 冻结 `frontend_recheck_handoff` 的最小对象边界与触发时机
- 冻结 `frontend_remediation_input` 的 fix inputs / suggested actions / recommended commands truth
- 冻结 bounded remediation runbook、command whitelist honesty、writeback artifact 与 provider handoff payload 的最小边界
- 冻结 recheck / remediation 与 `069` diagnostics truth、`071` visual / a11y truth 之间的 handoff 关系
- 冻结 future implementation touchpoints、最小测试矩阵与 docs-only honesty

### Out Of Scope

- 改写 `069` diagnostics / drift classification 或 `018` gate / report family truth
- 扩张 visual / a11y 反馈面、截图比对、视觉回归或 accessibility 平台
- 引入完整 auto-fix engine、任意脚本执行器、整页重写或 provider/runtime 代码生成
- 默认发现 `<frontend-source-root>`、默认回退 sample fixture、隐式 materialize observation artifact
- 修改 root `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md` 或生成 `development-summary.md`

## 3. 未来实现触点

本批仅 formalize docs，不进入实现。后续如进入实现批次，优先触点预计为：

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/core/frontend_gate_verification.py`
- `src/ai_sdlc/gates/frontend_contract_gate.py`
- `src/ai_sdlc/models/frontend_gate_policy.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`
- `tests/unit/test_verify_constraints.py`
- `tests/integration/test_cli_verify_constraints.py`

这些文件面只用于说明未来实现切片可能承接的位置，不代表当前 work item 允许修改。

## 4. 分阶段安排

### Phase 0：Formal baseline freeze

**目标**：将 P1 recheck / remediation feedback 的范围、truth-order、对象边界与 handoff 规则冻结成独立 canonical docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`.ai-sdlc/project/config/project-state.yaml`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 `specs/070/...` 与 `project-state.yaml`。  

### Phase 1：Positioning / truth-order / non-goals freeze

**目标**：锁定 `070` 在 `069` 之后、与 `071` 并列的 child 位置，以及 diagnostics / visual / runtime 的非目标。  
**产物**：`spec.md` 中的问题定义、范围、已锁定决策、FR-070-001 ~ FR-070-004。  
**验证方式**：formal docs review。  
**回退方式**：不触发任何 runtime 变更。  

### Phase 2：Recheck / remediation object boundary freeze

**目标**：冻结 `frontend_recheck_handoff`、`frontend_remediation_input`、bounded remediation command truth 与 source-root honesty。  
**产物**：`spec.md` 的 FR-070-005 ~ FR-070-014、关键实体描述。  
**验证方式**：对象边界对账。  
**回退方式**：不进入实现。  

### Phase 3：Runbook / writeback / provider handoff freeze

**目标**：冻结 remediation runbook、writeback artifact、provider handoff 与作者反馈诚实边界。  
**产物**：`spec.md` 的 FR-070-015 ~ FR-070-021、success criteria、`plan.md` 的 owner boundary / test matrix。  
**验证方式**：formal docs review。  
**回退方式**：不进入 CLI / service 写入实现。  

### Phase 4：Execution log init / project-state update / docs-only validation

**目标**：初始化 canonical docs、记录当前批次、推进 `project-state` 到下一个编号，并完成 docs-only 门禁。  
**产物**：`task-execution-log.md`、更新后的 `project-state.yaml`。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：仅回退当前 docs 与 `project-state.yaml`。  

## 5. Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| Diagnostics / drift child (`069`) | 冻结 coverage matrix、classification 与 compatibility feedback boundary | 不得直接定义作者 remediation loop |
| Recheck / remediation child (`070`) | 冻结 bounded remediation feedback、recheck handoff 与 writeback/handoff honesty | 不得重写 diagnostics truth、不得膨胀为 auto-fix engine |
| Visual / a11y child (`071`) | 冻结基础 visual / a11y 检查与反馈面 | 不得回头重写 remediation / recheck truth |
| Provider/runtime downstream | 承接外部前端项目实际修复与 provider 侧代码落地 | 不得在当前 planning baseline 中被隐式当作框架内实现 |

## 6. 关键路径验证策略

- `070` formal docs 必须能独立表达 `READY -> recheck handoff` 与 `RETRY -> remediation input` 的分流
- `070` formal docs 必须明确 `<frontend-source-root>` 是 observation remediation 的显式输入，而不是自动发现行为
- `070` formal docs 必须明确 remediation runbook 只允许 bounded / reviewable command 集，不得隐式扩大执行面
- `070` formal docs 必须明确 writeback / provider handoff 只承接摘要与审计信息，不直接修改外部前端源码
- `070` formal docs 必须明确 `071` 仍承接 visual / a11y，不得把截图或 accessibility 反馈混入当前 child

## 7. 最小测试矩阵（未来实现批次）

当前批次不写测试；以下仅为 future implementation baseline：

1. `ProgramService.build_integration_dry_run` 在 readiness `READY` 时生成 `frontend_recheck_handoff`
2. `ProgramService.build_integration_dry_run` 在 readiness 非 `READY` 时生成 `frontend_remediation_input`
3. remediation command 集对 observation fix input 始终要求显式 `<frontend-source-root>`
4. remediation execute 仅允许已知命令，未知命令必须显式失败
5. remediation writeback artifact 能记录 per-step execution result 与 remaining blockers
6. provider handoff payload 只消费 writeback artifact，不直接执行 provider/runtime 写入

## 8. 执行前置条件与回退

- 当前 work item 只能在 `069` accepted/frozen 后继续
- 当前 work item 只允许 docs-only 变更，不得触碰 `src/` / `tests/`
- 当前 work item 不得提前修改 root-level program truth
- 若 formal docs 出现越界到 diagnostics / visual-a11y / auto-fix engine / provider runtime 的表述，必须先回退到上游 child baseline 约束重新收口
