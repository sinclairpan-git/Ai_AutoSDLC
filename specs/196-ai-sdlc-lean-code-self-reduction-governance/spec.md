# 功能规格：AI-SDLC 框架缺口修复与自身减重

**功能编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**创建日期**：2026-07-12
**状态**：closure-source candidate；merge 后 `closed`
**类型**：治理总项 / 独立实现子项路线图
**当前分支边界**：只修改治理文档和 AI-SDLC 真值文件；运行时代码和规则由后续独立 work item
修改。测试默认同样后置，唯一例外是 FR-12 定义的 root exact truth 两个值机械更新。

## 1. 问题与基线

基线 revision：`c0f333c82c6f096ea8e74e57378eb7d7368f276c`。

- `src/ai_sdlc/`：215 个 Python 文件、107,482 物理行；61 个文件超过 400 行，15 个不少于 1,000 行。
- 3,348 个函数中，357 个超过 50 行，159 个不少于 100 行。
- `program_service.py`：17,369 行，`ProgramService` 249 个方法；`program_cmd.py`：7,062 行。
- `tests/`：189 个 Python 文件、109,872 物理行；55 个文件超过 400 行，21 个不少于 1,000 行。
- 只读结构审计识别到 13 个同形 `RequestStep`、11 个同形 `Result`、77 对高度相似长 CLI 命令，以及多组 dedupe、路径、YAML/JSON helper 候选。
- 当前统计只覆盖仓库中的 Python 产品代码和测试代码，不包含 `.venv`、缓存、worktree 与发布包。`src/ai_sdlc/` 未标记 vendored Python；生成资产和测试 fixture 必须由 WP-02 的路径分类器独立统计，不得混入手写代码预算。
- 基线全量测试：`3145 passed, 3 skipped in 443.28s`。

行数和相似度只用于发现候选，不直接证明可以删除。任何减重都必须同时满足兼容契约和 Reduction Contract。

## 2. 目标与范围

1. 将已证实的框架功能缺口、结构性臃肿和关联治理债务放在同一台账中管理。
2. 冻结 Lean Code 原则、公共兼容契约、量化减重合同和停止/回退条件。
3. 先修复会破坏后续实施的基础缺陷，再按目标切片建立最小充分的行为基线。
4. 每个缺陷或减重切片使用独立 work item、分支、PR 和回退，不做大爆炸重写。
5. 由两个本地独立只读 Agent 分别从兼容安全与精简效率维度评审同一内容哈希，双方 PASS 后启动首个实现子项。

当前治理总项不删除公共命令，不改变参数、默认值、退出码、artifact schema、状态语义或授权边界，不发布版本，也不更新全局 CLI。

### 2.1 路线终止的投入产出依据

本专项已持续接近7天，完成时间仍不可预测，token、评审、CI和协调成本持续上升，并阻塞正常特性开发。
当前已合入family ledger产品raw净删653行，相对初始`src/ai_sdlc` 107,482行基线仅约0.61%；即使WI217
GO再净删358行，累计1,011行也仅约0.94%，仍远低于RC-08的10%组合目标。该粗算只用于判断路线级
投入产出，不夸大为全仓精确净变化。

减重必须服务可维护性和特性交付，而不能替代特性交付。继续为不可达组合目标消耗无限token与日历时间
没有产品意义，因此WI217被设为最后工作项；剩余结构债降为非阻塞backlog，正常特性开发恢复优先级。

## 3. 统一问题台账

所有证据默认对应基线 revision；`program-manifest.yaml` 证据必须以目标提交内的 `truth_snapshot.repo_revision`、`generated_at`、`snapshot_hash` 三元组为准，并通过 `uv run ai-sdlc program truth audit` 复核。规范不得硬编码会随 truth sync 变化的 snapshot hash。

复核必须在目标 commit/PR checkout 上执行并记录目标 commit、三元组、audit 输出与退出码。当前交付只接受
`snapshot_state=fresh`、整体 `state=ready`、退出码 0，且 manifest 无 `invalid/stale`、validation error 或
blocker。唯一允许的 active-child pre-close 状态是：恰好一个已映射、`exists=false`、
`source_type=development_summary`、`truth_layer=close` 的当前 child `development-summary.md`，且 close totals/materialized
精确为 `N/(N-1)`；它表示尚未伪造的未来 closure，不是 GAP-11 回归。该 child closure 必须把 missing
归零并恢复 `N/N`。capability blocking refs 与 source inventory 精确集合仍须记录；任一其他 missing、任一
unmapped、超过一个 pre-close missing、non-ready、非零退出码、集合未解释变化或证据缺失均 fail-closed，
并在命中 GAP-09～GAP-11 时登记证据、重开对应 GAP，不得以 `PASS_WITH_REGISTERED_DEBT` 继续。

| 编号 | 类别 | 事实证据 / 复现入口 | 目标与责任 | 减重关键路径 |
|---|---|---|---|---|
| GAP-01 | 非阻塞结构债 backlog | 宪章规定 400 行/50 行，但当前 `uv run ai-sdlc verify constraints` 对历史超限无 BLOCKER；WI-202 No-Go 保留 | 不再创建减重 WI；只在正常特性改动自然触及时局部治理 | 否 |
| GAP-02 | 兼容缺口 | 现有测试分散，缺少目标切片统一的 CLI/artifact/状态/副作用 differential 基线 | WP-01：最小充分 Characterization/Golden | 是 |
| GAP-03 | 非阻塞结构债 backlog | `ProgramService` T66 两条路线已由 WI-216 证明 NO-GO，legacy保持 | 不重启减重路线；正常特性可按独立需求演进 | 否 |
| GAP-04 | 非阻塞结构债 backlog | `program_cmd.py` stage family 未实施 | 不创建减重 WI；正常特性可按独立需求演进 | 否 |
| GAP-05 | 已实现局部收益；剩余为非阻塞 backlog | WI-205、WI-206、WI-210、WI-211及WI-217各关闭一个 exact family；累计产品raw净删1,011行 | 已关闭family保留回退证据；不再选择新family reduction WI | 否 |
| GAP-06 | 非阻塞结构债 backlog | 6个 `build_p*_baseline` builder 候选未实施 | 不创建减重 WI；保留候选事实但不阻塞特性开发 | 否 |
| GAP-07 | 已关闭 | WI-197 / PR #121 / merge `4802596f`：adapter mutation 不再与 clean-tree preflight 自冲突 | T51 已完成；权威证据见 WI-197 execution log §6.3～6.7 | 否 |
| GAP-08 | 已关闭 | WI-198 / PR #122 / merge `68150d3f`：resume working set 以 active linked WI 为准 | T52 已完成；权威证据见 WI-198 execution log §3～§8 | 否 |
| GAP-09 | 已关闭 | WI-199 / PR #123 / merge `208a34c8`：framework capability 与 consumer inheritance fail-closed 分离 | T53A 已完成；回退整个 WI-199 会重开本项 | 否 |
| GAP-10 | 已关闭 | WI-200 / PR #124 / merge `c737eda0`：repository capability 与本机会话 consumption fail-closed 分离 | T53B 已完成；runtime admission 仍独立诊断 | 否 |
| GAP-11 | 已关闭 | WI-201 / PR #125 / merge `d19c8b7d`：source inventory 收敛为 complete、unmapped=0、missing=0 | T54 已完成；新增 source 继续 fail-closed | 否 |
| GAP-12 | 已关闭 | WI-207：formal PR #140、implementation PR #139、test-isolation repair PR #141；merge `8d8b8f96` 的 fresh-main real-hook/focused/full/Ruff/治理门禁全绿且 repository state clean | T55 已完成；回退 PR #139 或 #141 会重开本项 | 否 |
| GAP-13 | 已关闭 | WI-208 / PR #143 / merge `f51c176a`：共同 builder 以 canonical sources portable/lossless 重建 root/scoped resume-pack，保留 branch、active files、context 与 raw-byte convergence | T56 已完成；fresh-main relocation/focused/full/Ruff/治理门禁全绿，保护文件与 clean state 不变；回退 PR #143 会重开本项 | 否 |
| GAP-14 | 已关闭 | `comment_policy._is_comment_line()` 曾按 stripped diff line 判断前缀；WI-209 在 `main@85bdedac` 复现 single/double quoted scalar 续行均产生 1 finding，而 PyYAML token 实际跨越该内容行 | T57 / WI-209：formal PR #145/merge `46156c24` 与 implementation PR #146/merge `31aad572`；Round 15 双 Agent、Codex current-head、22/22 checks 与 fresh-main focused/full/Ruff/治理/clean-state 全部通过；回退 PR #146 会重开，且本项不计 RC-08 | 否 |
| GAP-15 | 已关闭（本 closure receipt merge 生效） | `main@e184c8e2`：`program validate` 前后 `.cursor/rules/ai-sdlc.mdc` SHA-256 均为 `d5f04acf...0b6a`；只读 `workitem plan-check --json` 却输出 `IDE adapter (cursor): installed 1 file(s)` 并将 SHA 改为 `02d9656d...e134`，产生 `+18/-6` tracked diff。根因是 `workitem` callback 对除 `init` 外全部子命令无条件调用 adapter hook | T58 / WI-214：formal PR #160、amendment PR #161、implementation PR #162 / merge `2845fedc`；reviewed tree=`03b4a1ff`，本地 LEAN/SAFETY 同身份 PASS0，22/22 checks，detached fresh-main full=`3303 passed, 3 skipped`、targeted=`50 passed`、truth=`ready/fresh 1126/1126`。Lifecycle delivery final tree=`3f6698d7` 同身份双 PASS0，PR #163 exact-head 10/10 checks、merge=`60fe6d90` 与 detached fresh-main 治理/scope/clean 全绿；只隔离五个只读命令的隐式 refresh，保留 `init/link` 既有写语义。历史时点仅说明 receipt fresh-main 后恢复 T66 准入；该准入已执行并由 WI216 `cancelled_no_go` supersede，不再授权进入旧实现路线 | 否 |

每条记录必须保留编号、证据 URI、revision/snapshot、复现命令、影响边界、责任子项和关闭证据。新问题先登记再分流，禁止顺手混入其他 PR。

本 WI217 closure source 是本路线唯一终局；合入时表中 GAP-01/GAP-03～06 按上述状态记为
`non_blocking_backlog`，不伪造其“已修复”，并解除对正常特性开发的阻断。GAP-02 的
characterization 能力保留为普通工程实践，不再产生减重 work item；已关闭 GAP-07～15 的历史证据不变。

## 4. Lean Code 原则

- **LP-01 行为优先**：净行数下降不能抵消功能、错误处理、审计证据或兼容损失。
- **LP-02 稳定重复才抽取**：至少三个当前调用者且语义、失败模式一致，才允许新增公共抽象。
- **LP-03 不为未来造扩展点**：无当前调用者和验收依据的接口、工厂、策略、配置默认拒绝。
- **LP-04 数据替代镜像代码**：只有字段差异且类型/失败语义不弱化时才采用数据驱动。
- **LP-05 公共入口薄**：CLI 只解析、调用领域服务、渲染；领域服务按责任内聚。
- **LP-06 单一真值源**：版本、schema、路径、阶段定义和规则 token 只能有一个 canonical source。
- **LP-07 低风险先行但不强制串行**：只处理与目标切片真实相关的前置，不用小收益任务拖延高收益切片。
- **LP-08 测试验证行为**：镜像测试可参数化，但场景、断言、平台和错误路径不得减少。
- **LP-09 增量治理**：历史债务报告化；硬门禁只约束新增或显著修改的代码。
- **LP-10 每包可量化减重**：每个实现包必须满足 Reduction Contract，不允许无限期“结构准备”。
- **LP-11 功能与减重分批**：出现公共行为需求时转为独立功能/迁移工作项。
- **LP-12 切换后删除**：L3 切片在同一工作包内完成 shadow、切换、稳定期和旧实现删除后才能关闭。
- **LP-13 有界投入与产品均衡**：减重必须有可解释收益、时间边界和退出条件；当边际收益不足、结束时间
  不可预测、token/验证成本过高或阻塞正常特性开发时，立即收口为backlog，不得以治理流程续投。

## 5. 公共兼容契约

| 编号 | 冻结内容 | 比较方式 |
|---|---|---|
| CC-01 | CLI 命令、参数、默认值、help、stdout/stderr、交互提示和 JSON envelope | surface manifest + transcript fixture |
| CC-02 | 成功、业务阻断和输入错误退出码 | characterization test |
| CC-03 | artifact 路径、schema 版本、字段、顺序语义和错误文本 | 版本化 normalizer + 结构 diff |
| CC-04 | checkpoint、work item、loop、review 的合法状态迁移 | 状态矩阵测试 |
| CC-05 | 默认 `--dry-run` 无写入，`--execute/--yes` 保持授权边界；WI-207 唯一窄例外是 `managed-delivery-apply --dry-run` 可执行既有幂等 adapter refresh，仅允许 managed adapter 文件与 project config 的宿主验证 exact delta | 工作区、`.git`、外部路径、子进程和网络副作用观测；WI-207 额外比较 adapter/config bytes 与 ingress state |
| CC-06 | 配置/环境变量优先级、幂等、重试、恢复和中断续跑 | 环境矩阵 + 重放测试 |
| CC-07 | Windows、macOS、Linux 与离线发布路径 | 受影响平台 smoke |
| CC-08 | 代表性兄弟项目共享 CLI 路径 | 有选择理由的项目清单 + smoke |

Golden normalizer 必须版本化，只允许显式列入 allowlist 的时间、绝对临时路径、随机 ID 等非语义字段变化。确定性不等于等价；完成判定必须是旧/新实现零未批准语义差异。

CC-05 描述默认授权合同，不追溯删除已经显式定义的 preflight/materialization 语义。WI-207 必须同时
冻结两层例外：`managed-delivery-apply` 省略 `--request` 时既有 truth-derived request 物化，以及本项
新增保留的 adapter/config 宿主验证刷新；direct `--execute` 缺少 `--yes` 时，二者仍可在 guard 前发生，
但不得执行 mutate action 或写 apply result artifact。任何其他例外必须另立合同，不得类推放宽。

## 6. 变更合同与 Reduction Contract

### 6.1 非减重变更合同

T51、T52、T53A、T53B、T54、T55、T56、T57、T58 属于缺陷/truth 修复，使用 NC-01～NC-06，不强迫承担减重阈值：

- **NC-01**：冻结可复现的 observed/expected behavior 和基线 revision。
- **NC-02**：列出受影响 CC、文件/符号、truth/fixture 影响分析；缺失或不确定时 fail-closed。
- **NC-03**：冻结最大新增手写产品/测试 LOC、文件数和公共抽象数，只允许修复所需最小变更。
- **NC-04**：先红后绿；定向、全量和受影响 smoke 通过。
- **NC-05**：提供 revert/配置回退、artifact 恢复和 owner。
- **NC-06**：不混入结构减重、功能扩展或无关 truth 清仓。

### 6.2 Reduction Contract

WP-03～WP-07 的每个减重候选在编码前冻结以下字段；缺一项不得进入 execute：

- **RC-01 目标切片**：文件、符号、命令/状态族、重复族和影响契约。
- **RC-02 基线**：手写产品 LOC、测试 LOC、复杂度、重复族、fan-out/fan-in、运行耗时；生成/fixture/vendored 单列。
- **RC-03 预算**：最大新增手写 LOC、模块和公共抽象数量，以及预计删除量。
- **RC-04 结果阈值**：重复类切片必须消除选定重复族且目标切片净 LOC 至少下降 10%。结构类切片除原文件中被迁移职责 LOC/方法数下降至少 90% 外，还必须满足以下至少一项：切片产品 LOC 净下降 10%、聚合圈复杂度下降 15%、跨领域依赖边下降 20%、选定重复分支 100% 消除；纯移动一律 No-Go。
- **RC-05 临时膨胀**：shadow 期间最多增加目标切片基线的 15% 或 1,000 行手写产品代码，取较小值；超出则缩小切片。旧实现删除前工作包不得关闭。
- **RC-06 保护成本**：适用矩阵要求 RC-06 的候选，其新增手写产品、test/harness/normalizer LOC 合计不得超过已通过候选审查并纳入具体 RC 的预计删除代码 25%，且路线图累计绝对上限 1,500 行；fixture/snapshot 文件每个冻结 CC 场景最多 2 个，版本库内规范化 snapshot 累计不超过 2 MiB。超限时缩小范围或复用现有测试，不得扩大预算分母。统一口径不追溯撤销已经双审、合并和 fresh-main 验收的 receipt，但后续候选计算路线累计上限时，必须按当前 product+proof 合并口径保守重列历史实际值或已批准上限，不得只累计 proof 子项。
- **RC-07 文件约束**：新增手写文件不超过 400 行、新增函数不超过 50 行；无三个当前调用者不得新增公共抽象。
- **RC-08 总体终态（待退役）**：历史组合目标要求手写产品 LOC 相对基线净下降至少 10%、选定重复族
  全部关闭，且 `program_service.py` 与 `program_cmd.py` 均降到 400 行以内。该组合目标已被用户判定
  不现实；WI217 closure 必须记为 `retired_unrealistic_composite_target`，不得写成达成、waiver 或失败后
  继续投资，也不再作为 WI196 关闭门。
- **RC-09 停止投资**：预测或实测不能达到该子项适用的 RC-04～RC-07，或保护成本超过收益时，停止该
  方案并保留旧实现，不得以结构准备续投。校验器只解析适用矩阵声明的字段；WI217 后不再准入新的减重候选。
- **RC-10 证据**：PR 必须给出 before/after、预算消耗、差异结果、回退演练和未解决风险。

门禁、兼容 harness 和 facade 不是减重成果；它们的新增必须计入预算。

### 6.3 适用矩阵

| 子项 | 强制合同 |
|---|---|
| T51/T52/T53A/T53B/T54/T55/T56/T57/T58 | NC-01～NC-06 + 受影响 CC；RC 不适用 |
| WP-01 | RC-01～RC-03、RC-06、RC-07、RC-09、RC-10 + impact analysis 选出的 CC；Phase A/B 落实 CC |
| WP-02 | RC-01～RC-03、RC-06、RC-07、RC-09、RC-10 + CC-01/02/03/05/06/07；代码指标与合同 admission 两个规则族都经历 report/warning/blocking，使用独立状态/回退开关 |
| WP-03/WP-04/WP-05 | RC-01～RC-07、RC-09、RC-10 + impact analysis 选出的 CC；RC-04 按重复/候选类型解释 |
| WP-06/WP-07 | RC-01～RC-07、RC-09、RC-10 + impact analysis 选出的 CC；RC-04 按结构类型解释，T61A/B 为 pre-merge gate |
| WI217/WI196 终局关闭 | WI217 GO/NO-GO exact receipt + RC-08 retired + 剩余 Gap=`non_blocking_backlog` |

## 7. 风险与执行边界

| 等级 | 典型改动 | 必要保护 |
|---|---|---|
| L1 | 完全相同 helper、测试参数化 | 定向 characterization + 全量回归 |
| L2 | store 公共逻辑、baseline 候选、Lean Gate | 目标切片 Golden/differential + 回退适配 |
| L3 | ProgramService 分域、stage engine | shadow 双跑、单切片切换、主线预发布稳定周期、独立删旧 PR |
| L4 | 删除公共命令、改变 schema/状态/安全边界 | 不属于减重；另立迁移/功能项并由用户批准 |

GAP-07、GAP-08 的缺陷修复按合同可独立或并行启动，且每个缺陷必须先写能复现原行为的定向 characterization test。两项现已分别由 WI-197、WI-198 关闭，WP-01A 的基础 barrier 已满足；后续候选仍须满足各自 impact analysis 与 sponsor/admission 条件。

GAP-12 与 GAP-13 是 WI-206 fresh-main 验收中暴露的两个不同根因；GAP-14 是 WI-207 fresh-main
诊断 dirty diff 时暴露的第三个独立验证根因。三项必须使用独立 WI/branch/PR。T55 已由 WI-207
关闭；T55 只处理 root program bypass、两个 managed-delivery 入口局部兼容刷新与 program test isolation；
T56 只处理 continuity canonical reconstruction；T57 只处理 comment-policy 对 quoted scalar 的误报。
三项都先红后绿，且不计为减重成果。由于它们会污染治理证据、恢复状态或阻断合法变更，路线在继续
新的 T63/T65/WP-06/WP-07 候选前先顺序关闭 T55、T56、T57。

GAP-15 是 WI-213 formal 验证时发现的独立入口分发缺陷，不是 GAP-12 回归：`program validate` 的
只读 bytes 仍稳定，但 `workitem` subapp callback 在只读子命令进入 handler 前无条件刷新 adapter。T58 必须
在独立 WI/branch/PR 中以 RED/GREEN bytes、输出与 clean-tree 证明关闭；WI-213 只登记事实并恢复 adapter
到 base bytes，不实施修复。由于该缺陷会污染 T61A baseline，T58 closure receipt fresh-main 是 T66 T61A 的硬前置。

兼容、安全或授权边界不得用 waiver 绕过。GAP-09～GAP-11 已由 WI-199～WI-201 关闭，不再是开放阻断依赖；后续目标切片仍须落盘 inheritance、adapter consumption 与 source inventory 的防回归影响分析。分析缺失或不确定，或 truth 再次出现对应 blocker、unmapped 或 §3 允许边界之外的 missing source 时，必须 fail-closed、登记 owner/证据并重开对应 GAP；truth 保持关闭条件时不得重复执行 T53A/T53B/T54。

## 8. 功能需求

- **FR-01**：GAP-01～GAP-15 必须有证据、边界、责任子项和关闭证据索引。
- **FR-02**：实现子项必须按 §6.3 适用矩阵 fail-closed 校验 NC、CC 与 RC；不允许伪造 N/A 绕门。
- **FR-03**：GAP-07、GAP-08、GAP-12、GAP-13、GAP-14、GAP-15 每项使用独立 WI/branch/PR，先红后绿验证原始缺陷。
- **FR-04**：WP-01 只覆盖目标切片实际影响的契约；Phase A 在编码前捕获旧基线，Phase B 必须绑定候选 commit/tree hash 并作为同一候选 PR 的 pre-merge gate。
- **FR-05**：WP-02 的代码指标与 NC/CC/RC admission 两个规则族都按 report-only、warning、blocking 演进，状态和回退独立；每阶段冻结 versioned expected delta，未列入 delta 的兼容差异仍为 BLOCKER。
- **FR-06**：WP-05 必须先做 go/no-go；预测不满足 RC 时直接取消，不预设 YAML/JSON 是答案。
- **FR-07**：WP-06、WP-07 每次只处理一个领域或 stage family，并在同一工作包完成主线预发布稳定周期与旧实现删除。这里的稳定周期不是版本发布：candidate PR 合并且 legacy 保留后，必须完成 required cross-platform CI、wheel/sdist、clean install、offline smoke、代表性 sibling project smoke 及 selector rollback/reapply；随后才允许独立 deletion PR。删除后重复同等安装包与回退验证，删除前不得关闭工作包。
- **FR-08**：每个子 WI 进入 execute 前必须具备进入、非目标、具体验证命令、完成、停止、回退和 evidence URI 合同。只有合同 admission gate 处于 `active + verified` 时才替代人工评审；未激活、禁用、降级、回退或健康检查失败时，L1/L2 普通项自动恢复一个独立合同 reviewer，L3 或影响 CC-05/CC-06 的高风险项自动恢复两个 Agent。
- **FR-09**：所有实现 PR 均遵守仓库 mainline PR/check/review/heartbeat 协议；L3 额外经过本地专职只读 reviewer。
- **FR-10**：双 Agent 评审记录必须包含 agent、维度、目标哈希、时间、findings、处置和 verdict；内容变化使旧 PASS 失效。
- **FR-11**：双 PASS 只替代治理文档逐条人工评审，不替代 L4 的用户批准。
- **FR-12**：本治理分支不得修改 `src/ai_sdlc/`、runtime rules、provider 或 workflow；formal source
  inventory 增加 canonical 五件套时，唯一测试例外是机械更新
  `tests/integration/test_repo_program_manifest.py` 的 inventory/close 两个精确预期值，不得新增测试逻辑
  或行数。
- **FR-13**：WI-207 不得修改 resume-pack/state reconstruction；WI-208 不得顺带修改 root adapter dispatch。
  两项分别 fresh-main 后继续进入 WI-209，不得提前恢复新的减重候选。
- **FR-14**：WI-209 只修 comment preservation 的 YAML quoted-scalar false positive，不得修改 adapter、
  resume reconstruction 或把所有 YAML `#` 行一律豁免；该项 fresh-main 门禁已满足。其历史“后续减重
  使用独立原子 WI”规则只适用于WI217之前，FR-15禁止WI217之后的新减重WI。
- **FR-15**：WI217 是最后一个减重 work item。Formal 后最多一个 implementation PR和一个 closure PR；
  GO/NO-GO 均由 closure 关闭 WI196、退役 RC-08、把剩余结构债转为非阻塞 backlog，并禁止创建新的
  减重 work item。Implementation 合并后 fresh-main NO-GO 时，唯一 closure PR 必须恢复 exact baseline
  product/proof blobs，不得增加 rollback PR。正常特性开发恢复，但本路线不自动授权版本发布。

## 9. 成功标准

- **SC-01**：四件套无未决占位、互相矛盾或无责任人的开放项。
- **SC-02**：GAP、LP、NC、CC、RC、FR 均在 `tasks.md` 有直接追踪。
- **SC-03**：路线图冻结统一合同模板；按 FR-08 取得风险分层 reviewer PASS，或取得 `active + verified` 机器 admission PASS，否则子 WI 不得进入 execute。
- **SC-04**：治理分支相对 main 无产品代码和 runtime rule 变更；测试变化只能是 FR-12 允许的 root
  exact truth 两个值替换，除此之外测试 diff 必须为空。
- **SC-05**：文档合同检查、`verify constraints`、`git diff --check` 与路径白名单检查通过。
- **SC-06**：兼容安全 Agent 与精简效率 Agent 对同一 `spec.md + plan.md + tasks.md` 内容哈希均明确 PASS。
- **SC-07**：GAP-07 与 GAP-08 已作为两个独立首批实现项分别关闭，关闭证据绑定 WI-197/PR #121 与 WI-198/PR #122；WP-01A 的基础 barrier 已满足。
- **SC-08**：历史减重工作包只有满足适用 Reduction Contract 才能以 `completed_reduction` 关闭。WP-05 单项 No-Go 用 `cancelled_no_go`；六个冻结候选均完成评估且全部 No-Go 时，GAP-06 可用 `closed_no_viable_reduction` 关闭，但不计减重成果。该重开规则只保留为历史合同；SC-11生效后不得重开为新的减重work item。
- **SC-09**：GAP-12 由 WI-207 关闭、GAP-13 由 WI-208 关闭、GAP-14 由 WI-209 关闭；任一项不得借
  另一项的测试、waiver 或 PR 伪装为已完成，且三者均不得计入 RC-08 产品 LOC 减重。
- **SC-10**：GAP-15 由 T58 独立关闭；五个只读 `workitem` 命令不得改变 adapter/config/working tree，
  其 help/invalid-input 同样无 refresh；`init/link` 的 valid/负路径 hook 次数、时序、输出、退出码与写语义
  零未批准差异；real-hook byte evidence 与 config-lock warning+continue/其他异常传播均须覆盖，且独立
  lifecycle delivery 后的 closure receipt 自身双审、Codex/checks、merge/detached fresh-main 前不得进入 T66 T61A。
- **SC-11**：WI217 closure 对 GO/NO-GO 选择恰好一个真实 outcome，missing/close truth 完整，WI196=closed、
  RC-08=`retired_unrealistic_composite_target`、剩余结构债=`non_blocking_backlog`，且无新减重 work item、
  第二个 implementation PR 或本路线发布动作。

## 10. 冻结决策

1. 采用“统一台账 + 原子子项”，不采用单分支重写或多领域打包。
2. GAP-09～GAP-11 保留在同一台账并修复，但不作为所有减重工作的总前置。
3. 取消混合型 WP-00 和 WP-08：基础缺陷各自立项；门禁升级归 WP-02；旧实现删除归 WP-06/WP-07。
4. 不预占正式 WI 编号；双 PASS 后使用当时下一可用编号。
5. Lean Gate 是否推广到普通用户项目另行决策。
6. WI-202 首次T62A候选经两套完整proof证实违反RC-06，按RC-09停止且不合入任何
   source/state/claim；GAP-01/T62A当时保持open，T62B/T62C未开始。该段原有重启条件已由第14项终局
   决策退役；不得复活WI-202或创建新的T62A～C减重WI，CC-05/CC-06 reviewer只作普通工程实践保留。
7. WI-206 关闭后依次执行 WI-207/GAP-12、WI-208/GAP-13、WI-209/GAP-14；三个基础修复完成后才
   恢复新的 T63/T65/WP-06/WP-07 原子减重选择，RC-08 全路线终态前不发布版本。
8. WI-210 与 WI-211 closure fresh-main 均已满足恢复门禁；WI-211 已关闭一个 T63
   mapping-dedupe family 并将实际 raw 净减 122 计入 RC-08 family ledger。后续候选选择已恢复，
   但必须使用新的独立原子 WI/branch/PR；不得关闭 GAP-05、WI-196、RC-08 或提前发布版本。
9. RC-08 前禁止 tag、GitHub Release、PyPI 发布和全局 CLI 更新。为避免 L3 “先稳定发布再删旧”与该
   禁令互锁，WP-06/WP-07 的一个稳定周期仅指 FR-07 定义的主线预发布稳定周期；candidate 与 deletion
   仍属于同一工作包，deletion 后还要验证安装包、offline/sibling smoke 与 rollback/reapply。该解释不
   构成版本发布，也不允许提前关闭 GAP-03、GAP-04、WI-196 或 RC-08。
10. WI-212 选中的 T66 bounded-stage domain 已进入 WI-213 formal-only 准入；current main 复算仍为
    45 methods / 3,638 physical / 3,305 executable / branch proxy 386。Ruff 88 列反证确认九组显式
    DTO/path binding 的 mechanical lower bound 约83～85行，不能藏入预备5行；WI-213 因此冻结 private
    module≤360、candidate facade addition≤72、terminal facade body≤45、binding/glue≤90，并重算
    shadow product≤522、product+proof≤712、terminal≤720、净删≥2,918。WI-212 的691/2,947与 WI-213
    早期701/2,937仅保留为历史预估。该修订只有在
    parent+child formal-six 双 PASS、mainline/fresh-main receipt 与后续 T61A 双 readiness GO 后才授权
    candidate；formal 本身不关闭 T66/GAP-03，不恢复旧 WI-203/WI-204 hash，也不发布版本。
11. WI-213 formal 验证新发现 GAP-15：`program validate` 已保持 adapter bytes，但 `workitem` callback 仍让
    只读子命令隐式 refresh。WI-213 只登记并恢复非范围 diff；其 lifecycle reconciliation 已由
    PR #159 / merge `d5ad7616` 与 detached fresh-main 完成。独立 T58/WI-214 的 formal PR #160、amendment
    PR #161 与 implementation PR #162 / merge `2845fedc` 已完成；lifecycle delivery final tree=`3f6698d7`
    同身份 LEAN/SAFETY PASS0，PR #163 exact-head 10/10 checks、merge=`60fe6d90` 与 detached fresh-main 全绿。
    本 closure receipt merge 关闭 GAP-15/T58，但 T66 仍 blocked；receipt detached fresh-main 通过后，唯一
    下一步才是创建 T66 implementation WI并先完成 T61A 双 readiness。失败必须回退 receipt，仍不得把缺陷
    修复计入 T66 减重收益。
12. 上述 T66 实现入口已经执行并由 WI-216 的 records-only recovery 取代：C2-safe 完整自然账本为
    `558 LOC / 64 branch`，高于对应 legacy `495/63`，产品源码净增35、proof净增285；后续无 DSL
    隔离 spike 在第二阶段达到 target=`1209/164`，高于两阶段 legacy=`842/92`且 branch 超硬门74。
    Pascal/LEAN 与 Confucius/SAFETY 对 spike 产品和 records-only 身份均裁决
    `STOP_SPIKE_NO_GO/findings=0`，并一致确认 C2 不能称为减重。因此 T66 本次实现尝试为
    `cancelled_no_go`，两条证据路线 `archived_not_merged`；GAP-03、WI-196、RC-08 与 release 继续 open。
    该段原有T66重启路径已由第14项终局决策退役；不得另立减重formal WI，也不得继承WI-215的GO、
    hash、预算或reviewer receipt。
13. WI-216 closure fresh-main 后从 `b4d2ce5a` 新选出的 WI-217 属于 T63/WP-03，而非 T66 重启。
    其13个 ProgramService artifact loader 基线为403 physical/branch39；clean spike实测 product=
    `+48/-406`、proof=`+48`、terminal=`44/4`；implementation canonical truth为3行，RC-06=`99/101`。Round 4 LEAN/SAFETY
    对同一 clean evidence 均 `APPROVE A/findings=0`。WI-217 formal 与 implementation 必须分离；formal
    fresh-main通过前不授权产品变更。以下第14项终局决策取代本项关于“只关闭family并保持父路线open”的
    未来时态，但不改写候选基线与已观察证据。
14. 本专项已持续接近7天且结束时间不可预测，token/评审/CI成本持续增加并影响正常特性开发；已合入
    product raw净删653行仅约占初始107,482行基线的0.61%，即使WI217 GO累计1,011行也仅约0.94%。
    基于该投入产出，用户冻结 WI217 为本轮减重专项最后一个 work item。本项取代第6～13项所有关于
    “未来重启、继续open、恢复选择、另立减重WI”的未来时态，但不改写其中已发生的历史事实。当前 formal 后至多一个 implementation PR 和一个
    closure PR；实现修复不得拆出第二 PR。GO 路径登记真实净删；NO-GO 路径登记最终产品净变化0，并区分
    pre-merge零产品合入或post-merge临时合入后exact rollback；两者都由
    closure 关闭 WI217/WI196，将 RC-08 记为 `retired_unrealistic_composite_target`，把 GAP-01/GAP-03～06
    与 T62～T67 剩余结构债转为 `non_blocking_backlog`，并禁止新的减重 work item。Closure merge后
    立即恢复正常特性/缺陷开发；fresh-main不延迟或重新阻断该恢复。本路线不创建版本、tag、Release、
    PyPI上传或全局CLI更新。
15. WI217 唯一implementation PR #168 已以 reviewed HEAD=`533363f495`、22/22 required checks、Codex
    current-head clean、LEAN/SAFETY同identity PASS0和detached fresh-main全绿形成最终GO；merge=
    `4d98039d`，实际product=`+48/-406/net -358`。本唯一closure source合入时，路线累计产品raw净删
    1,011行（约初始基线0.94%），关闭WI217/WI196，按第14项退役RC-08并转移剩余backlog。Source存在
    不提前代表main已关闭；closure PR merge是mainline状态生效点，detached fresh-main是post-merge
    acceptance。若该验收失败，按下述emergency corrective-revert路径撤销失败closure，不重启减重路线。

### 10.1 Closure post-merge failure 边界

- 唯一closure PR merge即是`completed_go/closed`、RC-08退役与backlog状态在main的生效点；detached
  fresh-main不延迟生效，只验证该状态。
- 若post-merge acceptance失败，立即用一个emergency corrective-revert PR精确恢复pre-closure records：
  删除WI217 summary、恢复manifest exact missing=`1`/close=`216/215`并重新sync truth；product/proof仍须
  相对`4d98039d`零diff，状态改为`closure_delivery_failed`，不得继续宣称closed。
- 该corrective-revert是“一次closure PR”上限的唯一安全例外，仅撤销失败closure，不构成第二closure、
  implementation或减重work item；不得重新选择候选。正常特性/缺陷开发不被该回退阻断；再次closure
  必须取得用户新的明确授权。
