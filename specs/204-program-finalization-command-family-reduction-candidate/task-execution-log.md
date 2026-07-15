# 任务执行日志：Program Finalization Command Family Reduction Candidate

**功能编号**：`204-program-finalization-command-family-reduction-candidate`
**创建日期**：2026-07-15
**当前状态**：Batch 0 formal drafting；产品代码未授权

## 1. Batch 2026-07-15-001：候选选择与 current baseline 复算

### 1.1 只读结论

- 当前 mainline：`6d2dc47fa57b589ecafaff9872a395684e535018`。
- WI-203 formal receipt：`75d3dda5ec8b45d0f9441058da889163d814b717`；target hash
  `cfcd63d7662175e8e9d413b831e582ee81d00958cb8d9c3c8c717de0987dc57f`。
- `program_cmd.py`、CLI tests、service tests 从 WI-203 baseline 到 current mainline 的 Git blob
  全部一致；2,020 target LOC、1,804 可删 body、216 retained、432 branch proxy 可继续使用。
- 产品新增 `P` 时：family=`216+P`，产品净删=`1804-P`；P≤303 保证 family≤519、净删≥1,501。
- 三个独立只读分析共同推荐 WI-203 candidate，且共同反对直接编码：必须先有独立 WI-204
  formal、T61A actual ledger 和 readiness 双 `GO`。

### 1.2 预审意见吸收

| 维度 | 结论 | Formal 处置 |
|---|---|---|
| 精简设计 | 该候选是当前唯一已冻结精确切片、删除下限与零公共抽象约束的路线 | 绑定单一 runner、product≤303/目标≤285 |
| 兼容安全 | WI-203 candidate 条件 GO；不能直接编码或自动成为 T62A sponsor | 独立 WI、T61A、release/deletion/settlement 边界 |
| 独立测量 | 新保护最低可信 155～175，硬上限 180；165 个既有测试必须复用 | planned claim=175、hard=180、超限 No-Go |

这些是 formal drafting 输入，不是 T02 的最终同 hash verdict。

### 1.3 已执行命令

- `git rev-parse` / blob identity / SHA-256 / AST-LOC 复算。
- `uv sync --frozen`。
- `uv run ai-sdlc workitem init`（WI-204 title/id/input/related references），创建 canonical docs 与 manifest mapping。

### 1.4 当前边界

- 未修改 `src/`、`tests/`、runtime rules、provider 或 workflow。
- Formal review target 尚待计算并提交两个独立 reviewer。
- Formal 合入前 effective claim=0，T61A 与 candidate 编码均未授权。

## 2. Formal 对抗评审 Round 1

**Target hash**：`1e195b071986bf052aa5ab63c97be9fad97a7aab4c0cc21e39e0702043e09501`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T11:32:35Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T11:32:09Z | FAIL | sponsor 激活顺序；candidate/删除后门槛混淆；replacement residual 防重复公式缺失 |

处置：Round 1 PASS 随 target 变化作废。Formal 已增加首个 T61A 写入前的 active receipt、具体
owner/handoff 与 30/14/7 日状态机；T24 只验 candidate 共存态并把终态指标标为 post-deletion
projection；冻结新 ID/hash/key 与扣除同源 claim 的 residual 公式。两位 reviewer 必须对新 hash
重新独立评审。

## 3. Formal 对抗评审 Round 2

**Target hash**：`fb370d904776b6a2d7d9a71b6e409228d5fbf01a2e8c76a6609a56e6f1842bd2`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T11:36:44Z | FAIL | active receipt 只在 implementation branch，不满足 mainline 可审计；residual 变量口径不可复算 |
| Confucius / 兼容安全 | 2026-07-15T11:36:47Z | PASS | none；Round 1 三项已关闭 |

处置：Round 2 verdict 全部作废。新增 activation-only PR，要求 exact receipt content 先成为
`origin/main` ancestor，再从 activation merge 创建 implementation branch；保护代码因此不能早于
mainline sponsor state。Residual 改为绑定 mainline ledger snapshot，逐一定义 D/C、跨 origin
占用、同 origin unique claims 与新风险缓冲，并固定单次扣减顺序。

## 4. Formal 对抗评审 Round 3（最终）

**冻结 target hash**：`487f460ab76cda9fa19bdb3aac4bc462211667b4bdf12fc2b65346e1d46ea54d`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T11:40:33Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T11:43:33Z | PASS | none |

双方独立复算 hash 一致。最终确认 activation-only receipt 必须先 mainline、implementation 从
activation merge 创建、receipt 不可见时 fail closed；candidate 共存态与 post-deletion 终态
分离；replacement residual 绑定 mainline snapshot 且跨 origin/同 origin/风险缓冲各扣一次。
Formal target 自此冻结；后续只允许在本日志与 handoff 追加 receipt，不修改三份 target 文件。

## 5. Formal 对抗评审 Round 4 触发

Truth sync 物化 WI-204 后，source inventory 从 1071/1071、close 203/203 变为
1076/1076、close 204/204；仓库级真值测试仍冻结旧 tuple。为避免在 formal 白名单外偷偷改测试，
三份 target 增加仅允许两个既有 tuple 机械同步、不得修改其他测试逻辑/文件的例外。Round 3 双
PASS 因 target 变化作废；新 target hash 为
`0f834dd204dad73f372bdc8a9f1cf21720efe29b3e2769ccfd8f1ad9d55f0842`，必须重新双审。

## 6. Formal 对抗评审 Round 4（最终）

**冻结 target hash**：`0f834dd204dad73f372bdc8a9f1cf21720efe29b3e2769ccfd8f1ad9d55f0842`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T11:53:08Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T11:53:37Z | PASS | none |

双方独立复算 hash 一致。Confucius 反向移除唯一声明的 truth tuple 白名单增量后，复现 Round 3
hash `487f460a...ea54d`，确认无隐藏 target 变化。Round 4 后 formal target 冻结。

### 6.1 Truth tuple TDD receipt

- 红灯：`uv run pytest -q tests/integration/test_repo_program_manifest.py` → 1 failed；actual
  inventory=1076，旧 expected=1071。
- 变更：仅把 source tuple `1071/1071/0/0→1076/1076/0/0`、close tuple
  `203/203→204/204`。
- 绿灯：同命令 → `1 passed in 57.22s`。
- 未新增测试逻辑、未放宽断言、未修改其他测试文件；不计 candidate protection claim。

## 7. Formal 全量验证

- Frozen target hash：`0f834dd204dad73f372bdc8a9f1cf21720efe29b3e2769ccfd8f1ad9d55f0842`。
- `uv run ruff check tests/integration/test_repo_program_manifest.py`：PASS。
- `uv run pytest`：`3186 passed, 3 skipped in 496.12s (0:08:16)`。
- `uv run ai-sdlc program truth audit`：ready/fresh，1076/1076 mapped，close 204/204。
- `uv run ai-sdlc verify constraints --json`：blockers=0，advisories=0。
- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc workitem plan-check --wi specs/204-program-finalization-command-family-reduction-candidate`：drift=NO。
- `git diff --check`：PASS；Cursor adapter 与 WI-196 scoped handoff 无 diff。

## 8. Formal 对抗评审 Round 5 触发

暂存检查发现三份 target 与 execution log 的 Markdown 软换行使用行尾双空格，违反仓库
`git diff --check`。已只删除这些行尾空格，不改变任何文字、数字或语义；Round 4 verdict 因
target bytes 变化作废。新 target hash：
`069fbc6fd816d0e5dd8f4163ffd5af332444313c887bb41fb750ccb0d2026123`。

## 9. Formal 对抗评审 Round 5（最终）

**最终冻结 target hash**：`069fbc6fd816d0e5dd8f4163ffd5af332444313c887bb41fb750ccb0d2026123`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T12:10:25Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T12:10:47Z | PASS | none |

两位 reviewer 均独立证明：只把删除的 13 处行尾双空格加回，即可逐文件复现 Round 4 hash 和
总 hash；因此正文、数字、白名单、授权与合同语义均未变化。当前三份 target 无 trailing
whitespace，Round 5 为最终双 PASS。

## 10. PR #128 当前头审查修复

- Codex P2：`linked_wi_id` 已指向 WI204，但 `checkpoint.feature.*` 仍指向 WI196；执行授权等路径
  继续读取 `feature.spec_dir`，恢复后可能操作错误工作项。
- 根因：`workitem link` 的合同只写 linked fields，不代表 active feature 切换；当前 docs branch
  已实际切换到 WI204，却遗漏了 feature binding 的同批更新。
- 修复：`feature.id/spec_dir/design_branch/current_branch` 全量绑定 WI204；`feature_branch` 预留
  canonical `-dev` 分支；docs baseline 固定为本分支创建点 `6d2dc47f...5018` 与创建时间。
- 保护边界：三份冻结 target 未修改，最终 target hash 仍为
  `069fbc6fd816d0e5dd8f4163ffd5af332444313c887bb41fb750ccb0d2026123`；未写入产品代码或
  T61A 保护代码。
- 定向验证：checkpoint/recover/execute authorization/task guard/readiness/branch manager 共
  `65 passed in 3.55s`。
- 首次治理验证如实阻断于 branch disposition 尚未登记；当前 docs branch 只处于
  `merge-pending`，合并后必须再复验 mainline ancestor truth。
- 关联 branch/worktree disposition 计划：`merge-pending`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`retained(PR #128 review)`

## 11. Formal 对抗评审 Round 6：FAIL 与缺口回填

**受审 HEAD**：`38fd75b72206a6538e49ca390fd08e92b6422b42`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T12:47:00Z | FAIL | 任意自由文本 disposition 可使 branch-check 假绿；`-dev` 与冻结 owner 冲突 |
| Confucius / 兼容安全 | 2026-07-15T12:48:22Z | FAIL | `-dev` 与 owner/activation 分支身份冲突；handoff 下一步已过期 |

处置：Round 5 的 target PASS 因三份 formal 文档变化作废，Round 6 的 HEAD verdict 也不能用于
新目标。Formal 已把 implementation owner 统一为 BranchManager canonical `-dev`，并新增 GAP-12：
branch disposition 使用显式 allowlist，`merge-pending` 只能通过 pre-merge branch-check/constraints，
close-check 必须阻断，unknown/free-text fail closed。新设计 target hash 为
`e3ce86022eae15c7753f2d9e83e40da4698f405bd10f4a5c8a3f4be7231998ea`；GAP-12 写代码前必须先获
两位 reviewer 对该同一 target 的设计 PASS。

## 12. Formal 对抗评审 Round 7：FAIL 与矩阵加固

**Target hash**：`e3ce86022eae15c7753f2d9e83e40da4698f405bd10f4a5c8a3f4be7231998ea`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T12:52:00Z | FAIL | 缺精确路径/LOC 预算；pending 缺 missing/ahead=0/behind/diverged 反例 |
| Confucius / 兼容安全 | 2026-07-15T12:53:13Z | FAIL | scalar pending 可覆盖多个 branch；archived/retained/removed 缺双向真值 |

处置：e3ce target 作废。Formal 现冻结 15 个精确路径与新增非空手写 LOC 上限
80 runtime/scaffold/rule/template + 180 tests = 260 total；`merge-pending` 仅允许唯一、当前 checkout、
有 worktree、ahead>0、behind=0 的关联 branch。它只证明本地 pre-merge 阶段，GitHub PR/head/base 继续
由当前 HEAD 的 review/checks 证明，不给本地 constraints 增加网络依赖。Branch final token 改为
`merged/deleted/archived(<原因>)`，worktree token 改为缺省/`待最终收口`、`removed`、
`retained(<原因>)`，并要求双向 inventory 一致。新设计 target hash 为
`0d8d9677e036e4420f7fd89746884b3b1c7f2b3677c415fec7d5b6efeb096604`。

## 13. Formal 对抗评审 Round 8：一方 FAIL

**Target hash**：`0d8d9677e036e4420f7fd89746884b3b1c7f2b3677c415fec7d5b6efeb096604`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T13:04:00Z | PASS | none；路径、预算与 pending 反例完整 |
| Confucius / 兼容安全 | 2026-07-15T13:05:00Z | FAIL | merged 可在 branch missing 时假绿；final worktree 可未决；bare archived token 冲突 |

处置：Round 8 verdict 全部随 target 改动作废。Formal 现要求 `merged` 有且仅有一个关联 branch
且 ahead=0，`deleted` 才允许 branch 不存在，archive 必须唯一、kind=archive 且带非空原因；
final/close 下唯一 worktree 必须 `retained(<原因>)`，无 worktree 必须 `removed`，缺省、未决或多个
均阻断。Tasks 的 archive token 已统一。新设计 target hash 为
`90c84aef02c4b6d1f59a9919ec3b30a34e4b9157f775c15ab3fe06f41ed3d1c7`。

## 14. Formal 对抗评审 Round 9：写码前双 PASS

**Target hash**：`90c84aef02c4b6d1f59a9919ec3b30a34e4b9157f775c15ab3fe06f41ed3d1c7`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T13:13:00Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T13:13:00Z | PASS | none |

双方独立复算 target 与三文件 hash 一致。Round 6～8 的自由文本、owner、路径/预算、pending
missing/multiple/current/worktree/ahead/behind、merged missing、archive reason 与 final worktree 未决
问题全部关闭。只授权按 15 路径与 80/180/260 新增行预算进入 GAP-12 TDD；candidate/T61A 仍未授权。

## 15. GAP-12 TDD 与全量回归

- 冻结 target 未变化：spec=`7f96fd8b...36c`、plan=`889a41b2...b5d`、tasks=`d5d4398b...563a`，
  composite=`90c84aef02c4b6d1f59a9919ec3b30a34e4b9157f775c15ab3fe06f41ed3d1c7`。
- RED：`uv run pytest -q tests/unit/test_workitem_traceability.py` → `26 failed, 8 passed`；
  失败均为 final-policy 参数尚未实现。
- GREEN：同一单元文件 → `34 passed`；六个调用面定向回归 → `360 passed`。
- 全量：`uv run pytest -q` → `3212 passed, 3 skipped in 482.35s (0:08:02)`。
- 静态/治理：Ruff PASS、`git diff --check` PASS；WI204 branch-check `ok=true`；
  `uv run ai-sdlc verify constraints --json` → blockers=0、advisories=0。
- 新增非空手写 LOC：runtime/scaffold/rule/template=`75/80`，tests=`171/180`，
  total=`246/260`；删除行未抵扣新增预算。
- 实现边界：只改冻结的 15 路径；未新增模块、schema、网络 gate 或 T61A/candidate 产品代码。
- 关联 branch/worktree disposition 计划：`merge-pending`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`retained(PR #128 dual code review)`

## 16. Program Truth 历史兼容回归与修复

- 发现：首次 live `program truth audit` 把 19 个历史 `close_check_refs` 判 blocked；代表性 WI095
  使用旧 `retained` token，direct close 正确 fail closed，但 Program Truth 不应把当前本地 branch
  inventory 反向写成历史发布证据失效。
- 根因：Program Truth 既有 normalizer 只过滤 `BLOCKER: branch lifecycle ...` 瞬态 blocker；
  GAP-12 新消息遗漏该稳定分类前缀，导致本应被过滤的 lifecycle blocker 泄漏到持久 truth。
- 修复：仅恢复所有 lifecycle blocker 的既有分类前缀；active branch-check、constraints 与 close
  仍收到相同 blocker，未知 token 仍 fail closed，pending 仍不能满足 close。
- 回归：traceability + Program Truth ephemeral contract → `35 passed`；代表性 WI095 direct close
  `ok=false`，normalized historical evidence `ok=true` 且 blockers=[]。
- 实时复验：`program truth audit` → `state=ready`、`snapshot=fresh`、两项 capability audit=ready、
  source inventory 1076/1076、close 204/204。
- 更新预算：runtime/scaffold/rule/template=`75/80`，tests=`172/180`，total=`247/260`。

## 17. Formal 对抗评审 Round 10 触发

兼容安全 reviewer 指出：稳定 lifecycle namespace 是 Program Truth 历史证据兼容合同，且对应的
`tests/unit/test_program_service.py` 不在 Round 9 的 15 路径白名单。按 fail-closed 规则，Round 9
设计 PASS 作废。Formal 已扩为 16 路径，只允许在既有 ephemeral drift 测试新增≤8 个非空行；
冻结 direct raw-block / historical normalized-pass / non-lifecycle blocker 保留合同，并把 caller policy
参数固定为 private `_require_final_branch_disposition`。未授权修改 `program_service.py`、兼容旧 token、
批量改历史日志或新增 legacy mode。

首次声明错误使用固定 spec→plan→tasks 顺序；formal 算法要求完整 hash/path 行按字节序排序。修正后的
**待审 target hash**：`95f0db6f833344a56fb94c4f8affdc96e2d2b8e07a2f68c0e68b304a6aa2828d`

- spec=`47bbbafe547a2724ae2609895d676515f7cfcb6dc1c996676642c494e1f6eddd`
- plan=`f3fa9fe5ee4b533415214fa83b317852fb852649afbbae4d2efcde8525a0418d`
- tasks=`e0568cb64892f469f4b66ef73308b1105ca0584f077d2d98f87571e58f5b465b`

代码继续前必须由 Pascal 与 Confucius 对该同一 target 独立复算并共同 PASS。

## 18. Formal 对抗评审 Round 10：双 PASS

**冻结 target hash**：`95f0db6f833344a56fb94c4f8affdc96e2d2b8e07a2f68c0e68b304a6aa2828d`

| Reviewer | UTC | Verdict | Findings |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T14:01:02Z | PASS | none |
| Confucius / 兼容安全 | 2026-07-15T14:01:02Z | PASS | none |

两位 reviewer 独立复算三文件 hash 与 byte-sorted composite 一致；Round 10 只授权参数私有化及
ProgramService 既有 ephemeral drift 测试≤8 行增量。代码树变化后仍需同一 HEAD 双 code PASS。

## 19. Round 10 授权实现与最终验证

- caller policy 参数已机械改名为 private `_require_final_branch_disposition`；未改变判断分支。
- `test_program_service.py` 仅在既有 ephemeral drift 测试新增 `7/8` 个非空行：覆盖三类 lifecycle
  blocker、`branch_lifecycle` check 过滤，以及 non-lifecycle blocker 继续阻断。
- 定向：六调用面 + Program Truth compatibility → `361 passed in 51.86s`；Ruff PASS。
- 最终全量：`3212 passed, 3 skipped in 489.63s (0:08:09)`。
- 最终治理：branch-check pending=`ok`；verify constraints 无 BLOCKER；Program Truth
  `ready/fresh`、capabilities ready、1076/1076、close 204/204；program validate PASS；
  plan-check drift=NO；`git diff --check` PASS。
- 最终新增非空手写 LOC：runtime/scaffold/rule/template=`79/80`，tests=`171/180`，
  total=`250/260`；路径白名单无越界。
