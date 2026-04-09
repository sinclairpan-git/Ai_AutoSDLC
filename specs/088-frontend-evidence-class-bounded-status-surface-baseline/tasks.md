# 任务分解：Frontend Evidence Class Bounded Status Surface Baseline

**编号**：`088-frontend-evidence-class-bounded-status-surface-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-088-001 ~ FR-088-010 / SC-088-001 ~ SC-088-004）

---

## 分批策略

```text
Batch 1: surface reconciliation
Batch 2: status contract baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `088` 只允许修改 `specs/088/...` 与本地 `project-state.yaml`
- `088` 不得实现 status summary、validator 或 close-stage resurfacing
- `088` 不得修改 `program-manifest.yaml`
- `088` 不得冻结具体 JSON key 名、table column 名或 CLI 文案
- `088` 不得改写 `083` ~ `087` 已冻结的 prospective contract
- `088` 不得 retroactively 改义 `068` ~ `071`
- `088` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：surface reconciliation

### Task 1.1 对齐 validator / diagnostics / writeback / status 边界

- [x] 回读 `083`、`084`、`085`、`086`、`087`
- [x] 回读 `USER_GUIDE.zh-CN.md` 中 `status --json` 与 `program status` 的边界
- [x] 回读 `src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/telemetry/readiness.py`

**完成标准**

- 能用单一 wording 解释为什么 `program status` 与 `status --json` 必须保持不同粒度

## Batch 2：status contract baseline freeze

### Task 2.1 新建 `088` formal docs

- [x] 在 `spec.md` 冻结 `program status` 与 `status --json` 的 summary 粒度
- [x] 在 `spec.md` 冻结 allowed bounded fields 与 forbidden payload
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- maintainer 能直接回答 `program status` 和 `status --json` 对 evidence-class 分别能露出什么

### Task 2.2 冻结 non-adjudication 边界

- [x] 在 `spec.md` 冻结 status surface 不得 first-detect、不得重裁 severity、不得 auto-heal
- [x] 在 `tasks.md` 明确 status surface 不得扩展成 diagnostics dump

**完成标准**

- reviewer 能直接判断某个 status 输出是否已经替代 owning surface

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `088` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `088` 能独立说明两类 status surface 的粒度边界与禁止项

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `87` 推进到 `88`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
