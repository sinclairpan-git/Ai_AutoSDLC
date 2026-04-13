---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md"
---
# 执行计划：Frontend Evidence Class Readiness Gate Runtime Baseline

**功能编号**：`107-frontend-evidence-class-readiness-gate-runtime-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`107` 的目标是把 `081` 冻结的 prospective contract 接到当前 runtime：frontend readiness gate 要识别 canonical `frontend_evidence_class`，并对 `framework_capability` 与 `consumer_adoption` 走不同 observation-attachment 语义。

## 2. 范围

### 2.1 In Scope

- 创建 `107` formal docs 与 execution log
- 在 `program-manifest.yaml` 注册 `107`
- 调整 `src/ai_sdlc/core/program_service.py` 的 frontend readiness 构建逻辑
- 调整 `src/ai_sdlc/core/frontend_gate_verification.py` 的 execute decision，使其识别 `framework_capability`
- 补充 focused unit / integration tests，并回放相关验证

### 2.2 Out Of Scope

- 修改 `verify constraints`、manifest sync 或 close-check 的其他 surface
- 引入新的 evidence class 枚举
- 伪造 observation artifact 或替 consumer adoption item 兜底
- 改写 `081`、`092`、`105`、`106` 的 historical docs

## 3. 变更文件面

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/core/frontend_gate_verification.py`
- `tests/unit/test_program_service.py`
- `tests/unit/test_frontend_gate_verification.py`
- `tests/integration/test_cli_program.py`
- `program-manifest.yaml`
- `specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`
- `specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/plan.md`
- `specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/tasks.md`
- `specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/task-execution-log.md`

## 4. 实施规则

### 4.1 Canonical truth first

- readiness gate 只能信任 `spec.md` footer 的 canonical `frontend_evidence_class`
- footer 缺失、为空或非法时，不得仅凭 manifest mirror 直接豁免

### 4.2 Scope discipline

- `107` 只处理 observation attachment 的 evidence-class-aware gating
- `consumer_adoption` 现有行为必须保持不变
- 其他真实 blocker 不得被 `107` 伪装为“通过”

### 4.3 Verification discipline

- 先补红灯测试，再改运行时逻辑
- 验证至少覆盖 unit、CLI status surface、execute gate path 与 diff hygiene

## 5. 分批计划

### Batch 1：formal baseline freeze and red tests

- 完成 `107` spec / plan / tasks / execution log
- 在 `program-manifest.yaml` 注册 `107`
- 为 framework-capability 豁免与 consumer-adoption 保留补 red tests

### Batch 2：runtime implementation

- 将 canonical evidence class 读取接入 `_build_frontend_readiness()`
- 为 execute decision 增加 framework-capability observation gap 豁免
- 保持其他 attachment / gate blocker 行为不变

### Batch 3：verification and close-out

- 运行 focused pytest 回归
- 回放 `uv run ai-sdlc program status` / `program validate`
- 运行 `git diff --check`，补 execution log，并准备 close-check

## 6. 最小验证策略

- `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'framework_capability or attachment_missing' -q`
- `uv run pytest tests/unit/test_program_service.py -k 'framework_capability or consumer_adoption or frontend_readiness' -q`
- `uv run pytest tests/integration/test_cli_program.py -k 'frontend_readiness or framework_capability' -q`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program status`
- `git diff --check -- src/ai_sdlc/core/program_service.py src/ai_sdlc/core/frontend_gate_verification.py tests/unit/test_program_service.py tests/unit/test_frontend_gate_verification.py tests/integration/test_cli_program.py program-manifest.yaml specs/107-frontend-evidence-class-readiness-gate-runtime-baseline`

## 7. 回滚原则

- 若 consumer-adoption 路径被放宽，必须回退
- 若 footer 缺失时仍被错误豁免，必须回退
- 若 framework-capability 路径仍继续暴露 `missing_artifact / scope_or_linkage_invalid`，则 `107` 不得宣称完成
