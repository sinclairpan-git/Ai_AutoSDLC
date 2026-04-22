# 功能规格：Frontend Theme Governance Generation Truth Consumption Baseline

**功能编号**：`176-frontend-theme-governance-generation-truth-consumption-baseline`
**状态**：已实现（2026-04-19）
**创建日期**：`2026-04-19`

## 1. 背景

`175` 已经把 frontend delivery context 写入 `generation.manifest.yaml`，但 theme/token governance 的下游消费仍存在两类静态入口：

1. `ProgramService.build_frontend_theme_token_governance_handoff()` 仍直接使用静态 `build_mvp_frontend_generation_constraints()`；
2. `ai-sdlc verify constraints` 在 148 链路里仍按静态 generation constraints 校验，无法识别 generation artifact 与 solution snapshot 的漂移。

这会导致用户已经选择组件库后，后续 theme governance handoff 与约束验收仍可能回到默认值。

## 2. 目标

让 frontend theme governance 的物化入口、handoff 入口与 verify 入口都默认消费当前项目的 generation truth。

## 3. 非目标

1. 不改 `solution-confirm --execute` 的自动安装边界；
2. 不把 `adapter_packages` 抬成正式 install truth；
3. 不扩展 quality platform / cross-provider consistency 的动态 theme truth 消费；
4. 不新增新的 provider 下载源解析逻辑。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-176-001 | frontend generation governance artifacts 必须提供可回读的结构化 loader |
| FR-176-002 | `ProgramService.build_frontend_theme_token_governance_handoff()` 必须消费 `resolve_frontend_generation_constraints()` |
| FR-176-003 | `rules materialize-frontend-theme-token-governance` 必须按当前项目 resolved generation truth 物化 theme governance baseline |
| FR-176-004 | `verify constraints` 的 148 theme governance 验证必须优先读取 generation governance artifacts |
| FR-176-005 | 当 generation truth 与 latest solution snapshot 推导出的 provider / delivery entry / packages / theme adapter / page schema 不一致时，`verify constraints` 必须返回 BLOCKER |

## 5. 验收场景

1. **Given** generation artifacts 已落盘，**When** loader 回读，**Then** 必须还原完整 `FrontendGenerationConstraintSet`。
2. **Given** theme governance handoff 被构建，**When** 当前项目已有 delivery context，**Then** 必须通过 `resolve_frontend_generation_constraints()` 消费当前 generation truth。
3. **Given** 148 基线下的 `generation.manifest.yaml` 被人为改成其他 provider / package / page schema，**When** 执行 `verify constraints`，**Then** 必须返回 `generation constraint drift` BLOCKER。

## 6. 影响文件

- `src/ai_sdlc/generators/frontend_generation_constraint_artifacts.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/cli/sub_apps.py`
- `tests/unit/test_frontend_generation_constraint_artifacts.py`
- `tests/unit/test_program_service.py`
- `tests/unit/test_verify_constraints.py`

---
related_doc:
  - "specs/175-frontend-generation-governance-materialization-delivery-context-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
