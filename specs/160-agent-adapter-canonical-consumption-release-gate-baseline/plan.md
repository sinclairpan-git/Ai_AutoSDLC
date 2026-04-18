# 实施计划：Agent Adapter Canonical Consumption Release Gate Baseline

**编号**：`160-agent-adapter-canonical-consumption-release-gate-baseline` | **日期**：2026-04-18 | **规格**：specs/160-agent-adapter-canonical-consumption-release-gate-baseline/spec.md

## 概述

`160` 承接 `159` 的 canonical proof runtime，把 proof 从“可观测字段”推进到“release/program truth gate”。实施顺序保持最小闭环：先写红灯测试，再把 gate 接到 `ProgramService`，最后补 formal carrier 与 manifest 映射。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Pydantic manifest、`ProgramService`、adapter governance surface  
**测试**：`tests/unit/test_program_service.py`  
**目标平台**：program truth snapshot / close-check readiness  
**约束**：

- canonical blocker 必须来自 machine-verifiable adapter truth
- 不改变 `159` 已冻结的 ingress/runtime proof 协议
- manifest 必须能把 `160` 映射回 `agent-adapter-verified-host-ingress`

## 阶段计划

### Phase 1：红灯锁定 gate 缺口

**目标**：为 canonical proof 未 `verified` / 已 `verified` 两种场景补单测  
**产物**：失败测试  
**验证方式**：`uv run pytest tests/unit/test_program_service.py -k canonical_consumption -q`

### Phase 2：ProgramService gate 实现

**目标**：在 truth capability 计算中消费 adapter governance surface  
**产物**：`ProgramService` canonical gate helper 与 blocker reason code  
**验证方式**：同上聚焦 pytest

### Phase 3：formal carrier 与 manifest 同步

**目标**：补 `160` carrier、release capability entry 与 spec 映射  
**产物**：`specs/160-*`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`  
**验证方式**：`python -m ai_sdlc run --dry-run`

## 实施顺序建议

1. 先写红灯测试，避免把 160 做成只有文档没有判定的空 carrier。
2. gate 只收敛在 `ProgramService`，不扩散到 adapter runtime。
3. 实现稳定后再回填 manifest/spec carrier，让 release capability 与 formal docs 同步。
