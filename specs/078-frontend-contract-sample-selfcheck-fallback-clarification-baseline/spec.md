# 功能规格：Frontend Contract Sample Selfcheck Fallback Clarification Baseline

**功能编号**：`078-frontend-contract-sample-selfcheck-fallback-clarification-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../077-frontend-contract-observation-backfill-playbook-baseline/spec.md`](../077-frontend-contract-observation-backfill-playbook-baseline/spec.md)、[`../../tests/integration/test_cli_scan.py`](../../tests/integration/test_cli_scan.py)、[`../../tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)

> 口径：`078` 不是新的 root closeout carrier，也不是 `068` ~ `071` 的 unblock 实现。它只冻结一条澄清：当没有真实前端源码输入时，框架维护者可以先使用 `065` 定义的内置 sample source 做 `scan -> artifact` 自检，证明流程主线仍可运行；但这条 sample self-check 绝不能被当成 `068` ~ `071` 的真实 close evidence。

## 问题定义

`077` 已经把 observation artifact 的真实 backfill 路径冻结成 operator-facing playbook，但当前存在一个实际认知落差：

- 仓库里确实已经有 `065` 定义的内置 sample frontend source fixture
- 这条 sample fixture 可以在没有外部前端项目时跑通 `scan -> canonical artifact` 主线
- 但它只能证明框架链路可用，不能替代 active spec 的真实业务 observation backfill

如果这层边界不单独冻结，后续很容易出现两种相反的偏差：

- 错误地以为“没有真实前端源码时什么都不能做”，忽略 `065` 的自检价值
- 错误地把 sample self-check 当成 `068` ~ `071` 的 unblock 证据，继续伪推进 root status

因此，`078` 需要把下面这件事变成单一 formal truth：

- 无真实输入时，允许先跑 sample self-check 验证流程
- sample self-check 的产物只能用于框架自检、演示与 smoke
- `068` ~ `071` 的 root blocker 仍然必须由真实实现来源的 canonical artifact 解除

## 范围

- **覆盖**：
  - 冻结 `065` sample self-check 与 `077` external backfill playbook 之间的职责边界
  - 冻结无真实输入时的合法 fallback：sample self-check
  - 冻结 sample self-check 能证明什么、不能证明什么
  - 冻结最小自检命令矩阵：`match / empty / missing-root`
- **不覆盖**：
  - 修改 `065` 或 `077` 已冻结正文
  - 回填 `068` ~ `071` 的真实 observation artifact
  - 修改 `frontend-program-branch-rollout-plan.md`、`program-manifest.yaml`、`src/` 或 `tests/`
  - 把 sample fixture 升格为 runtime fallback、默认 remediation 输入或 active spec close evidence

## 已锁定决策

- `tests/fixtures/frontend-contract-sample-src/**` 仍然只属于框架自检输入源
- sample self-check 的合法用途是证明 `scan -> canonical artifact` 与相关 gate 语义仍可运行
- sample self-check 不会改变 `068` ~ `071` 当前的 `missing_artifact [frontend_contract_observations]` root truth
- `077` 仍然是“真实 backfill 如何执行”的 playbook；`078` 只是补齐“无真实输入时先做什么”的 fallback 口径
- `match` sample 能证明 canonical export 主线可运行
- `empty` sample 能证明 valid-but-empty artifact 语义仍保持失败
- `missing-root` 能证明 scanner/export 不会偷偷 fallback

## 用户故事与验收

### US-078-1 — Maintainer 需要在无真实输入时先验证框架链路还活着

- **Given** 当前拿不到真实前端源码根目录
- **When** maintainer 运行 `065` sample self-check
- **Then** 能确认 `scan` 对 sample fixture 仍可导出 canonical artifact，并区分 `match / empty / missing-root` 三类语义

### US-078-2 — Reviewer 需要区分“流程可运行”与“blocker 已解除”

- **Given** sample self-check 已成功导出 artifact
- **When** reviewer 判断 `068` ~ `071` 是否已 unblock
- **Then** `078` 必须明确答案仍是否定的，因为 active spec 还没有真实实现来源的 canonical artifact

### US-078-3 — Operator 需要一个不伪推进的下一步口径

- **Given** 外部前端源码暂时不可得
- **When** operator 询问“下一步还能做什么”
- **Then** `078` 必须明确可先跑 sample self-check 验证框架主线，但不得宣称 root close 取得进展

## 功能需求

| ID | 需求 |
|----|------|
| FR-078-001 | `078` 必须明确自己是 docs-only clarification baseline，而不是新的 closeout carrier |
| FR-078-002 | `078` 必须明确 `065` sample self-check 仍然存在且可运行 |
| FR-078-003 | `078` 必须明确 sample self-check 的合法目的仅为 framework self-check / demo / smoke |
| FR-078-004 | `078` 必须明确 sample self-check 不能充当 `068` ~ `071` 的真实 backfill evidence |
| FR-078-005 | `078` 必须冻结 `match / empty / missing-root` 的最小命令矩阵与语义说明 |
| FR-078-006 | `078` 必须明确 `077` 与 `078` 的职责分层：前者处理真实 backfill，后者处理无真实输入时的 fallback 自检 |
| FR-078-007 | `078` 不得修改 `065`、`077`、`frontend-program-branch-rollout-plan.md`、`src/` 或 `tests/` |
| FR-078-008 | `078` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `77` 推进到 `78` |

## 最小自检矩阵

- `match`：
  - `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/match --frontend-contract-spec-dir <tmp-spec-dir> --frontend-contract-generated-at <UTC>`
  - 预期：成功导出 canonical artifact，且 observation 数量大于 `0`
- `empty`：
  - `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/empty --frontend-contract-spec-dir <tmp-spec-dir> --frontend-contract-generated-at <UTC>`
  - 预期：成功导出 canonical artifact，但 `observations == []`
- `missing-root`：
  - `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/missing --frontend-contract-spec-dir <tmp-spec-dir> --frontend-contract-generated-at <UTC>`
  - 预期：命令显式失败，不发生隐式 fallback

## 成功标准

- **SC-078-001**：reviewer 能从 `078` 直接读出 sample self-check 与真实 backfill 的职责边界
- **SC-078-002**：maintainer 能在无真实前端输入时，先使用 sample fixture 验证 scanner/export 主线仍可运行
- **SC-078-003**：`078` 不会伪造 `068` ~ `071` 已解除 root blocker 的结论
- **SC-078-004**：本轮 diff 仅新增 `078` formal docs 并把 `project-state.yaml` 推进到 `78`
