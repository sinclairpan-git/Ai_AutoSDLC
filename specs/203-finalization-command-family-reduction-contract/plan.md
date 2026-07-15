---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：Program Finalization Command Family Reduction Contract

**编号**：`203-finalization-command-family-reduction-contract`
**日期**：2026-07-14
**规格**：`specs/203-finalization-command-family-reduction-contract/spec.md`
**当前阶段**：Phase 0 设计准入；不修改产品代码
**风险等级**：L3

## 1. 概述

以一个 design-only formal PR 冻结 9 个 `program` handler orchestration body 的 WP-07
Reduction Contract。Formal 合入 main 后产生不可变 sponsor receipt；后续独立 candidate WI
按 T61A → TDD → staged migration → T61B → stable release → legacy deletion → rollback rehearsal
执行。任何阶段触发 RC-09 都保留或恢复旧实现。

选择 handler-only，是因为它已达到 `2020 → ≤519`、mirror 下降约 83%、净删除至少 1,501
的硬结果，同时不改 Rich renderer、ProgramService、DTO 或 artifact builder，回归面小于进一步
合并 renderer 的方案。9 个 renderer 以源码哈希和字符级输出 differential 保护，明确不计本项
成果。

## 2. 技术背景

**语言/版本**：Python >=3.11；具体 Python/Typer/Rich/PyYAML 版本由 T61A 固定
**主要依赖**：现有 Typer、Rich、PyYAML；禁止新增运行时依赖
**存储**：现有 `.ai-sdlc/memory/frontend-*` YAML/Markdown 和 optional report；schema 不变
**测试**：pytest、CliRunner、隔离 clone differential、StringIO/Rich Console、release smoke
**目标平台**：Windows、macOS、Linux；PowerShell 与离线安装路径
**固定环境**：`AI_SDLC_DISABLE_UPDATE_CHECK=1` 用于 handler differential；outer hook 另测
**约束**：私有模块≤230行、route adapters/selector≤70行、glue≤3行、函数≤50行、
公共抽象=0、shadow峰值≤303、终态≤519

PowerShell 在当前主机因无效 `System.Text.RegularExpressions, Version=10.0.0.0` assembly
在执行命令前崩溃。该宿主问题记录于 execution log；仓库命令临时使用 zsh 执行，但计划中
面向项目的命令继续以 PowerShell 语法给出，并要求 Windows/PowerShell smoke。

## 3. 宪章与治理检查

| 门禁 | 计划响应 |
|---|---|
| MVP / 范围严控 | 只选 9 个 handler body；thread-archive、renderer、service、DTO 全部排除。 |
| 关键路径可验证 | T61A/B 覆盖 surface、失败矩阵、artifact、side effect、runtime、renderer hash。 |
| 范围/验证/回退 | 每个 phase 有文件边界、命令、stop 与 rollback receipt。 |
| 状态落盘 | formal、baseline、review、handoff、candidate/deletion receipts 均进入 WI 目录。 |
| 产品/治理隔离 | Phase 0 仅 formal/truth/handoff；实现与 deletion 使用后续独立 PR。 |
| 400/50 | 新模块≤230；所有新/修改函数≤50；历史巨文件只减少目标职责。 |
| 单逻辑提交 | formal、candidate、stable release、legacy deletion 分开；candidate 内逐 commit 记 RC-05。 |
| WP-07 / LP-12 | shadow、切换、稳定发布和删旧均完成后才关闭。 |
| PR 协议 | 每个 mainline PR 均 push、Codex review、5分钟 heartbeat、required checks、merge。 |

## 4. 设计结构

### 4.1 当前 formal 产物

```text
specs/203-finalization-command-family-reduction-contract/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── candidate-baseline.json
```

### 4.2 后续 candidate 允许的源码结构

```text
src/ai_sdlc/cli/
├── program_cmd.py                    # 原 public symbols；9 个薄 adapter
└── _program_finalization_runner.py   # 唯一新增私有模块，≤230 LOC
```

私有模块只允许：

- frozen/slots private descriptor；
- 9 个显式 descriptor，绑定 typed service callables/field adapters/text；
- `_run_finalization_command(...)` 与小于 50 行的 resolve/preview/guard/execute/report helpers；
- 不依赖或反向 import `program_cmd.py` 的 renderer；renderer callback 由 handler 显式传入。

禁止：command-name `if/elif`、optional writer、字符串 method name+`getattr`、公共 executor/DSL、
新配置/环境开关、为未来 stage 预留字段。

## 5. 相位计划

### Phase 0：Formal admission 与 sponsor receipt

**目标**：冻结 RC/CC/T61/rollback，不授权实现。
**改动白名单**：本 WI 五个 formal 文件、合法 manifest/project-state/handoff/truth，以及
`tests/integration/test_repo_program_manifest.py` 中仅把既有 inventory tuple
`1066/1066/0/0`、close `202/202` 更新为 WI-203 登记后的 `1071/1071/0/1`、close
`203/202`。不得新增/删除测试逻辑、放宽断言或修改其他 `tests/` 文件。
**验证**：JSON/Markdown lint、constraints、truth audit、diff/path、同 hash 双 Agent。
**完成**：docs-only PR 合入 main，记录 merge commit 和 review target hash。
**回退**：revert formal PR；产品运行时不受影响，所有 sponsor claim 同时失效。

### Phase 1：T61A 旧行为与预算基线

**进入**：Phase 0 receipt 已在 main；candidate 独立 branch/WI；基线 commit 可检出。
**目标**：补齐固定环境 runtime、完整 surface/失败/副作用/golden、renderer hash。
**产物**：surface/runtime/side-effect baseline、golden、normalizer version、RC-05/06 ledger。
**硬门禁**：T61A 完成前不得写 candidate 产品代码。
**停止**：无法隔离外部写、缺少可复算 runtime、renderer hash 不稳定或保护成本预测超 180。

### Phase 2：TDD 私有 runner scaffold

**红灯**：先加入参数化 characterization/differential，证明 legacy 通过、空 candidate seam 失败。
**实现**：新增一个≤230行私有模块；initial shadow module+glue≤233，仅测试直接调用。
**绿灯**：单一 stage 的 dry-run/execute/report/artifact differential 通过。
**停止**：需要 stage-name 特判、service/renderer 修改、module>230 或 module+glue>233。

### Phase 3：建立可回退 candidate route

**策略**：一次为一个 handler 增加私有 candidate route adapter，但完整 legacy body 与 route
必须保留到稳定发布之后。9 个 adapters 加单一 internal selector 合计≤70行，import/glue≤3行；
它们与≤230行私有模块的共存新增总和≤303。不得新增 public CLI/env/config flag。

Internal selector 默认先保持 legacy；单 stage differential 通过后切到 candidate。切换仅改变
私有 binding/constant，回退时能以小型代码变更恢复 legacy。每个 commit 记录
added/deleted/net/coexisting peak；Phase 3 不删除任何 legacy body。

**顺序**：

1. `cross-spec-writeback`，先证明其 orchestration 字段、spec-dir side effect 与 route 回退；
2. guarded → broader → final governance；
3. persistence → persisted proof；
4. publication → closure → archive，重点验证 `soft_wrap` renderer callback 未变化。

**验证**：每步 targeted CLI/service tests；每组三步后 9-command matrix；全部完成后 full suite；
证明 legacy/candidate 两条内部 route 都能运行，且 candidate route 为稳定发布目标。

### Phase 4：T61B candidate differential 与删除前回退

固定 candidate hash，在两份 byte-identical clone 比较 legacy/candidate。默认 dry-run 可在无写
环境比较；所有 report/execute 分别在隔离 clone 运行。跑单命令矩阵和完整 9-stage chain，
比较 transcript、raw bytes、tree/mode、service order、external sentinel、runtime。

删除前 rollback：完整 legacy body 仍在同一候选 revision，内部 selector 指回 legacy，重跑
9 个 transcript/artifact/side-effect tree。
无 public flag。任一未批准差异使 candidate PR 不可 merge。

### Phase 5：Candidate PR 与稳定发布

Candidate PR 提交 T61A/B、before/after、RC ledger、rollback receipt；candidate route 已启用，
但完整 legacy body/route 仍保留。经过本地双 Agent、Codex review、required CI 后合入。发布
candidate stable `Vn`，用 wheel/sdist 安装产物在三平台、offline 和至少 2 个代表性 sibling
project 完成 smoke。每 OS 在两个 clean root 跑完整 9-stage chain，共 54 stage executions；另有
3 次独立 release-smoke job。零未批准差异/新 violation、truth fresh、p95 退化≤10% 后，才允许
deletion。该可复算门槛替代主观日历等待；未满足不得删 legacy route/body。

### Phase 6：独立 legacy deletion 与最终回退演练

独立 PR 删除所有已失活 legacy body/route 和 selector 的 legacy 分支，确认 9 个 renderer 源码
未变，重新运行 targeted、full、platform、offline、installed/sibling smoke，并发布 deletion
stable `Vn+1`。Rollback receipt 从已安装 `Vn+1` 回到 candidate stable `Vn`，验证 transcript/
artifact/side-effect tree 时分两步：安装 `Vn` 只证明 legacy code/route 可用性恢复；随后在精确
`Vn` tag 上应用 selector-only commit `Rlegacy`，构建记录 source commit、filename、SHA256 的
非发布 artifact，安装后实际运行 legacy route。最后重装 `Vn+1` 恢复当前 deletion 状态。
不得把 candidate-active 的 `Vn` 冒充 legacy-active，也不使用无 commit/hash 的临时版本。

只有 Phase 6 证据齐全且 final family≤519、净删≥1,501，candidate 才能
`completed_reduction`。

## 6. T61 测试矩阵

### 6.1 Surface 与失败矩阵

| 维度 | 场景 |
|---|---|
| discovery/help | 33 commands discovery；9 个完整 help；option 顺序/default/help/docstring |
| root/manifest | not-project；`--manifest` default/project-relative/nested-relative/absolute/`../`/missing/malformed/invalid 的既有解析与错误 |
| upstream | missing/malformed/non-completed；completed+blockers；no-required-work |
| steps/path | one-valid；valid+invalid partial；non-manifest/outside/missing spec path |
| accessibility | stable-empty visual/a11y；issue-review |
| modes | dry-run；dry-run+report；execute no yes；execute+yes；execute+yes+report；dry-run+yes |
| failures | step/artifact/report write failures；每个写入边界的 KeyboardInterrupt/SystemExit/隔离进程终止；残留 tree/raw bytes；retry/overwrite/partial mutation/recovery |
| full chain | 9 stages，前一 canonical artifact 可被后一 stage 消费 |
| outer hook | update disabled；uninitialized adapter no-op；initialized no-op；stale managed write；permission warning；help bypass；update→adapter→handler 顺序 |
| path/encoding | root=`项目-é-測試`；manifest=`配置/程序清单.yaml`；report=`报告/结果-é.md`；spec=`specs/001-课程-é`；POSIX surrogateescape；Windows non-UTF8 code page |

### 6.2 观测

- exit code、stdout/stderr 分离；renderer 调用次数按 dry-run/precondition/executor-writer/
  report-failure 矩阵；成功顺序为 `executor→writer→renderer→report`；
- before/after file tree、mode、hash、raw YAML/Markdown/report bytes；
- workspace、`.git`、temp-parent external sentinel、subprocess、network；
- 中断注入点：first step 前、每个 step 后、artifact 前/后、renderer 后、report mkdir/write；
  比较残留文件并重跑到完成；
- handler-only 与 full CLI outer adapter/update hook 分层；
- runtime warm-up 后 p50/p95，candidate p95 允许最多 10%退化且必须复测；
- renderer source hash；width 40/80/120、color off 的逐字符输出，无 normalizer。

### 6.3 Normalizer allowlist

只允许：

1. 两份临时 clone 的绝对 root；
2. 精确 key 为 `generated_at` 的时间；
3. 实际存在并逐字段登记的随机 ID。

禁止全局空白/path separator/time regex、key/list 排序、dedupe、删除 warning/blocker。

## 7. RC-05 / RC-06 账本

### 7.1 RC-05 commit ledger

每个 candidate commit 必须记录：

```text
commit
phase
new_product_loc
deleted_legacy_loc
net_product_loc
coexisting_shadow_loc
module_loc
adapter_loc
glue_loc
verdict
```

`coexisting_shadow_loc≤303` 是逐 commit 硬门槛。当前唯一允许的分配是 private module≤230、
9 个 route adapters+internal selector≤70、import/glue≤3；三项总和也必须≤303。完整 legacy
body/route 在 candidate merge 和稳定发布期间仍存在，不计作新增，但必须在独立 deletion PR
删除。Phase 3 不以提前删除 legacy 换取 shadow 预算。

### 7.2 RC-06 sponsor ledger

| 消费方 | 预算 | 记账规则 |
|---|---:|---|
| candidate T61A/B | ≤180 | 只计新手写 product/test/harness/normalizer；现有测试不计 |
| WI-202 T62A | ≤170 | 其 merged formal 必须声明确切 claim；实现后以实际值结算 |
| reserve | 3 | 不得自动借出 |

理论 25% 上限为 375，但本 receipt 主动只开放 353；合计≤353，且路线累计≤1,500。若
candidate 使用少于 180，剩余也不能自动扩大 WI-202；任何
重新分配都要新的同 hash formal review 和 mainline receipt。

Receipt 状态必须是 `provisional→active→verified→settled`；停滞进入 `stale`，取消、No-Go、被替代、
baseline/scope 变化、receipt revert 或超时进入 `revoked`。Active 30 日内未进入 T61A 自动
revoked；verified 14 日无 evidence 或连续 3 checkpoint blocked 自动 stale。Stale 不得新增
claim，既有 WI-202 claim 7 日内重新获 sponsor 或开始缩减/revert；revoked claim 在下一个
mainline PR 或 7 日内（取先到者）完成替代、缩减或 revert。状态写入 mainline handoff/ledger。
`settled` 只在 deletion `Vn+1`、实际 LOC 结算和 rollback receipt 全部完成后进入；按 actual
deletion 的 25%/路线 1,500 上限永久覆盖既有 actual claims，停止 freshness timeout，不得新增。

## 8. 关键验证命令

面向仓库自开发入口：

```powershell
$env:AI_SDLC_DISABLE_UPDATE_CHECK = "1"
uv run pytest -p no:cacheprovider tests/unit/test_program_service.py tests/integration/test_cli_program.py -k "(cross_spec_writeback or guarded_registry or broader_governance or final_governance or writeback_persistence or persisted_write_proof or final_proof_publication or final_proof_closure or final_proof_archive) and not thread_archive and not project_cleanup"
uv run pytest
uv run ruff check src tests
uv run ai-sdlc verify constraints
uv run ai-sdlc program truth audit
git diff --check
```

Formal PR 额外执行 review-target hash、JSON parse、path whitelist。Candidate/deletion PR 必须
执行 T61 harness、platform/offline/release/sibling smoke；任何失败均先按根因修复，不降级门禁。

## 9. Review target 与证据不可变性

Review target 固定为 `spec.md + plan.md + tasks.md + candidate-baseline.json`，相对路径文本也
进入哈希。`task-execution-log.md` 只追加 review/evidence receipt，不进入 target，避免记录 verdict
本身改变被审内容。Canonical 算法是：每行 `<lowercase file sha256><two spaces><relative path>`，
按 byte-order 排序，以单个 LF 连接，**末尾不加换行**，再对 UTF-8 payload 取 SHA-256。

以下 Python 是唯一规范参考；PowerShell/zsh 仅在产出相同 payload 时等价：

```python
from hashlib import sha256
from pathlib import Path

base = Path("specs/203-finalization-command-family-reduction-contract")
paths = [base / name for name in (
    "spec.md", "plan.md", "tasks.md", "candidate-baseline.json"
)]
lines = sorted(f"{sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}" for path in paths)
print(sha256("\n".join(lines).encode("utf-8")).hexdigest())
```

```powershell
$base = "specs/203-finalization-command-family-reduction-contract"
$files = @("spec.md", "plan.md", "tasks.md", "candidate-baseline.json")
$lines = foreach ($name in $files) {
  $path = Join-Path $base $name
  $relative = "$base/$name"
  $hash = (Get-FileHash -Algorithm SHA256 $path).Hash.ToLower()
  "$hash  $relative"
}
$payload = ($lines | Sort-Object) -join "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$env:TEMP\wi203-review-target.txt", $payload, $utf8NoBom)
(Get-FileHash -Algorithm SHA256 "$env:TEMP\wi203-review-target.txt").Hash.ToLower()
```

任一 target 文件变化使两个 PASS 同时失效，必须对新 hash 重审。

## 10. Stop、回退与开放问题

开放问题：无。路径兼容、renderer 边界、outer hook、预算分配和 release/deletion 顺序均已
冻结。

停止条件以 spec RC-09 为准。Formal 回退是 revert docs PR 并撤销 sponsor；candidate 删除前
切回 legacy route；删除后 revert deletion PR + 回滚 stable release。不得以 waiver、扩大
normalizer、降低平台覆盖或把 renderer 债务冒充关闭来继续投资。
