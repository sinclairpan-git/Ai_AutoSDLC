# Continuity Handoff

- Updated: 2026-07-21T12:07:32Z
- Reason: WI217 Formal Round 3 同源 finding 已完成最小修正
- Goal: 先冻结 WI217 artifact-loader exact-family 合同并完成 formal merge/fresh-main；随后在独立
  implementation 分支以 T61A/B 实现 product net delete≥358 且零功能差异
- State: branch=`feature/217-programservice-artifact-loader-dedupe-docs`，base=
  `b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`；等待提交新identity并执行formal Round 4双审，
  implementation blocked
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

## Blockers / Risks

- 当前formal truth snapshot尚未基于最终source commit机械同步；目标是ready/fresh且只有上述summary missing。
- RC-06 buffer只有3行；implementation不得增加“顺手”测试、truth或formatter churn。
- 两位reviewer必须审同一committed+clean HEAD/tree/formal-six；任一tracked变化使双方verdict失效。
- Remote Codex review仍可能受usage-limit影响；用户已授权本地SDLC双审替代，但required CI不可waive。

## Exact Next Steps

1. 提交当前formal修正，计算HEAD/tree/formal-six并取得LEAN/SAFETY Round 4同一身份PASS0。
2. 基于通过双审的source identity执行truth sync与formal gates；tracked变化后重新双审。
3. Formal PR required checks全绿后merge并完成detached fresh-main acceptance。
4. 只有第3步完成，才从新的fresh-main创建独立implementation worktree并执行T61A RED→GREEN。
