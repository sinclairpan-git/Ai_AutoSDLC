# WI220 开发总结：普通用户单入口收敛

## 结果

WI220 已把普通用户路径收敛为 `init → run → 有界 Result/Next`，并保留 `status --details`、`status --json`、
高级命令直接调用、既有退出码和 Runner/Loop/AgentOps 行为。参赛版本只作为外部行为参考，没有覆盖主线、复制模块
或引入五 Loop predecessor router。

实现 PR #185 的 exact reviewed head 为 `2cf63d83ca4e2acaa80ec09e286d2b958e43b29b`，已合并为
`origin/main@3258160213ec42291ee9e12244ae3e04ec0431f2`。Codex 对该 exact head 未发现重大问题，GitHub required
checks 23/23 通过。

## 交付边界

- 新增唯一的无持久化默认摘要投影，供 `run` 和 compact `status` 消费。
- 默认 help 只隐藏低频发现面；命令注册、直接调用和高级入口保留。
- compact checkpoint 恢复失败按 unavailable/blocked fail closed；details/JSON 兼容合同保留。
- dry-run 从全部 stage 结果计算 open-gate 真值，项目内路径以相对形式呈现。
- 未新增数据库、状态模型、checkpoint schema、loader、第二聚合器或新的顶层命令。

## 验证与评审

- fresh `origin/main@32581602`：beginner/run/status 相关套件 `108 passed in 59.40s`。
- 目标 Ruff、`verify constraints`、`program validate`、manifest gate 和 `git diff --check` 通过。
- PR #185 六平台兼容矩阵、安装/升级/smoke 等 required checks 最终 23/23 通过。
- exact-head Codex review 在逐项关闭 caller 结果误报、checkpoint 恢复和绝对路径呈现问题后返回无重大问题。

## ROI 与停止线

相对 PR #185 base `e70ced90`，按 Batch 020 改动清单排除 inventory truth 断言
`tests/integration/test_repo_program_manifest.py` 后，产品源码、行为测试和用户文档共 19 个文件，
`+1056/-123`。收益集中在首次使用认知成本、
结果可解释性和兼容恢复安全；实现没有引入第二套运行真值，但整改轮次与测试体量已高于最初乐观估计。

因此 WI220 到此停止：不继续优化文案、renderer、checkpoint 诊断或高级命令分类。任何新增特性必须脱离 WI220，
重新以用户价值、复用面、净代码量和验证成本进行 ROI 立项。

## 主线真值与遗留边界

- 本 records-only closure 补齐结构化 implementation provenance、T43 状态和 close layer；合入 `main` 后才成为
  WI220 的最终归档真值。
- Program Truth 中两个 release capability 仍被 16 个历史 `truth_check` 阻断，属于既有诚实 blocker；本 WI
  不删除 truth refs、不放宽分类，也不把 unrelated blocked 伪写为 ready。
- 用户明确排除的本地材料分支/worktree 不属于远端主线 closeout，未被删除、重命名或修改。
