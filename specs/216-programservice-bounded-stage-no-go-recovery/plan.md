# ProgramService 有界阶段 NO-GO 恢复实施计划

> **给 agentic workers：**执行本计划时使用 `superpowers:executing-plans`；在任何完成声明前使用
> `superpowers:verification-before-completion`。所有命令在隔离 worktree 中以 PowerShell 执行。

**目标**：把 WI215/T66 失败路线作为 records-only NO-GO receipt 合入 fresh main，保持产品、测试逻辑/
fixture 与版本零差异；测试唯一例外是 manifest exact 两个计数标量，并为未来真正净删的独立 formal
候选保留清晰入口。
**架构**：不改运行时架构；只更新 WI196→WI213→WI216 治理链、program manifest truth 和 continuity。
**技术栈**：Markdown、YAML、Git、`uv run ai-sdlc`、PowerShell、两位本地对抗 reviewer。

## 全局约束

- 工作目录固定为
  `/Users/sinclairpan/project/Ai_AutoSDLC/.worktrees/216-programservice-bounded-stage-no-go-recovery`。
- 基线固定为 `origin/main@7922956d3e248a93c3190240259850ab3498ec9f`；不得混入主工作树既有改动。
- 只允许 WI196/WI213/WI216 records、`program-manifest.yaml`、project-state、WI216 root/scoped handoff，
  以及 manifest exact 测试两个计数标量。
- 不运行会写产品状态的 managed delivery，不变更版本，不把两个失败证据分支推送为候选；唯一推送例外
  是 exact SHA 对应的契约冻结非合入 archive refs。
- 任一内容变更后重新计算 formal-nine；任一 commit/tree 变化后重新做最终双审。

## Task 1：建立 records-only 恢复合同

**文件**：

- 新建 `specs/216-programservice-bounded-stage-no-go-recovery/{spec.md,plan.md,tasks.md,task-execution-log.md,development-summary.md}`。
- 修改 `specs/196-ai-sdlc-lean-code-self-reduction-governance/{spec.md,plan.md,tasks.md,task-execution-log.md,development-summary.md}`。
- 修改 `specs/213-programservice-bounded-stage-reduction/{spec.md,plan.md,tasks.md,task-execution-log.md,development-summary.md}`。

**步骤**：

1. 写入 immutable baseline、C2-safe、spike commit/tree/blob。
2. 写入稳定账本：C2 `558/64 vs 495/63`、product净增35、proof净增285；spike
   `1209/164 vs 842/92`。
3. 把 T66 本次实现标为 `cancelled_no_go`；保持 GAP-03/WI196/RC-08/release open。
4. 明确 C2-safe/spike 为 `archived_not_merged`，产品、候选测试/proof 不进入本分支；manifest exact
   两个机械标量不是候选测试。
5. 检查范围：

   ```powershell
   git diff --name-only origin/main...HEAD
   git diff --check
   ```

**停止**：缺任何不可变证据、状态出现假关闭、diff 含产品或测试逻辑/fixture，或测试 diff 超出
manifest exact 两个计数标量时，立即修正，不进入评审。

## Task 2：formal-nine 对抗评审

formal-nine 是 WI196、WI213、WI216 各自的 `spec.md + plan.md + tasks.md`。唯一 hash 算法：

```powershell
$roots = @(
  'specs/196-ai-sdlc-lean-code-self-reduction-governance',
  'specs/213-programservice-bounded-stage-reduction',
  'specs/216-programservice-bounded-stage-no-go-recovery'
)
$files = foreach ($root in $roots) { "$root/spec.md"; "$root/plan.md"; "$root/tasks.md" }
$rows = foreach ($file in ($files | Sort-Object)) {
  "$((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant())  $file"
}
$payload = [Text.Encoding]::UTF8.GetBytes(($rows -join "`n") + "`n")
[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($payload)).ToLowerInvariant()
```

1. 提交 committed+clean authoring identity。
2. Pascal/LEAN 审查完整计数、净删除真实性、YAGNI、future route 是否直接。
3. Confucius/SAFETY 审查功能保持、证据可追溯、状态转换、回退与 release 边界。
4. 任一 finding 成立时最小修正、重新提交，并让双方对新的同一 formal-nine 复审。
5. 只有双方均为 `PASS0/findings=0` 才进入 truth；不得拼接不同轮次 verdict。

## Task 3：同步 program truth 与 continuity

**文件**：

- 修改 `program-manifest.yaml`。
- 修改 `.ai-sdlc/project/config/project-state.yaml`。
- 修改 `tests/integration/test_repo_program_manifest.py`，仅替换 inventory/close 两个期望标量。
- 修改 `.ai-sdlc/state/codex-handoff.md`。
- 新建 `.ai-sdlc/work-items/216-programservice-bounded-stage-no-go-recovery/codex-handoff.md`。

**步骤**：

1. 注册 WI216 及对 WI196、WI213、WI214 的依赖；把 `next_work_item_seq` 从215推进到217，其中 WI215
   明确保留为未合入实验编号。
2. 执行机械 truth sync：

   ```powershell
   uv run ai-sdlc program truth sync --execute --yes
   ```

3. 维护 root/scoped handoff byte-identical；不使用可能跟随旧 checkpoint 的 handoff CLI。
4. 验证：

   ```powershell
   uv run ai-sdlc program truth status
   uv run ai-sdlc program validate
   uv run ai-sdlc verify constraints
   Compare-Object (Get-Content .ai-sdlc/state/codex-handoff.md -Raw) (Get-Content .ai-sdlc/work-items/216-programservice-bounded-stage-no-go-recovery/codex-handoff.md -Raw)
   ```

## Task 4：records-only 最终验证与双审

1. 运行仓库现有 manifest exact、scope/continuity 与相关治理测试；先从测试清单定位精确命令，禁止猜测。
2. 验证 `origin/main...HEAD` 中 `src/**`、测试逻辑/fixture、workflow、依赖、版本、release diff 均为零；
   测试 diff 必须恰为 manifest exact 的两个标量。
3. 将 exact audit identities 持久化为非合入 archive：

   ```powershell
   git push origin 70f19275150831ceea89a6c1e006c056ee98c412:refs/heads/codex/archive/215-programservice-bounded-stage-c2-safe
   git push origin 60dcc4f65f2a332261b765bfe5fff9979397ddc7:refs/heads/codex/archive/215-nine-stage-no-dsl-no-go
   git ls-remote --heads origin refs/heads/codex/archive/215-programservice-bounded-stage-c2-safe refs/heads/codex/archive/215-nine-stage-no-dsl-no-go
   ```

   两个 ref 不开 PR、不 force-push、不删除；返回 SHA 必须逐字匹配。
4. 提交 final records identity，保持 clean。
5. Pascal/LEAN 与 Confucius/SAFETY 对同一 final HEAD/tree/formal-nine 复审；两者必须一致 PASS0。
6. 把 verdict、命令和结果只追加到 execution log/summary/handoff；若这些 records 变化，再对最终 commit/tree
   做 records-only 身份复审。

## Task 5：PR、合并与 detached fresh-main

1. 推送 `codex/216-programservice-bounded-stage-no-go-recovery` 并创建 records-only PR。
2. 按仓库协议请求 Codex review、保持约五分钟 heartbeat，监控 current HEAD 与 required checks。
3. 可操作 finding 只做范围内最小修复，并重新执行 Task 2～4。
4. current-head 无可操作 finding、required checks 全绿且本地双审仍有效后 squash merge；保留本地分支。
5. 在独立 detached fresh-main 重跑 truth/constraints/validate/manifest/scope/parity/clean。
6. detached fresh-main 通过只关闭 WI216 records recovery，不关闭 GAP-03/WI196/RC-08/release；用户原目标继续
   等待新的真实净删 formal 候选。

## 回退

- PR 合并前：不得只放弃 WI216 后恢复旧 T66 路线；保留 remote archive，并在 replacement records PR
  合入前把 T66 维持 fail-closed。
- 合并后 fresh-main 失败：优先提交修正 receipt，只回退错误 truth/continuity 字段并保留 NO-GO、archive 与
  `next_work_item_seq=217`。禁止单独 revert 整个 WI216 造成 T66 误解锁；若安全原因必须 full revert，先以
  独立紧急 freeze commit 保留 `cancelled_no_go` 和禁止候选准入，再执行 revert。
- 未来候选：另建 formal WI，重新采集完整 legacy 账本；不得继承 WI215 的 GO、hash 或 reviewer receipt。
