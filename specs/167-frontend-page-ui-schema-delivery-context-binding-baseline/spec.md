# 功能规格：Frontend Page UI Schema Delivery Context Binding Baseline

**功能编号**：`167-frontend-page-ui-schema-delivery-context-binding-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`166` 已经把当前选中的组件库解析成稳定的 delivery registry handoff，但 `147 page-ui-schema` 仍只暴露 page/schema/provider/style 基本信息，下游生成层看不到“本次该按哪条 delivery entry 和哪些组件库包去生成”。

这会导致一个明显断层：

1. 用户已经选了组件库；
2. 框架也已经知道该装哪些包；
3. 但后续 page/ui handoff 仍没有把这条选择变成默认生成上下文。

## 2. 目标

把 `delivery registry` 的最小上下文绑定进 `page-ui-schema-handoff`，让它开始作为后续 generation / quality 的共享输入锚点。

当前最小绑定包括：

- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`

## 3. 非目标

本基线不做以下事项：

1. 不直接改写 code generator；
2. 不重做 `147` 的 provider-neutral schema baseline；
3. 不新增真实 target project runtime code；
4. 不把 quality platform 全量改成直接消费 delivery registry。

## 4. 关键决策

- `page-ui-schema` 继续是 provider-neutral 的结构真值；
- 这次新增的是下游 handoff 上下文，不是改 schema 本体；
- handoff 中的 delivery context 继续单向来自 `166 delivery-registry-handoff`；
- `component_library_packages` 只用于告诉后续生成层“默认该按哪套组件库写”，不代表此时已经执行安装。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-167-001 | `FrontendPageUiSchemaHandoff` 必须新增 `delivery_entry_id` |
| FR-167-002 | `FrontendPageUiSchemaHandoff` 必须新增 `component_library_packages` |
| FR-167-003 | `FrontendPageUiSchemaHandoff` 必须新增 `provider_theme_adapter_id` |
| FR-167-004 | `ProgramService.build_frontend_page_ui_schema_handoff()` 必须把 `166 delivery-registry-handoff` 的相关字段绑定进 handoff |
| FR-167-005 | `program page-ui-schema-handoff` CLI 必须显式打印 delivery entry 与 component packages |
| FR-167-006 | 当前 prerequisite gap 仍允许作为 warning 暴露，不得因为机器暂时缺私有源条件就抹掉 delivery context 本身 |

## 6. 验收场景

1. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 `page-ui-schema-handoff`，**Then** 必须看到 `vue3-public-primevue`、`primevue`、`@primeuix/themes`。
2. **Given** 当前运行 `program page-ui-schema-handoff`，**When** 输出 handoff，**Then** 必须显式显示 `delivery entry` 与 `component package`。
3. **Given** `page-ui-schema` 结构本身有效，**When** 只存在 registry prerequisite gap，**Then** handoff 仍保留 delivery context，不得误报为无组件库上下文。

## 7. 影响文件

- `src/ai_sdlc/core/frontend_page_ui_schema.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_frontend_page_ui_schema.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/166-frontend-delivery-registry-runtime-handoff-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_page_ui_schema.py"
  - "src/ai_sdlc/core/program_service.py"
frontend_evidence_class: "framework_capability"
---
