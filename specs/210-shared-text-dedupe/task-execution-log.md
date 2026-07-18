# 任务执行日志：共享文本去重重复族减重

**功能编号**：`210-shared-text-dedupe`
**创建日期**：2026-07-18
**当前状态**：Batch 0 formal Round 3 双 FAIL 已接受；Round 4 current-truth 修订与重验中；产品实现未授权

## Batch 2026-07-18-001：下一原子候选选择

### 基线与扫描

- exact current main：`4b4348646a11cf2e27e488ddad892977958476a9`；worktree clean。
- `program_cmd.py`=`7065` 行，`program_service.py`=`17474` 行；WI-204 candidate 未实现。
- WI-204 的可信保护最低估算为 Pascal 222 / Confucius 356，均超过 hard cap 180；claim=0、revoked，
  不可复活。
- AST exact-body inventory 找到 28 defs / 27 modules / 196 LOC / 730 direct calls；唯一 body digest=
  `08aa3c8fe861c4d69e2fcfcdbc6bc212b7b6d0c52ef6e2e4b382327dd48d962a`。
- repo scan 未找到跨模块 private import consumer；`p1_artifacts` 只有私有 annotation 较窄，运行 body 相同。

### 候选对抗选择

- Pascal 从精简收益侧推荐该 T63，预测产品净删至少 156 行；拒绝当前 T65/WP-06/WP-07。
- Confucius 从兼容安全侧同意该 T63，要求 private aliases、730 calls 零改、clean subprocess import、
  事件/异常 differential 与严格停止条件。
- 两者起初对承载位置有分歧：Pascal 主张复用 `utils/helpers.py`，Confucius 误以为该依赖层不存在而
  倾向新 package-root leaf。
- 主线程回传当前真值：`utils/helpers.py` 已存在、96 raw / 68 non-empty LOC、stdlib-only，repo-wide
  有 55 个 importer（CLI/Core/Generators 中 42 个），10 个目标模块已依赖；Confucius 撤回错误前提。
  双方收敛为复用现有 text helper section，不新增模块。

### 受影响测试基线

- Confucius 独立执行 23 个受影响 unit files：`441 passed in 31.94s`。
- Confucius 独立执行 8 个代表性 CLI integration files：`398 passed in 60.84s`。
- exact main 的最近 fresh acceptance full：`3275 passed, 3 skipped`。
- 初始 839 项受影响集合用于 implementation candidate/revert/restored 对比；隔离 spike 随后扩展为
  Batch 003 记录的 32-file / 1282-test 集合。两者是递进验证，不是互相冲突的验收口径，也不会复制
  WI-204 大型 harness。

### 决策

- WI-210 选择 exact text-dedupe family，风险 L1，父责任 T63/WP-03/GAP-05。
- formal 与 implementation 必须独立 branch/PR；当前只允许 docs/truth/continuity。
- 预算 spike 仅校准 import/Ruff 实际成本，不构成实现授权或 PASS。

## Batch 2026-07-18-002：Canonical formal 编制

### 已完成

- 通过 `uv run ai-sdlc workitem init` 创建 canonical 四件套与 manifest mapping。
- CLI 自举误刷 `.cursor/rules/ai-sdlc.mdc`，已精确恢复为 HEAD；该文件不属于 formal diff。
- placeholder direct-formal 内容已替换为本项唯一 spec/plan/tasks，不修改产品或测试。
- 分支按框架 canonical 约定使用 `feature/210-shared-text-dedupe-docs`。

### 待完成

1. 冻结 terminal exact identity；
2. Pascal/Confucius 对同一 identity 评审至双 PASS；
3. 双 PASS 前不得 push/创建 PR，也不得进入产品实现。

### Branch/worktree disposition

- branch：`feature/210-shared-text-dedupe-docs`（本地 formal review candidate，尚未 push/创建 PR）。
- worktree：`retained(formal review and delivery pending)`。

## Batch 2026-07-18-003：隔离实现预算 Spike

- 隔离 worktree：`.worktrees/210-shared-text-dedupe-spike`；exact HEAD=`4b434864...`；未 commit/push。
- 只修改冻结的 28 个产品文件：`utils/helpers.py` 新增唯一实现，27 个目标模块以 import alias 保留
  28 个局部私有名；tests/docs/specs/.ai-sdlc 零 diff。
- 实测产品 raw=`+39/-252/net -213`；non-empty=`+35/-196/net -161`。non-empty additions 精确为
  28 个 alias import + 7 行 helper；空行删除只出现在 raw 账，不计 RC-04/RC-06 收益。
- 730 call expressions 的逐模块 AST 与 hash 完全不变；27 cold imports PASS；28 alias 均与 shared
  object identity 相同，无 cycle/import failure。
- Ruff lint PASS；format-check 的 inherited debt 为 exact baseline/candidate 同一 24-file 集合，
  `24→24`，不得写成 formatter PASS，也不得为本项顺带格式化 730 calls。
- 32 个代表性测试文件：`1282 passed in 165.56s`；`git diff --check` PASS。
- 批准私有 introspection 差异已实测：28 objects→1；`__module__` 统一到 `ai_sdlc.utils.helpers`；
  `__name__/__qualname__` 统一为 `_dedupe_text_items`；`p1_artifacts` annotation 变为 `object`。
- Formal 预算据此拆成 raw/non-empty 双账：产品 hard=`+39/-252` 与 `+35/-196`；RC-06 采用
  non-empty，product35+test≤9+truth≤2 计划≤46、hard cap=49。

## Batch 2026-07-18-004：Formal pre-review 门禁

- 本地 seed commit=`4038919060e64ea9b0eb039bd5c05756c40a0ab2`；该提交仅用于让 truth generator
  绑定已提交的 canonical sources，不构成双审 PASS 或 push 授权。
- root manifest expectation 仅机械同步两条既有断言：inventory=`1106/1106/0/1`，close=`210/209`；
  `tests/integration/test_repo_program_manifest.py`=`1 passed in 91.70s`，未改测试逻辑。
- `uv run ai-sdlc verify constraints` PASS；`uv run ai-sdlc program validate` PASS。
- seed commit 后首次 truth sync 生成 snapshot `4503b0c2550c...aff5c1`，随后 truth audit=`ready/fresh`；
  pre-review receipt commit=`31889a27d8d8b269260af7fa4e4d966ba6b882ee` 后终态 sync 生成 snapshot
  `e49c3edfc3c2552c907fb0d1a9c5e31126f62b08ca72c2e67d25641925117a3e`。source inventory 始终为
  `1106/1106`、missing close source=`1`。
- handoff CLI 因旧 checkpoint 短暂改写 resume-pack/WI208 handoff；两文件已精确恢复为 HEAD。
  Cursor rule、resume-pack、WI208 handoff 与 `src/` 均为 zero diff，root/scoped WI210 handoff byte-identical。
- 该终态 identity 随 Round 1 findings 退役，不得继续 review 或交付。

## Batch 2026-07-18-005：Formal Round 1 双 FAIL 与处置

- 退役 identity：commit=`a038a68a89964a94e109c1367608b4e8402362e4`，tree=
  `95e57fe7a618dbc643f08c20eeaef7d0097566a9`；Pascal 与 Confucius 均 `VERDICT: FAIL`。
- 两方共同 finding：父 formal 已修改却只审 child 三文件且使用第二套 combined recipe；handoff 仍要求
  重复 terminal commit/freeze；test 预算混用 raw/non-empty。
- 精简侧额外 finding：`__name__`/`__qualname__` 未进入批准 introspection allowlist；父 summary 将
  current missing 错写为 0。
- 安全侧额外 finding：manifest 缺少 WI210→WI196 dependency；未落盘 GAP-09～GAP-11 impact analysis；
  32-file targeted 集合没有确定性命令。
- 全部 finding 接受。Round 2 统一 test cap 为 Ruff 后 non-empty≤9；批准并扫描两项私有元数据差异；
  登记父依赖与 impact/evidence URI；冻结 25 unit + 7 CLI integration 的 exact PowerShell targeted 命令；
  review identity 改用父 plan §9 的父子六文件唯一算法。
- spike 清单复核还纠正历史表述：32-file/1282 集合是 25 unit + 7 CLI integration；此前
  23-unit/8-integration=839 是不同初始子集。内容变化后 Round 1 verdict 与所有旧 hash 全部失效。

## Batch 2026-07-18-006：Formal Round 2 修订与门禁

- finding 修订 commit=`526df48ebf72a23bcc809ef22827e49160bda585`；`src/` zero diff，formal 仍未
  push/建 PR。
- `program-manifest.yaml` 已登记 WI210→WI196 dependency；truth sync snapshot=
  `7de3b25313631d990c3d2005ddeffa4c2e821ef92a4fdda4b61190c85f704c70`，authoring hash=
  `10a371afa6870e0684d82179e6de827e889d63524c2f893da0654baf18aa683a`。
- manifest exact=`1 passed in 112.11s`；constraints PASS；program validate PASS；truth audit=
  `ready/fresh`、inventory=`1106/1106`、unmapped=0、唯一 pre-close missing=1。
- CLI handoff 的旧 checkpoint 副作用再次精确恢复；Cursor/resume/WI208 protected diff=0，WI210
  root/scoped handoff 保持 byte-identical。
- 本批提交后的 current HEAD 即 Round 2 review identity；review invocation 必须按父 plan §9 绑定父子
  六文件 combined 与可复算的 binary/name-status hashes。除双审外不再要求重复 commit/freeze。

## Batch 2026-07-18-007：Formal Round 2 split verdict 与 Round 3 处置

- reviewed commit/tree=`60c93644`/`23cc23b7`，six-file combined=`cde82e85...bf84e`；Confucius
  `PASS/findings:none`，Pascal `FAIL`，因此整体未通过，Confucius PASS 随内容修订失效。
- Pascal 三项 finding 全部接受：顶层 current state 滞后；root/scoped handoff 的 Changed Files 漏列
  3 个 base..HEAD 路径；两个未来 receipt sidecar 对 L1 candidate 过度实现。
- Round 3 只做最小处置：终态前同步 current state；handoff 补回 project-state、父 plan、manifest
  expectation test；复用 WI205/WI206 先例的单一 `t61-differential-rollback-receipt.json`。
- Round 2 两份 verdict 与所有 hash 退役；新内容必须重新同步 truth、通过 formal gates，并由两位 reviewer
  对同一新 identity 从零复审。

## Batch 2026-07-18-008：Formal Round 3 terminal gates

- 最小 finding 修订 commit=`c72b82abc384867f7cb6fbbabd4b5f9b66399cc2`；只改 formal docs/
  continuity，产品与测试 zero additional diff。
- truth sync snapshot=`9ee622990aa491b228e38e29a018647bd89f6667321ed83bd070bedcbe864216`；
  manifest exact=`1 passed in 108.03s`，constraints/validate PASS，truth audit=`ready/fresh 1106/1106`、
  unmapped=0、唯一 pre-close missing=1。
- root/scoped handoff 完整列出全部 12 个 base..HEAD formal diff 文件并保持 byte-identical；Cursor/
  resume/WI208 protected diff=0；唯一 future receipt 为 `t61-differential-rollback-receipt.json`。
- 本批提交后的 current HEAD 直接作为 Round 3 review identity；下一动作仅为绑定 exact commit/tree、
  父子六文件 combined 与 diff hashes 后双审，不再重复 commit/freeze。

## Batch 2026-07-18-009：Formal Round 3 双 FAIL 与 Round 4 处置

- reviewed commit/tree=`90011f74`/`c6b996f6`，six-file combined=`8ebd3834...15e50`；Pascal 与
  Confucius 均 `VERDICT: FAIL`，finding 完全一致。
- 唯一 finding：父 `development-summary.md` 仍写“当前进入 Round 2 修订”，与 Round 3 child/log/
  handoff current truth 冲突。其余 identity、单一 receipt、12-file handoff、gates 均无新增问题。
- Round 4 只把父 summary 改为不易再次陈旧的状态：Round 1～3 identity 已退役、当前 terminal
  formal identity 等待双审、implementation 未授权；同步必要 log/continuity 后重验。
- Round 3 verdict/hash 全退役；新 current HEAD 必须由两位 reviewer 从零复审。
