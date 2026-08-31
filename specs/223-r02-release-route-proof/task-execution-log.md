# 任务执行日志：R02 正式发布路线证明载体

**功能编号**：`223-r02-release-route-proof`
**创建日期**：2026-08-30
**状态**：Batch 002 review remediation；dev `needs_user`

## 1. 归档规则

- 每批开始前预读 PRD/宪章、WI222 合同、当前 spec/plan/tasks 与相关 workflow。
- 每批先实现和验证，再在本文件追加结果；同一逻辑批次的代码、测试、task 勾选与 execution log 使用一次提交。
- formal 与 dev 使用独立分支/PR；未通过 formal review 不进入实现。
- 不记录推测性提交 SHA，不通过追改历史 execution log 制造完成状态。

## 2. Batch 2026-08-30-001 | T11 formal 与特征化闸门

### 2.1 范围与预读

- worktree：`/Users/sinclairpan/project/Ai_AutoSDLC/.worktrees/223-r02-release-route-proof`
- branch：`feature/223-r02-release-route-proof-docs`
- base：`origin/main@49d43c459cdabe5d3664dafd4600192c01333500`
- 预读：`.ai-sdlc/memory/constitution.md`、WI222 spec/plan、路线图 P3、两个 Windows 相关 workflow、现有 recover tests。
- 排除：产品站/比赛材料、本地材料分支、未合并历史 worktree、runtime/installer/version/D2/P4。

### 2.2 改动前基线

- `uv run pytest -q`
- 结果：`3407 passed, 3 skipped in 957.27s`。

### 2.3 半天闸门证据

1. `gh release view v0.9.8 --repo sinclairpan-git/Ai_AutoSDLC --json tagName,targetCommitish,publishedAt,url,assets`
   - Windows asset：`ai-sdlc-offline-0.9.8-windows-amd64.zip`
   - digest：`sha256:0ed406cc9280a285478fdff5e52b322cce6331c7ed6769a8b50099a4ef4bdc72`
   - target commit：`4f3e55c300dab20fb4fea93818d79394a927f77e`
2. `gh run view 33084560424 --repo sinclairpan-git/Ai_AutoSDLC --json event,headSha,workflowName,url,jobs`
   - `event=release`、head 同 tag commit，Windows/macOS/Linux jobs 均 success。
   - 旧 run 缺 R02 生命周期/恢复/receipt，不能追认 `proven`。
3. 当前 Windows guide workflow 已覆盖 install、direct shim、init/adopt、`Result / Next`、业务文件 SHA256 保持；release smoke 已覆盖正式 asset 下载/安装。
4. `tests/integration/test_cli_recover.py` 已证明损坏 resume pack 后公开 `recover` 可重建；实现只调用既有能力。

### 2.4 对抗结论

- **主张方**：R02 可复用两条既有路径，正式 asset digest 机器可得，用户价值高。
- **反方**：旧 release run 无法追认；复制 workflow 会再次膨胀；手工 dispatch 不能冒充 release event。
- **Lean 合议**：只允许一个共享执行器、两个薄调用、一个临时 receipt；不设置机械 LOC blocker，但禁止平行状态与第三份实现。
- **决策**：`Go`。实现目标 1.5–2.5 人日、硬上限 3 人日；真实 release receipt 之前 R02 保持 `partial`。

### 2.5 本批文件

- `specs/223-r02-release-route-proof/{spec.md,plan.md,tasks.md,task-execution-log.md}`
- `docs/FRAMEWORK_ROADMAP.zh-CN.md`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `.cursor/rules/ai-sdlc.mdc`（workitem init 根据当前 canonical rule 自动刷新；提交前单独核对是否仅为生成同步）
- continuity 文件在本批验证后更新。

### 2.6 本批验证

- `uv run ai-sdlc workitem plan-check --wi specs/223-r02-release-route-proof`
  - `Pending todos=0`、`Drift=NO`。
- `uv run ai-sdlc program validate`
  - `PASS`。
- `uv run ai-sdlc program truth sync --dry-run`
  - snapshot `blocked`；原 16 blocker 保持；`1169/1169 mapped`、missing `4`、close `218/222`。
- `uv run ai-sdlc program truth sync --execute --yes`
  - 写入 snapshot hash `f9336bc3da77487f6a8e70403e23432eb3ff07f4b3f00ecf4e74ac69d55b39d0`；状态与 blocker 未漂白。
- `uv run ai-sdlc verify constraints`
  - `no BLOCKERs`。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`
  - 首次与 continuity relink 并发运行，断言通过但 teardown 正确报告仓库状态在测试期间变化；停止并发写入后独立重跑，`1 passed in 151.97s`。
- `git diff --check`
  - `PASS`。

### 2.7 审查与任务同步

- spec 覆盖 WI222 的 12 字段、R02 单路、事件分级、主动恢复和资产 digest。
- plan/tasks 没有 `TBD` 或实现占位；测试、脚本和 workflow 接口一致。
- `tasks.md` 的 T11 已完成；T21–T61 保持未执行，formal 不声称代码已落地。
- `workitem init` 触发的无关 Cursor rule 刷新已识别；formal 提交前恢复为 exact-main 内容。
- continuity 已从关闭的 WI222 重新 link 到 WI223；WI222 scoped handoff 无 diff。

### 2.8 本批结论

- formal 范围与 Go/No-Go 证据完整，允许进入独立 PR review。
- 未修改 runtime、workflow、installer、release/version 或历史 work item log。
- review clean 且 required checks 通过前，不创建 dev 实现提交。

### 2.9 disposition

- formal branch：`merge-pending`
- worktree：`retained(formal review and later dev transition)`
- 下一步：完成 formal 验证与 continuity，提交并创建 formal PR；review clean 后才进入 dev 分支。

## 3. Batch 2026-08-30-002 | Codex review remediation

### 3.1 Review findings 与核验

- P1：资产 digest 未绑定 build source commit。核验 `.github/workflows/release-build.yml`：checkout 未使用 `ref: inputs.tag`，而上传步骤可对目标 release 执行 `--clobber`；finding 成立。
- P2：提交中的 canonical/scoped handoff 仍记录未跟踪文件和待提交步骤；finding 成立。
- P2：`git diff --check HEAD^ HEAD` 报告 spec/tasks/execution log 的 Markdown 行尾空格，而 Batch 001 只检查了提交后的空 working tree；原 PASS 证据口径不完整，finding 成立。

### 3.2 聚焦整改

- 把 build provenance 纳入 `source_binding` 硬条件；仅 release metadata + asset digest 不再允许 `proven`。
- 原授权不含 `release-build.yml` 或 attestation，故 dev 状态从 `implement` 修正为 `needs_user`，不自行创建实现分支。
- 删除本批新增 formal 文档的行尾空格，并改用 commit-range diff-check。
- 本批内容提交后，从 clean committed state 重新生成 canonical/scoped handoff；不得保留待 commit/push 的过期步骤。

### 3.3 边界

- 本批只修改 WI223 formal、路线图、truth/continuity；不修改 workflow、runtime、installer、release/version 或历史 work item log。
- 若用户不批准 build provenance 扩展，WI223 以 formal No-Go 收口；若批准，再建立新的 bounded dev 计划。

### 3.4 Truth 与 focused 验证

- `workitem plan-check`：`Pending todos=0`、`Drift=NO`。
- `program validate`：`PASS`。
- Program Truth dry-run：原 16 blocker、`1169/1169 mapped`、missing `4`、close `218/222` 保持。
- Program Truth execute：snapshot hash `0a34feef4644dfdd1092bbaf9cdd6d075d5e6d8ebef41a86209275b1fd1ab7f0`；状态保持 `blocked`。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：`1 passed in 145.79s`，无并发状态写入。
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`。
- `git diff --check` 与 formal 文档行尾扫描：`PASS`；提交后还必须执行 commit-range diff-check。
