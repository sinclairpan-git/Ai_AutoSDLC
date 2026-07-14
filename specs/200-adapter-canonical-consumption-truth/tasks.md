# 任务分解：Adapter Canonical Consumption Truth Separation

**编号**：`200-adapter-canonical-consumption-truth` | **日期**：2026-07-14
**来源**：`spec.md` + `plan.md` | **关联**：GAP-10 / T53B

## Batch 1 — formal freeze 与对抗评审

- [x] **T11 根因与合同冻结**
  - 文件：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
  - 验收：NC-01～NC-06、受影响 CC、superseded contracts、预算、停止/回退齐全
  - 验证：占位扫描、文档对账、`git diff --check`

- [x] **T12 同一 hash 双 Agent PASS**
  - 依赖：T11
  - 验收：安全/证据真实性 agent 与精简/效率 agent 独立复算同一 review target hash 并明确 PASS
  - 停止：任一目标文档变化立即使既有 verdict 失效并重审

## Batch 2 — TDD truth correction

- [x] **T21 RED：repository truth 不得依赖 local adapter state**
  - 依赖：T12
  - 文件：`tests/unit/test_program_service.py`、`tests/integration/test_repo_program_manifest.py`
  - 验收：missing/unverified/verified local config 得到相同 repository capability；required evidence 为 121/122/159/200
  - 验证：`uv run pytest tests/unit/test_program_service.py -k "host_ingress and canonical" tests/integration/test_repo_program_manifest.py -q`

- [x] **T22 RED：digest transport 不得自证 consumption**
  - 依赖：T12
  - 文件：`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`
  - 验收：env match、旧 persisted verified、adapter exec child 均不能产生 trusted consumption verified；transport detail 必须精确等于 spec 冻结的否定式文案，并禁止旧 `Canonical adapter content consumption is recorded from machine-verifiable evidence` 肯定式文案
  - 验证：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py -k "canonical_consumption or adapter_exec" -q`

- [ ] **T23A GREEN Commit A：runtime 安全底线**
  - 依赖：T22
  - 文件：`src/ai_sdlc/integrations/ide_adapter.py`、对应 adapter tests
  - 验收：self-generated/manual env 永不产生 consumption verified；detail 无可信度升级；公共 carrier surface 不变
  - 提交/回退：独立提交 A；不得整体 revert 回 self-certified verified，只允许 forward fix 或保留 hard unverified 的局部回退
  - 验证：T22 命令转绿 + `git diff --numstat`

- [ ] **T23B GREEN Commit B：repository truth 分层**
  - 依赖：T21、T23A
  - 文件：`src/ai_sdlc/core/program_service.py`、`program-manifest.yaml`、对应 ProgramService/manifest tests
  - 验收：local config/env 不再影响 repository capability；新增产品总计 ≤12 LOC、净产品总计 ≤-15 LOC、0 公共抽象
  - 提交/回退：独立提交 B；可单独 revert，回退后因 A 保留而稳定 blocked
  - 验证：T21 命令转绿 + `git diff --numstat`

## Batch 3 — 证据、回归与交付

- [ ] **T31 脱敏 Codex canonical acceptance**
  - 依赖：T23B
  - 验收：记录 boolean match、AGENTS digest、Codex version、exit code、duration；prompt 原文不落盘
  - 验证：`codex debug prompt-input` 的流式 JSON 只进入本地布尔/摘要计算

- [ ] **T32 全量验证与 truth 收口**
  - 依赖：T31
  - 验收：在隔离临时 worktree 只 revert Commit B 后 runtime 仍 unverified、repository 稳定 blocked；targeted/full pytest、Ruff、constraints、program validate、truth sync/audit、close-check 全通过；Cursor 副作用已精确恢复
  - 验证：见 execution log 真实命令与结果

- [ ] **T33 最终双 Agent / Codex / CI 评审**
  - 依赖：T32
  - 验收：两个本地对抗 agent 对同一最终 HEAD/diff PASS；GitHub Codex 无 actionable findings；required checks 全绿

- [ ] **T34 PR merge 与 mainline fresh verification**
  - 依赖：T33
  - 验收：PR merge 到 main；fresh `origin/main` worktree 在无 local config 时 targeted/truth/status smoke 通过

## 合同映射

| 合同 | 任务 |
|---|---|
| NC-01 / NC-02 | T11、T21、T22 |
| NC-03 / NC-06 | T11、T23A、T23B |
| NC-04 | T21～T34 |
| NC-05 | T11、T32、T34 |
| CC-01/02/03 | T22、T23A、T32 |
| CC-05/06 | T21、T23B、T32 |
| CC-07/08 | T32、T34 |
| FR-200-001～008 | T21～T34 |
| SC-200-001～006 | T12、T21～T34 |
