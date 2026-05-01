# 任务拆分：Self-update / Update Advisor Runtime

**功能编号**：`185-self-update-update-advisor-runtime`  
**创建日期**：2026-05-01  
**状态**：进行中

## Task 1 — Runtime advisor core

- [x] 实现 installed runtime identity 与 source/editable fail-closed
- [x] 实现 GitHub stable release refresh、cache、freshness、backoff
- [x] 实现 notice eligibility 与 ack 去重

## Task 2 — CLI surfaces

- [x] 新增 `self-update identity/evaluate/check/ack-notice/instructions`
- [x] 全局 CLI Stage 0 自动检测与人类提醒
- [x] `python -m ai_sdlc` help surface 增补 `self-update`

## Task 3 — Tests and close-out

- [x] 新增 unit tests
- [x] 新增 CLI integration tests
- [x] 跑 focused/full verification
- [x] 刷新 program truth
- [x] close-check 执行并进入提交收口
