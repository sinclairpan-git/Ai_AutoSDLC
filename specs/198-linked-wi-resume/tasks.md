---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Linked Work Item Resume Working Set

**编号**：`198-linked-wi-resume` | **父项**：WI-196 `GAP-08 / T52`

**评审状态口径**：为避免 reviewer verdict 改写参与哈希的文件形成自引用循环，T12 与 T32 的最终双 Agent verdict 始终不在本文件勾选；权威 PASS/FAIL 只记录在 `task-execution-log.md` 与 continuity handoff。

## Batch 1：设计与 admission

### T11 冻结正式合同

- [x] canonical CLI 已创建 WI-198 四件套并登记 manifest/sequence。
- [x] observed/expected、三种方案、NC-01～NC-06、CC-03/04/06/07 已冻结。
- [x] 产品/测试 LOC、文件数、公共抽象、schema、legacy fresh 迁移与 stop gate 已冻结。
- [x] mainline tree equality、targeted 26 与 focused baseline 33 已记录。

### T12 同哈希双 Agent 设计评审

- [x] 计算 `spec.md + plan.md + tasks.md` bytes 拼接 SHA-256。
- [ ] 兼容安全 Agent 对该哈希 PASS（verdict 见 execution log/handoff）。
- [ ] 精简效率 Agent 对同一哈希 PASS（verdict 见 execution log/handoff）。
- [x] 所有成立 findings 必须修订；目标变化后旧 PASS 同时失效。

## Batch 2：TDD 实现

### T21 RED characterization

- [ ] unit fixture 证明 active linked WI 存在时 build pack 不得读取历史 feature docs。
- [ ] unit 证明旧版本生成但 fingerprint/root/scoped equality 均 fresh 的错误 pack仍会被识别并重建，包括 docs 已被 overlay 修正但 branch 仍历史的场景。
- [ ] unit 边界覆盖 linked missing/partial、无 linked 非标准 feature.spec_dir、persisted overlay、正确 fresh pack不误判，以及 semantic-only working-set/runtime/latest-summary 损坏、无效编码或不可读不新增异常。
- [ ] linked runtime branch 优先；linked 无 runtime branch 为空；无 linked 保留 feature branch。
- [ ] handoff integration 证明 canonical/scoped handoff 和 root/scoped pack 同属 linked WI，legacy fresh pack 可自愈。
- [ ] recover integration 证明 missing/checkpoint-stale/legacy-semantic-stale pack 按 linked WI 重建。
- [ ] RED 至少一项稳定失败于历史路径或 branch 泄漏，非 fixture/解析错误。
- [ ] RED 命令、关键 diff 与失败原因写入 execution log。

### T22 最小 GREEN

- [ ] 仅修改 `src/ai_sdlc/context/state.py` 中冻结的 `load_resume_pack`、pack builder 与两个 working-set builder。
- [ ] 非空 linked id 使用 `specs/<linked>`；无 linked 严格沿用 `feature.spec_dir`。
- [ ] linked target 缺失 fail-closed，不回退历史 docs。
- [ ] legacy fresh 错误 pack 复用 stale rebuild且 expected pack 至多构建一次；正确 fresh pack/persisted overlay 不误判，semantic-only `YamlStoreError`/`UnicodeError`/`OSError` 保持旧成功合同。
- [ ] linked 无 runtime branch 为空；无 linked branch、stage/batch/baseline/fingerprint/schema/error 不变。
- [ ] 三项 RED 与五个 focused 文件全部 GREEN。

### T23 预算与兼容复核

- [ ] 产品净新增 ≤20 LOC，测试新增 ≤140 LOC。
- [ ] 新增产品/测试文件=0、公共抽象=0、依赖/配置/schema=0。
- [ ] CC-03/04/06/07 before/after 证据按 allowlist 规范化，`timestamp`/显式 summary 与 approved path/branch delta 外无漂移。
- [ ] GAP-09～GAP-11、checkpoint migration 与历史 stage 无 diff。

## Batch 3：验证与交付

### T31 Fresh verification

- [ ] 五个 focused 文件全绿。
- [ ] `uv run pytest -q` 全绿。
- [ ] `uv run ruff check src tests` 全绿。
- [ ] `uv run ai-sdlc verify constraints` 无 BLOCKER。
- [ ] `git diff --check` PASS。
- [ ] adapter/test state 副作用未混入提交。

### T32 独立代码与 branch 评审

- [ ] RED reviewer 给出 spec compliant + task quality approved。
- [ ] GREEN reviewer 给出 spec compliant + task quality approved。
- [ ] 兼容安全与精简效率 final branch verdict（见 execution log/handoff）。
- [ ] 所有 Critical/Important/可操作 findings 关闭（见 execution log/handoff）。

### T33 PR、mainline 与父项关闭

- [ ] 推送独立 branch 并创建 WI-198 PR。
- [ ] 请求 Codex review 并维持约五分钟 heartbeat。
- [ ] 当前 HEAD review 无可操作问题且 checks 全绿后合并。
- [ ] mainline targeted 与 truth snapshot fresh。
- [ ] WI-196 Gap Evidence Index 将 GAP-08/T52 标为 closed。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| GAP-08 / T52 | T11～T33 |
| NC-01～NC-03 | T11、T23 |
| NC-04 | T21、T22、T31 |
| NC-05～NC-06 | T11、T23、T33 |
| CC-03/04/06/07 | T21～T23、T31 |
| FR-198-01～04 | T21、T22 |
| FR-198-05～09 | T21～T23、T31～T33 |
| SC-198-01～04 | T21～T23 |
| SC-198-05～07 | T12、T31～T33 |
