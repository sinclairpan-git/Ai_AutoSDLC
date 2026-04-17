# 任务分解：Agent Adapter Canonical Consumption Proof Runtime Baseline

**编号**：`159-agent-adapter-canonical-consumption-proof-runtime-baseline` | **日期**：2026-04-18
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal docs freeze
Batch 2: test-first runtime proof implementation
Batch 3: truth sync and closure evidence
```

---

## Batch 1：formal docs freeze

### Task 1.1 冻结 canonical consumption proof 正式真值

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. 159 formal docs 不再保留模板占位或旧 formal 模板遗留内容
  2. spec / plan / tasks 明确区分 ingress truth 与 canonical consumption truth
- **验证**：文档对账 + 搜索占位/旧模板遗留词应返回空结果

## Batch 2：test-first runtime proof implementation

### Task 2.1 先写失败测试锁定 proof 协议

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：tests/unit/test_ide_adapter.py, tests/integration/test_cli_adapter.py
- **可并行**：否
- **验收标准**：
  1. 测试覆盖 digest 缺失、匹配、不匹配场景
  2. 测试明确断言 ingress truth 不因 canonical proof 缺失而变化
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -q`

### Task 2.2 实现 canonical digest/proof runtime

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/models/project.py, src/ai_sdlc/integrations/ide_adapter.py
- **可并行**：否
- **验收标准**：
  1. project config 可持久化 canonical digest / result / evidence / consumed_at
  2. adapter governance surface 输出新增字段，且旧 ingress 字段保持兼容
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -q`

## Batch 3：truth sync and closure evidence

### Task 3.1 同步 program/workitem 真值并归档

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：task-execution-log.md, program-manifest.yaml, .ai-sdlc/project/config/project-state.yaml
- **可并行**：否
- **验收标准**：
  1. 159 执行日志回填真实验证命令与结果
  2. `program truth sync` 与 `workitem close-check` 可在当前 work item 上执行
- **验证**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc workitem close-check --wi specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline`
