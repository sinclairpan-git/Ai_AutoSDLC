# 功能规格：Frontend Generation Constraints Delivery Context Binding Baseline

**功能编号**：`168-frontend-generation-constraints-delivery-context-binding-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`167` 已经把选中的组件库上下文绑定进 `page-ui-schema-handoff`，但 `generation constraints` 仍然只暴露静态 whitelist / recipe / hard rules，看不到当前项目到底命中了哪条 delivery entry、该按哪些组件库包去生成。

这意味着：

1. 用户虽然已经选了组件库；
2. page/ui handoff 也已经知道这次选择；
3. 但真正约束后续代码默认怎么写的 generation 层，还没有正式继承这条上下文。

## 2. 目标

把 `page-ui-schema-handoff` 中的 delivery context 继续绑定进 `generation constraints` 的 handoff 与 artifact manifest，让后续代码生成默认继承当前组件库选择。

当前最小绑定包括：

- `effective_provider_id`
- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`

## 3. 非目标

本基线不做以下事项：

1. 不直接实现代码生成器；
2. 不改写 `quality platform`；
3. 不改变 `Ui*` 语义 whitelist 的 provider-neutral 主体；
4. 不执行真实安装或 target project runtime 接入。

## 4. 关键决策

- generation constraints 的 recipe / whitelist / hard rules 继续保持既有主线；
- 当前新增的是“默认生成上下文”，不是重写 generation baseline；
- generation handoff 必须单向消费 `167 page-ui-schema-handoff`；
- `component_library_packages` 在此仍表示“生成默认上下文”，不是“已经安装完成”。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-168-001 | `FrontendGenerationConstraintSet` 必须新增 delivery context 字段 |
| FR-168-002 | `build_mvp_frontend_generation_constraints()` 必须支持注入 delivery context |
| FR-168-003 | `generation.manifest.yaml` 必须保留 delivery context 字段 |
| FR-168-004 | `ProgramService` 必须提供 `build_frontend_generation_constraints_handoff()` |
| FR-168-005 | CLI 必须提供 `program generation-constraints-handoff` |
| FR-168-006 | handoff 必须显式显示 provider、delivery entry、component packages、allowed recipes 与 whitelist components |

## 6. 验收场景

1. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 generation handoff，**Then** 必须看到 `public-primevue`、`vue3-public-primevue`、`primevue`、`@primeuix/themes`。
2. **Given** 调用 `build_mvp_frontend_generation_constraints()` 并显式注入 delivery context，**When** materialize artifacts，**Then** `generation.manifest.yaml` 必须保留这些字段。
3. **Given** 当前没有 solution snapshot，**When** 运行 `program generation-constraints-handoff`，**Then** 必须返回 `frontend_solution_snapshot_missing` blocker。

## 7. 影响文件

- `src/ai_sdlc/models/frontend_generation_constraints.py`
- `src/ai_sdlc/generators/frontend_generation_constraint_artifacts.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_frontend_generation_constraints.py`
- `tests/unit/test_frontend_generation_constraint_artifacts.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/167-frontend-page-ui-schema-delivery-context-binding-baseline/spec.md"
  - "src/ai_sdlc/models/frontend_generation_constraints.py"
  - "src/ai_sdlc/core/program_service.py"
frontend_evidence_class: "framework_capability"
---
