# 功能规格：Agent Adapter Activation Contract

**功能编号**：`010-agent-adapter-activation-contract`  
**创建日期**：2026-04-02  
**状态**：已冻结（formal baseline）  
**输入**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../src/ai_sdlc/integrations/ide_adapter.py`](../../src/ai_sdlc/integrations/ide_adapter.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)

> 口径：本 work item 不是修一个“识别顺序小 bug”，而是把框架入口适配从“文件注入型软提示”升级为“AI 代理入口选择 + activation handshake + activation state + activation gate”的正式合同。若该合同缺位，`init / dry-run` 成功也不能代表框架已真正接管开发链路。

## 问题定义

当前框架存在三类连续缺口：

- `workitem / run` 等入口把 IDE adapter 文件写入视为接入完成，却没有证明目标代理真的采纳了约束
- `VS Code + Codex`、`VS Code + Claude Code` 这类混合宿主场景中，当前实现把编辑器宿主误当成约束消费入口，导致 adapter 安装目标错误
- 即使 `.codex/AI-SDLC.md` 已被代理读取，且代理执行过 `ai-sdlc run --dry-run`，仍可能继续按普通 coding 路径开发，没有真正进入 framework 约束链

因此，本 work item 要解决的不是“再多写一份 adapter 文件”，而是：

- 选择谁才是实际消费约束的 AI 代理入口
- 如何判断当前只是 `installed`，还是已经 `activated`
- 如何在未激活时阻断或降级，而不是误报“框架已接管”

## 范围

- **覆盖**：
  - 定义 `Editor Host` 与 `Agent Target` 的分离模型
  - 定义 `init` 阶段的 AI 代理入口选择流程
  - 锁定固定可选项：`Claude Code / Codex / Cursor / VS Code / 其他-通用`
  - 定义 adapter 的 activation state、activation evidence 与 support tier
  - 定义 `adapter installed != governance activated` 的正式状态语义
  - 定义 `adapter activate / status / activation gate` 的产品合同
  - 定义 mixed host 场景下的正确判定方式，例如 `VS Code + Codex` 应选 `Codex`
  - 定义旧项目从“只有 adapter_applied 元数据”迁移到新状态模型的回写规则
  - 为后续 CLI、adapter 模板、status/run/doctor、测试与用户文档改造提供 canonical formal baseline
- **不覆盖**：
  - 与第三方插件做原生 API 级双向集成
  - 在本 work item 中直接完成所有 adapter 运行时实现与 UI 交互实现
  - 为每个编辑器宿主组合枚举单独选项，例如“VS Code + Codex”
  - 将 `Codex / Claude Code / Cursor` 立即提升为强验证级原生接入
  - 改写后续前端治理、UI Kernel 或其他非入口能力的主规则体系

## 已锁定决策

- 选择的是**AI 代理入口**，不是编辑器宿主
- `VS Code + Codex 插件` 选择 `Codex`；`VS Code + Claude Code 插件` 选择 `Claude Code`
- `init` 的自动探测只负责默认聚焦，不自动确认
- 交互式选择列表固定为：
  - `Claude Code`
  - `Codex`
  - `Cursor`
  - `VS Code`
  - `其他-通用`
- 非交互环境不能卡住等待选择，必须优先接受显式参数，否则走 deterministic fallback 并打印说明
- `adapter installed != governance activated`
- 不能再把“adapter 文件存在”“adapter 文件被读到”“执行过 run --dry-run”视为等价激活
- activation 至少要区分 `selected / installed / acknowledged / activated`
- 若无法证明 activation，则框架只能宣称“已安装/已确认”，不能宣称“已接管”
- 对 file-based agent 的当前最高能力应以 `acknowledged` 或等价软激活为上限；只有未来具备可验证回执时，才允许升级到更高 support tier

## 用户故事与验收

### US-010-1 — Operator 需要在混合宿主场景中选对 AI 代理入口

作为**operator**，我希望 `ai-sdlc init` 询问的是“当前实际用于聊天开发的 AI 代理入口”，而不是笼统问我使用的 IDE，以便在 `VS Code + Codex`、`VS Code + Claude Code` 这类场景下把约束安装到正确目标上。

**验收**：

1. Given 项目根存在 `.vscode` 与 `.codex` 痕迹，When 我运行 `ai-sdlc init`，Then 默认聚焦应落在 `Codex`，而不是自动把 `VS Code` 视为最终 adapter target  
2. Given 我在交互式选择器中按上下键并回车确认，When `init` 完成，Then 项目配置中记录的是我确认的 `agent_target`，而不是仅记录宿主 IDE  
3. Given 我在 CI 或非交互终端中运行 `init`，When 我显式传入 `--agent-target codex`，Then 命令不应进入交互等待，而应直接写入确定的 target

### US-010-2 — Framework Maintainer 需要正式区分 installed 与 activated

作为**框架维护者**，我希望框架在状态、日志和门禁上正式区分 `selected / installed / acknowledged / activated`，以便不再把 adapter 文件写入误报成“框架已接管”。

**验收**：

1. Given 项目里只存在 `.codex/AI-SDLC.md` 且已写入 adapter 元数据，When 我查看 adapter status，Then 框架只能表述为 `installed` 或等价状态，不能表述为已激活  
2. Given 代理已经完成显式 activation handshake，When 我查看 status，Then 可以看到 activation state、support tier 与 evidence 信息  
3. Given 当前只有 `installed` 而没有 `activated`，When 我运行后续标准开发入口，Then 框架必须阻断或显式降级，而不是继续给出“可以开始受控开发”的误导性语义

### US-010-3 — Reviewer 需要入口层有单一、可验证的接管合同

作为**reviewer**，我希望能在 formal docs 中读到清晰的 activation contract、activation gate 与 support tier 边界，以便后续实现不会再次退化成“再多写一份 Markdown 提示文件”。

**验收**：

1. Given 我审阅 `010` formal docs，When 我检查 activation 设计，Then 可以明确看到 `adapter file present`、`agent acknowledged`、`governance activated` 不是同一件事  
2. Given 我审阅 mixed host 和 legacy 项目迁移设计，When 我检查该方案，Then 不会把 compatibility fallback 或 legacy adapter 元数据理解成“第二套规则系统”  
3. Given 后续实现完成，When 我执行针对 mixed host、installed-only、non-interactive 的回归测试，Then 可以稳定复现并验证 `010` 中定义的状态与门禁行为

## 功能需求

### Selection And Target Model

| ID | 需求 |
|----|------|
| FR-010-001 | 系统必须把 `Editor Host` 与 `Agent Target` 作为不同对象建模，选择目标是 `Agent Target`，不是编辑器宿主 |
| FR-010-002 | 系统必须在 `init` 阶段提供交互式 AI 代理入口选择器，固定可选项为 `Claude Code / Codex / Cursor / VS Code / 其他-通用` |
| FR-010-003 | 自动探测只能用于默认聚焦，不得自动确认最终 target |
| FR-010-004 | 系统必须支持显式参数指定 agent target，用于非交互环境或 operator 强制选择 |
| FR-010-005 | 对 mixed host 场景，系统必须保证“插件代理优先于编辑器宿主”，例如 `VS Code + Codex` 最终 target 为 `codex` |

### Activation State And Evidence

| ID | 需求 |
|----|------|
| FR-010-006 | 系统必须引入正式 activation state，至少区分 `selected / installed / acknowledged / activated` |
| FR-010-007 | 仅安装 adapter 文件时，系统只能进入 `installed` 或等价状态，不得提升为 `acknowledged` 或 `activated` |
| FR-010-008 | 系统必须支持显式 activation handshake，并将其结果落盘为机器可读取状态，而不是只存在于对话中 |
| FR-010-009 | 系统必须记录 activation evidence、source、timestamp 与 support tier，以支撑后续状态展示与门禁判定 |
| FR-010-010 | 在当前 file-based agent 能力下，系统必须允许 `acknowledged` 与 `verified` 分层，避免把软提示接入冒充为强验证接入 |

### CLI Surfaces And User Guidance

| ID | 需求 |
|----|------|
| FR-010-011 | 系统必须提供显式的 adapter 管理命令面，至少覆盖 `select / status / activate` 或等价能力 |
| FR-010-012 | `status`、`doctor`、`run --dry-run` 等入口必须展示当前 `agent_target`、activation state 与 support tier，而不是只展示 `adapter_applied` |
| FR-010-013 | adapter 模板文件必须从“先执行 run --dry-run”重写为“先完成 activation，再进入 run --dry-run” |
| FR-010-014 | 若项目未完成 activation，系统的提示语不得再宣称“框架已接管开发链路” |

### Activation Gate And Execution Policy

| ID | 需求 |
|----|------|
| FR-010-015 | 系统必须定义 activation gate，决定哪些命令在 `installed-only` 状态下只能降级、哪些必须阻断 |
| FR-010-016 | 在未达到最低 activation 前，系统不得把当前项目标记为“适合按框架标准流程继续开发” |
| FR-010-017 | activation gate 的判定必须基于 `agent_target + activation state + support tier + evidence`，而不是基于 adapter 文件是否存在 |

### Backward Compatibility And Migration

| ID | 需求 |
|----|------|
| FR-010-018 | 系统必须为已存在 `detected_ide / adapter_applied / adapter_version / adapter_applied_at` 的项目提供迁移路径 |
| FR-010-019 | 对旧项目的迁移默认只能把历史 adapter 接入提升为 `installed`，不得直接推断为 `activated` |
| FR-010-020 | 系统必须保留 deterministic fallback，确保未指定 target 的非交互场景仍可执行，但同时显式暴露其推断来源与可信度 |

### Verification And Regression

| ID | 需求 |
|----|------|
| FR-010-021 | 系统必须补 mixed host 场景测试，覆盖 `.vscode + .codex`、`.vscode + .claude` 等组合 |
| FR-010-022 | 系统必须补 `installed != activated` 的状态与文案回归测试 |
| FR-010-023 | 系统必须补非交互 `--agent-target` 与 fallback 行为测试 |
| FR-010-024 | 系统必须补 activation gate 的正反向测试，证明未激活时不会误报“已接管” |

## 关键实体

- **Editor Host**：外层编辑器宿主，例如 `vscode`、`cursor` 或无宿主环境；用于记录运行环境，但不决定最终约束消费入口
- **Agent Target**：当前实际消费框架约束的 AI 代理入口，例如 `claude_code`、`codex`、`cursor`、`vscode`、`generic`
- **Adapter Selection**：记录 operator 最终确认的目标、自动探测候选、选择来源、是否交互确认等信息
- **Activation State**：记录当前项目在 `selected / installed / acknowledged / activated` 生命周期中的位置
- **Activation Evidence**：记录 activation 的来源、时间、证据、支持等级与可信度
- **Support Tier**：区分 `soft_installed`、`acknowledged_activation`、`verified_activation` 或等价层级，避免把软提示接入误报成强验证接入
- **Activation Gate Policy**：定义在不同 activation state / support tier 下，CLI 各入口是允许、降级还是阻断

## 成功标准

- **SC-010-001**：在 `.vscode + .codex`、`.vscode + .claude` 的回归夹具中，最终 `agent_target` 必须稳定落到插件代理，而不是宿主 IDE  
- **SC-010-002**：在仅有 adapter 文件与旧版 `adapter_applied` 元数据的项目上，`status / run --dry-run / init` 不得继续宣称“框架已接管”  
- **SC-010-003**：operator 能在交互式 `init` 中通过固定五项列表完成确认，并在非交互场景中通过显式参数稳定复现同一结果  
- **SC-010-004**：adapter 模板、CLI 状态面与 activation gate 三者对“installed / acknowledged / activated”的表述保持单一真值  
- **SC-010-005**：旧项目迁移后默认进入 `installed` 或等价软接入状态，不会因历史 `.codex/AI-SDLC.md` 或 `run --dry-run` 记录被误推断为 `activated`
