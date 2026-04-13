---
related_doc:
  - "program-manifest.yaml"
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
---
# 任务分解：Agent Adapter Verified Host Ingress Runtime Baseline

**编号**：`122-agent-adapter-verified-host-ingress-runtime-baseline` | **日期**：2026-04-13
**来源**：`spec.md` + `plan.md`

---

## 分批策略

```text
Batch 1: red fixtures
Batch 2: state + canonical path runtime
Batch 3: auto verify + run gate
Batch 4: closeout
```

---

## Batch 1：Red fixtures

### Task 1.1 锁定 target/path/state 红灯夹具

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`tests/unit/test_ide_adapter.py`, `tests/integration/test_cli_adapter.py`, `tests/integration/test_cli_init.py`, `tests/integration/test_cli_run.py`
- **可并行**：否
- **验收标准**：
  1. 测试锁定 `TRAE` 不单列 target
  2. 测试锁定 canonical path 改为 `.claude/CLAUDE.md`、`AGENTS.md`、`.cursor/rules/ai-sdlc.mdc`、`.github/copilot-instructions.md`
  3. 测试锁定 `materialized / verified_loaded / degraded / unsupported` 状态面
  4. 测试锁定 `run` 不再依赖 `adapter activate`
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py -q`

## Batch 2：State + canonical path runtime

### Task 2.1 重构 adapter persisted state

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`src/ai_sdlc/models/project.py`, `src/ai_sdlc/integrations/ide_adapter.py`
- **可并行**：否
- **验收标准**：
  1. persisted config 可表达 ingress state、verification result、degrade reason 与 evidence 摘要
  2. 旧 `installed / acknowledged / activated` 语义不会再被误读成 verified host ingress
  3. backward compatibility 不会破坏现有项目加载
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -q`

### Task 2.2 切换 canonical path materialization

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/integrations/agent_target.py`, `src/ai_sdlc/integrations/ide_adapter.py`, `src/ai_sdlc/adapters/*`
- **可并行**：否
- **验收标准**：
  1. 明确适配目标只写入 `122` 冻结的 canonical path
  2. `generic` 仍只写 hint surface
  3. `TRAE` 不新增任何单独 path/materializer
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_init.py -q`

## Batch 3：Auto verify + run gate

### Task 3.1 实现 auto verify surface

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`src/ai_sdlc/integrations/ide_adapter.py`, `src/ai_sdlc/cli/adapter_cmd.py`
- **可并行**：否
- **验收标准**：
  1. `init / adapter select` 默认触发 verify 或诚实降级
  2. `adapter status` 暴露 verification result 与 degrade reason
  3. `adapter activate` 若保留，只作为 compatibility/debug surface
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py -q`

### Task 3.2 重构 run gate

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`src/ai_sdlc/cli/run_cmd.py`, `tests/integration/test_cli_run.py`
- **可并行**：否
- **验收标准**：
  1. `run --dry-run` 在未 verified 状态下给出诚实 warning，而不是要求先 `adapter activate`
  2. mutating delivery 相关路径按 ingress truth 阻断
  3. `acknowledged` 不再被视为 verified success
- **验证**：`uv run pytest tests/integration/test_cli_run.py -q`

## Batch 4：Closeout

### Task 4.1 完成 focused verification 与归档

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T32
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. focused unit/integration tests 通过
  2. `git diff --check` 通过
  3. 执行日志完整归档 state/path/gate 收敛结果
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py -q` + `git diff --check`
