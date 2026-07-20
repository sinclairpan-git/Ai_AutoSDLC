---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/213-programservice-bounded-stage-reduction/development-summary.md"
---
# 实施计划：Workitem 只读命令 Adapter 副作用隔离

**编号**：`214-workitem-readonly-adapter-side-effect`
**日期**：2026-07-19
**规格**：`specs/214-workitem-readonly-adapter-side-effect/spec.md`

## 1. 概述

先用 formal PR 冻结最窄兼容合同，再从 formal fresh main 创建 dev 分支，implementation fresh-main 后用
独立 lifecycle reconciliation PR 承载关闭事实。实现只让
`_workitem_before_command()` 为当前唯一依赖 callback 的写命令 `link` 消费 hook；测试证明五个只读入口从
hook 1 次变为 0 次，同时 `init/link` 的全部适用控制流零差异。T58 完成后只解除 T66 T61A 的前置阻断，
不计减重收益。

## 2. 技术背景与当前控制流

- Python >=3.11；Typer/Rich CLI；pytest；Ruff；无新增依赖。
- Root callback 对 `workitem` 只注入 adapter hook，子应用 callback 决定何时消费。
- `init` 已在 handler 内完成 root、ID、branch、clean-tree preflight 后显式消费 hook。
- `link` 依赖子应用 callback 在 handler 前消费 hook。
- 五个 read-only handler 不需要 adapter，但现有 callback 把它们与 `link` 一并消费。

## 3. 宪章与父合同响应

| 门禁 | 计划响应 |
|---|---|
| MUST-1 范围严控 | 只关闭 GAP-15；一个既有产品函数；不清理相邻代码 |
| MUST-2 可验证 | 15 个只读入口 + `init/link` 兼容矩阵；先 RED 后 GREEN |
| MUST-3 范围/验证/回退 | formal、implementation、lifecycle 分 PR；按 truth-first 顺序回退；每批记录证据 |
| MUST-4 状态落盘 | canonical docs、execution log、truth、root/scoped handoff 同步 |
| MUST-5 产品/治理隔离 | formal PR 不改 `src/tests`；dev PR 才改产品与测试 |
| NC-01～06 / CC-05 | observed/expected、最大范围、真实副作用、平台、回退均冻结 |
| 用户双对抗评审 | Pascal 审 LEAN/YAGNI；Confucius 审 SAFETY/COMPAT；同 identity 双 PASS0 |
| 发布边界 | T58 不发布；WI196/RC-08 全局终态前持续禁止发布 |

## 4. 最小设计

目标源码差异仅为把 callback 收敛为当前唯一写命令：

```python
if ctx.invoked_subcommand != "link":
    return
```

保留随后的 `_run_workitem_adapter(ctx)`，因此 `link` 仍走原路径，`init` 仍由 handler 显式调用。该设计不
维护命令名单，也不抽取常量、decorator、registry 或通用 classifier；未来命令必须显式选择写副作用。
若 Typer 实测证明此结构不能覆盖 help/invalid，则先回到 formal 复审，不得增加全局机制。

## 5. 测试设计

### 5.1 RED/GREEN 只读矩阵

| 命令 | normal | help | invalid |
|---|---|---|---|
| `plan-check` | syntactically valid `--plan` | `--help` | 缺少 `--wi/--plan` |
| `guard` | 默认/显式 request | `--help` | 未知 option |
| `close-check` | syntactically valid `--wi` | `--help` | 缺少 `--wi` |
| `branch-check` | syntactically valid `--wi` | `--help` | 缺少 `--wi` |
| `truth-check` | syntactically valid `--wi` | `--help` | 缺少 `--wi` |

`tests/integration/test_cli_workitem_adapter_dispatch.py` 是唯一新增测试文件，以参数化承担 15 个真实解析
入口。每格使用会记录 call、输出 marker、写 sentinel 文件的 hook。RED 期望 legacy 至少暴露 hook/write；
GREEN 要求 call=0、marker 不存在、adapter/config/tracked/untracked tree snapshot 不变。使用 no-op hook 在
byte-identical 临时项目重放同参数，逐字节比较 stdout/stderr/exit；不复制 handler 业务 fixture。

仅原始复现 `plan-check normal` 以 `@pytest.mark.real_ide_hook` 运行一组 production/no-op A/B：两份
byte-identical 临时项目预置“若 hook 执行必产生变更”的 Cursor managed fixture；捕获 guarded adapter/
project-config bytes 的 SHA-256、`git status --porcelain=v1 -uall`、stdout/stderr/exit并要求 candidate exact。
其余四个 normal 的同一 callback 分支由 15 格 sentinel 覆盖，不重复昂贵 production fixture。

### 5.2 `init/link` 兼容矩阵

- 共享 `tests/unit/test_cli_hooks.py` 只补一例 production partial-write：真实 `apply_adapter` 后令
  `_persist_config` 触发 project-config `PermissionError`，断言 guarded bytes 与 warning；既有三例继续覆盖
  config-lock return、unexpected exception、non-config PermissionError。
- `init`：只在 `test_cli_workitem_init.py` 复用 valid、missing title、dirty/wrong branch、no-project、duplicate；
  注入“warning 后 return”和“raise”两种 hook outcome，只断言本次分发的 call order、继续 scaffold或不开始。
- `link`：只在 `test_cli_workitem_link.py` 复用 valid/missing/no-checkpoint；补 help/unknown option、call order、
  dirty、no-project及同样两种 hook outcome；只断言 handler 继续或在 handler 前传播，不复制 partial-write fixture。
- 只新增分发/顺序证明，不复制 handler 的业务断言；所有 baseline assertion 必须先在未改产品源码时通过或
  作为预期 RED 明确失败。

### 5.3 冻结验证命令

- `V1`：`uv run --python 3.11 pytest tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py -q`
- `V2`：`uv run --python 3.11 pytest -q`
- `V3`：`uv run --python 3.11 ruff check src tests`
- `V4a`：`uv run --python 3.11 ruff format --check tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py`
- `V4b`：按下方 fixed-base 程序执行 formatter-red 路径集合与 changed-range 门禁；这两个 legacy 文件在
  formal base `d7f8b163` 已 formatter-red，禁止用动态 `origin/main` 或只比较 red 文件数量。
- `V5`：`uv run --python 3.11 ai-sdlc verify constraints`
- `V6`：`git diff --check`

V1 的 RED 只允许新 dispatch assertions 失败；`init/link` legacy characterization 必须保持绿。GREEN、
implementation final identity 和 fresh-main 均重跑 V1～V3、V4a/V4b、V5～V6；跨平台 required checks
重跑 full pytest。不得为使历史全库 formatter 诊断变绿而格式化非范围文件。

#### V4b fixed-base 可执行程序

T21 在 RED 前把 `FORMAT_BASE_SHA` 冻结为本 amendment 的 detached fresh-main exact SHA，写入 implementation
execution log 与 handoff；dev、PR、merge、fresh-main 始终使用该固定 SHA。以下 PowerShell 程序只接受
committed+clean candidate，冻结其 SHA，要求 candidate formatter-red 路径集合是 base 集合的大小写敏感子集，
并对两个 legacy-red 文件的每个 candidate changed range 执行 Ruff range check。路径统一为 `/` 且按大小写
敏感方式排序去重；任一工具异常、新增 red path、range format failure、不可解析输出或 base 不可达均失败。

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:FORMAT_BASE_SHA = "<amendment detached fresh-main exact SHA>"
$legacyFiles = @(
  "src/ai_sdlc/cli/workitem_cmd.py",
  "tests/integration/test_cli_workitem_init.py"
)
$baseDir = Join-Path ([IO.Path]::GetTempPath()) ("wi214-format-" + [guid]::NewGuid())

function Get-FormatterRedPaths([string]$root) {
  Push-Location $root
  try {
    $output = @(& uv run --python 3.11 ruff format --check src tests 2>&1)
    $code = $LASTEXITCODE
    if ($code -notin @(0, 1)) { throw "ruff format failed with exit $code" }
    $paths = @($output |
      ForEach-Object {
        $match = [regex]::Match([string]$_, '^Would reformat:\s+(.+)$')
        if ($match.Success) { $match.Groups[1].Value.Replace('\', '/') }
      } |
      Sort-Object -Unique -CaseSensitive)
    $summary = [regex]::Match(
      ($output -join "`n"), '(?m)^(?<count>\d+) files? would be reformatted(?:,|$)')
    if ($code -eq 1 -and
        (-not $summary.Success -or [int]$summary.Groups['count'].Value -ne $paths.Count)) {
      throw "unparseable ruff formatter-red output"
    }
    if ($code -eq 0 -and $paths.Count -ne 0) {
      throw "inconsistent ruff formatter-clean output"
    }
    $paths
  } finally { Pop-Location }
}

$status = @(& git status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw "cannot inspect candidate worktree" }
if ($status.Count -ne 0) { throw "candidate worktree must be committed and clean" }
$candidateSha = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "cannot freeze candidate SHA" }
& git merge-base --is-ancestor $env:FORMAT_BASE_SHA $candidateSha
if ($LASTEXITCODE -ne 0) { throw "FORMAT_BASE_SHA is not a candidate ancestor" }

git worktree add --detach $baseDir $env:FORMAT_BASE_SHA
if ($LASTEXITCODE -ne 0) { throw "FORMAT_BASE_SHA is not reachable" }
try {
  $baseRed = @(Get-FormatterRedPaths $baseDir)
  $candidateRed = @(Get-FormatterRedPaths (Get-Location).Path)
  $baseSet = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
  foreach ($path in $baseRed) { $null = $baseSet.Add($path) }
  $newRed = @($candidateRed | Where-Object { -not $baseSet.Contains($_) })
  if ($newRed) { throw "new formatter-red paths: $($newRed -join ', ')" }

  foreach ($file in $legacyFiles) {
    $patch = @(& git diff --unified=0 "$env:FORMAT_BASE_SHA...$candidateSha" -- $file)
    if ($LASTEXITCODE -ne 0) { throw "cannot diff $file" }
    $matches = [regex]::Matches(
      ($patch -join "`n"), '(?m)^@@ [^+]*\+(?<start>\d+)(?:,(?<count>\d+))? @@')
    if ($patch.Count -ne 0 -and $matches.Count -eq 0) {
      throw "cannot parse changed ranges for $file"
    }
    foreach ($match in $matches) {
      $start = [int]$match.Groups['start'].Value
      $count = if ($match.Groups['count'].Success) {
        [int]$match.Groups['count'].Value
      } else { 1 }
      if ($count -eq 0) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
          throw "legacy file removed: $file"
        }
        $lineCount = @(Get-Content -LiteralPath $file).Count
        $rangeStart = if ($lineCount -eq 0) {
          1
        } else {
          [Math]::Min([Math]::Max(1, $start), $lineCount)
        }
        $endExclusive = if ($lineCount -eq 0) {
          2
        } else {
          [Math]::Min($lineCount + 1, $rangeStart + 2)
        }
      } else {
        $rangeStart = $start
        $endExclusive = $start + $count
      }
      uv run --python 3.11 ruff format --check --range "$rangeStart-$endExclusive" $file
      if ($LASTEXITCODE -ne 0) {
        throw "formatter debt in $file range $rangeStart-$endExclusive"
      }
    }
  }
} finally {
  git worktree remove --force $baseDir
  if ($LASTEXITCODE -ne 0) { throw "cannot remove formatter base worktree" }
}
```

Implementation reviewed HEAD 必须记录本程序冻结的 candidate SHA、base/candidate red path 集合摘要与每个
emitted range；merge 后先证明 merge tree 等于 reviewed tree，再在 detached fresh-main 对相同
`FORMAT_BASE_SHA` 重跑，不复用动态 diff。

## 6. 分阶段执行

### Phase 0：formal current-main 冻结

1. 从 `origin/main@d5ad7616` 建独立 docs worktree/branch，初始化 WI214。
2. 恢复 `workitem init` 带来的非范围 Cursor refresh，证明 SHA=`d5f04acf...0b6a`、相对 main diff=0。
3. 冻结 spec/plan/tasks、parent T58 active 状态、源码边界与兼容矩阵。
4. 计算 parent+child formal-six identity；Pascal/Confucius 独立审查，成立 finding 最小修正并对新身份从零复审。
5. 同步 formal truth/handoff，跑治理门禁，再对 final current identity 双审 PASS0。
6. push formal PR、请求 Codex review、等待 required checks、merge，detached fresh-main 复验。

**禁止**：本阶段修改 `src/**` 或测试逻辑。
**回退**：revert formal PR；GAP-15/T58 保持 open。

### Phase 1：dev TDD 与最小实现

1. 从 formal fresh main 创建 `feature/214-workitem-readonly-adapter-side-effect-dev` 与独立 worktree。
2. 创建唯一新测试文件 `test_cli_workitem_adapter_dispatch.py`；删除既有 init 测试文件中冻结错误合同的
   `test_workitem_non_init_runs_adapter_before_handler_once`，由新文件的参数化 `plan-check normal` 格承接反转
   后的分发断言。除此迁移外，既有 init/link 文件只补 hook 时序与两类 outcome；产品源码未改时运行
   V1 RED，记录失败格、代表性 real-hook hash/write/output evidence。
3. 仅把 `_workitem_before_command()` 收敛为 `link` 才继续，禁止修改其他产品函数。
4. 跑 V1～V6 GREEN：15 格、一组 `plan-check` real-hook A/B、共享 partial-write、`init/link` 两类 outcome、
   full、Ruff、constraints。
5. 复核产品 diff 只有一个函数，无公共符号/依赖/配置/版本变化。

**停止**：需要改 adapter 算法、handler、root callback、其他 CLI family 或新增抽象。
**回退**：revert 单一实现 commit；formal 仍有效，T66 保持阻断。

### Phase 2：implementation truth、最终审查与 mainline

1. 先完成 implementation execution log、RED/GREEN/real-hook receipt、program truth、root/scoped handoff与
   V1～V6；冻结 committed+clean terminal identity、source/test diff 与 manifest snapshot。
2. Pascal 从最小性、直接性、测试重复、YAGNI 审查；Confucius 从解析时机、负路径、输出/bytes、平台、
   rollback 审查。任一文件变化使双方 verdict 同时失效；修正后先重跑相关 gate/truth，再对新身份双审。
3. 双 PASS0 后不得再改内容；push implementation PR、请求 Codex current-head review并 heartbeat required checks。
4. merge 后 detached fresh-main 重跑 V1～V6、truth/manifest/scope/parity/Cursor/clean；只声明
   implementation accepted，GAP-15/T58 仍 active，T66 仍 blocked。

### Phase 3：独立 lifecycle reconciliation 与关闭

1. 从 implementation fresh main 创建 `codex/214-workitem-readonly-adapter-side-effect-lifecycle`；只修改
   child/parent lifecycle docs、program truth、root/scoped handoff和必要的 manifest exact 机械期望。
2. 写入 implementation reviewed/merge/fresh-main receipts，把 GAP-15/T58 标记 closure-ready/active、
   T42 保持 in_progress、T66 保持 blocked；本分支不得修改 `src/tests`、依赖、workflow 或版本。
3. 先同步 truth/handoff并跑 constraints/validate/truth/manifest/scope/parity/Cursor/clean，再由 Pascal/
   Confucius 对 final committed+clean lifecycle identity 双审 PASS0。
4. push lifecycle delivery PR、Codex current-head review、required checks、merge、detached fresh-main；只有该
   fresh-main 通过后，才从新 main 创建独立 receipt branch/PR，落盘 GAP-15/T58 closed/completed、T42
   completed 与 T66 ready。Receipt 本身也必须同身份双审、Codex/checks、merge/detached fresh-main；全部通过后
   才创建独立 T66 implementation WI并先执行 T61A 双 readiness。

**回退**：implementation 已 merge、delivery 未 merge时直接 revert implementation PR；delivery 已 merge但
receipt 未生效时先 revert/correct delivery source，再 revert implementation，不得回退不存在的 closure
receipt；receipt 已生效时先 revert/correct receipt 以重开 GAP-15并阻断 T66，再依次 revert delivery 与
implementation。不得留下 closed truth 指向 legacy behavior。

## 7. 证据与路径边界

允许的产品/测试路径：

```text
src/ai_sdlc/cli/workitem_cmd.py
tests/integration/test_cli_workitem_init.py
tests/integration/test_cli_workitem_link.py
tests/integration/test_cli_workitem_adapter_dispatch.py
tests/unit/test_cli_hooks.py
```

Formal/lifecycle 可修改 WI214、WI196、WI213 对账文档、program manifest/truth、root/scoped handoff及
manifest exact 机械期望。不得修改 workflow、provider、runtime rule、依赖、版本或 T66 product/proof。

## 8. 开放问题

无用户决策项。测试布局已冻结为一个新增参数化 dispatch 文件 + 两个既有 init/link 文件；禁止再创建测试
DSL、fixture framework 或五套 handler 业务副本。
