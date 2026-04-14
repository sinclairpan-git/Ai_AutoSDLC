# 功能规格：Frontend Contract Observation Backfill Playbook Baseline

**功能编号**：`077-frontend-contract-observation-backfill-playbook-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)、[`../012-frontend-contract-verify-integration/plan.md`](../012-frontend-contract-verify-integration/plan.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_contract_observation_provider.py`](../../src/ai_sdlc/core/frontend_contract_observation_provider.py)、[`../../src/ai_sdlc/scanners/frontend_contract_scanner.py`](../../src/ai_sdlc/scanners/frontend_contract_scanner.py)、[`../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py`](../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py)、[`../../src/ai_sdlc/gates/frontend_contract_gate.py`](../../src/ai_sdlc/gates/frontend_contract_gate.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)

> 口径：`077` 不是新的 root closeout carrier，也不是 `068` ~ `071` 的实现工单。它只把当前外部输入缺口 `missing_artifact [frontend_contract_observations]` 冻结成一份可执行 playbook，说明“必须在真实前端源码上如何生成 canonical observation artifact、如何回填到 active spec、以及什么情况下 gate 仍会失败”。

## 问题定义

当前 root truth 已经稳定到一条很明确的边界：

- `068` ~ `071` 的 docs-only carrier closeout 已归档
- root `program status` 仍未进入 `close`
- 共同 blocker 不是仓库内实现缺失，而是 active spec 仍缺少 canonical `frontend-contract-observations.json`

现有仓库已经具备 observation artifact 的 schema、scanner、CLI export 与 runtime attachment/gate 语义，但还缺一份 operator-facing 的正式执行面，导致后续很容易出现三类不诚实推进：

- 把 `tests/fixtures/frontend-contract-sample-src/` 当成真实前端实现来源
- 手写自由 JSON 回填到 active spec，而不是走 canonical scanner/provider 产物
- 误以为“artifact 存在”就等于 gate 可通过，忽略 empty observations、freshness 或 drift 语义

因此，`077` 要冻结的不是新代码，而是当前框架对外部 frontend observation backfill 的唯一可执行说明：

- 从真实前端源码生成 artifact 的前置条件是什么
- annotation / schema / canonical 输出路径是什么
- 哪个 CLI 命令是当前唯一受支持的标准导出入口
- 回填到 active spec 后还需要跑哪些 read-only 验证

## 范围

- **覆盖**：
  - 冻结 `frontend-contract-observations.json` 的 canonical 生成/回填 playbook
  - 冻结真实前端源码、annotation marker、spec 目标目录与最小验证命令
  - 冻结当前 `068` ~ `071` 的 backfill 目标面与非目标
  - 冻结 gate 失败语义：missing artifact、invalid artifact、valid empty、drift
- **不覆盖**：
  - 在本仓库内伪造或生成真实业务前端 observation artifact
  - 修改 `program-manifest.yaml`、root DAG、`068` ~ `071` formal docs 或任意 `src/` / `tests/`
  - 新增 CLI 参数、provider registry、自动回填器或外部仓库适配脚本
  - 把 sample fixture 或 test helper 冒充真实 backfill 证据

## 已锁定决策

- canonical artifact 文件名固定为 `frontend-contract-observations.json`
- canonical schema version 固定为 `frontend-contract-observations/v1`
- canonical 回填位置固定为目标 spec 目录下的 `frontend-contract-observations.json`
- 当前标准导出入口是：
  - `uv run ai-sdlc scan <frontend_source_root> --frontend-contract-spec-dir <target_spec_dir> --frontend-contract-generated-at <UTC timestamp>`
- 当前标准 scanner 只识别带有 `ai-sdlc:frontend-contract-observation` marker 的 `.js/.jsx/.ts/.tsx/.vue/.mjs/.cjs` 文件
- 真实 backfill 必须来自外部 frontend 实现仓库；`tests/fixtures/frontend-contract-sample-src/` 只用于框架自检，不可作为 active spec 的真实输入
- attached artifact 若 `observations` 为空，gate 仍失败；artifact 存在不等于 contract truth 已满足
- 当前 CLI export 产物天然携带 `source_digest`，因此 freshness 可验证；CLI 还未暴露显式 `source_revision` 注入参数
- 本 spec 的 `frontend_evidence_class` 仅用于框架侧 capability 分类与 `program status` 口径对齐；`missing_artifact [frontend_contract_observations]` 对 consumer adoption 仍然是 blocker，`ready/advisory_only` 不代表已解除

## 用户故事与验收

### US-077-1 — Program Maintainer 需要一份诚实的外部 backfill 手册

- **Given** `068` ~ `071` 因 `missing_artifact [frontend_contract_observations]` 卡在 root
- **When** maintainer 准备去真实前端项目生成 observation artifact
- **Then** `077` 能直接给出前置条件、导出命令、目标 spec 目录和验证步骤

### US-077-2 — Operator 需要知道什么不算有效回填

- **Given** operator 看到 sample fixture、手写 JSON 或 empty observation artifact
- **When** 准备把这些内容塞回 active spec
- **Then** `077` 已明确这些都不能当作真实 close evidence

### US-077-3 — Reviewer 需要快速判断 artifact 是否满足 gate

- **Given** 某个 active spec 已经出现 `frontend-contract-observations.json`
- **When** reviewer 对照 `077` 审核 provenance、freshness 与 observation payload
- **Then** 能直接判断它是 missing / invalid / empty / drift / clean 哪一类状态

## 功能需求

| ID | 需求 |
|----|------|
| FR-077-001 | `077` 必须明确自己是 docs-only playbook baseline，而不是新的 root closeout carrier |
| FR-077-002 | `077` 必须明确当前 blocker 是 `missing_artifact [frontend_contract_observations]`，而不是本仓库 scanner/CLI 不存在 |
| FR-077-003 | `077` 必须冻结 canonical artifact 文件名、schema version 与目标 spec 路径 |
| FR-077-004 | `077` 必须冻结当前标准导出命令与所需参数 |
| FR-077-005 | `077` 必须明确 scanner marker、支持文件后缀与 duplicate/invalid JSON 的失败条件 |
| FR-077-006 | `077` 必须明确 observation payload 至少包含 `page_id`、`recipe_id`，并可附带 `i18n_keys`、`validation_fields`、`new_legacy_usages` |
| FR-077-007 | `077` 必须明确真实 backfill 输入源必须是外部 frontend 实现仓库，而不是本仓库 sample fixture |
| FR-077-008 | `077` 必须明确 empty observations、invalid artifact 与 drift 都不能当作 unblock evidence |
| FR-077-009 | `077` 必须列出当前 first-wave 回填目标 `068`、`069`、`070`、`071` 的 spec 目录 |
| FR-077-010 | `077` 必须明确回填后的最小 read-only 验证步骤 |
| FR-077-011 | `077` 不得修改 `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`、`068` ~ `071` formal docs、`src/` 或 `tests/` |
| FR-077-012 | `077` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `76` 推进到 `77` |

## 当前回填目标

- `specs/068-frontend-p1-page-recipe-expansion-baseline`
- `specs/069-frontend-p1-governance-diagnostics-drift-baseline`
- `specs/070-frontend-p1-recheck-remediation-feedback-baseline`
- `specs/071-frontend-p1-visual-a11y-foundation-baseline`

> 说明：`077` 只冻结 first-wave target list，不声称这些 spec 已经拿到了真实 observation artifact。

## 成功标准

- **SC-077-001**：reviewer 能从 `077` 直接读出 observation artifact 的生成入口、schema、回填位置与失败语义
- **SC-077-002**：operator 能区分真实外部 backfill 与 sample fixture / 手写 JSON / empty artifact
- **SC-077-003**：`077` 能为 `068` ~ `071` 提供明确的 target spec list 与最小验证命令
- **SC-077-004**：本轮 diff 仅新增 `077` formal docs 并把 `project-state.yaml` 推进到 `77`
- **SC-077-005**：`077` 不会伪造“artifact 已生成”或“root 已解除 blocker”的结论
---
related_doc:
  - "frontend-program-branch-rollout-plan.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_contract_observation_provider.py"
  - "src/ai_sdlc/scanners/frontend_contract_scanner.py"
  - "src/ai_sdlc/core/frontend_contract_runtime_attachment.py"
  - "src/ai_sdlc/gates/frontend_contract_gate.py"
  - "src/ai_sdlc/cli/commands.py"
frontend_evidence_class: "framework_capability"
---
