# 功能规格：Frontend Browser Gate Runner Delivery Context Propagation Baseline

**功能编号**：`172-frontend-browser-gate-runner-delivery-context-propagation-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`171` 已经让 browser gate 的 Python execution context、bundle artifact 和 CLI 继承当前组件库选择，但 Node/Playwright runner payload 仍没有携带同一份 delivery context。

这会导致：

1. Python 侧知道当前组件库路径；
2. 真正执行浏览器探针的 runner 却拿不到这些字段；
3. interaction snapshot 仍然不能证明“实际探针按哪条组件库路径执行”。

## 2. 目标

把当前 delivery context 继续传入 browser gate runner payload，并写入 interaction snapshot，使真实探针执行面也保留当前组件库上下文。

最小字段集合为：

- `delivery_entry_id`
- `component_library_packages`
- `provider_theme_adapter_id`
- `effective_provider`
- `effective_style_pack`

## 3. 非目标

本基线不做以下事项：

1. 不新增 provider-specific probe 逻辑；
2. 不改 interaction probe verdict；
3. 不增加新的 artifact 类型；
4. 不宣称组件库标准测试已经完整实现。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-172-001 | `run_default_browser_gate_probe()` 传给 Node runner 的 payload 必须包含 delivery context 字段 |
| FR-172-002 | `frontend_browser_gate_probe_runner.mjs` 必须把这些字段写入 `interaction-snapshot.json` |
| FR-172-003 | 本基线不得改变既有 probe 成败判定逻辑 |

## 5. 验收场景

1. **Given** browser gate runner 正常执行，**When** 写出 `interaction-snapshot.json`，**Then** 必须看到 `delivery_entry_id`、`component_library_packages`、`provider_theme_adapter_id`。
2. **Given** 当前 delivery context 为 `vue3-public-primevue`，**When** runner 成功执行，**Then** interaction snapshot 必须保留该值。

## 6. 影响文件

- `src/ai_sdlc/core/frontend_browser_gate_runtime.py`
- `scripts/frontend_browser_gate_probe_runner.mjs`
- `tests/unit/test_frontend_browser_gate_runtime.py`

---
related_doc:
  - "specs/171-frontend-browser-gate-delivery-context-binding-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
frontend_evidence_class: "framework_capability"
---
