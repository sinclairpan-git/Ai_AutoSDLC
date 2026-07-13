# 任务分解：AI-SDLC 精简代码治理与框架自身减重计划

**编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**日期**：2026-07-12
**来源**：`spec.md` + `plan.md`
**执行边界**：本工作项所有任务均为治理文档与真值同步，不修改产品运行时代码。

## 任务路径约束

允许路径：

- `specs/196-ai-sdlc-lean-code-self-reduction-governance/**`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `.ai-sdlc/state/checkpoint.yml`
- `.ai-sdlc/state/codex-handoff.md`
- `.ai-sdlc/state/resume-pack.yaml`
- `.ai-sdlc/work-items/196-ai-sdlc-lean-code-self-reduction-governance/codex-handoff.md`

禁止路径：

- `src/ai_sdlc/**`
- `tests/**`
- `rules/**`
- `src/ai_sdlc/rules/**`
- `providers/**`
- `.github/workflows/**`

## Batch 1：基线与范围冻结

### Task 1.1：创建独立工作区与正式工作项

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. Work Item 196 位于独立 worktree 和独立 docs 分支。
  2. canonical 四件套直接位于 `specs/196-ai-sdlc-lean-code-self-reduction-governance/`。
  3. `program-manifest.yaml` 登记唯一 spec entry，`next_work_item_seq` 更新为 197。
  4. 当前 main 上的未提交 handoff/benchmark 文件未进入该分支。
- **验证**：`git status --short --branch`、manifest 定向检索、四件套文件检查。
- **回退**：删除 worktree 和未合并分支，不影响 main。

### Task 1.2：记录可复现的当前基线

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`spec.md`、`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. 记录产品/测试文件数、LOC、超限文件、超长函数和主要结构重复。
  2. 明确静态相似度数据是候选信号，不直接等同于可删除代码。
  3. 记录全量测试 baseline revision 和结果。
- **验证**：重新执行只读统计和 `uv run pytest`。
- **回退**：恢复统计段落，不影响运行时。

## Batch 2：原则与兼容契约冻结

### Task 2.1：冻结 Lean Code 原则

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`spec.md`
- **可并行**：否
- **验收标准**：
  1. LP-01 至 LP-12 完整、无互相矛盾。
  2. 原则同时防止功能缩水和过度抽象。
  3. 明确功能开发与减重不能混批。
- **验证**：原则编号唯一性、占位符和交叉引用扫描。
- **回退**：文档 revert。

### Task 2.2：冻结公共兼容面

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`spec.md`、`plan.md`
- **可并行**：否
- **验收标准**：
  1. CC-01 至 CC-08 覆盖 CLI、artifact、状态、副作用、平台和兄弟项目。
  2. 每个契约有机器可执行的比较方式。
  3. 明确非语义动态字段的规范化边界。
- **验证**：兼容矩阵人工对账。
- **回退**：文档 revert。

### Task 2.3：冻结风险、停止和回退规则

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`spec.md`、`plan.md`
- **可并行**：否
- **验收标准**：
  1. L1-L4 风险等级完整。
  2. 所有 L2/L3 工作包具有 Golden/differential/fallback 要求。
  3. 未批准行为差异和 smoke 失败均触发停止。
- **验证**：风险矩阵与工作包逐项映射。
- **回退**：文档 revert。

## Batch 3：子工作项路线图

### Task 3.1：定义兼容保险和 Lean Gate 工作包

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T23
- **文件**：`plan.md`
- **可并行**：否
- **验收标准**：
  1. WP-01 在任何产品减重之前建立 Characterization/Golden Master。
  2. WP-02 采用 report-only → warning → blocking 渐进策略。
  3. 两个工作包均有完成条件和回退方式。
- **验证**：路线图依赖检查。
- **回退**：文档 revert。

### Task 3.2：定义低、中、高风险减重工作包

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`plan.md`
- **可并行**：否
- **验收标准**：
  1. WP-03 至 WP-08 按风险递增排序。
  2. `ProgramService` 和 stage engine 不得早于兼容保险启动。
  3. 高风险切换保留 facade/旧实现并延迟删除。
- **验证**：工作包入口条件、完成条件、停止条件和回退方式逐项检查。
- **回退**：文档 revert。

### Task 3.3：冻结验证与 PR 策略

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`plan.md`
- **可并行**：否
- **验收标准**：
  1. L1-L3 验证矩阵完整。
  2. 每个子工作项独立 work item、branch、PR 和 revert。
  3. L3 必须本地独立只读 review，并遵守仓库 mainline PR 协议。
- **验证**：与 `AGENTS.md`、constitution、quality-gate 对账。
- **回退**：文档 revert。

## Batch 4：真值同步、验证和评审

### Task 4.1：同步 program truth 与 handoff

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、handoff 文件、`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. Work Item 196 在 program/project truth 中唯一登记。
  2. handoff 记录当前目标、状态、变更、命令、风险和下一步。
  3. 不把原 main 工作区的 WI-195 handoff 改动带入本分支。
- **验证**：`program truth sync --dry-run`、handoff show、git diff。
- **回退**：仅 revert 196 对应的 truth/handoff 变更。

### Task 4.2：运行文档与仓库门禁

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. 四件套无占位符。
  2. `uv run ai-sdlc verify constraints` 无 BLOCKER。
  3. `git diff --check` 通过。
  4. 相对 main 没有产品代码、测试或 runtime rules 变更。
- **验证**：占位符扫描、constraints、diff-check、路径白名单检查。
- **回退**：修正文档或撤销不合规路径。

### Task 4.3：完成本地只读评审并提交用户审核

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：四件套与 handoff
- **可并行**：否
- **验收标准**：
  1. 无 BLOCKER；WARNING 已修复或明确记录。
  2. 评审确认本工作项没有进入产品实现。
  3. 文档提交后等待用户批准，未批准前不创建 WP-01 实现分支。
- **验证**：独立只读 review 结果、git status、commit 内容检查。
- **回退**：按评审意见修订后重新验证。

## 需求追踪矩阵

| 需求 | 任务 |
|---|---|
| FR-001～FR-005 | T12、T21 |
| FR-006～FR-008 | T22、T31、T32 |
| FR-009～FR-012 | T23、T32、T33 |
| FR-013～FR-015 | T23、T31、T42 |
| FR-016 | T11、T42、T43 |
| FR-017～FR-018 | T32、T33、T43 |
