# 执行计划：Frontend Framework-Only Closure Policy Baseline

**功能编号**：`079-frontend-framework-only-closure-policy-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only policy freeze

## 1. 目标与定位

`079` 的目标是冻结一个更保守且可执行的 policy split：本仓库作为 framework-only repository，可以证明 framework capability 已完成，但不能凭空证明 consumer implementation 已完成。两者都是真值，但属于不同层级。

## 2. 范围

### 2.1 In Scope

- 创建 `079` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `79`
- 冻结 framework capability evidence 与 consumer implementation evidence 的 policy split
- 冻结 future work item 的拆分原则

### 2.2 Out Of Scope

- 修改任何 runtime status、gate 代码或 root rollout wording
- retroactively 关闭 `068` ~ `071`
- 回填真实 `frontend-contract-observations.json`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/079-frontend-framework-only-closure-policy-baseline/spec.md`
- `specs/079-frontend-framework-only-closure-policy-baseline/plan.md`
- `specs/079-frontend-framework-only-closure-policy-baseline/tasks.md`
- `specs/079-frontend-framework-only-closure-policy-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Policy Freeze

### 4.1 Repository role

- 当前仓库是 framework-only repository
- 它负责 contract、scanner、verify/gate、diagnostics、rollout honesty 与 sample self-check
- 它不自然产出真实业务页面实现

### 4.2 Evidence split

- **Framework capability evidence**
  - formal docs
  - 框架实现
  - 定向测试
  - sample self-check
- **Consumer implementation evidence**
  - 外部真实实现来源
  - canonical `frontend-contract-observations.json`
  - 与 active spec contract 的真实对齐结果

### 4.3 Planning rule

后续设计类似 frontend work item 时，必须在 design 阶段明确：

- 哪些 deliverable 属于 framework capability baseline
- 哪些 deliverable 属于 external backfill / adoption evidence
- 若两者都需要，必须拆成不同 work item 或不同 root sync layer，不能继续共享同一个 close gate

### 4.4 Non-goals

- 不新增 `framework-ready` 之类 runtime status code
- 不在本轮改写 `068` ~ `071` root truth
- 不把 sample self-check 升格为 consumer artifact

## 5. 分阶段计划

### Phase 0：truth alignment

- 回读 `065`、`076`、`077`、`078`
- 确认仓库当前没有已冻结的替代状态术语

### Phase 1：docs-only policy freeze

- 新建 `079` formal docs
- 把 framework-only closure policy 写成单一 truth

### Phase 2：verification and archive

- 运行 docs-only 验证
- 记录当前 root truth 不变
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/079-frontend-framework-only-closure-policy-baseline`

## 7. 回滚原则

- 如果 `079` 把 sample self-check 写成 consumer implementation evidence，必须回退
- 如果 `079` 发明新的 runtime status code，必须回退
- 如果本轮误改 root rollout wording、`src/` 或 `tests/`，必须回退
