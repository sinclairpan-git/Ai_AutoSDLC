# 任务分解：Resume-pack 可迁移、无损的 canonical reconstruction

**编号**：`208-resume-pack-portable-lossless-reconstruction`
**父项**：WI-196 `GAP-13 / T56`
**来源**：`spec.md + plan.md`

## Batch 1：诊断与 formal truth

### T11 关闭前置 GAP-12

- **状态**：已完成
- **验收**：WI-207 repair PR #141 merge=`8d8b8f96`；fresh detached main 的 real-hook 4、focused 238、
  full `3224 passed, 3 skipped`、Ruff/format/constraints/validate/truth 全绿，pre/post state 相同且 clean。

### T12 初始化 WI208 canonical formal

- **状态**：已完成
- **依赖**：T11
- **验收**：branch=`feature/208-resume-pack-portable-lossless-reconstruction-docs`，base=
  `origin/main@8d8b8f96`；workitem init 更新 next sequence/manifest；root exact inventory/close 两个值机械
  `1091/207→1096/208`、无测试逻辑/行数变化；非目标 Cursor refresh 已精确恢复。

### T13 冻结根因与 canonical source matrix

- **状态**：已完成
- **依赖**：T12
- **验收**：调用链归一到 `load_resume_pack -> _build_resume_pack_from_checkpoint`；记录 filesystem
  absolute fallback、optional artifact 缺失、WI-182 handoff 与 WI-198 impact；不把旧 pack当来源。

### T14 同步父/前项状态

- **状态**：已完成
- **依赖**：T11～T13
- **验收**：WI-196 GAP-12/T55=closed、GAP-13/T56=active、GAP-14/T57=queued；WI-207 T52/T53
  completed；不关闭 WI-196/GAP-05/RC-08，不发布版本。

## Batch 2：formal 对抗评审与合并

### T21 冻结六文件 review target

- **状态**：已完成；当前六文件 target 已按父计划 §9 冻结
- **依赖**：T14
- **文件**：child 与 WI-196 parent 的 `spec.md / plan.md / tasks.md`
- **验收**：source priority、兼容矩阵、allowlist、预算、RED/GREEN、回退与 fresh-main 可执行；使用父计划
  §9 唯一 canonical combined recipe。

### T22 Pascal 精简/直接性评审

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；历史轮次仅保留在日志
- **依赖**：T21
- **验收**：确认单 builder、无三套 CLI patch、无通用 parser/path framework、120/240 行预算现实；输出
  findings-first `PASS/FAIL` 与精确 target 身份。

### T23 Confucius 兼容/安全性评审

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；历史轮次仅保留在日志
- **依赖**：T21
- **验收**：确认 checkpoint/WI-198、path/Windows、unreadable optional、crash-convergence/idempotence、
  staged-pair fault、rollback、CLI/error contract 完整；输出 `PASS/FAIL` 与精确 target 身份。

### T24 findings 收敛至同一 hash 双 PASS

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；formal 文件不内嵌动态 verdict/hash
- **依赖**：T22、T23
- **验收**：逐条验证/处置；任一六文件变化使双方旧 verdict 失效；最终 Pascal/Confucius 对同一 combined
  均 PASS 且无 actionable finding。

### T25 formal gates、PR 与 merge

- **状态**：pending
- **依赖**：T24
- **验收**：constraints/validate/truth/manifest exact/diff-check/Cursor zero-diff；formal commit/PR、Codex、
  required checks、heartbeat、merge；implementation branch 只能基于 formal merge main。

## Batch 3：TDD implementation

### T31 写 relocation/loss RED

- **状态**：blocked by T25
- **依赖**：T25
- **文件**：四个 test allowlist 文件
- **验收**：至少一个 RED 暴露旧 absolute root，至少一个 RED 暴露 linked branch/context 丢失或 active
  files 未按 `STAGE_FILES` 构造；覆盖 matching/mismatched/no-linked handoff、linked Branch
  attached/detached/GitError/historical-feature/sentinel 与 branch-invalid-context-valid、handoff
  missing/OSError/invalid UTF-8/malformed/duplicate、runtime priority、docs baseline semantic mismatch、
  zero-option/partial summary wire grammar、root/scoped missing/corrupt/stale/mismatch、Windows/escape、staged-pair
  fault 与 convergence/no-op；handoff 第三态覆盖 fresh pack byte/no-event 与 invalid-pack rebuild，另有
  model-equal/raw-bytes-different pack 首次收敛/二次 no-op。

### T32 实现 portable path normalization

- **状态**：blocked by T31
- **依赖**：T31
- **文件**：`src/ai_sdlc/context/state.py`
- **验收**：filesystem/working-set paths 与 active files repo-relative、`/` 分隔；旧 root/drive/UNC/escape
  不泄漏；partial docs 和无 linked 行为保持。

### T33 实现 lossless canonical reconstruction

- **状态**：blocked by T32
- **依赖**：T32
- **文件**：仅 `src/ai_sdlc/context/state.py`；`core/handoff.py` 只回归，不修改
- **验收**：spec §3 优先级；old pack not donor；semantic compare 覆盖 stage/batch/task、branch、docs
  baseline、六个 path、active files 与 context；root/scoped crash-convergent；runtime branch 优先；handoff
  为所有 matching active WI 补 context、只以 eligible Branch 补 linked branch；active files 只来自
  working-set 或 `STAGE_FILES`，no-linked 始终取 checkpoint feature branch 并保留 matching handoff context；
  reader 三态保持 WI-198 semantic-only 边界，root/scoped 同时比较 model 与 raw bytes。

### T34 focused GREEN 与预算

- **状态**：blocked by T33
- **依赖**：T33
- **验收**：plan §8 focused 全绿；产品最多 1 文件/net +120，测试最多 4 文件/net +240；无 test
  deletion/weakening、无第二个产品文件。

## Batch 4：proof 与 final review

### T41 full/governance/differential/rollback

- **状态**：blocked by T34
- **依赖**：T34
- **验收**：full/Ruff/format/constraints/validate/truth/diff-check 全绿；批准差分只有 NC-05；byte-only
  首次 repair 只复用既有 event 文本/canonical serialization/rebuild timestamp，第二次 status/recover
  bytes/event no-op；revert/reapply tree exact；测试未污染外部 checkout。

### T42 final tree 双 Agent 复审

- **状态**：blocked by T41
- **依赖**：T41
- **验收**：冻结 HEAD/tree/binary/name-status/formal hash/LOC/test evidence；Pascal 与 Confucius 对同一
  target 双 PASS；任何后续 tree 变化使 verdict 作废。

## Batch 5：PR、fresh-main 与路线继续

### T51 implementation PR 交付

- **状态**：blocked by T42
- **依赖**：T42
- **验收**：push、ready PR、current-head Codex review、heartbeat；actionable finding 修复后重跑 T41/T42；
  required checks 全绿后 merge。

### T52 fresh-main 关闭 GAP-13

- **状态**：blocked by T51
- **依赖**：T51
- **验收**：fresh detached main 运行 relocation node、focused/full/Ruff/constraints/truth、root/scoped equal、
  second no-op、clean-state；只把 GAP-13/T56 标 closed。

### T53 启动 WI209

- **状态**：blocked by T52
- **依赖**：T52
- **验收**：WI209 单独处理 GAP-14 quoted-scalar comment-policy false positive；不提前启动新的
  T61/T62/T63～T67，不关闭 WI-196/RC-08，不发布版本。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| GAP-13 / T56 | T11～T53 |
| NC-01～NC-06 | T21～T42 |
| CC-03 / CC-06 / CC-07 | T21～T42 |
| FR-208-01～FR-208-08 | T13、T21、T31～T41 |
| FR-208-09～FR-208-12 | T21～T53 |
| SC-208-01～SC-208-09 | T31～T53 |
