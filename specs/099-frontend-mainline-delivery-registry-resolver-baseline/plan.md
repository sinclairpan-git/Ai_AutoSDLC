# 执行计划：Frontend Mainline Delivery Registry Resolver Baseline

**功能编号**：`099-frontend-mainline-delivery-registry-resolver-baseline`  
**创建日期**：2026-04-12  
**状态**：docs-only resolver contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`099` 的目标不是实现 resolver runtime，而是把 `097` 拆分建议里的第二块正式切片单独冻结出来：

- 冻结 built-in provider artifacts、install strategies、style pack manifests 的 join 规则；
- 冻结 `solution_snapshot` + `posture_mode` 到 `delivery_bundle_entry` 的解析边界；
- 冻结 `provider_manifest_ref` / `resolved_style_support_ref` 的单向引用规则；
- 冻结 artifact drift 的 fail-closed 行为；
- 保持 runtime materialization、action planning 与 mutating execution 继续在后续切片中独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `099` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `100`
- 在 `program-manifest.yaml` 为 `099` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 built-in registry entry enumeration、install/style join、entry selection 与 fail-closed drift 规则
- 冻结 `099` 与 `073 / 096 / 097 / 098` 的 truth order

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 resolver runtime、artifact writer、installer、action planner 或 rollback executor
- 改写 `073` solution truth、`096` host runtime truth、`098` detector truth
- 新增第三条 built-in delivery entry
- 允许 arbitrary registry source 进入主流程

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`
- `specs/099-frontend-mainline-delivery-registry-resolver-baseline/plan.md`
- `specs/099-frontend-mainline-delivery-registry-resolver-baseline/tasks.md`
- `specs/099-frontend-mainline-delivery-registry-resolver-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Truth order

- `099` 只能消费 `016`、`073`、`094`、`095`、`096`、`097`、`098` 与现有 built-in artifact reality
- `099` 不得回写或重新定义这些上游 truth
- downstream 只能消费 resolver 输出；planner 不得反向改写 registry truth

### 4.2 Resolver boundary

- `073` effective stack/provider/style 先于 built-in catalog join
- `098` posture verdict 只能经过受控 `posture_mode` 归一化进入 resolver
- `component_library_packages` 只能来自 install strategy packages
- `adapter_packages` 在未声明独立 adapter artifact 时必须为空列表

### 4.3 Drift boundary

- provider manifest、style-support、install strategy、style pack manifest 任一缺失时必须 fail-closed
- resolver 不得静默 fallback 到默认 provider/style
- `provider_manifest_ref` / `resolved_style_support_ref` 只能单向引用既有 artifacts
- resolver 不得创建目录、写 registry 文件、安装依赖或改根工程

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `097` 对 resolver 的原始拆分建议与字段面
- 回读 `098` 的 detector handoff 边界，确认 posture verdict 不会反向污染 registry truth
- 回读 built-in provider / style / install strategy 现有代码 reality，确认 v1 entry 只有两条

### Phase 1：formal resolver baseline freeze

- 在 `spec.md` 冻结 provider artifacts、solution catalog artifacts 与 resolver selection context
- 在 `spec.md` 冻结 v1 registry matrix、single-ref 规则与 fail-closed drift semantics
- 在 `plan.md` 写清 docs-only 边界、manifest mirror 需求与验证命令
- 在 `tasks.md` 固化 research、formal freeze、registry sync 与验证 checklist

### Phase 2：verification and registry sync

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/099-frontend-mainline-delivery-registry-resolver-baseline`

## 7. 回滚原则

- 如果 `099` 让人误以为 resolver runtime 或 planner 已经实现，必须回退
- 如果 `099` 生成了第二份 provider/style compatibility truth，必须回退
- 如果 `099` 允许 arbitrary registry source 进入 v1 mainline，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
