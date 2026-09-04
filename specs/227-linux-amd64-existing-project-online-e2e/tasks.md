# 任务分解：R10 Linux AMD64 已有项目在线 E2E

**编号**：`227-linux-amd64-existing-project-online-e2e`  
**来源**：`spec.md` + `plan.md`

## Checklist

- [x] T11 冻结 R10-only formal baseline、范围与停止条件。
- [ ] T21 以直接 workflow 合同测试建立 R10 matrix RED。
- [ ] T22 参数化现有 R06 POSIX consumer 并取得本地 GREEN。
- [ ] T31 在 PR exact HEAD 上取得真实 Ubuntu R10 `partial` receipt。
- [ ] T32 完成 exact-head 复审、合并与主线核验。

## Batch 1：formal baseline

### Formal baseline T11：冻结单工作项执行合同

- **状态**：done
- **范围**：`specs/227-linux-amd64-existing-project-online-e2e/`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`
- **验收标准**：基线、范围、单分支/单 PR、真实 Ubuntu 首验和停止条件已明确；没有 runtime、schema、producer 或其他路线授权。

## Batch 2：TDD 与最小参数化

### Task 2.1 建立 R10 matrix RED

- task_id: T21
- status: todo
- depends: none
- scope:
  - tests/integration/test_github_workflows.py
- acceptance:
  - 验收标准：测试要求恰好 R06/R10 两行、匹配 runner/OS/arch/asset/shell，以及动态 receipt/artifact 绑定；在 workflow 未实现时按预期失败。
- verify:
  - .venv/bin/python -m pytest tests/integration/test_github_workflows.py -q -k macos_user_guide

### Task 2.2 参数化现有 consumer

- task_id: T22
- status: blocked
- depends: T21
- scope:
  - .github/workflows/macos-user-guide-e2e.yml
  - tests/integration/test_github_workflows.py
- acceptance:
  - 验收标准：单 job/单 run block 同时承载 R06 与 R10；直接测试和完整 workflow 测试通过。
- verify:
  - .venv/bin/python -m pytest tests/integration/test_github_workflows.py -q

## Batch 3：真实环境认证与收口

### Task 3.1 真实 Ubuntu 首验

- task_id: T31
- status: blocked
- depends: T22
- scope:
  - docs/FRAMEWORK_ROADMAP.zh-CN.md
  - specs/227-linux-amd64-existing-project-online-e2e/task-execution-log.md
- acceptance:
  - 验收标准：Ubuntu AMD64 job 成功并上传合法 R10 partial receipt；macOS R06 同时成功。
- verify:
  - GitHub Actions exact-head run and artifact receipt

### Task 3.2 exact-head 合并收口

- task_id: T32
- status: blocked
- depends: T31
- scope:
  - specs/227-linux-amd64-existing-project-online-e2e/tasks.md
  - specs/227-linux-amd64-existing-project-online-e2e/task-execution-log.md
- acceptance:
  - 验收标准：required checks 全绿、一次 Codex review 无可操作问题、合并树等于候选树；R10/R02 均不越权写成 proven。
- verify:
  - PR checks and review plus origin/main tree equality

## 固定止损

- 最多两轮确定性、同路径聚焦修复；API/网络/runner 排队不计轮次。
- 需要改 runtime/schema/release producer、复制完整 workflow 或触及其他路线时立即 No-Go。
- 不创建第二 WI、第二分支、第二 PR，也不为 receipt 单独发版。
