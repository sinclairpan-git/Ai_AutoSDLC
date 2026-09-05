# 任务执行日志：Requirement Loop 有界动态专家评审纵向薄片

**功能编号**：`228-requirement-bounded-dynamic-expert-review`
**创建日期**：2026-09-05
**状态**：G1 formal/admission 进行中；无产品实现

## 1. 归档规则

- 本文件固定归档 WI228 的 formal、实现、真实回放和 Go/No-Go，不创建平行执行日志。
- 每批先预读 spec/plan/tasks/宪章，再实现或评审，随后在同一批提交内更新任务与回执。
- 每个验证记录命令、输入规模（如适用）、耗时、exit code 和关键结果；失败不能写成 PASS。
- Formal 与实现各最多一轮初审和一轮整改复审；两个身份必须绑定同一文档或实现 head。
- 本 docs branch 不得写产品代码；formal 合入后才允许唯一 implementation PR。

## 2. 批次记录

### Batch 2026-09-05-001 | T11-T12 | Formal admission

#### 2.1 批次范围

- 基线：`origin/main@71e4ff5098505d0c6321c9162c1b9b1647d155d1`，即 PR #205 合并并 fresh-main 验收后的主线。
- 预读：主仓 P4 路线图、Requirement/Loop 模型与 CLI；参赛版稳定基线 `b6addbab` 的动态专家行为和删除合同。
- 创建：canonical `spec.md / plan.md / tasks.md / task-execution-log.md`、Program manifest 映射、next work item 序号。
- 排除：产品代码、测试逻辑、R09、Lean、其余四类 Loop、参赛版通用 kernel 复制。

#### 2.2 现状与决策

- 主仓 Requirement 已有确定性 intake、一个 `LoopRound`、`needs_review` 与显式 user freeze，但没有独立专家入口、风险角色或 reviewed-input digest。
- 参赛版仅两份主要通用 review 文件已超过 1400 行，完整审查面更大；证明行为可行，但不适合作为主仓 Phase A-1 的复制目标。
- Admission 选择 Requirement 专属薄片：瞬时 input/roles、严格临时 execution、最多两角色、现有 LoopRound 两轮、freeze 前完整 execution 校验。
- 兼容决策：新 loop 用 `review_required=true` 强制新合同；旧 artifact 缺字段时继续原 freeze 行为并显式提示，不迁移、不伪装成新评审。

#### 2.3 已执行命令

- `gh pr view 205 ...` / `gh run view 33955004801 ...`：PR #205 current head `111b588` 获 Codex clean review，PR Checks 与 9 项 Compatibility Gate 全部成功。
- `gh pr merge 205 --squash`：exit 0；merge SHA `71e4ff5098505d0c6321c9162c1b9b1647d155d1`。
- fresh detached main：WI227 close-check exit 0、`done_gate=ready`；`program validate: PASS`；`verify constraints: no BLOCKERs`；工作树 clean。
- `uv run ai-sdlc workitem init --wi-id 228-requirement-bounded-dynamic-expert-review ...`：exit 0；生成 canonical formal 并映射 manifest。
- 初始化产生的无关 `.cursor/rules/ai-sdlc.mdc` 刷新已回退，不纳入本工作项。

#### 2.4 对抗评审 Round 1

- 绑定哈希：`spec=5E37D76D...A4D29`、`plan=A96345E5...D47D8`、`tasks=EE1C7A47...5454F`、`log=1173B60A...D6DBE0`。
- 产品/ROI 身份：`PRODUCT REJECT`，1 Critical + 4 Important。
- 架构/代码纯洁身份：`ARCHITECTURE REJECT`，1 Critical + 4 Important。
- 两方一致 Critical：digest 只证明输入身份，不能证明独立专家实际执行；只传 digest 的 freeze 是伪评审门禁。
- 两方一致 Important：普通澄清会被误算为 review round；legacy/new freeze 兼容未定义；盲测 ROI 与有效 finding/误报标准不足；600 行和文件预算口径不一致。
- 架构追加 Important：reviewer 实际读取内容未与 digest 同源，路径/TOCTOU 边界未冻结。

#### 2.5 唯一一轮 Formal 整改

- 新增严格但不持久化的 `RequirementReviewExecution`：freeze 同次校验当前 digest/round、完整唯一角色、全部 completed、无 `blocker/required` finding；RequirementFreeze 只记 digest/roles/time。
- reviewer 只消费 review 输出中的 canonical projection，artifact path 不再是摘要外内容源；明确只保证单 active-writer 顺序漂移检测。
- `needs_user` 阶段澄清不增轮；`needs_review` 后只有绑定当前 execution 的修订进入 round 2；freeze 关闭实际 current round。
- 新 loop 标记 `review_required=true`；legacy open/closed loop 无迁移兼容旧 freeze 并提示。
- 机制路由测试与 ROI 盲测分离；冻结有效 finding 定义、clean 对照与零错误 actionable finding 阈值。
- 预算统一为 `src/ai_sdlc/**` gross additions ≤600，并冻结产品源码 allowlist；测试/文档不计行数但逐项映射验收。
- Go/No-Go 唯一终态：Go 合入当前 runtime；No-Go 移除 runtime，只用同一个 terminal PR 归档，不再追加 records PR。

#### 2.6 验证与真值（待完成）

- `uv run ai-sdlc program truth sync --dry-run`：exit 0；完整映射 `1190/1190`、unmapped 0、missing 8。
- `uv run ai-sdlc program truth sync --execute --yes`：exit 0；写回 `program-manifest.yaml`，WI228 的 spec/plan/tasks/execution/预期 close 五层均有 canonical mapping。
- `uv run ai-sdlc program validate`：exit 0，PASS。
- `uv run ai-sdlc program truth audit`：exit 1；snapshot fresh，完整映射 `1190/1190`；仅报告同步前已存在的 16 个 `truth_check` blocker（WI095–105、121–126），没有 WI228 blocker，故如实记为历史 Program Truth 债而非本工作项 PASS。
- `uv run ai-sdlc verify constraints`：exit 0，no BLOCKERs。
- `uv run ai-sdlc workitem plan-check --wi specs/228-requirement-bounded-dynamic-expert-review --json`：exit 0，`drift=false`、`pending_todos=0`。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：1 个固定库存回归，146.49 秒，exit 0，`1 passed`；期望库存同步为 `1190/1190/0/8`、close `226/218`。
- 初次 manifest regression 曾与 handoff/link 写入并发，既发现旧固定库存又触发 mutation guard；该失败不计 PASS，最终回归已在无并发写入下串行重跑。
- `git diff --check`：整改后 exit 0；提交前再跑一次。
- branch/worktree：`feature/228-requirement-bounded-dynamic-expert-review-docs` / `/tmp/ai-sdlc-wi228-requirement-expert`。

#### 2.7 对抗评审 Round 2 与首个 PR head

- 绑定哈希：`spec=E479596E...E0826F`、`plan=6E57887A...CD3B4`、`tasks=F656BDEB...808B`、`log=1C308093...B13B`。
- 产品/ROI 身份：`PRODUCT PASS`，Critical 0、Important 0；唯一 Minor 是把 T31 的“只写回执摘要”改为“写入可复核回放证据”，已按原有验收边界修正。
- 架构/代码纯洁身份：`ARCHITECTURE PASS`，Critical 0、Important 0；实现期须保持 canonical `role_id` 一一对应，并以同一打开句柄完成普通文件、大小和内容校验，不新增机制或 formal 负担。
- 措辞修正与评审证据落盘前的身份重绑结果：`PRODUCT PASS0`、`ARCHITECTURE PASS0`；Critical 0、Important 0。
- 首个 PR head `fa8813928f7990bd6bfce4033059f9f7ae18bfb4` 的 whitespace-normalized 内容哈希为：`spec=62583B4E...42004`、`plan=E54FD98C...FC378`、`tasks=4C0B1743...4C3EA`、`log=CDC214F3...A9AE`；两个身份分别返回 `PRODUCT PASS0 FINAL-WHITESPACE` 与 `ARCHITECTURE PASS0 FINAL-WHITESPACE`。
- 两个身份已就唯一对抗整改达成一致；后续 required PR gate 只能补齐 Codex 指出的可执行合同，不重新开放对抗方案空间。最终实施准入以 PR conversation 中同时绑定 exact commit SHA 与两位原身份回执的外部 receipt 为准，避免把自指的当前日志哈希伪装成不可变证明。

#### 2.8 Codex exact-head required review

- PR：`#206`；reviewed commit：`fa8813928f7990bd6bfce4033059f9f7ae18bfb4`；Codex 于 2026-09-05T09:38:08Z 完成 review。
- P1：评审后修订要求 execution，却没有冻结 `requirement start --review-result-file` 公共接口与测试。
- P1：日志只显示早期内容哈希，必须让两位专家把最终判断绑定到不可变 exact head/tree，并在 PR 外部 receipt 归档。
- P2：现有 CLI 在 core freeze validation 前调用 writer adapter；必须冻结纯读取 preflight → adapter → 最终复核 → write 的顺序，并以整树 no-mutation 测试覆盖所有 rejected execution。
- 处理边界：只修订 formal 命令/顺序/验证合同；不写产品代码、不增加状态、文件、依赖或预算。修改后由原 PRODUCT/ARCHITECTURE 身份核对同一 staged tree，通过后提交，并在 PR comment 记录 exact commit + tree + 两份 PASS0；随后只请求一次 Codex re-review。
- 原身份对首版补漏哈希 `spec=D087A549...FC562`、`plan=9E09D620...937DA`、`tasks=D48FE0DE...9FA46`、`log=9982C09F...FEEEE` 聚焦复审时一致发现：不能把 actionable finding 套入 start 的拒绝矩阵，否则真正发现问题的 round 1 无法驱动 round 2。最终合同拆为共享安全/身份/completed preflight，start 接受 actionable finding 修订，只有 freeze 要求 clean；该修正不新增状态或接口。
- 新 head `21ce255ec07368881cbd25a334966d93bb073724` / tree `b6a3737bc2d833873e07c94ed2d4f8b708fe8b01` 已取得 `PRODUCT EXACT-HEAD PASS0` 与 `ARCHITECTURE EXACT-HEAD PASS0`，并在 PR conversation 归档最小 receipt；Codex re-review 于 2026-09-05T10:10:49Z 仍发现两项可操作合同歧义。
- P1：round 2 后若持久化 `needs_user`，后续 start 可能借免 execution 澄清路径覆盖 round 2。修正为现有 command `blocked`，不调用 adapter、不写 status/intake/round，重复实质修改仍 blocked；只保留对现有 round 2 重新 review 后 freeze 的路径。
- P2：review role 缠绕了展示 `name` 与 execution `role_id`。修正为每个返回角色直接包含稳定 canonical `role_id`，execution validator 只按该字段核对精确唯一集合；不新增角色实体、registry 或状态。

#### 2.9 批次结论

- T11 已完成；T12 的初始 formal、唯一对抗整改、真值同步与本地验证已完成。首个 exact-head Codex review 给出三项合同补漏，当前按 required PR gate 聚焦修订，尚未取得新 head 的最终准入。
- 当前 `execution_started=false`；没有实现代码或实现授权消费。
