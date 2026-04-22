# 功能规格：Frontend Managed Delivery Artifact Generate Delivery Context Baseline

**功能编号**：`170-frontend-managed-delivery-artifact-generate-delivery-context-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`167/168/169` 已经把当前选中的 delivery context 继续绑定进 `page-ui-schema-handoff`、`generation-constraints-handoff` 与 `quality-platform-handoff`。但 `165` 之后真正执行 mutate 的 `program managed-delivery-apply`，虽然已经拥有 `artifact_generate` action，却仍存在两条断层：

1. truth-derived dry-run 输出需要把 `artifact_generate` 稳定呈现为已选动作的一部分；
2. `artifact_generate` 写出的 `src/generated/frontend-delivery-context.ts` 需要固定成可直接被 managed frontend 入口消费的 TypeScript object literal contract。

这会让链路停在“handoff 已知道 delivery context”，但真正 materialize 到受控前端目录时仍然不够清晰。

## 2. 目标

把当前 delivery context 继续绑定进 truth-derived `managed-delivery-apply` 的 `artifact_generate` slice，使其成为受控交付的正式一环。

本基线至少要保证：

1. truth-derived request 的 dry-run 明确显示 `artifact_generate` 已被选中；
2. `artifact_generate` payload 固定生成 `src/generated/frontend-delivery-context.ts` 与 `src/App.vue`；
3. `frontend-delivery-context.ts` 使用稳定的 TypeScript object literal 结构，显式保留 `deliveryEntryId`、`componentLibraryPackages` 与相关 delivery truth；
4. execute 路径继续通过现有 `managed_delivery_apply` runtime 写出上述文件，不另造第二套文件写入链。

## 3. 非目标

本基线不做以下事项：

1. 不引入真实代码生成器或模板市场；
2. 不改写 browser gate、workspace integration 或 root takeover 语义；
3. 不把 `artifact_generate` 扩成任意自由文本生成；
4. 不新增 target project runtime install / adapter expansion；
5. 不重写 `167/168/169` 已冻结的 handoff truth。

## 4. 关键决策

- `artifact_generate` 继续只消费现有 `solution snapshot + page-ui handoff + generation handoff + quality handoff`；
- `frontend-delivery-context.ts` 表达的是 managed frontend 的默认 delivery context，不是新的 canonical planning truth；
- `App.vue` 继续作为最小 managed frontend 入口文件，与 `frontend-delivery-context.ts` 形成受控配套产物；
- dry-run 输出必须诚实反映 `decision_receipt.selected_action_ids` 中实际选中的 mutate actions，不允许 handoff 已接通但 guard surface 遗漏。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-170-001 | truth-derived `build_frontend_managed_delivery_apply_request()` 必须将 `artifact_generate` 保持在默认选中的 mutate action 集合中 |
| FR-170-002 | `program managed-delivery-apply --dry-run` 必须显式显示 `managed_target_prepare, dependency_install, artifact_generate` 的选中动作面 |
| FR-170-003 | `_artifact_generate_payload()` 必须稳定生成 `src/generated/frontend-delivery-context.ts` 与 `src/App.vue` |
| FR-170-004 | `frontend-delivery-context.ts` 必须包含 `deliveryEntryId`、`providerThemeAdapterId`、`componentLibraryPackages` 与 `pageSchemas` 等 delivery context 字段 |
| FR-170-005 | `frontend-delivery-context.ts` 必须以稳定的 TypeScript object literal 形式输出，而不是仅用 JSON dump 伪装源码 |
| FR-170-006 | execute 路径必须继续通过既有 `managed_delivery_apply` artifact writer 写出 `frontend-delivery-context.ts` 与 `App.vue` |
| FR-170-007 | 本基线不得把 `artifact_generate` 扩成无边界多文件 scaffold；当前只允许 materialize 受控的 delivery context carrier |

## 6. 验收场景

1. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 truth-derived managed delivery request，**Then** `artifact_generate` 必须出现在默认选中的 mutate actions 中。
2. **Given** `artifact_generate` payload 被物化，**When** 查看 `src/generated/frontend-delivery-context.ts`，**Then** 必须看到 `deliveryEntryId: "vue3-public-primevue"`、`"primevue"` 与项目级 delivery context 字段。
3. **Given** 用户执行 `program managed-delivery-apply --execute --yes --ack-effective-change`，**When** apply 成功进入 pending browser gate，**Then** `managed/frontend/src/generated/frontend-delivery-context.ts` 与 `managed/frontend/src/App.vue` 必须真实落盘。

## 7. 影响文件

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

---
related_doc:
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md"
  - "specs/165-frontend-solution-confirm-continue-apply-orchestration-baseline/spec.md"
  - "specs/167-frontend-page-ui-schema-delivery-context-binding-baseline/spec.md"
  - "specs/168-frontend-generation-constraints-delivery-context-binding-baseline/spec.md"
  - "specs/169-frontend-quality-platform-delivery-context-binding-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
