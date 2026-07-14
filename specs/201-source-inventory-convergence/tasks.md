# 任务分解：Source Inventory Convergence

**编号**：`201-source-inventory-convergence`
**日期**：2026-07-14
**来源**：`spec.md + plan.md`
**父任务**：WI-196 `T54 / GAP-11`

## Batch 1：基线与 formal freeze

### T11 冻结 source debt 与 NC/CC 合同

- **依赖**：无。
- **范围**：记录目标 revision、mainline 1061/1028/33/11、WI-201 投影 1066/1033/33/12、33 个 release 集合、影响文件/符号、NC-01～06、CC-01/02/03/06、预算与回退。
- **完成**：spec/plan/tasks 无 placeholder，范围明确排除 runtime、release 正文和 WP-01～WP-07。
- **验证**：`rg` placeholder 检查、plan §5 Phase 0 唯一命令计算的 formal hash、`git diff --check`；评审 agent 不得另换串联算法。

### T12 双 agent 对抗 formal review

- **依赖**：T11。
- **范围**：Agent A 审兼容、真实性、fail-closed、回退安全；Agent B 审精简、直接性、预算和过度实现。
- **完成**：两者对同一 formal hash 独立 PASS；finding 全部处置并重新双审。
- **证据**：agent、维度、hash、时间、findings、处置、verdict 写入 execution log。

## Batch 2：TDD 与最小修复

### T21 增加仓库 source inventory 完整性断言并取得 RED

- **依赖**：T12、formal baseline commit。
- **文件**：`tests/integration/test_repo_program_manifest.py`。
- **预算**：只改 1 个现有测试文件，新增断言不超过 12 行，不新增 fixture/抽象。
- **完成**：目标测试明确因 WI-201 投影 `unmapped=33` 或 `missing=12` 失败；同时冻结 33 个 `path/release_doc/release` 精确三元组；不是语法/环境错误。
- **验证**：`uv run pytest tests/integration/test_repo_program_manifest.py::test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence -q`。

### T22 登记 33 个 release source

- **依赖**：T21 RED。
- **文件**：`program-manifest.yaml.source_registry`。
- **预算**：恰好 33 entries/99 YAML 行；0 schema/产品代码。
- **完成**：v0.7.5～v0.7.19、v0.8.0～v0.8.10、v0.9.0～v0.9.6 逐项唯一映射为 `release_doc/release`，不修改 release 正文或 discovery。
- **验证**：registry 唯一性检查 + targeted test 中 unmapped 断言。

### T23 补齐 11 个历史 development summary

- **依赖**：T21 RED；可在 T22 后串行对账。
- **文件**：spec §2.2 的 11 个 `development-summary.md`。
- **预算**：每个不超过 25 个非空正文行，无新模板/schema。
- **完成**：每项含真实状态、已交付事实、验证/合并证据、未完成边界；WI-196 不伪报路线完成。
- **停止**：证据无法支持时停止，不写推测，不临时新增 exception 字段。

### T24 补齐 WI-201 development summary

- **依赖**：T22、T23。
- **文件**：`specs/201-source-inventory-convergence/development-summary.md`。
- **完成**：自身不产生 missing source，且仅记录当时真实进度；所有仓库内更新在最终 execute sync 前冻结，终审/PR/mainline 结果只写外部 receipt。

## Batch 3：收敛验证与终审

### T31 GREEN、validate、constraints 与 evidence freeze

- **依赖**：T22～T24。
- **完成**：targeted/full/Ruff/validate/constraints 各完成一次并 PASS；dry-run 确认 1066/1066/0/0、202/202 与两个 capability `closed/ready/[]`；预算、summary、execution log、handoff 和副作用证据全部写回并形成 evidence-freeze clean HEAD。冻结后只复跑 targeted/validate/constraints/dry-run/预算/diff/Cursor，不重复 full/Ruff。
- **附加验证**：`uv run pytest`、`uv run ruff check src tests`、`git diff --check`。
- **副作用控制**：每次 CLI 后确认 `.cursor/rules/ai-sdlc.mdc` 与目标 HEAD 一致；差异只用 `apply_patch` 精确恢复。

### T32 最终 sync、clean-HEAD 只读复验与 rollback drill

- **依赖**：T31 evidence-freeze clean HEAD。
- **完成**：复跑 T31 冻结后定向门禁再执行唯一 execute sync，提交 snapshot-only finalization；此后分支零写入。final clean HEAD 只复跑 targeted/validate/audit/dry-run/constraints/diff，不重复 full/Ruff；临时 clean worktree 按逆序反向 revert 冻结基线 `c737eda056...HEAD`，确认 tree 等于 base，audit 因且仅因 33 unmapped 退出 1，另行断言 missing=11，并精确恢复 1061/1028/33/11 与两个 `closed/ready/[]`；所有 sync 后结果只记录到外部 immutable receipt，随后删除临时 worktree。
- **判定**：任何新增 source debt、`missing!=0` 下的假 ready、capability differential、非 fresh、非 ready、预算超限、产品代码变化、sync 后仓库写入或 rollback drill 偏差均 FAIL。

### T33 双 agent 最终 clean-HEAD review

- **依赖**：T32、clean HEAD。
- **完成**：两个既有 agent 对同一 HEAD 与 rollback receipt 分别从安全真实性与精简直接性独立 PASS；内容变化后从 T31 重新冻结并全部重审。
- **证据**：完整 verdict 与 finding disposition 保存在外部 task receipt，并在 T34 写入 PR comment；不得回写被审分支。

### T34 PR、CI、合并与 mainline smoke

- **依赖**：T33 双 PASS。
- **完成**：推送独立分支、PR、外部 receipts、`@codex review`、heartbeat；Codex 无 actionable finding、required checks 全绿后合并；fresh `origin/main` 证明 merge SHA 与 reviewed HEAD 相关路径等价，targeted/truth audit/constraints 复现 1066/1066/0/0、202/202、两个 `closed/ready/[]`，并把三元组和退出码写入 PR receipt。
- **回退**：revert WI-201 PR；重新 truth sync 恢复目标 revision artifact。

## 追踪矩阵

| 规格 | 任务 |
|---|---|
| FR-01、NC-01～03、NC-06 | T11、T12 |
| FR-02～03、SC-01 | T21、T22 |
| FR-04～06、SC-02 | T23、T24 |
| FR-07～09、SC-03～05 | T21、T31、T32 |
| FR-10～11、SC-06 | T12、T33、T34 |
| FR-12、NC-05～06 | T11、T31～T34 |
| FR-13、SC-04 | T32、T33、T34 |
