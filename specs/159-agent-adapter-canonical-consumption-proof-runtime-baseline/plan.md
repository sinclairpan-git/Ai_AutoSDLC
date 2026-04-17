# 实施计划：Agent Adapter Canonical Consumption Proof Runtime Baseline

**编号**：`159-agent-adapter-canonical-consumption-proof-runtime-baseline` | **日期**：2026-04-18 | **规格**：specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline/spec.md

## 概述

为 IDE adapter 增加一个与 `adapter_ingress_state` 平行的 canonical content consumption proof 维度。runtime 通过计算 canonical 文件 `sha256:` 摘要，并校验宿主显式提供的 digest/path 环境变量，独立记录 canonical consumption truth；现有 verified ingress 逻辑保持不变。

## 技术背景

**语言/版本**：Python 3.11+
**主要依赖**：Typer CLI、Pydantic project config、现有 `ide_adapter` integration
**存储**：`.ai-sdlc/project/config/project-config.yaml`
**测试**：`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`
**目标平台**：Cursor / VS Code / Codex / Claude Code adapter governance surface
**约束**：
- 不更改 `adapter_ingress_state` / `adapter_verification_result` 的现有语义
- 不宣称 Codex 或其他宿主今天已经原生输出该 digest proof
- proof 必须 machine-verifiable，不能退回人工声明

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| machine-verifiable truth only | proof 只接受 digest/path 显式匹配，不把宿主类型 env 当成 canonical 内容消费证明 |
| docs/code/test 同步 | 先冻结 159 formal docs，再以 TDD 补测试和实现，最后回写 execution log |

## 项目结构

### 文档结构

```text
specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/models/project.py
src/ai_sdlc/integrations/ide_adapter.py
tests/unit/test_ide_adapter.py
tests/integration/test_cli_adapter.py
```

## 阶段计划

### Phase 0：研究与决策冻结

**目标**：冻结 canonical consumption proof 协议与状态字段，不让 159 再漂回“宿主类型推断=内容消费证明”
**产物**：spec.md / plan.md / tasks.md / task-execution-log.md
**验证方式**：文档对账 + 代码面搜索
**回退方式**：仅编辑 159 work item 文档，不触碰 runtime 代码

### Phase 1：测试先行锁定协议

**目标**：先以单元/CLI 集成测试固定 digest 缺失、匹配、不匹配语义
**产物**：失败测试 + 明确的新 payload 字段断言
**验证方式**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -q`
**回退方式**：撤回新增测试并重新收敛协议

### Phase 2：runtime 实现与持久化

**目标**：在 project config 与 `ide_adapter` 中实现 canonical digest/proof 判定与输出
**产物**：project config 字段、digest 计算 helper、adapter governance payload 扩展
**验证方式**：同上聚焦 pytest
**回退方式**：回退新增字段与判定 helper，恢复旧 surface

### Phase 3：真值同步与收口

**目标**：同步 work item 文档、program truth、close-check 记录，为后续 cluster 收口留证据
**产物**：更新后的 task-execution-log、program truth sync/close-check 输出
**验证方式**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc workitem close-check --wi specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline`
**回退方式**：保留实现，补修文档/manifest 对齐问题

## 工作流计划

### 工作流 A：canonical digest proof runtime

**范围**：project config、adapter runtime、adapter status JSON
**影响范围**：adapter governance surface、status telemetry surface、close-check 可观察字段
**验证方式**：unit + integration pytest；program truth sync；workitem close-check
**回退方式**：移除新增字段与 proof helper，恢复到仅有 ingress truth 的状态

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 宿主未来若原生输出 proof 是否要兼容新的 env key | 开放 | 后续扩展 |
| verify constraints 是否要把 canonical consumption proof 纳入 release gate | 后续工作项处理 | 不阻塞 159 runtime baseline |

## 实施顺序建议

1. 先冻结 159 formal docs，清掉模板占位与错误继承内容。
2. 先写失败测试锁定 proof 协议，再补最小实现。
3. 跑聚焦验证与 truth sync / close-check，并把结果回填 execution log。
