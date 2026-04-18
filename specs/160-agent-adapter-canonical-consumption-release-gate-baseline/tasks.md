---
related_spec: specs/160-agent-adapter-canonical-consumption-release-gate-baseline/spec.md
related_plan: specs/160-agent-adapter-canonical-consumption-release-gate-baseline/plan.md
---

# 160 Tasks

## 批次策略

### Batch 1: gate red-green

- 先补 canonical gate 红灯测试。
- 在 `ProgramService` 中接入 canonical blocker。

### Batch 2: formal carrier sync

- 回填 `160` formal docs。
- 在 `program-manifest.yaml` 中登记 capability/spec 映射。

## 任务清单

- [x] T11 canonical gate 红灯测试
  - 优先级: P0
  - 依赖: 无
  - 文件: `tests/unit/test_program_service.py`
  - 验收: `unverified` 与 `verified` 两类场景都被测试锁定
  - 验证: `uv run pytest tests/unit/test_program_service.py -k canonical_consumption -q`

- [x] T12 ProgramService canonical gate 实现
  - 优先级: P0
  - 依赖: T11
  - 文件: `src/ai_sdlc/core/program_service.py`
  - 验收: `agent-adapter-verified-host-ingress` 在 canonical proof 未 `verified` 时稳定返回 blocker
  - 验证: `uv run pytest tests/unit/test_program_service.py -k canonical_consumption -q`

- [x] T13 formal carrier 与 manifest 映射同步
  - 优先级: P1
  - 依赖: T12
  - 文件: `specs/160-agent-adapter-canonical-consumption-release-gate-baseline/`, `program-manifest.yaml`, `.ai-sdlc/project/config/project-state.yaml`
  - 验收: `160` 已成为正式 carrier，且 root manifest 能把它映射到 `agent-adapter-verified-host-ingress`
  - 验证: `python -m ai_sdlc run --dry-run`
