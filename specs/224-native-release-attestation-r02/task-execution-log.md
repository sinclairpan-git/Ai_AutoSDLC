# 任务执行日志：原生发布制品证明与 R02 强验证

**功能编号**：`224-native-release-attestation-r02`
**创建日期**：2026-08-31
**状态**：PR #194 实现已合并；records/truth/continuity-only post-merge closeout 进行中；R02 保持 `partial`

## Batch 2026-08-31-001 | T11–T12 formal

- **范围**：停止 WI223 自定义 sidecar；验证原生 attestation；建立 WI224 bounded formal。
- **远端证据**：PR #191 closed/unmerged；archive ref exact `6d0f6c83214eb44b2ed22f2b182763880bcdd023`；spike run `33366044473` success。
- **本地证据**：spike workflow test RED（文件缺失）后 GREEN `10 passed`；constraints 无 BLOCKER；下载 ZIP SHA256 `d427bbf10d318310d5c9f2014441f2ee865e481b9b8789b38a772b56b9f5c85a`；`gh attestation verify` exact repo/workflow/ref/digest/hosted-runner 通过。
- **关键决策**：WI223 不合并；WI224 跳过已归档的序号 223，避免跨 ref 同号双真值；正式实现只改 2 workflow + 1 test。
- **formal truth**：continuity 后最终 execute 已写入 `program-manifest.yaml`，精确 hash 以其 `truth_snapshot.snapshot_hash` 为准；状态 blocked/fresh；16 blockers 保留；inventory `1169/1169`、missing `4`、close `218/222`。
- **formal 验证**：constraints 无 BLOCKER；plan-check `Drift=NO`；program validate PASS；workflow tests `9 passed`；manifest truth test `1 passed in 122.12s`；Ruff 与 diff-check PASS。
- **Lean 自审**：formal 主体 245 行；未来产品改动严格限定 2 workflow + 1 test，0 新 runtime/状态/sidecar/workflow/通用抽象。
- **PR 评审状态**：formal PR #192 已创建；首轮 handoff P2 已在 `89ba139d` 修复；第二轮 execution-log P2 已确认，用户仅授权本次单文件最终例外，下一状态固定为 final review，只有无可操作问题且 required checks 全绿才允许合并。
- **分支处置**：formal=`merge-pending`；spike=`retained(no-merge evidence)`。

## Batch 2026-08-31-002 | T12 post-merge truth closeout

- **合并证据**：PR #192 final reviewed head `9a61ca7da39c5beca93e8eac2030e324d23483be` 无 finding，全部 required checks 通过；squash merge 后 exact `origin/main@547e78fd4f03083f2e8c6bb6d258523c8776b0d7`。
- **执行真值**：exact main 分类 `formal_freeze_only`、`execution_started=false`、`contained_in_main=true`；尚无 workflow/runtime 实现，不虚报 execute 已启动。
- **Program Truth**：合并后审计为 stale，仅因最终 execution-log authoring 未进入上一个 snapshot；本批只刷新 truth/roadmap/continuity，保留 16 blockers 与 `1169/1169`、missing `4`、close `218/222`。
- **下一步**：closeout clean/green 合并后，从新的 exact main 创建 dev worktree，按 T20 的 RED 测试启动 bounded execute。
- **分支处置**：formal=`mainline_merged`；closeout=`mainline_merged`；spike=`retained(no-merge evidence)`。

## Batch 2026-08-31-003 | T20–T21 producer RED→GREEN

- **开发基线**：PR #193 squash merge 后 exact `origin/main@1f6f3eba3ff429e7e7a175c6f1545ccec7360925`；dev 分支 `feature/224-native-release-attestation-r02` 从该提交创建。
- **基线验证**：实现前全量 `uv run pytest -q` 为 `3407 passed, 3 skipped in 919.71s`；focused workflow tests 为 `9 passed`。
- **RED**：仅新增 producer 合同测试后，同一 focused 命令为 `3 failed, 9 passed`；失败分别对应 checkout 未绑定 tag、三项原生 attestation 权限缺失、`actions/attest@v4`/复验步骤缺失。
- **GREEN**：Release Build 增加精确 tag/commit guard、原生签发、按 repo/signer/ref/digest/hosted-runner 复验，并复用同一 smoke-passed asset path 后，同一 focused 命令为 `12 passed`；Ruff、YAML parse、`git diff --check` 均通过。
- **范围/Lean**：产品改动仍为 1 个既有 workflow + 1 个既有测试文件；0 新 runtime、依赖、状态、sidecar、workflow 或通用抽象。测试只保护 tag、权限、顺序和 fail-closed 合同，不复制 workflow 实现。
- **下一步**：提交并推送 producer checkpoint，从 exact dev head 创建临时 tag，以 `upload_to_release=false` 调度三平台 Release Build；远端失败且不能在范围内聚焦修复则 No-Go，成功后才进入 T30。

## Batch 2026-08-31-004 | T41 producer remote canary

- **精确身份**：dev checkpoint/tag 为 `0c6c9d6d43f98dcfd169f418e6f6dc616c996c4b` / `spike-native-release-attestation-0c6c9d6d`；Release Build run `33387100262` 由 `workflow_dispatch` 和 exact tag ref 触发，输入 `upload_to_release=false`。
- **三平台结果**：Windows job `99472083502`、macOS job `99472083618`、Linux job `99472083702` 全部 build/smoke/attest/verify success；release upload 均按条件跳过，`gh release view` 确认该 tag 没有 Release。
- **原生证明**：Windows `sha256:c63e2b0d684dcae47693d7da7e9d8d7ef913a91e3372eccf5d9a9d72e67feafa` / attestation `44121736`；macOS `sha256:13f4d7a9dceda845e3137efa7225ff0129c56f36011736cfbfc190a83b6fed5e` / `44121642`；Linux `sha256:89d9a17ba2aac316413e36a3dd711cd36ae7cab870cee6c316427e7f460a9c98` / `44121583`。每个平台均用 exact repo、`release-build.yml` signer、tag ref、commit digest 和 hosted-runner 限制完成复验；repository attestation API 每个 digest 返回 1 条记录。
- **决策**：producer fail-fast gate 通过，允许进入 T30/T31；未创建版本、Release、sidecar 或持久化状态。

## Batch 2026-08-31-005 | T30–T31 consumer RED→GREEN

- **RED**：仅增加 natural-release/recovery receipt 合同测试后，focused suite 为 `2 failed, 12 passed`；失败分别对应缺少 `release.published` 与缺少 resume-pack corruption/recover/receipt。
- **GREEN**：现有 Windows E2E 增加自然 release tag checkout、动态 package/tag、同 tag 指南保护、下载后解压前 attestation 强验证、主动破坏并恢复 resume-pack，以及 12 字段 `route-receipt.json`；同一 focused suite 为 `14 passed`。
- **状态边界**：PR 和 `workflow_dispatch` receipt 固定为 `partial`；只有 `release.published` 且 attestation、安装、init/adopt、Result/Next、业务 hash 与 recover 全部成功，脚本执行到末尾时才写 `proven`。
- **manual 真实回放**：exact head `8c65f652e3f876fc322f9492e418c4a6d9a922fc` 的 Windows run `33388433742` / job `99476251047` success；下载 evidence 后验证 receipt 恰为 12 字段、`route_id=R02`、`status=partial`、`acquisition_mode=published_release_manual`、`attestation_verified=false`，recover log 含 rebuilt success，业务文件前后 hash 相同。
- **范围/Lean**：仍只修改两个既有 workflow 和一个既有测试文件；receipt 进入现有临时 evidence artifact，0 新 runtime、依赖、状态、sidecar、workflow 或通用抽象。
- **下一步**：进入 T42 全量验证、Lean 复核与开发 PR；实现合并仍保持路线真值 `0/12 proven、12/12 partial`，等待未来自然 release receipt。

## Batch 2026-08-31-006 | T42 full verification / Lean

- **全量验证**：冻结同一候选后，`uv run pytest -q` 为 `3412 passed, 3 skipped in 890.16s`；此前 focused `14 passed`、Ruff、YAML、内嵌 PowerShell AST、constraints、plan-check、program validate、`git diff --check` 均通过。
- **变化预算**：产品改动净限于 `release-build.yml +53/-3`、`windows-user-guide-e2e.yml +96/-8`、`test_github_workflows.py +140/-2`；测试与两个 workflow 的新增量约 1:1，不存在测试细节数倍于核心实现。无新增文件，0 新 runtime/依赖/状态/sidecar/workflow/通用抽象。
- **400 行信号**：测试文件当前 409 行，仅作为 advisory；新增合同直接覆盖 149 行 workflow 行为、RED→GREEN 与两次远端真实回放，未伴随复杂 helper、耦合或职责扩张，不升级为 REQUIRED。
- **剩余真值**：实现 PR 只能证明 producer 和 manual partial；自然 `release.published` 尚未发生，因此合并后仍保持 `0/12 proven、12/12 partial`，未来真实 receipt 另做最小 closeout。
- **PR 载体**：draft PR #194 已创建；最终评审候选只认 push 后的 live remote PR HEAD，不把 draft 创建时的 predecessor SHA 当成 review target。
- **下一步**：最终 continuity 后冻结候选，复跑 exact-tree 全量验证，提交推送并将 PR #194 标记 ready；请求 Codex review，最多两轮，clean/green 后合并。

## Batch 2026-08-31-007 | T42 Codex review round 1 focused P2

- **评审 finding**：PR #194 exact head `f6f055ca57a3df6467618b13dc4080ad11705808` 的首轮 Codex review 指出，fork 中的自然 `release.published` 会从固定官方上游下载，但随后按 fork 的 `GITHUB_REPOSITORY` 验证，导致仓库身份自相矛盾。
- **RED→GREEN**：先把合同收紧为“自然 release 使用当前 `GITHUB_REPOSITORY`，手工 replay 才使用官方上游”；同一 focused suite 从 `1 failed, 13 passed` 转为 `14 passed`。
- **聚焦修复**：只在现有 Windows R02 workflow 中按事件选择下载仓库；未改 producer、runtime、installer、USER_GUIDE、版本状态、receipt 字段或路线真值。
- **复验**：focused `14 passed`；Ruff、两份 workflow YAML parse、内嵌 PowerShell AST、`git diff --check`、constraints、plan-check（`Drift=NO`）与 program validate 全部通过。既有 exact-tree 全量 `3412 passed, 3 skipped` 不因本次单一字符串/分支绑定修复重复消耗约 15 分钟。
- **剩余边界**：保持 `0/12 proven、12/12 partial` 与 16 个历史 Program Truth blocker；推送同一 PR 后仅再请求一次 exact-live-head Codex review，仍受最多两轮约束。

## Batch 2026-08-31-008 | T42 Codex review round 2 final focused P2

- **评审 finding**：exact head `41b31796bebaa77db183cc2dab2b3a1a4eb35af6` 的第二轮 Codex review 指出，手工重放虽已从官方上游下载，但 receipt 仍把当前 workflow 仓库和触发 SHA 写成 asset 来源，产生错误 provenance。
- **RED→GREEN**：合同先要求 `source_binding` 分别记录 asset 与 workflow 身份，并要求手工 replay 解析远端 tag commit；focused suite 从 `1 failed, 13 passed` 转为 `14 passed`。
- **聚焦修复**：保留 12 个顶层 receipt 字段，只将 `source_binding` 拆为 `asset(repository/tag/commit)` 与 `workflow(repository/commit/event/run_id)`；手工 replay 用 `git ls-remote` 解析官方 tag 的 peeled commit，自然 release 复用已校验 tag commit，PR 本地制品沿用 PR workflow commit。
- **复验**：focused `14 passed`；证据 tag `spike-native-release-attestation-0c6c9d6d` 远端解析为 exact `0c6c9d6d43f98dcfd169f418e6f6dc616c996c4b`；Ruff、YAML、内嵌 PowerShell AST、`git diff --check`、constraints、plan-check（`Drift=NO`）与 program validate 全部通过。
- **轮次边界**：这是批准范围内第二次也是最后一次 review remediation；推送后只请求 final exact-live-head review。若仍有 finding，不再循环实现，停止并向用户报告；若 clean 且 required checks 全绿则合并。

## Batch 2026-08-31-009 | T42 terminal sponsor decision

- **终局 finding**：final review 指出同 tag 的 `release.published` 与 `workflow_dispatch` 共用 concurrency group；手工 replay 会因 `cancel-in-progress=true` 取消唯一自然发布 `proven` 路径。两轮整改额度耗尽后先进入 `needs_user`，监控暂停，未自动继续。
- **Sponsor 决策**：用户只授权一次终局微修复，并冻结唯一产品改动为 concurrency key 加入 event identity；投入限于一个 workflow 表达式、一个合同测试及必要 WI224 records/continuity。此后 review 只给 verdict，不再整改。
- **RED→GREEN**：先增加自然发布与手工 replay 必须隔离的独立合同；focused suite 从 `1 failed, 14 passed` 转为 `15 passed`。GREEN 后将断言合并进既有 natural-release 合同以避免测试膨胀，最终为 `14 passed`。产品改动仅一行，0 新文件、runtime、依赖、状态、workflow 或抽象。
- **复验**：Lean 后 focused `14 passed`；Ruff、YAML parse、`git diff --check`、constraints、plan-check（`Drift=NO`）与 program validate 全部通过；本机无 actionlint，远端 required checks 作为 workflow 最终执行门禁。
- **收敛规则**：两轮后统一进入一次 terminal sponsor decision；决策必须冻结唯一改动、投入边界和终止结果。终局复评 clean/green 才合并；若出现新的核心 P2 以上 finding 则直接 No-Go/再次 `needs_user`，不得开启第四次实现。该通用规则在 WI224 收口后另立 formal governance work item，不混入本实现 PR。

### Batch 2026-08-31-010 | PR #194 post-merge truth closeout source

- **验证画像**：`truth-only`
- **本批边界**：只修改 WI224 spec/plan/tasks/execution log、roadmap、Program Truth snapshot 与 continuity，不触碰产品实现、测试、release/version 或 truth classifier。
- **改动范围：** 已进入主线的实现精确限于 `.github/workflows/release-build.yml`、`.github/workflows/windows-user-guide-e2e.yml`、`tests/integration/test_github_workflows.py`；本批仅为上述实现补齐 mainline truth 载体。
- **合并证据**：PR #194 final reviewed head `8efab7410abe0bab9bda35427205cb4a34b8fdfb` 获 Codex verdict “Didn't find any major issues”，全部 required checks 通过；squash merge 为 exact `origin/main@3155af394c5739518145d736e0766d779c0728f8`。reviewed head tree 与 main tree 均为 `08ea7ad559a98c41a0dc8946489dbf2e8d64dbcd`，因此不以 squash 后不成立的 ancestor 关系冒充 containment。
- **实现终态**：terminal fix commit `3acb73fa` 只将 event identity 加入 concurrency key；合同先 RED `1 failed, 14 passed`，初始 GREEN `15 passed`，Lean 合并断言后最终 focused `14 passed`。产品净改动 1 行、既有测试净增 3 行，未开启第四次整改。
- **归档与清理**：实现载体保存在 remote `archive/224-native-release-attestation-r02-pr194@8efab7410abe0bab9bda35427205cb4a34b8fdfb`；formal 载体保存在 `archive/224-native-release-attestation-r02-docs-pr192@9a61ca7da39c5beca93e8eac2030e324d23483be`。原 dev/formal 分支与 formal worktree 已在 exact archive 验证后删除；证据 tag `spike-native-release-attestation-0c6c9d6d` 保留。
- **统一验证命令**：`uv run pytest tests/integration/test_github_workflows.py -q`、`uv run pytest tests/integration/test_repo_program_manifest.py -q`、`uv run ai-sdlc verify constraints`、`uv run ai-sdlc program validate`、`uv run ai-sdlc workitem plan-check --wi specs/224-native-release-attestation-r02`、`uv run ai-sdlc program truth sync --dry-run`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc program truth audit`、`uv run ai-sdlc workitem truth-check --wi specs/224-native-release-attestation-r02 --rev HEAD --json`、`uv run ai-sdlc workitem close-check --wi specs/224-native-release-attestation-r02 --json`、branch lifecycle、continuity parity/YAML 与 `git diff --check`。
- **代码审查**：final review 只验证冻结的稳定 finding 及回归面并给 verdict；无可操作问题后合并。两轮后的通用收敛机制只登记为后续 G1 formal governance work item，本批不修改 review runtime、schema、ledger 或状态机。
- **任务/计划同步状态**：T42 完成；PR #194 已进入主线。自然 `release.published` receipt 尚未发生，因此仍为 `0/12 proven、12/12 partial、0/12 missing`；16 个历史 Program Truth blocker、inventory `1169/1169`、missing `4`、close `218/222` 保持不变。
- **改动范围**：`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/224-native-release-attestation-r02/codex-handoff.md`、`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`program-manifest.yaml`、`specs/224-native-release-attestation-r02/spec.md`、`specs/224-native-release-attestation-r02/plan.md`、`specs/224-native-release-attestation-r02/tasks.md`、`specs/224-native-release-attestation-r02/task-execution-log.md`。
- **已完成 git 提交**：是（本 Batch 010 由当前 closeout records `HEAD` 承载，以 live PR exact head 复核）。
- **提交哈希**：`HEAD`（非自引用稳定标记；实际 SHA 以 live PR exact head 为准）。
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`retained(closeout PR review)`
- **生效边界**：本记录只有在唯一 records/truth/continuity closeout PR 合并后才成为 exact-main 终态；随后在隔离远端 clone 中物化唯一主 archive 并验证 `mainline_merged`、`execution_started=true`、`contained_in_main=true` 与 close-check 零 blocker。
