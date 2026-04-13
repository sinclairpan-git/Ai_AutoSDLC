# 功能规格：Frontend Mainline Delivery Materialization Runtime Baseline

**功能编号**：`124-frontend-mainline-delivery-materialization-runtime-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 已完成首批切片
**输入**：[`../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`](../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md`](../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md)、[`../../src/ai_sdlc/models/frontend_managed_delivery.py`](../../src/ai_sdlc/models/frontend_managed_delivery.py)、[`../../src/ai_sdlc/core/managed_delivery_apply.py`](../../src/ai_sdlc/core/managed_delivery_apply.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)

> 口径：`124` 是 `120/T12` 的 implementation carrier。它把 `123` 的窄版 apply executor 向前推进一层，使其能在已确认 action plan 约束下执行受控 `dependency_install` 与 `artifact_generate`，并把 managed target path / will_not_touch / preflight-vs-execute 语义收敛成真正的 runtime truth。`124` 不实现 browser gate、workspace takeover、任意 shell 步骤或自由写文件。

## 问题定义

`123` 已经建立 execution session、ledger、dependency 排序与 honest result，但它故意把 `dependency_install` 与 controlled subtree file writer 留在下游。若继续停在这里，`T13` 之前的 frontend delivery 仍然无法 materialize provider packages 和受控 scaffold，apply runtime 也无法证明自己真的服从 `will_not_touch` 边界。

`124` 的目标是补齐这一层最小但严格的 materialization runtime：

- `dependency_install` 只能消费已确认 plan 中声明的 package manager / install strategy / package set
- `artifact_generate` 只能在 managed target 子树内写入受控目录与文件
- dry-run/preflight 只能做 payload 与 boundary 校验，不得偷偷产生副作用
- execute path 必须把写入/安装结果继续写回 action-level ledger truth

## 范围

- **覆盖**：
  - 为 `frontend_action_plan.action_items[]` 新增受控 executor payload truth
  - 支持 `dependency_install` 与 `artifact_generate` 两类 materialization action
  - 引入 `managed_target_path` runtime truth，并与 `will_not_touch` 做 fail-closed boundary 校验
  - 将 `ProgramService` 的 managed delivery apply 路径区分为 preflight 与 execute 两种上下文
  - 补 unit/integration tests，覆盖 payload 校验、越界阻断、实际文件 materialization 与 install hook
- **不覆盖**：
  - `workspace_integration`、root-level takeover、旧 frontend 根目录接管
  - browser gate、recheck/remediation、program readiness 聚合
  - 任意自由 shell 命令、任意下载源、任意 repo 外路径写入

## 已锁定决策

- materialization runtime 继续沿用 `123` 的 execution session / ledger / honest result vocabulary，不另起第二套 apply 状态机。
- `dependency_install` 只接受结构化 payload：`install_strategy_id`、`package_manager`、`working_directory`、`packages`。
- `artifact_generate` 只接受结构化 payload：`directories` 与 `files[]`；文件内容来自 plan truth，不接受运行时自由生成目标路径。
- `managed_target_path` 必须是 repo 内相对路径；缺失、绝对路径或路径穿越都必须 fail-closed。
- `will_not_touch` 继续以 repo-relative 边界表达；任何目标路径一旦落入其内，必须在执行前阻断。
- preflight 只能验证 payload/boundary，不得执行安装或写文件。

## 功能需求

| ID | 需求 |
|----|------|
| FR-124-001 | 系统必须为 `dependency_install` 与 `artifact_generate` action 提供结构化 executor payload truth |
| FR-124-002 | `dependency_install` 只能执行已确认 action plan 中声明的 package manager、install strategy 与 package 集合 |
| FR-124-003 | `artifact_generate` 只能写入 `managed_target_path` 子树，且不得命中 `will_not_touch` |
| FR-124-004 | preflight 必须校验 payload、managed target path 与 path boundary，但不得产生文件或安装副作用 |
| FR-124-005 | execute path 成功后必须把安装/写入结果写入 `after_state`，并继续沿用 action-level ledger truth |
| FR-124-006 | 对缺 payload、空 package 集合、空 artifact payload、路径越界与 `will_not_touch` 命中，系统必须 `blocked_before_start` |
| FR-124-007 | `124` 不得把 browser gate、workspace takeover 或自由 shell 步骤混进 apply runtime |

## Exit Criteria

- **SC-124-001**：`dependency_install` 能通过结构化 payload 与 install hook 执行，并把结果写入 ledger
- **SC-124-002**：`artifact_generate` 能在 managed target 子树内真实写文件，并对越界路径 fail-closed
- **SC-124-003**：focused tests 与 CLI execute 路径能证明 preflight 不产生副作用、execute 才 materialize

---
related_doc:
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "src/ai_sdlc/models/frontend_managed_delivery.py"
  - "src/ai_sdlc/core/managed_delivery_apply.py"
  - "src/ai_sdlc/core/program_service.py"
frontend_evidence_class: "framework_capability"
---
