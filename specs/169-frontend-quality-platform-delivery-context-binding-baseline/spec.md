# 功能规格：Frontend Quality Platform Delivery Context Binding Baseline

**功能编号**：`169-frontend-quality-platform-delivery-context-binding-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`168` 已经让 generation constraints 默认继承当前选中的组件库上下文，但 `quality-platform-handoff` 仍只暴露质量矩阵、证据契约和 page/style 信息，缺少“这次到底按哪条组件库路径验收”的 delivery context。

这会导致：

1. 生成层已经知道默认按哪套组件库写；
2. 验收层却还不能明确显示“按哪条 delivery entry 在验”；
3. 对用户来说，链路最后一段仍然不像“选一次，后面都自动跟随”。

## 2. 目标

把当前组件库选择的最小 delivery context 绑定进 `quality-platform-handoff`，让质量验收层开始显式继承这次选择。

最小字段集合为：

- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`

## 3. 非目标

本基线不做以下事项：

1. 不改 `src/ai_sdlc/models/frontend_quality_platform.py` 的质量模型本体；
2. 不改质量矩阵、证据模型或 verdict 规则；
3. 不执行真实测试运行器；
4. 不把安装状态与质量验收真值混写。

## 4. 关键决策

- quality model 本体继续只表达质量真值；
- delivery context 只作为 acceptance handoff 的输入元数据挂在 `ProgramService / CLI` 上；
- handoff 必须单向继承 `page-ui-schema-handoff` 已经绑定好的 delivery context；
- 这一步表达的是“按哪条组件库路径验收”，不是“组件库已经安装成功”。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-169-001 | `ProgramFrontendQualityPlatformHandoff` 必须新增 `delivery_entry_id` |
| FR-169-002 | `ProgramFrontendQualityPlatformHandoff` 必须新增 `component_library_packages` |
| FR-169-003 | `ProgramFrontendQualityPlatformHandoff` 必须新增 `provider_theme_adapter_id` |
| FR-169-004 | `ProgramService.build_frontend_quality_platform_handoff()` 必须继承 `page-ui-schema-handoff` 的 delivery context |
| FR-169-005 | `program quality-platform-handoff` CLI 必须显式打印 delivery entry 与 component packages |
| FR-169-006 | 本基线不得改写 quality platform 模型本体 |

## 6. 验收场景

1. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 `quality-platform-handoff`，**Then** 必须看到 `vue3-public-primevue`、`primevue`、`@primeuix/themes`。
2. **Given** 当前运行 `program quality-platform-handoff`，**When** 输出 handoff，**Then** 必须显式显示 `delivery entry` 与 `component package`。
3. **Given** 质量矩阵和证据契约保持不变，**When** 完成这次绑定，**Then** quality model 本体不需要被改写。

## 7. 影响文件

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/168-frontend-generation-constraints-delivery-context-binding-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
