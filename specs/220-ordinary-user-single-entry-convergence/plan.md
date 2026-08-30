---
related_plan: docs/FRAMEWORK_ROADMAP.zh-CN.md
---

# 实施计划：普通用户单入口收敛

**编号**：`220-ordinary-user-single-entry-convergence` | **日期**：2026-08-29
**规格**：`specs/220-ordinary-user-single-entry-convergence/spec.md`
**状态**：已完成；PR #185 已合并，records-only closure 合入主线后生效

## 1. 概述

本计划以一个内部、无持久化的默认展示投影统一 `run/status` 的普通用户输出，再按条件收敛根帮助。它复用
checkpoint、`get_loop_status()`、`build_status_json_surface()`、现有 next actions 与 `RulesLoader`；不复制参赛版
路由器，不改变主线 Runner、Loop、Program Truth 或 status JSON authority。

交付拆成两个可独立回退的产品切片：P2A 先完成高 ROI 的结果/下一步合同，P2B 只在 P2A 稳定且总预算仍不超过
6 人日时隐藏默认 help 的高级命令。Formal、production implementation 和合并分别受独立批准/验证门禁约束。

## 2. 技术背景

**语言/版本**：Python 3.11+
**CLI**：Typer + Rich
**现有真值**：checkpoint/resume、`core.loop_status`、`telemetry.readiness.build_status_json_surface`、RulesLoader
**测试**：pytest、Typer `CliRunner`、Ruff、跨平台 GitHub Actions
**目标平台**：Windows PowerShell/cmd、macOS、Linux
**存储**：无新增；只读现有 `.ai-sdlc/` 状态
**总预算**：4–6 人日；P2A 2–3，P2B 1–2，验证/评审 1

## 3. 宪章与 ROI 检查

| 门禁 | 计划响应 |
|---|---|
| MVP 优先 | P2A 优先；P2B 受预算和稳定性条件约束 |
| 关键路径可验证 | 四类 run 结果、三类 Loop pointer、status 三种模式、隐藏命令兼容均有 CLI 测试 |
| 范围/验证/回退 | P2A/P2B 独立提交；允许文件面和停止条件已冻结 |
| 状态外化 | 不新增状态；只消费现有 truth，摘要不落盘 |
| 产品/框架隔离 | 产品代码仅在 `src/ai_sdlc`，Formal/continuity 在 canonical 目录 |
| 400/50 风险 | 数字只触发复核；投影超过 180 行或无法双消费者复用时降级，不机械拆文件 |
| ROI | 不采用完整五 Loop router、新 advanced 命令或第二状态面 |

## 4. 冻结文件面

### 4.1 P2A 允许范围

```text
src/ai_sdlc/cli/
├── default_summary.py          # 至多一个内部纯展示投影；无写入、无 public schema
├── beginner_guidance.py        # 仅在复用现有 renderer 明显更小时二选一修改
├── run_cmd.py                  # 只接摘要，不重构 Runner/AgentOps
└── commands.py                 # status default/details 分流；JSON 早返回不变

tests/
├── unit/test_default_summary.py
├── integration/test_cli_run.py
└── integration/test_cli_status.py
```

`default_summary.py` 与 `beginner_guidance.py` 不得同时形成两套 projection；实现时二选一。除非 characterization
证明现有 API 无法复用，不得修改 `core/loop_status.py`、`telemetry/readiness.py`、Runner、ProgramService、模型或
持久化层。

### 4.2 P2B 条件范围

```text
src/ai_sdlc/cli/main.py
src/ai_sdlc/__main__.py
tests/unit/test_command_names.py
tests/integration/test_cli_beginner_ux.py
tests/integration/test_cli_module_invocation.py
README.md
```

仅允许调整 Typer `hidden` 元数据、module ASCII fallback 根帮助、可见/可调用矩阵测试和高级命令索引；不得移动命令实现。

### 4.3 最终一致性范围

```text
AGENTS.md
src/ai_sdlc/templates/AGENTS.md.j2
src/ai_sdlc/templates/adapters/**          # 只改确有默认入口漂移的 canonical guidance
docs/**                                    # 只改用户入口/命令索引相关文档
specs/220-ordinary-user-single-entry-convergence/**
.ai-sdlc/state/**
.ai-sdlc/work-items/220-ordinary-user-single-entry-convergence/**
program-manifest.yaml
tests/integration/test_repo_program_manifest.py
```

只有 `rg` 证明文字与新 runtime 不一致时才修改对应 guidance；不做全库措辞美化。

## 5. 设计边界

### 5.1 单一展示投影

内部投影输入为已经存在的 checkpoint、Loop status、status surface 和本次 run outcome，输出只包含：

```text
current_loop
result
next_action
blockers[0..3]
applicable_rules[0..2]
```

投影不得读写 YAML/JSON 之外的新文件，不缓存，不成为 gate/execute authority。run/status 负责收集各自已有上下文，
投影只做确定性优先级、去重和截断。若收集逻辑无法保持单一边界，则优先在调用方保留少量适配，而不是再造 helper。

### 5.2 优先级与真假边界

Next 优先级固定为：本次 run 的 reconcile/adapter/halt/gate 明确信息 > active workitem 的首个
`next_required_action` > 单一 current Loop 的既有 next action > `None`。Blocker 只来自本次失败、malformed/
ambiguous Loop 或 status surface 中 `blocking=true` 的现有 item，不把 advisory 升格为 blocker。

Current Loop 只选择一个已存在未关闭 pointer；无 pointer 时显示 `pipeline/<stage>`。不得在 P2 校验 predecessor
链、创建新的 route result model 或推断 frontend 路径。

Applicable Rules 只使用 checkpoint stage 与现有 `RulesLoader`；最多输出规则名和标题，不读取全文。

### 5.3 兼容策略

- `run` 参数、执行顺序、进度、frontend summary、AgentOps 和 exit code 不变。
- `status --json` 继续走现有 early return；新增 `--details` 只切换人类 renderer。
- 默认 status 改变是本项的产品行为；旧人类详细面由 `--details` 保留。
- 高级命令只隐藏 help，不更改 command object、名称、参数或实现。
- 不按 TTY/非 TTY 分叉默认输出，避免脚本在不同终端得到不同文本；机器调用继续使用既有 `--json`。

## 6. 阶段计划

### Phase 0：Formal freeze（当前阶段）

**目标**：冻结证据、用户合同、兼容矩阵、允许文件面、RED 顺序、预算和停止条件。
**产物**：四份 canonical Formal 文档、manifest/continuity。
**验证**：constraints、program validate/truth、manifest test、diff-check、exact-head 只读 review。
**回退**：只回退 WI220 Formal/continuity，不触碰产品代码。
**出口**：用户明确批准后才能创建 dev 分支和 RED。

### Phase 1：P2A characterization / RED

**目标**：先锁定 run/status/Loop pointer/exit/JSON 基线，再写预期新输出 RED。
**验证**：`test_cli_run.py`、`test_cli_status.py`、新的纯投影 unit tests。
**停止**：若需要修改 Runner、ProgramService、Loop model 或 status JSON builder，回到 Formal 复审。

### Phase 2：P2A minimal GREEN

**目标**：落一个内部纯投影，接入 run/status，新增 `status --details`。
**验证**：正常/open/preflight/halt、single/multiple/malformed/no-loop、default/details/json 矩阵。
**回退**：独立 revert P2A commit。

### Phase 3：P2A adversarial ROI gate

**目标**：检查输出真假、重复实现、实现体积、异常处理与兼容。
**Go**：P2A ≤3 人日、投影 ≤180 行、无新状态/API/schema、定向回归通过。
**No-Go/降级**：超限则只保留 run 五项摘要和 status details 迁移桥，暂停 help 隐藏。

### Phase 4：P2B default help convergence（条件）

**目标**：默认 help 六入口，高级命令直接可达，README 提供分类索引。
**验证**：console/module 根 help allowlist、所有隐藏命令 `--help`、representative advanced argv、command inventory。
**回退**：只恢复 `hidden` 元数据和 README 段落。

### Phase 5：一致性、全量验证与交付

**目标**：只修正真实漂移的 guidance，完成新用户/高级用户/三平台验证与独立评审。
**验证**：focused/full pytest、Ruff、constraints、Program Truth、manifest、diff-check、required checks。
**交付**：按本仓库 PR/Codex review/heartbeat/merge protocol 闭环。

## 7. 关键路径验证矩阵

| 路径 | 主验证 | 不变量 |
|---|---|---|
| run normal/open/halt/preflight | CLI integration + exit assertion | 原执行/上报不变，五项摘要真实 |
| Loop single/multiple/malformed/none | pure projection unit + CLI | fail-closed，无 predecessor router |
| Applicable Rules | unit fixture + CLI | stage-based，≤2，name/title only |
| status default/details | before/after characterization | details 保留旧关键行，default 仅四项 |
| status JSON | parsed deep contract + no-write assertion | shape/语义/exit/只读不变 |
| console/module root help | exact visible allowlist | 两条入口均仅六入口 |
| advanced commands | command inventory + representative `--help` | 所有命令仍可调用 |
| docs/guidance | bounded rg + doc assertions | init/run 默认路径一致 |
| clean new user | init → run E2E | 不要求手动 diagnostics |
| cross platform | GitHub required checks | Windows/macOS/Linux 全绿 |

## 8. 实施顺序与提交策略

1. 提交 Formal 候选并等待用户批准。
2. P2A RED：characterization 与预期输出失败证据。
3. P2A GREEN：单一投影 + run/status；定向 review；独立 commit。
4. 执行 P2A ROI gate；不满足则停止。
5. P2B RED/GREEN：help visibility + README；独立 commit。
6. 只修真实 guidance 漂移，运行 full/cross-platform/independent review，PR 合并。

生产阶段每个切片最多两轮同类对抗整改；第三轮仍需扩大设计时 No-Go。不得把验证失败转化为新治理层。

## 9. 开放决策

| 决策 | 当前状态 | 阻塞阶段 |
|---|---|---|
| Formal 是否批准进入生产实现 | 已批准（2026-08-29） | 已解除 |
| P2B 是否执行 | P2A ROI gate 后自动按冻结条件决定 | Phase 4 |
