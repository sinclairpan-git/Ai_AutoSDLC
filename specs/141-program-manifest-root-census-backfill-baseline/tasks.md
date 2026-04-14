---
related_doc:
  - "specs/141-program-manifest-root-census-backfill-baseline/spec.md"
  - "specs/141-program-manifest-root-census-backfill-baseline/plan.md"
  - "program-manifest.yaml"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
---
# 任务分解：Program Manifest Root Census Backfill Baseline

**编号**：`141-program-manifest-root-census-backfill-baseline` | **日期**：2026-04-14  
**来源**：`plan.md` + `spec.md`（`FR-141-001` ~ `FR-141-009` / `SC-141-001` ~ `SC-141-005`）

---

## 分批策略

```text
Batch 1: formal freeze / 双轮对抗评审
Batch 2: repo-level census regression red-green
Batch 3: root manifest 38-entry backfill（37 个历史缺口 + `141` 自身）
Batch 4: truth sync / truth audit verification
Batch 5: execution log / development summary / next tranche handoff
```

---

## 执行护栏

- `141` 只清根 manifest 漏项导致的 migration noise，不修 `frontend-mainline-delivery` 的 runtime/close-check blocker
- 不发明新的 capability membership、release role 或伪 dependency truth
- 对本 tranche 新回填的非 release-scope entries，`roles` 与 `capability_refs` 保持空列表
- `frontend_evidence_class` 只能镜像 canonical footer；canonical 缺失则留空
- `program truth sync --execute --yes` 只能在 repo-level regression 与 `truth sync --dry-run` 都通过后执行

---

## Batch 1：formal freeze / 双轮对抗评审

### Task 1.1 完成 `spec.md` 两轮对抗评审

- [x] 起草 `spec.md`
- [x] 由 Avicenna 完成第 1 轮对抗评审
- [x] 由 Russell 完成第 1 轮对抗评审
- [x] 根据第 1 轮意见收紧 `migration_pending`、`depends_on`、repo-level regression 口径
- [x] 由 Avicenna 完成第 2 轮对抗评审
- [x] 由 Russell 完成第 2 轮对抗评审
- [x] 收口 `branch_slug` 与非 release-scope `roles/capability_refs` 边界

### Task 1.2 完成 `plan.md` 两轮对抗评审

- [x] 起草 `plan.md`
- [x] 由 Avicenna 完成第 1 轮对抗评审
- [x] 由 Russell 完成第 1 轮对抗评审
- [x] 根据第 1 轮意见加入 `truth sync --dry-run` 闸口与 tranche-2 交接证据字段
- [x] 由 Avicenna 完成第 2 轮对抗评审
- [x] 由 Russell 完成第 2 轮对抗评审
- [x] 收口最终 tests evidence 与 `truth sync --execute` 前置条件

---

## Batch 2：repo-level census regression red-green

### Task 2.1 先写回归测试红灯

- [x] 新增 repo-level pytest 回归测试，直接加载当前仓库根目录的 `program-manifest.yaml`
- [x] 先断言当前根 manifest 仍存在 missing-entry migration warnings，并由红灯测试确认当前工作树实际缺口已随 `141` 创建增至 38 个
- [x] 运行该测试并确认红灯来自根 census 漏项，而不是测试夹具错误

**完成标准**

- 在修改 manifest 之前，未来“再漏纳管”的行为已经有失败测试保护

### Task 2.2 预先冻结 backfill metadata

- [x] 盘点启动时 37 个历史缺失目录，并把 `141` 自身目录加入实际回填写集
- [x] 为每个缺失 entry 冻结 `id/path/branch_slug/owner/frontend_evidence_class`
- [x] 明确 `066` 双目录共存场景的纳管策略
- [x] 对无可靠依赖来源的历史 spec 统一写成 `depends_on: []`

**完成标准**

- 回填规则在改 YAML 前已固定，不会边写边漂移

---

## Batch 3：root manifest 37-entry backfill

### Task 3.1 回填根 manifest

- [x] 在 `program-manifest.yaml` 中回填启动时 37 个历史缺失 spec entries，并补上 `141` 自身 entry
- [x] 保持现有 release target / capability / closure audit authoring intent 不变
- [x] 对新回填的非 release-scope entries 保持空 `roles/capability_refs`
- [x] 确认 `frontend_evidence_class` 仅在 canonical footer 存在时镜像回填

**完成标准**

- 根 manifest 对所有带 `spec.md` 的 `specs/*` 目录达到 1:1 覆盖

### Task 3.2 跑局部验证

- [x] 运行 repo-level census regression，确认从红灯转绿
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 确认 `migration_pending: manifest entry missing for specs/...` 已清零

**完成标准**

- 缺 entry 导致的 migration cause 已从 authoring layer 消失

---

## Batch 4：truth sync / truth audit verification

### Task 4.1 先跑 dry-run，再落盘 snapshot

- [x] 运行 `uv run ai-sdlc program truth sync --dry-run`
- [x] 检查 dry-run 输出，确认 missing-entry cause 已清零
- [x] 在 dry-run 与 repo-level regression 都通过后运行 `uv run ai-sdlc program truth sync --execute --yes`

**完成标准**

- 不会在根 manifest 仍错误时把 pseudo-truth snapshot 固化到根账本

### Task 4.2 固定 audit 收敛结果

- [x] 运行 `uv run ai-sdlc program truth audit`
- [x] 记录 `state`、`snapshot_state`、`migration_pending_count`、`release_capabilities`
- [x] 确认 `frontend-mainline-delivery` 的真实 blocker 仍保留
- [x] 明确当前仓库是否已从 `migration_pending` 收敛到 `blocked`

**完成标准**

- truth ledger 只剩真实 blocker 或其他剩余真实 migration cause

---

## Batch 5：execution log / development summary / next tranche handoff

### Task 5.1 回填执行归档

- [x] 更新 `task-execution-log.md`
- [x] 生成 `development-summary.md`
- [x] 记录 repo-level regression、validate、truth sync、truth audit 的命令与结果

### Task 5.2 创建第二 tranche 入口

- [x] 创建下一个 tranche 的 `spec.md`
- [x] 明确其只处理 `frontend-mainline-delivery` blockers：`095/096/098/099/100/101/102/103/104/105/123/124/125/126`
- [x] 在交接口径中带上 `release_capabilities`、`blocking_refs`、`migration_pending_count`、`migration_pending_specs`

**完成标准**

- `141` 完成可信收尾，且第二 tranche 有明确 machine-readable 起点
