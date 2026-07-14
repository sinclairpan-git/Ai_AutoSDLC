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

## 8. Batch 2026-07-14-007：T21/T22 RED

- docs baseline：`dc5cd531`；已 fast-forward 到 `feature/200-adapter-canonical-consumption-truth`。
- 测试预算：4 个获准文件，`30 additions / 30 deletions`，净增长 0，无新 fixture/snapshot。
- T21 RED：missing/unverified local config 均错误返回 repository `blocked`，root manifest required evidence 仍缺 159/200；`3 failed, 1 passed`。
- T22 RED：env digest match、CLI status、adapter exec child 均错误返回 consumption `verified`；`3 failed, 3 passed`。
- 失败均命中冻结根因；未出现无关测试错误。下一步先实现并独立提交 Commit A runtime 安全底线。

## 9. Batch 2026-07-14-008：Commit A GREEN（提交前）

- 产品变更仅 `src/ai_sdlc/integrations/ide_adapter.py`：`6 additions / 45 deletions`，删除 persisted verified helper/分支；新增量低于 12 LOC，净 `-39 LOC`。
- digest/path match 固定为 `unverified` + `transport:env:AI_SDLC_ADAPTER_CANONICAL_SHA256` + 空 `consumed_at`；detail 精确为冻结的否定式文案。
- `adapter exec` surface、env 注入、timeout、退出码未改；detail 仅加入既有 status/governance JSON 输出，不写回 ProjectConfig schema。
- T22 targeted：`6 passed, 49 deselected`；adapter unit+CLI full：`55 passed`；相关 Ruff：PASS；`git diff --check`：PASS。
- 下一步：提交独立 Commit A；随后只做 repository truth Commit B。

## 10. Batch 2026-07-14-009：Commit B GREEN（提交前）

- Commit A：`68ff711e`，独立包含 runtime fail-closed 安全底线及对应测试。
- Commit B 产品变更：`src/ai_sdlc/core/program_service.py` 为 `0 additions / 29 deletions`；删除 local adapter gate、专用常量/提示/import。`program-manifest.yaml` 将 goal 与 required evidence 收口为 121/122/159/200，160-163 保留 provenance，并补齐 WI200 release-scope role/capability ref。
- 累计产品代码预算：`6 additions / 74 deletions`，净 `-68 LOC`；2 个产品文件，0 公共抽象。
- 累计测试预算：`30 additions / 31 deletions`，净 `-1 LOC`；4 个文件，0 fixture/snapshot。
- T21：`4 passed, 402 deselected`；T21+T22 combined：`10 passed, 451 deselected`；相关 Ruff 与 constraints：PASS。
- 首次 `program validate` 准确拦截 WI200 manifest entry 缺 role/capability ref；补齐后复跑 PASS，仅保留 33 条历史 release migration warning。两次 CLI Cursor 副作用均已精确恢复，当前零 diff。
- 下一步：提交独立 Commit B，然后进入脱敏 probe、选择性回退演练和全量验证。

## 11. Batch 2026-07-14-010：Commit B、脱敏 probe 与选择性回退

- Commit B：`f384f20f`；A/B 已保持独立提交边界。
- 脱敏 Codex acceptance：`embedded_match=true`；`AGENTS.md sha256=20cfaecf63092a2294f0154efddecb1e686a7a38bc569de2d2dc962ef1b9db41`；`codex-cli 0.137.0`；exit `0`；duration `36.573s`；stderr empty。完整 prompt 未输出、未落盘。
- 首次回退演练返回 repository ready；诊断确认临时进程被 active editable install 劫持，实际加载的是主 worktree 模块，故该结果无效且未计为证据。
- 修正后显式移除 editable finder、将临时 worktree `src` 置于首位，并验证两个模块均来自 temp。仅 revert B 后：runtime=`unverified`，evidence=`transport:env:AI_SDLC_ADAPTER_CANONICAL_SHA256`，repository=`blocked`，blocker=`adapter_canonical_consumption:unverified`。
- 临时 worktree 已删除；下一步执行 full pytest/Ruff、truth sync/audit、close-check 与最终预算核验。

## 12. Batch 2026-07-14-011：全量验证与 self-close 依赖修正

- 全量 `uv run pytest -q`：`3186 passed, 3 skipped in 441.50s`；全仓 `uv run ruff check .`：PASS。
- truth sync 首轮正确发现 `close_check:specs/200-adapter-canonical-consumption-truth` 尚未通过；WI200 direct close-check 进一步显示 T33/T34、log/profile、branch lifecycle 与 program truth 等未完成项。
- 根因：把当前 WI200 自身 close-check 作为 capability required close evidence，会要求在最终双审、CI、PR merge 前先完成这些动作，形成 self-close 依赖。未扩大 filter、未提前勾选或重定义 T33/T34。
- 两名原对抗 agent 基于现场证据独立一致推荐 B：truth refs 保留 121/122/159/200，close refs 仅保留已闭合的 121/122/159；拒绝 follow-up closure PR、新 WI、waiver/filter 与假完成。
- 已按该边界同步 formal docs、manifest 与既有 test；旧 formal verdict 因目标变化失效，下一步重新做同哈希双 Agent review。

## 13. Batch 2026-07-14-012：self-close 修正同哈希双 PASS

- 修订后的 formal review target：`edd7d503ed01beb7bdddd2eb65178b75820d556300e7d6e5f63d76e3f8e046f8`。
- 安全 agent 独立复算：PASS；确认 fail-closed、B-only rollback、truth 200 保留、T33/T34 不提前完成且未削弱 close-check。
- 精简 agent 独立复算：PASS；确认未新增 WI、follow-up closure PR、filter、waiver、schema 或产品代码，预算边界不变。
- 下一步：复跑 targeted、validate、truth sync/audit；capability 应由 121/122/159 close + 121/122/159/200 truth 确定为 ready，WI200 direct close-check 继续如实保持交付期未完成。

## 14. Batch 2026-07-14-013：T32 最终验证画像

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/core/program_service.py`、`program-manifest.yaml`、4 个既有测试文件、`specs/200-adapter-canonical-consumption-truth/` 与 continuity state。
- 统一验证命令：
  - `uv run pytest -q`：`3186 passed, 3 skipped in 441.50s`。
  - `uv run ruff check .`：PASS。
  - `uv run ai-sdlc verify constraints`：`no BLOCKERs`。
  - `uv run ai-sdlc program validate`：PASS，保留 33 条历史 migration warning。
  - `uv run ai-sdlc program truth sync --execute --yes` + `program truth audit`：snapshot `fresh`；adapter capability `closure=closed`、`audit=ready`；全局 inventory 仍为 migration pending 33。
  - required close refs `121/122/159` 通过 ProgramService 同一路径逐项复核：全部 `true`。
- 选择性回退：只 revert B 后 runtime=`unverified`、repository=`blocked`；A 安全底线保留。
- 预算：产品 `6 additions / 74 deletions`，净 `-68 LOC`；测试 `30 additions / 31 deletions`，净 `-1 LOC`；2 product files、4 test files、0 公共抽象/fixture/schema。
- 代码审查：self-close 现场 finding 已由两个原维度 agent 一致推荐 B，并对修订 formal hash `edd7d503...` 双 PASS；最终 clean-HEAD 实现复审仍待 T33。
- 任务/计划同步状态：T21～T32 已按真实证据完成；T33/T34 保持未勾选，等待本地终审、GitHub Codex/CI、PR merge 与 mainline smoke。
- **已完成 git 提交**：是（实现提交 A/B 已独立完成；本批 evidence/truth 随后固化）
- **提交哈希**：`f384f20f`（Commit B；Commit A 为 `68ff711e`）

## 15. Batch 2026-07-14-014：clean-HEAD 双审 findings

- 审查目标：`4d96459003ef9f14a8055f0c760f701993703971`；两个 agent 均独立读取同一 clean HEAD，并返回 FAIL。
- 安全 finding 成立：`adapter status --json` 未获准新增 `adapter_canonical_consumption_detail`，且为该字段二次调用 evaluation 会产生非原子状态；最小修复为删除新增字段与第二次 evaluation，以既有 result/evidence/consumed_at 表达边界。
- 精简 findings 成立：T31/T32 勾选后 formal 三件套当前 hash 已变化，旧 `edd7d503...` verdict 失效；三个测试名仍描述旧行为；两份 handoff 在 evidence commit 后仍写 pending。
- 处置：不新增 schema/抽象/路径；删除 2 行产品字段暴露，测试改为明确断言字段不存在并重命名，同步 continuity；验证、truth sync 与证据提交后重新执行同 HEAD 双审。
- formal 三件套按冻结算法独立复算为 `d37fe1c548323ced601d4583ea81129cb2ffbcb3cdec63e5303e30978970bed7`；该 hash 在复审前不再变更。

## 16. Batch 2026-07-14-015：review remediation GREEN

- 已删除治理 surface 的新增 detail 字段和第二次 canonical evaluation；既有 JSON 字段集合恢复不变，runtime 仍由 `unverified`、transport evidence、空 consumed_at 表达可信度边界。
- 三个反向命名测试已改为当前语义；CLI 测试明确断言 `adapter_canonical_consumption_detail` 不存在；未新增 schema、抽象或执行分支。
- targeted：`9 passed, 452 deselected`；adapter unit+CLI：`55 passed`；全量：`3186 passed, 3 skipped in 426.60s`；相关 Ruff 与 `git diff --check`：PASS。
- 最终预算：产品 `+4/-74`，净 `-70 LOC`；测试 `+30/-38`，净 `-8 LOC`；2 product files、4 test files、0 public abstractions/fixtures/schema。
- formal target 独立复算仍为 `d37fe1c548323ced601d4583ea81129cb2ffbcb3cdec63e5303e30978970bed7`；旧 clean-HEAD verdicts 保持失效，等待修复提交后的同 HEAD 双审。
- **已完成 git 提交**：是（截至本批已有 evidence commit `4d964590`；本轮 focused repair 待固化）
- **提交哈希**：`4d96459003ef9f14a8055f0c760f701993703971`
