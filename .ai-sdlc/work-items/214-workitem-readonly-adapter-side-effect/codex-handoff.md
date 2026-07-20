# Continuity Handoff

- Updated: 2026-07-20T03:45:40Z
- Reason: 最终本地审查修正的 terminal gates 已完成；固化 receipt 后直接进入新身份双审
- Goal: 关闭 GAP-15/T58，并以可执行的格式门禁保持一行产品修复零回归
- State: T21-T31 completed；两项测试证据修正与 terminal gates 全绿，等待新身份双审
- Stage: decompose
- Work Item: 214-workitem-readonly-adapter-side-effect
- Branch: feature/214-workitem-readonly-adapter-side-effect-dev
- Base: origin/main@8999efcf2feccab88f8b957601b0be379032a1b7

## Changed Files

- .ai-sdlc/state/codex-handoff.md
- .ai-sdlc/work-items/214-workitem-readonly-adapter-side-effect/codex-handoff.md
- program-manifest.yaml
- src/ai_sdlc/cli/workitem_cmd.py
- specs/214-workitem-readonly-adapter-side-effect/development-summary.md
- specs/214-workitem-readonly-adapter-side-effect/task-execution-log.md
- specs/214-workitem-readonly-adapter-side-effect/tasks.md
- tests/integration/test_cli_workitem_adapter_dispatch.py
- tests/integration/test_cli_workitem_init.py
- tests/integration/test_cli_workitem_link.py
- tests/unit/test_cli_hooks.py

## Key Decisions

- Formal PR #160 与 V4 amendment PR #161 已 merge/fresh-main；implementation 唯一固定格式基线为
  `FORMAT_BASE_SHA=8999efcf2feccab88f8b957601b0be379032a1b7`。
- 产品只改 `_workitem_before_command()` 一处谓词：非 `link` 直接 return；`init` 继续由 handler 消费 hook。
- 测试保持一个参数化 dispatch 文件、既有 init/link integration 与 hook unit，不新增 DSL/公共 fixture/产品抽象。
- V4a 对三个可清洁测试文件 strict；V4b 对 base/candidate red-path Ordinal subset 与两个 legacy changed ranges
  fail closed，禁止格式化 273 个历史 debt 文件。
- Implementation fresh-main 前只声明代码候选通过；GAP-15/T58 仍 active、T66 T61A 仍 blocked。

## Commands / Tests

- Amendment final `e4ca3e42`/tree `1bef978f` 双 PASS0；PR #161 Codex/checks 全绿；merge/frozen base=
  `8999efcf`，detached fresh-main truth/manifest/V4b/constraints/clean 全绿。
- Test-only commit=`8f4f63dd`；detached RED=`16 failed, 33 passed in 16.27s`，失败范围与合同一致。
- Product commit=`bd8a0de2`；targeted GREEN=`49 passed in 15.14s`；full=`3302 passed, 3 skipped in 673.22s`。
- Ruff lint/V4a PASS；V4b 13 emitted ranges PASS；constraints no BLOCKERs；diff-check PASS。
- Terminal source=`581cf344`；首个 truth snapshot=`034f3464...d732`、inventory=`1126/1126`、manifest-only
  commit=`e68ae027`；final manifest refresh 后不再反写 tracked source。
- Cursor protected rule SHA 保持 `d5f04acf...0b6a`；final identity 只有全部 T31 gates 通过才可送审。
- Final gates on `7b33ec67`：targeted=`49 passed in 16.43s`、full=`3302 passed, 3 skipped in 682.71s`、
  truth ready/fresh、manifest exact=`1 passed in 102.45s`、Ruff/V4/constraints/scope/clean 全绿。
- PR #162 Codex reviewed exact `8d09b7bba8` 无 major issue；首轮 Compatibility Gate 的 Ubuntu/macOS
  pytest 均因 real-hook A/B 比较不同绝对临时路径而失败，旧 Codex/双审 identity 随测试修正退役。
- 本地以 `COLUMNS=200` 精确复现 RED；当前使用等长 `control/subject` 两个 byte-identical 隔离 repo，只
  归一化绝对根路径后比较完整 stdout/stderr，保留 Rich 列宽与其余输出差异。
- 修正后 terminal identity=`33a37b53`/tree=`90e5e950`：宽终端 targeted=`49 passed in 15.82s`、full=
  `3302 passed, 3 skipped in 674.46s`；Ruff/V4a/V4b、constraints、validate、truth ready/fresh 1126/1126、
  manifest exact=`1 passed in 102.03s`、scope/parity/Cursor/clean 全绿。
- 双项目 correction identity=`36f49b62`/tree=`04ae4bea`：80/200/300 列单测 PASS、宽终端 targeted=
  `49 passed in 16.47s`、full=`3302 passed, 3 skipped in 683.70s`；Ruff/V4a/V4b、constraints、validate、
  truth ready/fresh 1126/1126、manifest exact=`1 passed in 110.91s`、scope/parity/Cursor/clean 全绿。
- 最终本地审查 exact `98b7c6f2`：Pascal/LEAN=`PASS0`，Confucius/SAFETY=`FAIL2`；真实 no-project
  自动化与 config-lock warning byte-exact 两项 finding 均成立，旧 verdict 全部退役。
- 两项最小测试修正的 mutation 均预期 RED；恢复产品源码后两项=`2 passed`、宽终端 targeted=`50 passed`
  且 80/200/300 列 real-hook A/B、Ruff/diff-check 全绿。被中止的 full 不是验收，final identity 必须重跑。
- 修正 terminal identity=`56367d96`/tree=`64305f84`：targeted=`50 passed`、full=`3303 passed, 3 skipped`
  且 Ruff/V4a/V4b、constraints、validate、truth ready/fresh 1126/1126、manifest exact、scope/parity/Cursor/
  clean 全绿；本 continuity-only source 后再次重验，成功后不再反写 tracked source。

## Blockers / Risks

- 新 identity 双 PASS0、PR #162 22/22 checks、merge/detached fresh-main 前不得开始 lifecycle。
- 用户批准 PR #162 一次性治理例外：OpenAI 官方事故期间，本地 LEAN+SAFETY 同身份 PASS0 取代 current-head
  GitHub Codex 回执；例外不自动扩展到 lifecycle 或发布阶段。
- handoff CLI 依据旧 WI208 checkpoint 写错 scoped copy；已用 apply_patch 恢复 WI208/resume-pack，并直接维护
  当前 WI214 root/scoped byte-identical，禁止把错误路由变化带入 implementation。

## Local PR Review

- Pascal/LEAN implementation pre-review：FAIL2，产品最小性 PASS；两项断言精度 finding 已在暂停的 dev worktree 修正。
- Confucius/SAFETY implementation pre-review：FAIL4，产品范围 PASS；三组测试证据已修正，V4 矛盾由本 amendment 处理。
- Amendment Round 4 final：同一 `e4ca3e42` identity 双 PASS0；仅作为 amendment receipt，不替代 implementation review。
- Implementation Round 1：Pascal FAIL1（仅 continuity P3）、Confucius PASS0；identity 变化使两份 verdict 均退役。
- Implementation Round 2：同一 `8d09b7bb` identity Pascal/Confucius 均 PASS0；PR #162 CI 促成测试修正后
  两份 verdict 与 Codex current-head review 全部退役，必须从零重审。
- Post-CI Round 4：Pascal continuity FAIL 已修正；Confucius SAFETY 对 `551d90b9` 报告同 repo A/B 偏离
  plan 的“两份 byte-identical 临时项目”P3。Finding 成立，旧 review 均退役。
- Final local review：Pascal 对 `98b7c6f2` PASS0；Confucius FAIL2 的 no-project 自动化与 warning byte-exact
  finding 已仅以测试修正，产品源码保持不变；必须对新 committed+clean identity 从零双审。

## Exact Next Steps

- 让 Pascal/LEAN 与 Confucius/SAFETY 对新 committed+clean identity 从零审到 PASS0。
- 双 PASS0 且 PR #162 22/22 checks 全绿后，按用户批准的一次性例外直接 merge并 detached fresh-main。
- Implementation fresh-main 通过后创建独立 lifecycle reconciliation；不得提前关闭 GAP-15/T58 或放行 T66。
