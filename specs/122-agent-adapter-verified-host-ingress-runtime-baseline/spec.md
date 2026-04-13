# 功能规格：Agent Adapter Verified Host Ingress Runtime Baseline

**功能编号**：`122-agent-adapter-verified-host-ingress-runtime-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：`program-manifest.yaml`、`specs/010-*`、`specs/094-*`、`specs/120-*`、`specs/121-*`、`src/ai_sdlc/models/project.py`、`src/ai_sdlc/integrations/agent_target.py`、`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`、`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`、`tests/integration/test_cli_init.py`、`tests/integration/test_cli_run.py`

> 口径：`122` 不是再做一版 adapter 说明文，也不是继续让用户执行 `adapter activate` 兜底。它承接 `121` 已冻结的 root truth，把“真实 adapter 安装/验证”正式落成 runtime baseline：固定明确适配目标与默认入口，新增自动 verify 与诚实降级状态机，并把 `run / init / status` 的门禁从人工确认迁到 machine-verifiable ingress truth。

## 问题定义

`121` 已经把一个根级事实冻结清楚：当前仓库缺的不是“再投放一份提示文件”，而是 **verified host ingress runtime**。现状缺口可以直接落到代码面：

- `agent_target` 仍只服务旧的 soft-prompt 语义，没有 verified host ingress 的状态模型
- `ide_adapter.py` 当前把 Claude/Codex/VS Code 写到 `.claude/AI-SDLC.md`、`.codex/AI-SDLC.md`、`.vscode/AI-SDLC.md` 这类非厂商公开默认读取入口
- `run` 当前只阻断 `installed`，但 `acknowledged` 本质仍是 operator acknowledgement，不是宿主真实加载
- `init`/`adapter status` 仍把“先 `adapter activate`，再 `run --dry-run`”作为主路径
- `TRAE` 既没有被厂商公开文档明确支持默认读取入口，也没有可冻结的验证协议，因此当前只能按 `generic` 处理，不能被加入明确适配列表

如果这一层继续不落成 runtime，仓库虽然已经有 `121` root truth，但用户路径仍然是假闭环：

1. 安装命令结束后，系统不知道宿主是否真的读取了规则
2. `adapter activate` 继续把执行压力丢给用户
3. 下游 mainline / managed delivery 仍可能在 soft prompt acknowledged 状态下继续误放行

## 范围

- **覆盖**：
  - 固定当前明确适配目标与默认入口写入路径
  - 为 `adapter` 建立 `materialized / verified_loaded / degraded / unsupported` ingress truth
  - 新增 `adapter verify` 或等价自动 verify runtime
  - 让 `init` / `adapter select` 自动触发 materialize + verify
  - 更新 `status / adapter status / run` 的 gate truth
  - 补 unit/integration focused tests
- **不覆盖**：
  - 为厂商公开支持尚不明确的目标单列新 adapter target
  - 做第三方 IDE/plugin 原生双向深集成 beyond bounded verification
  - 把所有下游 managed delivery / browser gate 一并改完
  - 重新设计 `121` 已冻结的 root truth

## 已锁定决策

- 明确适配目标在 runtime 中仍只允许：
  - `Claude Code`
  - `Codex`
  - `Cursor`
  - `VS Code`
  - `generic`
- `TRAE` 不新增为单独 target；在厂商公开支持不明确前，一律按 `generic` 处理
- 当前 v1 默认入口基线冻结为：
  - `Claude Code` -> `.claude/CLAUDE.md`
  - `Codex` -> `AGENTS.md`
  - `Cursor` -> `.cursor/rules/ai-sdlc.mdc`
  - `VS Code` -> `.github/copilot-instructions.md`
  - `generic` -> `.ai-sdlc/memory/ide-adapter-hint.md`
- ingress runtime 的最小状态机冻结为：
  - `materialized`
  - `verified_loaded`
  - `degraded`
  - `unsupported`
- `adapter activate` 降级为 compatibility/debug surface；它可以保留，但不再是主路径成功条件
- `init` / `adapter select` 完成后，系统必须自动尝试 verify；用户默认不再需要手动执行 `adapter activate`
- `run --dry-run` 可以在 `materialized`/`degraded` 状态下继续，但必须诚实提示非 verified；任何 mutating mainline / managed delivery 路径不得把 `acknowledged` 或未验证状态视为 verified success

## 当前运行时目标矩阵

| Target | v1 canonical path | verify expectation | 当前策略 |
|---|---|---|---|
| `Claude Code` | `.claude/CLAUDE.md` | 尝试拿到 machine-verifiable ingress evidence | 明确适配 |
| `Codex` | `AGENTS.md` | 尝试拿到 machine-verifiable ingress evidence | 明确适配 |
| `Cursor` | `.cursor/rules/ai-sdlc.mdc` | 尝试拿到 machine-verifiable ingress evidence | 明确适配 |
| `VS Code` | `.github/copilot-instructions.md` | 尝试拿到 machine-verifiable ingress evidence | 明确适配 |
| `generic` | `.ai-sdlc/memory/ide-adapter-hint.md` | 无统一 verify protocol | 诚实降级 |

## 用户故事与验收

### US-122-1 — Operator 需要安装完成后自动得到真实适配结果

作为 **operator**，我希望 `ai-sdlc init` 或 adapter 选择完成后，系统自动完成目标落位并尝试验证，而不是再让我手工执行 `adapter activate` 才能继续。

**验收**：

1. Given 我执行 `ai-sdlc init` 或 `adapter select`，When 命令结束，Then 系统已经自动完成 materialize + verify 或诚实降级  
2. Given verify 失败或目标只支持 generic，When 我查看结果，Then 只能看到 `degraded/unsupported` 等诚实状态，而不是“已激活”

### US-122-2 — Maintainer 需要 `run` 按 ingress truth 门禁

作为 **maintainer**，我希望 `run` 的前置门禁基于 verified host ingress truth，而不是用户是否执行过 `adapter activate`，这样下游 mutating 路径不会再偷跑。

**验收**：

1. Given 当前 target 只有 `materialized` 或 `degraded`，When 运行 `ai-sdlc run --dry-run`，Then 命令可以继续，但必须清楚说明非 verified 状态  
2. Given 当前 target 未达到 mutating delivery 允许阈值，When 进入 managed delivery / mutating path，Then 系统必须阻断并给出稳定 reason code

### US-122-3 — Reviewer 需要回归测试覆盖新的路径矩阵

作为 **reviewer**，我希望 unit/integration tests 能覆盖默认入口写入、自动 verify、generic 降级和 `TRAE` 不单列这几类路径，这样后续不会退回旧的伪适配实现。

**验收**：

1. Given 我检查 adapter 相关测试，When 查看 target 枚举与路径断言，Then 不再出现 `TRAE` 单列 target  
2. Given 我检查 `init / adapter / run` 回归，When 对照 `122`，Then 可以看到 `materialized / verified_loaded / degraded / unsupported` 的正反夹具

## 功能需求

| ID | 需求 |
|----|------|
| FR-122-001 | 系统必须将当前明确适配目标固定为 `Claude Code / Codex / Cursor / VS Code / generic` |
| FR-122-002 | 系统必须把各目标的默认入口写入路径改为 `122` 冻结的 canonical path |
| FR-122-003 | 系统必须新增或重构 adapter ingress truth，至少覆盖 `materialized / verified_loaded / degraded / unsupported` |
| FR-122-004 | 系统必须提供 `adapter verify` 或等价自动 verify runtime，并让 `init / adapter select` 默认触发 |
| FR-122-005 | `adapter activate` 不得再作为主路径成功条件；若保留，只能作为 compatibility/debug surface |
| FR-122-006 | `status / adapter status` 必须暴露 target、ingress state、verification result、degrade reason 与 evidence 摘要 |
| FR-122-007 | `run --dry-run` 可以在未 verified 状态下继续，但必须诚实提示风险；mutating mainline / managed delivery 路径必须基于 ingress truth 做 gate |
| FR-122-008 | `generic` 不得伪装成明确适配；`TRAE` 当前必须继续按 `generic` 处理 |
| FR-122-009 | `122` 必须补 unit/integration focused tests，覆盖 canonical path、auto verify、generic degrade、run gate 与 `TRAE` 不单列 |

## 成功标准

- **SC-122-001**：adapter 写入路径已切换到 `122` 定义的 canonical path
- **SC-122-002**：`init / adapter select` 完成后不再要求用户先手工执行 `adapter activate`
- **SC-122-003**：`status / adapter status / run` 对 verified/degraded truth 的口径一致
- **SC-122-004**：测试矩阵已覆盖 explicit targets、generic degrade 与 `TRAE` 不单列

---
related_doc:
  - "program-manifest.yaml"
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "specs/121-agent-adapter-verified-host-ingress-truth-baseline/spec.md"
  - "src/ai_sdlc/models/project.py"
  - "src/ai_sdlc/integrations/agent_target.py"
  - "src/ai_sdlc/integrations/ide_adapter.py"
  - "src/ai_sdlc/cli/adapter_cmd.py"
  - "src/ai_sdlc/cli/run_cmd.py"
  - "tests/unit/test_ide_adapter.py"
  - "tests/integration/test_cli_adapter.py"
  - "tests/integration/test_cli_init.py"
  - "tests/integration/test_cli_run.py"
