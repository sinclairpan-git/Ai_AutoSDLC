# 功能规格：Frontend Framework-Only Root Policy Sync Baseline

**功能编号**：`080-frontend-framework-only-root-policy-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../076-frontend-p1-root-close-sync-baseline/spec.md`](../076-frontend-p1-root-close-sync-baseline/spec.md)、[`../077-frontend-contract-observation-backfill-playbook-baseline/spec.md`](../077-frontend-contract-observation-backfill-playbook-baseline/spec.md)、[`../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`](../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md)、[`../079-frontend-framework-only-closure-policy-baseline/spec.md`](../079-frontend-framework-only-closure-policy-baseline/spec.md)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：`080` 是 root honesty-sync carrier。它不发明新的 runtime status，也不把 `068` ~ `071` 改写成 `close`；它只把 `079` 已冻结的 framework-only policy split，同步进根级 rollout wording，让 root 人读真值不再把“consumer implementation evidence 仍缺”误写成“框架侧 capability 尚未具备”。

## 问题定义

根级 `frontend-program-branch-rollout-plan.md` 当前已经诚实区分了两件事：

- `068` ~ `071` 的 docs-only carrier closeout 已分别归档
- root `program status` 仍未把它们视为 `close`

但它仍保留了一个不够精确的旧表述：

- `missing_artifact [frontend_contract_observations]` 仍被直读成“这批项还缺前端实现”
- `077`、`078`、`079` 已经冻结了外部回填 playbook、sample self-check 边界与 framework-only policy split，但这些 truth 还没有同步到根级 rollout wording

在 framework-only repository 里，这会造成新的语义滑坡：

- reviewer 可能把 root non-close 误判成框架能力仍未具备
- operator 可能继续试图在本仓库伪造 consumer observation artifact 来“关单”
- 后续 author 无法从根文档直接读出 `068` ~ `071` 当前到底缺的是哪一层 evidence

因此 `080` 的目标是把根级 wording 再收紧一步：

- 保留 `068` ~ `071` 当前仍非 `close`
- 保留 `missing_artifact [frontend_contract_observations]`
- 但明确这在当前仓库语境下代表 consumer implementation evidence 仍外部缺失，而不是 framework capability 尚未成立

## 范围

- **覆盖**：
  - 新建 `080` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `80`
  - 更新根级 `frontend-program-branch-rollout-plan.md` 的 P1 主线分段、表项与备注
  - 把 `077`、`078`、`079` 已冻结 truth 同步到 root wording
- **不覆盖**：
  - 修改 `program-manifest.yaml`
  - 修改 `program status` / `verify constraints` / runtime implementation
  - retroactively 改写 `068` ~ `071` 为 `close`
  - 生成真实 `frontend-contract-observations.json`
  - 进入 `src/` / `tests/`

## 已锁定决策

- `080` 只同步 root wording，不改变机器状态本身
- `missing_artifact [frontend_contract_observations]` 必须继续保留，不能被文案粉饰为“已解决”
- `079` 的 policy split 必须原样下沉到 root rollout wording
- `077`、`078` 只作为 root explanation input，不会被写成已补齐真实 consumer evidence
- `080` 自身不写入 root rollout table 或 root manifest

## 用户故事与验收

### US-080-1 — Reviewer 需要从 root 文档直接读出当前缺的是哪层 evidence

作为 **reviewer**，我希望在根级 rollout plan 里直接读出 `068` ~ `071` 当前缺的是 consumer implementation evidence，而不是框架 capability，这样我不需要反复回读 `077` ~ `079` 才能判断当前 root non-close 的真实含义。

**验收**：

1. Given 我查看 `frontend-program-branch-rollout-plan.md`，When 我读 P1 主线与 `068` ~ `071` 表项，Then 我能看到 `missing_artifact [frontend_contract_observations]` 仍在，但它被明确解释为 consumer implementation evidence 外部缺口
2. Given 我对照 `079`，When 我查看根级备注，Then 我不会把 root non-close 误解为 framework capability 缺失

### US-080-2 — Operator 需要继续保持 honesty-sync carrier 边界

作为 **operator**，我希望 `080` 继续保持 carrier-only 边界，只同步 root wording 与编号，而不去碰 runtime truth、manifest 或真实 observation 生成。

**验收**：

1. Given 我检查本轮 diff，When 我查看文件面，Then 只看到 `080` docs、`project-state.yaml` 与根级 rollout wording
2. Given 我运行 `uv run ai-sdlc program status`，When 我对比 `068` ~ `071`，Then 当前 root machine truth 仍保持 non-close，不会被本轮 wording sync 偷改

## 功能需求

| ID | 需求 |
|----|------|
| FR-080-001 | `080` 必须明确自己是 root honesty-sync carrier，而不是新的 policy baseline 或 retroactive close |
| FR-080-002 | `080` 必须把 `079` 的 framework-only policy split 同步到根级 rollout wording |
| FR-080-003 | `080` 必须保留 `068` ~ `071` 当前 root `program status` 仍非 `close` 的 truth |
| FR-080-004 | `080` 必须保留 `missing_artifact [frontend_contract_observations]`，并明确其在当前仓库中代表 consumer implementation evidence 外部缺口 |
| FR-080-005 | `080` 必须在根级备注中同步 `077`、`078`、`079` 的角色边界 |
| FR-080-006 | `080` 不得修改 `program-manifest.yaml`、`src/`、`tests/` 或既有 active spec formal docs |
| FR-080-007 | `080` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `79` 推进到 `80` |
| FR-080-008 | `080` 不得把自己写入根级 rollout table 或 root manifest |

## 成功标准

- **SC-080-001**：根级 rollout wording 能直接表达 `068` ~ `071` 当前缺的是 consumer implementation evidence，而不是框架 capability
- **SC-080-002**：`079` 的 policy split 已在 root 文档可见，不再只存在于下游 baseline
- **SC-080-003**：本轮 diff 不修改 `program-manifest.yaml`、`src/`、`tests/` 或 `068` ~ `071` formal docs
- **SC-080-004**：`uv run ai-sdlc program status` 与 root wording 继续一致，均保持 `068` ~ `071` 非 `close`

---
related_doc:
  - "specs/076-frontend-p1-root-close-sync-baseline/spec.md"
  - "specs/077-frontend-contract-observation-backfill-playbook-baseline/spec.md"
  - "specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md"
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "frontend-program-branch-rollout-plan.md"
---
