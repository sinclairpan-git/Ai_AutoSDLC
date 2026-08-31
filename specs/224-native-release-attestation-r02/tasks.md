---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
related_doc:
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
---
# 任务分解：原生发布制品证明与 R02 强验证

**编号**：`224-native-release-attestation-r02` | **日期**：2026-08-31

## Batch 1：formal 与证据冻结

### T11：归档错误路线并冻结原生 spike 证据（P0）

- [x] PR #191 以 No-Go 关闭、未合并，head 保存到 remote archive ref。
- [x] 原生 spike run `33366044473` producer/verifier 成功；本地用 exact repo/workflow/ref/digest 再验证成功。
- [x] 明确只允许两个 workflow、一个测试文件，不复活 sidecar 或跨 run API 查询。

### T12：同步 formal 真值并完成评审（P0）

- [x] 更新 roadmap、manifest dependency、项目序号和固定库存期望。
- [x] 运行 constraints、plan-check、program validate/truth、manifest/workflow tests、Ruff、diff-check。
- [x] 更新 execution log/continuity，提交 formal PR；两轮后经用户批准一次最终例外，final review 无 finding。
- [x] formal PR required checks 全绿后合并，exact `origin/main@547e78fd4f03083f2e8c6bb6d258523c8776b0d7` 已验证。
- [x] post-merge truth closeout 合并后，再从新的 exact main 创建 dev 分支。

## Batch 2：Release Build producer

### T20：写 tag guard 与原生 attestation RED（P0）

- [x] 在 `test_github_workflows.py` 先要求：tag ref/commit guard；`id-token/attestations/artifact-metadata` 权限；`actions/attest@v4` 在 smoke 后、release upload 前；禁止 `.provenance.json`。
- [x] 运行 focused test，确认因现有 workflow 缺少这些行为而失败。

### T21：实现最小 producer 并转 GREEN（P0）

- [x] Release Build checkout 精确 tag，验证 `GITHUB_REF == refs/tags/$RELEASE_TAG` 且 tag/checkout/GITHUB_SHA 相同。
- [x] 每个平台 archive 在 smoke 后签发，并执行 `gh attestation verify --repo ... --signer-workflow ... --source-ref ... --source-digest ... --deny-self-hosted-runners`。
- [x] 签发/复验失败时不得执行 `gh release upload`；focused test 转 GREEN。

## Batch 3：Windows R02 consumer

### T30：写 natural-release receipt RED（P0）

- [ ] 测试先要求 `release.published`、动态 tag/asset、同 tag 指南命令匹配、安装前强验证、signed `buildTrigger=workflow_dispatch`、主动 recover 和 WI222 12 字段 receipt。
- [ ] 测试要求 PR/manual receipt 恒为 `partial`，只有 natural release + 全部检查成功才能为 `proven`。
- [ ] 运行 focused test，确认因现有 Windows workflow 缺少这些行为而失败。

### T31：实现 consumer 并转 GREEN（P0）

- [ ] 保留现有 PR/manual 路径；新增自然 release tag 来源并移除仅阻止未来 tag 的硬编码分支，同时验证 checkout 中指南包含该 tag/asset。
- [ ] release 路径下载后、解压前验证 attestation 的 repo/signer/ref/digest/trigger/runner。
- [ ] 复用现有 init/adopt/Result-Next/业务 hash；主动损坏 continuity 后执行已发布 CLI `recover` 并复核业务文件。
- [ ] 将 12 字段 `route-receipt.json` 写入现有 evidence artifact；不新增 workflow 或持久化状态。

## Batch 4：真实验证与交付

### T41：远端 producer 证明（P0）

- [ ] 从 dev exact head 创建临时 tag，以 `--ref <tag>` 调度 Release Build 且 `upload_to_release=false`。
- [ ] 三平台 build/smoke/attest/verify 全绿；不得创建或修改 Release。
- [ ] 查询 attestation 证据，确认 exact tag ref/commit/signer workflow。

### T42：Lean 复核、PR 与收口（P0）

- [ ] 运行 plan 中全部本地验证；确认 0 新 runtime/状态/sidecar/workflow，改动未超 2.5 人日边界。
- [ ] dev PR 请求 Codex review，最多两轮；clean/green 后合并。
- [ ] 合并后保持 `0/12 proven、12/12 partial`；未来自然 release receipt 另开最小 truth closeout。
