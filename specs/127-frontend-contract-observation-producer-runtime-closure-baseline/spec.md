# 功能规格：Frontend Contract Observation Producer Runtime Closure Baseline

**功能编号**：`127-frontend-contract-observation-producer-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 已完成首批闭环
**输入**：[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../077-frontend-contract-observation-backfill-playbook-baseline/spec.md`](../077-frontend-contract-observation-backfill-playbook-baseline/spec.md)、[`../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`](../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md)、[`../../src/ai_sdlc/scanners/frontend_contract_scanner.py`](../../src/ai_sdlc/scanners/frontend_contract_scanner.py)、[`../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py`](../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py)、[`../../src/ai_sdlc/core/frontend_contract_verification.py`](../../src/ai_sdlc/core/frontend_contract_verification.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)

> 口径：`127` 是 `120/T21` 的 implementation carrier。它不重写 `012/013/065/077/078` 的 formal truth，而是把 observation scanner / producer 已存在的实现真正闭成 runtime 主链：`scan` 导出需要直出 canonical source profile，sample self-check artifact 与真实 consumer evidence 要在 runtime 中可区分，且 active contract/gate self-check surface 与普通 `program` surface 不能再把 sample artifact 误当成普通 spec 的真实证据。

## 问题定义

`013` 已冻结 canonical observation artifact contract，`065/077/078` 又分别冻结了 sample self-check、真实 backfill playbook 与二者的职责边界。但当前仓库仍有三处运行时缺口：

- `scan` 虽然已经能导出 canonical artifact，但 operator 不能从导出面直接看出当前产物到底是 sample self-check 还是 consumer evidence
- runtime attachment / verify / gate 只消费 artifact 文件本身，还没有把 sample self-check 与真实 consumer evidence 做成机器可判定的 source profile
- `program` readiness / remediation 还会把 sample-derived artifact 视为普通 attached input，导致非自检 spec 可能被误判为已具备真实 observation evidence

`127` 的目标是补齐这条 runtime split：保持 canonical schema 不变，只在 runtime 中根据 provenance/source_ref 解析 source profile，并把 `sample_selfcheck` 限定在显式 self-check work item；其它 spec 若拿到 sample artifact，必须诚实回退为 `frontend_contract_observations` 仍待真实回填。

## 范围

- **覆盖**：
  - 为 canonical observation artifact 增加 runtime source profile 判定
  - `scan` CLI 导出时直出 `sample_selfcheck / consumer_evidence / opaque` profile
  - runtime attachment 挂接 source profile / requirement / issue
  - verify / gate / program 将 sample self-check artifact 与真实 consumer evidence 区分处理
  - 将 `T21` implementation carrier 注册进 manifest/backlog/project-state
- **不覆盖**：
  - 修改 `frontend-contract-observations.json` schema version
  - 新增 provider registry、外部 source root discovery 或自动 backfill
  - 把 sample fixture 升级为默认 remediation 输入或 active spec close evidence
  - 补齐 `T22` 的完整 runtime attachment/gate/readiness 聚合 closeout

## 已锁定决策

- canonical observation artifact 继续沿用 `frontend-contract-observations/v1`，不为 `127` 引入新 schema
- source profile 仅由 runtime 基于现有 provenance/source_ref 判定，不向 operator 泄漏 sample fixture 的真实路径
- `sample_selfcheck` 只允许用于显式 framework self-check scope；普通 spec 若附着 sample artifact，必须重新暴露 `frontend_contract_observations` 缺口
- `consumer_evidence` 仍然表示“来自显式 source tree 的 scanner 产物”；manual / unknown provider 统一保留为 `opaque`
- remediation 下一步仍统一落回 `uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir <spec-dir>`，不允许 runtime 推断默认 source root

## 功能需求

| ID | 需求 |
|----|------|
| FR-127-001 | `scan` CLI 在 canonical export 成功后，必须输出当前 observation artifact 的 runtime source profile |
| FR-127-002 | runtime policy 必须能将 observation artifact 至少区分为 `sample_selfcheck`、`consumer_evidence`、`opaque` |
| FR-127-003 | runtime attachment 必须保留 source profile、requirement state 与抽象 issue message，供后续 verify / program 使用 |
| FR-127-004 | active `012/018` contract/gate self-check runtime 在读取 canonical artifact 时，必须能够区分 `sample_selfcheck` 与普通 evidence profile，并只在允许 scope 上放行 sample artifact |
| FR-127-005 | `program` readiness / remediation 必须把普通 spec 上的 `sample_selfcheck` artifact 视为需要重新 materialize consumer evidence 的 blocker |
| FR-127-006 | `127` 不得泄漏 sample fixture 实际路径；runtime 只允许输出抽象 source profile 与抽象 issue message |
| FR-127-007 | `127` 必须保持 `012` / `018` 这类显式 self-check 链路可继续消费 sample artifact，以免回归已冻结自检主线 |

## Exit Criteria

- **SC-127-001**：`scan` 成功导出时可以稳定看到 source profile，operator 不再只能靠路径猜测产物性质
- **SC-127-002**：普通 spec 附着 sample-derived observation artifact 时，`program` 与 verify/gate 不再误判为 ready
- **SC-127-003**：`012/018` 既有 sample self-check 验证链路保持可运行，不被新的 runtime split 误伤

---
related_doc:
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/077-frontend-contract-observation-backfill-playbook-baseline/spec.md"
  - "specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md"
  - "src/ai_sdlc/scanners/frontend_contract_scanner.py"
  - "src/ai_sdlc/core/frontend_contract_runtime_attachment.py"
  - "src/ai_sdlc/core/frontend_contract_verification.py"
  - "src/ai_sdlc/core/program_service.py"
frontend_evidence_class: "framework_capability"
---
