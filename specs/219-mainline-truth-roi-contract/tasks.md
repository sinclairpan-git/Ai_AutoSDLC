# 任务分解：主线真值复位与轻量 ROI 合同

**编号**：`219-mainline-truth-roi-contract`
**来源**：`spec.md`
**阶段**：formal design review

## Batch 1：Formal 规格

- [x] **T11 建立 origin/main 隔离基线**
  - 验收：worktree HEAD 精确等于 `origin/main@76252746`；状态/handoff/checkpoint targeted baseline 全绿。
  - 证据：`63 passed in 38.46s`；`verify constraints: no BLOCKERs`。

- [x] **T12 复现当前真值与 continuity 漂移**
  - 依赖：T11
  - 验收：记录 WI204 `branch_only_implemented`、`BLOCK_CODE_PREPARE_TASKS`、陈旧 PR 173 handoff；同时
    证明 Program Truth=`fresh`、release targets=`ready`。
  - 补充证据：link WI219 后 canonical resolver 返回 WI219，但 readiness binding、active dir 和 execute
    authorization 仍返回 WI204，根因限定为 linked-first 消费分叉。

- [x] **T13 冻结 formal 规格与 scope/ROI 停止条件**
  - 依赖：T12
  - 验收：`spec.md` 无 TODO/TBD/placeholder；方案、范围、功能需求、成功标准和停止条件唯一明确；Track A
    只允许一个共享纯解析语义、三个既有消费方和定向测试，不修改 writer/schema/Runner/ProgramService。
  - Formal inventory：WI219 新增 5 个已映射 layer，close 暂为 218/217；只机械更新 root manifest tuple，
    保留 missing=1，不放宽任何完整性断言。

- [x] **T14 首轮独立对抗合议**
  - 依赖：T13
  - 结论：`REJECT`；有效阻断为 formal truth 分类、status 消费面遗漏、committed handoff 陈旧、adapter
    allowlist 漏洞与双模板语义验收不足。optional-link Critical 经 WI198 证据复核后撤回。

- [x] **T15 Formal 整改与同候选验证**
  - 依赖：T14
  - 验收：规格冻结 behind-only base、formal-control classification、完整 consumer matrix、semantic-set test；
    删除 adapter escape hatch；canonical/scoped handoff 不再记录已提交前状态。
  - 证据：formal required/forbidden 自审 PASS；targeted suite `79 passed`；constraints 无 BLOCKER；Ruff PASS；
    post-commit continuity refresh 由 T16 候选 identity 提交完成。

- [ ] **T16 原三席 round 2 同 identity 复审**
  - 依赖：T15
  - 验收：三个 reviewer 审同一 base/head；任一有效 Critical/Important 未关闭则不批准且不进入第三轮。

- [ ] **T17 用户审阅并批准 formal 规格**
  - 依赖：T16
  - 验收：合议通过后用户明确批准；批准前没有产品或特性测试实现任务。

## 后续批次

尚未授权。T17 完成后通过正式 planning 流程生成，不得预填或推断实现任务。
