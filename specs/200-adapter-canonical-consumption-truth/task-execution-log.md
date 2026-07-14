# 任务执行日志：Adapter Canonical Consumption Truth Separation

**功能编号**：`200-adapter-canonical-consumption-truth`
**创建日期**：2026-07-14
**状态**：formal freeze 进行中

## 1. 归档规则

- 只记录真实执行的命令、结果、review hash 和 revision。
- prompt-input 原文、用户上下文、system/developer instructions 不落盘。
- 任一 formal review target 变化后，旧双 PASS 自动失效。
- 每个实现批次必须包含 RED、GREEN、预算、回退、代码审查和任务同步状态。

## 2. Batch 2026-07-14-001：根因复现与候选方案收敛

### 2.1 基线与工作树

- 基线：`origin/main@208a34c82da0474a3cf51f3758934a188758b33d`。
- worktree：`.worktrees/200-adapter-canonical-consumption-truth`。
- Stage-1 docs branch：`feature/200-adapter-canonical-consumption-truth-docs`；运行时 branch：`feature/200-adapter-canonical-consumption-truth`。
- PowerShell 在启动前因本机 `System.Text.RegularExpressions, Version=10.0.0.0` 程序集错误退出；本工作项按已记录的兼容回退使用 zsh。

### 2.2 修复前证据

- fresh worktree 不存在 ignored `.ai-sdlc/project/config/project-config.yaml`。
- `uv run ai-sdlc adapter status --json` 返回 detected/target=`cursor`、canonical path=`.cursor/rules/ai-sdlc.mdc`、canonical consumption=`unverified`；同一 commit 的旧工作树曾因本机 config 返回 verified。
- WI162 execution log 证明曾使用 `adapter exec -- ... adapter select` 把 self-generated digest 写回 ignored config；fresh worktree 无法重放该状态。
- 159～163 的 direct close-check 均返回 `ok=true`，说明实现/归档证据已存在，漂移来自 repository truth 读取本机 runtime state。

### 2.3 官方契约与真实 probe

- fresh Codex manual 明确：Codex 在开始工作前读取 `AGENTS.md`，并按 project root 到 cwd 构造 instruction chain。
- 当前 Codex CLI：`0.137.0`。
- `codex debug prompt-input` 现场脱敏检查：当前 `AGENTS.md` 被完整嵌入 model-visible input（`embedded_match=true`）；该命令构造新 invocation，不能证明已经运行中的父会话。
- 结论：probe 可作一次性 acceptance，不进入默认 status/truth，也不生成 tracked prompt receipt。

### 2.4 对抗评审收敛

1. 首轮：两名 agent 均选择 repository/runtime 分层；安全 agent 要求 tracked receipt，精简 agent拒绝第二套证据框架。
2. 核验发现 `artifact_probe_ref` 只有模型字段、未被 ProgramService 消费，且 WI140 明确禁止为 release gate 新建手工 probe registry；因此不新增 receipt/schema/cache。
3. 第二轮：精简 agent 对 `121/122/159/200` required evidence 方案 PASS；安全 agent指出唯一 P0 是 carrier/env 仍输出伪 `verified`。
4. 第三轮：将 digest match 降级为 transport evidence、删除旧 persisted verified 保留链路后，精简 agent PASS；安全 agent已明确该条件满足后无需 tracked receipt。formal hash 双审尚待执行。

### 2.5 当前决策

- 采用 D 分层；repository capability 不读取 ignored config/current env。
- env digest/path 仅为 transport diagnostics，不是 host/current-session consumption proof。
- 不删除 public `adapter exec`，不新增 probe/receipt/registry。
- 下一步：对 formal 三件套计算 hash，两个 agent 同版本审查；共同 PASS 后才进入 TDD RED。

### 2.6 初始化副作用

- `workitem init` 按预期更新 next WI seq、manifest mapping 并生成 formal 四件套。
- CLI 非授权改写 `.cursor/rules/ai-sdlc.mdc`；已使用 `apply_patch` 精确恢复 HEAD 内容，不纳入 WI200。

### 2.7 代码审查与任务同步

- 代码审查：当前仅 formal docs/init metadata，无产品实现。
- tasks 状态：T11/T12 尚未完成；双 Agent 对同一 formal hash PASS 后再勾选。
- branch/worktree disposition：docs branch 完成 formal commit 后 fast-forward 运行时 branch；最终 PR merge 后清理。

## 3. Batch 2026-07-14-002：formal hash 首轮审查与回退修订

- review target：`3e9d08d87f31c4ed7123e8f0d7addeeaae8018e11a586e96d32566a68987005d`；两名 agent 均独立复算一致。
- 精简 agent：PASS。
- 安全 agent：FAIL，两个 findings 均成立：整体 revert 会恢复 self-certified verified；T22 未 exact-lock transport detail 的可信度边界。
- 处置：Phase 2 拆为先落地且不可整体回退的 runtime 安全 Commit A，再落地可独立回退的 repository 分层 Commit B；B 回退后因 A 保留而稳定 blocked。T22/T23A 增加 detail exact semantic assertion，T32 增加隔离 worktree 选择性回退演练。
- 本次修改使旧 hash 与 verdict 全部失效；下一步复算新 hash并重新双审。

## 4. Batch 2026-07-14-003：formal 同版本双 PASS

- 最终 formal review target：`534291f87b5bb8c3357d547a7deb3969c56e834bd95cb385084c515f35bd89c2`。
- 安全 agent 独立复算同一 hash：PASS；确认 Commit A 安全底线、Commit B 选择性回退、T32 隔离演练和 exact detail 合同均 fail closed。
- 精简 agent 独立复算同一 hash：PASS；确认未新增框架/schema/命令/cache/重复 gate，预算与 GAP-10 边界不变。
- T11/T12 已完成；任何 formal 目标文件后续变化都会使本轮双 PASS 失效。
- 下一步：执行 docs-stage 验证并提交 Stage-1 docs baseline；再 fast-forward 到运行时分支进入 TDD RED。

## 5. Batch 2026-07-14-004：任务状态变更后的最终复审

- 勾选 T11/T12 改变了 formal review target，因此 `534291f87b5bb8c3357d547a7deb3969c56e834bd95cb385084c515f35bd89c2` 的双 PASS 已按规则失效。
- 最终冻结 review target：`46e3031afa5e6c72fab993d0d70171d08a8c348bfef72c2e5ccd923bcec387d2`。
- 安全 agent 独立复算该 target：PASS。
- 精简 agent 独立复算该 target：PASS。
- 自本记录起至进入 RED 前，不再修改 `spec.md`、`plan.md`、`tasks.md`；执行证据仅追加到本日志与 handoff。

## 6. Batch 2026-07-14-005：docs-stage 验证

- `git diff --check`：PASS。
- `uv run ai-sdlc verify constraints`：PASS，`no BLOCKERs`。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：PASS，`1 passed`。
- `uv run ai-sdlc program validate`：PASS；同时保留 33 条历史 release truth `migration_pending` warning，本工作项未扩大范围处理。
- CLI 再次改写 `.cursor/rules/ai-sdlc.mdc`；已用精确 `apply_patch` 恢复 HEAD，`git diff --exit-code -- .cursor/rules/ai-sdlc.mdc`：PASS。

## 7. Batch 2026-07-14-006：暂存区盲点修正与最终双 PASS

- 提交前首次对新增文件运行 `git diff --cached --check`，发现生成模板在 11 行保留 Markdown 行尾空格；此前未暂存时的 `git diff --check` 未覆盖 untracked 文件，因此原“PASS”仅覆盖 tracked diff。
- 已仅删除 `spec.md`、`plan.md`、`tasks.md` 的行尾空格；语义与任务状态不变，但按规则使 `46e3031afa5e6c72fab993d0d70171d08a8c348bfef72c2e5ccd923bcec387d2` verdict 失效。
- 最终冻结 review target：`02b86ed28feea46ed3e2cec893a79d997ccc20cbf58945ca88fb5ee3ad85dfe6`。
- 安全 agent 独立复算：PASS；精简 agent 独立复算：PASS。
- `git diff --cached --check`：PASS。后续不再修改 formal target 三件套，直接提交 docs baseline。
