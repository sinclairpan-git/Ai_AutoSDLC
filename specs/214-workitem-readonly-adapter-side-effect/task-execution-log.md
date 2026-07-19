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

- 已完成 git 提交：是；authoring commit=`d3acfedea507a23bb30d53d84906c11a0c03c41a`。
- branch：`merge-pending`
- worktree：`retained(formal authoring)`

## 7. Batch 2026-07-19-003：formal 对抗评审 Round 1 双 FAIL

### 7.1 受审身份

- HEAD=`1603d4b1eaa345373fac70c5a9dc207d30f7b3cf`
- tree=`2d109ccd74703dfab5315ae702ada1663a626c71`
- parent+child formal-six=`aa24fb807312573246bbafbe5fc5619b0c041dda6613305811b966de08622f63`
- Pascal/LEAN=`FAIL`、actionable findings=1；Confucius/SAFETY=`FAIL`、actionable findings=4。
- 两人独立核对同一 committed+clean identity，审查期间零编辑、零真实 adapter 调用。

### 7.2 Findings 与处置

1. Pascal P2 成立：child 未冻结具体 targeted 命令和测试布局。处置为唯一新增参数化
   `test_cli_workitem_adapter_dispatch.py`，init/link 只改既有测试文件，并在 plan/tasks 写 V1～V6 精确命令。
2. Confucius P1 成立：implementation fresh-main 后没有合法 PR 承载 closure。新增独立 lifecycle
   reconciliation branch/PR、双审/Codex/checks/fresh-main；回退顺序先重开 truth 再 revert implementation。
3. Confucius P1 成立：旧顺序在双审后才同步 truth/handoff。修订为先 terminal truth/handoff/gates，再冻结
   committed+clean identity 双审；任何后续内容变化都重跑 gate/truth 并让双方从零复审。
4. Confucius P1 成立：hook exception 未区分 project-config `PermissionError` 的 warning+continue 与其他
   exception propagation。新增 production `apply_adapter` 先写、`_persist_config` 失败的 partial-write/输出/
   continuation fixture；其他异常保留原类型/消息与前缀写入，不引入事务化。
5. Confucius P2 成立：sentinel 不能替代 parent 要求的 real-hook byte evidence。五个 normal 增加
   `@pytest.mark.real_ide_hook` 的 byte-identical 临时根、guarded SHA/status/stdout/stderr/exit exact 证明。

### 7.3 结论

- 五项全部接受并做最小合同修订；没有扩到 adapter 算法、root callback、handler、ProgramService/T66、
  依赖、workflow 或版本。
- Round 1 两份 verdict 与 identity 全部退役；修订提交后必须由 Pascal/Confucius 对新身份从零复审。

## 8. Batch 2026-07-19-004：formal 对抗评审 Round 2 双 FAIL

### 8.1 受审身份

- HEAD=`144c8c5080a90f8819639204be0ab1b12a4acd1c`
- tree=`37de73e387fcd55fd19df20909eba04c2500ad1b`
- parent+child formal-six=`53d85b2a46b54deb0b05f53789c2517a17d879ec015f0829fee898ab174b246c`
- Pascal/LEAN=`FAIL`、findings=2；Confucius/SAFETY=`FAIL`、findings=1；同 identity、clean、只读。

### 8.2 Findings 与处置

1. Confucius P2 成立：tasks 完成定义与 FR-007 仍残留两阶段措辞，可能让 lifecycle 修订逃逸重审；
   改为 formal/implementation/lifecycle 三阶段均 mainline/fresh-main且同 identity 双 PASS0，并把 T41
   明确为登记 implementation receipt。
2. Pascal P2 成立：15 格已覆盖同一 callback 分支，再跑五个 production/no-op 双项目是重复乘积；
   real-hook 收敛为原始 `plan-check normal` 一组代表性 A/B，其他四个 normal 由 sentinel 覆盖。
3. Pascal P2 成立：在 init/link 各复制 production partial-write fixture 越过分发边界；共享
   `test_cli_hooks.py` 只补一例 partial-write，init/link 只注入 return/raise outcome 验证继续或中断顺序。

### 8.3 结论

- Round 1 的五项 finding 已被双方确认实质闭合；Round 2 三项新增 finding 全部接受并继续减去重复证据。
- 精确 targeted 命令加入 `tests/unit/test_cli_hooks.py`；仍只有一个新增测试文件，不新增测试 DSL/fixture framework。
- Formal-six 已变化，Round 2 verdict 全部退役；提交后必须对新 identity 进行 Round 3 双审。
