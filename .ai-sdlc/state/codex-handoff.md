# Continuity Handoff

- Updated: 2026-07-21T12:29:27Z
- Reason: WI217 truth/gates 已完成并修正 Formal Round 6 handoff 时态
- Goal: 先冻结 WI217 artifact-loader exact-family 合同并完成 formal merge/fresh-main；随后在独立
  implementation 分支以 T61A/B 实现 product net delete≥358 且零功能差异
- State: branch=`feature/217-programservice-artifact-loader-dedupe-docs`，base=
  `b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`；formal source已提交，等待当前committed+clean identity
  的LEAN/SAFETY双PASS0，implementation blocked
- Stage: plan
- Work Item: 217-programservice-artifact-loader-dedupe

## Changed Files

- WI217 pre-close canonical spec/plan/tasks/log；summary只注册且保持不存在；WI196 five docs最小更新
- `program-manifest.yaml`、project-state、manifest exact 两个机械标量
- root/scoped `codex-handoff.md`（必须 byte-identical）
- Formal scope 禁止 `src/**`、产品测试逻辑、workflow、依赖、版本和 release

## Key Decisions

- 选择13-loader T63 exact family，不重启 WI213/WI215 T66。Clean evidence：legacy403/branch39，
  product `+48/-406`、proof `+48`、terminal44/4、RC-06含truth≤2为98/101。
- 唯一方案：一个private helper +12 direct exact label bindings + cleanup-only wrapper；产品/runtime禁止
  新模块、registry/reflection/DSL/getattr/type erasure、第二family和全文件formatter；T61A test-only
  inspection除外。
- Pascal/LEAN与Confucius/SAFETY Round 4均对同一clean spike
  `APPROVE A/findings=0`；污染首棵spike已排除。
- Formal与implementation独立PR；formal detached fresh-main通过前不得创建implementation branch。
- Pre-close truth只允许WI217 `development-summary.md`一个mapped/`exists=false`：inventory
  `complete 1136/1136`、missing/unmapped=`1/0`、close=`216/215`；closure才创建summary并恢复`216/216`。
- 即使implementation成功，也只关闭该T63 family；GAP-03/T66、GAP-05、WI196、RC-08、release保持open。
- Legacy 5 behavior GREEN/1 binding RED只绑定独立proof-red worktree；atomic revert只验baseline exact
  blobs与406 unit，reapply再验candidate exact blobs、6 proof与412 unit。

## Commands / Tests

- Fresh-main baseline：`tests/unit/test_program_service.py` = `406 passed in 35.83s`。
- Clean spike strengthened proof：legacy=`1 binding failed, 5 behavior passed, 406 deselected`；candidate=
  `6 passed, 406 deselected`；full ProgramService=`412 passed in 34.28s`；Ruff/diff-check PASS；proof仍+48，
  current clean spike product/test仍`+96/-406`。
- Formal init使用仓库source CLI；其非范围Cursor adapter refresh已恢复为HEAD exact。
- Formal R3 identity=`3510fce9/2342bd22/formal-six 1db59fc2...5c39`；LEAN/SAFETY各FAIL1同源，
  rollback/proof-red证据解耦修正文档diff-check PASS。
- Formal R4 identity=`dd2287fd/a53f310b/formal-six 856e7819...a669`；LEAN=`FAIL1`指出handoff仍要求
  重复提交，SAFETY=`PASS0`；该identity两项verdict均因本修正失效。
- Formal source R5在`114a5f73/61da9d78/formal-six 856e7819...a669`取得LEAN/SAFETY同身份PASS0。
- Truth sync commit=`0c1352a7`；manifest exact=`1 passed in 115.06s`，constraints无BLOCKER，validate PASS，
  truth audit=`ready/fresh`、mapped=`1136/1136`、missing/unmapped=`1/0`、close total/materialized=`216/215`，scope/Cursor/
  handoff parity/diff-check/clean均PASS。
- Formal R6 identity=`0c1352a7/758de9ff/formal-six 856e7819...a669`；LEAN/SAFETY均`FAIL1`且只指出
  handoff仍要求重复truth sync；本次只修正未纳入truth authoring hash的两份handoff。

## Blockers / Risks

- Formal truth已ready/fresh，唯一missing为WI217 summary；后续不得改已映射authoring source使其stale。
- RC-06 buffer只有3行；implementation不得增加“顺手”测试、truth或formatter churn。
- 两位reviewer必须审同一committed+clean HEAD/tree/formal-six；任一tracked变化使双方verdict失效。
- Remote Codex review仍可能受usage-limit影响；用户已授权本地SDLC双审替代，但required CI不可waive。

## Exact Next Steps

1. 对当前committed+clean HEAD/tree/formal-six取得LEAN/SAFETY同一身份PASS0。
2. 双PASS0后推送formal branch并创建PR；current-head review无actionable finding且required checks全绿后merge。
3. 完成detached fresh-main acceptance，不删除本地formal branch。
4. 只有第3步完成，才从新的fresh-main创建独立implementation worktree并执行T61A RED→GREEN。
