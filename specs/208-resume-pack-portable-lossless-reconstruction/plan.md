# 实施计划：Resume-pack 可迁移、无损的 canonical reconstruction

**编号**：`208-resume-pack-portable-lossless-reconstruction`
**规格**：`specs/208-resume-pack-portable-lossless-reconstruction/spec.md`
**父项**：WI-196 `GAP-13 / T56`

## 1. 目标

用一次字段级 source 收敛修复 `status/recover/handoff` 的共同 resume builder：checkpoint 继续是 active WI、
fingerprint、docs baseline 与 execute fallback 的权威锚点，active-WI runtime 保持 stage/batch/task 优先；
matching handoff 为所有 active WI 补 context、只以 eligible Branch 补 linked branch，其他 active-WI optional
artifacts 只补各自负责的字段；所有 repo 内部路径统一 portable，不在三个 CLI handler 写分支，不从旧 pack
迁移字段。

## 2. 现状调用链与根因

```text
status / recover ───────────────┐
handoff update -> refresh pack ├─ load_resume_pack
build/save direct tests ────────┘        │
                                         ├─ root/scoped freshness + equality
                                         └─ _build_resume_pack_from_checkpoint
                                              ├─ runtime/latest-summary/working-set
                                              └─ filesystem fallback  <-- absolute path + sparse fields
```

`state.py` 已有 active linked WI、runtime/working-set overlay、fingerprint、semantic stale 和 staged pair write；
本项复用这些机制。唯一需要补齐的是 portable fallback、matching handoff 的窄字段 fallback，以及 semantic
comparison 对新增 canonical fields 的覆盖。

## 3. 影响边界

### 产品文件 allowlist

```text
src/ai_sdlc/context/state.py
src/ai_sdlc/core/handoff.py        # regression-only，不修改
```

禁止改 `cli/commands.py`、`cli/handoff_cmd.py`、models/schema、adapter、Program Truth 与 comment policy。

### 测试文件 allowlist

```text
tests/unit/test_context_state.py
tests/integration/test_cli_status.py
tests/integration/test_cli_recover.py
tests/integration/test_cli_handoff.py
```

既有 `tests/unit/test_handoff.py`、`tests/flow/test_recover_flow.py` 只回归，不新增逻辑。

## 4. 宪章与父合同检查

| 门禁 | 响应 |
|---|---|
| checkpoint 权威锚点 | active WI/fingerprint/docs baseline/execute fallback 由 checkpoint 锚定；字段按 spec §3 优先级派生，旧 pack 不 overlay |
| NC-01～NC-06 | 单 builder、TDD、最小 allowlist、focused/full、独立 revert |
| CC-03 schema/serialization | schema/字段/错误文本不变；仅批准字段值规范化/补齐 |
| CC-06 幂等/恢复 | missing/corrupt/stale/mismatch 一次收敛，第二次无写入 |
| CC-07 跨平台 | POSIX relocation + Windows drive/UNC/backslash fixture |
| WI-198 impact | runtime 仍最高；handoff context 对所有 active WI 可用，eligible Branch 只补 linked；no-linked branch 不变 |
| WI-207/WI-209 分流 | 不触及 adapter/comment parser；GAP-12 closed、GAP-14 queued |

## 5. Phase 0：formal freeze

1. 记录 WI-207 repair PR #141 merge `8d8b8f96` 与 fresh-main `3224 passed, 3 skipped`、clean-state
   acceptance，关闭 GAP-12/T55。
2. 初始化 WI208 canonical docs，恢复 `workitem init` 产生的非目标 Cursor refresh。
3. 冻结 spec §3 source matrix、§4 migration/mismatch matrix、allowlist、预算、RED/GREEN 与回退合同。
4. 完成后同步 WI-196 和 WI-207 状态；fresh-main 后 GAP-13/T56=closed、GAP-14/T57=queued。
5. 对 child + parent 六份 formal 计算父计划 §9 canonical combined hash；Pascal/Confucius 从零评审。
6. 任一 finding 先验证再修订；六文件一变，双方旧 verdict 同时失效，直到同一 hash 双 PASS。
7. 运行 constraints、program validate/truth、manifest exact、diff-check；提交 formal PR，Codex/checks 全绿后合并。

## 6. Phase 1：TDD RED

### 6.1 Unit matrix

在 `test_context_state.py` 建立单一 fixture builder，覆盖：

- 当前 root 与 relocated root 不同；filesystem fallback 当前绝对路径在 RED 中可见；
- matching root/scoped handoff 含 Work Item、Branch、Goal/State/Next；无 runtime/working-set；
- handoff Branch 的 attached、detached `HEAD`、GitError 历史 fallback、`none`、active linked 与 checkpoint
  feature id 相同/不同；Branch 不合格但 context 合法；
- handoff zero-option 与 Goal/State/Next 部分为空，`none` sentinel、精确 summary 拼接/默认文本；
- persisted working-set/current-root absolute、other-root absolute、Windows drive/UNC、backslash relative、`..`；
- runtime branch 优先、no-linked matching/mismatch、handoff missing/OSError/invalid UTF-8/malformed/duplicate、
  partial docs、optional artifact unreadable；
- handoff OSError/invalid UTF-8/malformed/duplicate/root-scoped mismatch 分别验证 fresh semantic-only 时原 pack
  bytes/no event，以及 pack 本已 invalid 时忽略 handoff 并从其他 canonical sources rebuild；
- root/scoped missing/corrupt/stale/model mismatch、model-equal/raw-bytes-different 与
  semantic-fresh-but-wrong path/context/docs baseline；
- scoped replace 成功、root replace 失败的 fault injection：原异常、staged cleanup、next-load convergence、
  third-load no-op。

RED 断言只锁定 spec 需求：portable paths、canonical field values、root/scoped equality、old pack not donor。

### 6.2 CLI matrix

- `status`：real Git fixture attached 写 continuity，detached/relocated 后删 scoped pack；首次 repair、第二次 no-op。
- `recover`：corrupt/stale/mismatch 走既有 event text，stage/batch/task/docs baseline 不漂移。
- `handoff`：update 后 pack 与 handoff summary 一致；linked 只接受 eligible branch，active files 使用
  working-set 或 stage-required docs，runtime branch 仍优先。no-linked update 后删/损坏 pack 再重建仍保留
  feature branch/context，zero-option/partial summary 精确且 second load no-op。

至少一个失败必须明确显示旧 absolute root，至少一个显示 linked branch/context 丢失或 active files 未按
`STAGE_FILES` 构造；fixture error 不算 RED。

## 7. Phase 2：最小 GREEN

只在共同 builder 附近完成：

1. 增加一个 private repo-path normalizer：识别当前-root absolute、POSIX relative、Windows drive/UNC 与
   escape；输出 portable string 或 fail-closed 空值。
2. filesystem fallback 全部经 normalizer 写 relative；working-set 的六个 path/active files 只 overlay
   合法 portable 值，非法值保留 filesystem/stage-required fallback。
3. 增加一个 private handoff fallback reader：接受 active WI 匹配的 canonical handoff，按 spec §3 sentinel/
   summary wire grammar 提供 context；调用方仅在 linked WI 下消费通过资格检查的 Branch。reader 返回
   available/clean absent-or-not-applicable/unreadable-or-invalid 三态；scoped 存在时必须字节一致；只解析
   固定字段/章节，不实现通用 Markdown parser。
4. 按 spec §3 合并 runtime、working-set、latest-summary、handoff、filesystem；不读取 pack。
5. semantic compare 扩展到 spec §4 fields（含 docs baseline）；fresh semantic probe 遇 handoff 第三态时
   保留原 pack，pack 本已 invalid 时忽略该 source 并复用同一个 expected pack 重建。root/scoped 同时比较
   model 与 raw bytes；invalid 时继续既有 crash-convergent staged pair write。
6. 不修改 `handoff.py`；现有 handoff update 已先写 canonical/scoped，再调用共同 refresh。

若需要第二个产品文件、public helper 或超过 120 行净新增，停止并重新做设计/双审。

## 8. Phase 3：验证与回退

### Focused

```powershell
uv run pytest tests/unit/test_context_state.py tests/unit/test_handoff.py tests/flow/test_recover_flow.py tests/integration/test_cli_status.py tests/integration/test_cli_recover.py tests/integration/test_cli_handoff.py -q
uv run ruff check src/ai_sdlc/context/state.py src/ai_sdlc/core/handoff.py tests/unit/test_context_state.py tests/integration/test_cli_status.py tests/integration/test_cli_recover.py tests/integration/test_cli_handoff.py
uv run ruff format --check src/ai_sdlc/context/state.py src/ai_sdlc/core/handoff.py tests/unit/test_context_state.py tests/integration/test_cli_status.py tests/integration/test_cli_recover.py tests/integration/test_cli_handoff.py
```

### Full/governance

```powershell
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
git diff --check
```

format 采用 baseline-differential gate：若 exact base 的同一命令为绿，candidate 必须为绿；若 base 已有
继承失败，必须冻结 base/candidate 排序后的待格式化文件集合并证明完全相同。另对本次 changed allowlist
分别复制 exact base/candidate、使用同一 Ruff 版本格式化后计算 normalized numstat；raw 与 normalized
product/test net 都必须满足 `120/240`，不得用压缩长行规避预算。

每组命令前后比较 tracked status/index/content、canonical adapter、project config、root/scoped pack 与
checkpoint；允许 pack 首次批准修复，第二次必须完全相同，不执行自动 restore。Phase 3、PR 与 fresh-main
期间任何 Cursor 非目标变化都直接 FAIL；只有 Phase 0 初始化/bootstrap 的已记录 refresh 可在 formal
baseline 冻结前用 `apply_patch` 恢复，不能计入门禁 PASS。

### Differential / rollback

- before/after 逐字段及 raw bytes 对比；approved delta 仅为 spec NC-05。byte-only mismatch 首次只允许
  canonical serialization、既有 stale/rebuilt event 序列与 rebuild timestamp 变化；其余模型字段、
  checkpoint、CLI/event 文本不变，第二次 load 无写入/无 event。
- 实现 commit detached revert 后 tree 必须等于 formal main；reapply 后等于 candidate。
- rollback 后旧缺陷可复现但 WI-207/WI-209 和 schema 不变。

## 9. Phase 4：复审、PR 与 fresh-main

1. 冻结 HEAD/tree、binary diff、name-status、formal combined、raw/normalized LOC budget、focused/full evidence。
2. Pascal 从精简/直接性复审；Confucius 从兼容/安全性复审；任一变更使双方 verdict 作废。
3. 双 PASS 后 push implementation branch、创建 ready PR、请求 current-head Codex review并约五分钟 heartbeat。
4. actionable finding focused 修复后重新跑门禁和双审；required checks 全绿才 merge。
5. fresh detached `origin/main` 重跑 relocation node、focused/full/Ruff/constraints/truth 与第二次 no-op/clean
   check；通过后只关闭 GAP-13/T56并启动 WI209，不发布版本。

## 10. 实施顺序与回退点

```text
formal 双 PASS/merge
  -> RED commit/receipt
  -> minimal GREEN
  -> focused/full/differential/revert
  -> final-tree 双 PASS
  -> PR/Codex/checks/merge
  -> fresh-main
  -> GAP-13 close / WI-209 formal
```

每一箭头前一个阶段未满足即停止；不以 waiver、旧 pack donor 或扩大 allowlist继续。
