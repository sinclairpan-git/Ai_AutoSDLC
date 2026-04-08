# 任务分解：Frontend Contract Observation Backfill Playbook Baseline

**编号**：`077-frontend-contract-observation-backfill-playbook-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-077-001 ~ FR-077-012 / SC-077-001 ~ SC-077-005）

---

## 分批策略

```text
Batch 1: truth and scope freeze
Batch 2: operator checklist freeze
Batch 3: execution log, project-state update, docs-only validation
```

---

## 执行护栏

- `077` 只允许修改 `specs/077/...` 与本地 `project-state.yaml`
- `077` 不得修改 `frontend-program-branch-rollout-plan.md`、`program-manifest.yaml`
- `077` 不得回写 `068` ~ `071` formal docs，也不得进入 `src/` / `tests/`
- `077` 不得伪造任何 active spec 已取得真实 observation artifact

---

## Batch 1：truth and scope freeze

### Task 1.1 冻结 `077` 的 playbook 定位

- [x] 在 `spec.md` 明确 `077` 是 docs-only backfill playbook baseline
- [x] 在 `plan.md` 明确 `077` 不属于新的 root close-sync 或 implementation carrier
- [x] 在 `spec.md` / `plan.md` 明确当前 blocker 仍是外部 observation artifact gap

**完成标准**

- reviewer 可直接读出 `077` 只负责冻结 backfill 执行面，不负责生成真实 artifact

### Task 1.2 冻结 canonical truth inputs

- [x] 在 `spec.md` 明确 canonical artifact 文件名、schema version 与目标 spec 路径
- [x] 在 `plan.md` 明确当前标准导出入口是 `uv run ai-sdlc scan ... --frontend-contract-spec-dir ...`
- [x] 在 `spec.md` 明确 sample fixture 不可作为 active spec 的真实输入

**完成标准**

- operator 不会把 test fixture 或自由 JSON 误读成可接受 backfill

## Batch 2：operator checklist freeze

### Task 2.1 冻结 annotation 与导出步骤

- [x] 在 `plan.md` 给出最小 annotation block 样例
- [x] 在 `plan.md` 明确支持文件后缀、duplicate `page_id` 与 invalid JSON 的失败条件
- [x] 在 `plan.md` 冻结 first-wave target spec list

**完成标准**

- operator 能直接按文档执行外部 source scan 与 spec backfill

### Task 2.2 冻结 gate 判定与非法捷径

- [x] 在 `plan.md` 明确 missing / invalid / empty / drift 的最小判定
- [x] 在 `plan.md` 列出非法捷径清单
- [x] 在 `spec.md` 明确 artifact 存在不等于 blocker 已解除

**完成标准**

- reviewer 可直接用 `077` 审核 backfill 是否诚实

## Batch 3：execution log, project-state update, docs-only validation

### Task 3.1 初始化 `077` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 归档 research inputs、命令与结果

**完成标准**

- `077` formal docs 可独立说明 external observation backfill 的执行入口与边界

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `76` 推进到 `77`
- [x] 不伪造 close、merge 或 artifact 已生成 truth

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行 docs-only / read-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且不引入新的约束错误

## 完成定义

- `077` formal docs 已冻结外部 observation artifact 的生成、回填与验收步骤
- `project-state.yaml` 已前进到 `77`
- 本轮未修改 root rollout wording、manifest、`src/`、`tests/` 或 active spec 正文
