# 功能规格：Frontend Managed Browser Entry Materialization Baseline

**功能编号**：`173-frontend-managed-browser-entry-materialization-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`170` 已让 managed delivery 默认生成 `frontend-delivery-context.ts` 与 `App.vue`，`171/172` 也让 browser gate 继承并传播当前 delivery context。但 browser gate 真正导航时默认仍在寻找 `managed/frontend/index.html`，而 managed delivery 之前并不会生成这个 entry。

这会导致：

1. browser gate 已经拿到了正确上下文；
2. 但默认 managed frontend 仍可能没有可导航入口；
3. 探针只能诚实返回 `browser_entry_unavailable`，无法把执行链真正拉通。

## 2. 目标

让 truth-derived managed delivery 默认生成可导航的 `managed/frontend/index.html`，作为 browser gate 的最小 browser entry。

这个 entry 必须：

- 直接展示当前 `deliveryEntryId`
- 展示 `componentLibraryPackages`
- 展示 `pageSchemaId`
- 保留可消费的 delivery context JSON

## 3. 非目标

本基线不做以下事项：

1. 不引入完整前端构建系统；
2. 不替代真实 Vue app runtime；
3. 不改 browser gate verdict；
4. 不做 provider-specific probe 逻辑；
5. 不宣称完整页面生成器已完成。

## 4. 功能需求

| ID | 需求 |
|----|------|
| FR-173-001 | truth-derived `artifact_generate` 必须新增 `index.html` |
| FR-173-002 | `index.html` 必须包含 `frontend-browser-entry` 容器 |
| FR-173-003 | `index.html` 必须显式显示当前 delivery entry、component packages 与 page schema ids |
| FR-173-004 | `index.html` 必须内嵌 delivery context JSON，供后续 probe / runtime 消费 |
| FR-173-005 | 本基线不得引入 build step 或额外 frontend bundler 依赖 |

## 5. 验收场景

1. **Given** truth-derived managed delivery request，**When** 物化 `artifact_generate` payload，**Then** files 必须包含 `index.html`。
2. **Given** 执行 truth-derived `managed-delivery-apply`，**When** apply 成功，**Then** `managed/frontend/index.html` 必须真实落盘。
3. **Given** browser gate runner 收到 `managed/frontend/index.html`，**When** 导航该 entry，**Then** 必须能得到 `completed` 级别的基础导航结果。

## 6. 影响文件

- `src/ai_sdlc/core/program_service.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`
- `tests/unit/test_frontend_browser_gate_runtime.py`

---
related_doc:
  - "specs/170-frontend-managed-delivery-artifact-generate-delivery-context-baseline/spec.md"
  - "specs/171-frontend-browser-gate-delivery-context-binding-baseline/spec.md"
  - "specs/172-frontend-browser-gate-runner-delivery-context-propagation-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
