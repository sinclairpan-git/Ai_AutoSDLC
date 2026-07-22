# 执行日志：消费项目与框架约束隔离

**工作项**：`218-consumer-framework-constraint-isolation`
**基线**：`1de1c3269a76e8ca885a940bd561f32cc7612534`

## 2026-07-21 Batch 001：问题复现与根因冻结

- Agent Store 是用户明确报告问题的普通消费项目；参赛仓库因用户主动要求复制规则，不计入本缺陷。
- 当前源码 `collect_constraint_blockers()` 无条件调用 framework release/docs/template/rule helpers。
- `build_constraint_report()` 与 `build_verification_gate_context()` 还会按内部 WI 编号加载附件、coverage 和
  context payload；仅过滤 blocker 不足以解决污染。
- 使用 current-main 纯函数对 Agent Store 稳定复现 17 条 framework-oriented blockers：
  release/version/offline 10、beginner guide 3、frontend instruction 1、rule/checklist parity 3。
- Agent Store `pyproject.toml` 为 `project.name=agent-store`，且不存在 `src/ai_sdlc/__init__.py`；
  Ai_AutoSDLC 为 `project.name=ai-sdlc` 且包入口存在。
- 根因结论：单一 collector/report 混合仓库所有权，并以通用文档、局部规则路径或内部数字编号推断完整框架身份。

## 2026-07-21 Batch 002：方案对抗评审

- 消费项目/兼容性专家与框架门禁/安全专家首轮均为 `ACCEPT_WITH_CHANGES`；交叉反驳后统一要求：
  顶层覆盖 collect/report/context、保留 consumer common gates、隔离内部编号、报告元数据与实际执行一致。
- 代码纯洁性专家与范围安全专家对极简双信号方案首轮均为 `PASS_WITH_CHANGES`；交叉反驳后统一接受：
  `project.name + src/ai_sdlc/__init__.py`，三入口机械分支，不引入 role config、VerificationPlan 或 registry。
- 两位专家共同冻结生产净增 `+55～+77`、硬上限 `+80`，最多两个私有 helper；超限即停止压缩。
- 已知残余风险：双信号同时被协调修改无法由启发式独立抵抗；用真实 framework checkout 身份测试防意外，
  不扩展为外部身份系统。

## 2026-07-21 Batch 003：独立 formal 工作树与基线

- 从 `origin/main@1de1c326` 创建隔离工作树
  `.worktrees/218-consumer-constraint-isolation`。
- docs branch：`feature/218-consumer-framework-constraint-isolation-docs`。
- `uv sync --frozen` 成功；baseline `uv run pytest -q tests/unit/test_verify_constraints.py` =
  `147 passed in 10.14s`。
- `uv run ai-sdlc workitem init` 创建 canonical 四件套、manifest mapping，并把 next sequence 推进到 219。
- init 自动刷新 `.cursor/rules/ai-sdlc.mdc`；该 diff 不属于本项，已恢复为 HEAD exact content，formal scope
  不包含 `.cursor/**`。
- 当前下一门：完成 formal source、program truth/handoff、提交 clean identity，并启动 PRD 双专家评审。

## 2026-07-21 Batch 004：Formal truth 与本地门禁

- checkpoint 已链接 WI218 canonical plan；root/scoped handoff 已生成且内容一致。
- `uv run ai-sdlc program truth sync --execute --yes`：snapshot `ready`，inventory `1141/1141`，
  missing/unmapped=`1/0`；唯一 missing 是尚未到 close 阶段的 WI218 `development-summary.md`。
- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc program truth audit`：`ready/fresh`。
- `uv run ai-sdlc verify constraints`：no BLOCKERs。
- formal 四件套已完成 placeholder、自相矛盾、范围蔓延和验收覆盖自检；T11 完成。
- 当前下一门：manifest exact、提交 clean formal identity、两位专家独立审查与交叉反驳。

## 2026-07-21 Batch 005：Manifest exact RED 与机械修正

- `tests/integration/test_repo_program_manifest.py` 首跑按预期 RED：旧 fixture 固定
  `1136/1136、missing=0、close=216/216`，实际 WI218 pre-close 为
  `1141/1141、missing=1、close=217/216`。
- 失败只来自新增 canonical 四件套和预期缺失的 `development-summary.md`；validation、mapping 和 capability
  closure 没有产品异常。
- formal scope 增加唯一机械例外：只更新该 integration test 的两个精确 tuple；不修改产品行为测试。
- 修正后必须重跑 manifest exact、constraints、program validate/truth 和 diff-check。
- 修正后 `uv run pytest -q tests/integration/test_repo_program_manifest.py`：`1 passed in 108.14s`；
  `git diff --check`：PASS。

## 2026-07-22 Batch 006：Formal 对抗评审 Round 1

- Review identity：HEAD=`465c342337e737bc0cfa53e09f81ca2cb58b87a4`，tree=
  `1b16cd40febd722d5ea45c5be697ed72a68e08d1`，worktree clean。
- formal-four hash算法：按 spec/plan/tasks/log 固定顺序生成
  `<lowercase file sha256><two spaces><repo-relative path>`，单个 LF 连接且末尾无 LF，再对 UTF-8 manifest
  文本做 SHA256；combined=`2b0115b3dfe51a75cfca5b0d23620449a96dbec2f07651ae3944cac36c8c1856`。
- LEAN=`findings=1`、SAFETY=`findings=3`；两者独立命中 P1：现有 consumer PrimeVue import-boundary
  report/context 未在 common 清单冻结，可能被错误关闭。
- SAFETY 另有 P2：invalid pyproject 语义未定义；真实 Agent Store 零写入验收缺少可重复指纹协议。
- 交叉反驳后双方统一：PrimeVue 与基础 governance/provenance 保持 common；invalid pyproject 不得崩溃，
  sentinel absent按consumer、present时报唯一 identity blocker；用 routing-census + `003/012` 两个非空代表
  fixture，避免为所有 common gate/WI 复制测试；Agent Store current-source 双跑并比较三类前后指纹。
- 双方确认上述修订不需要新抽象，产品仍可控制在≤80 raw additions。Round 1 verdict 因文档变化全部失效。
- 当前下一门：提交新的 clean formal identity并从零完成 LEAN/SAFETY Round 2。

## 2026-07-22 Batch 007：Formal 对抗评审 Round 2

- Review identity：HEAD=`78eb9957c79683f1eb15da8856933f451a5f4bb2`，tree=
  `494dbef27367ad00b66179d4b28029c58e1119e5`，formal-four=`a4e3975320d86de2434993a292ae0a27c5f7699054051222f1a4bf122055ac49`，
  worktree clean。
- LEAN=`PASS0/findings=0`；确认 PrimeVue common、invalid pyproject、Agent Store 协议仍在≤80行和单helper边界。
- SAFETY=`FAIL1`：T11 验收仍引用旧范围 FR/SC 001～008、LC-01～07，遗漏新增 009～010 和 LC-08。
- Finding成立；只把T11范围修正为 FR/SC 001～010、LC-01～08。tracked文档变化使Round2双方verdict全部失效。
- 当前下一门：重建truth与committed+clean identity，LEAN/SAFETY Round3从零复审。

## 2026-07-22 Batch 008：Formal 对抗评审 Round 3 PASS0

- Review identity：HEAD=`e7e2155e9205e0acba03125d1a878a2032ff6aec`，tree=
  `704e863f5fd01a5fe7474de76845b7732cc3d62c`，formal-four=
  `f133d5d991edb7471d6a4f5961dc42980dc9484cbfec89bfdd19ef73a600f171`，worktree clean。
- LEAN=`PASS0/findings=0`：范围与所有权闭合，单helper/三入口可在≤80 raw additions实现，测试没有膨胀。
- SAFETY=`PASS0/findings=0`：双信号、common/framework隔离、invalid语义、Agent Store零写入与回退合同完整。
- T12完成。写入本receipt会改变formal-four；下一步只允许对回执后的final identity进行同双 reviewer确认，
  不再改变产品设计。

## 2026-07-22 Batch 009：Codex source-inventory P1 与 lifecycle prerequisite

- PR #170 Codex 在 `e31cb7db` 指出：把仓库级 manifest regression 放宽为 `missing=1` 会重新打开 WI201
  已关闭的 source-inventory 缺口；LEAN/SAFETY 复核确认诊断成立。
- 直接预建 summary 会触发既有 ProgramService false-close：summary 存在即 `stage_hint=close`，execute gate
  会把未完成 WI 当作 closed。因此先交付独立 lifecycle prerequisite PR #171。
- PR #171 final HEAD=`517ead3f`，LEAN/SAFETY同identity PASS0，Codex未发现major issue，22/22 checks
  全绿；squash merge=`fb75a9d6`。detached fresh-main focused=4、ProgramService=416、CLI=233、Ruff与
  constraints均PASS，产品/测试blob与reviewed HEAD一致。
- Formal 分支合入该 prerequisite 后新增诚实 `stage: close-pending` summary；只声明 formal candidate，
  T13/T21～T33保持pending。manifest exact恢复为`missing=0`、close=`217/217`，不建立active-WI waiver。
- 本次更改使旧formal-four hash及旧LEAN/SAFETY verdict失效；truth、门禁与双评审必须在新committed+clean
  identity从零重建。
