# 任务分解：AI-SDLC 框架缺口修复与自身减重

**编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**来源**：`spec.md` + `plan.md`
**当前分支边界**：允许当前 child 五件套、父路线五件套、被关闭前项的 execution/summary 回写、
program/project truth、checkpoint、handoff 和 resume-pack；禁止修改 `src/ai_sdlc/**`、`rules/**`、
`providers/**`、`.github/workflows/**`。唯一测试例外是新增 canonical 五件套时机械更新
`tests/integration/test_repo_program_manifest.py` 的 inventory/close 两个精确值，不得新增测试逻辑或行数。

## Batch 1：治理基线（已完成）

### T11 创建隔离工作区与 canonical 工作项

- **范围**：独立 worktree/branch、四件套、manifest 和 project state。
- **完成**：WI-196 唯一登记，`next_work_item_seq=197`，不带入 main 的无关改动。
- **验证**：`git status --short --branch`、manifest/四件套检查。
- **回退**：删除未合并 worktree/branch。

### T12 记录可复现基线

- **依赖**：T11。
- **范围**：产品/测试 LOC、超限文件/函数、重复候选、基线 revision 和全量测试。
- **完成**：统计口径区分产品、测试以及后续必须单列的生成/fixture/vendored 分类。
- **验证**：只读统计与 `uv run pytest`。

## Batch 2：治理合同（已完成并经首轮评审修订）

### T21 冻结 LP、NC、CC 与 Reduction Contract

- **依赖**：T12。
- **完成**：LP-01～12、NC-01～06、CC-01～08、RC-01～10 及适用矩阵唯一、无冲突、可映射到实现验收。
- **验证**：编号唯一性和追踪检查。

### T22 冻结统一问题台账

- **依赖**：T21。
- **完成**：GAP-01～11 有证据、影响边界、责任子项、关键路径属性和关闭证据要求。
- **验证**：证据路径、manifest snapshot 和复现入口对账。

### T23 冻结原子路线图

- **依赖**：T22。
- **完成**：基础缺陷、减重包和关联治理债务互不混责；每包有进入/验证/完成/停止/回退。
- **验证**：逐包合同检查与依赖图检查。

## Batch 3：双 Agent 对抗评审

### T31 首轮独立评审

- **依赖**：T23。
- **执行**：兼容安全 Agent 与精简效率 Agent 对同一内容独立只读评审。
- **完成**：两份 findings-first verdict 落盘；不要求用户处理中间意见。

### T32 核验并修订 findings

- **依赖**：T31。
- **执行**：逐条对照仓库事实；正确意见修改，错误或过度建议记录拒绝理由。
- **完成**：所有 BLOCKER/WARNING 有 disposition，目标文件形成新的 review target hash。

### T33 最终同哈希复审

- **依赖**：T32。
- **记录字段**：`agent_id`、`dimension`、`review_target_hash`、`reviewed_at`、`findings`、`dispositions`、`verdict`、`evidence_uri`。
- **规则**：`spec.md`、`plan.md` 或 `tasks.md` 任一变化，已有两个 PASS 同时失效。
- **完成**：两个 Agent 对同一哈希均明确 `VERDICT: PASS`。

## Batch 4：真值与交付验证

### T41 同步 program truth 与 continuity

- **依赖**：T33。
- **完成**：canonical/scoped handoff 记录双 PASS、当前风险、T62A No-Go 与重新启动前置；resume-pack 指向 WI-196，不得指向已关闭的 GAP-07/08 或旧 WI-202。
- **验证**：handoff show、resume-pack/checkpoint 对账、program truth dry-run。

### T42 运行最终门禁

- **依赖**：T41。
- **完成**：编号/追踪/占位符检查、路径白名单、`uv run ai-sdlc verify constraints`、`git diff --check`、targeted truth tests 全部通过。
- **规则**：验证后若目标文件变化，回到 T33。

### T43 提交 WI-196

- **依赖**：T42。
- **完成**：提交只包含治理文档和合法 truth/handoff；随后按仓库 mainline PR 协议交付。
- **提交后验证**：在目标 commit/PR checkout 上运行 `uv run ai-sdlc program truth audit`，把目标 commit、`repo_revision + generated_at + snapshot_hash`、audit 输出、退出码和 blocking refs/source inventory 精确集合写入 execution log/PR 证据。
- **判定**：只有 `snapshot_state=fresh`、整体 `state=ready`、退出码 0，且无 `invalid/stale`、validation
  error 或 blocker 才可继续。active child 在 pre-close 只允许一个 mapped/`exists=false` 的当前
  `development-summary.md`，close=`N/(N-1)`；closure 必须恢复 missing=0、close=`N/N`。任一其他
  missing、任一 unmapped、非零、non-ready、集合未解释增减或证据缺失一律停止并返回 T41/T22；若命中
  GAP-09～GAP-11，必须重开对应 GAP，不允许 `PASS_WITH_REGISTERED_DEBT` 例外。
- **回退**：revert WI-196 文档提交，不影响产品运行时。

## Batch 5：独立实现子项目录

表中 `standalone` 项必须各自创建正式 work item，不能与相邻行合并 PR；`embedded gate` 项属于对应候选 WI/PR 的强制阶段，不另起事后审计 PR。

| 任务 | 交付方式 | 责任 | 风险 | 硬依赖 | 关闭证据 |
|---|---|---|---:|---|---|
| T51 修复 adapter mutation/preflight 顺序（已完成） | standalone | GAP-07 | L1/L2 | 已满足 | WI-197 / PR #121 / merge `4802596f`；NC、红绿 characterization、clean-tree、CLI/full/CI |
| T52 修复 linked-WI resume/handoff 派生（已完成） | standalone | GAP-08 | L2 | 已满足 | WI-198 / PR #122 / merge `68150d3f`；NC、红绿 fixture、recover/handoff、artifact diff |
| T53A 关闭 frontend inheritance truth（已完成） | standalone | GAP-09 | L2 | 已满足 | WI-199 / PR #123 / merge `208a34c8` |
| T53B 关闭 adapter consumption truth（已完成） | standalone | GAP-10 | L2 | 已满足 | WI-200 / PR #124 / merge `c737eda0` |
| T54 收敛 source inventory（已完成） | standalone | GAP-11 | L2 | 已满足 | WI-201 / PR #125 / merge `d19c8b7d`；0 unmapped / 0 missing |
| T55 隔离 program implicit adapter side effect（已完成） | standalone | GAP-12 | L2 / CC-05 | 已满足 | WI-207；PR #139 + repair PR #141 / merge `8d8b8f96`；fresh-main full 3224/3、repository state clean |
| T56 建立 portable/lossless resume reconstruction（已完成） | standalone | GAP-13 | L2 | 已满足 | WI-208 / PR #143 / merge `f51c176a`；canonical source、relocation/focused/full、双 Agent、Codex、22/22 checks、fresh-main clean |
| T57 修复 YAML quoted-scalar comment-policy false positive（已完成） | standalone | GAP-14 | L2 | T56 与 formal PR #145/merge `46156c24` 已满足；Round 15 candidate/replay 同树且 Pascal/Confucius 双 PASS；PR #146 Codex current-head clean、22/22 checks、merge `31aad572` 与 fresh-main acceptance 全部通过 | WI-209 / PR #146；old/new 对称 quoted token span、quoted/plain/literal/real-comment、默认/quotePath=false 空格与 mixed escape characterization + focused/full/constraints/cross-platform/fresh-main clean；回退 PR #146 会重开 |
| T61A 捕获目标切片旧行为 | embedded gate | GAP-02/WP-01A | L1/L2 | T51、T52 + fail-closed impact analysis | 固定环境、allowlist、surface/Golden 基线 |
| T61B 候选实现 differential 与回退演练 | embedded pre-merge gate | GAP-02/WP-01B | L1～L3 | T61A + candidate hash | 零未批准差异、rollback receipt；未通过不得 merge/close |
| T62A code + contract report-only（open） | standalone | GAP-01/WP-02 | L1/L2 | T61A + 新/替代 sponsor + 父合同重新双审 | WI-202 候选 RC-09 No-Go；重启项须分类/合同缺口报告、历史零误阻断、RC-06 预算 |
| T62B code + contract warning | standalone | GAP-01/WP-02 | L2 | T62A 稳定 | 两规则族 warning fixture、waiver schema、独立开关 |
| T62C code + contract blocking | standalone | GAP-01/WP-02 | L2 | T62B 稳定 | 两规则族 blocker、admission `active + verified`、独立降级与 reviewer fallback 测试 |
| T63 单个 helper/DTO/test 重复族（按 family 继续） | standalone + T61A/B | GAP-05/WP-03 | L1 | T51、T52 已满足；WI-205、WI-206、WI-210 各完成一个 family；WI-211 formal in progress | WI-210 / PR #149 / merge `904fe5de`：28→1 body、产品 net -213；WI-211 候选为10→1 mapping body、23 calls、预测 raw net -122，但仅在 formal/implementation/closure 全部验收后记账 |
| T64 单个 Loop Store family | standalone + T61A/B | GAP-05/WP-04 | L2 | T51、T52 | store differential、LOC -10%、恢复/损坏输入测试 |
| T65 单个 baseline 候选 go/no-go | standalone + T61A/B on Go | GAP-06/WP-05 | L2 | T51、T52 | Go=`completed_reduction`；单项 No-Go=`cancelled_no_go`；六项全 No-Go=`closed_no_viable_reduction` |
| T66 单个 ProgramService 领域切片 | standalone + T61A/B | GAP-03/WP-06 | L3 | T51、T52 + 真实重叠子项 | 迁移职责 -90%、RC-04 结构改善、稳定发布、删旧后回退演练 |
| T67 单个 Program Stage family | standalone + T61A/B | GAP-04/WP-07 | L3 | T51、T52 + 真实重叠子项 | 镜像 LOC -70%、33 命令兼容、稳定发布、删旧后回退演练 |

**全局恢复门禁**：T57/WI-209 与 WI-210 closure fresh-main acceptance 已完成；表中 T61A、
T62A～T62C、T63～T67 的新实例已恢复选择，但仍须逐项满足各自依赖、sponsor、RC 与原子 WI/branch/PR。
WI-211 已选择一个 T63 candidate，但 formal merge/fresh-main 前不得创建 implementation branch。
既有已完成 receipt 不受影响；各行保留的历史 T51/T52 依赖已满足，不需要重复执行。

每个目标切片必须先落盘 GAP-09～GAP-11 防回归 impact analysis；除当前 active child 唯一 mapped
pre-close `development-summary.md`（close=`N/(N-1)`）外，分析缺失/不确定或当前 truth 再现对应
blocker、unmapped/missing source 时默认阻断并重开相应 GAP。关闭条件持续满足时不得重复执行
T53A/T53B/T54，也不得把它们重新解释为待满足硬依赖。

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| GAP-01～GAP-14 | T22、T51～T67 |
| LP-01～LP-12 | T21、T23、T32、T63～T67 |
| NC-01～NC-06 | T21、T51～T57 |
| CC-01～CC-08 | T21、T51、T52、T55～T57、T61A、T61B、T62A～T62C、T63～T67（按 impact analysis） |
| RC-01～RC-10 | T21、T32、T61A、T61B、T62A～T62C、T63～T67（按适用矩阵） |
| FR-01～FR-02 | T21、T22、T32 |
| FR-03～FR-04 | T51、T52、T55～T57、T61A、T61B |
| FR-05～FR-07 | T62A～T62C、T65～T67 |
| FR-08～FR-09 | T23、T43、全部实现子项 |
| FR-10～FR-11 | T31～T33 |
| FR-12 | T42、T43、T55～T57 formal truth |
| FR-13 | T55、T56 |
| FR-14 | T57 |
| SC-01～SC-09 | T32、T33、T41～T43、T55～T57 |
