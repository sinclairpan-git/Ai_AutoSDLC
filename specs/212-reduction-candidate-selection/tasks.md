# 任务分解：AI-SDLC 精益减重候选选择

**编号**：`212-reduction-candidate-selection`
**来源**：`spec.md + plan.md`
**分支类型**：docs-only formal；禁止产品 execute

## Batch 1：fresh-main 扫描

### T11 冻结身份与总体缺口

- **状态**：completed
- **范围**：main commit/tree、Python、产品 LOC、两个超大文件、truth/release 状态。
- **验收**：所有数字可复算；GAP-03～06、WI-196、RC-08、release 保持 open。
- **验证**：Git identity、`rg --files | wc`、`wc -l`、program truth audit。

### T12 扫描 T63/T64 重复族

- **状态**：completed
- **依赖**：T11
- **范围**：AST exact-body family、调用者、物理/非空 LOC、RC-06 预测；复核 Loop Store 既有 No-Go。
- **验收**：字段级 validator wrapper 不被误算为可直接删除；当前扫描的 T63 family 按合并
  product+proof 全部 RC-09 No-Go，不得以“低风险”或“小收益 Deferred”绕过 RC-06。
- **验证**：AST group recipe + `rg` 调用者 + 历史 T63/T64 receipt。

### T13 审计 T65 六个 baseline builder

- **状态**：completed
- **依赖**：T11
- **范围**：六个定义、真实消费者、动态字段、序列化/loader/资源打包/离线成本。
- **验收**：每项有 Go/No-Go/Deferred 与保守净收益；本 WI 不冒充 standalone T65 receipt。
- **验证**：AST LOC、consumer graph、exclude-default 数据化成本模型。

### T14 审计 T66/T67 结构候选

- **状态**：completed
- **依赖**：T11
- **范围**：T66 九 stage 45 methods；T67 current 九 handler 与 WI-203 baseline/204 No-Go。
- **验收**：T66 3,638/3,305 与 45-symbol 集合精确；T67 九函数逐字一致且旧 claim=0。
- **验证**：AST recipe、Git baseline exact compare、outside-service reference scan、165-test inventory。

### T15 冻结唯一下一候选

- **状态**：completed
- **依赖**：T12～T14
- **决策**：Conditional Go=`T66 bounded-stage ProgramService domain`；其他候选有 disposition。
- **验收**：预备 RC-01～RC-07/09/10 数学闭合；只授权下一 formal WI，不授权产品实现。
- **停止**：保护/实现 additions、shadow、文件/函数或语义边界不可达即改为 No-Go，不扩大删除分母。

## Batch 2：父路线缺口修正

### T21 修正 L3 稳定期/发布禁令死锁

- **状态**：completed
- **依赖**：T15
- **文件**：WI-196 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`。
- **改动**：把 WP-06/WP-07 的稳定发布周期明确为主线预发布稳定周期；RC-08 前不创建版本/tag/Release/PyPI/全局 CLI；RC-06 文字范围与适用矩阵统一。
- **验收**：candidate merge 后 legacy 仍在；required CI + wheel/sdist clean install + offline/sibling + selector rollback/reapply 通过后才允许独立 deletion PR；删除前不能关闭。
- **回退**：revert WI212 formal PR；不得只保留 Conditional Go 而撤掉稳定期定义。

## Batch 3：双 Agent 对抗评审

### T31 冻结 formal-six identity

- **状态**：completed
- **依赖**：T21
- **范围**：按父 plan §9 唯一算法计算 child/parent `spec.md + plan.md + tasks.md` 六文件 SHA-256 与 canonical combined。
- **验收**：工作树中的六文件与受审 identity 一致；审查期间只读。

### T32 LEAN/YAGNI 独立审查

- **状态**：pending
- **依赖**：T31
- **Reviewer**：Pascal
- **检查**：候选排序、收益/预算、是否过度实现、是否小收益拖延结构主线、恢复入口。
- **通过**：`PASS` 且 actionable findings=0。

### T33 SAFETY/COMPAT 独立审查

- **状态**：pending
- **依赖**：T31
- **Reviewer**：Confucius
- **检查**：功能/CLI/artifact/状态/授权/平台/离线/回退证据，发布禁令和旧 claim 边界。
- **通过**：`PASS` 且 actionable findings=0。

### T34 处置 finding 并同 identity 复审

- **状态**：pending
- **依赖**：T32、T33
- **规则**：正确 finding 做最小修正；错误/扩范围建议记录拒绝证据；六文件变化使双方旧 verdict 同时失效。
- **完成**：同一 identity 上 Pascal/Confucius 均 PASS、findings=0。

## Batch 4：truth、PR 与 fresh-main 验收

### T41 同步 continuity 与 closure

- **状态**：pending
- **依赖**：T34
- **范围**：root/scoped handoff、WI212 execution log、development summary、parent writeback。
- **验收**：handoff byte-identical；只声明候选选择完成，不声明 T66 实现或路线关闭。

### T42 绑定 program truth 并冻结 clean identity

- **状态**：pending
- **依赖**：T41
- **步骤**：一次 truth sync；manifest/project-state/文档单一提交链；禁止重复 sync 制造 identity。
- **验收**：truth `ready/fresh`、source inventory complete；active pre-close/closure 只出现父合同允许的精确状态；
  `test_repo_program_manifest.py` 只机械替换 inventory/close 两值，diff=`+2/-2`，无测试逻辑/LOC 增量。

### T43 运行最终本地门禁

- **状态**：pending
- **依赖**：T42
- **验证**：
  - `ai-sdlc verify constraints`
  - `ai-sdlc program validate`
  - `ai-sdlc program truth audit`
  - manifest exact integration test
  - `git diff --check`
  - 禁止路径 zero diff
  - root/scoped handoff parity
  - clean worktree

### T44 双 review current HEAD、PR 与 merge

- **状态**：pending
- **依赖**：T43
- **验收**：两个本地 reviewer 对 current HEAD/tree PASS；Codex reviewed current head 无 actionable finding；全部 required checks 成功；squash merge。

### T45 detached fresh-main 验收

- **状态**：pending
- **依赖**：T44
- **验收**：merge tree=reviewed tree；constraints/validate/truth/manifest/scope/parity/clean 全绿。
- **后续**：只创建新的 T66 bounded-stage formal WI；不得直接在 WI212 分支实现或发布。

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| FR-001～FR-004 | T11～T15 |
| FR-005 | T11、T41～T45 |
| FR-006、FR-006A | T21、T32～T45 |
| FR-007 | T31～T34、T44 |
| FR-008 | T15、T41、T45 |
| SC-001～SC-003 | T12～T21 |
| SC-004～SC-005 | T41～T45 |
| SC-006 | T31～T34、T44 |
| SC-007 | T15、T45 |
