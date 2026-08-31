# 功能规格：原生发布制品证明与 R02 强验证

**功能编号**：`224-native-release-attestation-r02`
**创建日期**：2026-08-31
**状态**：P3-B formal；实现已获用户授权，但须在本 formal 合并后进入独立 dev 分支
**远端主线基线**：`origin/main@49d43c459cdabe5d3664dafd4600192c01333500`
**关联基线**：`specs/222-first-user-twelve-route-e2e-contract/spec.md`

## 1. 目标与边界

本工作项用 GitHub 原生 Artifact Attestation 替代 WI223 的自定义 provenance sidecar，只补齐 R02（Windows AMD64 / 已有项目 / 在线正式发布包）所需的发布来源证明。Release Build 在精确 tag ref 上构建、smoke、签发并上传资产；现有 Windows User Guide E2E 在下一次自然 `release.published` 事件中下载资产、强验证签名，再执行既有 `init/adopt`、业务文件保护和主动恢复，最后上传一个临时 R02 receipt。

### 1.1 允许范围

- formal：本目录、路线图、manifest、项目序号、Program Truth 固定库存期望与 continuity。
- dev：`.github/workflows/release-build.yml`、`.github/workflows/windows-user-guide-e2e.yml`、`tests/integration/test_github_workflows.py`。
- 使用 `actions/attest@v4` 和 `gh attestation verify`；不新增产品依赖。
- PR 与手工重放只生成 `partial`；只有未来自然 release event 的完整同 job 证据才允许 `proven`。

### 1.2 禁止范围

- 不修改 runtime、installer、`USER_GUIDE.zh-CN.md` 正文、版本号、release 状态、D2/P4、R01/R03–R12。
- 不新增 sidecar、通用 provenance 框架、共享执行器、第三个 workflow、数据库、ledger、状态机或长期 receipt 存储。
- 不回填 v0.9.8 为 `proven`，不为完成本工作项创建新版本或 Release。
- 不修改历史 work-item execution log，不删除现有 16 个 Program Truth blocker，不新增 `development-summary.md` 美化 close。

## 2. 已验证的架构前提

- PR #191 已以 No-Go 关闭且未合并；exact head `6d0f6c83214eb44b2ed22f2b182763880bcdd023` 保存在 `archive/223-r02-release-route-proof-pr191-no-go`。
- 原生 spike commit/tag 为 `efb1347b19a56981ab4f8c9d198e37faaf1c98e6` / `spike-native-attestation-20260831-efb1347b`。
- GitHub Actions run [`33366044473`](https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/33366044473) 的 Windows producer 与独立 verifier 均成功。
- 下载 ZIP 的 SHA256 为 `d427bbf10d318310d5c9f2014441f2ee865e481b9b8789b38a772b56b9f5c85a`；本地 `gh attestation verify` 复验确认 signer workflow、tag ref、source/build digest、`push` trigger 和 `github-hosted` runner 均来自签名证书。

因此，本工作项不得再讨论或修补自定义 sidecar；若原生路径不能在正式 Release Build 中保持同等绑定，则直接 No-Go。

## 3. 用户场景与验收

### US-224-1：发布资产绑定精确 tag source（P0）

作为发布维护者，我希望 Release Build 只在 `refs/tags/<tag>` 与输入 tag 一致时上传已签发资产，以便 release 文件不能来自默认分支或另一个 checkout。

1. **Given** Release Build 没有以 `--ref <tag>` 调度，**When** workflow 比较 `github.ref`、输入 tag、tag commit 与 `github.sha`，**Then** 在构建/上传前失败。
2. **Given** 三个平台 smoke 成功，**When** 上传 release asset，**Then** 每个 archive 已由原生 attestation 签发并按 repo、signer workflow、tag ref、tag commit 复验通过。

### US-224-2：R02 在自然发布事件中形成强证据（P0）

作为首次 Windows 用户和评审者，我希望同一个 release job 在安装前验证正式 ZIP 的签名来源，并完成已有项目接入与恢复，以便 R02 不再依赖跨 workflow 的人工拼接。

1. **Given** PR 或 `workflow_dispatch` 重放，**When** 生命周期步骤成功，**Then** receipt 仍为 `partial`。
2. **Given** 下一次自然 `release.published`，**When** ZIP attestation、安装、`Result / Next`、`adopt`、业务文件 hash 和 `recover` 全部成功，**Then** receipt 才能为 `proven`。
3. **Given** 任一签名字段、tag commit、恢复或业务文件检查失败，**When** 生成 receipt，**Then** job fail closed，不能产出 `proven`。

## 4. 功能需求

- **FR-224-001**：Release Build 必须拒绝 `github.ref != refs/tags/${inputs.tag}` 或 `github.sha != <tag>^{commit}`，checkout 也必须落在同一 commit。
- **FR-224-002**：每个平台 archive 必须在 smoke 后、`gh release upload` 前由 `actions/attest@v4` 签发，并用 `gh attestation verify` 复核 repo、signer workflow、source ref/digest 和 hosted runner。
- **FR-224-003**：Windows User Guide E2E 只新增 `release.published` 入口和动态 release tag/asset 解析；自然 release 必须确认同一 tag checkout 的指南包含该 tag/asset 命令形状，现有 PR 与手工入口继续可用。
- **FR-224-004**：自然 release 路径必须在解压安装前验证 archive attestation，要求 build trigger 为 `workflow_dispatch`，source ref 为 release tag，source digest 为该 tag commit。
- **FR-224-005**：R02 receipt 复用 WI222 的 12 个字段，作为现有 Actions evidence artifact 的临时文件；不写入产品状态或 Program Truth。
- **FR-224-006**：自然 release 路径必须真实损坏并通过已发布 CLI `recover` 恢复 continuity 文件，且恢复前后业务文件 hash 不变。
- **FR-224-007**：合并实现本身不改变 `0/12 proven、12/12 partial`；只有未来真实 release receipt 才能另行更新路线真值。

## 5. ROI 与停止条件

- **价值**：9.5/10；直接补首次用户正式资产来源与 R02 自包含证据。
- **投入**：目标 1–2 人日，硬上限 2.5 人日；正式产品改动限定 2 个 workflow 和 1 个既有测试文件。
- **维护面**：0 个新产品依赖、0 个新持久化状态、0 个 sidecar、0 个新 workflow、0 个通用抽象。
- **停止**：需要新服务/ledger、复制第二套 R02 生命周期、修改 runtime/installer/版本、扩展其他路线、两轮评审仍有核心问题，或投入超过硬上限时立即 No-Go。
- **决策**：`implement`；依据是 exact remote spike 的真实签发与独立验证，而不是文档推测。

## 6. 成功标准

- **SC-224-001**：workflow 契约测试完成 RED→GREEN，并证明 tag guard、attest-before-upload、release-only 强验证和 receipt 状态边界。
- **SC-224-002**：临时 tag 上的 Release Build（`upload_to_release=false`）三平台成功签发/复验，不创建 Release。
- **SC-224-003**：实现 PR 的 Windows PR job 保持通过并输出 `partial` receipt；自然 release 前不得宣称 R02 `proven`。
- **SC-224-004**：focused tests、全量 tests、Ruff、constraints 与 diff-check 通过；Codex review 最多两轮后 clean，否则 No-Go。
