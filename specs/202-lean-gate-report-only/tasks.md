---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Lean Gate Report-Only 基线

**编号**：`202-lean-gate-report-only`
**预算**：产品新增 `≤210` LOC，test/harness/normalizer 新增 `≤140` LOC，合计 `≤350` LOC。
**禁止**：T62B/T62C、现有 gate/telemetry/state/config 改动、公共抽象、依赖、schema、fixture/snapshot。

## Batch 1：formal 与准入

### T11 捕获 T61A 旧行为基线

- **状态**：completed
- **依赖**：mainline `d19c8b7d`
- **产物**：`spec.md` §3、`task-execution-log.md` Batch 001
- **验收**：独立 clone 捕获 help/plain/JSON/exit/telemetry 写集/tracked tree；动态字段 allowlist 明确。

### T12 冻结具体 RC-06 分母与预算

- **状态**：completed-pending-review
- **依赖**：T11
- **产物**：`spec.md` §4
- **验收**：10 个精确符号基线 2,254 LOC；保守预计净删除 1,400 LOC；WI-202 总预算 350 LOC；双 PASS 前可用预算为 0。

### T13 双 Agent formal admission

- **状态**：in-progress
- **依赖**：T11、T12
- **验收**：兼容安全与精简效率 agent 分别复算 `spec + plan + tasks + expected-delta` 同一 hash；findings、处置、时间和 verdict 落日志；内容变化后双方重跑，最终均为 PASS。
- **停止**：任一 agent 认为分母不可证、兼容差异未冻结或方案超过 350 LOC，即保持 design，不进入 RED。

## Batch 2：RED characterization

### T21 冻结原 verify constraints 零差异

- **状态**：planned
- **依赖**：T13
- **文件**：`tests/integration/test_cli_verify_constraints.py`、`expected-delta.json`
- **验收**：plain/JSON/exit/digest 语义/telemetry 写集/adapter/config 与基线一致；仅 command help 新增一行在 allowlist。

### T22 新命令与 code rule RED

- **状态**：planned
- **依赖**：T13
- **文件**：`tests/integration/test_cli_verify_lean_report.py`、`tests/unit/test_command_names.py`
- **验收**：缺命令或 core 时按预期失败；覆盖 400/50、新/历史/changed、分类优先级、rename、Unicode/CRLF/Windows path、binary/symlink/submodule/unavailable、确定排序和 exit 0。

### T23 contract rule 与副作用 RED

- **状态**：planned
- **依赖**：T13
- **验收**：覆盖 declared/expected/gaps、非法/重复 token、waiver_effect=none、两个规则族独立 unavailable、前后文件/hash/Git 零写入；失败原因必须是未实现而非 fixture 错误。

## Batch 3：最小实现

### T31 实现纯读取 report builder

- **状态**：planned
- **依赖**：T22、T23 RED
- **文件**：`src/ai_sdlc/core/lean_gate_report.py`
- **验收**：`lean-gate-report/v1` 字段、NUL diff、blob/mode、分类、AST、父矩阵解析和 neutral findings 通过；单文件≤400、函数≤50、无公共框架。

### T32 接入薄 CLI

- **状态**：planned
- **依赖**：T31
- **文件**：`src/ai_sdlc/cli/verify_cmd.py`、`tests/unit/test_command_names.py`
- **验收**：三个显式参数、plain/JSON 一致；合法 findings/unavailable exit 0；usage error 保持 Typer 标准；不初始化 telemetry。

### T33 收敛到 RC-06

- **状态**：planned
- **依赖**：T31、T32
- **验收**：产品≤210、测试≤140、合计≤350；新产品/测试文件各≤1；公共抽象/依赖/schema/fixture=0。超限则 No-Go，不得把预算改大。

## Batch 4：候选验收与回退

### T41 全量与兼容验收

- **状态**：planned
- **依赖**：T21～T33
- **命令**：targeted pytest、full pytest、Ruff、mypy、`verify constraints`、Program Truth audit、`git diff --check`、exact-revision lean report。
- **验收**：全部 fresh PASS；原表面零未批准差异；snapshot fresh 且无新 blocker。

### T42 零写入与跨平台验收

- **状态**：planned
- **依赖**：T41
- **验收**：独立 clone 前后内容 hash、Git、telemetry/checkpoint/config/manifest 均无 delta；Ubuntu/macOS/Windows Python 3.11/3.12 required matrix 通过。

### T43 rollback drill

- **状态**：planned
- **依赖**：T41
- **验收**：临时 index 或 worktree revert candidate commits 后原 command surface、constraints、targeted/full smoke 恢复；不修改当前分支历史。

### T44 双 Agent 最终代码审查

- **状态**：planned
- **依赖**：T41～T43
- **验收**：兼容安全与精简效率 agent 审阅同一 candidate commit/tree；双方 PASS。任何修复使旧 PASS 失效并重跑。

## Batch 5：PR、合并与 mainline

### T51 提交并开启 PR

- **状态**：planned
- **依赖**：T44
- **验收**：intentional commit、push、ready PR、`@codex review`、约五分钟 heartbeat；PR body 包含 base/head、预算、测试、回退和 expected delta。

### T52 review/CI 收敛与合并

- **状态**：planned
- **依赖**：T51
- **验收**：Codex 无 actionable major issue；required checks 全绿；focused 修复均有 fresh evidence；PR 合并且远端 feature branch 按策略清理。

### T53 mainline 重放与父项同步

- **状态**：planned
- **依赖**：T52
- **验收**：mainline exact tree 等于 reviewed tree；targeted、constraints、truth audit、lean report 重放；WI-196 Gap Evidence Index 将 T61A/T62A 标为 closed，T62B 保持下一独立项。

## 需求追踪

| 规格 | 任务 |
|---|---|
| FR-202-01～FR-202-03 | T22、T23、T31、T32 |
| FR-202-04～FR-202-06 | T22、T23、T31、T32 |
| FR-202-07～FR-202-09 | T21、T23、T41、T42 |
| FR-202-10 / RC-06 / RC-07 / RC-09 | T12、T33、T41 |
| RC-01～RC-03 / RC-10 | T11、T12、T41、T43、T51 |
| CC-01～CC-03 | T11、T21、T22、T41 |
| CC-05～CC-07 | T23、T41、T42、T43 |
| SC-202-01～SC-202-06 | T13、T33、T41～T53 |
