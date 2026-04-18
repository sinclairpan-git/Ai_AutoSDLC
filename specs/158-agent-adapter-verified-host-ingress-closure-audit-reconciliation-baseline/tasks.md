---
related_spec: specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md
related_plan: specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/plan.md
---

# 158 Tasks

## 批次策略

### Batch 1: 冻结 S9 证据宇宙

- 对齐 010 / 094 / 120 / 121 / 122 与 root manifest 的现状。
- 明确哪些字段是 acknowledgement，哪些字段是 verified truth。
- 形成 fail-closed guardrails，禁止先删 cluster 再补证据。

### Batch 2: 复测现场事实

- 重新采集 adapter status。
- 对 `run --dry-run` 做有界观测并分类。
- 运行适配器相关测试与 truth audit。

### Batch 3: Root reconciliation

- 若证据足够，关闭或移除 root cluster。
- 若证据不足，保留 `partial` 并更新摘要、缺口与后续动作。

### Batch 4: Close readiness

- 运行 close-check。
- 根据结果决定 158 是否可关闭，或显式保留为未闭合状态。

## 执行护栏

1. [x] 不得在没有 fresh dry-run 证据前移除 `agent-adapter-verified-host-ingress`。
2. [x] 不得把 `adapter activate` 视为 verified proof。
3. [x] 不得仅凭 `env:OPENAI_CODEX` 推断 canonical path 内容已被宿主读取，除非代码路径能给出 machine-verifiable 支撑。
4. [x] 不得把“长时间静默后完成”笼统记录成“dry-run 通过”；必须单独说明可观察性缺口。
5. [x] root manifest、adapter status、121/122 三者必须同语义对齐。

## 任务清单

### Batch 1

- [x] T11 证据宇宙冻结
  - 优先级: P0
  - 依赖: 无
  - 文件: `program-manifest.yaml`, `specs/010-*`, `specs/094-*`, `specs/120-*`, `specs/121-*`, `specs/122-*`
  - 验收: 产出一份 S9 现状矩阵，能指出哪些 root summary 语句已过期，哪些约束仍有效
  - 验证: 人工比对 root summary 与 121/122 的冻结语义

- [x] T12 合议 guardrails 固化
  - 优先级: P0
  - 依赖: T11
  - 文件: `specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md`, `specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/plan.md`, `specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/tasks.md`
  - 验收: 文档明确 fail-closed 规则、UX 约束、以及“closure 不可预设”的范围边界
  - 验证: 文档审查通过

### Batch 2

- [x] T21 适配器真值复测
  - 优先级: P0
  - 依赖: T12
  - 文件: `src/ai_sdlc/integrations/ide_adapter.py`, `src/ai_sdlc/cli/adapter_cmd.py`, 相关证据记录
  - 验收: fresh `adapter status --json` 被采集并解释，关键字段与当前实现对应关系清晰
  - 验证: `python -m ai_sdlc adapter status --json`

- [x] T22 启动入口可观察性分类
  - 优先级: P0
  - 依赖: T12
  - 文件: `src/ai_sdlc/cli/run_cmd.py`, `.ai-sdlc/state/checkpoint.yml`, 相关证据记录
  - 验收: `run --dry-run` 被明确分类为成功且可观察、成功但静默、失败或静默待修复之一；若存在长时间静默，必须指出观测边界、原因归属，以及历史 checkpoint 是否是主要干扰因素
  - 验证: `python -m ai_sdlc run --dry-run`

- [x] T23 相关回归验证
  - 优先级: P1
  - 依赖: T21, T22
  - 文件: `tests/unit/test_ide_adapter.py`, `tests/integration/test_cli_adapter.py`, `tests/integration/test_cli_init.py`, `tests/integration/test_cli_run.py`
  - 验收: 相关测试结果可解释，且与 T21/T22 的结论一致
  - 验证: `uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py`

- [x] T24 项目真值刷新
  - 优先级: P1
  - 依赖: T21, T22
  - 文件: `program-manifest.yaml`, truth audit 输出
  - 验收: truth audit 的现状与采集到的 ingress/startup 事实相符
  - 验证: `python -m ai_sdlc program truth audit`

### Batch 3

- [x] T31 闭合路径判定（由 163 fresh close sweep 复核后完成）
  - 优先级: P0
  - 依赖: T21, T22, T24
  - 文件: `program-manifest.yaml`
  - 验收: 只有当 verified host ingress 与 canonical content consumption proof 都具备足够证据时，才允许移除或关闭 root cluster；`163` 已据此执行 root cluster removal
  - 验证: root manifest diff 可由 evidence bundle 支撑

- [x] T32 保守路径判定（本批选中）
  - 优先级: P0
  - 依赖: T21, T22, T24
  - 文件: `program-manifest.yaml`
  - 验收: 若 T31 条件不满足，则保留 `partial`，并更新摘要为“verified host ingress 已成立，但 canonical content actual consumption proof 仍缺”的当前态
  - 验证: root manifest diff 不再包含陈旧叙述

- [x] T33 UX 语义对齐
  - 优先级: P1
  - 依赖: T31 或 T32
  - 文件: root summary、相关说明文档、必要时后续 work item
  - 验收: 操作者能区分 acknowledgement、verified ingress、canonical consumption proof、close readiness 四个维度
  - 验证: 人工 review root summary 与 CLI 输出说明

### Batch 4

- [x] T41 关闭前检查
  - 优先级: P0
  - 依赖: T31 或 T32
  - 文件: `specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/`
  - 验收: close-check 输出与本项最终状态一致
  - 验证: `python -m ai_sdlc workitem close-check --wi specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline`

- [x] T42 未闭合缺口显式化
  - 优先级: P0
  - 依赖: T41
  - 文件: `program-manifest.yaml`, 必要时新增 follow-up work item
  - 验收: 若 158 不能关闭，阻断项被明确保留且可继续跟踪
  - 验证: 人工检查 root cluster / follow-up 记录完整

## 完成条件

满足以下条件前，不得宣布 158 完成：

1. fresh evidence 已重新采集；
2. root cluster 已根据证据作出 closure 或 partial 决议；
3. `run --dry-run` 的现实表现已有明确分类；
4. close-check 与最终结论一致。

---

frontend_evidence_class: "framework_capability"
