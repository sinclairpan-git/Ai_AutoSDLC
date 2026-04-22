# 功能规格：Frontend Quality Consistency Upstream Truth Consumption Baseline

**功能编号**：`177-frontend-quality-consistency-upstream-truth-consumption-baseline`
**状态**：已实现（2026-04-19）
**创建日期**：`2026-04-19`

## 1. 背景

`176` 已经把 generation truth 接入 theme governance handoff / verify，但 quality platform 与 cross-provider consistency 仍有两类残留：

1. `ProgramService` 的 quality / consistency handoff 仍直接消费静态 theme / quality baseline；
2. `verify constraints` 的 149 / 150 链路仍可绕过真实 upstream artifacts，只按静态 baseline 校验。

这会导致 theme 或 quality artifact 已经漂移时，下游 quality / consistency 验收仍可能误判为通过或只暴露不完整 blocker。

## 2. 目标

让 quality platform 与 cross-provider consistency 的 handoff、规则物化与 verify 默认消费当前 upstream truth，而不是静态 baseline。

## 3. 非目标

1. 不处理 `program truth sync` source inventory 编目迁移；
2. 不新增 provider-specific style pack；
3. 不改变 cross-provider certification gate 语义；
4. 不改自动安装/adapter package 边界。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-177-001 | theme token governance artifacts 必须提供可回读 loader |
| FR-177-002 | quality platform artifacts 必须提供可回读 loader |
| FR-177-003 | `ProgramService.build_frontend_quality_platform_handoff()` 必须消费 resolved theme truth |
| FR-177-004 | `ProgramService.build_frontend_cross_provider_consistency_handoff()` 必须消费 resolved theme / quality truth |
| FR-177-005 | `rules materialize-frontend-quality-platform` 与 `rules materialize-frontend-cross-provider-consistency` 必须按当前项目 resolved truth 物化 |
| FR-177-006 | `verify constraints` 的 149 链路必须读取 upstream theme artifacts |
| FR-177-007 | `verify constraints` 的 150 链路必须读取 upstream quality artifacts |

## 5. 验收场景

1. **Given** theme token governance artifacts 已落盘，**When** loader 回读，**Then** 必须还原完整 `FrontendThemeTokenGovernanceSet`。
2. **Given** quality platform artifacts 已落盘，**When** loader 回读，**Then** 必须还原完整 `FrontendQualityPlatformSet`。
3. **Given** quality handoff / cross-provider handoff 被构建，**When** 当前项目已有 delivery truth，**Then** 必须通过 resolved upstream truth 计算结果。
4. **Given** 149 基线下 upstream theme artifact 已损坏，**When** 执行 `verify constraints`，**Then** 必须返回 quality platform consistency blocker。
5. **Given** 150 基线下 upstream quality evidence refs 被改坏，**When** 执行 `verify constraints`，**Then** 必须返回 `unknown quality evidence` blocker。

## 6. 影响文件

- `src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py`
- `src/ai_sdlc/generators/frontend_quality_platform_artifacts.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/cli/sub_apps.py`
- `tests/unit/test_frontend_theme_token_governance_artifacts.py`
- `tests/unit/test_frontend_quality_platform_artifacts.py`
- `tests/unit/test_program_service.py`
- `tests/unit/test_verify_constraints.py`

---
related_doc:
  - "specs/176-frontend-theme-governance-generation-truth-consumption-baseline/spec.md"
  - "specs/149-frontend-p2-quality-platform-baseline/spec.md"
  - "specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
