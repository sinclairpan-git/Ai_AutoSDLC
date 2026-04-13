# 功能规格：Frontend Mainline Browser Gate Probe Runtime Implementation Baseline

**功能编号**：`125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 已完成首批切片
**输入**：[`../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`](../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md)、[`../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md`](../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)

> 口径：`125` 是 `120/T13` 的 implementation carrier。它把 browser gate probe runtime 的第一条真实执行链落成代码：从 managed delivery apply artifact 冻结 execution context，创建 gate-run scoped runtime session 与 artifact namespace，materialize structured artifact records / receipts / bundle input，并把 latest probe artifact 写回 canonical memory 路径。`125` 首批切片不会伪装成 browser gate 最终判定，也不会把 `020` execute state、recheck/remediation binding 或真实 Playwright 扩展面混进来。

## 范围

- **覆盖**：
  - canonical managed delivery apply artifact，作为 browser gate 的合法上游输入
  - `BrowserQualityGateExecutionContext`、`BrowserGateProbeRuntimeSession`、artifact records、check receipts、bundle input 的结构化 runtime
  - `program browser-gate-probe` dry-run/execute CLI
  - gate-run scoped artifact namespace 与 `latest.yaml`
  - evidence missing / actual quality blocker 的结构化分类
- **不覆盖**：
  - `020` execute handoff binding
  - bounded replay / remediation closure
  - 多浏览器矩阵或完整 Playwright binary capture

## 已锁定决策

- browser gate probe 只能消费 canonical apply artifact；不得从 CLI 手输零散 scope 参数拼装上下文。
- 一个 `gate_run_id` 对应一个 runtime session、一个 artifact root、一个 bundle input。
- 当前切片对尚未 materialize 的 Playwright smoke / interaction probe 明确记为 `evidence_missing`，不得伪装成 `pass`。
- visual / a11y evidence 若已存在，可被 bridge 成当前 gate run 的结构化 receipts；缺失则同样记为 `evidence_missing`。
- `125` 只产出 probe runtime truth，不直接给 `ready / recheck_required / needs_remediation` 的 execute-level结论。

## 功能需求

| ID | 需求 |
|----|------|
| FR-125-001 | 系统必须先把 managed delivery apply 结果写成 canonical latest artifact，供 browser gate 消费 |
| FR-125-002 | browser gate probe request 必须从 apply artifact 与 latest solution snapshot 冻结唯一 execution context |
| FR-125-003 | execute path 必须创建 gate-run scoped runtime session 与 artifact namespace |
| FR-125-004 | bundle input 只能引用当前 gate run artifacts，不得混入历史 latest snapshot refs |
| FR-125-005 | 当前切片必须结构化区分 `evidence_missing` 与 `actual_quality_blocker` |
| FR-125-006 | CLI 必须明确说明当前切片只 materialize probe runtime truth，不等于 downstream execute readiness 已完成 |

## Exit Criteria

- **SC-125-001**：`program managed-delivery-apply --execute` 能写出 canonical apply artifact
- **SC-125-002**：`program browser-gate-probe --execute` 能写出 latest browser gate artifact 与 gate-run scoped artifact root
- **SC-125-003**：focused tests 能证明 bundle 只引用当前 gate run artifacts，且当前切片不会误报最终 ready

---
related_doc:
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
