# 功能规格：Frontend Generation Governance Materialization Delivery Context Baseline

**功能编号**：`175-frontend-generation-governance-materialization-delivery-context-baseline`
**状态**：已实现（2026-04-19）
**创建日期**：`2026-04-19`

## 1. 背景

`168` 已经把 delivery context 绑定进 `generation constraints handoff`，但真正执行 `rules materialize-frontend-mvp` 与 `program remediate --execute` 时，generation governance artifacts 仍然使用静态 `build_mvp_frontend_generation_constraints()` 默认值。

这意味着：

1. 用户已经完成组件库选择；
2. `program generation-constraints-handoff` 也能看到当前 delivery context；
3. 但真正落盘到 `governance/frontend/generation/generation.manifest.yaml` 的内容，仍可能回退成空 delivery context。

## 2. 目标

让 generation governance artifacts 的真实物化入口优先绑定当前项目的 delivery context。

本基线至少要把以下字段进入 materialized generation truth：

- `effective_provider_id`
- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`
- `page_schema_ids`

## 3. 非目标

本基线不做以下事项：

1. 不新增完整前端代码生成器；
2. 不改 browser gate verdict；
3. 不改 provider whitelist / recipe / hard-rule 主体规则；
4. 不宣称 adapter package 已自动接入。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-175-001 | `FrontendGenerationConstraintSet` 必须新增 `page_schema_ids` |
| FR-175-002 | `ProgramFrontendGenerationConstraintsHandoff` 必须显式暴露 `page_schema_ids` |
| FR-175-003 | `program generation-constraints-handoff` CLI 必须显示 `page schema` |
| FR-175-004 | `generation.manifest.yaml` 必须保留 `page_schema_ids` |
| FR-175-005 | `rules materialize-frontend-mvp` 必须优先消费当前项目的 generation delivery context |
| FR-175-006 | `program remediate --execute` 的 frontend governance materialization 路径必须与 `rules materialize-frontend-mvp` 使用同一条 resolved generation constraints truth |

## 5. 验收场景

1. **Given** 当前 solution snapshot 选择 `public-primevue`，**When** 构建 generation handoff，**Then** 必须同时看到 `component_library_packages` 与 `page_schema_ids`。
2. **Given** 显式注入 `page_schema_ids` 的 generation constraints，**When** materialize artifacts，**Then** `generation.manifest.yaml` 必须保留该字段。
3. **Given** 当前项目已有 frontend solution snapshot 与 provider profile truth，**When** 执行 `rules materialize-frontend-mvp`，**Then** `generation.manifest.yaml` 必须写出当前 delivery context，而不是静态默认值。

## 6. 影响文件

- `src/ai_sdlc/models/frontend_generation_constraints.py`
- `src/ai_sdlc/generators/frontend_generation_constraint_artifacts.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/cli/sub_apps.py`
- `tests/unit/test_frontend_generation_constraints.py`
- `tests/unit/test_frontend_generation_constraint_artifacts.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/168-frontend-generation-constraints-delivery-context-binding-baseline/spec.md"
  - "specs/167-frontend-page-ui-schema-delivery-context-binding-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
