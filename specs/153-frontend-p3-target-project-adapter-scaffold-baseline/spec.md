# 功能规格：Frontend P3 Target Project Adapter Scaffold Baseline

**功能编号**：`153-frontend-p3-target-project-adapter-scaffold-baseline`
**创建日期**：2026-04-16
**状态**：已实现
**输入**：承接 `152` 的第一条 runtime tranche，落地 `target-project-adapter-layer` 的 scaffold truth、runtime boundary receipt 与最小 handoff surface；仍不进入外部 target project 的真实 runtime code。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`

> 口径：`152` 已冻结 runtime carrier、boundary receipt、evidence return 的真值顺序。`153` 是该顺序里的第一条真正 runtime tranche：它把 Core 侧应输出给目标业务前端项目的 `Adapter Scaffold Contract`、`Runtime Boundary Receipt`、artifact materialization、ProgramService handoff、CLI handoff 与 verify attachment 全部落成 machine-verifiable 产物，但仍不伪造“外部 target project runtime 已完成”。

## 范围

- **覆盖**：
  - 落地 `153` 的 runtime adapter scaffold models、validator 与 artifact materializer
  - 落地 `governance/frontend/provider-runtime-adapter/` canonical artifact set
  - 落地 `ProgramService.build_frontend_provider_runtime_adapter_handoff()`
  - 落地 `program provider-runtime-adapter-handoff` CLI
  - 落地 `verify constraints` 对 `153` 的 scoped attachment report
  - 将 `public-primevue` 与 `react-nextjs-shadcn` 纳入首版 target-project adapter scaffold truth
- **不覆盖**：
  - 不在 Ai_AutoSDLC Core 仓库中实现外部 target project 的真实 runtime code
  - 不在本工单中实现 evidence ingestion / global truth surfacing 的后续 tranche
  - 不启用 `independent-adapter-package` 的实际包化
  - 不宣称 React public runtime 或第二 public provider 已真实交付

## 用户场景与测试

### US-153-1 — Framework Maintainer 需要 machine-verifiable 的 target-project scaffold truth

作为**框架维护者**，我希望 Core 能输出稳定的 target-project adapter scaffold truth，这样 `152` 之后的 runtime 承接不再停留在文档描述。

**优先级说明**：P0。没有 scaffold truth，`152` 仍只是 successor planning truth。

**独立测试**：运行 `build_p3_target_project_adapter_scaffold_baseline()` 与 artifact materializer，可以看到稳定的 provider target、carrier mode、runtime delivery state 与 boundary receipt。

**验收场景**：

1. **Given** 我调用 `build_p3_target_project_adapter_scaffold_baseline()`，**When** 我检查输出，**Then** 我能看到 `public-primevue` 与 `react-nextjs-shadcn` 的 target-project adapter scaffold truth
2. **Given** 我 materialize artifact，**When** 我检查 `governance/frontend/provider-runtime-adapter/`，**Then** 我能看到 manifest、handoff schema、adapter targets 与每个 provider 的 scaffold / runtime boundary receipt

### US-153-2 — Delivery Owner 需要可直接消费的 handoff surface

作为**交付负责人**，我希望 `ProgramService` 和 CLI 能直接暴露 runtime adapter handoff surface，这样我能知道当前 effective provider 是否已经进入 scaffolded 状态。

**优先级说明**：P0。没有 handoff surface，外部 target project 无法接上这条 runtime 主线。

**独立测试**：在存在 frontend solution snapshot 的情况下，运行 `program provider-runtime-adapter-handoff` 能看到 provider、stack、carrier mode 与 runtime/evidence state。

**验收场景**：

1. **Given** solution snapshot 指向 `public-primevue/vue3`，**When** 我运行 `program provider-runtime-adapter-handoff`，**Then** 我能看到 `target-project-adapter-layer + scaffolded + missing`
2. **Given** 没有 solution snapshot，**When** 我运行 handoff CLI，**Then** 它会 fail-closed 并提示 `frontend_solution_snapshot_missing`

### US-153-3 — Reviewer 需要 scoped verify 能识别 scaffold truth 缺口

作为**reviewer**，我希望 `verify constraints` 能在 active `153` 时识别 runtime adapter artifact 缺失或 runtime not-started 的状态，这样我能判断 `153` 是否真的落地。

**优先级说明**：P1。没有 scoped verify，`153` 只能靠人工阅读判断。

**独立测试**：删除 `adapter-scaffold.yaml` 或把 snapshot 切到 `react-nextjs-shadcn`，`verify constraints` 会输出对应 blocker。

**验收场景**：

1. **Given** `public-primevue` 的 `adapter-scaffold.yaml` 缺失，**When** 我运行 `verify constraints`，**Then** 它会报告 `provider runtime adapter artifact missing`
2. **Given** snapshot 切到 `react-nextjs-shadcn/react`，**When** 我运行 `verify constraints`，**Then** 它会报告 `runtime adapter scaffold not started`

## 边界情况

- `react-nextjs-shadcn` 当前仍只进入 `not-started` scaffold truth，不得被误报为 runtime delivered
- `independent-adapter-package` 只有在 `validated_project_count >= 2` 时才允许成立
- `runtime_delivery_state=verified` 但 `evidence_return_state!=fresh` 必须直接判为无效
- 外部 target project 仍可缺席；`153` 的完成口径仅代表 Core 已输出受控 scaffold contract

## 需求

### 功能需求

- **FR-153-001**：系统必须提供 `FrontendProviderRuntimeAdapterSet` 及其子模型，表达 target-project adapter scaffold、carrier mode、runtime delivery state 与 evidence return state
- **FR-153-002**：系统必须提供 `build_p3_target_project_adapter_scaffold_baseline()`，把 `public-primevue` 与 `react-nextjs-shadcn` 物化为首版 scaffold truth
- **FR-153-003**：系统必须 materialize `provider-runtime-adapter.manifest.yaml`、`handoff.schema.yaml`、`adapter-targets.yaml` 与每个 provider 的 `adapter-scaffold.yaml` / `runtime-boundary-receipt.yaml`
- **FR-153-004**：系统必须提供 `validate_frontend_provider_runtime_adapter()`，能对 active solution snapshot 做 scoped runtime adapter validation
- **FR-153-005**：系统必须提供 `ProgramService.build_frontend_provider_runtime_adapter_handoff()` 与 `program provider-runtime-adapter-handoff`
- **FR-153-006**：`verify constraints` 必须在 active `153` 时消费 runtime adapter artifacts，并输出独立的 `frontend_provider_runtime_adapter_consistency` coverage gap
- **FR-153-007**：系统不得将 `153` 的 scaffold truth 伪造成外部 target project runtime delivered truth

### 关键实体

- **AdapterScaffoldContract**：定义目标业务前端项目必须 materialize 的 Kernel Wrapper / Provider Adapter / Legacy Adapter / receipt 文件
- **RuntimeBoundaryReceipt**：定义 provider 当前的 policy gate、carrier mode、runtime delivery state、evidence return state 与 boundary constraints
- **ProviderRuntimeAdapterTarget**：将 scaffold contract 与 boundary receipt 绑定到单个 provider
- **FrontendProviderRuntimeAdapterSet**：`153` 的顶层 runtime adapter scaffold truth

## 成功标准

- **SC-153-001**：`153` 的 models / artifacts / validator 可以独立表达 target-project adapter scaffold truth
- **SC-153-002**：`ProgramService` 与 CLI 可直接暴露 `153` handoff surface
- **SC-153-003**：`verify constraints` 可在 active `153` 时识别 artifact 缺失与 `not-started` 的 runtime adapter 缺口
- **SC-153-004**：`153` 的完成口径保持诚实，仍不宣称外部 target project runtime 已完成

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
