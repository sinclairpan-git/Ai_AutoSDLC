---
related_plan: "specs/203-finalization-command-family-reduction-contract/plan.md"
related_doc:
  - "specs/203-finalization-command-family-reduction-contract/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：Program Finalization Command Family Reduction Candidate

**编号**：`204-program-finalization-command-family-reduction-candidate`
**日期**：2026-07-15
**规格**：`specs/204-program-finalization-command-family-reduction-candidate/spec.md`

## 1. 实施结论

采用“保护先行、单 stage 迁移、legacy 默认、差分后切换”的最短闭环。WI-203 已冻结完整
Reduction Contract，本计划不再设计第二套 runner 框架或测试 DSL，只补 candidate 必需的
binding、账本和执行顺序。

Formal 与实现分支严格分离：

```text
docs branch / formal dual PASS / mainline receipt
  → implementation branch / T61A ≤180
  → readiness dual GO
  → one-stage TDD
  → nine-stage candidate + legacy fallback
  → T61B + rollback + candidate PR
  → future stable Vn
  → future independent deletion Vn+1 + rollback + settlement
```

## 2. 技术背景与结构

**语言**：Python 3.11/3.12
**CLI**：Typer + Rich
**测试**：pytest、Ruff；复用 59 CLI + 106 service tests
**平台**：Windows、macOS、Linux；PowerShell 与离线安装链
**核心约束**：WI-203 CC/RC 全量继承；产品新增≤303、保护新增≤180、函数≤50

计划中的唯一新产品文件：

```text
src/ai_sdlc/cli/_program_finalization_runner.py  # private, ≤230 LOC
src/ai_sdlc/cli/program_cmd.py                   # 9 thin adapters + selector ≤70, glue ≤3
```

测试优先放在既有 `tests/integration/test_cli_program.py`；只有当单文件维护性明显下降时才允许
一个同目录 private candidate harness/test module，且所有新增手写 LOC 仍计入同一 180 行 claim。

## 3. 阶段计划

### Phase 0：Formal admission

1. 证明 current baseline 与 WI-203 target/test blobs 无漂移。
2. 冻结 claim key、planned=175、hard=180、owner、deadline 与范围。
3. 两个对抗 reviewer 对同一 formal hash 独立审查，修复后重复至共同 PASS。
4. 运行 constraints、truth、path whitelist、diff check；仅 docs/state/manifest 与
   `test_repo_program_manifest.py` 两个既有 tuple 的 `1071→1076`、`203→204` 精确同步进入
   formal PR，不新增测试逻辑或触及其他测试文件。
5. PR 经 Codex review、required checks 后合入 main；本阶段不授权产品编码。

**回退**：revert formal PR；effective claim 保持 0。

### Phase 1：T61A 与实现准入

1. 从 formal merge 后 main 新建 activation-only branch/worktree；只读重算 target/renderer/
   ProgramService/test blobs、LOC、branch proxy 与 public surface。
2. 写入固定 owner、implementation branch、handoff、baseline 与时限的 active receipt，通过不含
   产品/测试代码的独立 PR 合入 main；exact receipt commit 成为 main ancestor 前不得生效。
3. 从 activation merge 后 main 新建 implementation branch/worktree。只有 mainline active receipt
   可见后，才先跑 165 个既有测试并实现参数化 capture/differential/ledger；首份 evidence 转
   `verified`，以后逐 commit 计 actual claim。
4. 捕获固定环境 runtime p50/p95；覆盖 WI-203 T61A 的失败、中断、路径、编码和 outer hook 矩阵。
5. 两个 reviewer 审查 T61A evidence、实际 claim 和拟议产品切片；共同 `GO` 才进 Phase 2。

**停止**：actual protection>180、基线漂移、场景只能靠复制 snapshot 或弱化 normalizer 完成。

### Phase 2：TDD 与 staged candidate

1. 建立只对 candidate seam 失败的红灯，不改 public command。
2. 实现单一 private runner，只迁 `cross-spec-writeback`；产品 ledger 先验证≤285目标可达。
3. 按一个 commit/一个可验证切片迁移剩余 stage，selector 仍指向 legacy。
4. 每步运行对应既有 tests、candidate differential、LOC/AST/保护区 hash。
5. 全部 stage 一致后，将 internal selector 切到 candidate；不暴露 public flag，且完整 legacy
   继续共存。Family≤519、净删≥1,501 等只在本阶段做 post-deletion projection。

**停止**：runner 需要 command-name `if/elif`、optional writer、reflection/DSL、保护区修改，或
产品新增>303。

### Phase 3：T61B、rollback 与 candidate PR

1. 在 byte-identical baseline/candidate clone 跑完整 T61B，逐项输出 diff receipt。
2. 运行 p50/p95 复测、9-stage chain、platform matrix 与 full suite。
3. 以 selector-only commit 切回 legacy，验证 transcript/artifact/side-effect tree 后再恢复 candidate。
4. 两个 reviewer 对 candidate tree 独立 PASS；Codex review 无 actionable finding。
5. 合入 candidate PR，但保留 legacy body；状态写为 `candidate_merged_awaiting_stable_release`。

**回退**：candidate merge 前切 selector；merge 后 revert candidate PR。不得提前删除 legacy。

### Phase 4：后续交付边界

Stable Vn、安装产物/平台/offline/sibling smoke、独立 deletion Vn+1、真实
`Vn+1→Vn→Rlegacy→Vn+1` rollback 与 sponsor settlement 由后续 mainline 节点执行。只有这些
证据完成后，父路线图才记录实际净减重；WI-204 的 candidate merge 不能提前领取成果。

## 4. 关键验证

| 关键路径 | 必须证据 |
|---|---|
| baseline | revision/blob/SHA/LOC/AST 一致 |
| sponsor | unique key、planned/actual/hard cap、状态与 deadline |
| public surface | 33 command discovery；9 command help/options/docstring |
| behavior | exit/stdout/stderr/call order/raw bytes/tree/mode/side effects |
| renderer | source hash、调用次数、40/80/120 width 字符一致 |
| failures | load/validation/executor/writer/report/interruption/retry |
| paths | relative/absolute/`../`、Unicode、locale/encoding、external sentinel |
| size | protection≤180；product≤303；family≤519；net delete≥1,501 |
| performance | candidate p95 regression≤10% |
| rollback | selector-only legacy route evidence |

## 5. 开放问题

无。T61A 结果只允许产生 `GO` 或 RC-09 `No-Go`，不能扩大预算或缩小兼容矩阵。
