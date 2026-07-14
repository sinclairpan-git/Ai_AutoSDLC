---
related_plan: "specs/199-frontend-inheritance-truth/plan.md"
related_doc:
  - "specs/199-frontend-inheritance-truth/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 任务分解：Frontend Inheritance Truth Closure

**编号**：`199-frontend-inheritance-truth` | **父任务**：GAP-09 / T53A

## Batch 1：事实、设计与对抗 admission

### T11 冻结 before evidence

- **文件**：`task-execution-log.md`
- **动作**：记录两个 handoff 的 `frontend_solution_snapshot_missing`、truth 的两个 GAP-09 blocker、16 个 capability carrier 的 `framework_capability` 分类与已有框架能力 observation waiver。
- **完成**：证据可由当前 checkout 命令复现；不运行 solution-confirm execute。

### T12 冻结原子合同

- **文件**：`spec.md`、`plan.md`、`tasks.md`
- **动作**：冻结 scope/non-goal、方案/拒绝方案、NC/CC、151/290 LOC（PR P2 后实测 150/289，各留 1 LOC）、正常多行格式、无伪 snapshot、allowlist、entry/done/stop/rollback 与 exact truth delta。
- **完成**：三件套无 placeholder、无第二真值源、无前端实现授权扩张。

### T13 双 Agent 同哈希评审

- **依赖**：T11、T12
- **动作**：兼容安全 Agent 与精简效率 Agent 独立复算 `spec.md + plan.md + tasks.md` hash；修订所有成立 finding 后重跑。
- **完成**：同一 hash 双 `PASS`、均为“未发现可操作问题”；目标变化自动失效。

## Batch 2：严格 RED → 最小 GREEN

### T21 RED characterization

- **依赖**：T13
- **文件**：`tests/unit/test_program_service.py`、`tests/unit/test_frontend_quality_platform.py`；后者只新增 public validator 传 `None` 必须失败的负向禁止测试；允许 `tests/integration/test_cli_status.py` 仅更新既有 consumer status fixture 的 blocker 精确集合；只有 repo map 必须随 truth blocker 集合变化时才允许修改 `tests/integration/test_frontend_mainline_blocker_execution_map.py`。
- **fixtures**：framework-only 健康 artifacts 无 snapshot；generation/quality canonical manifest missing/malformed/cross-ref 损坏与 truth path/reason guidance；canonical provider manifest missing、declared install strategy missing；schema-valid generation page/provider/packages semantic drift、delivery entry empty；`execution_order`、`recipe`、`whitelist`、`hard_rules`、`token_rules`、`exceptions` 六类 weakening；consumer unknown/not-inherited/blocked；missing ref、mixed class、canonical footer missing/empty/malformed、mirror conflict；framework waiver 下非 inheritance remediation 保留；public quality validator `None` 禁止；raw handoff status。
- **完成**：旧实现因缺 requirement/health 判定、consumer 非 inherited 映射不足或 validator 不接受 framework context 而失败；失败均来自冻结合同而非 fixture 错误。
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/unit/test_frontend_quality_platform.py -q`，并记录目标失败集合。

### T22 最小 GREEN

- **依赖**：T21
- **文件**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/frontend_quality_platform.py`
- **动作**：实现 frontend-mainline-only 的 footer+mirror 全称判定和 schema/semantic framework artifact health；canonical provider/strategy 文件存在性必须在 fallback loader 前验证；generation 六类治理面与 provider-context builder baseline 精确对账；quality 内部一致性只走私有 helper，公开 validator 不变；让 release blocker、guidance、surface 复用 requirement；framework waiver 保留非 inheritance remediation；原始 inheritance status/handoff 不变。
- **完成**：T21 全绿；产品净新增 ≤151 LOC、测试新增 ≤290 LOC；正常多行格式，无伪 snapshot、无物理压行；除获准 canonical YAML 修正外无新文件/公共 API/依赖/config/schema。

## Batch 3：验证、审计与独立复审

### T31 分层验证

- **依赖**：T22
- **命令**：
  1. `uv run pytest tests/unit/test_program_service.py tests/unit/test_frontend_quality_platform.py -q`
  2. `uv run pytest tests/integration/test_cli_status.py::test_status_json_blocks_frontend_inheritance_drift_in_truth_ledger -q`
  3. `uv run pytest tests/integration/test_frontend_mainline_blocker_execution_map.py -q`（如受影响）
  4. `uv run pytest -q`
  5. `uv run ruff check src tests`
  6. `uv run ai-sdlc verify constraints`
  7. `git diff --check`
- **完成**：全部通过；Cursor adapter 等非授权副作用已核对并精确恢复。

### T32 Truth closure 与父项同步

- **依赖**：T31
- **动作**：同步/审计 truth snapshot；更新本项 execution log/development summary、WI-196 GAP index、WI-198 mainline closure 与 continuity handoff。
- **完成**：snapshot fresh；健康仓库只移除两个 GAP-09 blocker且不新增 framework artifact blocker；GAP-10/GAP-11 状态有精确 retained evidence。

### T33 最终双 Agent 评审

- **依赖**：T32
- **动作**：两个原维度 Agent 对同一 clean HEAD 复核实现、测试、truth delta、预算和回退。
- **完成**：同一 HEAD 双 PASS；任何 finding 回到 T21/T22 并使旧 verdict 失效。

## Batch 4：PR、Codex 与 mainline closure

### T41 独立 PR 闭环

- **依赖**：T33
- **动作**：push、建 PR、请求 `@codex review`、heartbeat 监控；actionable finding 在同分支修复并重新验证/评审。
- **完成**：Codex 无可操作问题、required checks 全绿、PR squash merge。

### T42 Mainline evidence

- **依赖**：T41
- **动作**：在合并 commit 等价 checkout 重跑定向测试、constraints 与 truth audit，更新 WI-196 GAP-09 为 closed。
- **完成**：mainline 不含两个 GAP-09 blocker，无回归；进入 GAP-10/T53B。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| FR-01～FR-04、CC-01/03 | T21、T22、T32 |
| FR-05～FR-07、FR-09～FR-10、CC-02/04/05 | T21、T22、T31、T32 |
| FR-08、预算/停止/回退、可读性 | T13、T22、T33 |
| SC-01 | T13、T33 |
| SC-02～SC-05 | T21～T33 |
| SC-06 | T41、T42 |
