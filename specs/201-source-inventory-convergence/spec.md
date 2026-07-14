# 功能规格：Source Inventory Convergence

**功能编号**：`201-source-inventory-convergence`
**创建日期**：2026-07-14
**状态**：设计评审中
**父项**：WI-196 `GAP-11 / T54`
**基线 revision**：`c737eda056b2c86a6110ab32db237c417ee19a04`
**输入**：逐项关闭 33 个 unmapped source 与 11 个 missing source；真实例外才允许携带 owner、原因和到期日。本工作项不改变产品运行时行为，也不启动 WP-01～WP-07。

## 1. 问题与范围

mainline 基线 `program-manifest.yaml` 的 source inventory 为 `total=1061`、`mapped=1028`、`unmapped=33`、`missing=11`，整体为 `migration_pending`。WI-201 初始化进入 manifest 后，实时投影为 `total=1066`、`mapped=1033`、`unmapped=33`、`missing=12`。33 个 unmapped source 全部是仓库内已存在但尚未登记的 release 文档；历史 11 个 missing source 与当前新增的 1 个 missing source都是 `development-summary.md`。现有证据表明这些债务可以直接修复，不需要新增 exception/waiver 机制。

现有 runtime 有一项必须显式防护的语义：inventory 的 `complete` 只由 unmapped 集合决定，`missing_sources` 非零时 audit 仍可能返回 ready/exit 0。因此本工作项绝不能把 `state=complete` 单独当作成功；最终必须同时断言 `missing_sources=0`，并且在 12 份 summary 全部落盘前不得持久化 ready snapshot。本项不顺手改变这项既有 runtime 语义。

本工作项覆盖：

- 在现有 `source_registry` schema 内登记 33 个 release 文档；
- 为 11 个历史工作项补齐基于现存规格、执行日志、提交与 PR 证据的简明 summary；
- 为 WI-201 自身提供 `development-summary.md`，避免本次 work item 反向制造新 missing source；
- 用仓库级集成测试阻止 unmapped/missing source 回归；
- 刷新并审计 canonical truth snapshot，使 source inventory 完整且整体 ready。

明确不覆盖：

- 不修改 `src/ai_sdlc/**`、source discovery/runtime 逻辑或公共 schema；
- 不修改 33 个 release 文档正文，不重写历史 spec/plan/tasks/log/status；
- 不引入 exception、waiver、owner/expiry 新字段或第二套 source truth；
- 不执行 WP-01～WP-07 的结构减重，不发布新版本，不更新全局 CLI；
- 不把“治理基线已交付”写成“全部减重路线已完成”。

## 2. 可复现基线与问题台账

### 2.1 Unmapped release 文档（33）

| 路径集合 | 数量 | 目标映射 |
|---|---:|---|
| `docs/releases/v0.7.5.md`～`docs/releases/v0.7.19.md` | 15 | `source_type=release_doc`, `truth_layer=release` |
| `docs/releases/v0.8.0.md`～`docs/releases/v0.8.10.md` | 11 | `source_type=release_doc`, `truth_layer=release` |
| `docs/releases/v0.9.0.md`～`docs/releases/v0.9.6.md` | 7 | `source_type=release_doc`, `truth_layer=release` |

每个路径必须逐项、唯一地出现在 `program-manifest.yaml.source_registry` 中，不允许通过放宽 discovery 或过滤 warning 来“清零”。

### 2.2 Missing development summary（11）

1. `183-production-feedback-guard-adoption`
2. `186-agentops-production-runtime-integration`
3. `188-vue3-public-primevue-default-provider-governance`
4. `189-loop-engine-local-adversarial-pr-review`
5. `190-loop-engine-status-list-baseline`
6. `191-loop-engine-next-action-guidance-baseline`
7. `192-loop-engine-requirement-loop-runtime`
8. `193-loop-engine-design-contract-loop-runtime`
9. `194-loop-engine-implementation-loop-runtime`
10. `195-loop-engine-frontend-evidence-loop-runtime`
11. `196-ai-sdlc-lean-code-self-reduction-governance`

上述 summary 必须只陈述可由对应 spec、tasks、execution log、merge commit 或 PR 证明的结果。WI-196 只能表述为治理基线已交付、子路线仍在推进，不能伪造整体减重完成。

## 3. 用户故事与独立验收

### US-01：完整登记 release truth（P0）

作为框架维护者，我希望所有已存在的 release 文档都进入 canonical source registry，以便 truth audit 不再把合法历史文档当作迁移债务。

**独立测试**：在根仓库构建 truth snapshot，断言 `unmapped_sources == 0`、不存在 unmapped warning，且 33 个 registry 三元组逐项精确等于 `path + release_doc + release`。

### US-02：诚实补齐工作项总结（P0）

作为后续维护者，我希望每个已登记 work item 都有可追溯的开发总结，以便 source inventory 完整，同时不把计划或局部交付冒充为完成事实。

**独立测试**：truth snapshot 断言 `missing_sources == 0`；人工/agent 只读复核 11 个历史 summary 的状态措辞与证据 URI。

### US-03：阻止清单债务复发（P0）

作为发布负责人，我希望仓库集成测试和 truth audit 对新增 unmapped/missing source fail closed，以便相同债务不能在后续 PR 中静默恢复。

**独立测试**：新增断言先在基线 RED，补齐 registry/summary 后 GREEN；连续两次 truth sync 的语义结果相同。

## 4. 影响分析与兼容合同

### 4.1 文件与符号

| 范围 | 处理 | 说明 |
|---|---|---|
| `program-manifest.yaml.source_registry` | 修改 | 新增且仅新增 33 个 release 映射 |
| 11 个历史 WI 的 `development-summary.md` | 新增 | 基于已有证据做简明事实归档 |
| `specs/201-source-inventory-convergence/development-summary.md` | 新增 | 防止当前 WI 产生新 missing source |
| `tests/integration/test_repo_program_manifest.py` | 修改 | 在现有根仓库测试中增加完整性断言 |
| `program-manifest.yaml.truth_snapshot` | 生成更新 | 由 canonical sync 刷新，不手工伪造 |
| `src/ai_sdlc/core/program_service.py` discovery/inventory 构建逻辑 | 只读验证 | 不修改产品实现 |

### 4.2 受影响 Compatibility Contracts

- **CC-01**：`program truth audit` 的命令/参数/JSON schema 不变；stdout 中 migration pending count=`33` 及有限 pending-source 预览按预期消失。
- **CC-02**：同一 clean checkout 上 audit 因 33 个 unmapped source 产生的 exit `1` 收敛为 ready exit `0`，这是本工作项唯一有意退出行为差异；missing 必须由独立计数断言，不能用 exit code 代替。
- **CC-03**：artifact 路径与 schema 不变；registry 与 snapshot 内容按本规格预期更新。
- **CC-06**：truth sync 必须幂等；第二次执行不产生新的语义差异或 source debt。
- **不影响 CC-04/05/07/08**：无状态机、授权边界、平台执行路径或兄弟项目 CLI 行为变更；若验证发现影响则停止并重新评审范围。

### 4.3 NC-01～NC-06

| 合同 | 本工作项冻结内容 |
|---|---|
| NC-01 | mainline observed=`1061/1028/33/11`，WI-201 投影=`1066/1033/33/12`；expected=`1066/1066/0/0 + close 202/202 + complete + ready + exit 0`；基线 revision 见页首 |
| NC-02 | 影响文件/符号和 CC 见 §4.1～4.2；不确定影响一律停止执行 |
| NC-03 | 产品 LOC/文件/公共抽象/schema=`0`；registry 恰好 33 entries/99 YAML 行；历史 summary 11 个 + 当前 summary 1 个，每个不超过 25 个非空正文行；测试只改 1 个现有文件，新增断言不超过 12 行 |
| NC-04 | 先让仓库集成测试在基线因 33/11 失败，再以最小 truth/docs 修复转绿；执行 targeted、full、Ruff、constraints、truth audit |
| NC-05 | owner=AI-SDLC framework maintainers；在 final candidate 的临时 clean worktree 反向 revert 本 PR 全部提交，断言精确恢复 1061/1028/33/11 与两个 `closed/ready/[]`；生成 snapshot 由 sync 重建 |
| NC-06 | 不混入运行时代码、减重包、release 内容重写、历史状态重写或无关 truth 清仓 |

Reduction Contract（RC-01～RC-10）不适用：本项是 WI-196 明确登记的 L2 truth 修复，不是结构减重实现包。

## 5. 功能需求

- **FR-01**：执行前必须记录目标 checkout、基线 inventory、33/11 精确集合和复现命令。
- **FR-02**：必须为 §2.1 的 33 个路径逐项新增唯一 registry entry，沿用现有 `path/source_type/truth_layer` schema；测试必须精确检查三元组，不能只检查 path mapped。
- **FR-03**：不得通过忽略 release 文档、过滤 warning、修改 completeness 判定或新增例外机制达成指标。
- **FR-04**：必须补齐 §2.2 的 11 个历史 summary，并为每项保留状态、已交付事实、验证/合并证据和未完成边界。
- **FR-05**：必须在最终 truth sync 前新增 WI-201 summary，避免修复提交新增第 12 个 missing source。
- **FR-06**：任何无法由现有证据支持的 historical completion claim 必须删除；若某 summary 无法诚实完成，则停止实现并按父项要求另行设计 owner/reason/expiry 例外，不得临时造字段。
- **FR-07**：必须在 `test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence` 或同一现有仓库集成测试文件中先增加完整性断言，保留 RED/GREEN 证据。
- **FR-08**：最终 snapshot 必须精确满足 `total_sources=1066`、`mapped_sources=1066`、`unmapped_sources=0`、`missing_sources=0`、close layer=`202/202`、inventory state `complete`、整体 state `ready`、audit exit `0`；不得依赖 state 间接推断 missing 为零。
- **FR-09**：必须在持久化 snapshot 前完成并写回 truth dry-run、manifest validate、constraints、targeted/full pytest、Ruff、预算与 `git diff --check`；最后一次 `truth sync --execute --yes` 之后只允许提交 snapshot 和运行只读验证，禁止再修改 inventory-covered 文件。
- **FR-10**：formal docs 与最终 clean HEAD 分别由“兼容/真实性/回退安全”和“精简/直接性/过度实现”两个独立 agent 对抗评审；formal hash 必须使用 plan §5 Phase 0 冻结的唯一命令计算，两者必须先复算相同 digest 再对同一 hash/HEAD 给出 PASS，内容或 hash 算法变化使旧 PASS 失效。最终 HEAD verdict 只写入外部 task/PR receipt，不回写被审分支；若分支再变，双 PASS 全部失效。
- **FR-11**：必须通过独立 PR、GitHub Codex review、required checks 和 mainline fresh-checkout smoke 交付；外部 receipt 必须记录 reviewed HEAD、merge SHA、相关路径 tree/diff 等价、snapshot 三元组、精确 source/close/capability 集合和命令退出码。
- **FR-13**：final clean HEAD 必须在临时 worktree 对冻结基线 `c737eda056b2c86a6110ab32db237c417ee19a04..HEAD` 全部提交按逆序执行 `git revert --no-commit` 演练；回退态 tree 等于冻结基线，validate 通过、audit 因且仅因 33 个 unmapped source 退出 1，另行断言 `missing=11`，source 恢复 1061/1028/33/11、两个 capability 保持 `closed/ready/[]`，临时 worktree 删除后候选树无残留。
- **FR-12**：任何产品代码、新公共 schema、新 fixture 文件、release 正文变化或 WP-01～WP-07 工作均视为范围蔓延并阻断交付。

## 6. 边界与停止条件

- 同一路径已登记、path 大小写或排序冲突：停止并修正 registry，而不是重复登记。
- summary 与历史状态/PR 证据冲突：以可验证证据为准，降级措辞；无法判断则停止。
- sync 后出现非 §2 所列的新 unmapped/missing/invalid/stale：视为未登记范围变化，停止并重新做影响分析。
- audit 仍非 ready，或任何 capability blocker 复发：停止；不得把非零退出码标成通过。
- audit 在 `missing_sources != 0` 时返回 ready/exit 0：视为假绿并停止；不得持久化或交付该 snapshot。
- `frontend-mainline-delivery` 或 `agent-adapter-verified-host-ingress` 任一 capability 不再保持 `closed/ready/[]`：停止并回滚当前候选。
- 最后一次 execute sync 后任何 inventory-covered 文件、registry authoring 内容或被审 HEAD 发生变化：snapshot/终审证据失效，必须重新执行完整冻结流程。
- CLI 生成的 `.cursor/rules/ai-sdlc.mdc` 工作区副作用必须用 `apply_patch` 恢复到目标 HEAD 内容，不能混入提交。

## 7. 成功标准

- **SC-01**：33 个 release 文档逐项映射，registry 无重复，`unmapped_sources=0`。
- **SC-02**：11 个历史 summary 与 WI-201 summary 均存在且有证据约束，`missing_sources=0`。
- **SC-03**：最终为 `1066/1066/0/0`、close=`202/202`，inventory=`complete`，snapshot=`fresh`，program=`ready`，audit exit `0`，无 migration warning；两个既有 capability 前后均保持 `closed/ready/[]`。
- **SC-04**：仓库集成测试有可审计 RED/GREEN 记录；targeted/full pytest、Ruff、constraints、validate、幂等、diff check 与整分支 rollback drill 全部通过。
- **SC-05**：产品代码、公共抽象和 schema 变更为 0；实际改动不超过 NC-03 预算。
- **SC-06**：两个对抗 agent 对同一 formal hash 和最终 clean HEAD 均独立 PASS；外部 receipt 不改变 reviewed HEAD；PR Codex review 无 actionable finding，required checks 全绿，merge tree 与 reviewed tree 相关路径等价，mainline smoke 复现 SC-03。
