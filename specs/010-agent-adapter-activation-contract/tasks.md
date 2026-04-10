---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "USER_GUIDE.zh-CN.md"
---
# 任务分解：Agent Adapter Activation Contract

**编号**：`010-agent-adapter-activation-contract` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-010-001 ~ FR-010-024 / SC-010-001 ~ SC-010-005）

---

## 分批策略

```text
Batch 1: selection truth and activation state model freeze
Batch 2: CLI surface and activation gate baseline
Batch 3: adapter template rewrite, migration, and regression matrix
Batch 4: persistence durability implementation
Batch 5: selector and activation truth implementation
Batch 6: docs, backlog, and execution close-out
```

---

## Batch 1：selection truth and activation state model freeze

### Task 1.1 冻结 Editor Host / Agent Target 分离模型

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确选择目标是 `Agent Target`，不是 `Editor Host`
  2. formal docs 明确 mixed host 场景下插件代理优先于编辑器宿主
  3. 固定列表为 `Claude Code / Codex / Cursor / VS Code / 其他-通用`
- **验证**：文档对账

### Task 1.2 冻结 activation state / evidence / support tier 模型

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确至少存在 `selected / installed / acknowledged / activated`
  2. formal docs 明确 `adapter installed != governance activated`
  3. formal docs 明确 activation evidence 与 support tier 是门禁输入的一部分
- **验证**：文档对账

### Task 1.3 冻结旧项目迁移保守语义

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`, `specs/010-agent-adapter-activation-contract/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确旧项目迁移默认只能落到 `installed` 或等价软接入状态
  2. formal docs 禁止将旧版 `adapter_applied` 自动升级为 `activated`
  3. formal docs 明确 backward compatibility 不得制造误导性成功语义
- **验证**：文档交叉引用检查

---

## Batch 2：CLI surface and activation gate baseline

### Task 2.1 冻结 init 选择器与 non-interactive 入口合同

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`, `specs/010-agent-adapter-activation-contract/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `init` 的自动探测只负责默认聚焦，不自动确认
  2. 非交互环境必须优先使用显式参数，否则走 deterministic fallback
  3. formal docs 明确交互式选择与非交互 fallback 的单一语义
- **验证**：命令语义对账

### Task 2.2 冻结 `adapter select / status / activate` CLI surface

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 给出显式 adapter 管理命令面或等价能力集合
  2. formal docs 明确 activation handshake 不得继续隐藏在 Markdown 提示中
  3. formal docs 明确 `status` 必须显示 target、state、tier、evidence
- **验证**：文档对账

### Task 2.3 冻结 activation gate 与误导性成功语义阻断规则

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确哪些命令在 `installed-only` 状态下只能降级或阻断
  2. formal docs 明确 `run --dry-run` 成功不代表 activation 成功
  3. formal docs 明确未激活前不得宣称“框架已接管”
- **验证**：状态与门禁语义检查

---

## Batch 3：adapter template rewrite, migration, and regression matrix

### Task 3.1 冻结 adapter 模板改写口径

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `.codex/AI-SDLC.md`、`.claude/AI-SDLC.md` 等模板应由“先 dry-run”改为“先 activate，再 dry-run”
  2. formal docs 明确模板文件不再被视为接管成功证据
  3. formal docs 明确模板只是 activation surface 的一部分
- **验证**：文档对账

### Task 3.2 冻结 mixed host / installed-only / non-interactive 回归矩阵

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/010-agent-adapter-activation-contract/plan.md`, `specs/010-agent-adapter-activation-contract/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 mixed host 正反向测试矩阵
  2. formal docs 明确 `installed != activated` 回归测试
  3. formal docs 明确非交互 `--agent-target` 与 fallback 的测试覆盖
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 formal baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`, `specs/010-agent-adapter-activation-contract/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 `selection / activation / gate / migration / tests` 五类边界保持单一真值
  3. 当前 `design/010-agent-adapter-activation-contract` 分支上的 formal docs 可作为后续继续实现该 P0 修复的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：persistence durability implementation

### Task 4.1 实现 YAML save no-op 与 Windows replace retry

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`src/ai_sdlc/core/config.py`, `tests/unit/test_project_config.py`
- **可并行**：否
- **验收标准**：
  1. `project-config.yaml` 序列化内容未变化时不再触发实际写入
  2. Windows `PermissionError` 在 bounded retry/backoff 内可恢复
  3. 持续性权限错误仍会显式失败
- **验证**：`uv run pytest tests/unit/test_project_config.py -q`

### Task 4.2 实现 adapter config no-op persistence

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/integrations/ide_adapter.py`, `tests/unit/test_ide_adapter.py`, `tests/integration/test_cli_status.py`
- **可并行**：否
- **验收标准**：
  1. 配置字段未变时不刷新 `adapter_applied_at`
  2. adapter 相关重复命令不再无差别改写 `project-config.yaml`
  3. 状态变化时仍能正常落盘
- **验证**：`uv run pytest tests/unit/test_project_config.py tests/unit/test_ide_adapter.py tests/integration/test_cli_status.py -q`

---

## Batch 5：selector and activation truth implementation

### Task 5.1 实现统一 agent-target detect / selector helper

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T42
- **文件**：`src/ai_sdlc/integrations/agent_target.py`, `src/ai_sdlc/integrations/ide_adapter.py`, `tests/unit/test_agent_target.py`, `tests/unit/test_ide_adapter.py`
- **可并行**：否
- **验收标准**：
  1. mixed host env 下 `codex` / `claude_code` 优先于 `vscode`
  2. selector 固定五项，支持上下键与回车确认
  3. detect / selector truth 可被 `init` 与 `adapter select` 复用
- **验证**：`uv run pytest tests/unit/test_agent_target.py tests/unit/test_ide_adapter.py -q`

### Task 5.2 将 selector 接到 init 与 adapter select

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/commands.py`, `src/ai_sdlc/cli/adapter_cmd.py`, `tests/integration/test_cli_init.py`, `tests/integration/test_cli_adapter.py`
- **可并行**：否
- **验收标准**：
  1. `init` 在交互式 TTY 且无显式参数时进入 selector
  2. `adapter select` 在交互式 TTY 且无显式参数时进入同一 selector
  3. 非交互环境下显式参数仍可稳定 override；无参数时走 deterministic fallback 或 bounded user error
- **验证**：`uv run pytest tests/integration/test_cli_init.py tests/integration/test_cli_adapter.py -q`

### Task 5.3 暴露 activation evidence / support tier truth surface

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`src/ai_sdlc/models/project.py`, `src/ai_sdlc/integrations/ide_adapter.py`, `src/ai_sdlc/cli/adapter_cmd.py`, `src/ai_sdlc/cli/commands.py`, `tests/integration/test_cli_adapter.py`, `tests/integration/test_cli_status.py`, `tests/integration/test_cli_run.py`
- **可并行**：否
- **验收标准**：
  1. `adapter activate` 会写 activation source / evidence / timestamp / acknowledged tier
  2. `adapter status` 与 `status` 会显示 target、state、tier 与 activation truth
  3. 未激活时 `run --dry-run` 仍不会误报已接管
- **验证**：`uv run pytest tests/integration/test_cli_adapter.py tests/integration/test_cli_status.py tests/integration/test_cli_run.py -q`

---

## Batch 6：docs, backlog, and execution close-out

### Task 6.1 回写 USER_GUIDE 与 backlog 真值

- **任务编号**：T61
- **优先级**：P1
- **依赖**：T53
- **文件**：`USER_GUIDE.zh-CN.md`, `docs/framework-defect-backlog.zh-CN.md`, `specs/010-agent-adapter-activation-contract/spec.md`, `specs/010-agent-adapter-activation-contract/plan.md`, `specs/010-agent-adapter-activation-contract/tasks.md`
- **可并行**：否
- **验收标准**：
  1. USER_GUIDE 把交互式 selector 写回主路径，`--agent-target` 退回 fallback/override
  2. backlog 中 `FD-2026-04-02-002/003/004` 与 `FD-2026-04-03-005` 的状态与当前实现一致
  3. `010` formal docs 不再停留在 `formal_freeze_only`
- **验证**：`uv run ai-sdlc verify constraints`, `git diff --check -- docs specs/010-agent-adapter-activation-contract`

### Task 6.2 创建 execution log 并完成 close-out 验证

- **任务编号**：T62
- **优先级**：P1
- **依赖**：T61
- **文件**：`specs/010-agent-adapter-activation-contract/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `task-execution-log.md` 覆盖 latest batch 的 code-change 验证证据、代码审查、任务同步与 git close-out markers
  2. `uv run ai-sdlc workitem close-check --wi specs/010-agent-adapter-activation-contract` 通过
  3. `uv run ai-sdlc workitem truth-check --wi specs/010-agent-adapter-activation-contract` 不再是 `formal_freeze_only`
- **验证**：`uv run ai-sdlc workitem close-check --wi specs/010-agent-adapter-activation-contract`, `uv run ai-sdlc workitem truth-check --wi specs/010-agent-adapter-activation-contract`
