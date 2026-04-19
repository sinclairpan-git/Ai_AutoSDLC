# 功能规格：Frontend Delivery Registry Runtime Handoff Baseline

**功能编号**：`166-frontend-delivery-registry-runtime-handoff-baseline`  
**状态**：已实现（2026-04-19）  
**创建日期**：`2026-04-19`

## 1. 背景

`099` 已把 `frontend_delivery_registry` / `delivery_bundle_entry` 的 join 规则、字段面与 fail-closed 边界冻结为 formal truth，但当前仓库还没有一个可执行 runtime 去把这些真值真正暴露给 `ProgramService` / CLI。

这会带来三个直接问题：

1. 用户看不到“当前选中的组件库，框架到底认定为哪条官方 delivery entry”；
2. `managed-delivery-apply` 虽然已经能安装包，但它复用了内部 bundle 组装逻辑，外部没有独立可审计的 registry handoff surface；
3. 非技术用户会误以为“框架知道企业组件库包名”就等于“框架已经知道私有源地址并可直接自动下载”。

## 2. 目标

补一条最小 runtime handoff：

`program delivery-registry-handoff`

它必须把当前 `solution snapshot` 对应的 provider / stack / style 解析成稳定的 delivery registry truth，并诚实展示：

1. 当前命中的 `entry_id`；
2. 组件库包集合；
3. install strategy 与 access mode；
4. provider manifest / style-support 的引用；
5. 当前仍需满足的 registry prerequisite。

## 3. 非目标

本基线不做以下事项：

1. 不执行真实安装；
2. 不接收 operator 手填 npm URL、git repo 或任意私有源地址；
3. 不把企业私有 registry 的真实下载地址猜测成 framework builtin truth；
4. 不把 `adapter_packages` 从空数组升级成独立 install truth；
5. 不重做 `099` docs-only contract freeze，只承接其 runtime 暴露层。

## 4. 关键决策

### 4.1 真值来源

- `entry_id` 继续来自 `effective_frontend_stack + effective_provider_id`；
- `component_library_packages` 继续来自 install strategy `packages`；
- `availability_prerequisites` 继续来自 provider manifest；
- `resolved_style_support_ref` 继续单向指向 `providers/frontend/<provider_id>/style-support.yaml#style_pack_id=<id>`。

### 4.2 当前 prerequisite 语义

registry handoff 需要把“这条 delivery entry 存在”与“当前机器已经满足执行条件”分开表达。

因此：

- entry 解析成功时，handoff 可以是 `ready`；
- 当前机器若仍缺 private/public registry prerequisite，应作为 warning surface 暴露；
- 这些 prerequisite gap 不能再把 registry truth 误报成不存在。

### 4.3 对非技术用户的诚实口径

- `public-primevue` 的包集合是 framework builtin public package truth；
- `enterprise-vue2` 的包名 `@company/enterprise-vue2-ui` 是 framework builtin contract truth；
- 这不等于 framework 已经知道企业真实 npm 下载链接；
- 企业私有 registry 的网络、token 与源配置仍需由后续环境接入真值承接。

## 5. 功能需求

| ID | 需求 |
|----|------|
| FR-166-001 | 系统必须提供 `ProgramService.build_frontend_delivery_registry_handoff()` |
| FR-166-002 | 系统必须提供 `program delivery-registry-handoff` CLI |
| FR-166-003 | handoff 必须展示 `registry_id`、`entry_id`、provider、stack、style、install strategy、package manager、component_library_packages、adapter_packages |
| FR-166-004 | handoff 必须展示 `provider_manifest_ref`、`resolved_style_support_ref` 与 `provider_theme_adapter_id` |
| FR-166-005 | handoff 必须区分 structural drift blocker 与当前 prerequisite gap；前者阻断 entry truth，后者作为 warning surface |
| FR-166-006 | `enterprise-vue2` 与 `public-primevue` 都必须能输出稳定 handoff |
| FR-166-007 | `adapter_packages` 在当前 baseline 仍必须显式为空数组 |

## 6. 验收场景

1. **Given** 当前没有 solution snapshot，**When** 运行 `program delivery-registry-handoff`，**Then** 必须返回 `frontend_solution_snapshot_missing` blocker。
2. **Given** 当前 snapshot 指向 `vue3 + public-primevue + modern-saas`，**When** 构建 handoff，**Then** 必须看到 `vue3-public-primevue`、`primevue`、`@primeuix/themes`、`public-primevue-default`。
3. **Given** 当前 snapshot 指向 `vue2 + enterprise-vue2 + enterprise-default`，**When** 构建 handoff，**Then** 必须看到 `vue2-enterprise-vue2`、`@company/enterprise-vue2-ui`、`company-registry-network`、`company-registry-token`。
4. **Given** 当前机器缺企业私有 registry prerequisite，**When** 构建 handoff，**Then** 必须仍能看到 entry truth，但 prerequisite gap 只能作为 warning 暴露，不能把 entry 本身误判为不存在。

## 7. 影响文件

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`
- `USER_GUIDE.zh-CN.md`

---
related_doc:
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
