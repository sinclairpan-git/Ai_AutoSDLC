# 任务执行日志：AI-SDLC 精简代码治理与框架自身减重计划

**功能编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**创建日期**：2026-07-12
**状态**：进行中

## 1. 归档规则

- 本文件只记录 Work Item 196 治理总项；后续产品减重使用各自子工作项日志。
- 每批必须记录范围、命令、结果、风险、回退和任务同步状态。
- 本工作项不得修改 `src/ai_sdlc/`、`tests/`、runtime rules、provider 或 workflow。
- 代码/功能实现不得以“完善计划”为由混入本分支。

## 2. Batch 2026-07-12-001：独立分支、基线与 canonical scaffold

### 2.1 范围

- 覆盖任务：T11、T12。
- 基线 revision：`c0f333c82c6f096ea8e74e57378eb7d7368f276c`。
- 独立 worktree：`.worktrees/196-lean-code-self-reduction-governance`。
- 独立分支：`feature/196-ai-sdlc-lean-code-self-reduction-governance-docs`。

### 2.2 执行命令与结果

- `git worktree add .worktrees/196-lean-code-self-reduction-governance -b codex/196-lean-code-self-reduction-governance main`
  - 结果：成功创建隔离 worktree；随后因 canonical `workitem init` 分支前置重命名为 `feature/196-ai-sdlc-lean-code-self-reduction-governance-docs`。
- `uv sync --frozen`
  - 结果：成功创建 Python 3.11.15 虚拟环境并按锁文件安装依赖。
- `uv run pytest`
  - 结果：`3145 passed, 3 skipped in 443.28s`。
- `uv run ai-sdlc workitem init ...`
  - 首次结果：adapter hook 改写 `.cursor/rules/ai-sdlc.mdc`，与 workitem init 的 clean-tree preflight 冲突，命令被安全阻断。
  - 处置：用 `apply_patch` 恢复 adapter 与测试触发的 resume-pack 路径副作用；未提交或 stash 无关变化。
  - 第二次结果：使用仓库集成测试同样的 `CliRunner + patch(run_ide_adapter_if_initialized)` 方式，只抑制无关 adapter hook，canonical branch preflight、scaffolder 和 manifest sync 完整执行；四件套创建成功，`program-manifest.yaml` 登记成功。

### 2.3 基线事实

- 产品 Python：215 文件、107,482 行；61 文件超过 400 行，51 文件超过 500 行，15 文件不少于 1,000 行。
- 产品函数：3,348 个；357 个超过 50 行，159 个不少于 100 行。
- 测试 Python：189 文件、109,872 行；55 文件超过 400 行，21 文件不少于 1,000 行。
- 静态结构重复只作为工作包候选信号，不能直接视为可删除代码；任何删除仍需 Golden/differential evidence。

### 2.4 风险与决策

- 决策 D-001：不绕过 docs branch preflight；按 CLI 接受的 `feature/<wi>-docs` 命名分支。
- 决策 D-002：不把 adapter 自动升级混入本治理项目。
- 决策 D-003：本工作项只创建治理四件套，不修改产品代码。
- 风险 R-001：全量测试会重写 root-bound `resume-pack.yaml` 绝对路径；每次验证后必须检查并恢复非项目副作用。
- 风险 R-002：CLI adapter hook 与 clean-tree preflight 存在顺序冲突；本工作项只记录现象，不顺带修复。
- 风险 R-003：checkpoint 通过 `linked_wi_id` 关联到 196 后，handoff CLI 仍从旧 `feature=189` 派生 resume-pack 工作集；本分支保留 checkpoint 历史 feature/stage，只将 resume-pack 的当前 spec/plan/tasks/branch 指针纠正到 196。

### 2.5 任务同步

- T11：已完成。
- T12：已完成；基线统计与全量测试证据均已复核。
- 是否进入产品实现：否。

## 3. Batch 2026-07-12-002：原则、兼容契约与路线图

### 3.1 范围

- 覆盖任务：T21、T22、T23、T31、T32、T33。
- 改动：将 scaffold 占位内容重写为 Work Item 196 专用治理规范。

### 3.2 产出

- `spec.md`：LP-01～LP-12、CC-01～CC-08、L1～L4、FR-001～FR-018、成功标准和冻结决策。
- `plan.md`：WP-01～WP-08、Lean Gate 渐进策略、验证矩阵、停止条件、提交/PR 策略。
- `tasks.md`：docs-only 路径约束、四批治理任务和需求追踪矩阵。

### 3.3 当前状态

- 文档编写：完成。
- 占位符自审：待执行。
- program truth / handoff：待同步。
- constraints / diff-check：待执行。
- 独立只读评审：待执行。
- 用户审核：待提交后进行。

## 4. Batch 2026-07-12-003：自审、关联与提交前验证

### 4.1 覆盖任务

- T41、T42；T43 在提交后完成 revision truth-check 和用户审核交付。

### 4.2 命令与结果

- 文档契约脚本：LP=12、CC=8、FR=18、SC=8，YAML 可解析，manifest 中 196 唯一登记；结果 PASS。
- `git diff --check`：PASS。
- 产品路径白名单检查：`src/ai_sdlc/`、`tests/`、`rules/`、`providers/`、`.github/workflows/` 无变更。
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`。
- `workitem plan-check --wi ...`：不适用；196 不引用外部 `related_plan`，canonical plan 即本目录 `plan.md`。
- 提交前 `workitem truth-check --wi ...`：按预期返回未在 HEAD 找到四件套；该命令只读取 revision，不读取未提交文件，提交后必须重跑。
- `workitem link`：checkpoint 的 `linked_wi_id` / `linked_plan_uri` 已关联到 196。
- `handoff update`：canonical 与 scoped handoff 已生成；resume-pack 的旧 feature 派生指针已纠正为 196。

### 4.3 自审结论

- 规格覆盖：LP、CC、FR、SC 均有任务或验证映射。
- 占位符：扫描未发现实际占位内容；`SC-001` 中只保留机器检查的禁止项定义。
- 范围：保持 docs-only，没有产品实现。
- 兼容：没有删除或改变公共功能。
- 当前结论：允许提交治理基线；提交后继续 revision truth/program truth 验证。
