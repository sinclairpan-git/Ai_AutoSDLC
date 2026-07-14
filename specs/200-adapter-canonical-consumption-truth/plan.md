# 实施计划：Adapter Canonical Consumption Truth Separation

**编号**：`200-adapter-canonical-consumption-truth` | **日期**：2026-07-14 | **规格**：`specs/200-adapter-canonical-consumption-truth/spec.md`

## 1. 决策摘要

采用双层真值：

```text
tracked repository evidence
  └─ ProgramService capability truth: 121 / 122 / 159 / 200

per-session local observation
  └─ adapter status: ingress + canonical transport diagnostics
```

repository capability 只说明 adapter proof/runtime contract 已被实现和关闭；本机会话是否消费 canonical 内容继续由 runtime surface fail-closed 表达。两层不互相升级，也不共享 ignored config。

## 2. 技术背景

**语言/版本**：Python 3.11+
**主要依赖**：Pydantic、Typer、`ProgramService`、`ide_adapter`
**本机存储**：`.ai-sdlc/project/config/project-config.yaml`（ignored，仅 runtime）
**仓库真值**：`program-manifest.yaml` + work-item truth/close evidence
**目标平台**：macOS / Linux / Windows；Codex / Cursor / VS Code / Claude Code adapter surface

## 3. 变更合同

| 项 | 冻结值 |
|---|---|
| 风险等级 | L2 truth correction |
| 受影响 CC | CC-01/02/03/05/06/07/08 |
| 产品预算 | 新增 ≤12 LOC；净 ≤-15 LOC；2 files；0 public abstractions |
| 测试预算 | 新增 ≤30 LOC；目标切片净不增长；4 files；0 fixtures |
| 明确非目标 | receipt/cache/probe command、新 schema、删除 adapter exec、GAP-11、结构减重 |
| rollback | 保留 runtime 安全提交 A；仅 revert repository 分层提交 B，结果必须稳定 blocked |

唯一获准的外部行为差异是：self-generated/手工 env digest match 不再返回 consumption `verified`。命令 surface、字段集合、退出码、传输和 mutate admission 不变。

## 4. 阶段计划

### Phase 0 — formal freeze 与同版本双审

- 冻结 observed/expected、superseded contracts、NC/CC、LOC/file budget、停止/回退。
- 对 `spec.md + plan.md + tasks.md` 复算固定 SHA-256 review target。
- 安全 agent 与精简 agent 必须对同一 hash PASS；任一目标文件变化使旧 verdict 失效。

### Phase 1 — TDD RED

1. `test_program_service.py`：把 local `missing/unverified/verified` 从 repository snapshot 输入中剥离。
2. `test_ide_adapter.py`：digest transport match 与旧 persisted verified 都必须保持 consumption unverified。
3. `test_cli_adapter.py`：carrier 继续执行，但 child status 不得返回 consumption verified。
4. `test_repo_program_manifest.py`：锁定 truth refs=`121/122/159/200`、close refs=`121/122/159`，并保留 `160-163` provenance。

RED 必须归因于当前动态 blocker 与旧 verified 自证逻辑；若失败来自其他领域，停止并先诊断。

### Phase 2 — 最小 GREEN（两个独立提交）

#### 2.1 Commit A：runtime truth correction（安全底线，先落地）

- 删除旧 persisted consumption verified 的保留 helper/分支。
- digest/path match 返回 `unverified` + `transport:env:AI_SDLC_ADAPTER_CANONICAL_SHA256`，`consumed_at` 为空。
- detail 精确等于 spec 冻结的否定式 transport 文案；测试禁止旧 `Canonical adapter content consumption is recorded from machine-verifiable evidence` 肯定式文案。
- no-env/mismatch/generic 继续 fail closed。
- 保持 `adapter exec` 的命令、timeout、env 注入和退出码实现。

Commit A 不得整体 revert 回 self-certified verified；发生兼容回归时只允许 forward fix 或保留 hard unverified 的局部回退。

#### 2.2 Commit B：Program truth 分层（可独立回退）

- 删除 `ProgramService` 的 local adapter canonical release blocker、专用常量/提示和不再需要的 import。
- 更新 capability goal、`spec_refs` 与 required evidence；当前 WI200 只进入 truth refs，close refs 仅使用已闭合的 121/122/159，避免 self-close 循环。
- 不新增替代 helper、waiver 或硬编码 ready。
- 若 Commit B 被 revert，Commit A 仍使旧动态 gate 只能读到 `unverified`，repository capability 因此稳定 blocked，不会恢复本机伪 ready。

### Phase 3 — 验证与真值收口

1. targeted pytest 转绿并核算预算。
2. 运行一次脱敏 `codex debug prompt-input` acceptance；只记录 boolean/digest/version/exit/duration。
3. 在隔离临时 worktree 选择性 revert Commit B，验证 runtime 仍 unverified、repository capability 稳定 blocked；不得 revert Commit A。
4. 运行全量 pytest、Ruff、constraints、program validate、truth sync/audit；核验 required close refs 121/122/159 通过，并如实记录 WI200 direct close-check 尚有 T33/T34/branch lifecycle 等交付期 blocker，不把它作为 capability 输入。
5. 两个对抗 agent 对同一最终 HEAD/diff 再审，直到共同 PASS。
6. push、PR、`@codex review`、约五分钟 heartbeat；修复 actionable findings，全部 checks 通过后 merge。
7. 在 fresh `origin/main` worktree 重跑 targeted、truth 与 adapter status smoke。

## 5. 关键路径与验证

| 路径 | 预期 | 验证 |
|---|---|---|
| repo config missing | capability 只看 tracked evidence | ProgramService unit + fresh worktree |
| repo config unverified/verified | capability/snapshot hash 一致 | parameterized unit |
| env digest match | transport evidence 存在，consumption unverified，detail 无可信度升级 | ide adapter unit/integration exact text |
| old persisted verified | 不再保留 trusted result | ide adapter unit |
| adapter exec | surface/exit 保持，child 不再伪 verified | CLI integration |
| default truth/status | 无 Codex 子进程、无 prompt 落盘 | code review + command timing |
| manifest | truth 121/122/159/200；close 121/122/159；160-163 provenance | repo manifest test + validate |

## 6. 停止与回退

任一条件成立立即停止当前方案：

1. 需要新增公共状态、命令、receipt、cache、probe registry 或通用 evidence framework；
2. `adapter exec` 命令/参数/退出码发生未批准差异；
3. local config 仍影响 repository capability 或 tracked evidence 反向授予 runtime verified/mutate；
4. 产品/测试预算超限或测试场景减少；
5. Windows/macOS/Linux 任一受影响 smoke 回归。

回退顺序：保留 Commit A → 只 revert Commit B → 从回退后的 `program-manifest.yaml` 重建 truth snapshot → 验证 runtime unverified + repository blocked → 复跑 adapter/runtime targeted tests。Commit A 发生实现问题时必须 forward fix，或只回退非安全机械部分并保持 `unverified`；不得整体恢复 self-certified verified，也不得用 ignored local config 恢复 repository truth。

## 7. Review target 算法

在 worktree 根执行：

```text
for f in specs/200-adapter-canonical-consumption-truth/spec.md specs/200-adapter-canonical-consumption-truth/plan.md specs/200-adapter-canonical-consumption-truth/tasks.md; do shasum -a 256 "$f"; done | sort -k2 | shasum -a 256
```

两个 agent 必须独立复算并在 verdict 中写出同一 hash。
