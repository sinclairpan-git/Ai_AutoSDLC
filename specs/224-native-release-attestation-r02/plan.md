---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
related_doc:
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
---
# 实施计划：原生发布制品证明与 R02 强验证

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` task-by-task；当前计划不授权自动扩展范围或创建额外 subagent。

**Goal:** 用 GitHub 原生签名把 release archive 绑定精确 tag source，并让现有 Windows R02 在自然 release 中强验证后形成临时 receipt。

**Architecture:** producer 在 Release Build 内 smoke、签发、复验后才上传；consumer 在同一个 R02 job 内验证正式 ZIP 后再运行既有生命周期与恢复。两端只通过 GitHub attestation 服务和 archive digest 连接，不新增 sidecar 或状态系统。

**Tech Stack:** GitHub Actions、PowerShell 7、Bash、`actions/attest@v4`、GitHub CLI、pytest/PyYAML。

**Spec:** `specs/224-native-release-attestation-r02/spec.md`

**状态：** PR #194 已以 reviewed tree 精确匹配的 squash merge 进入 `origin/main@3155af394c5739518145d736e0766d779c0728f8`；本计划只剩 records/truth/continuity 收口，路线真值保持 `0/12 proven、12/12 partial`。

**编号**：`224-native-release-attestation-r02` | **日期**：2026-08-31 | **规格**：`specs/224-native-release-attestation-r02/spec.md`

## 1. 架构

```text
tag ref + tag commit
  → Release Build smoke
  → actions/attest@v4
  → gh attestation verify
  → release asset upload
  → natural release.published
  → Windows R02 verify-before-install
  → init/adopt/recover + route receipt
```

生产者建立密码学证明，消费者只验证签名证书和同 job 生命周期结果；不再反向查询 workflow run，也不创建自定义 provenance 文件。

## 2. 全局约束

- formal 与 dev 分支分离；formal clean/green 合并后才创建 dev 分支。
- 产品改动仅限 2 个 workflow 与 1 个既有测试文件。
- `workflow_dispatch` 必须由维护者执行 `gh workflow run release-build.yml --ref <tag> -f tag=<tag> ...`；workflow 内部再次 fail closed。
- PR/manual receipt 为 `partial`；自然 release receipt 才可能为 `proven`。
- 不发布版本、不修改 release、不扩其他路线、不新增 framework/runtime。

## 3. 文件职责

| 文件 | 唯一职责 |
|---|---|
| `.github/workflows/release-build.yml` | tag guard、三平台 smoke、原生签发/复验、随后上传 |
| `.github/workflows/windows-user-guide-e2e.yml` | 现有 R02 生命周期加 natural release 入口、签名验证、恢复和 receipt |
| `tests/integration/test_github_workflows.py` | 解析 workflow 结构并保护事件、权限、顺序和 fail-closed 合同 |

## 4. 执行阶段

### Phase A：formal 收口

- 冻结 PR #191 No-Go、spike exact tag/run/certificate 证据和本范围。
- 同步 roadmap、manifest、Program Truth 固定库存和 continuity。
- formal PR 只接受直接影响真值/可执行性的 P0/P1 或 P2；最多两轮。

### Phase B：Release Build producer（TDD）

- RED：测试要求 tag guard、OIDC/attestation 权限、`actions/attest@v4` 位于 smoke 之后且 upload 之前、无 sidecar。
- GREEN：精确 tag checkout/commit guard；每个 matrix archive 原生签发并用同一 repo/signer/ref/digest 复验。
- 临时 tag 调度必须使用 `upload_to_release=false`，不得创建或修改 Release。

### Phase C：R02 consumer（TDD）

- RED：测试要求 `release.published`、release-only `gh attestation verify`、`workflow_dispatch` build trigger、12 字段 receipt、PR/manual `partial`。
- GREEN：现有 Windows job 动态使用 event tag/版本；自然 release 在解压前验证，随后执行现有生命周期、主动 recover 和业务文件复核。
- 不抽共享脚本，不修改 Release Artifact Smoke；避免为两个调用点建立新抽象。

### Phase D：验证与交付

- focused pytest、Ruff、PowerShell/YAML parse、constraints、全量 pytest、diff-check。
- 推送 dev PR，请求 Codex review；最多两轮聚焦整改。
- clean/green 后合并，但保持 R02 `partial`，等待下一次自然 release 产生真实 receipt。

## 5. 验证命令

```powershell
uv run pytest tests/integration/test_github_workflows.py -q
uv run ruff check tests/integration/test_github_workflows.py
uv run ai-sdlc verify constraints
uv run ai-sdlc workitem plan-check --wi specs/224-native-release-attestation-r02
uv run ai-sdlc program validate
uv run pytest -q
git diff --check
```

远端生产者验证：

```powershell
$Tag = "spike-native-release-attestation-<short-sha>"
gh workflow run release-build.yml --ref $Tag -f tag=$Tag -f upload_to_release=false
```

## 6. 回退

- formal 与 dev 各自单一语义 PR，可独立 revert。
- 原生 attestation 不写仓库状态；回退 workflow 即移除新增行为。
- 任何自然 release 前失败都保持真实 `partial`；禁止降低 `proven` 标准绕过失败。
