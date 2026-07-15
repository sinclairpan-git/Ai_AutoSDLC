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
- 首次治理验证如实阻断于 branch disposition 尚未登记；本批将当前 docs branch 明确登记为
  PR #128 的 merge carrier，合并后再复验 mainline ancestor truth。
- 关联 branch/worktree disposition 计划：`feature/204-program-finalization-command-family-reduction-candidate-docs` 作为 PR #128 merge carrier，合并后由 mainline truth 结算。
- 当前批次 branch disposition 状态：`PR merge carrier`
- 当前批次 worktree disposition 状态：`retained through PR #128`
