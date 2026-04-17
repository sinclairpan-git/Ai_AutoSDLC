---
related_spec: specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md
---

# 158 Plan

## 概览

本计划把 158 定义为一次 truth-only reconciliation。目标不是“把 S9 做绿”，而是基于最新证据重新判断 root cluster `agent-adapter-verified-host-ingress` 是否还能继续保留为 `partial`。如果证据不足，本项的正确结果就是保留缺口并修正文案，而不是强行闭合。

## 技术背景

当前事实面有三层：

1. 适配器真值层：`adapter status` 已给出 `verified_loaded`，证据为 `env:OPENAI_CODEX`，canonical path 为 `AGENTS.md`。
2. 语义冻结层：121 已把 activation 语义降为 acknowledgement；122 已把 verified host ingress 与 canonical path / truth gate 机制冻结。
3. 启动体验层：`python -m ai_sdlc run --dry-run` 在当前会话内会成功返回，但在约 20 秒内缺少进度与中间反馈，闭环仍不足。
4. checkpoint 现实层：当前 `.ai-sdlc/state/checkpoint.yml` 仍绑定历史 work item `specs/001-ai-sdlc-framework` 且处于 `close`，仓库级入口可能因此落到一条很重的历史路径。

158 的工作就是把这三层重新对齐，并决定 root manifest 是否需要收敛。

## 约束

1. 在 fresh dry-run 证据出现前，不允许直接删除 S9/root cluster。
2. 不允许把 `adapter activate` 当成 verified ingress proof。
3. 不允许只凭环境变量存在就宣称“宿主已加载 canonical path 内容”，除非代码路径能证明这件事。
4. 若执行中发现 `run --dry-run` 仍静默，应优先分类和记录，而不是立即进入实现性修复。
5. 本项优先做审计与决议；只有当审计本身要求最小代码修补时，才允许引出后续 work item，而不是在 158 内顺手扩大实现面。

## 项目结构

- [spec.md](/Users/sinclairpan/project/Ai_AutoSDLC/specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md)
- [plan.md](/Users/sinclairpan/project/Ai_AutoSDLC/specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/plan.md)
- [tasks.md](/Users/sinclairpan/project/Ai_AutoSDLC/specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/tasks.md)
- [program-manifest.yaml](/Users/sinclairpan/project/Ai_AutoSDLC/program-manifest.yaml)
- [project-state.yaml](/Users/sinclairpan/project/Ai_AutoSDLC/.ai-sdlc/project/config/project-state.yaml)

## 分阶段计划

### Phase 1: 冻结证据宇宙与 guardrails

整理 010、094、120、121、122 与当前 root manifest 的关系，明确：

- 哪些旧叙述已被替代；
- 哪些验证条件仍然有效；
- 哪些字段只是 acknowledgement；
- 哪些字段属于 machine-verifiable ingress truth。

产出：一份可执行的 evidence matrix，用于约束后续决议。

### Phase 2: Fresh evidence sweep

重新采集并保存：

- `python -m ai_sdlc adapter status --json`
- `python -m ai_sdlc run --dry-run` 的有界观测
- `.ai-sdlc/state/checkpoint.yml` 与当前 active work item 的关系
- 适配器与 run 相关单测 / 集成测试结果
- `python -m ai_sdlc program truth audit`

同时需要检查 `run --dry-run` 的关键路径，判断静默来自：

- adapter pre-gate；
- governance truth gate；
- runner 自身进入无输出路径；
- 历史 checkpoint 导致的重路径或状态装配；
- 或测试 / 终端环境造成的可见性差异。

产出：一份 fresh evidence bundle 与 startup classification。

### Phase 3: Root reconciliation decision

基于 Phase 2 结果作出决议：

1. 若 ingress truth 与 startup behavior 均具备闭环证据，则关闭或移除 root cluster。
2. 若 ingress truth 已 verified，但 startup behavior 仍无闭环，则保留 `partial`，并把 root summary 改写成“host ingress 已证实，startup observability 仍待修复”的当前态。

此阶段必须同步吸收 UX 合议建议，避免再出现“字段是绿的，但操作者不知道当前到底可不可以继续”的界面语义。

### Phase 4: Close readiness

在 root manifest 决议后刷新 truth，并运行 close-check。若仍有遗留缺陷，则把 158 保持打开状态，直到缺口被显式挂接到后续 work item。

## 验证策略

| 验证项 | 命令 | 通过条件 |
| --- | --- | --- |
| 适配器真值 | `python -m ai_sdlc adapter status --json` | 关键字段可重复得到，且与人工摘要一致 |
| 启动入口观测 | `python -m ai_sdlc run --dry-run` | 能被明确归类为成功且可观察、成功但静默、失败或静默待修复之一 |
| 回归测试 | `uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py` | 相关测试通过，或失败与当前缺口一致且已解释 |
| 项目真值 | `python -m ai_sdlc program truth audit` | truth audit 与 root 决议一致 |
| Work item 完整性 | `python -m ai_sdlc workitem close-check --wi specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline` | close-check 无阻断项，或阻断项已被保留为未关闭理由 |

## 风险

1. `run --dry-run` 的静默可能是平台差异，不一定是治理逻辑本身错误。
2. `env:OPENAI_CODEX` 能证明当前宿主类型，但未必自动证明 canonical content 已被宿主读取。
3. 历史 checkpoint 若未与当前 work item 对齐，仓库级入口观测可能持续污染 158 的判断。
4. root manifest 若只修文案不修判定依据，仍会重复旧问题。

## 决策规则

本项执行时必须遵循以下规则：

1. 证据优先于历史叙事。
2. 当前观测优先于旧的保守摘要。
3. 不能把“verified ingress”外推为“startup path fully proven”。
4. 不能为了关闭 work item 而缩减证据标准。

---

frontend_evidence_class: "framework_capability"
