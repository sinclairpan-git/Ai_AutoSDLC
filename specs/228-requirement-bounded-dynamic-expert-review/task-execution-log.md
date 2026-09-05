# 任务执行日志：Requirement Loop 有界动态专家评审纵向薄片

**功能编号**：`228-requirement-bounded-dynamic-expert-review`
**创建日期**：2026-09-05
**状态**：G3 三例真实盲测达到 GO；implementation 收口验证中

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

### Batch 2026-09-05-002 | T21-T32 | Requirement 薄片与真实盲测

#### 2.10 实现边界

- implementation base：formal PR #206 merge `5967c87cfe8e7f384f319761e70f299b605379b0`；候选最初在 `feature/228-requirement-bounded-dynamic-expert-review-dev` 开发，terminal closure 前重命名为 archive carrier。
- 新增 Requirement 专属瞬时 review input/execution；新 loop 强制评审，旧 intake 缺 `review_required` 时保持兼容并提示。
- `review` 只返回 canonical projection、digest、1 个 primary 和至多 1 个 cross-risk；临时 execution 以同一打开句柄完成普通文件、非 symlink、256 KiB、UTF-8 JSON 和严格 schema 校验。
- revision/freeze 在 adapter 前纯读取 preflight；writer 内按当前 intake/digest/round 再校验。只有 clean execution 可 freeze；actionable execution 只允许 round 1→2 修订；第三实质版本 command blocked。
- 没有新增依赖、workflow、状态机、ledger、持久化 review artifact 或第二类 Loop。

#### 2.11 实现期定向验证

- `uv run pytest tests/unit/test_requirement_review.py tests/unit/test_requirement_loop.py tests/integration/test_cli_loop.py -q`：`91 passed`，exit 0。
- 扩大回归（Requirement、Loop status、Design Contract、Implementation、constraints、CLI、new requirement flow）：`407 passed in 21.24s`，exit 0。
- `uv run ruff check`（本批变更 Python 文件）：exit 0，`All checks passed`。
- `uv run ai-sdlc verify constraints`：exit 0，`no BLOCKERs`。
- `uv run ai-sdlc program validate`：exit 0，PASS。

#### 2.12 三例盲测输入与 Round 1 只读回执

三个 baseline 均在空目录经真实 CLI 初始化和 `start` 生成；专家只收到 canonical projection，不知道预期答案。A/B 仅在盲审完成后把原始输出重绑到语义相同、只更换随机 Loop ID 的 projection；两位原专家均重算并确认 digest。C 使用全新随机 ID 和全新 reviewer。命中风险短语只验证路由，不计有效 finding。

复现公共前缀（本候选源码环境）：

```powershell
$Cli='/tmp/ai-sdlc-pr206-main-verify-5967c87c/.venv/bin/ai-sdlc'
& $Cli init . --agent-target codex --shell powershell
```

- A / `req-p2c7`：idea=`客服管理员需要在内部控制台查看客户资料；只允许拥有客户支持权限的已登录员工访问。`；acceptance=`拥有客户支持权限的员工可以查看所属租户客户资料`、`无权限员工和跨租户访问均被拒绝并记录审计日志`。
- B / `req-r8d4`：idea=`数据管理员需要把旧版 CSV 客户档案迁移到新系统；保留 customer_id；范围只覆盖 UTF-8 CSV。`；acceptance=`所有合法行导入后 customer_id 与总数保持一致`、`非法行被报告且不得覆盖已有记录`。
- C / `req-m4v10`：idea=`框架开发者用户使用纯函数 normalize_slug(text) 生成内部配置键。输入必须是 Python str，规范化前用 len(text) 计算且不超过 200 个 Unicode code point；依次执行 NFKC、casefold，只保留 ASCII a-z 和 0-9，将每段连续其他字符替换为一个连字符，再移除首尾连字符。函数不读写文件、网络或进程级状态；不同输入允许产生相同结果，冲突由调用方处理。`；acceptance 依次为：非 str/超过 200 的精确异常；输出字符集和确定性；三个精确样例；空结果异常；200 边界、展开后不限长及冲突非目标。完整原文保存在本节下方 clean-control 回执。

对应命令均为：

```powershell
& $Cli loop requirement start --loop-id <id> --idea <idea> --acceptance <criterion> ... --json
& $Cli loop requirement review --loop-id <id> --json
```

输入字节按 `idea + LF + acceptance...` 的 UTF-8 长度计算。只读回执的树摘要算法为：递归枚举全部普通文件，按相对路径排序，逐行连接 `relative_path + TAB + lowercase_sha256(file)`，以 LF 连接后再取 SHA-256；因此既覆盖内容也覆盖文件集合。

| Case | start receipt | Round 1 review receipt | full digest / roles |
|---|---|---|---|
| A 安全/权限 | 257 bytes；556 ms；exit 0 | 15 files；516 ms；exit 0；before=after=`5e9947cb8f0eb66192f02c1afee2a922178431b94969105e0bf4911d259cf0a0` | `879a0bf214476f5f97ca3f6d5ee513ac5002aadd993a130eb0f60a57b509824f`；quality + security |
| B 数据迁移 | 222 bytes；554 ms；exit 0 | 15 files；524 ms；exit 0；before=after=`68a578bf643879c892920bf234d0ace18c10036796c282d73d411af16bc6dcb3` | `4ff6287709445a0f25a37ec7cf1f94d79cb1c4dd8307cfdb633b6e65d273e827`；quality + data |
| C clean 对照 | 1056 bytes；567 ms；exit 0 | 15 files；541 ms；exit 0；before=after=`644682993efede84efa245e32c652b978da051b5fc6033faaf91a7103b055526` | `59b06e22b8d350fa0189795444cdb2e65054afc9d9fa7be39ef8ac52d53519f4`；quality |

#### 2.13 专家原始输出与独立盲裁

- A / `requirement-quality` 原始 findings：
  - `required`，`intake.raw_text / intake.acceptance_criteria`：“客户资料”未定义允许展示字段及敏感字段处理；建议冻结字段白名单、隐藏/脱敏规则和验收。
  - `required`，`intake.acceptance_criteria[1]`：未覆盖未登录、会话失效或身份无效请求；建议增加拒绝并审计验收。
- A / `security-privacy-authorization` 原始 finding：
  - `required`，`intake.raw_text / intake.acceptance_criteria`：字段可见性和敏感信息边界未定义；建议冻结允许字段、排除/脱敏和无权字段不出现在页面/响应的验收。
- B / `requirement-quality` 原始 findings：
  - `required`，`intake.acceptance_criteria`：“合法行/非法行”缺字段、类型和必填规则；建议冻结列、必填、类型和逐行合法性口径。
  - `required`，`intake.acceptance_criteria[0..1]`：已有 ID、源内重复和重复执行语义不明；建议冻结冲突策略、重复规则、幂等和总数口径。
- B / `data-integrity-migration-compatibility` 原始 finding：
  - `required`，`intake.acceptance_criteria`：中途失败的提交、回退和重试语义不明；建议冻结原子回退或可识别部分成功与幂等重试验收。
- C 的全新 `requirement-quality` reviewer 原始输出为 `findings=[]`。其五条完整 acceptance 为：
  1. `非 str 输入抛出 TypeError("SLUG_TYPE")；规范化前 len(text)>200 抛出 ValueError("SLUG_TOO_LONG")；所有错误都不返回部分结果`
  2. `输出非空时只含小写 ASCII a-z、0-9 和内部单个连字符；相同输入每次结果相同`
  3. `输入 "  Hello__World  " 输出 "hello-world"；输入 "ＡＢＣ １２" 输出 "abc-12"；输入 "Straße" 输出 "strasse"`
  4. `空字符串、只含分隔字符或经规则转换后为空时抛出 ValueError("SLUG_EMPTY")`
  5. `len(text)=200 时允许处理；NFKC/casefold 展开后的输出不另设长度上限；函数不负责检测或解决不同输入的结果冲突`
- 独立裁决逐条检查“baseline 未覆盖、隐藏真值一致、影响验收/风险、建议可执行、非审美偏好”：A 三条、B 三条均为有效增量；C clean；`valid_incremental_count=6`、`false_actionable_count=0`。A 中两个字段边界 finding 语义重叠，但相对 baseline 都正确，因此保留原始回执，只在 ROI 样例阈值上按一个 case 计数。
- clean-control 资格筛选透明记录：`req-7f3a` 因缺 summary/detail、一致时间窗等真实缺口作废；`req-q9k2` 因 `order_id` 可能承载个人信息作废；`req-m4v8`、`req-m4v9` 因 clarification_count=1 未进入评审。所有失败尝试均作废而不是改判 clean，最终只计全新 `req-m4v10`。这防止通过暴露 `clean` 标签或反复调参制造零误报。

#### 2.14 唯一修订、Round 2 与冻结终态

- A 修订：冻结普通客服字段白名单、phone/email 脱敏、address/government_id 排除、supervisor 完整字段权限，以及未认证/失效会话/无权限/跨租户拒绝并审计；命令为上述 `start` 追加 `--review-result-file /tmp/ai-sdlc-wi228-executions/p2c7-round1.json`；618 bytes，572 ms，exit 0。
- B 修订：冻结 `customer_id,email,status`、必填/email/status 规则、已有/源内重复跳过并报告、重复执行幂等及中途失败全量回退；命令为上述 `start` 追加 `--review-result-file /tmp/ai-sdlc-wi228-executions/r8d4-round1.json`；627 bytes，573 ms，exit 0。
- Round 2 review：A digest `f6526339d884cdd5ff41822595c3908aff9f77111cd4ed31c63cb3e451379b0e`，15 files、530 ms、exit 0、before=after=`4166ac2b056d9f9911ce2a8e3f214acde36a9edc3c5e35e0b88510ee1262cc9a`；B digest `a11f437e496fe3f4fcea32dcb9ccfb37a7e9b4a99f9c936d81095f82cf4b327d`，15 files、528 ms、exit 0、before=after=`8eb4de785f4d4ce06660c398a7021274a821617288818e1c953de320aeb8da96`。
- 原两位专家对 A/B Round 2 均返回各自角色 `status=completed, findings=[]`；没有第三轮。
- freeze 精确命令为 `& $Cli loop requirement freeze --loop-id <id> --review-result-file <round-clean.json> --yes --json`：A execution 346 bytes、580 ms、exit 0；B execution 354 bytes、594 ms、exit 0；C execution 232 bytes、658 ms、exit 0。
- artifact inspection：A/B `closed,current_round=2,rounds=2`；C `closed,current_round=1,rounds=1`；freeze 只记录 `review_input_digest/review_role_ids/reviewed_at`，三例 Loop 中 `execution|finding` 文件计数为 0。

#### 2.15 Go/No-Go

- SC-228-007：A、B 各有有效增量 finding；C clean；三例错误 actionable finding 为 0；A/B 均在唯一一次复审收敛。**GO**。
- GO 只准许收口当前 Requirement 薄片。Design Contract、Implementation 及其余 Loop 不在本 PR 扩展，也不因本次结论自动创建后续 work item。
- T21、T22、T31、T32 完成；进入 T41 的同一 implementation head 双专家实现评审与完整验证。

### Batch 2026-09-05-003 | T41 | Implementation terminal candidate

#### 2.16 准备

- **验证画像**：`code-change`
- **改动范围**：formal 冻结的 7 个 `src/ai_sdlc/**` allowlist 路径、Requirement/相邻兼容测试、README/用户指南、WI228 formal/closure 与 continuity；无 allowlist 外产品源码。
- **体量**：formal merge base `5967c87c...` 起，tracked 产品新增 286 行，新模块 309 行，gross additions=`595/600`。
- 关联 branch/worktree disposition 计划：`archive/228-requirement-bounded-dynamic-expert-review-terminal` 是唯一 terminal PR carrier，merge 后保留本地分支与当前 worktree；已合并的 formal 分支重命名为 `archive/requirement-expert-review-formal` 并保留本地历史，不再与 WI228 lifecycle 关联。

#### 2.17 统一验证命令

- 初始定向验证为 `91 passed`；实现预审唯一整改后，同一命令为 `101 passed in 3.53s`，exit 0。
- 扩大 Requirement/相邻兼容回归：`407 passed in 21.24s`，exit 0。
- 唯一整改后的最终 `uv run pytest -q`：`3486 passed, 3 skipped in 1019.87s`，exit 0。
- `uv run ruff check <本批 Python 改动>`：`All checks passed!`，exit 0。
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`，exit 0。
- `uv run ai-sdlc program validate`：PASS，exit 0。
- `uv run ai-sdlc workitem plan-check --wi specs/228-requirement-bounded-dynamic-expert-review --json`：`drift=false,pending_todos=0`，exit 0。
- `git diff --check`：exit 0。
- `uv run ai-sdlc program truth sync --dry-run` 与 `--execute --yes`：exit 0；最终 snapshot hash 以同一 terminal tree 的 `program-manifest.yaml` 为准，inventory `1190/1190`、unmapped 0、missing 7、close `219/226`。snapshot 如实保留 16 个既有历史 truth blocker，WI228 五层均 materialized。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：首次按预期只因新增 development summary 使固定库存从 `missing 8/close 218` 变为 `7/219` 而失败；机械同步两个断言后最终重跑 `1 passed in 157.29s`，exit 0。
- final Program Truth、全量 pytest 与 close-check 在 terminal content 完整后串行重跑，结果以本批同一 repo tree 回执及 PR 外部 exact-head gate 为准。

#### 2.18 代码审查

- 三例价值回放已经由 PRODUCT/ROI 主审、ARCHITECTURE/纯洁风险审和独立盲裁完成：A/B 各有有效增量且一次复审收敛，C clean，三例 `false_actionable=0`。
- terminal candidate 必须由原 PRODUCT/ARCHITECTURE 两个身份审查同一完整实现 tree；任何 Critical/Important 只允许一轮聚焦整改，最终 PASS0 绑定 exact commit/tree 并在 PR conversation 留外部 receipt，避免修改本文件造成自引用失效。
- GitHub Codex review 与 required checks 仅接受当前 PR HEAD；没有 clean review 和全绿 checks 不合并。
- terminal candidate 预审发现并在唯一聚焦整改波次修复：临时执行文件 `findings` 必填；以同一文件描述符完成普通文件、大小和 inode/device 校验并拒绝 FIFO/设备/替换竞态；显式修订未重给 acceptance 时保留已有标准；拒绝 intake/loop-run 半套 artifact；blocked `next_action` 区分可修订、待评审与两轮终止；补齐最大文件、FIFO、路径替换、半套 artifact、adapter 最终重校验等测试。整改后 PRODUCT 指出的匿名 clean 对照和独立复现证据也由 2.12～2.14 的最终回放取代。
- 本波次之后不再允许第二个整改波次；最终同头复审若仍有 Critical/Important，直接按 formal 判定 NO-GO。

#### 2.19 任务/计划同步状态

- T11～T32 已完成；T41 仓内内容和不可绕过的外部门禁已冻结。双专家 exact-head、Codex review、required checks、merge 与 fresh-main 事实只留在 PR/平台回执，不创建 post-merge records PR。
- spec、plan、tasks、roadmap 与 development summary 已同步本次 GO：只交付 Requirement 薄片，不自动扩展 Design Contract、Implementation 或其他 Loop，不创建后续 records-only PR。
- **已完成 git 提交**：是（本 marker 随 terminal candidate commit 一起落盘）。
- **提交哈希**：`HEAD`；动态 exact-head 身份与最终 commit SHA 只写 PR 外部 receipt。
- 当前批次 branch disposition 状态：`archived(terminal PR carrier retained after merge)`
- 当前批次 worktree disposition 状态：`retained(terminal PR carrier; do not delete local branch after merge)`
