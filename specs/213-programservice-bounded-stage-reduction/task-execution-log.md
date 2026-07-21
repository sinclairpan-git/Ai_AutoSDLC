# 任务执行日志：ProgramService 九阶段精益减重正式合同

**功能编号**：`213-programservice-bounded-stage-reduction`
**创建日期**：2026-07-19
**状态**：formal authoring；未授权产品 execute

## 1. 归档规则

- 本文件只记录已经发生且可复算的事实；future merge/check/release 不写占位哈希。
- 每个 meaningful batch 追加范围、身份、命令、结果、风险和下一步。
- Formal-six 变化使两个 reviewer verdict 同时失效；不同 round 不拼接。
- WI213 关闭只表示 formal receipt 完成，不表示 candidate/T66/GAP-03/WI196/RC-08/release 完成。

## 2. Batch 2026-07-19-001：隔离 formal 初始化

### 2.1 身份

- Base/HEAD：`e184c8e27818aa7950fcc64dbb10fa7a65888f8c`
- Branch：`feature/213-programservice-bounded-stage-reduction-docs`
- Worktree：`.worktrees/213-programservice-bounded-stage-reduction-formal`
- Python：3.11.15
- Root 工作树的既有 dirty changes 未进入本 worktree。

### 2.2 执行

```text
uv run --python 3.11 ai-sdlc workitem init \
  --wi-id 213-programservice-bounded-stage-reduction \
  --title "ProgramService Bounded Stage Reduction" \
  --input "在 current main 上冻结 T66 九阶段 ProgramService 领域切片的实测基线、兼容合同、精益预算、T61A/B、candidate shadow、预发布稳定验证与独立 legacy deletion；formal 合入前禁止产品实现。" \
  --related-plan specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md \
  --related-doc specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md \
  --related-doc specs/212-reduction-candidate-selection/development-summary.md
```

结果：canonical `spec.md/plan.md/tasks.md/task-execution-log.md` 创建；project-state
`next_work_item_seq 213→214`；manifest 映射创建。CLI 同时刷新 `.cursor/rules/ai-sdlc.mdc`，该变更不在
formal 白名单且写入了与仓库 PowerShell 约定冲突的 host shell 文本，已用 base bytes 精确恢复；
`git diff --exit-code -- .cursor/rules/ai-sdlc.mdc` 通过。未运行 truth sync，避免在未冻结 source identity
上制造 stale snapshot。

## 3. Batch 2026-07-19-002：current-main 实测

### 3.1 AST/LOC

Python3.11 AST recipe：physical=`end_lineno-lineno+1`；executable=首个非 docstring statement 到 end；
branch proxy=base1 + branch/comprehension/bool-op/try/match。

```text
family              count  physical  executable  header  branch
request builder         9       961         898      63     112
executor                9      1589        1517      72     148
artifact writer         9       378         288      90      72
payload builder         9       431         359      72      18
payload loader          9       279         243      36      36
total                  45      3638        3305     333     386
public                 27      2928        2703     225     332
private                18       710         602     108      54
```

- `program_service.py`=17,474；`program_cmd.py`=7,057；`src/ai_sdlc/**/*.py`=217 files/107,321 LOC。
- 18 private payload methods 各有一个 service 内调用；`src/**` 外部引用=0。
- AST Call 聚合：request=`18 service + 9 other src + 66 tests`；execute=`9+9+79`；writer=`0+9+27`；
  private build/load 各=`9+0+0`。
- 现有选中测试 physical：unit 106/3,835，CLI 59/2,482，合计165/6,317。

### 3.2 现有行为测试

```text
AI_SDLC_DISABLE_UPDATE_CHECK=1 .venv/bin/python -m pytest -p no:cacheprovider \
  tests/unit/test_program_service.py tests/integration/test_cli_program.py \
  -k '(cross_spec_writeback or guarded_registry or broader_governance or final_governance or \
       writeback_persistence or persisted_write_proof or final_proof_publication or \
       final_proof_closure or final_proof_archive) and not thread_archive and not project_cleanup' -q
```

结果：`165 passed, 474 deselected in 2.77s`。测试后 Git 状态没有新增产品、测试、adapter 或 runtime diff。
该结果只证明 legacy current-main 健康，不是 T61A/T61B 或 candidate PASS。

## 4. Batch 2026-07-19-003：formal 合同 authoring

### 4.1 已冻结

- 目标严格限于九 stage/45 methods；DTO、CLI、renderer、thread archive/project cleanup 排除。
- 一个 private module、显式 typed/path binding、public thin facade；无 dependency/public abstraction。
- T61A 在产品编码前，且需要 LEAN/SAFETY 对同 proof identity 双 GO；candidate/stability/deletion 顺序
  不可合并，RC-08 前不发布。
- 禁止反射、stage-name `if/match`、循环 import、DSL、DTO 搬迁、公共开关和未来扩展点。

### 4.2 当前状态与风险

- Child `spec/plan/tasks` 已形成完整草案；parent `spec/plan/tasks` 已完成 T24 最小 writeback，只登记
  WI213 formal active、当前预算和未授权边界，没有写入 future receipt。
- 当前内容尚未 committed，也没有 review identity；任何 reviewer PASS 均尚不存在。
- 一个只读 feasibility reviewer 正在独立核验格式化后的 binding/facade 物理 LOC；其结果需先 disposition，
  再冻结 formal-six。
- `development-summary.md` 尚未创建，符合 formal 未完成状态；truth sync 尚未执行。

### 4.3 精确下一步

1. 收齐 feasibility 结论；按代码事实接受最小修正或 RC-09 No-Go，不为保留 Go 放宽结构。
2. 更新 root/scoped handoff，并运行文档/预算/未决标记/scope 初检。
3. 提交 clean authoring identity。
4. Pascal 与 Confucius 对同一 formal-six 从零对抗评审；循环至双 PASS0。

## 5. Batch 2026-07-19-004：feasibility 反证与预算纠正

### 5.1 初始结论及撤回

只读 reviewer 首先确认：45 methods 与165-test 基线无漂移；八个 downstream request/executor 各只有一个
归一化 AST shape，九 writers/payload builders/loaders 各一个 shape，cross-spec request/execute 是唯一
特殊 strategy；private descriptor + factory injection 的单模块方向 `GO`。其初始建议认为 glue≤5。

根线程按 `pyproject.toml` 的 Ruff line-length=88 提出反证：facade 若显式传 Request/Step/Result factory 和
path，formatter 会展开为多行；若改为短 binding，则九组 binding 的 physical LOC 必须计费。Reviewer 复核后
明确撤回 glue≤5，也否定本 formal 早期 glue≤15。

### 5.2 Ruff 物理下限

- Terminal facade：build 9×1 + execute 9×1 + write 9×3=`45`。
- Candidate selector+route addition：build 9×2 + execute 9×2 + write 9×4=`72`。
- 每个显式 binding 包含 definition、Request/Step/Result factory、source/output path 和 step-dir/cross
  filename；九组至少81行，连同 import/selector/分隔机械下限约83～85，hard cap=`90`。
- Reviewer 对 private module 的分区估算为348行；hard cap 收紧为360，保留12行余量。

### 5.3 冻结新预算

```text
shadow product = 360 + 72 + 90 = 522 <= 545          buffer 23
terminal        = 225 + 45 + 90 + 360 = 720
net delete      = 3638 - 720 = 2918
RC-06 cap       = floor(2918 * 25%) = 729
product+proof   = 522 + 190 = 712 <= 729              buffer 17
route total     = historical 184 + 712 = 896 <= 1500
ProgramService reduction = 3638 - (225 + 45 + 90) = 3278
ProgramService projected = 17474 - 3278 = 14196
```

WI212 的 691/2947 和本 formal 早期 701/2937 都退役，只作审计历史；不能拼入后续预算。Reviewer 对
新数学与结构给出 final `GO`：module alias import1行、九组 binding81行、一次性 tools config8行，合计
glue90；selector 计入 private module。唯一开放风险是 module 仅有12行余量；module>360、strict mypy/
Ruff 迫使超限或 RC-06 buffer 被击穿时必须立即 `NO-GO`，不得再次放宽预算。

## 6. Batch 2026-07-19-005：GAP-15 只读入口副作用登记

### 6.1 A/B 证据

在 current base `e184c8e2`、已恢复 adapter base bytes 的同一 worktree 执行：

```text
before cursor sha256 = d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a
uv run --python 3.11 ai-sdlc program validate
after program validate = d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a

uv run --python 3.11 ai-sdlc workitem plan-check \
  --wi specs/213-programservice-bounded-stage-reduction --json
stdout includes = IDE adapter (cursor): installed 1 file(s)
after plan-check = 02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134
tracked diff = .cursor/rules/ai-sdlc.mdc +18/-6
```

`plan-check` 自身返回 success、`drift=false`，但违反其 help/handler 的 read-only 合同。代码定位：
`main.py` 为 workitem 注入 hook；`workitem_cmd.py::_workitem_before_command` 对除 `None/init` 外所有
subcommand 调 `_run_workitem_adapter`，因此 handler 之前已经写盘。`program validate` bytes 稳定，证明这是
新的 workitem 分发缺陷，不是已关闭 GAP-12 的 program 路径回归。

### 6.2 处置

- 已将 `.cursor/rules/ai-sdlc.mdc` 再次恢复为 base bytes；formal scope 中 adapter diff=0。
- Parent WI196 登记 GAP-15/T58；child formal 冻结“WI213 fresh-main → T58 fresh-main → T66 T61A”。
- WI213 不修改 source/test logic；T58 必须独立 WI/branch/PR、TDD、双 Agent、CI/Codex/fresh-main。
- 已完成的 `plan-check` success evidence 保留；在 T58 关闭前不重复运行该命令污染 formal worktree。

## 7. Batch 2026-07-19-006：formal Round 1 双 FAIL 与最小修订

### 7.1 受审身份

- HEAD=`0ab64e9180a979f5711b1d3423e06c85f82fc630`
- tree=`53ac0a441b9b91d78f6490b71af8ba848f1be92a`
- formal-six combined SHA-256=`7c37b888c8b8eab82d641ebe83f3588cf5ac7c1084d9db9a0578eca9edf86b96`
- 审查前后工作树 clean；两位 reviewer 均只读且身份匹配。

### 7.2 Findings 与 disposition

- Pascal/LEAN：2 findings，`FAIL`。成立项为 parent canonical 示例仍指 WI211，以及 child SC-005 与
  GAP-15 唯一下一步矛盾。
- Confucius/SAFETY：7 findings，`FAIL`。除 canonical 重合项外，还包括 Python callable/DTO surface 未
  可执行证明、late-bound `self` dispatch 未冻结、deletion merge 前无法真实 revert 最终 mainline、T61A
  NO-GO 删除唯一证据、offline 仅覆盖运行未覆盖 no-index 安装、T58 未冻结 `init/link` 负路径时序。
- 九条 reviewer 报告合并为八个唯一 finding，全部由源码/测试事实证实，未拒绝任何意见。

### 7.3 最小修订

- Canonical PowerShell 示例机械切到 WI213；SC-005 只授权 T58，T58 fresh-main 后才授权 T66 WI。
- T61A/B 增加版本化 `inspect/dataclasses` Python-surface manifest 与 execute/writer late-bound dispatch 矩阵；
  不新增公共抽象、不放宽 proof≤190，超限仍 No-Go。
- T61A NO-GO 先固化 commit/tree/raw hash/verdict/closure receipt，不删除唯一证据。
- Candidate/deletion 安装使用受控 wheelhouse、断网 `--no-index --find-links`，覆盖 sdist build isolation。
- Deletion current head 先审查/CI/merge，再对精确 merge commit 在一次性隔离 worktree 实际 revert；随后
  回 deletion fresh-main，双态验证后才关闭 T66。
- T58 矩阵补五只读命令的 help/invalid-input，并冻结 `init/link` valid/负路径 hook 次数、时序、输出、
  退出码与写入；任一行为变化必须 explicit expected delta。

本轮任一 formal-six 变化已使 Round 1 两份 verdict 同时失效；修订提交后必须由双方对新 identity 从零复审。

## 8. Batch 2026-07-19-007：formal Round 2 split verdict 与 truthiness 修订

### 8.1 受审身份与结论

- HEAD=`fd421ea6f1f7b50bd7a42243b72640bff8c7bf09`
- tree=`1fabfec635d2eb88eed28d7d3f2ace84d1948c78`
- formal-six combined SHA-256=`3db6ef5816ec21daa8281e784d109a7bdfbbdc4ff13c249a3fdd7fb1ec9efdd5`
- Pascal/LEAN：`PASS`、findings=0；Confucius/SAFETY：`FAIL`、findings=2。两者 identity 匹配且只读。
- 内容变化使 Pascal PASS 与 Confucius FAIL 同时失效；不得拼接 Pascal Round 2 与未来安全 verdict。

### 8.2 新 findings 与处置

1. Legacy 九组 writer/executor 使用 `value or fallback`，先前“显式参数绕过”错误忽略 falsey object；同时
   宽泛 `generated_at` normalizer 会吞掉 `is None` 回归。修订为 `None/truthy/falsey` request/result 和
   `generated_at=None/""/固定 truthy` clock-spy 矩阵；只允许规范化实证来自默认时钟的值，caller truthy
   时间逐字节比较。
2. `__post_init__ identity` 不可跨进程。修订为 presence/module/qualname/signature/source SHA-256/行为
   digest；field default/default_factory 使用 MISSING/typed literal/callable canonical 编码；source 不可读
   fail-closed，禁止 `id()` 或含地址 `repr()`。

两项均成立并完成最小合同修正；不新增公共抽象、不放宽 proof≤190，Round 3 必须同 identity 双 PASS0。

## 9. Batch 2026-07-19-008：formal Round 3 同一 fingerprint finding

- 受审 identity：HEAD=`178e805be9cda71e066387db6a77f02086a368e1`；tree=
  `52183d315cfc2d5da4d6ba9ac38074b977db26f6`；formal-six=
  `614c5158c91fa40904219146c7a10e8562a3de1192e8ae01a167fad0b5ebc388`；clean、只读。
- Pascal/LEAN 与 Confucius/SAFETY 均 `FAIL`、各 findings=1，意见统一：统一 source hash 会让必须改 body 的
  public facade 永远不通过，且 `inspect.getsource(builtins.list/dict)` 必然失败，使 legacy T61A 直接 No-Go。
- 成立并最小修订为三类 schema：public API 只比 surface+behavior；DTO `__post_init__` 因禁止修改而比
  source-or-normalized-code+behavior；当前内建 factory 仅 allowlist `builtins.list/dict` stable tag+behavior。
  未知 callable 才 fail-closed，仍禁止 identity/address repr，proof≤190 不变。
- Formal-six 已变化，Round 3 两个 FAIL 只保留为历史；Round 4 必须对新 committed+clean identity 从零双审。

## 10. Batch 2026-07-19-009：formal Round 4 split verdict 与 YAGNI 收敛

- 受审 identity：HEAD=`7b75b93cbc6f6eceff3eb6062d22763346b54ce6`；tree=
  `1076c1db876a30468514358173dcfd04f6749487`；formal-six=
  `db44ca60a1b4d0a96106abfa286ff93a8d3f2a08b3421c2396184c361074a816`；clean、只读。
- Confucius/SAFETY=`PASS`、findings=0；Pascal/LEAN=`FAIL`、findings=1。内容变化使两 verdict 同时失效。
- Pascal finding 成立：目标 DTO hook 均为可读取的普通 Python 源码，wheel/sdist 均包含 source；
  `normalized-code` fallback 为不存在的 bytecode-only 场景引入跨 Python 3.11/3.12 code-object canonicalizer，
  挤压 proof≤190 且增加假差异。
- 最小修订：DTO hook 只比较 source SHA-256+behavior，source unreadable 直接 fail-closed；保留当前
  `builtins.list/dict` tag，不实现 bytecode/code-object fallback。Round 5 必须新 identity 双 PASS0。

## 11. Batch 2026-07-19-010：formal Round 5 authoring 双 PASS

- HEAD=`e00aea25bc9ddb5da475e22eb6f02ba820cec4c0`
- tree=`f17e24baf9747488a7a178d175bead33daf8db84`
- formal-six=`674407cf6ac8c2f726a3975dc6fffeac0cc88786bf50a19d0e1687d09684cf27`
- Pascal/LEAN：`PASS`、findings=0；Confucius/SAFETY：`PASS`、findings=0；worktree clean、双方只读。
- 双方确认 normalized-code 完全移除，public/DTO/builtin 三类 fingerprint、truthiness/clock、预算、
  rollback、offline、GAP-15 和发布边界均闭合。
- 随后创建 `development-summary.md` 并更新 T31～T41 状态，因此 Round 5 降为 authoring receipt；最终
  formal-six 变化后必须重新提交、同步 truth、跑门禁并在 T44 由双方对 current identity 再次 PASS0。

## 12. Batch 2026-07-19-011：formal mainline 与 fresh-main acceptance

- Codex 对旧头 `6c242f9c` 的成立 P2 促使 child/parent summary 区分已完成 terminal gates 与待交付
  lifecycle；Round 8 双方再指出 current-state/PR body 时序问题，均做最小修正。
- 最终 Round 9 reviewed HEAD/tree=`94acfdf424932d354bde33f2bd9a8a554fa63fb8`/
  `9d1c0f6915e31bf79d2d2fd768adc5a5ca8ffe05`，formal-six=
  `283b623babe7b98eb8d62acb79af2cea79e56d36941cb5269ad3ffbd5f61f099`；Pascal/LEAN 与
  Confucius/SAFETY 均 PASS、findings=0。
- Codex current-head provenance P2 声称 snapshot revision `a638be64` 不可达；本地
  `merge-base --is-ancestor` 与 GitHub commit/compare API 证明它是 `94acfdf4` 的直接父提交。两名 Agent
  独立一致 REJECT，无文件修改；两个 review thread 均 resolved。
- PR #158 required/compatibility checks=`13/13 success`，squash merge=`450d49885bba028ea7f4e9e3d0896c158a536862`；
  merge tree=`9d1c0f69` 与 reviewed tree 相同。
- Detached fresh-main `450d4988`、Python 3.14.3：targeted=`165 passed, 474 deselected in 4.15s`、manifest
  exact=`1 passed in 110.90s`，constraints/validate/truth=`ready/fresh 1121/1121`、unmapped/missing=`0/0`、
  scope/handoff parity/Cursor/clean 全绿；版本未变。
- T42～T45 完成；WI213 formal-only 关闭。本 lifecycle reconciliation fresh-main 后，唯一下一项才是
  独立 T58/GAP-15；T58 fresh-main 前不得进入 T66 T61A，且 GAP-03、WI196、RC-08 与
  发布继续 open。

## 13. Batch 2026-07-19-012：lifecycle 对抗复审 Round 1

- Review identity=`90b65eba`/tree `94399b8a`/formal-six=`fe6e04fb...ff32`。Pascal/LEAN 发现
  handoff 要求重复提交已提交 receipt；Confucius/SAFETY 发现 T58 在 lifecycle reconciliation
  交付前过早授权，以及 handoff current base/changed-files 滞后。
- 三项 finding 全部成立，只修正授权时序与 continuity 事实；产品、测试、预算、
  workflow、依赖与版本不变。旧 verdict 退役，修正后必须对新 identity 双 PASS0。

## 14. Batch 2026-07-19-013：lifecycle mainline 与 WI214 handoff

- 最终 lifecycle reviewed identity=`762a3fa52b52288bb5dbec8f6305d65349760064`、tree=
  `901dfa8f3267792362316bc962705abf77380316`、formal-six=
  `e51befd27416e0f75533e4b97548ef452fa0056033633487944491db4a949431`；Pascal/LEAN 与
  Confucius/SAFETY 均 PASS、findings=0。
- PR #159 的 Codex P2 错误声称 snapshot source `4f113788` 不可达；本地 ancestry、GitHub commit/
  compare API 与两名 reviewer 独立核验均证明实际链为 `4f113788 -> bd1a7084 -> 762a3fa5`，finding
  被一致拒绝并 resolved。Required checks 全绿，squash merge=`d5ad7616f7f39f68365d6d39f8701a86c1f599e7`。
- Detached fresh-main `d5ad7616`、tree=`901dfa8f`：constraints/validate/truth `ready/fresh 1121/1121`、
  targeted=`165 passed`、manifest exact=`1 passed`、scope/handoff parity/Cursor/clean 全绿。
- Lifecycle reconciliation 已关闭，正式授权从该 main 创建 T58/WI214；当前 WI214 formal active，
  其 implementation fresh-main 前仍不得进入 T66 T61A，版本发布仍禁止。

## 15. Batch 2026-07-19-014：WI214 下游准入措辞 superseding correction

- §14 末句把 T66 阻断只写到 WI214 implementation fresh-main，弱于 WI214 已冻结的三阶段关闭合同；
  该历史句保留但由本段取代。
- 当前唯一有效门禁为：WI214 formal、implementation、lifecycle reconciliation 均 mainline/fresh-main，
  且 lifecycle reconciliation fresh-main 明确关闭 GAP-15/T58 后，才可创建 T66 implementation WI并进入 T61A。
- 本修正只校准 current truth/continuity，不修改 WI213 已验收事实、产品、测试、预算、依赖或版本。

## 16. Batch 2026-07-19-015：WI214 implementation receipt 与 T66 准入恢复

- WI214 final implementation reviewed HEAD/tree=`75d60375`/`03b4a1ff`，Pascal/LEAN 与
  Confucius/SAFETY 同身份 PASS0；PR #162 22/22 checks，squash merge=`2845fedc`。
- Detached fresh-main tree 与 reviewed tree 相同；full=`3303 passed, 3 skipped`、targeted=`50 passed`、
  truth=`ready/fresh 1126/1126`，其余实现门禁全绿。
- 本独立 lifecycle reconciliation merge/fresh-main 后关闭 GAP-15/T58。唯一下一步是新建 T66
  implementation WI并先取得 T61A 双 readiness GO；T66/GAP-03/WI196/RC-08/release 仍保持 open。

## 17. Batch 2026-07-19-016：WI214 lifecycle delivery/receipt superseding boundary

- §16 的“lifecycle reconciliation merge/fresh-main 后关闭”由本段细化：delivery PR 始终保持 T58 active、
  T66 blocked；delivery detached fresh-main 后另建 main-derived closure receipt branch/PR。
- 只有 receipt 自身同身份双审、Codex/checks、merge/detached fresh-main 全绿，才关闭 GAP-15/T58并恢复
  T66 WI/T61A 准入。T66 产品、GAP-03、WI196、RC-08 与 release 仍保持 open。

## 18. Batch 2026-07-20-017：WI214 delivery mainline 与 closure receipt

- WI214 delivery final HEAD/tree=`1d99b798`/`3f6698d7` 同身份 LEAN/SAFETY PASS0；PR #163 exact-head
  10/10 checks 全绿并按用户授权采用本地 SDLC 双审替代继续等待远端 Codex 最终文字回执，squash
  merge=`60fe6d90`。
- Detached fresh-main tree 一致，constraints/validate/truth=`ready/fresh 1126/1126`、manifest exact、
  scope/parity/Cursor/clean 全绿。
- 本 closure receipt merge 关闭 GAP-15/T58，但 T66 仍 blocked；receipt detached fresh-main 通过后才允许
  创建 T66 implementation WI并执行 T61A 双 readiness。失败立即回退 receipt；不关闭 GAP-03/WI196/
  RC-08，不发布版本。

## 19. Batch 2026-07-21-018：下游 T66 实现 NO-GO

- WI216 记录本 formal 下游首次实现的确定结果：C2-safe records=`70f19275/2fdd9aaa`，完整自然账本
  `558/64` 对 legacy `495/63`，产品 `+443/-408`、proof净增285；该路线不是减重。
- 独立 no-DSL spike 产品=`6c945b40/6341bcb2`、records=`60dcc4f6/44420f6d`，第二阶段
  target=`1209/164` 对两阶段 legacy=`842/92`；LEAN/SAFETY 对产品及 records 均为
  `STOP_SPIKE_NO_GO/findings=0`。
- T66 本次 implementation=`cancelled_no_go`，C2/spike=`archived_not_merged`，运行时仍为 fresh-main
  legacy。WI213 formal receipt 保留为历史合同，但不授权继续旧 Phase 3；GAP-03/WI196/RC-08/release open。
