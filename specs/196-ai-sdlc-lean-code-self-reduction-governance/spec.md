# 功能规格：AI-SDLC 框架缺口修复与自身减重

**功能编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**创建日期**：2026-07-12
**状态**：双 Agent 评审门禁
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

## 3. 统一问题台账

所有证据默认对应基线 revision；`program-manifest.yaml` 证据必须以目标提交内的 `truth_snapshot.repo_revision`、`generated_at`、`snapshot_hash` 三元组为准，并通过 `uv run ai-sdlc program truth audit` 复核。规范不得硬编码会随 truth sync 变化的 snapshot hash。

复核必须在目标 commit/PR checkout 上执行并记录目标 commit、三元组、audit 输出与退出码。当前交付只接受 `snapshot_state=fresh`、整体 `state=ready`、退出码 0，且 manifest 无 `missing/invalid/stale`、validation error 或 blocker；capability blocking refs 与 source inventory 计数仍须作为精确集合记录在 execution log。任意 non-ready、非零退出码、集合变化或证据缺失均 fail-closed；若 GAP-09～GAP-11 对应 blocker 或 unmapped/missing source 再现，必须登记证据并重开对应 GAP，不得以 `PASS_WITH_REGISTERED_DEBT` 继续。

| 编号 | 类别 | 事实证据 / 复现入口 | 目标与责任 | 减重关键路径 |
|---|---|---|---|---|
| GAP-01 | 治理缺口 | 宪章规定 400 行/50 行，但当前 `uv run ai-sdlc verify constraints` 对历史超限无 BLOCKER | WP-02：report → warning → changed-code blocking | 是 |
| GAP-02 | 兼容缺口 | 现有测试分散，缺少目标切片统一的 CLI/artifact/状态/副作用 differential 基线 | WP-01：最小充分 Characterization/Golden | 是 |
| GAP-03 | 结构臃肿 | `src/ai_sdlc/core/program_service.py` 17,369 行、249 方法 | WP-06：逐领域切片、保留 facade、稳定后删旧实现 | 是 |
| GAP-04 | 结构臃肿 | `src/ai_sdlc/cli/program_cmd.py` 7,062 行；33 个公共 program 命令与 77 对相似长命令候选 | WP-07：逐 stage family 双跑与收敛 | 是 |
| GAP-05 | 重复实现 | `models/frontend_*`、`telemetry/*`、`generators/frontend_*_artifacts.py` 中存在大量 `_dedupe*`；多个 store 与镜像测试存在重复候选 | WP-03/WP-04：只合并语义和失败模式一致的重复族 | 是 |
| GAP-06 | 单一真值源候选 | `frontend_page_ui_schema.py`、`frontend_cross_provider_consistency.py`、`frontend_quality_platform.py`、`frontend_provider_expansion.py`、`frontend_provider_runtime_adapter.py`、`frontend_theme_token_governance.py` 的 6 个 `build_p*_baseline` builder | WP-05：对该有限候选集逐项 go/no-go；只有净减重合同成立才实施 | 条件性 |
| GAP-07 | 已关闭 | WI-197 / PR #121 / merge `4802596f`：adapter mutation 不再与 clean-tree preflight 自冲突 | T51 已完成；权威证据见 WI-197 execution log §6.3～6.7 | 否 |
| GAP-08 | 已关闭 | WI-198 / PR #122 / merge `68150d3f`：resume working set 以 active linked WI 为准 | T52 已完成；权威证据见 WI-198 execution log §3～§8 | 否 |
| GAP-09 | 已关闭 | WI-199 / PR #123 / merge `208a34c8`：framework capability 与 consumer inheritance fail-closed 分离 | T53A 已完成；回退整个 WI-199 会重开本项 | 否 |
| GAP-10 | 已关闭 | WI-200 / PR #124 / merge `c737eda0`：repository capability 与本机会话 consumption fail-closed 分离 | T53B 已完成；runtime admission 仍独立诊断 | 否 |
| GAP-11 | 已关闭 | WI-201 / PR #125 / merge `d19c8b7d`：source inventory 收敛为 complete、unmapped=0、missing=0 | T54 已完成；新增 source 继续 fail-closed | 否 |
| GAP-12 | 已关闭 | WI-207：formal PR #140、implementation PR #139、test-isolation repair PR #141；merge `8d8b8f96` 的 fresh-main real-hook/focused/full/Ruff/治理门禁全绿且 repository state clean | T55 已完成；回退 PR #139 或 #141 会重开本项 | 否 |
| GAP-13 | 已关闭 | WI-208 / PR #143 / merge `f51c176a`：共同 builder 以 canonical sources portable/lossless 重建 root/scoped resume-pack，保留 branch、active files、context 与 raw-byte convergence | T56 已完成；fresh-main relocation/focused/full/Ruff/治理门禁全绿，保护文件与 clean state 不变；回退 PR #143 会重开本项 | 否 |
| GAP-14 | implementation adversarial review | `comment_policy._is_comment_line()` 按 stripped diff line 判断前缀；WI-209 在 `main@85bdedac` 复现 single/double quoted scalar 续行均产生 1 finding，而 PyYAML token 实际跨越该内容行 | T57 / WI-209：formal PR #145 已合并为 `46156c24`；Round 10 fresh full/治理门禁已通过，terminal replay/双审待完成；fresh-main 前保持开放，禁止 waiver | 是（验证可靠性） |

每条记录必须保留编号、证据 URI、revision/snapshot、复现命令、影响边界、责任子项和关闭证据。新问题先登记再分流，禁止顺手混入其他 PR。

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

T51、T52、T53A、T53B、T54、T55、T56、T57 属于缺陷/truth 修复，使用 NC-01～NC-06，不强迫承担减重阈值：

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
- **RC-06 保护成本**：WP-01/WP-02 新增的手写产品、test/harness/normalizer LOC 合计不得超过已通过候选审查并纳入具体 RC 的预计删除代码 25%，且路线图累计绝对上限 1,500 行；fixture/snapshot 文件每个冻结 CC 场景最多 2 个，版本库内规范化 snapshot 累计不超过 2 MiB。超限时缩小范围或复用现有测试，不得扩大预算分母。
- **RC-07 文件约束**：新增手写文件不超过 400 行、新增函数不超过 50 行；无三个当前调用者不得新增公共抽象。
- **RC-08 总体终态**：仅用于路线图组合终态，不作为单个子项关闭条件。路线图关闭时手写产品 LOC 相对基线净下降至少 10%；选定重复族全部关闭；`program_service.py` 与 `program_cmd.py` 均降到 400 行以内。
- **RC-09 停止投资**：预测或实测不能达到该子项适用的 RC-04～RC-07，或会使 RC-08 组合终态不可达，或保护成本超过收益时，停止该方案并保留旧实现，不得以结构准备续投。校验器只解析适用矩阵声明的字段。
- **RC-10 证据**：PR 必须给出 before/after、预算消耗、差异结果、回退演练和未解决风险。

门禁、兼容 harness 和 facade 不是减重成果；它们的新增必须计入预算。

### 6.3 适用矩阵

| 子项 | 强制合同 |
|---|---|
| T51/T52/T53A/T53B/T54/T55/T56/T57 | NC-01～NC-06 + 受影响 CC；RC 不适用 |
| WP-01 | RC-01～RC-03、RC-06、RC-07、RC-09、RC-10 + impact analysis 选出的 CC；Phase A/B 落实 CC |
| WP-02 | RC-01～RC-03、RC-06、RC-07、RC-09、RC-10 + CC-01/02/03/05/06/07；代码指标与合同 admission 两个规则族都经历 report/warning/blocking，使用独立状态/回退开关 |
| WP-03/WP-04/WP-05 | RC-01～RC-07、RC-09、RC-10 + impact analysis 选出的 CC；RC-04 按重复/候选类型解释 |
| WP-06/WP-07 | RC-01～RC-07、RC-09、RC-10 + impact analysis 选出的 CC；RC-04 按结构类型解释，T61A/B 为 pre-merge gate |
| 路线图关闭 | RC-08 + 所有 Gap Evidence Index |

## 7. 风险与执行边界

| 等级 | 典型改动 | 必要保护 |
|---|---|---|
| L1 | 完全相同 helper、测试参数化 | 定向 characterization + 全量回归 |
| L2 | store 公共逻辑、baseline 候选、Lean Gate | 目标切片 Golden/differential + 回退适配 |
| L3 | ProgramService 分域、stage engine | shadow 双跑、单切片切换、稳定发布、独立删旧 PR |
| L4 | 删除公共命令、改变 schema/状态/安全边界 | 不属于减重；另立迁移/功能项并由用户批准 |

GAP-07、GAP-08 的缺陷修复按合同可独立或并行启动，且每个缺陷必须先写能复现原行为的定向 characterization test。两项现已分别由 WI-197、WI-198 关闭，WP-01A 的基础 barrier 已满足；后续候选仍须满足各自 impact analysis 与 sponsor/admission 条件。

GAP-12 与 GAP-13 是 WI-206 fresh-main 验收中暴露的两个不同根因；GAP-14 是 WI-207 fresh-main
诊断 dirty diff 时暴露的第三个独立验证根因。三项必须使用独立 WI/branch/PR。T55 已由 WI-207
关闭；T55 只处理 root program bypass、两个 managed-delivery 入口局部兼容刷新与 program test isolation；
T56 只处理 continuity canonical reconstruction；T57 只处理 comment-policy 对 quoted scalar 的误报。
三项都先红后绿，且不计为减重成果。由于它们会污染治理证据、恢复状态或阻断合法变更，路线在继续
新的 T63/T65/WP-06/WP-07 候选前先顺序关闭 T55、T56、T57。

兼容、安全或授权边界不得用 waiver 绕过。GAP-09～GAP-11 已由 WI-199～WI-201 关闭，不再是开放阻断依赖；后续目标切片仍须落盘 inheritance、adapter consumption 与 source inventory 的防回归影响分析。分析缺失或不确定，或 truth 再次出现对应 blocker、unmapped/missing source 时，必须 fail-closed、登记 owner/证据并重开对应 GAP；truth 保持关闭条件时不得重复执行 T53A/T53B/T54。

## 8. 功能需求

- **FR-01**：GAP-01～GAP-14 必须有证据、边界、责任子项和关闭证据索引。
- **FR-02**：实现子项必须按 §6.3 适用矩阵 fail-closed 校验 NC、CC 与 RC；不允许伪造 N/A 绕门。
- **FR-03**：GAP-07、GAP-08、GAP-12、GAP-13、GAP-14 每项使用独立 WI/branch/PR，先红后绿验证原始缺陷。
- **FR-04**：WP-01 只覆盖目标切片实际影响的契约；Phase A 在编码前捕获旧基线，Phase B 必须绑定候选 commit/tree hash 并作为同一候选 PR 的 pre-merge gate。
- **FR-05**：WP-02 的代码指标与 NC/CC/RC admission 两个规则族都按 report-only、warning、blocking 演进，状态和回退独立；每阶段冻结 versioned expected delta，未列入 delta 的兼容差异仍为 BLOCKER。
- **FR-06**：WP-05 必须先做 go/no-go；预测不满足 RC 时直接取消，不预设 YAML/JSON 是答案。
- **FR-07**：WP-06、WP-07 每次只处理一个领域或 stage family，并在同一工作包完成稳定期与旧实现删除。
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
  resume reconstruction 或把所有 YAML `#` 行一律豁免；WI-209 fresh-main 前不得恢复新的减重候选。

## 9. 成功标准

- **SC-01**：四件套无未决占位、互相矛盾或无责任人的开放项。
- **SC-02**：GAP、LP、NC、CC、RC、FR 均在 `tasks.md` 有直接追踪。
- **SC-03**：路线图冻结统一合同模板；按 FR-08 取得风险分层 reviewer PASS，或取得 `active + verified` 机器 admission PASS，否则子 WI 不得进入 execute。
- **SC-04**：治理分支相对 main 无产品代码和 runtime rule 变更；测试变化只能是 FR-12 允许的 root
  exact truth 两个值替换，除此之外测试 diff 必须为空。
- **SC-05**：文档合同检查、`verify constraints`、`git diff --check` 与路径白名单检查通过。
- **SC-06**：兼容安全 Agent 与精简效率 Agent 对同一 `spec.md + plan.md + tasks.md` 内容哈希均明确 PASS。
- **SC-07**：GAP-07 与 GAP-08 已作为两个独立首批实现项分别关闭，关闭证据绑定 WI-197/PR #121 与 WI-198/PR #122；WP-01A 的基础 barrier 已满足。
- **SC-08**：后续减重工作包只有满足适用 Reduction Contract 才能以 `completed_reduction` 关闭。WP-05 单项 No-Go 用 `cancelled_no_go`；六个冻结候选均完成评估且全部 No-Go 时，GAP-06 可用 `closed_no_viable_reduction` 关闭，但不计减重成果。只有基线或消费者发生实质变化才允许重新打开。
- **SC-09**：GAP-12 由 WI-207 关闭、GAP-13 由 WI-208 关闭、GAP-14 由 WI-209 关闭；任一项不得借
  另一项的测试、waiver 或 PR 伪装为已完成，且三者均不得计入 RC-08 产品 LOC 减重。

## 10. 冻结决策

1. 采用“统一台账 + 原子子项”，不采用单分支重写或多领域打包。
2. GAP-09～GAP-11 保留在同一台账并修复，但不作为所有减重工作的总前置。
3. 取消混合型 WP-00 和 WP-08：基础缺陷各自立项；门禁升级归 WP-02；旧实现删除归 WP-06/WP-07。
4. 不预占正式 WI 编号；双 PASS 后使用当时下一可用编号。
5. Lean Gate 是否推广到普通用户项目另行决策。
6. WI-202 首次 T62A 候选经两套完整 proof 证实违反 RC-06，按 RC-09 停止且不合入任何
   source/state/claim；GAP-01/T62A 保持 open，T62B/T62C 未开始。重启必须同时取得新的或替代
   sponsor，并重新冻结和双审父合同；在此之前按 FR-08 为 CC-05/CC-06 保留两个独立 reviewer。
7. WI-206 关闭后依次执行 WI-207/GAP-12、WI-208/GAP-13、WI-209/GAP-14；三个基础修复完成后才
   恢复新的 T63/T65/WP-06/WP-07 原子减重选择，RC-08 全路线终态前不发布版本。
