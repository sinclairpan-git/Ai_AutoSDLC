# 功能规格：Frontend Browser Gate Rendered Delivery Context Validation Baseline

**功能编号**：`174-frontend-browser-gate-rendered-delivery-context-validation-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`171/172/173` 已经让 browser gate 继承当前 delivery context，并拥有默认可导航的 `managed/frontend/index.html`。但现有 probe 仍只证明“能打开页面”和“能点到一个交互目标”，还不能证明页面实际渲染内容是否与当前 delivery context 一致。

这会留下一个关键信任缺口：

1. browser gate 已经知道本次选择了什么组件库、delivery entry 与 page schema；
2. 但 probe 还没有把这些真值和页面实际渲染结果对比；
3. 因而无法在页面渲染错库、漏 schema、错 entry 时诚实阻断。

## 2. 目标

让 browser gate runner 对当前 browser entry 的已渲染内容执行最小 delivery context 校验。

本基线至少要校验：

- `delivery_entry_id`
- `component_library_packages`
- `page_schema_ids`

## 3. 非目标

本基线不做以下事项：

1. 不引入 provider-specific 深度视觉验收；
2. 不替代完整前端端到端业务测试；
3. 不扩展 adapter package 自动接入语义；
4. 不要求真实框架 runtime 已全部完成。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-174-001 | browser gate execution context 必须正式携带 `page_schema_ids` |
| FR-174-002 | browser gate runner 必须把 `page_schema_ids` 落入 interaction snapshot |
| FR-174-003 | runner 必须从页面已渲染 DOM 中提取 delivery entry、component packages 与 page schema ids |
| FR-174-004 | 当渲染结果与 payload context 不一致时，runner 必须返回 `actual_quality_blocker` |
| FR-174-005 | mismatch blocker code 至少要能区分 delivery entry、component package、page schema 三类不一致 |

## 5. 验收场景

1. **Given** browser gate execution context，**When** probe request / bundle input 落盘，**Then** 必须包含 `page_schema_ids`。
2. **Given** runner 收到包含 `page_schema_ids` 的 payload，**When** 写 interaction snapshot，**Then** 快照必须保留该字段。
3. **Given** 页面渲染出的 delivery entry / component packages / page schema ids 与 payload 一致，**When** runner 完成 probe，**Then** interaction classification 必须为 `pass`。
4. **Given** 页面漏渲染组件包或 page schema，**When** runner 完成 probe，**Then** interaction classification 必须为 `actual_quality_blocker`。

## 6. 影响文件

- `src/ai_sdlc/models/frontend_browser_gate.py`
- `src/ai_sdlc/core/frontend_browser_gate_runtime.py`
- `src/ai_sdlc/core/program_service.py`
- `scripts/frontend_browser_gate_probe_runner.mjs`
- `tests/unit/test_frontend_browser_gate_runtime.py`
- `tests/unit/test_program_service.py`

---
related_doc:
  - "specs/171-frontend-browser-gate-delivery-context-binding-baseline/spec.md"
  - "specs/172-frontend-browser-gate-runner-delivery-context-propagation-baseline/spec.md"
  - "specs/173-frontend-managed-browser-entry-materialization-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
