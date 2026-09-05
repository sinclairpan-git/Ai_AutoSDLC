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

### Batch 2026-09-05-002 | T21-T32 | Implementation candidate 与价值回放

#### 2.10 候选范围与本地验证

- implementation base：formal PR #206 merge `5967c87cfe8e7f384f319761e70f299b605379b0`。
- 最终 GO 候选：commit `9dd98366d56e51a27290f45280c0c407ab457301`；tree `6a73a0244668b4f940d653181ebd50e991fad674`；工作区 clean。
- 产品源码严格限定 formal 的 7 文件 allowlist，gross additions=`595/600`；没有新增依赖、workflow、持久 review/finding artifact、状态机、ledger 或第二类 Loop。
- 唯一整改后的定向回归：`101 passed in 3.53s`；最终全量：`3486 passed, 3 skipped in 1019.87s`；Ruff、constraints、program validate、plan-check、manifest regression 与 `git diff --check` 均通过。

#### 2.11 三例匿名价值回放

三个样例均在空目录用候选 CLI 初始化。`review` 前后树摘要按“相对路径排序 + 每文件 SHA-256，再对清单取 SHA-256”计算；三例均为 15 files、before=after，确认只读。

| Case | baseline 与结果 | Round 1 digest / tree hash | 终态 |
|---|---|---|---|
| A `req-p2c7` 安全/权限 | 未定义资料字段、脱敏和失效会话；两位专家共 3 条 required | `879a0bf214476f5f97ca3f6d5ee513ac5002aadd993a130eb0f60a57b509824f` / `5e9947cb8f0eb66192f02c1afee2a922178431b94969105e0bf4911d259cf0a0` | 修订后 digest `f6526339d884cdd5ff41822595c3908aff9f77111cd4ed31c63cb3e451379b0e`；round 2 clean/closed |
| B `req-r8d4` 数据迁移 | 未定义 schema、冲突、幂等和失败回退；两位专家共 3 条 required | `4ff6287709445a0f25a37ec7cf1f94d79cb1c4dd8307cfdb633b6e65d273e827` / `68a578bf643879c892920bf234d0ace18c10036796c282d73d411af16bc6dcb3` | 修订后 digest `a11f437e496fe3f4fcea32dcb9ccfb37a7e9b4a99f9c936d81095f82cf4b327d`；round 2 clean/closed |
| C `req-m4v10` clean | `normalize_slug(text)` 的类型、长度、NFKC/casefold、字符集、异常、样例与冲突非目标均已明确；全新 reviewer 无 finding | `59b06e22b8d350fa0189795444cdb2e65054afc9d9fa7be39ef8ac52d53519f4` / `644682993efede84efa245e32c652b978da051b5fc6033faaf91a7103b055526` | round 1 clean/closed |

- A/B 原两位专家在随机 ID 重绑时独立重算 digest，确认只改变 Loop ID、需求语义未变；原始 finding 原文未增删润色。A/B 经一次修订后相同身份均返回 `findings=[]`。
- C 的 `req-7f3a`、`req-q9k2` 因真实缺口作废，`req-m4v8`、`req-m4v9` 因仍需澄清作废；最终只计全新 `req-m4v10`，避免标签泄漏或反复调参制造 clean。
- 独立裁决结果：`valid_incremental_count=6`、`false_actionable_count=0`；SC-228-007 的阶段性价值门为 GO。三例 Loop 内 `execution|finding` 持久文件计数均为 0。

#### 2.12 唯一实现整改与终审

- implementation 预审唯一整改关闭：same-handle 普通文件/大小/inode 校验，拒绝 FIFO/设备/路径替换；`findings` 必填；半套 intake/loop-run artifact fail closed；修订默认保留旧 acceptance；blocked next action 区分可修订、待评审和两轮终止；补齐直接测试和可复现回放。
- 最终 exact-head PRODUCT/ROI：核对 `9dd98366...` / `6a73a024...`，Critical 0、Important 0、Minor 0，`PRODUCT PASS0`。
- 最终 exact-head ARCHITECTURE/代码纯洁：核对同一 commit/tree，Critical 0、Minor 0；仍有 1 Important，`ARCHITECTURE NO-GO`。
- 残余 Important：`requirement_loop.py` 先用未清洗的 `options.acceptance` truthiness 判断是否替换旧标准，后执行 `_clean_items`。round 2 显式 `--acceptance "   "` 会清空旧 criteria、持久化 `needs_user`；再次补充有效 criteria 又被 round-2 状态阻断，形成不可恢复死锁。专家用真实调用复现；最小修法虽小，但已经超过 formal 允许的唯一整改波次。
- 终局判定：SC-228-008 与硬停止条件触发，阶段性价值 GO 被实现终审 NO-GO 覆盖。不得再修、不得合入 runtime、不得新建后续 work item。

### Batch 2026-09-05-003 | T32-T41 | Terminal NO-GO closure

#### 2.13 回退与范围

- `git revert --no-edit 9dd98366d56e51a27290f45280c0c407ab457301`：生成 `d4bf2961`，保留完整候选审计历史并撤回产品实现、测试、README、用户指南和 GO closure。
- 相对 formal merge base，terminal PR 的 `src/ai_sdlc/**`、Requirement/CLI 行为测试、`README.md`、`USER_GUIDE.zh-CN.md` diff 必须为空；只允许 WI228 closure、roadmap、Program Truth、continuity，以及 close layer materialize 后机械同步 `test_repo_program_manifest.py` 的 missing/close 库存断言。
- 已合并 formal 分支重命名为 `archive/requirement-expert-review-formal`；唯一 terminal carrier 为 `archive/228-requirement-bounded-dynamic-expert-review-terminal`。两条本地历史均保留，不删除本地分支。

#### 2.14 统一验证命令

- **验证画像**：`code-change`
- **改动范围**：`specs/228-requirement-bounded-dynamic-expert-review/spec.md`、`specs/228-requirement-bounded-dynamic-expert-review/plan.md`、`specs/228-requirement-bounded-dynamic-expert-review/tasks.md`、`specs/228-requirement-bounded-dynamic-expert-review/task-execution-log.md`、`specs/228-requirement-bounded-dynamic-expert-review/development-summary.md`、`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`program-manifest.yaml`、`tests/integration/test_repo_program_manifest.py`、canonical/scoped continuity files
- 同一 terminal content 固定后执行：
  - `git diff --exit-code 5967c87cfe8e7f384f319761e70f299b605379b0..HEAD -- src/ai_sdlc tests/unit tests/integration/test_cli_loop.py README.md USER_GUIDE.zh-CN.md`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program validate`
  - `uv run ai-sdlc workitem plan-check --wi specs/228-requirement-bounded-dynamic-expert-review --json`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run pytest tests/integration/test_repo_program_manifest.py -q`
  - `uv run ruff check tests/integration/test_repo_program_manifest.py`
  - `uv run ai-sdlc workitem close-check --wi specs/228-requirement-bounded-dynamic-expert-review --json`
  - `git diff --check`
- 动态 exact-head Codex review、required checks、merge SHA 和 fresh-main 验收只留在 PR/平台回执；不通过则不合并，不为记录结果创建第二个 PR。

#### 2.15 代码审查与 Git 收口

- **代码审查结论**：runtime 候选为 `PRODUCT PASS0` / `ARCHITECTURE NO-GO`，因此产品不交付；terminal diff 只记录既定 NO-GO，不包含替代实现或新治理机制。
- **已完成 git 提交**：是（本 marker 随 terminal closure commit 一起落盘）。
- **提交哈希**：`HEAD`；动态 exact-head SHA 只写 PR 外部 receipt。
- 当前批次 branch disposition 状态：`archived(terminal NO-GO carrier retained after merge)`
- 当前批次 worktree disposition 状态：`retained(terminal NO-GO closure and fresh-main acceptance)`

#### 2.16 任务/计划同步状态

- T11～T41 全部收口：实现/价值回放如实记录，最终 Important 触发 NO-GO，候选 runtime 与行为测试全部撤回。
- spec、plan、tasks、roadmap 与 development summary 一致标记 G4 NO-GO closed；P4 不进入 Phase B，不创建后续 work item。
- Program Truth materialize WI228 close layer；唯一库存断言从 missing 8/close 218 机械同步为 missing 7/close 219。
