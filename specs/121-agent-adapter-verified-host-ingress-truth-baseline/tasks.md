---
related_doc:
  - "program-manifest.yaml"
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "src/ai_sdlc/integrations/agent_target.py"
  - "src/ai_sdlc/integrations/ide_adapter.py"
  - "src/ai_sdlc/cli/adapter_cmd.py"
  - "src/ai_sdlc/cli/run_cmd.py"
---
# 任务分解：Agent Adapter Verified Host Ingress Truth Baseline

**编号**：`121-agent-adapter-verified-host-ingress-truth-baseline` | **日期**：2026-04-13
**来源**：`spec.md` + `plan.md`

---

## 分批策略

```text
Batch 1: formal truth freeze
Batch 2: root manifest sync
Batch 3: project-state handoff + verification
```

---

## Batch 1：Formal truth freeze

### Task 1.1 冻结明确适配列表与状态边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `121` 明确当前明确适配列表只包含 `Claude Code / Codex / Cursor / VS Code / generic`
  2. `121` 明确 `TRAE` 当前只能归入 `generic`
  3. `121` 明确 `materialized / verified_loaded / degraded / unsupported` 的最小状态语义
  4. `121` 明确 `adapter activate` 只代表 operator acknowledgement
- **验证**：文档对账

## Batch 2：Root manifest sync

### Task 2.1 回写 capability closure truth

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `program-manifest.yaml` 新增 `agent-adapter-verified-host-ingress`
  2. 该 cluster 的 `closure_state` 明确为 `partial`
  3. summary 明确当前实现仍缺厂商公开支持的默认入口对齐与 machine-verifiable host ingress
- **验证**：YAML 对账

## Batch 3：Project-state handoff

### Task 3.1 推进 project-state 与 formal closeout

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T21
- **文件**：`.ai-sdlc/project/config/project-state.yaml`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `next_work_item_seq` 从 `121` 推进到 `122`
  2. `task-execution-log.md` 明确本工单只完成 root truth sync，不实现 adapter runtime
  3. 后续 implementation carrier 可直接引用 `121`
- **验证**：文档对账 + YAML 对账

### Task 3.2 完成 focused verification

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：无
- **可并行**：否
- **验收标准**：
  1. `git diff --check` 通过
  2. `121` 与 `program-manifest.yaml`、`project-state.yaml` 的口径一致
- **验证**：`git diff --check`
