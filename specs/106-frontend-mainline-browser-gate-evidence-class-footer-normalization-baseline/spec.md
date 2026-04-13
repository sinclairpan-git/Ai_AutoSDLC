# 功能规格：Frontend Mainline Browser Gate Evidence Class Footer Normalization Baseline

**功能编号**：`106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline`  
**创建日期**：2026-04-13  
**状态**：formal baseline 已冻结；footer normalization 首批已完成  
**输入**：[`../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md`](../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)、[`../102-frontend-mainline-browser-quality-gate-baseline/spec.md`](../102-frontend-mainline-browser-quality-gate-baseline/spec.md)、[`../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`](../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md)、[`../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`](../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md)、[`../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`](../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)

> 口径：`106` 不是新的 browser gate runtime feature，也不是补造 `frontend_contract_observations` 证据。它只处理一个更窄但必须诚实收口的问题：`100`~`104` 已经在 `program-manifest.yaml` 声明 `frontend_evidence_class=framework_capability`，但对应 `spec.md` 缺少 canonical footer，导致 `verify constraints` / `program status` 将其报告为 `frontend_evidence_class_authoring_malformed:missing_footer_key`。`106` 的目标是把 authored spec footer 与既有 runtime/manifest truth 对齐，让状态面只暴露真实剩余缺口，而不是作者格式错误。

## 问题定义

在 `105` 完成后，browser gate 主线的 formal / implementation carrier 已经具备连续链路，但当前 program status 仍存在一个人为噪声：`100`~`104` 虽然已经在 manifest 中镜像 `frontend_evidence_class: framework_capability`，`spec.md` 正文也明显属于 framework capability 约束切片，但它们缺少 `092` 所要求的 canonical footer。

这会带来三个问题：

- `verify constraints` 会额外产出 `frontend_evidence_class_authoring_malformed:missing_footer_key`
- `program status` 会把 authored-footer 错误与真正的 external artifact gap 混在一起
- 后续治理会误以为 `100`~`104` 还缺新的 evidence-class 设计，而不是单纯缺少 authoring footer

因此，`106` 的目标不是改变 `verify_constraints.py` 的行为，也不是消灭 `frontend_contract_observations` 之类仍然真实存在的 blocker，而是把 `100`~`104` 的 authored footer 补齐到 `092/088` 已冻结的 canonical 形态，确保框架状态面回到真实剩余问题。

## 范围

- **覆盖**：
  - 为 `100`~`104` 的 `spec.md` 补齐 canonical `related_doc` + `frontend_evidence_class` footer
  - 创建 `106` formal docs 与 execution log，作为本次 normalization 的合法 carrier
  - 在 `program-manifest.yaml` 注册 `106`
  - 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `106` 推进到 `107`
  - 用 fresh verification 证明 `missing_footer_key` 已被消除，而 `frontend_contract_observations` 等真实外部缺口仍被保留
- **不覆盖**：
  - 修改 `src/ai_sdlc/core/verify_constraints.py` 或 `program_cmd.py` 的运行时逻辑
  - 补造 `frontend_contract_observations`、browser evidence、policy artifacts 或其他外部输入
  - 改写 `100`~`105` 的主合同语义、dependency graph 或 runtime 行为
  - 把 authoring footer 规范化扩张成新的 evidence-class 规则设计

## 已锁定决策

- `106` 只修 authored spec footer，不改 manifest 已存在的 `frontend_evidence_class` truth
- `100`~`104` 的 `frontend_evidence_class` 固定为 `framework_capability`
- `related_doc` 只回填到各自 `spec.md` 已显式依赖的上游 spec，不凭空新增新的 contract source
- `frontend_contract_observations`、`scope_or_linkage_invalid` 等仍真实存在的 blocker 必须继续保留；`106` 不得伪造“全部完成”
- `106` 作为 governance normalization carrier，只允许修改目标 specs、`program-manifest.yaml`、`project-state.yaml` 与本工单 docs

## 用户故事与验收

### US-106-1 — Maintainer 需要 authored footer 与 manifest mirror 对齐

作为 **framework maintainer**，我希望 `100`~`104` 的 `spec.md` footer 与 manifest mirror 保持一致，这样 `verify constraints` 报出的就是实际治理缺口，而不是作者遗漏。

**验收**：

1. Given 我运行 `uv run ai-sdlc verify constraints`，When `100`~`104` 被扫描，Then 不再出现 `frontend_evidence_class_authoring_malformed:missing_footer_key`
2. Given 我查看 `100`~`104` 的 `spec.md` 尾部，When 我核对 authoring footer，Then 每个 spec 都包含 canonical `related_doc` 与 `frontend_evidence_class: "framework_capability"`

### US-106-2 — Operator 需要 program status 只暴露真实剩余缺口

作为 **operator**，我希望 `program status` 不再把 footer 缺口和真实前端证据缺口混在一起，这样我能明确知道当前剩下的是外部输入问题，而不是 spec 作者格式错误。

**验收**：

1. Given 我运行 `uv run ai-sdlc program status`，When 读取 `100`~`104` 状态，Then 不再看到 `fec=frontend_evidence_class_authoring_malformed:missing_footer_key`
2. Given `frontend_contract_observations` 仍未补齐，When 我查看同一状态面，Then 真实 blocker 继续保留，不会被 `106` 隐藏

## 功能需求

| ID | 需求 |
|----|------|
| FR-106-001 | `106` 必须作为 browser gate mainline 的 footer normalization carrier 被正式定义 |
| FR-106-002 | `100`~`104` 的 `spec.md` 必须补齐 canonical footer，且 `frontend_evidence_class` 固定为 `framework_capability` |
| FR-106-003 | `100`~`104` 的 `related_doc` 只能引用各自 `spec.md` 已声明输入的上游 formal docs |
| FR-106-004 | `106` 不得修改 `verify_constraints.py`、`program_cmd.py` 或任何运行时代码 |
| FR-106-005 | `program-manifest.yaml` 必须注册 `106` canonical entry |
| FR-106-006 | `.ai-sdlc/project/config/project-state.yaml` 必须将 `next_work_item_seq` 从 `106` 推进到 `107` |
| FR-106-007 | `106` 的 fresh verification 必须证明 `missing_footer_key` 已清除，但不得宣称 `frontend_contract_observations` 等外部缺口已解决 |

## 成功标准

- **SC-106-001**：`uv run ai-sdlc verify constraints` 通过，且 `100`~`104` 不再触发 `frontend_evidence_class_authoring_malformed:missing_footer_key`
- **SC-106-002**：`uv run ai-sdlc program status` 中 `100`~`104` 不再显示 `fec=frontend_evidence_class_authoring_malformed:missing_footer_key`
- **SC-106-003**：`100`~`104` 的 `spec.md` footer 与 `program-manifest.yaml` 的 `frontend_evidence_class` mirror 一致
- **SC-106-004**：真实剩余 blocker 仍被诚实暴露，没有被 authoring normalization 伪装为“全部完成”

---
related_doc:
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md"
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "src/ai_sdlc/core/verify_constraints.py"
frontend_evidence_class: "framework_capability"
---
