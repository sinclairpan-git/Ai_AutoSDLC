# 功能规格：Agent Adapter Verified Host Ingress Truth Baseline

**功能编号**：`121-agent-adapter-verified-host-ingress-truth-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：`program-manifest.yaml`、`specs/010-*`、`specs/094-*`、`specs/120-*`、`src/ai_sdlc/integrations/agent_target.py`、`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`

> 口径：`121` 不是直接实现新的 adapter verify runtime，也不是再扩一轮 IDE 列表。它只做一件事：把“真实 adapter 安装/验证”正式提升为 root-level capability truth，冻结明确适配列表、厂商公开支持的默认读取入口边界，以及“未明确支持就只能归入 generic”的规则。

## 问题定义

当前仓库对 adapter 的 formal truth 仍有一个 root-level 缺口：

- `010` 已经把 `installed != activated`、`acknowledged != verified` 的 formal contract 冻结出来
- `094` 已经明确 `init`/Stage 0 不得把 adapter 文件写入误报成“框架已接管”
- `120` 也已经把“真实 adapter 安装/验证”识别成 P0 blocker，但它只能先记成 `pending_root_truth_update`

真正还缺的一层是：**root manifest 还没有正式承认这是一条独立 open capability**。结果就是：

- 当前实现仍把 `.claude/AI-SDLC.md`、`.codex/AI-SDLC.md`、`.vscode/AI-SDLC.md` 这类非厂商公开默认读取入口当成 `installed`
- `adapter activate` 仍只是 operator acknowledgement，却会被下游误读成“可以继续受控开发”
- 像 `TRAE` 这类目标，当前没有查到足够明确的厂商公开文档来证明默认读取入口和验证协议，但如果不把规则写死，又会被重新塞进“明确适配列表”

因此，`121` 的目标不是直接修掉所有 adapter 行为，而是先冻结 root truth：

1. 哪些目标可以进入 **明确适配列表**
2. 哪些入口才算 **厂商公开支持的默认读取入口**
3. 什么情况下只能落为 `generic / degraded / unsupported`
4. `adapter activate` 为什么不能单独等同“真实接入成功”

## 范围

- **覆盖**：
  - 在根级 `program-manifest.yaml` 增加 `agent-adapter-verified-host-ingress` open cluster
  - 冻结明确适配列表与 `generic` 边界
  - 冻结“厂商公开文档明确支持”与“只能归入 generic”的判定规则
  - 冻结 verified host ingress 的最小状态语义
  - 为 `120/T00` 和后续 implementation carrier 提供单一上游 truth
- **不覆盖**：
  - 在本 work item 中直接实现 host/plugin nonce probe
  - 直接改写 `ide_adapter.py`、`run_cmd.py`、`adapter_cmd.py` 的 runtime 行为
  - 为厂商公开支持尚不明确的目标单独建 adapter target
  - retroactively 重写所有历史 adapter 模板与测试

## 已锁定决策

- `program-manifest.yaml > capability_closure_audit` 现在必须正式承认：`agent-adapter-verified-host-ingress` 是一个独立 open cluster
- 明确适配列表当前只包含：
  - `Claude Code`
  - `Codex`
  - `Cursor`
  - `VS Code`
  - `generic`
- `TRAE` 当前**不进入**明确适配列表；在厂商公开文档未明确默认读取入口与验证机制前，只能归入 `generic`
- “明确适配”必须同时满足两件事：
  1. 厂商公开文档明确给出 repo/workspace 级默认读取入口或等价规则入口
  2. 仓库能把后续实现的验证语义绑到该入口，而不是只靠 operator acknowledgement
- verified host ingress 的最小状态语义冻结为：
  - `materialized`：已写入目标入口或等价 hint 面
  - `verified_loaded`：已有机器证据证明宿主/插件本次真的读取了该入口
  - `degraded`：目标存在但缺官方入口、缺验证协议，或当前只能走 best-effort/hint 模式
  - `unsupported`：当前没有可接受的入口/协议，不能宣称适配
- `adapter activate` 在当前 reality 下仍只代表 **operator acknowledgement**；它不能单独满足 `verified_loaded`
- `generic` 不是“弱一点的明确适配”，而是**无法证明厂商公开支持/验证协议时的诚实归类**

## 当前明确适配矩阵（按厂商公开文档冻结）

| Target | 当前可承认的默认入口基线 | 当前结论 |
|---|---|---|
| `Claude Code` | `CLAUDE.md` 或 `.claude/CLAUDE.md` | 明确适配目标 |
| `Codex` | `AGENTS.md` | 明确适配目标 |
| `Cursor` | `.cursor/rules/*.mdc` | 明确适配目标 |
| `VS Code` | `.github/copilot-instructions.md` | 明确适配目标 |
| `generic` | 无统一默认入口；只能 hint/best-effort | 诚实降级目标 |
| `TRAE` | 厂商公开文档尚未明确默认读取入口/验证协议 | 当前归入 `generic` |

## 用户故事与验收

### US-121-1 — Maintainer 需要 root truth 正式承认“真实适配”仍未闭环

作为 **maintainer**，我希望 root manifest 正式承认“真实 adapter 安装/验证”是一个独立 open capability，而不是继续散落在 `010/094/120` 的补丁式文案里。

**验收**：

1. Given 我查看 `program-manifest.yaml`，When 我读取 `capability_closure_audit`，Then 能看到 `agent-adapter-verified-host-ingress` open cluster
2. Given 我查看该 cluster 的 summary，When 对照当前实现，Then 能明确读到“`adapter activate` 不等于 verified host ingress”

### US-121-2 — Operator 需要明确知道哪些目标才算“明确适配”

作为 **operator**，我希望仓库只把厂商公开支持明确的目标列入明确适配列表；如果支持不明确，就只能归入 `generic`，避免安装成功被误报。

**验收**：

1. Given 我审阅 `121`，When 我查看明确适配列表，Then 只能看到 `Claude Code / Codex / Cursor / VS Code / generic`
2. Given 我查看 `TRAE` 的处理规则，When 我对照 `121`，Then 只能看到“当前归入 `generic`”，而不是单独 target

### US-121-3 — Reviewer 需要 verified host ingress 有最小状态语义

作为 **reviewer**，我希望 formal docs 先冻结 `materialized / verified_loaded / degraded / unsupported` 这组状态，这样后续实现不会再把“文件存在”误写成“宿主已读取”。

**验收**：

1. Given 我审阅 `121`，When 我查看 verified host ingress 状态定义，Then 可以明确读到四种最小状态语义
2. Given 我查看 `adapter activate` 的边界，When 对照 `121`，Then 能明确读到它只代表 operator acknowledgement

## 功能需求

| ID | 需求 |
|----|------|
| FR-121-001 | 系统必须在 `program-manifest.yaml > capability_closure_audit` 中新增 `agent-adapter-verified-host-ingress` open cluster |
| FR-121-002 | `121` 必须冻结当前明确适配列表，仅包含 `Claude Code / Codex / Cursor / VS Code / generic` |
| FR-121-003 | `121` 必须明确：只有厂商公开文档能清楚说明默认读取入口与后续可验证路径的目标，才允许进入明确适配列表 |
| FR-121-004 | `121` 必须明确：厂商公开支持不明确的目标不得单列；当前 `TRAE` 必须归入 `generic` |
| FR-121-005 | `121` 必须冻结 verified host ingress 的最小状态语义：`materialized / verified_loaded / degraded / unsupported` |
| FR-121-006 | `121` 必须明确 `adapter activate` 只代表 operator acknowledgement，不得单独满足 `verified_loaded` |
| FR-121-007 | `121` 必须为后续 implementation carrier 冻结每个明确适配目标的默认入口基线 |
| FR-121-008 | `121` 只回写 root truth 与 formal carrier，不在本 work item 中直接实现新的 adapter verify runtime |
| FR-121-009 | `121` 必须为 `120/T00` 从 `pending_root_truth_update` 升格为正式 tranche 提供已满足的 root truth 前置条件 |

## 成功标准

- **SC-121-001**：root manifest 已正式记录 `agent-adapter-verified-host-ingress` open cluster
- **SC-121-002**：仓库里对“明确适配列表”的口径不再把 `TRAE` 单独列为 target
- **SC-121-003**：后续实现者可以直接从 `121` 读出默认入口边界与最小状态语义
- **SC-121-004**：`120/T00` 现在已具备从 `pending_root_truth_update` 升格为正式 follow-up tranche 的 root truth 前置条件

---
related_doc:
  - "program-manifest.yaml"
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "src/ai_sdlc/integrations/agent_target.py"
  - "src/ai_sdlc/integrations/ide_adapter.py"
  - "src/ai_sdlc/cli/adapter_cmd.py"
  - "src/ai_sdlc/cli/run_cmd.py"
