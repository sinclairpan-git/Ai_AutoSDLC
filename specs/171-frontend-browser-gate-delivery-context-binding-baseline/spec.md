# 功能规格：Frontend Browser Gate Delivery Context Binding Baseline

**功能编号**：`171-frontend-browser-gate-delivery-context-binding-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`169` 已经让 `quality-platform-handoff` 继承当前组件库选择，`170` 也让 managed delivery 默认生成受控前端产物。但真正执行质量验收的 `browser-gate-probe` 仍只绑定 provider/style truth，没有把 delivery entry、组件包集合和 theme adapter 带进 runtime execution context。

这会导致：

1. handoff 已知道当前组件库路径；
2. browser gate 真正执行时却看不到同一份 delivery context；
3. 用户仍无法把“后续测试和验收会按所选组件库走”理解成真实 execution truth。

## 2. 目标

把当前 delivery context 绑定进 browser gate execution/runtime，使 `program browser-gate-probe` 的 request、execute artifact 与 CLI surfaced diagnostics 都显式继承当前组件库选择。

最小字段集合为：

- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`

## 3. 非目标

本基线不做以下事项：

1. 不改 Playwright runner 或 probe verdict 规则；
2. 不新增真正的组件库专属测试用例；
3. 不改 browser gate 与 quality gate 的 blocking / advisory 判定；
4. 不把“组件库已安装”与“browser gate 已验证通过”混写；
5. 不替代后续更完整的 quality execution/runtime integration。

## 4. 关键决策

- browser gate execution context 直接继承 `quality-platform-handoff` 的 delivery context；
- delivery context 进入 request / bundle / CLI surfaced diagnostics，但不改变既有 gate verdict 逻辑；
- 这一步表达的是“质量执行面知道当前组件库路径”，不是“组件库标准测试已经全部实现”。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-171-001 | `BrowserQualityGateExecutionContext` 必须新增 `delivery_entry_id` |
| FR-171-002 | `BrowserQualityGateExecutionContext` 必须新增 `component_library_packages` |
| FR-171-003 | `BrowserQualityGateExecutionContext` 必须新增 `provider_theme_adapter_id` |
| FR-171-004 | `BrowserQualityBundleMaterializationInput` 必须新增同一组 delivery context 字段 |
| FR-171-005 | `ProgramService.build_frontend_browser_gate_probe_request()` 与 execute 路径必须从 `quality-platform-handoff` 继承当前 delivery context |
| FR-171-006 | `program browser-gate-probe` CLI 必须显式打印 delivery entry 与 component packages |

## 6. 验收场景

1. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 browser gate execution context，**Then** 必须看到 `vue3-public-primevue`、`primevue`、`@primeuix/themes`。
2. **Given** 当前执行 `program browser-gate-probe --execute`，**When** gate artifact 落盘，**Then** `execution_context` 与 `bundle_input` 都必须包含上述 delivery context 字段。
3. **Given** 当前运行 `program browser-gate-probe --execute`，**When** CLI 输出 guard/result，**Then** 必须显式打印 `delivery entry` 与 `component package`。

## 7. 影响文件

- `src/ai_sdlc/models/frontend_browser_gate.py`
- `src/ai_sdlc/core/frontend_browser_gate_runtime.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_frontend_browser_gate_runtime.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/169-frontend-quality-platform-delivery-context-binding-baseline/spec.md"
  - "specs/170-frontend-managed-delivery-artifact-generate-delivery-context-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
frontend_evidence_class: "framework_capability"
---
