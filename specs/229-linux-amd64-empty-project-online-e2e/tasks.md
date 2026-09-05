---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 任务分解：R09 Linux AMD64 空项目在线首次用户闭环

**编号**：`229-linux-amd64-empty-project-online-e2e`  
**来源**：`spec.md` + `plan.md`  
**状态**：formal admission 对抗评审中；implementation 未授权

## Checklist

- [x] T11 冻结 R09-only formal baseline、ROI、allowlist、预算与停止条件。
- [ ] T12 完成产品价值与架构纯洁两位专家的 exact-head 对抗评审并收敛为 PASS0。
- [ ] T13 完成 formal PR、Codex/CI 和 fresh-main 归档；停在 implementation execute gate。
- [ ] T21 在直接 workflow 合同测试中建立 R09/empty/matrix RED（未授权）。
- [ ] T22 在现有单一 POSIX consumer 中最小参数化 R09并取得本地 GREEN（未授权）。
- [ ] T31 在 PR exact HEAD 取得真实 Ubuntu R09 partial receipt 与 R06/R10 回归（未授权）。
- [ ] T32 完成 implementation exact-head 复审、合并与 fresh-main 验收（未授权）。

## Batch 1：formal admission

### Task 1.1 冻结产品合同

- task_id: T11
- status: done
- depends: none
- scope:
  - specs/229-linux-amd64-empty-project-online-e2e/
  - program-manifest.yaml
  - .ai-sdlc/project/config/project-state.yaml
  - docs/FRAMEWORK_ROADMAP.zh-CN.md
- acceptance:
  - R09 用户链路、12 字段 receipt、`partial/proven` 边界和 empty 语义明确。
  - allowlist、220 gross additions、1.5 人日、单 implementation PR 和 No-Go 条件冻结。
  - 不含产品源码、workflow 或测试实现。
- verify:
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program validate
  - uv run ai-sdlc workitem plan-check --wi specs/229-linux-amd64-empty-project-online-e2e --json

### Task 1.2 对抗评审与 formal 收敛

- task_id: T12
- status: pending
- depends: T11
- scope:
  - specs/229-linux-amd64-empty-project-online-e2e/
- acceptance:
  - 产品专家验证真实用户价值、证据强度和 partial/proven 口径。
  - 架构专家验证单 consumer、无新抽象/状态/依赖、allowlist 与预算可执行。
  - 只允许一轮修订；修订后两者均为 PASS0，否则 formal No-Go。
- verify:
  - 两份独立 exact-head 评审记录

### Task 1.3 formal PR 与 execute gate

- task_id: T13
- status: pending
- depends: T12
- scope:
  - formal docs / Program Truth / roadmap / continuity / inventory assertion
- acceptance:
  - formal PR 不含 workflow、tests 行为或 `src/ai_sdlc/**` diff。
  - Codex 当前 HEAD 无可操作意见，required checks 全绿，fresh-main 验收通过。
  - formal 合并后明确停在用户 implementation execute gate。
- verify:
  - gh PR exact-head evidence
  - detached fresh-main constraints / Program validate / plan-check / clean

## Batch 2：TDD 与最小实现（未授权）

### Task 2.1 建立 R09 合同 RED

- task_id: T21
- status: blocked
- depends: T13 + explicit user execute approval
- scope:
  - tests/integration/test_github_workflows.py
- acceptance:
  - 测试要求 R06/R09/R10 三行矩阵、project kind、empty precondition、动态 receipt/artifact。
  - 当前主线因缺少 R09 按预期失败，且不修改生产 workflow 来制造红灯。
- verify:
  - uv run pytest tests/integration/test_github_workflows.py -q -k posix_user_guide

### Task 2.2 最小参数化现有 consumer

- task_id: T22
- status: blocked
- depends: T21
- scope:
  - .github/workflows/macos-user-guide-e2e.yml
  - tests/integration/test_github_workflows.py
- acceptance:
  - 单 job/单 replay 承载 R06/R09/R10，R09 empty，R06/R10 existing。
  - 不改 runtime、schema、producer、依赖、用户指南，不新建 workflow/helper。
  - workflow + 直接测试 gross additions <=220。
- verify:
  - uv run pytest tests/integration/test_github_workflows.py -q
  - uv run ruff check tests/integration/test_github_workflows.py
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program validate

## Batch 3：真实环境认证与收口（未授权）

### Task 3.1 真实 Ubuntu R09 首验

- task_id: T31
- status: blocked
- depends: T22
- scope:
  - implementation PR exact HEAD workflow run/artifact
- acceptance:
  - R09/Linux AMD64 job 成功并上传合法 `partial` receipt。
  - 空目录、init、Result/Next、recover 均有同一 artifact 证据。
  - 同 matrix 的 R06/R10 回归通过。
- verify:
  - GitHub Actions exact-head run + downloaded artifact inspection

### Task 3.2 exact-head 合并收口

- task_id: T32
- status: blocked
- depends: T31
- scope:
  - tasks / execution log / roadmap / Program Truth / continuity
- acceptance:
  - 两位独立实现评审 PASS0、Codex current-head clean、required checks 全绿。
  - 合并后 detached fresh-main 验证；R09 只写 `partial`，不得写 `proven`。
- verify:
  - PR/merge/fresh-main evidence

## 固定止损

- formal 一轮修订后仍有 Important/Critical：No-Go，不创建 dev 分支。
- implementation 超出一个 PR、两轮确定性修复、220 gross additions或冻结 allowlist：No-Go。
- 需要新 workflow/helper/runtime/schema/producer/依赖/用户指南正文：No-Go 或重新 formal 准入。
- 不创建第二 WI、records-only PR 或为本项单独发布版本。
