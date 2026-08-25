# 任务执行日志：主线真值复位与轻量 ROI 合同

**功能编号**：`219-mainline-truth-roi-contract`
**创建日期**：2026-08-25
**状态**：formal design review

## Batch 2026-08-25-001 | T11-T13

### 变更范围

- 从当前远端 `origin/main@762527466119dde127d7488b73d5592e44afaaa6` 创建独立 worktree；
- 通过 `workitem init` 生成 canonical formal docs，并同步 Program Truth 映射；
- 只改写 WI219 formal 文档，未修改产品/测试实现。

### 基线命令与结果

- `uv run ai-sdlc handoff show`：成功，复现仍要求合并 PR 173 的陈旧 handoff；
- `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_handoff.py tests/unit/test_checkpoint_fr088.py tests/unit/test_handoff.py -q`：`63 passed in 38.46s`；
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`；
- `uv run ai-sdlc program truth sync --execute --yes`：完成 WI219 manifest 映射；
- `uv run ai-sdlc status --json`：复现 active WI204=`branch_only_implemented`、
  `BLOCK_CODE_PREPARE_TASKS`；Program Truth=`fresh`，release targets=`ready`。

### 决策

- 采用现有真值入口、定向 active binding 消费修正与模板提示方案；
- link WI219 后通过现场解析确认：checkpoint feature=WI204、linked=WI219、canonical active=WI219，但
  readiness binding/dir 与 execute active 均为 WI204；
- WI198 已冻结 linked-first 语义并明确拒绝 link 时改写历史 feature，因此根因是 readiness 与 execute
  authorization 各自直接读取 `checkpoint.feature`，不是 link 写入或 checkpoint schema 失效；
- 本 WI 允许一个无 I/O/持久化的共享 spec-dir helper，使 resume、readiness 与 execute 三个消费方复用同一
  active binding；不得扩展 writer、Runner、ProgramService、status schema 或状态机；
- 产品 30 LOC、测试 150 LOC 作为 re-review 信号，不作脱离风险的机械门禁；
- 用户批准 formal 规格前不进入实现。

### Formal inventory RED

- `tests/integration/test_repo_program_manifest.py` 在旧主线 tuple `1142/1142/0/0` 上稳定 RED；实际 WI219
  formal inventory 为 `1147/1147/0/1`，close layer 为 `218/217`；其余 78 项通过。
- 历史 WI217 formal 提交采用相同 missing close 语义；因此只更新两个精确 tuple，不改完整性、unmapped、
  capability 或 release 断言。

### 下一步

- 对 formal 文档执行 placeholder、矛盾、scope 和歧义自审；
- 提交当前 formal identity；
- 请求用户审阅 `spec.md`。
