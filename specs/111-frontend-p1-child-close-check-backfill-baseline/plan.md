# 实施计划：Frontend P1 Child Close Check Backfill Baseline

**功能编号**：`111-frontend-p1-child-close-check-backfill-baseline`  
**创建日期**：`2026-04-13`  
**状态**：已完成

## 1. 背景与目标

`111` 的目标是把 `068-071` 的 latest-batch execution log 从历史模板升级到现行 close-check 口径。实现方式只限 formal carrier 注册、project-state 推进，以及在四个目标 `task-execution-log.md` 末尾追加 docs-only close-out backfill 段落；不引入新的运行时行为或新的实现结论。

## 2. 实施范围

- 新建 `111` formal docs
- 更新 `program-manifest.yaml` 与 `.ai-sdlc/project/config/project-state.yaml`
- 为 `068-071` 各追加一段 latest-batch close-check backfill 记录
- 复跑 `verify constraints`、`program validate`、`git diff --check` 与 `068-071 / 111` 的 `workitem close-check`

## 3. 约束

- 仅允许修改：
  - `.ai-sdlc/project/config/project-state.yaml`
  - `program-manifest.yaml`
  - `specs/068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md`
  - `specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`
  - `specs/070-frontend-p1-recheck-remediation-feedback-baseline/task-execution-log.md`
  - `specs/071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md`
  - `specs/111-frontend-p1-child-close-check-backfill-baseline/*`
- 不改 `068-071` 的 `spec.md / plan.md / tasks.md`
- 不新增代码或测试

## 4. 步骤

### Step 1 — 冻结 carrier 与范围

**状态**：已完成

- 读取 `068-071` 的 close-check blocker，确认缺口集中在 latest-batch close-out schema，而不是实现本身
- 创建 `111` carrier，并把 `next_work_item_seq` 推进到 `112`

### Step 2 — 追加 latest-batch close-check backfill

**状态**：已完成

- 为 `068-071` 各追加 append-only latest-batch 段落
- 段落统一补齐 `统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作`

### Step 3 — 完成验证与提交

**状态**：已完成

- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program validate`
- 运行 `git diff --check`
- 运行 `uv run ai-sdlc workitem close-check --wi specs/<068-071...>`
- 运行 `uv run ai-sdlc workitem close-check --wi specs/111-frontend-p1-child-close-check-backfill-baseline`

## 5. 完成定义

- `068-071` 的 latest batch 不再因 close-check mandatory fields 缺失而阻塞
- `111` 自身 close-check 通过
- 工作树 clean，且本批只包含 docs/state/manifest 变更
