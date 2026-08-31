---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
related_doc:
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
---
# 任务分解：R02 正式发布路线证明载体

**编号**：`223-r02-release-route-proof` | **日期**：2026-08-30
**来源**：`spec.md` + `plan.md`

## 分批策略

```text
Batch 1: formal scope and characterization gate
Batch 2: RED route proof contracts
Batch 3: shared Windows R02 executor
Batch 4: two thin workflow integrations
Batch 5: verification, Lean review, PR and continuity
Batch 6: next natural release evidence (deferred; no release authorization)
```

## Batch 1：formal scope and characterization gate

### T11：冻结 R02 范围、证据与 Go/No-Go

- **优先级**：P0
- **依赖**：WI222 已合入 exact main；用户已批准执行
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`program-manifest.yaml`
- **验收**：
  - [x] 固定 exact main、v0.9.8 Windows digest、release run 与 `3407/3` 基线。
  - [x] 只批准 R02；记录真实 `release` event 与 build provenance 同时成立才能 `proven`。
  - [x] 固定 3 人日、两轮 review、无 runtime/installer/version/D2/P4 的退出条件。
  - [x] `plan-check`、Program Truth 同步、constraints、库存测试和 diff-check 通过。
- **提交**：`docs: formalize WI223 R02 release route proof`

## Batch 2：build provenance and route proof RED

### T20：先写 release-build provenance 合同并实现 archive-qualified sidecar

- **优先级**：P0 / approved after formal merge
- **依赖**：T11 formal PR clean/green 合并；用户已批准聚焦修改 `release-build.yml`
- **文件**：修改 `tests/integration/test_github_workflows.py`、`.github/workflows/release-build.yml`
- **步骤**：
  - [ ] 先写 RED，要求 release build checkout 精确使用 `ref: ${{ inputs.tag }}`，并要求 workflow 为每个 archive 生成唯一的 `<archive-name>.provenance.json`；三平台矩阵不得上传同名 sidecar。
  - [ ] sidecar 只包含 `schema_version`、`release_tag`、`source_commit`、`archive_name`、`archive_digest`、`workflow_run_id`；不新增通用 attestation 框架或持久化 ledger。
  - [ ] 在上传前通过 GitHub commit/ref API 把 tag 解析为精确 40 位 commit，验证 `$GITHUB_SHA`/checkout commit 等于该 commit，并用实际 archive SHA256 写 `archive_digest`；`workflow_run_id` 必须取当前 `$GITHUB_RUN_ID`，任一字段缺失或不一致时禁止 `gh release upload`。
  - [ ] 将 archive-qualified sidecar 与对应 archive 一起上传到同一 release；禁止依赖 `--clobber` 覆盖其他平台的 provenance；focused test 由 RED 转 GREEN。
- **提交**：与 T21/T31 的同一 provenance + receipt 逻辑批次提交。

### T21：先写共享执行器与 receipt 合同测试

- **优先级**：P0
- **依赖**：T20 provenance sidecar 合同已 GREEN
- **文件**：新建 `tests/integration/test_windows_r02_route_proof.py`
- **接口**：测试读取 `scripts/ci/Invoke-WindowsR02RouteProof.ps1`，要求脚本公开 plan 中的五个参数，并固定 R02 与 12 字段。
- **步骤**：
  - [ ] 新增下列测试骨架，并明确由“脚本尚不存在”触发 RED：

    ```python
    def test_windows_r02_executor_freezes_receipt_contract() -> None:
        script = _SCRIPT.read_text(encoding="utf-8")
        for field in _REQUIRED_RECEIPT_FIELDS:
            assert f'"{field}"' in script
        assert '$env:GITHUB_EVENT_NAME -eq "release"' in script
        assert '$buildProvenanceVerified' in script
        assert 'status = if ($isFormalReleaseProof -and $buildProvenanceVerified) { "proven" } else { "partial" }' in script
    ```

  - [ ] 增加 tag 必须解析为 40 位 commit、sidecar 的 `source_commit == tag commit`、`archive_digest == local digest`、run ID/workflow/event/status/conclusion/headSha 全部匹配、digest/provenance fail-closed、`resume-pack.yaml` 故障注入、`recover` 执行和业务 hash 再比较断言。
  - [ ] 运行 `uv run pytest tests/integration/test_windows_r02_route_proof.py -q`，记录预期 FAIL 为缺少脚本，而不是语法/收集错误。
- **提交**：与 T31 的 GREEN 实现合并为同一逻辑批次提交，不单独提交永久 RED。

## Batch 3：shared Windows R02 executor

### T31：抽取唯一 R02 Windows 执行器

- **优先级**：P0
- **依赖**：T21 RED 已记录；build provenance 范围已获新授权
- **文件**：新建 `scripts/ci/Invoke-WindowsR02RouteProof.ps1`
- **输入**：`ArchivePath`、`BuildProvenancePath`、`ReleaseTag`、`PackageSourceMode`、`EvidenceRoot`、`ProjectRoot`
- **输出**：安装/init/adopt/recover 日志、业务文件前后 hash、release/build metadata、`route-receipt.json`
- **步骤**：
  - [ ] 从现有 Windows guide replay 抽取已有项目构造、安装、direct shim、stale PATH、init/adopt 与业务文件保护；不增加新的产品行为。
  - [ ] `published_release` 模式运行：

    ```powershell
    $release = gh release view $ReleaseTag --repo $env:GITHUB_REPOSITORY --json tagName,assets | ConvertFrom-Json
    $asset = $release.assets | Where-Object { $_.name -eq (Split-Path $ArchivePath -Leaf) }
    $localDigest = "sha256:$((Get-FileHash -Algorithm SHA256 -LiteralPath $ArchivePath).Hash.ToLowerInvariant())"
    if (-not $asset.digest -or $asset.digest -ne $localDigest) { throw "release asset digest mismatch" }
    $provenance = Get-Content -LiteralPath $BuildProvenancePath -Raw | ConvertFrom-Json
    $tagCommit = gh api "repos/$($env:GITHUB_REPOSITORY)/commits/$ReleaseTag" --jq .sha
    if ($LASTEXITCODE -ne 0 -or $tagCommit -notmatch '^[0-9a-f]{40}$') { throw "release tag commit resolution failed" }
    $buildRunId = [string]$provenance.workflow_run_id
    if ($buildRunId -notmatch '^\d+$') { throw "release build run id is missing or invalid" }
    $buildRunJson = gh run view $buildRunId --repo $env:GITHUB_REPOSITORY `
      --json databaseId,workflowName,event,headSha,status,conclusion,url
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($buildRunJson)) { throw "release build run lookup failed" }
    $buildRun = $buildRunJson | ConvertFrom-Json
    $buildProvenanceVerified = (
      $provenance.release_tag -eq $ReleaseTag -and
      $provenance.source_commit -eq $tagCommit -and
      $provenance.archive_name -eq $asset.name -and
      $provenance.archive_digest -eq $localDigest -and
      [string]$buildRun.databaseId -eq $buildRunId -and
      $buildRun.workflowName -eq "Release Build" -and
      $buildRun.event -eq "workflow_dispatch" -and
      $buildRun.headSha -eq $tagCommit -and
      $buildRun.status -eq "completed" -and
      $buildRun.conclusion -eq "success"
    )
    ```

  - [ ] 在 init/adopt 后写坏 `.ai-sdlc/state/resume-pack.yaml`，执行 direct shim `recover`，验证恢复成功且 YAML 不再是注入内容。
  - [ ] 再次比较四个业务文件 hash；任何变化 fail closed。
  - [ ] 用 `ConvertTo-Json -Depth 8` 写 receipt；仅 `$env:GITHUB_EVENT_NAME -eq "release"`、published digest、tag commit、Release Build run、build provenance 与全部核心检查同时成功时输出 `proven`。
  - [ ] 运行 focused test 由 RED 转 GREEN，并运行 PowerShell parser 无错误。
- **提交**：`feat: add shared Windows R02 route proof executor`

## Batch 4：two thin workflow integrations

### T41：先写 workflow 复用 RED

- **优先级**：P0
- **依赖**：T31；build provenance 范围已获新授权
- **文件**：修改 `tests/integration/test_github_workflows.py`
- **步骤**：
  - [ ] 要求两个 workflow 都包含 `scripts/ci/Invoke-WindowsR02RouteProof.ps1`。
  - [ ] 要求 Windows guide PR path 监听 `scripts/ci/**`，release smoke 保留 `release: published`。
  - [ ] 要求两个 workflow 上传 `route-receipt.json`，并禁止在两个 YAML 中继续出现完整的 `& $directShim adopt .` 与 resume-pack 注入实现。
  - [ ] 运行 focused test，记录当前 workflow 未调用共享脚本的预期 RED。

### T42：改为两个薄调用

- **优先级**：P0
- **依赖**：T41 RED
- **文件**：修改 `.github/workflows/windows-user-guide-e2e.yml`、`.github/workflows/release-artifact-smoke.yml`
- **步骤**：
  - [ ] Windows guide 只负责构建或下载 archive、构造输入并调用共享执行器；保留现有 artifact 名和 PR 真实 Windows job。
  - [ ] Release smoke Windows job 下载正式 asset 后调用同一执行器；保留 `verify_offline_bundle.py` 与 POSIX jobs。
  - [ ] 两个入口设置只读 `GH_TOKEN`，传入同一参数接口；不新增矩阵或第三个 workflow。
  - [ ] focused workflow tests 与全仓 YAML parse 由 RED 转 GREEN。
- **提交**：`ci: reuse R02 proof in Windows release routes`

## Batch 5：verification, Lean review, PR and continuity

### T51：完成验证与半天 Lean/ROI 复核

- **优先级**：P0
- **依赖**：T42
- **步骤**：
  - [ ] 运行 focused pytest、Ruff、PowerShell parser、constraints、全量 pytest 和 `git diff --check`。
  - [ ] 计算两个 workflow 变更前后内联核心行数、共享执行器调用数和新增持久化状态数；必须是 2 个调用点、0 个新持久化状态。
  - [ ] PR Windows job 必须真实通过；下载 receipt 并确认 PR event 为 `partial`。
  - [ ] 更新本 execution log、tasks、双 handoff 与路线图实际状态。
  - [ ] 推送 dev PR，请求 Codex review；最多两轮聚焦整改。
  - [ ] checks 与 review clean 后合并；不把 R02 改为 proven。
- **提交**：实现批次最后一次记录提交，与对应代码/测试同批对齐。

## Batch 6：next natural release evidence

### T61：等待自然 release event 产生正式 receipt

- **优先级**：P1 / deferred
- **依赖**：实现 PR 合并；未来另有 release 授权
- **禁止动作**：不得为完成 T61 创建新版本、绕过 D2 或把手工 dispatch 改称 release event。
- **验收**：未来真实 release job 的 R02 receipt 为 `proven`，资产 digest 与 release API 一致；届时另开最小 records/truth closeout。
