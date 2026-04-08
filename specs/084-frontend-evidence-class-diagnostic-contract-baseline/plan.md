# 执行计划：Frontend Evidence Class Diagnostic Contract Baseline

**功能编号**：`084-frontend-evidence-class-diagnostic-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective diagnostics contract

## 1. 目标与定位

`084` 的目标是把 `083` 已冻结的 detection surface 继续前推成 diagnostics contract：未来 evidence-class 校验一旦发现问题，至少要使用稳定的问题族群、稳定的严重级别边界，以及稳定的最小诊断字段集合。

## 2. 范围

### 2.1 In Scope

- 创建 `084` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `84`
- 冻结 future problem families、minimum payload 与 severity boundary
- 冻结 bounded status exposure 的上限

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 设计 JSON schema、dataclass 或 telemetry storage
- 引入 manifest mirror 字段本身
- retroactively 改义 `068` ~ `071`
- 改写 `083` 的 owning surface 归属

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`
- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/plan.md`
- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/tasks.md`
- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Contract Rules

### 4.1 Problem families

- `frontend_evidence_class_authoring_malformed`
- `frontend_evidence_class_mirror_drift`

### 4.2 Severity boundary

- owning surface 上最低严重级别均不得低于 `BLOCKER`
- status surfaces 不负责 severity adjudication

### 4.3 Minimum payload

- `problem_family`
- `detection_surface`
- `spec_path`
- `error_kind`
- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint`

### 4.4 Bounded status exposure

- status surfaces 只展示 blocker presence、problem family 和关联 spec 标识
- 不展开 full diagnostic narrative

## 5. 分阶段计划

### Phase 0：diagnostic vocabulary alignment

- 回读 `083`
- 回读 defect backlog 中 `detection_surface` 填写原则
- 回读用户指南中 `status --json` 与 `verify constraints` 的边界

### Phase 1：diagnostic contract freeze

- 新建 `084` formal docs
- 写清问题族群、严重级别边界与最小 payload
- 写清 status surface 的克制边界

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/084-frontend-evidence-class-diagnostic-contract-baseline`

## 7. 回滚原则

- 如果 `084` 让人误以为当前 CLI 已经实现新的 diagnostics payload，必须回退
- 如果 `084` 把 status surface 升格成 full diagnostic surface，必须回退
- 如果 `084` 改写 `083` 的 owning surface 归属，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
