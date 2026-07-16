# 任务执行日志：Frontend Artifact Path Dedupe Reduction

**功能编号**：`205-frontend-artifact-path-dedupe`\
**创建日期**：2026-07-15\
**当前状态**：formal review candidate；未进入 execute

## 1. 归档与安全规则

- 每个批次记录目标 revision/tree、范围、命令、结果、RC/CC/GAP 影响、回退和评审结论。
- formal 变化会使两个 Agent 的旧 verdict 同时失效；final source 另算 tree/diff hash。
- 临时 mutation RED 与 rollback rehearsal 只能在可恢复 patch/disposable clone 中执行，不使用
  destructive reset/checkout，不覆盖用户改动。
- 全量测试或 CLI hook 产生的 `.cursor`/continuity 副作用先机械核对，再用 `apply_patch` 恢复；
  不进入产品 diff。
- 产品、测试和本日志按逻辑批次提交；日志不预写未知 commit hash。

## 2. Batch 2026-07-15-001：完成范围审计与候选选择

### 2.1 persistent objective 审计

- WI-204 的 RC-09 No-Go、legacy 保留与 GAP-13 修复已经 mainline 收口；它只证明单一
  Program Finalization candidate 合法停止，不等于 WI-196 整体减重完成。
- WI-196 `development-summary.md`、`tasks.md`、`spec.md`、`plan.md` 一致要求 WP-02～WP-07
  继续逐项处置，并以 RC-08 route closure 作为 parent 关闭条件。
- 当前 `program_service.py=17,474` 行、`program_cmd.py=7,062` 行，仍明显不满足 RC-08 的
  两文件 ≤400 行终态。因此发布 v0.9.7 被暂缓，先执行剩余原子减重 WI。

### 2.2 fresh-main 基线

- 审计 revision：`e4f395e3b2247c0968d61aebd53814b1602f7845`。
- 隔离工作树：`.worktrees/release-v0.9.7-program-finalization`，HEAD 与 `origin/main` 相同。
- 命令：`uv sync --frozen`；结果：Python 3.11.15 环境安装成功。
- 命令：`uv run pytest -q`；结果：`3220 passed, 3 skipped in 534.62s`。
- 测试期间 `.cursor/rules/ai-sdlc.mdc` 被 real hook 改写；精确 diff 只包含 adapter 模板刷新，
  已用 reverse `apply_patch` 恢复，最终工作树 clean。

### 2.3 并行只读候选审计

**Pascal / 精简直接性**：

- 12 个 `_dedupe_paths` AST body hash 同为 `c75c133e2c`，每个 9 LOC，共 108 产品 LOC；
  13 个现有调用点、相同顺序/Path/error/no-I/O 语义。
- private helper 方案预计新增 23～26、删除 108、净删 82～85；目标切片下降 75.9%～78.7%。
- WP-04 三个 Loop Store 的完全一致切片只有 39 LOC，新增中立 helper 会超过 RC-06 25%，
  本轮 No-Go。

**Carver / WP-05 实测**：

- 六个固定 builder 中，只有 `build_p2_frontend_page_ui_schema_baseline` 条件 GO：317 LOC，
  预计终态 235～245、净删 72～82；新增保护硬 cap 18～20 LOC。
- 其余五项因资源表示已接近/超过 builder LOC，或实际依赖上游动态对象，判定 No-Go。
- 决策：先执行风险更低、RC 余量更明确的 T63/WP-03 path family；Page/UI baseline 作为下一
  独立 T65/WP-05 候选，不混入 WI-205。

## 3. Batch 2026-07-15-002：创建 WI-205 formal candidate

### 3.1 canonical scaffold

- branch：`feature/205-frontend-artifact-path-dedupe-docs`
- worktree：`.worktrees/205-frontend-artifact-path-dedupe`
- 基线：`origin/main@e4f395e3`
- 命令：`uv run ai-sdlc workitem init --wi-id 205-frontend-artifact-path-dedupe ...`
- 结果：canonical `spec.md / plan.md / tasks.md / task-execution-log.md` 创建成功，
  `program-manifest.yaml` 映射和 `next_work_item_seq=206` 已生成；未产生 Cursor side effect。

### 3.2 Round 0 formal 设计（旧口径，已失效）

- 比较了 private helper、12 处 inline `dict.fromkeys`、跨类型 generic utility 三个方案。
- 采用单 private `_artifact_paths.py`；拒绝保留 12 份 inline semantic truth，也拒绝扩大到 text/
  mapping/model dedupe。
- 当时冻结新增 raw LOC ≤27、新增 tests/harness=0、重复族 12→1、净删≥81、目标切片下降≥75%；
  该口径已被 Round 1 findings 判定不可复算并失效，仅保留为审计历史。
- 不触发 frontend solution confirmation：本项不改变技术栈、provider、页面、UI 或浏览器行为。

### 3.3 Round 1 formal review target（已失效）

固定顺序 SHA-256 tuple：

- `spec.md`：`7c55563fe303c653354cc69fa7b4a8d0c2bd8ac11c176b87a30b4cef0f66bebb`
- `plan.md`：`58d0c68aa74c0185394adfa5b66f8a0a1957365bdb725172e4372c4dee22d0b8`
- `tasks.md`：`404ab3d22580cd452442ee095049d481f49f74103f6bd50d07594ab8d75ded91`

占位扫描：`待补|TODO|TBD|用户故事 N|EntityA|待补充源码|待补工作流|...` 无命中。

### 3.4 下一步

1. Pascal/Confucius 对上述同一 tuple 独立 review。
2. 处置全部 finding，重算 tuple，直到双方一致 PASS。
3. 同步 Program Truth/continuity，提交 docs PR 并按本仓库协议 review/merge。
4. 从合并后的 main 新建 implementation branch，执行 T61A RED/GREEN 与最小产品减重。

## 4. Batch 2026-07-15-003：formal Round 1 finding 与修订

### 4.1 Pascal / 精简直接性 verdict

- 结论：FAIL。
- Critical：14 个既有 dedupe tests 均只制造一个重复路径；反转唯一结果仍为同一结果，计划中的
  mutation 不可能 RED，因此不能证明 first-seen order。
- Important：旧账本把 AST/non-empty 的 108 LOC 与 raw git deletion 混写，且没有固定命令和
  allowlist，净减重结论不可复算。

### 4.2 Confucius / 兼容证明性状态

- Confucius 在评审中复现“反转 first-seen order 后 14 tests 仍全部通过”。
- formal 内容在其最终 hash recheck 前已因处置 Pascal finding 而变化；按 hash freeze 规则，旧 tuple
  评审失效，Confucius 正确地没有对漂移内容出具 PASS/FAIL。

### 4.3 finding 处置

- 允许且只允许在既有 `test_frontend_contract_artifacts.py` 增加一个多 `Path` 顺序 test，非空
  LOC≤8；通过现有模块 private binding 覆盖 baseline local helper 与收敛后的 imported helper。
- T61A 冻结临时 reverse mutation 的预期差异为 `[first, second]` 对 `[second, first]`，要求稳定
  assertion RED，随后仅用 `apply_patch` 恢复并 GREEN。
- 将 Reduction Contract 拆为两套可复算账本：AST/non-empty 算法切片 108→9；固定 13 个产品
  文件使用 `git diff --numstat e4f395e3 -- src/ai_sdlc/generators`，要求 additions≤26、
  deletions≥108、net≤-82。
- 保护增量单列：唯一顺序 test≤8 非空 LOC；不得新增第二测试资产、fixture、harness 或 snapshot。
- 任一 formal 内容变化同时作废双方旧 verdict；下一轮只接受相同新 tuple 上的双 PASS。

### 4.4 Round 2 formal review target

固定顺序 SHA-256 tuple：

- `spec.md`：`2f34b3cf3b9c4f8365afea14f2b09073a1f453b22fd36b9080ae18c48245f2a1`
- `plan.md`：`6569f32c777f98568d01de26d804a70fe9074f94383ab0bba0ad8c6a6e653baf`
- `tasks.md`：`dc8145fdf2bfb79f82d90f59e80734f1d771e4038be3a87d68f02e1005389e25`

Round 2 只接受两个 Agent 在评审结束前复算并确认上述 tuple 未漂移后的 verdict。

## 5. Batch 2026-07-15-004：formal Round 2 findings 与修订

### 5.1 Pascal / 精简直接性 verdict

- 结论：FAIL；前后 tuple recheck 一致。
- Critical：父 RC-06 要求 product/test/harness/normalizer additions 合并计费，旧 formal 却分别
  允许产品 26 与 test 8，理论总额 34>27，属于拆账绕过。
- Important：raw ledger 已修好，但 AST gate 缺完整 serializer/digest/definition/call-site/LOC 的
  可执行命令，不能机械证明 12→1 且不保留 wrapper。

### 5.2 Confucius / 兼容证明性 findings

- Pascal finding 处置将使 tuple 漂移，因此 Confucius 按指令停止旧 tuple verdict。
- Important：RC-02 的 test LOC、complexity、fan-in/out 与 runtime 仍是近似值或未冻结。
- Important：CC-03/T61A-B 缺 baseline/candidate Golden、versioned normalizer/allowlist 与结构 diff。
- Important：truth gate 只检查 inventory，不足以证明目标 commit fresh/ready/exit 0/zero blocker；
  GAP-09～11 回归时必须 fail-closed/reopen。
- 已实证 private-binding 方案可行；正确 mutation 是 reverse(unique output)，不是 reverse(input)；
  12-module baseline 为 76 passed。

### 5.3 Round 2 finding 处置

- 不新增 test function：在既有 dedupe test function 内只加两行 direct-binding 顺序断言。
  预测/硬门禁为产品 raw additions≤24、test raw additions=2、source 合计≤26≤RC-06 cap 27。
- 完整 AST serializer 冻结为 `ast.dump(ast.Module(body=node.body), include_attributes=False)`；
  baseline 12 defs/13 calls/108 LOC/complexity 36/fan-out 36，完整 digest 为
  `fc689b7af4ea63842b5f23af0e85b3e1d71d9255606baabb679fded9b83be9b4`。
- 14 个既有 dedupe tests 精确为 280 raw/239 non-empty LOC；76-test targeted 五次运行分别为
  0.74/0.73/0.73/0.73/0.73 秒，median=0.73、p95=0.74。
- frontend CLI/Program baseline 命令：`uv run pytest -q tests/integration/test_cli_program.py
  tests/integration/test_cli_verify_constraints.py -k frontend`；结果：67 passed、208 deselected in 6.09s。
- 补充生产 caller 漏项：`test_cli_rules.py` 9 tests + 两个精确 solution-confirm nodeid，结果 11 passed
  in 0.77s；与 broad slice 合计 78 passed。既有断言是 substring/count/parsed payload 等 semantic
  assertions，不表述为 raw stdout/stderr equality。
- Golden 两次 run 改为顺序复用同一 shared basetemp；baseline receipt 在 candidate 覆盖前写到
  root 外；manifest key 使用 `.as_posix()`，regular file raw bytes 不做 allowlist 变换，pytest
  symlink/reparse-point 与 directory metadata 不比较。
- 修订后的 shared basetemp 命令连续运行两次，均为 418 files、root
  `ef3c1dd2e7ef0b776277d8b2d79365f5be672b797c5a25318aa1acf2de08f7f9`；12 个既有
  expected-file-set tests 合计覆盖 94 条 canonical paths。
- `wi205-tree-v1` 使用 regular non-symlink relative path + raw-bytes SHA-256，allowlist 为空；
  两次独立 baseline 均为 418 files，root digest
  `ef3c1dd2e7ef0b776277d8b2d79365f5be672b797c5a25318aa1acf2de08f7f9`。
- baseline/candidate 各生成一份 receipt；不新增 normalizer/harness source。CLI/Program semantic
  assertions 另跑完整 78-test surface，renderer normalizer 为空。
- 技术审计补齐全量 ledger：产品 modules=2602 raw/2275 non-empty；artifact test files=2723/2317；
  helper project-internal fan-out=0；direct call fan-in 分布为 contract=2、其余 11 modules=1；
  candidate 必须 module import fan-in=12、symbol call fan-in=13。
- truth gate 增加目标 commit 动态三元组、fresh/ready/exit 0/zero blocker、exact capability/blocking refs
  与 inventory；GAP-09～11 blocker/debt 再现即 fail-closed/reopen。

### 5.4 Round 3 formal review target

固定顺序 SHA-256 tuple：

- `spec.md`：`4030db5834569555ed243476d0c65dacb2570bdc58b01787f25b3c5f20dc0ac0`
- `plan.md`：`73c1c906793a8d169650a2ce6db000a94c66e32a4911ca480e971e199646130f`
- `tasks.md`：`801773745a2470ef53a0f28fc41107bd8987173d7f626d1eb05aec0abdfe054f`

Round 3 只接受两个 Agent 前后复算一致、且对上述同一 tuple 给出的明确 verdict。

## 6. Batch 2026-07-16-005：formal Round 3 finding 与标准 Git 收敛

### 6.1 Pascal / 精简直接性 verdict

- 结论：FAIL；前后 tuple recheck 一致。
- Critical：Round 3 的 custom `python -c` 实际实现遍历、过滤、相对化、排序、逐文件 SHA-256、
  manifest 序列化和 root digest，不能按“一个逻辑命令/一行”逃避 RC-06；正常格式化后会使
  product 24 + test 2 + normalizer 超过 cap 27。
- 删除 Golden 同样不可接受：父 WI-196 CC-03/WP-01/T61A-B 明确要求 versioned normalizer、
  GoldenSnapshot、DifferentialResult 与 rollback receipt。

### 6.2 双 Agent 交叉裁决

- Pascal/Confucius 一致保留当前 typed 9-line product helper；借用任意 sibling module 会制造错误
  领域耦合，`dict.fromkeys` 会改变 AST/调用细节，无类型 helper 会弱化静态合同。
- 双方一致采用标准 Git object database identity，normalizer id=`wi205-git-tree-v1`。Git 原生比较
  relative path、raw blob bytes、mode 与 symlink target；不新增自写遍历/过滤/序列化/hash source，
  handwritten harness/normalizer source LOC=0。
- 双方一致采用 `allowlist=[]`：不排除 pytest `*current`。在固定 shared absolute basetemp、fresh
  index、同一 Git/toolchain 下，Confucius probe 两次均 76 passed、463 entries（418 regular +45
  mode-120000 symlinks）、OID `b7870e8536674c689402d6f35436ed3fcf2aa24c`。
- root 随后用另一 fixed absolute basetemp 独立复算，两次为 76 passed、463 entries、OID
  `68caa600db4789be8743eab641e336faf3185e6d`。两 probe 的 OID 差异来自被纳入比较的 absolute
  symlink target root；各自在同一 root 内稳定。这验证了“paired run 必须复用同一 absolute
  basetemp”，也验证 OID 不得跨 root/OS 当常量。任一 paired baseline 不稳定或需要 exclude 即
  fail-closed/RC-09。
- 父 `specs/196.../plan.md` 要求 structured differential/rollback receipt 写入 child scoped work-item。
  因此只新增一个 generated
  `.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`，同时
  承载 surface manifest、GoldenSnapshot、DifferentialResult 与 rollback；它计 1 个 snapshot/receipt
  和实际体积，不计 handwritten source LOC。execution log 记录 URI/SHA-256，handoff 只做摘要。

### 6.3 RC-06 最终口径与下一轮

- product raw additions≤24 + existing test raw additions=2 + custom harness/normalizer source=0，
  total handwritten source additions≤26≤27。
- custom `wi205-tree-v1` Python normalizer、418-file-only Golden 与
  `ef3c1dd2...e08f7f9` 均为历史实验，已废弃，不得作为 T61A/T61B evidence。
- `spec.md + plan.md + tasks.md` 完全对齐后重算 Round 4 tuple；只有 Pascal/Confucius 对该同一 tuple
  前后复算一致并明确 PASS，才能进入 T61A/实现。

### 6.4 Round 4 formal review target

固定顺序 SHA-256 tuple：

- `spec.md`：`f85bbe21bc24c505c4cc13fb47aa61f5909bd8bb3e4c9a8af002df2030886c21`
- `plan.md`：`d23bf71f04fead7a2cc5ab67d42179d0aac396a05c95bae9fa25ee21bbb8cee8`
- `tasks.md`：`e64a1ecfd81b6664cb29ac763a43c43d8f3b3d91a5bdb575dabe205459a6ab96`

Round 4 只接受两个 Agent 对上述同一 tuple 完成全文评审、结束前复算三 hash 未漂移后给出的明确
`VERDICT: PASS`。任一正式文件变化同时作废双方 verdict。

## 7. Batch 2026-07-16-006：formal Round 4 findings 与修订

### 7.1 同哈希 verdict

- Pascal / 精简直接性：`PASS`；开始/结束 tuple 一致；确认 `24+2+0=26≤27`、标准 Git 无隐藏
  source、单 receipt 最小、任务无过度实现。
- Confucius / 兼容证明性：`FAIL`；开始/结束 tuple 一致。
- Important 1：仅设置 `core.autocrlf=false` 不能阻断 system/global/worktree `.gitattributes` 或 clean
  filter；不同 raw bytes 可能进入同一 index blob，造成 Git tree 假等价。
- Important 2：formal 禁止 workflow 变更，却要求现有 CI 在三平台各跑 baseline×2↔candidate paired
  tree；当前 compatibility workflow 只 checkout candidate 并跑 pytest，该证据不可执行。

### 7.2 finding 处置

- `wi205-git-tree-v1` 增加 `GIT_ATTR_NOSYSTEM=1`、外置空 `core.attributesFile`、basetemp 内零
  `.gitattributes` 与 fresh Git `info/attributes` 为空的 fail-closed 检查；receipt 记录全部配置与检查。
  PowerShell runbook 使用 native-command fail-fast；未新增 reusable harness/normalizer source。
- 本机 zsh 等价协议实测两次：`76 passed`，463 entries，tree OID 均为
  `68caa600db4789be8743eab641e336faf3185e6d`；attributes isolation checks 全部通过。
- paired Git tree/rollback 明确限定为本地 T61A/B pre-merge gate。CC-07 由现有 Windows/macOS/Linux
  full pytest 承担；full suite 包含强化后的顺序 test 与 76 个 artifact tests。不修改 workflow、
  不新增跨平台 harness，也不宣称 CI 产出 baseline/candidate OID。

### 7.3 Round 5 formal review target

固定顺序 SHA-256 tuple：

- `spec.md`：`df53befed5871c1357159c560091d3bc409095794723d4175d2f13bb12b0e2e9`
- `plan.md`：`e9db0cd839806c7d0f8049875abe7cd997a7c3f50da65a4e33d151c097903bfc`
- `tasks.md`：`17d126249eca5bfb1c9d05f52a9bb46e82791a5cbf12127edc0692ccd0665251`

Round 5 仍要求两个 Agent 对上述同一 tuple 全文评审并在结束时复算未漂移；任一修改使旧 verdict
同时失效。

## 8. Batch 2026-07-16-007：formal Round 5 finding 与修订

### 8.1 同哈希 verdict

- Pascal / 精简直接性：`FAIL`；Confucius / 兼容证明性：`FAIL`；双方开始/结束 tuple 均一致。
- 共同 Important：PowerShell runbook 启用 native-command fail-fast 后，fresh Git repo 上未显式设置
  的 `core.symlinks` 查询会 exit 1；当前 macOS/Linux 实测 `core.filemode=true`、`core.symlinks`
  unset/exit 1，因此 protocol 会在 receipt 记录阶段中止。
- Confucius 另指出 `$PSNativeCommandUseErrorActionPreference` 需要 PowerShell 7.3+；未冻结版本时，
  较旧 PowerShell 又可能不 fail-fast，造成假绿。

### 8.2 finding 处置与实证

- `core.filemode/core.symlinks` 改为
  `git config --bool --get --default=true`；显式 false 仍记录 false，unset 则记录有效默认 true，命令
  exit 0。fresh external Git repo 实测两项均输出 true、协议不中止。
- PowerShell block 在执行任何 native command 前断言版本≥7.3，并在 receipt 记录 shell/version；
  保留 native-command fail-fast。该修订只改变执行 runbook，不新增 source 或产品范围。

### 8.3 Round 6 formal review target

固定顺序 SHA-256 tuple：

- `spec.md`：`df53befed5871c1357159c560091d3bc409095794723d4175d2f13bb12b0e2e9`
- `plan.md`：`cfb7d032e847e6bdd6c877c2e41780bd11213fa8b413d8081a2f7c81814839e6`
- `tasks.md`：`17d126249eca5bfb1c9d05f52a9bb46e82791a5cbf12127edc0692ccd0665251`

Round 6 要求两个 Agent 对上述同一 tuple 全文评审、结束复算一致并明确 PASS；任一修改使 verdict
失效。

### 8.4 Round 6 同哈希双 PASS

评审完成时间：`2026-07-16T04:07:57Z`。

| agent | dimension | target tuple | findings | disposition | verdict |
|---|---|---|---|---|---|
| Pascal / `wi200_lean_design` | 精简、直接性、预算、可执行性 | `df53befe / cfb7d032 / 17d12624` | 无 Critical/Important/其他可操作问题 | 无待处置项 | `PASS` |
| Confucius / `wi200_proof_safety` | 兼容、证明、回退、truth | `df53befe / cfb7d032 / 17d12624` | 无 Critical/Important/其他可操作问题 | 无待处置项 | `PASS` |

两位 Agent 均在开始与结束复算完整 SHA-256，与 §8.3 精确 tuple 一致；只读评审未修改文件。formal
三件套自此冻结，后续 truth/continuity/PR 记录不得修改三文件；若修改，必须重新双审。

### 8.5 formal post-review governance verification

- `OPENAI_CODEX=1 uv run ai-sdlc program truth sync --execute --yes`：exit 0；snapshot state=`ready`；
  inventory=`1081/1081`、unmapped=0、missing=0；snapshot hash
  `2fa46a15d8b37a6a9befdaeaad451695e6f9f7e63c1c8adfe11cdc2316c2dd4b`。
- `uv run ai-sdlc program truth audit`：exit 0；state=`ready`、snapshot state=`fresh`、两个 release
  capability closure=`closed`/audit=`ready`，zero blocker。
- `uv run ai-sdlc program validate`：PASS；`uv run ai-sdlc verify constraints`：no BLOCKERs；
  `git diff --check`：PASS。
- 三 formal hash 复算仍精确等于 §8.3；上述日志落盘后再次 sync/audit，确保最终 snapshot 覆盖本记录。

## 9. Batch 2026-07-16-008：staged whitespace gate 与 Round 7

- 首次 staged `git diff --cached --check` 发现新 Markdown 元数据使用双空格 hard-break，构成 trailing
  whitespace；commit `9261ec8b` 已本地生成但未 push/PR。
- 只删除 `spec.md` 顶部 4 行、`plan.md` 顶部 3 行、`tasks.md` 顶部 3 行以及 summary/log 元数据的
  行尾双空格；字节差异仅为 line-ending 前两个 U+0020 删除，语义、命令、预算和验收合同未变。
- 清理后 `git diff --check` 与 staged baseline check 均零输出。因为 formal 三文件字节变化，Round 6
  双 PASS 按 anti-drift 规则失效，必须对新 tuple 再审；本地 commit 将在双 PASS/truth 后 amend。

Round 7 exact tuple：

- `spec.md`：`dcc8c533ddd90c4d1585c82787b04c1a18c61337f91daceb42d7715db3c5dbe2`
- `plan.md`：`5166e4bf90367aa726b5153554668758c22f91d23b88d6a28b39d112588b30b4`
- `tasks.md`：`ff33ad8febcf798462144e83d5e7b5b0ead2ae1c98fec623ad77007dc2cbb6bb`

Round 7 仍要求两个 Agent 开始/结束复算一致并明确 PASS；不得因差异机械而跳过 hash 纪律。

### 9.1 Round 7 verdict 与渲染修订

- Pascal：`PASS`；确认唯一字节差异为指定 trailing spaces。
- Confucius：`CHANGES_REQUESTED`；双空格是 CommonMark hard break，直接删除会把 metadata 在 HTML
  中折叠为一个 paragraph 的连续文本，存在真实 rendering regression。
- 处置：在 formal 10 行以及 summary/log 相同 metadata 模式使用反斜杠 hard break；无 trailing
  whitespace。`markdown-it-py 4.0.0` 实证 spec metadata 仍生成 4 个 `<br />`，视觉分行保持；
  `git diff --check` 零输出。

Round 8 exact tuple：

- `spec.md`：`5984e1ac079c81f3b7bb26bbe4c2a4d03ffec09b4b7606749ec9e416a107dda7`
- `plan.md`：`6fc9c41e43400dbb34fcb049e3b1051227eb330e7c48ab9e5f6680d3f0d1051d`
- `tasks.md`：`721036d5877eb4c855a8b01e7f01eb6ea9861d0a560c252477487c1ecb5bec89`

Round 8 继续执行完整 anti-drift 双审；任一修改使 verdict 失效。

### 9.2 Round 8 同哈希双 PASS

- Pascal / 精简直接性：`PASS`；Confucius / 兼容渲染证明：`PASS`。
- 两者开始/结束 SHA-256 均精确等于 §9.1 Round 8 tuple，无文件漂移、无可操作 finding。
- `markdown-it-py 4.0.0` 对 spec/plan/tasks 分别生成 4/3/3 个 `<br />`；当前反斜杠版本与 Round 6
  双空格版本渲染 HTML 逐字节相同；`git diff --check` clean。
- Confucius 补充运行 `tests/unit/test_artifact_target_guard.py`：`9 passed`；未发现机器 parser 依赖
  metadata 行尾字节。
- Round 8 tuple 成为最终 formal freeze；后续只允许更新 execution log、summary、truth/continuity，
  不再修改 `spec.md/plan.md/tasks.md`。

## 10. Batch 2026-07-16-009：PR #133 CI truth failure 与 Round 9 重算

### 10.1 CI failure 与顺序修复证据

- formal branch 已以 commit `b92184982a3578da4e758bf02e6c68dd45c55e41` 推送并创建 PR #133。
  `verify` 与 Windows pwsh/cmd smoke 通过；六个 Windows/macOS/Ubuntu × Python 3.11/3.12 full-suite
  jobs 均只在同一个 root manifest nodeid 失败。macOS/Ubuntu 为 `1 failed, 3219 passed, 3 skipped`；
  Windows 为 `1 failed, 3218 passed, 4 skipped`。
- 唯一失败为
  `tests/integration/test_repo_program_manifest.py::test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence`。
  WI-205 五件套使 Program Truth inventory 从 1076/1076 增为 1081/1081、close layer 从 204/204
  增为 205/205；既有 assertion 仍冻结旧值。
- 本地先只替换 inventory tuple，测试精确 RED 于 close `204 != 205`；再替换 close tuple 后同一
  nodeid 为 `1 passed in 66.97s`。两处均是既有 assertion line replacement，无新 test/function/file，
  raw additions=2、deletions=2。

### 10.2 RC-06 No-Go 与最小重新收敛

- Pascal/Confucius 均确认 Git numstat 的 replacement additions 必须计入 RC-06，不能用两条 deletion
  抵扣。Round 8 的 9 LOC helper 预测为 product 24 + order test 2 + inventory truth 2 = 28，超过
  cap 27，因此旧 exact-body 方案为 No-Go。
- 重新候选只把旧反向 `if path in seen: continue` 收敛为正向 `if path not in seen:`；membership、
  `seen.add`、`unique.append` 的执行条件/顺序、hash/equality 调用与异常传播不变。candidate function
  为 8 non-empty LOC；新 module 11 raw lines + 12 imports = product additions 23。
- 独立 AST 复算 candidate body digest 为
  `aec166ee2bb024d3307e2501c63d2b38373207d4e8e355bc73861a2814678c91`，complexity=3、
  syntactic fan-out=3。最终冻结预算为 product 23 + order test 2 + inventory truth 2 = 27；
  product deletions≥108、net≤-85。
- Program Truth source inventory 只枚举 manifest spec 五层与 discovery/registry 文档，不枚举
  `src/` Python 文件；因此后续新增 `_artifact_paths.py` 不会再改变 1081/205 assertion。本轮 formal
  明确把 RC-06 限定为 handwritten product/test source，formal/truth/continuity 文档不冒充代码预算。
- Round 8 的双 PASS 已因 formal 内容变化失效。Round 9 必须由 Pascal/Confucius 对新的同一完整
  `spec.md + plan.md + tasks.md` tuple 从头评审并在结束复算无漂移后分别明确 PASS，才允许进入 T61A。

### 10.3 Round 9 formal review target

送审前门禁：root manifest 精确 nodeid `1 passed in 67.47s`；`program validate: PASS`；
`verify constraints: no BLOCKERs`；`git diff --check` clean。固定顺序 SHA-256 tuple：

- `spec.md`：`8f92edd344c80f49591581fe52b5af62c19e37f4b32492c21e3f5da2813fafd7`
- `plan.md`：`c9713a59bbdf169ed2d9c892bb2bdc18a2c77153e7b80bbec417a45eb7238676`
- `tasks.md`：`cb482c11ca7efbd6dcd3eeb56fb1072924fe647d2e9587915b29d9bd0183e3dc`

Round 9 只接受两个 Agent 对上述同一 tuple 的完整只读评审；开始/结束 hash 必须一致。任何 formal
修改使双方 verdict 同时失效并进入下一轮。

### 10.4 Round 9 双 FAIL 与 finding 处置

- Pascal / 精简直接性：`FAIL`；Confucius / 兼容证明性：`FAIL`。两者开始/结束均复算为 §10.3
  完整 tuple，无文件漂移。
- Pascal Important 1：`tasks.md` T23/T32 与 `plan.md` 开放问题仍把最终测试 diff 误写为只有两行，
  会与已纳入 RC-06 的 root truth `+2/-2` 冲突；RC 追踪也漏列 T14。处置：全量区分 order `+2/0`
  与 root truth `+2/-2`，追踪矩阵补 T14。
- Pascal Important 2：验证矩阵写“原算法逐行等价”，但 candidate AST/digest 已变化。处置：改为
  “正向分支可观察语义等价 + tests”。
- Confucius Important：spec §1 省略 `ast.Module(..., type_ignores=[])` 与 `.encode()`，按文字复算得到
  `c12c23a6...cdf48a` 而不是冻结的 baseline digest。处置：spec 改为与 Appendix A.1 完全一致的
  `hashlib.sha256(...encode()).hexdigest()` serializer。
- 其余复算无可操作问题：两者均确认 candidate 8 LOC/11 raw module、product additions 23、
  `23+2+2=27`、正向 membership 非 line-golf。Confucius side-effect probe 覆盖 distinct/equal objects、
  hash/equality/iterator failure、unhashable 与 mixed hashable non-Path，输出、调用序列和异常一致；
  artifact 76、CLI broad 67、rules/exact 11 均通过，root manifest `1 passed in 66.43s`。

### 10.5 Round 10 formal review target

定向修订后 `git diff --check` clean。固定顺序 SHA-256 tuple：

- `spec.md`：`e90ca209bf567a0d019163d9d0d49f26d74fc4f88d3950f09c9d90a046e751d1`
- `plan.md`：`a04f18a627d9661b0582fa73c9079b25ef713fcf72de7db196197617dbf02eef`
- `tasks.md`：`9ec861f4410a17c16de289bde9054778e73d0c75d6d32b16a7bbfc78c4ab1ed7`

Round 10 仍需 Pascal/Confucius 对上述同一完整 tuple 从头复审、结束复算未漂移并分别明确 PASS。

### 10.6 Round 10 同哈希双 PASS

| agent | dimension | target tuple | findings | verdict |
|---|---|---|---|---|
| Pascal / `wi200_lean_design` | 精简、直接性、预算、原子性 | `e90ca209 / a04f18a6 / 9ec861f4` | 无 Critical/Important/其他可操作问题 | `PASS` |
| Confucius / `wi200_proof_safety` | 兼容、证明、回退、truth、CI | `e90ca209 / a04f18a6 / 9ec861f4` | 无 Critical/Important/其他可操作问题 | `PASS` |

- 两位 Agent 均在开始与结束复算 §10.5 三个完整 SHA-256，结果精确一致；只读评审未修改文件。
- Pascal 独立确认 baseline 12 defs/108 LOC/13 calls、candidate 8 LOC、11 raw module、product additions
  23 与 `23+2+2=27`，方案无 line-golf、隐藏 source 或过度实现。
- Confucius 独立确认 exact serializer、side-effect/exception 轨迹、formal `+5 sources/+1 close` 与后续
  product file 不进入 truth inventory 的边界、Golden/rollback 及六个跨平台 full-suite job 的职责。
- Round 10 tuple 成为 formal freeze；后续只更新 summary/log/truth/continuity。若三份 formal 任一字节
  变化，双 PASS 立即失效并必须重审。

### 10.7 formal post-review Program Truth

- `OPENAI_CODEX=1 uv run ai-sdlc program truth sync --execute --yes`：exit 0；snapshot state=`ready`；
  snapshot hash=`0a9806010bcfee8d193f4370f18808afc8d96b6bfae2f04c3def40ef584959f5`；
  inventory=`1081/1081`、unmapped=0、missing=0；spec/plan/tasks/execution/close 均为 `205/205`。
- `uv run ai-sdlc program truth audit`：exit 0；state=`ready`、snapshot state=`fresh`；两个 release
  capability closure=`closed`/audit=`ready`，zero blocking refs。
- 本记录会改变 execution source hash，因此记录后必须再执行一次 sync/audit；只接受第二次 audit
  的 fresh snapshot 作为提交前最终证据。

## 11. Batch 2026-07-16-010：T61A/T61B 实现、差分与回退验收

### 11.1 fresh-main baseline 与 mutation RED/GREEN

- implementation worktree 从 formal PR #133 merge commit
  `a76ef8b1b63cc65046bf91e09fad2ebb6f40073d` 创建；branch 为
  `feature/205-frontend-artifact-path-dedupe-dev`。三份 formal SHA-256 仍精确等于 §10.5。
- 12-module artifact suite 五次均为 76 passed；pytest 秒数为
  `1.67 / 0.74 / 0.72 / 0.74 / 0.75`，含首次创建 venv 的冷启动；全样本 median=0.74，
  nearest-rank p95=1.67，四次 warm-run p95=0.75。
- baseline AST 复算：12 definitions、13 calls、108 algorithm LOC、complexity/fan-out=36、body digest
  `fc689b7af4ea63842b5f23af0e85b3e1d71d9255606baabb679fded9b83be9b4`；测试账本仍为
  12 files=2723/2317、14 dedupe symbols=280/239。
- 同一 `/tmp/ai-sdlc-wi205-shared`、外置 Git dir、fresh index、空 attributes file、
  `GIT_ATTR_NOSYSTEM=1`、`core.autocrlf=false` 下，两次 baseline 均为 tree
  `a9b62108e4d591bb74ea2947a531085236445333`、463 entries（418 regular +45 symlinks）。
- 既有 contract dedupe test 只增加冻结的两行 direct-binding 顺序断言，diff=`+2/0`。临时把旧
  helper 改为 `return list(reversed(unique))` 后，精确失败为 index 0 `second != first`；用
  `apply_patch` 恢复后 nodeid 1 passed、artifact suite 76 passed。未新增 test function/file/helper。

### 11.2 最小产品减重与 RC 账本

- candidate commit：`7b96f96952d2733e3d7969e70e2b9ae24ef0611e`。
- 新增 11 raw-line `_artifact_paths.py`；12 个 generator 各加一条 private import 并删除本地 body；
  13 个 `return _dedupe_paths(...)` 调用表达式及 writer/serialization 未修改。
- candidate AST：1 definition、13 calls、12 imports、8 algorithm LOC、complexity/fan-out=3，digest
  `aec166ee2bb024d3307e2501c63d2b38373207d4e8e355bc73861a2814678c91`。
- `git diff --numstat e4f395e3 HEAD` 的冻结 source set：产品 additions=23、deletions=132、net=-109；
  order test=`+2/0`；root inventory truth=`+2/-2`；RC-06 additions=`23+2+2=27`，精确等于 cap。
  candidate test ledger 为 12 files=2725/2319、14 dedupe symbols=282/241。

### 11.3 T61B differential、CLI surface 与 rollback

- candidate 76-test artifact suite 通过；raw tree 仍为 baseline
  `a9b62108e4d591bb74ea2947a531085236445333`/463，`diff-tree --binary` 零输出，allowlist=`[]`。
- broad frontend slice：67 passed、208 deselected in 5.59s；rules 9 tests + 两个精确
  solution-confirm nodeid：11 passed in 0.71s；合计 78 passed。
- CLI/governance 测试会安装 managed `.cursor/rules/ai-sdlc.mdc`；每次均用 `apply_patch` 恢复为
  HEAD 精确内容，最终 diff 为零，未把测试副作用纳入实现。
- disposable clone 中 candidate `7b96f969`、revert `091f5d548dec16d079fa67d879e60fec3493a103`、
  restored candidate `c1db361be20c016da6a31fd88ed997bbcd8c3b1b` 三段均为 76 passed，且 raw tree
  均与 baseline 相同；主 worktree 未执行 reset/checkout。

### 11.4 全量、治理与结构化收据

- fresh-main baseline full suite：`3220 passed, 3 skipped in 534.72s`；candidate full suite：
  `3220 passed, 3 skipped in 512.20s`。
- `uv run ruff check .`：PASS；`uv run ai-sdlc program validate`：PASS；
  `uv run ai-sdlc verify constraints`：no BLOCKERs；`git diff --check`：PASS。
- pre-final evidence `program truth audit`：state=`ready`、snapshot=`fresh`、inventory=`1081/1081`、
  unmapped=0、missing=0、zero blocking refs。execution/summary 落盘后仍须 sync/audit 最终 target。
- 唯一收据：
  `.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`；
  6977 bytes；SHA-256
  `3c0269fd5f34063f70600659ca2b4497dd78752e1f17af1f3ce68cf71e090310`；schema
  `wi205-differential-rollback-receipt.v1`；GoldenSnapshot、DifferentialResult、rollback verdict 均 PASS。

### 11.5 remaining gate

- 提交 execution/summary/receipt/continuity 后执行最终 Program Truth sync/audit，记录 target
  revision/generated_at/snapshot hash。
- 计算 final tree/diff hash，交 Pascal/Confucius 对同一 target 独立复审；只有双 PASS 才允许 push、
  implementation PR、Codex review/heartbeat、跨平台 CI 与 merge。
