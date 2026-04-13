# 功能规格：Frontend Evidence Class Readiness Gate Runtime Baseline

**功能编号**：`107-frontend-evidence-class-readiness-gate-runtime-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`](../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md)、[`../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md`](../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md)、[`../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`](../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md)、[`../106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md`](../106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py)

> 口径：`107` 是 `081` 的首次 runtime 落地批次，不再只停留在 prospective contract。它只处理一个已经被 `106` 暴露出来的真实缺口：对已声明 `frontend_evidence_class: framework_capability` 的 future frontend item，`program status` / execute gate 仍然因为缺少真实 `frontend_contract_observations` 而 fail closed。`107` 的目标是在不改写 `consumer_adoption` 语义的前提下，把 framework-capability item 的 readiness gate 调整为 evidence-class-aware。

## 问题定义

`081` 已明确冻结 future machine-gate target：

- `framework_capability` item 的 close 不得再被真实 `frontend_contract_observations` 缺失直接阻塞
- `consumer_adoption` item 若要求真实页面实现证据，仍必须由 canonical observation artifact 满足

但当前 runtime reality 仍停留在更早的统一附件语义：

- [`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py) 的 `_build_frontend_readiness()` 对所有 frontend item 都先读取 runtime attachment
- [`src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py) 的 execute decision 在 attachment 缺失时一律给出 `blocked / scope_or_linkage_invalid`
- 因此 `100`~`106` 这类已经规范化为 `framework_capability` 的 work item，仍在 `program status` 与 execute gates 上暴露为 `missing_artifact`

`106` 只消除了 `missing_footer_key` 噪声，没有也不应该掩盖这个真实运行时缺口。`107` 要做的是把 evidence class 真正接到 frontend readiness gate 上，让 machine truth 与 `081` 冻结的 contract 对齐。

## 范围

- **覆盖**：
  - 创建 `107` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `107`
  - 在 `src/ai_sdlc/core/program_service.py` 读取 canonical `frontend_evidence_class` footer，并把该 truth 传入 frontend readiness / execute decision
  - 在 `src/ai_sdlc/core/frontend_gate_verification.py` 为 `framework_capability` + `missing frontend_contract_observations` 增加非阻塞判定
  - 补充 unit / integration tests，证明 `framework_capability` 与 `consumer_adoption` 走不同 gate 语义
- **不覆盖**：
  - 修改 `081`、`092`、`105`、`106` 的 historical wording
  - 为任何 work item 伪造 `frontend-contract-observations.json`
  - 改变 `consumer_adoption` item 的 close contract
  - 新增新的 evidence class 枚举值
  - 扩张到 `verify constraints`、manifest sync 或 close-check 的其他非必要行为

## 已锁定决策

- `107` 只信任 canonical `spec.md` footer 的 `frontend_evidence_class`；footer 缺失或无效时不得静默豁免
- `framework_capability` 只豁免“缺少真实 `frontend_contract_observations`”这一类 attachment 缺口；`consumer_adoption` 继续维持现状
- `framework_capability` 在豁免路径下应表现为 readiness clear，而不是继续输出 `missing_artifact / blocked`
- 豁免只解决 observation attachment 缺口，不伪装其他真实 blocker 已完成
- `107` 必须让 `program status`、`evaluate_execute_gates()` 与 CLI status surface 对该差异保持一致

## 用户故事与验收

### US-107-1 — Framework Maintainer 需要 framework-capability item 不再被真实 observation artifact 卡死

作为 **framework maintainer**，我希望已经声明 `frontend_evidence_class: framework_capability` 的 future frontend item 在缺少真实 `frontend_contract_observations` 时不再 fail closed，这样 framework-side runtime work item 可以按自身证据闭环，而不是永远挂在外部 consumer artifact 上。

**验收**：

1. Given 某个 future frontend spec 的 canonical footer 声明 `frontend_evidence_class: "framework_capability"`，When `program status` 构建该 spec 的 frontend readiness 且 observation attachment 缺失，Then readiness 不再输出 `missing_artifact / scope_or_linkage_invalid`
2. Given 同样的 spec 已经 `close`，When `evaluate_execute_gates()` 运行，Then 该 spec 不会因为缺少真实 observation artifact 而单独阻塞 execute gate

### US-107-2 — Consumer Adoption Owner 需要既有真实证据语义保持不变

作为 **consumer adoption owner**，我希望 `consumer_adoption` item 继续要求真实 observation artifact，这样 framework-only 豁免不会误伤真实页面实现接入的 close truth。

**验收**：

1. Given 某个 future frontend spec 的 canonical footer 声明 `frontend_evidence_class: "consumer_adoption"`，When observation attachment 缺失，Then readiness 仍保持 `blocked / scope_or_linkage_invalid`
2. Given 同样的 spec 已经 `close`，When `evaluate_execute_gates()` 运行，Then execute gate 仍会因为缺少真实 observation artifact 而失败

### US-107-3 — Operator 需要 CLI status 诚实反映 evidence-class-aware gate

作为 **operator**，我希望 CLI `program status` 直接把 evidence-class-aware 的 readiness truth 暴露出来，这样我能区分“framework item 的非阻塞 observation 缺口”和“consumer adoption item 的真实缺口”。

**验收**：

1. Given `framework_capability` spec 缺少 observation artifact，When 我运行 `uv run ai-sdlc program status`，Then 输出不再出现该 spec 的 `missing_artifact / scope_or_linkage_invalid`
2. Given `consumer_adoption` spec 缺少 observation artifact，When 我运行相同命令，Then 输出仍继续暴露该 blocker

## 边界情况

- canonical footer 缺失、为空或非法时，不得仅凭 manifest mirror 直接豁免
- `framework_capability` 若后续提供了 attachment 并进入其他真实 gate blocker，`107` 不负责伪装这些 blocker 为通过
- 非 frontend spec 或历史未进入 evidence-class contract 的 spec，不在 `107` 的行为承诺面内

## 功能需求

| ID | 需求 |
|----|------|
| FR-107-001 | `107` 必须把 canonical `frontend_evidence_class` 引入 `program/frontend readiness` 判定链路 |
| FR-107-002 | 当 canonical evidence class 为 `framework_capability` 且唯一缺口是 `frontend_contract_observations` 缺失时，execute gate 不得继续返回 `blocked / scope_or_linkage_invalid` |
| FR-107-003 | 当 canonical evidence class 为 `consumer_adoption` 时，缺少 `frontend_contract_observations` 的行为必须保持不变 |
| FR-107-004 | footer 缺失或无效时，`107` 不得静默按 `framework_capability` 豁免 |
| FR-107-005 | `program status`、`evaluate_execute_gates()` 与 CLI status surface 必须对 evidence-class-aware readiness 保持一致 |
| FR-107-006 | `107` 必须补充 focused unit / integration tests 覆盖 framework-capability 豁免与 consumer-adoption 保留两条路径 |
| FR-107-007 | `program-manifest.yaml` 必须注册 `107` canonical entry |

## 成功标准

- **SC-107-001**：`framework_capability` spec 在缺少 observation artifact 时，`build_status()` 返回 `frontend_readiness.execute_gate_state == "ready"`
- **SC-107-002**：`consumer_adoption` spec 在相同缺口下，`build_status()` 仍返回 `blocked / scope_or_linkage_invalid`
- **SC-107-003**：`evaluate_execute_gates()` 对 closed framework-capability spec 不再因 observation artifact 缺失而失败
- **SC-107-004**：CLI `program status` 集成回归能区分 framework-capability 与 consumer-adoption 两条路径

---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
frontend_evidence_class: "framework_capability"
---
