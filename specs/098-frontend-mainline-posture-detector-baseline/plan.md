# 执行计划：Frontend Mainline Posture Detector Baseline

**功能编号**：`098-frontend-mainline-posture-detector-baseline`  
**创建日期**：2026-04-12  
**状态**：docs-only detector contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`098` 的目标不是实现 detector runtime，而是把 `097` 拆分建议里的第一块正式切片单独冻结出来：

- 冻结 detector 允许消费的 evidence source class；
- 冻结 attachment truth、repo stack signal、component-library clue 的判定优先级；
- 冻结五类 `support_status` 的成立条件与诚实降级规则；
- 冻结 `sidecar_root_recommendation` 在 detector 阶段的生成边界；
- 保持 resolver、delivery bundle、action planning 继续在后续切片中独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `098` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `99`
- 在 `program-manifest.yaml` 为 `098` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 detector evidence source、判定优先级、五类状态与 sidecar recommendation boundary
- 冻结 `098` 与 `014 / 073 / 094 / 095 / 096 / 097` 的 truth order

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 detector runtime、repo walker、manifest parser 或 filesystem mutation
- formalize resolver、delivery bundle materialization 或 provider/style truth
- 改写 `014` attachment truth、`073` solution truth、`097` registry truth
- 在 detector 阶段默认 takeover old frontend 或默认 root integration

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/098-frontend-mainline-posture-detector-baseline/spec.md`
- `specs/098-frontend-mainline-posture-detector-baseline/plan.md`
- `specs/098-frontend-mainline-posture-detector-baseline/tasks.md`
- `specs/098-frontend-mainline-posture-detector-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Truth order

- `098` 只能消费 `014`、`073`、`094`、`095`、`096`、`097` 与 machine-observable repo evidence
- `098` 不得回写或重新定义这些上游 truth
- downstream 只能消费 posture verdict；resolver 不得反向改写 detector contract

### 4.2 Detector boundary

- attachment truth 优先于 repo scan truth
- stack-level repo evidence 优先于 component-library clue
- evidence 冲突或不足时必须 fail-closed 到 `ambiguous_existing_frontend`
- `supported_existing_candidate` 不得被写成默认 takeover ready

### 4.3 Sidecar boundary

- `sidecar_root_recommendation` 只能表达推荐子树、默认 `will_not_touch` 与 root-level actions 默认关闭
- detector 不得创建目录、写脚手架、改 manifest、改 lockfile、改 CI/proxy/route
- provider/style/install/runtime package truth 继续留给 resolver 与 action planner

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `095` 对 `frontend_posture_assessment` 的原始要求
- 回读 `097` 的 posture / registry formal contract 与拆分建议
- 回读 `014` attachment truth、`073` solution freeze boundary 与 `096` host readiness boundary
- 回读现有 scanner / attachment 相关代码，只确认现有 reality，不把它误写成 detector 已实现

### Phase 1：formal detector baseline freeze

- 在 `spec.md` 冻结 evidence source class、dominant evidence 规则与五类 status semantics
- 在 `spec.md` 冻结 `sidecar_root_recommendation` 的 detector-only boundary
- 在 `plan.md` 写清 docs-only 边界、manifest mirror 需求与验证命令
- 在 `tasks.md` 固化 research、formal freeze、registry sync 与验证 checklist

### Phase 2：verification and registry sync

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/098-frontend-mainline-posture-detector-baseline`

## 7. 回滚原则

- 如果 `098` 让人误以为 resolver 或 action engine 已经实现，必须回退
- 如果 `098` 让 component-library clue 越权决定 supported verdict，必须回退
- 如果 `098` 允许 detector 阶段修改旧工程或根目录，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
