# 任务执行日志：Workitem 只读命令 Adapter 副作用隔离

**功能编号**：`214-workitem-readonly-adapter-side-effect`  
**创建日期**：2026-07-19  
**当前状态**：formal authoring；产品代码未修改

## 1. 固定归档规则

- 每批开始前预读宪章、WI196、WI213 与 WI214 当前 formal。
- 每批记录 identity、范围、命令、结果、finding disposition、回退和下一步。
- 产品实现必须在 formal fresh-main 后的 dev branch，以测试 RED 开始。
- 任一受审文件变化使 Pascal/Confucius 同轮 verdict 同时失效，不拼接不同身份结论。
- 提交只包含一个逻辑批次；未来 hash 不预写，实际发生后追加。

## 2. Batch 2026-07-19-001：WI214 初始化与非范围 adapter 恢复

### 2.1 基线与命令

- base：`origin/main@d5ad7616f7f39f68365d6d39f8701a86c1f599e7`
- worktree：`.worktrees/214-workitem-readonly-adapter-side-effect`
- branch：`feature/214-workitem-readonly-adapter-side-effect-docs`
- 初始化：`uv run --python 3.11 ai-sdlc workitem init --wi-id 214-workitem-readonly-adapter-side-effect
  --title "Workitem Read-only Adapter Side Effect" --input "独立修复 GAP-15：仅隔离 workitem
  plan-check、guard、close-check、branch-check、truth-check 五个只读命令及其 help/invalid 路径的隐式
  adapter refresh，保持输出、退出码和 clean-tree；完整保留 init/link 在 valid、missing option、dirty、
  no-project、no-checkpoint、hook exception 下的既有写入时序。禁止修改 ProgramService/T66、adapter
  算法、全局 classifier、依赖或版本。" --related-plan
  specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md --related-doc
  specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md --related-doc
  specs/213-programservice-bounded-stage-reduction/development-summary.md`

### 2.2 结果

- CLI 创建 canonical 四件套、project sequence `214→215` 与 manifest entry。
- 初始化消费既有写路径并把 Cursor adapter 从 base SHA `d5f04acf...0b6a` 刷新为
  `02d9656d...e134`。该文件不是 WI214 formal scope，已恢复为 base bytes。
- 恢复后 `git diff --exit-code origin/main -- .cursor/rules/ai-sdlc.mdc` 为 0；最终 SHA=
  `d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`。
- root worktree 的用户未提交内容未读取、未复制、未修改。
- 删除注释原因：`.ai-sdlc/state/codex-handoff.md` 的原 `## Local PR Review` 是已归档到 WI213 execution/summary 的上一工作项瞬时状态；切换 WI214 时由本日志与新双评审任务替代，未删除源码注释或历史证据。

### 2.3 边界

- 本批只写 formal/state/manifest；`src/**`、`tests/**`、workflow、provider、依赖、版本均未修改。
- `workitem init` 的 refresh 是既有且受保留的 valid 行为；本 WI 只移除五个 read-only 路径的隐式消费。

## 3. Batch 2026-07-19-002：根因与兼容矩阵冻结

### 3.1 源码事实

- `src/ai_sdlc/cli/main.py` 在 top-level `workitem` 时只把 `run_ide_adapter_if_initialized` 注入 context meta。
- `src/ai_sdlc/cli/workitem_cmd.py::_workitem_before_command` 当前跳过 `None/init`，其余子命令均在
  handler 前执行 hook。
- `workitem_init` 在 root、ID、docs branch 与 clean-tree preflight 后显式执行 hook。
- `workitem_link` 无显式 hook，依赖子应用 callback；handler 内依次执行 option、root、checkpoint、save。

### 3.2 测试库存

- `test_cli_workitem_init.py` 已覆盖 valid、missing title、dirty/wrong branch、duplicate 与部分 adapter 时序；
  其中旧 `non_init` 测试用 `plan-check` 期待 hook 1 次，正是待转为 RED 的错误合同。
- `test_cli_workitem_link.py` 已有 valid、missing option、checkpoint fixture，但 autouse no-op hook 掩盖了调用时序。
- 五个 read-only handler 各有领域 integration tests；WI214 只补分发/bytes/output 证明，不复制业务矩阵。
- 使用 patch 的 Typer 控制流探针确认：五个 read-only 的 help/invalid 会识别子命令并进入当前 callback；
  `link` help/missing 当前消费 hook，`init` help/missing 不消费；未知 subcommand 不消费。

### 3.3 冻结结论

- 最小实现是让一个既有 callback 仅在 `invoked_subcommand == "link"` 时继续；不建立命令名单、
  classifier、registry 或 decorator。
- 15 格只读矩阵的唯一批准差异是 hook `1→0` 及其 receipt/write 消失。
- `init/link` 适用行为全部以 zero-delta 回归保护；`init no-checkpoint` 明确 N/A，不制造伪覆盖。
- 尚未修改产品或测试；必须先完成 formal 双 Agent review 与 mainline/fresh-main。

## 4. 当前评审与执行状态

- T11～T13：completed。
- T14 formal 双 Agent 对抗评审：pending。
- T15 formal PR/fresh-main：pending。
- T21～T33 implementation/closure：pending。
- GAP-15/T58、T66、GAP-03、WI196、RC-08、release：全部未完成。

## 5. 下一步

1. 最小更新 parent WI196 的 T58 状态为 WI214 formal active，并冻结 parent+child formal-six。
2. 提交 clean formal identity；Pascal/Confucius 分别从 LEAN 与 SAFETY 维度独立评审。
3. 对成立 finding 做最小修订，重算 identity并从零复审，直到同 identity 双 PASS0。
4. 仅在 formal PR/Codex/checks/merge/fresh-main 后进入 dev TDD。

## 6. 提交与 disposition

- 已完成 git 提交：否（本批提交须同时包含 formal/state/manifest/parent 最小对账）。
- branch：`merge-pending`
- worktree：`retained(formal authoring)`
