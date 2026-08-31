# 任务执行日志：原生发布制品证明与 R02 强验证

**功能编号**：`224-native-release-attestation-r02`
**创建日期**：2026-08-31
**状态**：formal/closeout 已合并；dev producer 远端 GREEN；consumer 本地 GREEN

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
- **范围/Lean**：仍只修改两个既有 workflow 和一个既有测试文件；receipt 进入现有临时 evidence artifact，0 新 runtime、依赖、状态、sidecar、workflow 或通用抽象。
- **下一步**：完成 PowerShell/YAML/本地门禁后提交 consumer checkpoint，并从 exact branch head 调度一次 manual `v0.9.8` partial path；通过后进入 T42 全量验证与 PR。
