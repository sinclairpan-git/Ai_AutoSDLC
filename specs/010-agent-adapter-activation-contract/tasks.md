---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/USER_GUIDE.zh-CN.md"
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
