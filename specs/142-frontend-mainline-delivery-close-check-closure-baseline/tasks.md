---
related_doc:
  - "specs/142-frontend-mainline-delivery-close-check-closure-baseline/spec.md"
  - "specs/142-frontend-mainline-delivery-close-check-closure-baseline/plan.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md"
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md"
  - "program-manifest.yaml"
---
# 任务分解：Frontend Mainline Delivery Close-Check Closure Baseline

**编号**：`142-frontend-mainline-delivery-close-check-closure-baseline` | **日期**：2026-04-14  
**来源**：`plan.md` + `spec.md`（`FR-142-001` ~ `FR-142-006` / `SC-142-001` ~ `SC-142-003`）

---

## 分批策略

```text
Batch 1: formal freeze / 双轮对抗评审
Batch 2: blocker universe refresh + blocker-execution-map
Batch 3: product-host-registry-apply 子链
Batch 4: browser-gate-recheck 子链
Batch 5: capability closure audit reconciliation
```

---

## 执行护栏

- `142` 自身不是 release carrier，不加入 `frontend-mainline-delivery.spec_refs`
- blocker universe 必须来自最新 `program truth audit` + `required_evidence.close_check_refs`
- `blocker-execution-map.yaml` 必须放在 `specs/142-frontend-mainline-delivery-close-check-closure-baseline/`
- map 校验 pytest 必须进入默认 pytest 收集路径，并作为 `142` 的最终 tests evidence
- 任何 batch 都不得用 docs-only wording 覆盖 `capability_closure_audit:capability_open`

---

## Batch 1：formal freeze / 双轮对抗评审

### Task 1.1 完成 `spec.md` 两轮对抗评审

- [x] 起草 `spec.md`
- [x] 由 Avicenna 完成第 1 轮对抗评审
- [x] 由 Russell 完成第 1 轮对抗评审
- [x] 根据第 1 轮意见加入“最新 truth audit + close_check_refs 是 blocker universe 唯一入口”
- [x] 根据第 1 轮意见加入 machine-readable `blocker-execution-map.yaml`
- [x] 由 Avicenna 完成第 2 轮对抗评审
- [x] 由 Russell 完成第 2 轮对抗评审

### Task 1.2 完成 `plan.md` 两轮对抗评审

- [x] 起草 `plan.md`
- [x] 由 Avicenna 完成第 1 轮对抗评审
- [x] 由 Russell 完成第 1 轮对抗评审
- [x] 根据第 1 轮意见补上 map canonical path、schema 与强制 close evidence
- [x] 由 Avicenna 完成第 2 轮对抗评审
- [x] 由 Russell 完成第 2 轮对抗评审
- [x] 根据第 2 轮意见补上 map pytest 断言范围与默认 pytest 收集要求

---

## Batch 2：blocker universe refresh + blocker-execution-map

### Task 2.1 刷新 blocker universe

- [x] 重新运行 `uv run ai-sdlc program truth audit`
- [x] 提取最新 `release_capabilities[].blocking_refs`
- [x] 对齐 `program-manifest.yaml` 中 `frontend-mainline-delivery.required_evidence.close_check_refs`
- [x] 识别新增 / 消失 / 漂移 blocker

### Task 2.2 建立 machine-readable blocker map

- [x] 创建 `specs/142-frontend-mainline-delivery-close-check-closure-baseline/blocker-execution-map.yaml`
- [x] 为每个 blocker_ref 填写 `carrier_spec`
- [x] 为每个 blocker_ref 填写 `execution_batch`
- [x] 为每个 blocker_ref 填写 `verification_command_or_surface`
- [x] 为每个 blocker_ref 填写 `expected_close_evidence`
- [x] 为跨链 prerequisite（至少 `124 -> 125`）填 `prerequisites`

### Task 2.3 锁定 map 校验

- [x] 新增 map validation pytest
- [x] 断言 blocker_ref / carrier_spec / verification surface / evidence 非空且合法
- [x] 将该测试放入默认 pytest 收集路径
- [x] 跑红灯/翻绿，确认 map 漂移会被直接卡住

---

## Batch 3：product-host-registry-apply 子链

### Task 3.1 冻结子链执行顺序

- [x] 按 `095 -> 096 -> 098 -> 099 -> 100 -> 101 -> 123 -> 124` 固定基础 host/apply 顺序，并将 `144` 标注为后续 closure bridge
- [x] 为每个 carrier spec 绑定对应 close-check / truth-check / verify evidence
- [x] 明确哪些 child work 可以并行、哪些必须串行

### Task 3.2 逐批实现并验证

- [x] 对每个 child work 执行实现
- [x] 每批结束后回跑对应 `workitem close-check`
- [x] 回跑 `program truth audit`，确认对应 blocker_ref 消失

---

## Batch 4：browser-gate-recheck 子链

### Task 4.1 冻结子链执行顺序

- [x] 按 `102 -> 103 -> 104 -> 105 -> 125 -> 126 -> 143` 固定 browser gate / recheck / real-probe 顺序
- [x] 在 map 中显式标注 `125` 依赖 `124`
- [x] 为每个 blocker 绑定 browser gate runtime close evidence

### Task 4.2 逐批实现并验证

- [x] 对每个 child work 执行实现
- [x] 每批结束后回跑对应 `workitem close-check`
- [x] 回跑 `program truth audit`，确认对应 blocker_ref 消失

---

## Batch 5：capability closure audit reconciliation

### Task 5.1 复核 capability closure audit

- [x] 在所有 close_check blockers 消失后复核 `capability_closure_audit`
- [x] 用 machine evidence 驱动 closure audit 收敛
- [x] 重新运行 `uv run ai-sdlc program truth audit`

### Task 5.2 最终 close 条件

- [x] 仅当 `frontend-mainline-delivery.audit_state=ready` 时关闭 `142`
- [x] 回填 `task-execution-log.md`
- [x] 生成 `development-summary.md`

**完成标准**

- `142` 不再是“解释 blocker 的文档 tranche”，而是能够把 `frontend-mainline-delivery` 真正收敛为 `ready` 的执行入口
