# Continuity Handoff

- Updated: 2026-07-21T13:16:58Z
- Reason: 用户以时间、收益可见性、Token/评审/CI 成本和特性开发机会成本为依据，冻结本轮减重路线终止边界
- Goal: 完成 WI217 formal；至多执行一个 implementation PR；随后用一个 closure PR 在 GO 或 NO-GO 下均关闭 WI217/WI196、退役 RC-08，并恢复正常特性开发
- State: branch=`feature/217-programservice-artifact-loader-dedupe-docs`，base=`b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`；PR #167 已推送旧 HEAD `1a24ace02fa448c152e11e082ba2a835c99d423b`，其评审与 CI 因终止合同变更失效；终止 source R3 已双 PASS0，truth snapshot 与正式门禁已完成，等待最终 current identity 双审，implementation blocked
- Stage: plan
- Work Item: 217-programservice-artifact-loader-dedupe

## Changed Files

- WI217 canonical `spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`
- WI196 canonical `spec.md` / `plan.md` / `tasks.md` / `development-summary.md` / `task-execution-log.md`
- `program-manifest.yaml` 与 program truth 机械 snapshot 已在 source 双审通过后重新同步
- root/scoped `codex-handoff.md` 必须 byte-identical
- Formal scope 禁止 `src/**`、产品测试逻辑、workflow、依赖、版本和 release

## Key Decisions

- WI217 是本轮减重专项最后一个 work item；当前 formal 后至多一个 implementation PR 和一个 closure PR，不得创建新的减重 work item。
- 现有已合并 product raw net delete 为 `653` 行；相对 `src/ai_sdlc` 初始基线 `107482` 行约 `0.61%`。若 WI217 GO 再净减 `358` 行，累计约 `1011` 行或 `0.94%`，远低于 RC-08 的 `10%` 组合终态。
- RC-08 退役为 `retired_unrealistic_composite_target`，不得表述为实现、豁免或质量门禁通过；剩余 GAP-01、GAP-03 至 GAP-06 及 T62 至 T67 结构债转为非阻塞 backlog。
- GO：唯一 implementation PR 完成当前 T63 exact family 后进入 closure；NO-GO：本地门禁不通过则不创建 implementation PR，或已创建 PR 后关闭且零产品合入，再进入 closure。
- Closure PR 无论 GO/NO-GO 都关闭 WI217/WI196、恢复正常特性开发；closure 不自动授权 release，发布仍走独立正常流程。
- Closure 正常路径 records-only；若 implementation 已合并后 detached fresh-main 失败，同一 closure PR 精确恢复 pre-implementation product/proof blobs并登记最终零产品净变化，不增加 rollback PR。
- 候选技术合同不扩张：13-loader T63 exact family、一个 private helper、12 个 direct exact label bindings、cleanup-only wrapper；禁止新模块、registry/reflection/DSL/getattr/type erasure、第二 family 和全文件 formatter。
- Pre-close truth 允许 WI217 `development-summary.md` 一个 mapped/`exists=false`；closure 才创建 summary 并恢复 materialization。

## Commands / Tests

- Fresh-main baseline：`tests/unit/test_program_service.py` = `406 passed in 35.83s`。
- Clean spike：legacy=`1 binding failed, 5 behavior passed, 406 deselected`；candidate=`6 passed, 406 deselected`；full ProgramService=`412 passed in 34.28s`；product `+48/-406`，proof `+48`，terminal `44/4`，RC-06=`98/101`。
- 旧 formal R7 identity=`1a24ace0/b111d6f5/formal-six 856e7819...a669` 曾取得 LEAN/SAFETY PASS0；该结论与其 PR #167 CI 均因本次终止合同变更失效，不得复用。
- 终止 source 首提交=`022344ed/abfbfdfd/formal-six c144c69d...70c1`；R2 LEAN FAIL1、SAFETY FAIL3均已按最小范围修正，旧 R2 identity 失效。
- Source R3 identity=`26d11c44/0b3e9034/formal-six 40c6d928...06a4`；LEAN/SAFETY均 PASS0/findings=0。
- Truth sync commit=`df9fae3d`；manifest exact=`1 passed in 114.15s`，constraints无BLOCKER，validate PASS，truth audit=`ready/fresh`、mapped=`1136/1136`、missing/unmapped=`1/0`、close=`216/215`。
- Formal scope=`14/14 allowed`、unexpected=`0`、`src/**=0`、Cursor diff=`0`；测试仅两个既有manifest exact计数替换；handoff parity、diff-check、clean均PASS。

## Blockers / Risks

- 当前 program truth 已 ready/fresh，唯一 missing 是合同要求 closure 前不得创建的 WI217 summary。
- 新 HEAD/tree/formal-six 必须取得 LEAN/SAFETY 同一身份 PASS0；任一 tracked 变化使 verdict 失效。
- Remote Codex review 可能受服务状态影响；用户允许本地 SDLC 双审替代，但 required CI 不可 waive。
- 不得因评审意见创建第二个 implementation PR、额外 closure PR 或新的减重 work item；可操作修复必须收敛在允许的现有 PR 内。

## Exact Next Steps

1. 对当前 committed+clean HEAD/tree/formal-six与truth receipt取得 LEAN/SAFETY 最终同一身份 PASS0；finding只在本分支最小修复后重审。
2. 双审通过后推送并更新 PR #167，只接受新 HEAD 的 review 与 required checks；全绿后合并并 detached fresh-main 验收。
3. 至多一次 implementation 尝试；随后一个 closure PR 无条件关闭 WI217/WI196、退役 RC-08、把剩余债务转 backlog并恢复特性开发；post-merge NO-GO由该closure同时回退。
