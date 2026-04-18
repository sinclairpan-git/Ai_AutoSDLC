# 158 Agent Adapter Verified Host Ingress Closure Audit Reconciliation Baseline

## 背景

`program-manifest.yaml` 当前仍将 `agent-adapter-verified-host-ingress` 保留为 `partial`，并把缺口归因于“未对齐 vendor default entry / 缺少 machine-verifiable host ingress runtime / TRAE generic”。但近期事实源已发生变化：

1. `python -m ai_sdlc adapter status` 当前返回：
   - `adapter_ingress_state=verified_loaded`
   - `governance_activation_state=verified_loaded`
   - `adapter_verification_evidence=env:OPENAI_CODEX`
   - `adapter_canonical_path=AGENTS.md`
2. `specs/121-*` 已把 `adapter activate` 降级为 acknowledgement-only，不再把人工确认当作 verified proof。
3. `specs/122-*` 已明确 canonical path / auto verify / truth gate，并接受 `run --dry-run` 在 `materialized` 或 `degraded` 语义下继续，但不把它当成治理激活证明。
4. 2026-04-18 fresh 现场观测下，`python -m ai_sdlc run --dry-run` 当前会先输出 `Stage close: running (dry-run)`，随后以 `Stage close: RETRY` / `Dry-run completed with open gates` 结束；因此它已具备阶段级可观察结论，但不能被表述成“治理已闭环”或“close gate 已通过”。
5. 当前 `.ai-sdlc/state/checkpoint.yml` 已切换到 `specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline`，且 `current_stage=close`；因此仓库级 `run --dry-run` / `status` 观测到的行为，反映的是后续 canonical consumption proof carrier 的 close-stage 现场，而不再是 158 初始审计时的历史 `001` 路径。

因此，下一项工作不能直接宣称 S9 闭合；必须先做一次 fail-closed 的 reconciliation：重新核对 root cluster、121/122 的冻结语义、适配器实际输出，以及启动入口的可观察行为，再决定是关闭 root cluster，还是保留 `partial` 并修正文案与后续缺口。

## 问题陈述

当前系统在“适配器接入真值已 verified”与“canonical content 仍缺消费证明 / close gate 仍为 RETRY”之间存在解释张力：

- 从接入真值看，Codex host ingress 已有 machine-verifiable 证据。
- 从启动体验看，`run --dry-run` 当前已能输出阶段运行与阶段结论，但结果仍是 `close: RETRY`，因此不能被误写为 close-ready。
- 从 root manifest 文案看，旧摘要仍停留在 010/094 时期的保守叙述，没有吸收 121/122 的真值冻结与当前 `adapter status` 输出。

若直接删除 S9/root cluster，会把“已验证的 host ingress”与“未证明的 dry-run startup behavior”混为一谈。若继续保留旧摘要，又会低估当前已 materialized 的 verified host ingress 能力。

## 目标

本 work item 的目标是：

1. 以 machine-verifiable evidence 重新审计 `agent-adapter-verified-host-ingress` root cluster。
2. 明确区分以下三件事：
   - host ingress 是否 verified_loaded；
   - `adapter activate` 是否只是 acknowledgement；
   - `run --dry-run` 是否具备可观察、可终止、可解释的启动入口行为。
3. 在 root manifest 中做 truth-preserving reconciliation：
   - 若证据足够，允许关闭或移除该 root cluster。
   - 若证据不足，必须保留 `partial`，但更新摘要、缺口与后续动作，不能继续沿用陈旧叙述。
4. 将 UX 合议结论固化为约束：用户不能面对“真值已绿但入口静默挂起”的混乱反馈。

## 非目标

本 work item 不做以下事情：

1. 不预设 S9 一定关闭。
2. 不把 `adapter activate` 升格为 verified proof。
3. 不仅凭 `env:OPENAI_CODEX` 就推断“宿主已读取 canonical path 内容”，除非当前实现能提供额外 machine-verifiable 证据。
4. 不以文档改写掩盖 `run --dry-run` 的长时间静默或可观察性问题。
5. 不扩展新的 IDE vendor 适配范围；本项只处理当前 Codex canonical path 与启动真值闭环。

## 输入与事实源

本项执行时必须以以下输入为准：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/010-agent-adapter-activation-contract/`
- `specs/094-stage0-init-dual-path-project-onboarding-baseline/`
- `specs/120-open-capability-tranche-backlog-baseline/`
- `specs/121-agent-adapter-verified-host-ingress-truth-baseline/`
- `specs/122-agent-adapter-verified-host-ingress-runtime-baseline/`
- `src/ai_sdlc/integrations/ide_adapter.py`
- `src/ai_sdlc/cli/adapter_cmd.py`
- `src/ai_sdlc/cli/run_cmd.py`
- `tests/unit/test_ide_adapter.py`
- `tests/integration/test_cli_adapter.py`
- `tests/integration/test_cli_init.py`
- `tests/integration/test_cli_run.py`
- `.ai-sdlc/state/checkpoint.yml`
- 新鲜采集的 `python -m ai_sdlc adapter status` / `python -m ai_sdlc adapter status --json`
- 新鲜采集的 `python -m ai_sdlc run --dry-run` 有界观测结果
- `python -m ai_sdlc program truth audit`

## 功能需求

### FR-158-001 真值冻结

在做任何 root cluster 状态变更前，必须先冻结当前证据宇宙，明确：

- 哪些事实已被 121/122 改写；
- 哪些 root manifest 叙述已过期；
- 哪些行为仍缺 fresh evidence。

### FR-158-002 适配器状态复测

必须重新采集 adapter 状态，并确认以下字段的一致性：

- `agent_target`
- `adapter_applied`
- `adapter_activation_state`
- `adapter_support_tier`
- `adapter_ingress_state`
- `adapter_verification_result`
- `adapter_verification_evidence`
- `adapter_canonical_path`
- `governance_activation_state`
- `governance_activation_verifiable`

### FR-158-003 启动入口可观察性审计

必须对 `python -m ai_sdlc run --dry-run` 做一次有界观测，不允许把“长时间静默后完成”笼统表述成“已经通过”。执行结果至少要被归类为以下之一：

1. 明确成功且可观察，或成功但存在可解释的静默缺口；
2. 明确失败并可解释；
3. 仍静默/阻塞，需要后续缺陷 work item 继续处理。

同时必须说明该结果是否受到历史 checkpoint 路径影响，避免把“checkpoint 负载”误判为“adapter ingress 退化”。

### FR-158-004 Root Cluster Reconciliation

必须基于 fresh evidence 在 root manifest 中作出二选一决策：

1. 关闭或移除 `agent-adapter-verified-host-ingress`；
2. 保留 `partial`，并把摘要改写为符合 121/122 与现场复测事实的版本。

不允许第三种状态，即继续保留过时摘要而不解释当前 verified_loaded 事实。

### FR-158-005 UX Guardrail 固化

执行结果必须把以下 UX 约束落地到文档或后续动作：

- `adapter status` 的 acknowledgement 字段不得掩盖 verified ingress 真值。
- `run --dry-run` 不得以静默行为向操作者制造“像是通过又像是挂起”的歧义。
- 若 root cluster 不能关闭，必须明确给出操作者仍缺哪一条证据。

## 成功标准

### SC-158-001

存在一份基于 fresh evidence 的 reconciliation 结论，且该结论可解释为什么 root cluster 被关闭或保留。

### SC-158-002

`adapter status` 与 root manifest 的叙述不再互相矛盾。

### SC-158-003

`run --dry-run` 的现场表现被明确记录为成功但静默、成功且可观察、失败或静默待修复之一，不再用模糊语言表述。

### SC-158-004

任何 `verified_loaded` 结论都只建立在 machine-verifiable evidence 上，而不是 operator acknowledgement。

## 验证

至少执行并归档以下验证：

1. `python -m ai_sdlc adapter status --json`
2. `python -m ai_sdlc run --dry-run` 的有界观测记录
3. `uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py`
4. `python -m ai_sdlc program truth audit`
5. `python -m ai_sdlc workitem close-check --wi specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline`

## 交付物

本项至少产出：

1. 一份更新后的 root manifest 决议，或一份明确说明“暂不关闭”的 root summary 修正。
2. 一份对 `run --dry-run` 可观察行为的证据记录，至少说明“成功但静默”是否仍构成未闭环缺口。
3. 一份与 121/122 保持一致的 ingress truth 说明。
4. 必要时新增后续缺陷或改进行动项，但不得伪装为本项已关闭。

## 完成定义

只有在以下条件满足时，本项才可关闭：

1. root cluster 的最终状态已被证据化决议；
2. `adapter status`、root manifest、121/122 之间无语义冲突；
3. `run --dry-run` 的现实行为已有明确归类；
4. 若仍存在缺口，缺口已被显式保留，而不是被文档性掩盖。

---

frontend_evidence_class: "framework_capability"
