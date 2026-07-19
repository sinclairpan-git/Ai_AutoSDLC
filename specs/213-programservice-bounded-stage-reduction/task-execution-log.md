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
