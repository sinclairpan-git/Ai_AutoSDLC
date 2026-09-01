---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 任务分解：两轮评审终局 Sponsor 决策收敛合同

**编号**：`225-review-terminal-sponsor-convergence` | **日期**：2026-08-31
**来源**：`spec.md` + `plan.md`
**边界**：仅 G1 formal/admission；`AGENTS.md` 与 runtime/rules execute 均未授权

## 分批策略

```text
Batch 1: 冻结精确主线与真实复发层
Batch 2: 完成方案/ROI admission 与唯一候选
Batch 3: 同步 roadmap/Program Truth、验证、独立评审与 Formal PR
```

三个批次串行执行。任何规则或代码实现只记录为后续候选，不在 WI225 中落地。

## Batch 1：基线与证据

### Task 1.1 冻结远端主线和用户批准边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/225-review-terminal-sponsor-convergence/spec.md`
- **可并行**：否
- **任务**：
  - [x] 固定 `origin/main@e8a73ec409a7eb771abc41dcc996dc198c031a5d`。
  - [x] 记录 WI224 不再修改、旧 heartbeat 删除、G1 仅 formal/admission。
  - [x] 排除参赛版、产品站、本地材料分支和所有 runtime execute。
- **验收标准**：基线、授权与排除范围可独立复核；不存在 #196 或 WI224 继续修复入口。
- **验证**：`git rev-parse origin/main`；`git status --short --branch`。

### Task 1.2 审计现有评审与终态承载

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`AGENTS.md`、`src/ai_sdlc/core/loop_models.py`、`src/ai_sdlc/core/pr_review_service.py`、`src/ai_sdlc/core/pr_review_models.py`、`tests/unit/test_pr_review_service.py`
- **可并行**：否
- **任务**：
  - [x] 核对 repo-local heartbeat 协议缺少两轮后的 terminal sponsor 分支。
  - [x] 核对现有 `needs_user / max_rounds=2` 与错误的 `increase --max-rounds` 提示。
  - [x] 核对稳定 finding signature/history、`risk_accepted`、final report 和 attestation 可复用。
- **验收标准**：能区分真实复发层和仅相邻的 Local PR Review runtime；不以相邻代码存在替代实际因果。
- **验证**：`rg` + 目标源码/测试行人工对账。

## Batch 2：Admission 与止损

### Task 2.1 对抗比较三种落地方案

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/225-review-terminal-sponsor-convergence/spec.md`、`specs/225-review-terminal-sponsor-convergence/plan.md`
- **可并行**：否
- **任务**：
  - [x] 比较 repo-local 协议、Local PR runtime、新 sponsor artifact。
  - [x] 选择只修改根 `AGENTS.md` 的后续候选。
  - [x] 将 runtime 和新 artifact 方案判为 No-Go。
- **验收标准**：只有一个候选；候选作用于真实复发层；没有隐含 schema/状态机扩张。
- **验证**：spec/plan 交叉对账；独立 formal/ROI 评审。

### Task 2.2 冻结候选投入与终止结果

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/225-review-terminal-sponsor-convergence/spec.md`、`specs/225-review-terminal-sponsor-convergence/plan.md`、`docs/framework-defect-backlog.zh-CN.md`
- **可并行**：否
- **任务**：
  - [x] 冻结后续候选为一个规则实现 PR、总投入不超过 0.5 人日。
  - [x] 定义 `unique_delta / effort_cap / terminal_outcome` 三字段与新高风险事实边界。
  - [x] 定义第二文件/runtime/schema/第二例外/post-merge records PR 均触发 No-Go。
- **验收标准**：模型仍可处理真实高风险证据，但不能借其恢复无限修复循环。
- **验证**：`rg -n "unique_delta|effort_cap|terminal_outcome|No-Go|0.5" specs/225-review-terminal-sponsor-convergence docs/framework-defect-backlog.zh-CN.md`。

## Batch 3：Formal 真值与评审

### Task 3.1 同步 roadmap、Program Truth 与固定库存期望

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、`tests/integration/test_repo_program_manifest.py`
- **可并行**：否
- **任务**：
  - [x] 将 G1 状态更新为 WI225 formal/admission，规则 execute 未授权。
  - [x] 同步 Program Truth，并确认原 16 个 blocker 不变。
  - [x] 仅同步固定库存期望到 `1174/1174 mapped`、missing 5、close `218/223`，不修改测试逻辑。
- **验收标准**：inventory complete、unmapped 0；不补 `development-summary.md`；P3/P4/D2 状态不变。
- **验证**：`program validate`、truth sync/audit、manifest regression。

### Task 3.2 完成 continuity、验证、独立评审与 Formal PR

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/225-review-terminal-sponsor-convergence/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/225-review-terminal-sponsor-convergence/codex-handoff.md`
- **可并行**：否
- **任务**：
  - [x] 运行 constraints、plan-check、truth、manifest regression、全量 pytest/Ruff 和 `git diff --check`。
  - [x] 更新 canonical/scoped continuity，并记录 `formal_freeze_only / execution_started=false` 预期。
  - [x] 完成一次独立 formal/ROI 评审；只整改可操作的范围、真值或可执行性问题。
  - [ ] 形成单一语义提交、push、Formal PR、Codex review 与约五分钟 heartbeat。
- **验收标准**：验证通过；评审无可操作问题；PR 不含 `AGENTS.md`、runtime、schema 或 WI224 历史修改。
- **验证**：命令回执、PR exact-head review、required checks。

## 明确禁止的任务

- 不得在 WI225 内修改 `AGENTS.md`；它只是后续唯一候选。
- 不得修改 `src/`、CLI、review model/schema、workflow、release 或 WI224。
- 不得新建 sponsor artifact、ledger、waiver、receipt、certificate 或新状态。
- 不得创建 `development-summary.md` 或以 formal carrier 冒充实现完成。
- 不得在本 Formal PR 合并后自动进入规则实现；必须重新取得 execute 授权。
