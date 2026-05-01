# 执行计划：Self-update / Update Advisor Runtime

**功能编号**：`185-self-update-update-advisor-runtime`  
**创建日期**：2026-05-01  
**对应规格**：[`spec.md`](./spec.md)

## 1. 实现切片

1. Runtime identity 与 fail-closed 判定
2. GitHub stable release refresh、用户级 cache、freshness/backoff
3. Notice eligibility、ack 去重、双语 CLI 提醒
4. `self-update` helper machine contract 与显式更新 instructions
5. 全局 CLI Stage 0 hook
6. 单元测试、CLI 集成测试、约束验证与 close-check

## 2. 设计约束

- 不在用户不确认的情况下执行安装、替换文件或升级 Python 环境
- 不让 update advisor 改变主命令退出码
- 不在 `--help`、`--json`、completion、source/editable runtime 中输出人类提醒
- helper machine output 是 IDE/AI 后续集成的唯一判断面

## 3. 验证策略

- focused unit tests：runtime identity、notice eligibility、backoff、stale cache、ack
- focused CLI tests：`self-update identity/evaluate` JSON、交互提醒去重、source runtime 静默
- regression smoke：`python -m ai_sdlc --help`
- governance：`ruff`、`verify constraints`、`workitem close-check`
