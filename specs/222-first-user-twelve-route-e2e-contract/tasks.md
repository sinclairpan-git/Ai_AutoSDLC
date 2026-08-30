---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 任务分解：跨平台首次用户十二路线证据合同

**编号**：`222-first-user-twelve-route-e2e-contract`
**日期**：2026-08-30
**来源**：`spec.md` + `plan.md`
**边界**：仅 P3-A formal/admission；所有 runtime/workflow/release 任务均未授权

## 分批策略

```text
Batch 1: 冻结精确基线与十二路线合同
Batch 2: 完成证据普查、ROI 对抗与最小薄片建议
Batch 3: 同步 roadmap/Program Truth、验证、独立评审与 PR
```

三个批次串行执行，避免基线、证据分类和真值同步互相漂移。任何发现需要修改 runtime、workflow 或 release 的事项，只记录为后续候选，不在 WI222 内实现。

## Batch 1：基线与合同

### Task 1.1 冻结远端主线与范围

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`
- **可并行**：否
- **任务**：
  - [x] 记录 `origin/main@2e507df62c65cdd6d3137764bb492dc445a82074` 与正式 release/tag 基线。
  - [x] 明确忽略产品站、本地材料分支、未合并 worktree 和参赛版实现。
  - [x] 固定 formal-only、D2/P4/release/runtime 不在范围及唯一库存测试例外。
- **验收标准**：基线和排除范围均可从 `spec.md` 单独复核；不存在 runtime execute 授权暗示。
- **验证**：`git rev-parse HEAD`；`rg -n "真值基线|本次不覆盖|唯一允许" specs/222-first-user-twelve-route-e2e-contract/spec.md`

### Task 1.2 定义十二路线与证据状态合同

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`
- **可并行**：否
- **任务**：
  - [x] 定义 R01–R12，完整覆盖 3 × 2 × 2 组合。
  - [x] 定义每路线 12 个最小证据字段。
  - [x] 定义 `proven / partial / missing`，禁止间接证据升级状态。
- **验收标准**：12 个 route ID 唯一；每条路线都有平台、项目模式、获取模式；`proven` 有完整证据前置条件。
- **验证**：路线表人工对账 + `rg -n "R0[1-9]|R1[0-2]" specs/222-first-user-twelve-route-e2e-contract/spec.md`

## Batch 2：证据普查与 ROI 决策

### Task 2.1 逐路映射现有证据并去重缺口

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`、`USER_GUIDE.zh-CN.md`、`.github/workflows/windows-user-guide-e2e.yml`、`.github/workflows/windows-offline-smoke.yml`、`.github/workflows/posix-offline-smoke.yml`、`.github/workflows/release-artifact-smoke.yml`
- **可并行**：否
- **任务**：
  - [x] 对 R01–R12 分别登记已有主线证据和缺失字段。
  - [x] 固定当前结论 `0/12 proven、12/12 partial、0/12 missing`。
  - [x] 将重复缺口收敛为最多 6 个共性缺口。
- **验收标准**：没有路线被错误宣称为从零缺失，也没有路线因共享 smoke 被错误标记为 `proven`。
- **验证**：逐路路径复核；独立 formal 评审重点检查证据过度声明。

### Task 2.2 完成对抗 ROI、止损边界和单一薄片建议

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`、`specs/222-first-user-twelve-route-e2e-contract/plan.md`
- **可并行**：否
- **任务**：
  - [x] 记录 P3-A 不超过 1 人日、完整 P3 维持 6–10 人日的投入边界。
  - [x] 写明第二套状态机/ledger、大量 workflow 复制、无关 runtime 扩张等 No-Go。
  - [x] 只保留 R02 正式 release 路线 receipt 作为一个后续最小薄片，且标记未授权执行。
- **验收标准**：建议数量为 1；薄片可独立提升一条路线；具备半天 Lean/ROI 复核和明确退出条件。
- **验证**：`rg -n "后续最小薄片|No-Go|未授权" specs/222-first-user-twelve-route-e2e-contract/spec.md specs/222-first-user-twelve-route-e2e-contract/plan.md`

## Batch 3：真值与 formal 收口

### Task 3.1 同步 roadmap、manifest 与固定库存期望

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、`tests/integration/test_repo_program_manifest.py`
- **可并行**：否
- **任务**：
  - [x] 将 P3 状态更新为 WI222 formal/admission 进行中，runtime 未授权。
  - [x] 同步 Program Truth，核对新增 WI222 只增加 formal source 和缺失 `development-summary.md`。
  - [x] 仅调整固定库存与 close layer 期望，不修改测试逻辑。
  - [x] 确认既有 16 个 D2 blocker 和 11/16 admission 结论保持不变。
- **验收标准**：Program Truth inventory 完整、unmapped 为 0；close materialized 不因伪造总结而增加；D2 状态不变。
- **验证**：`uv run ai-sdlc program validate`；`uv run ai-sdlc program truth sync --dry-run`；`uv run pytest tests/integration/test_repo_program_manifest.py -q`

### Task 3.2 完成验证、continuity 与独立 formal 评审

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/222-first-user-twelve-route-e2e-contract/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/222-first-user-twelve-route-e2e-contract/codex-handoff.md`（scoped `resume-pack.yaml` 按 `.gitignore` 仅作本地恢复缓存，不强制入库）
- **可并行**：否
- **任务**：
  - [x] 运行 constraints、plan-check、program validate/truth、focused tests、Ruff 和 `git diff --check`。
  - [x] 更新 execution log 与 continuity，记录实际结果和 branch/worktree disposition。
  - [x] 请求一次独立对抗 formal/ROI 评审，只整改可操作的 P0/P1 或真值 P2。
  - [ ] 无可操作问题后形成单一语义 commit、push、PR 和 Codex review；仍不进入 runtime execute。
- **验收标准**：所有验证通过；评审无可操作问题；formal PR 只包含允许范围；后续薄片保持未授权。
- **验证**：`git diff --check`；`git status --short`；execution log 中的命令回执；PR exact-head review。

## 禁止生成的任务

- 不得新增 `src/`、workflow、installer、用户指南实现任务。
- 不得把 R03–R12 展开为 10 个复制式 follow-up WI。
- 不得补 `development-summary.md`、删除 Program Truth blocker 或启动 v0.9.9。
- 不得因评审偏好新增 route ledger、waiver、certificate、dashboard 或第二套 close 状态。
