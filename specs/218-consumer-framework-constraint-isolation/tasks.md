# 任务分解：消费项目与框架约束隔离

**编号**：`218-consumer-framework-constraint-isolation`
**来源**：`spec.md` + `plan.md`

## Batch 1：Formal PRD

- [x] **T11 冻结产品需求与精简合同**
  - 文件：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
  - 验收：FR-218-001～010、SC-218-001～010、LC-01～08 均有唯一可执行定义；无 TODO/TBD/placeholder。

- [x] **T12 完成双专家对抗评审**
  - 依赖：T11
  - 验收：LEAN 与 SAFETY 独立审查同一 committed+clean identity；交叉反驳后均为 PASS0/findings=0。

- [x] **T13 归档 formal PRD**
  - 依赖：T12
  - 验收：formal-only 本地门禁、Codex review、required checks、merge 和 detached fresh-main 全绿；
    formal diff 不包含 WI218 的 `src/**` 或产品行为测试；`development-summary.md` 精确标记
    `stage: close-pending`，inventory=`1141/1141/0/0`、close=`217/217`，status/execute gate 不得推进 close。
  - 实际证据：formal PR #170 以 `bf4f4cf8` 合并；lifecycle prerequisite PR #171 以 `fb75a9d6` 合并，
    formal 与 lifecycle 的 current-head review、required checks 和 detached fresh-main 验收均通过。

## Batch 2：TDD 实现

- [x] **T21 写入 consumer/framework 隔离 RED 测试并校正既有 framework fixture 身份**
  - 依赖：T13
  - 文件：`tests/unit/test_verify_constraints.py`、`tests/unit/test_runner_confirm.py`、
    `tests/unit/test_run_cmd.py`、`tests/integration/test_cli_run.py`；另保留
    `tests/integration/test_cli_verify_constraints.py`、`tests/integration/test_cli_index_gate.py` 两个精确
    framework identity fixture setup 例外
  - 验收：Agent Store、routing-census、`003/012` metadata/编号碰撞在 legacy implementation baseline 上
    按预期 RED；四态身份、invalid pyproject 二态、PrimeVue/common-gate characterization 不产生无关失败。
    verify constraints 新行为断言只在 `test_verify_constraints.py`；`014` runner/summary 断言只在 LC-02
    精确允许的三个对应测试；两个 identity integration 例外文件仅为明确验证 framework-only
    `003/012/018/073` 或 backlog/profile/doc-first surfaces 的逐个 fixture 创建 `pyproject.toml`
    （`[project].name = "ai-sdlc"`）和 `src/ai_sdlc/__init__.py`，不改断言/预期输出、不用
    module/global autouse；downstream/relinked `003` 与 consumer `003/012` collision fixture 保持无身份信号。
    consumer `014` 必须对 canonical context、`SDLCRunner`、`run` CLI summary 写 negative assertions；
    framework positive fixtures 必须带双身份信号并证明既有 `014` attachment/warning 保留。
  - 实际证据：consumer/framework、routing-census、`003/012` 碰撞、PrimeVue 与 `014` 下游测试均按冻结合同
    完成 RED/GREEN；implementation branch focused=`233 passed`。

- [x] **T22 实现最小双信号与三入口分流**
  - 依赖：T21
  - 文件：`src/ai_sdlc/core/verify_constraints.py`（scope/canonical context，并回收行数）、
    `src/ai_sdlc/core/runner.py`（只删除重复注入）、`src/ai_sdlc/cli/run_cmd.py`（只复用同一
    `_repository_scope` 做 summary guard）
  - 验收：T21 全部 GREEN；三个产品文件合计 raw additions ≤80、helper 目标1且≤2、无新模块/配置/公开抽象；
    `ProgramService` 通用路径不改。
  - 实际证据：三个产品文件合计 `+80/-31`、净增 `+49`，私有 helper=`1`；runner 删除重复注入，
    PrimeVue 空扫描与 consumer `014` 下游呈现两个 P2 已最小修复，`ProgramService` 未修改。

## Batch 3：验收与交付

- [x] **T31 完成本地完整验收**
  - 依赖：T22
  - 验收：focused pytest、Ruff、full pytest、constraints、program validate/truth、diff-check 全绿；
    真实 Agent Store 以 current-source、`python -B` 连续双跑，framework-only findings 为0，且前后
    status/diff/dirty-path 三类指纹完全一致。
    full pytest 必须确认 33 个既有 framework fixture 不再因缺少身份信号失败；yaml-store permission 用例
    即使 isolated rerun 通过也不豁免，仍由 full-suite gate 约束。
    同时确认 consumer `014` 三个下游表面均无 framework attachment/warning，framework positive fixtures
    保留既有行为，且 LC-01 三文件合计 raw additions ≤80。
  - 实际证据：implementation branch focused=`233 passed`、full=`3332 passed, 3 skipped`，constraints、
    program validate/truth 与 diff-check 全绿；真实 Agent Store framework-only blockers=`0` 且双跑零写入。

- [x] **T32 完成本地对抗代码评审**
  - 依赖：T31
  - 验收：LEAN/SAFETY 对同一 committed+clean implementation identity 均 PASS0/findings=0；
    任何 finding 均在同一分支最小修复并使旧 verdict 失效。
  - 实际证据：LEAN/SAFETY R5 对同一 committed+clean implementation identity 均为
    `PASS0/findings=0`。

- [x] **T33 完成 implementation PR 与 fresh-main 验收**
  - 依赖：T32
  - 验收：Codex review 无可操作问题、required checks 全绿、merge 成功；detached fresh-main 重跑
    focused/full/constraints/Agent Store 隔离验收全部通过。
  - 实际证据：implementation PR #172 reviewed HEAD=`499b383e`、tree=`c319a6b6`，Codex 对精确 HEAD
    未发现 major issue，required checks=`22/22`，squash merge=`fec4c010`；detached fresh-main focused=
    `233 passed`、full=`3332 passed, 3 skipped in 944.67s`，constraints、program validate 与真实 Agent Store
    零写入验收全部通过。
