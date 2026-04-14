---
related_doc:
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/plan.md"
  - "program-manifest.yaml"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/workitem_cmd.py"
  - "src/ai_sdlc/core/close_check.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/rules/quality-gate.md"
  - "docs/framework-defect-backlog.zh-CN.md"
---
# 任务分解：Program Truth Ledger And Release Audit Baseline

**编号**：`140-program-truth-ledger-release-audit-baseline` | **日期**：2026-04-14  
**来源**：`plan.md` + `spec.md`（`FR-140-001` ~ `FR-140-014` / `SC-140-001` ~ `SC-140-005`）

---

## 分批策略

```text
Batch 1: formal freeze / adversarial review / decompose correction
Batch 2: schema and manifest validation red-green
Batch 3: repo census / spec index / capability mapping
Batch 4: minimal snapshot / truth sync / truth audit
Batch 5: status-readiness / release-audit gate integration
Batch 6: migration diagnostics / derived views / focused verification
```

---

## 执行护栏

- `140` 不得推翻 `082/087` 已冻结的 field-level canonical ownership
- `140` 不得把 `program-manifest.yaml` 扩成手写运行态总账本；snapshot 只允许持久化最小聚合结果
- `140` v1 的 mandatory evidence 只允许来自 `workitem truth-check`、`workitem close-check`、`verify constraints`
- `140` 不得新建手工维护的 command/probe registry 作为 release blocker
- `140` 必须区分 `closure_state` 与 `audit_state`；其中 `audit_state` 是唯一 release 裁决状态
- `140` 在 `tasks.md` 缺失时不得对用户表述“可以进入实现”

---

## Batch 1：formal freeze / adversarial review / decompose correction

### Task 1.1 起草 formal docs 并完成两轮对抗评审

- [x] 创建 `spec.md`
- [x] 创建 `plan.md`
- [x] 用 AI-Native expert 完成第 1 轮对抗评审并回收意见
- [x] 用 coding-framework architect 完成第 1 轮对抗评审并回收意见
- [x] 根据第 1 轮意见收窄 schema、CLI 面与 gate 口径
- [x] 用 AI-Native expert 完成第 2 轮对抗评审并确认 `no blocker`
- [x] 用 coding-framework architect 完成第 2 轮对抗评审并确认 `no blocker`

**完成标准**

- `140/spec.md` 与 `140/plan.md` 不再把 manifest 写成第二真值系统
- `closure_state` / `audit_state`、canonical precedence、migration mode、v1 evidence 边界都已冻结

### Task 1.2 纠正流程顺序并补齐 DECOMPOSE 产物

- [x] 在 framework defect backlog 记录“plan 后跳过 tasks 直接谈实现”的违约
- [x] 创建 `tasks.md`
- [x] 将下一步口径纠正为 “先进入 tasks/decompose，再谈实现”
- [x] 不把 `140` 表述为已进入实现阶段

**完成标准**

- `140` 已重新回到 `spec -> plan -> tasks` 的合法顺序
- backlog 中有对应违约留痕，本轮不再口头跳过

---

## Batch 2：schema and manifest validation red-green

### Task 2.1 先写 truth-ledger schema / audit 红灯夹具

- [x] 为 `ProgramManifest` v2 ledger schema 补 unit tests
- [x] 为旧 schema / 新 schema / migration mode 写兼容夹具
- [x] 为 `truth audit` 的 canonical conflict、missing release-scope entry、stale snapshot 场景写红灯测试

**文件**

- `tests/unit/test_program_models.py`
- `tests/integration/test_cli_program.py` 或新增 truth-ledger 定向测试文件

**完成标准**

- 在实现前，truth-ledger 的关键 contract 已有失败测试保护

### Task 2.2 实现最小 ledger schema 与 manifest 校验

- [x] 扩展 `src/ai_sdlc/models/program.py`
- [x] 在 `src/ai_sdlc/core/program_service.py` 增加 ledger load / validate / migration mode 逻辑
- [x] 保持 `082/087/119` 的 canonical ownership 与 closure truth 映射不被破坏

**文件**

- `src/ai_sdlc/models/program.py`
- `src/ai_sdlc/core/program_service.py`

**完成标准**

- manifest 能解析 authoring intent + 最小 snapshot
- release-scope 与 non-release-scope migration gap 被显式区分

---

## Batch 3：repo census / spec index / capability mapping

### Task 3.1 做全仓 spec census 与缺口归类

- [x] 按“包含 `spec.md` 的 `specs/*` 子目录”口径扫描全仓
- [x] 识别缺失 entry、重复 entry、orphan entry
- [x] 区分 release-scope blocker 与 non-release-scope migration gap

**文件**

- `program-manifest.yaml`
- `src/ai_sdlc/core/program_service.py`
- 对应测试文件

**完成标准**

- truth audit 能稳定指出当前 manifest 的全仓覆盖缺口

### Task 3.2 补齐 spec role / capability refs / required evidence refs

- [x] 为 release-scope specs 补齐 `roles`
- [x] 为 release-scope capabilities 补齐 `spec_refs`
- [x] 将 required evidence 限定到 `truth-check` / `close-check` / `verify` refs
- [x] 保证 capability 与 spec 侧引用双向一致

**文件**

- `program-manifest.yaml`
- 对应测试文件

**完成标准**

- release-scope 的 capability graph 与 evidence refs 可被机器读取

---

## Batch 4：minimal snapshot / truth sync / truth audit

### Task 4.1 实现最小 snapshot 生成与 freshness contract

- [x] 实现 `authoring_hash`、`source_hashes`、`snapshot_hash`
- [x] 让 snapshot 只持久化 `closure_state` / `audit_state` / `blocking_refs` / `stale_reason`
- [x] 不把 task progress、close readiness、逐项 evidence 明细写入 snapshot

**文件**

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/models/program.py`

**完成标准**

- snapshot 可被判定为 `fresh/stale/invalid`
- snapshot 不会演变成第二运行态账本

### Task 4.2 实现 `program truth sync` 与 `program truth audit`

- [x] 增加 `program truth sync --dry-run/--execute`
- [x] 增加 `program truth audit`
- [x] 让 canonical conflict 强制映射为 `audit_state=blocked`

**文件**

- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/core/program_service.py`
- 对应测试文件

**完成标准**

- `truth sync` 只负责显式写 snapshot
- `truth audit` 对 release-scope blocker fail-closed

---

## Batch 5：status-readiness / release-audit gate integration

### Task 5.1 让既有 status/readiness 消费 ledger/snapshot

- [x] 让 `program status` 读取 ledger/snapshot
- [x] 让 readiness 在 ledger/snapshot 失败时显式暴露 `stale/invalid`
- [x] 保持 read-only surfaces 不写 snapshot

**文件**

- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/telemetry/readiness.py`
- 对应测试文件

**完成标准**

- status/readiness 不再 fail-open

### Task 5.2 接入 release audit hard gate

- [x] 让 release audit 以 `audit_state` 为唯一裁决状态
- [x] authoritative `closure_state` 仅作为解释层，不反向 override audit
- [x] 对 missing release-scope entry、missing evidence、canonical conflict、migration_pending fail-closed

**文件**

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/core/close_check.py`
- 需要时补相关 gate 文件与测试

**完成标准**

- close/release 路径不能再被 formal close wording 假绿绕过

---

## Batch 6：migration diagnostics / derived views / focused verification

### Task 6.1 输出 migration diagnostics 与 derived-view 约束

- [x] 输出旧 schema / 缺 role / 缺 ref / 缺 hash 的最小补齐建议
- [x] 让 derived dashboard / summary 明确带 `generated_at` / `repo_revision`
- [x] 禁止 derived views 拥有高于 ledger/snapshot 的 authority

**文件**

- `src/ai_sdlc/core/program_service.py`
- 相关文档文件

**完成标准**

- 旧仓库升级路径可操作，不再要求人工从零盘全仓

### Task 6.2 完成 focused verification 与归档

- [x] 运行 truth-ledger / release-audit 定向测试
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `uv run ai-sdlc program truth audit`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 回填 `task-execution-log.md`

**完成标准**

- `140` 的最小实现闭环有 fresh verification 与执行归档
