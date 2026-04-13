---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md"
---
# 任务分解：Frontend Evidence Class Readiness Gate Runtime Baseline

**编号**：`107-frontend-evidence-class-readiness-gate-runtime-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-107-001` ~ `FR-107-007` / `SC-107-001` ~ `SC-107-004`）

---

## 分批策略

```text
Batch 1: formal baseline freeze and red tests
Batch 2: runtime implementation
Batch 3: verification and close-out
```

---

## 执行护栏

- `107` 必须只放宽 `framework_capability` 的 observation-attachment 缺口
- `107` 不得放宽 `consumer_adoption` 的真实证据要求
- `107` 不得在 footer 缺失或非法时静默豁免
- `107` 不得把其他真实 gate blocker 伪装为“通过”

---

## Batch 1：formal baseline freeze and red tests

### Task 1.1 冻结 107 formal baseline

- [x] 完成 `107` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 注册 `107`

**完成标准**

- `107` 有合法 carrier，且 manifest graph 能引用本 work item

### Task 1.2 先补 evidence-class-aware red tests

- [x] 在 `tests/unit/test_frontend_gate_verification.py` 增加 framework-capability observation gap 豁免红灯测试
- [x] 在 `tests/unit/test_program_service.py` 增加 framework-capability / consumer-adoption readiness 分流红灯测试
- [x] 在 `tests/integration/test_cli_program.py` 增加 CLI status 分流红灯测试

**完成标准**

- 新测试在运行时调整前先失败，精确描述 `107` 要交付的行为

## Batch 2：runtime implementation

### Task 2.1 接入 canonical evidence class 到 readiness chain

- [x] 在 `src/ai_sdlc/core/program_service.py` 读取 canonical `frontend_evidence_class`
- [x] 将 evidence class 接入 frontend readiness state 计算
- [x] 保持 footer 缺失 / 无效时不豁免

**完成标准**

- readiness chain 只在 canonical `framework_capability` 条件成立时放宽 observation 缺口

### Task 2.2 调整 execute decision 的 evidence-class-aware attachment semantics

- [x] 在 `src/ai_sdlc/core/frontend_gate_verification.py` 为 `framework_capability` + `frontend_contract_observations` 缺失增加非阻塞判定
- [x] 保持 `consumer_adoption` 与其他 attachment blocker 行为不变

**完成标准**

- execute decision 能区分 framework-capability 与 consumer-adoption 两条路径

## Batch 3：verification and close-out

### Task 3.1 回放 focused verification

- [x] 运行 focused unit / integration pytest 回归
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc program status`

**完成标准**

- framework-capability 豁免与 consumer-adoption 保留均有 fresh verification 证明

### Task 3.2 完成 diff hygiene 与 close-out

- [x] 运行 `git diff --check`
- [x] 更新 `task-execution-log.md`
- [x] 运行 `uv run ai-sdlc workitem close-check --wi specs/107-frontend-evidence-class-readiness-gate-runtime-baseline`

**完成标准**

- `107` 可以作为 evidence-class-aware readiness runtime carrier 收口
