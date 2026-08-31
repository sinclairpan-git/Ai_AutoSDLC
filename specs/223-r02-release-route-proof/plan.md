---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
related_doc:
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
---
# 实施计划：R02 正式发布路线证明载体

**编号**：`223-r02-release-route-proof` | **日期**：2026-08-30 | **规格**：`specs/223-r02-release-route-proof/spec.md`

## 1. 目标与架构

**目标**：先冻结 R02 证明所需的 build provenance 缺口；在用户另行批准前，不进入共享执行器实现。

**候选架构（未授权）**：若用户批准扩展，release build 必须先输出可验证 provenance，把 archive digest、tag commit、build source commit 和 run 绑定；R02 PowerShell 执行器再负责安装、生命周期、故障恢复与 receipt。只做消费 workflow 而不补 build provenance 时，receipt 永远保持 `partial`。

**技术栈**：PowerShell 7 / Windows PowerShell installer、GitHub Actions、GitHub CLI、Python 3.11+ / pytest / PyYAML。无新增产品依赖，无数据库或持久化服务。

## 2. 全局约束

- formal 文档在 `feature/223-r02-release-route-proof-docs` 完成；用户未批准 build provenance 扩展前，不创建 dev 分支。
- 不修改 `src/ai_sdlc/`、installer、用户指南正文、版本/release、D2/P4、历史 execution log、truth classifier 或既有 16 blocker。
- 只实现 R02；不参数化为 R01–R12 通用运行平台。
- 只有真实 `release` event、asset digest 与 build source/tag commit 精确绑定且全部检查通过时 receipt 才可为 `proven`；本 PR 不发布新版本。
- 每个实现批次遵循 RED → GREEN → refactor；不得先写执行器再补测试。
- 当前改动前基线为 `3407 passed, 3 skipped in 957.27s`。

## 3. 文件职责

```text
scripts/ci/Invoke-WindowsR02RouteProof.ps1
  候选唯一 R02 Windows 执行器；当前未授权创建

.github/workflows/release-build.yml
  若用户另行批准，固定 tag checkout 并产生 asset provenance；当前不得修改

.github/workflows/windows-user-guide-e2e.yml
  PR 本地 bundle 与手工正式包重放入口；调用共享执行器并上传 evidence

.github/workflows/release-artifact-smoke.yml
  正式 release event 入口；调用同一执行器并保留三平台 smoke

tests/integration/test_github_workflows.py
  锁定两个 workflow 的薄调用与禁止重复合同

tests/integration/test_windows_r02_route_proof.py
  锁定执行器参数、12 字段、digest fail-closed、事件分级和恢复命令合同

specs/223-r02-release-route-proof/*
docs/FRAMEWORK_ROADMAP.zh-CN.md
program-manifest.yaml
.ai-sdlc/state/codex-handoff.md
.ai-sdlc/work-items/223-r02-release-route-proof/codex-handoff.md
  formal、路线图、Program Truth 映射与连续性记录
```

不新建 JSON schema 文件、Python receipt framework 或持久化 ledger；receipt 结构由 WI222 spec 和 focused tests 共同约束。

## 4. 执行器接口

实现分支上的 PowerShell 入口固定为：

```powershell
pwsh -NoProfile -File scripts/ci/Invoke-WindowsR02RouteProof.ps1 `
  -ArchivePath <absolute-zip> `
  -BuildProvenancePath <absolute-json> `
  -ReleaseTag <vX.Y.Z> `
  -PackageSourceMode <pull_request_local_bundle|published_release> `
  -EvidenceRoot <absolute-dir> `
  -ProjectRoot <absolute-dir>
```

执行器从 GitHub Actions 环境读取 `GITHUB_EVENT_NAME`、`GITHUB_REPOSITORY`、`GITHUB_RUN_ID`、`GITHUB_SHA`、`GITHUB_WORKFLOW_REF` 和 `RUNNER_*`。`published_release` 模式需要 `GH_TOKEN`，通过 `gh release view` 取得 asset digest，并读取 `release-build-provenance.json` 验证 tag、build source commit、archive name/digest 与 run；本地产物模式明确记录无正式 provenance。

候选 provenance sidecar 固定为最小结构：

```json
{
  "schema_version": "1.0",
  "release_tag": "vX.Y.Z",
  "source_commit": "40-char commit",
  "archive_name": "ai-sdlc-offline-X.Y.Z-windows-amd64.zip",
  "archive_digest": "sha256:...",
  "workflow_run_id": "..."
}
```

`route-receipt.json` 顶层结构固定为：

```json
{
  "schema_version": "1.0",
  "status": "partial",
  "route_id": {},
  "environment": {},
  "project_mode": {},
  "acquisition_mode": {},
  "source_binding": {},
  "asset_integrity": {},
  "installation": {},
  "lifecycle": {},
  "result_next": {},
  "success_receipt": {},
  "fault_recovery": {},
  "evidence_links": {}
}
```

## 5. 阶段计划

### Phase 0：特征化与 Go/No-Go（已完成，结论已修正）

- 验证 GitHub Release API 暴露 v0.9.8 Windows digest。
- 验证 release run `33084560424` 为真实 `release` event，但旧 run 缺逐路 receipt，不能追认 proven。
- 验证已有 workflow 与 `recover` 能力足以抽取复用，不需 runtime 变更。
- 初判为 Go；Codex review 证明 release asset 缺 build provenance，修正为 `needs_user`。

### Phase 1：formal review

- 完成 spec/plan/tasks、路线图状态、manifest truth sync 与 continuity。
- 运行 plan-check、program validate、truth dry-run/execute、constraints 和库存测试。
- 单独提交、推送 formal PR，请求 Codex review；无可操作问题且 checks 通过后合并。

### Phase 2：TDD 实现（blocked）

只有用户明确批准以下新增范围后才解锁本阶段：允许聚焦修改 `release-build.yml`，固定构建 ref 并输出可验证 provenance sidecar；否则本阶段取消。

1. 在 dev 分支先增加 release-build RED：checkout 必须绑定 `inputs.tag`，sidecar 必须记录 tag/source/archive digest/run，上传前必须验证 source commit 等于 tag commit。
2. 最小修改 `release-build.yml` 生成并上传 sidecar；不新增通用 attestation 层。
3. 增加 R02 focused RED，要求 sidecar source/tag 和 archive digest 验证、共享执行器、12 字段、恢复与事件分级。
4. 抽出 `Invoke-WindowsR02RouteProof.ps1`，从 Windows guide workflow 删除内联核心块，使 RED 转 GREEN。
5. 将 release artifact smoke Windows job 改为同一执行器的薄调用；保留 `verify_offline_bundle.py` 和 POSIX jobs。
6. 运行 focused tests、YAML parse、PowerShell parser、Ruff、constraints 与全量 pytest。

### Phase 3：真实 PR Windows 验证与 Lean 复核

- PR 触发 `windows-user-guide-e2e`，真实 Windows runner 安装本地候选 bundle、执行生命周期和主动恢复。
- 下载/检查 receipt artifact，确认 PR 状态为 `partial`。
- 比较变更前后 workflow 内联核心行数与调用点；若形成双轨或维护面扩大，回退并 No-Go。
- Codex review 最多两轮；通过后合并实现 PR。

### Phase 4：自然发布证明（不由本工作项强制触发）

- 下一次自然 release event 自动运行共享执行器并校验正式 asset digest。
- 只有取得真实 `proven` receipt 后，另做最小 records/truth closeout；此前 R02 保持 `partial`。
- 不为完成此阶段单独创建 release 或修改版本。

## 6. 关键验证

```powershell
uv run pytest tests/integration/test_windows_r02_route_proof.py tests/integration/test_github_workflows.py -q
uv run ruff check tests/integration/test_windows_r02_route_proof.py tests/integration/test_github_workflows.py
Get-Content .github/workflows/windows-user-guide-e2e.yml -Raw | ConvertFrom-Yaml | Out-Null
Get-Content .github/workflows/release-artifact-smoke.yml -Raw | ConvertFrom-Yaml | Out-Null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path scripts/ci/Invoke-WindowsR02RouteProof.ps1),
  [ref]$null,
  [ref]$errors
) | Out-Null
if ($errors.Count) { throw ($errors | Out-String) }
uv run ai-sdlc verify constraints
uv run pytest -q
git diff --check
```

若 PowerShell 环境没有 `ConvertFrom-Yaml`，以现有 pytest/PyYAML 全仓解析测试为主并在 execution log 说明，不引入模块依赖。

## 7. 回退与停止

- formal 与实现分别独立 commit/PR，可用单次 `git revert` 回退。
- digest API 不稳定、v0.9.8 CLI 无法完成真实 recovery、共享执行器必须修改 runtime、投入将超过 3 人日，或两轮 review 仍不 clean 时立即停止。
- build provenance 需要第三个 workflow；在当前授权下已触发停止，等待用户决定是否扩展。
- 停止时保留真实 RED/CI 证据，标记 `No-Go / needs_user`；不得增加适配层、放宽 proven 或发布新版本来掩盖失败。

## 8. 开放状态

| 问题 | 当前结论 | 阻塞点 |
|---|---|---|
| v0.9.8 是否能被旧 release run 追认 proven | 否；旧 run 没有逐路 receipt | 无；保持 partial |
| 当前 asset digest 是否证明 archive 来自 tag commit | 否；release-build checkout 未绑定 `inputs.tag` | dev execute / needs_user |
| 是否立即发布 v0.9.9 取得 release event | 否；D2 与版本均未授权 | release |
| 是否扩展其他 11 路 | 否；先完成 R02 Lean/ROI | 新用户批准 |
