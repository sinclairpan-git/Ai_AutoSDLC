# Development Summary：WI-200 Adapter Canonical Consumption Truth

**状态**：实现与 T32 验证完成，待最终同 HEAD 双复审、PR/CI 与 mainline closure
**父项**：WI-196 `GAP-10 / T53B`
**最终 formal hash**：`edd7d503ed01beb7bdddd2eb65178b75820d556300e7d6e5f63d76e3f8e046f8`

## 当前结论

- 根因有两层：ProgramService 的 repository release truth 读取 ignored local config/env，导致同 commit 随机器漂移；adapter carrier 又把自身生成并注入的 digest match 误报为 host/session consumption `verified`。
- Commit A `68ff711e` 删除 persisted canonical verified 保留链路，将 digest/path match 固定为 `unverified` + transport evidence + 空 consumed_at；公共 `adapter exec` 命令、参数、timeout、env 注入与退出码不变。
- Commit B `f384f20f` 删除 ProgramService local adapter blocker、专用常量/提示/import；capability goal 明确为 tracked proof/runtime contract delivery，不代表当前 session consumption。
- 现场 truth sync 发现 WI200 self-close 依赖。两名对抗 agent 一致选择非循环修正：truth refs=`121/122/159/200`，close refs=`121/122/159`；200 保留本次实现 truth，T33/T34 不提前完成，close-check filter 不放宽。
- 脱敏 Codex probe 为 `embedded_match=true`，AGENTS sha256=`20cfaecf63092a2294f0154efddecb1e686a7a38bc569de2d2dc962ef1b9db41`，Codex 0.137.0，exit 0，36.573 秒；完整 prompt 未输出或落盘。
- 隔离 worktree 只 revert B 后，临时模块路径已验证：runtime 保持 `unverified` 与 transport evidence，恢复的旧 repository gate 稳定 `blocked`。
- 全量为 `3186 passed, 3 skipped`；全仓 Ruff、constraints、program validate、targeted 与 adapter full slice 均 PASS。
- 产品代码累计 `+6/-74`，净 `-68 LOC`；测试 `+30/-31`，净 `-1 LOC`。未新增公共抽象、fixture、schema、receipt、cache、probe 命令或第二真值源。
- 当前 truth snapshot 为 fresh；`agent-adapter-verified-host-ingress` 已 `closed + ready`，required close refs 121/122/159 全部通过；只保留全局历史 33 条 release migration pending 与既有 source inventory debt。

## 下一步

1. 对 clean HEAD 进行兼容安全与精简效率双 Agent 实现终审。
2. 推送 PR、请求 `@codex review` 并持续 heartbeat；required checks 全绿且无 actionable finding 后合并。
3. fresh `origin/main` 重跑 targeted、truth audit 与无 local config adapter status smoke。
