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

- [ ] **T13 归档 formal PRD**
  - 依赖：T12
  - 验收：formal-only 本地门禁、Codex review、required checks、merge 和 detached fresh-main 全绿；
    formal diff 不包含 WI218 的 `src/**` 或产品行为测试；`development-summary.md` 精确标记
    `stage: close-pending`，inventory=`1141/1141/0/0`、close=`217/217`，status/execute gate 不得推进 close。

## Batch 2：TDD 实现

- [ ] **T21 写入 consumer/framework 隔离 RED 测试并校正既有 framework fixture 身份**
  - 依赖：T13
  - 文件：`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`、
    `tests/integration/test_cli_index_gate.py`
  - 验收：Agent Store、routing-census、`003/012` metadata/编号碰撞在 legacy implementation baseline 上
    按预期 RED；四态身份、invalid pyproject 二态、PrimeVue/common-gate characterization 不产生无关失败。
    新行为断言只在 unit 文件；两个 integration 文件仅为明确验证 framework-only
    `003/012/018/073` 或 backlog/profile/doc-first surfaces 的逐个 fixture 创建 `pyproject.toml`
    （`[project].name = "ai-sdlc"`）和 `src/ai_sdlc/__init__.py`，不改断言/预期输出、不用
    module/global autouse；downstream/relinked `003` 与 consumer `003/012` collision fixture 保持无身份信号。

- [ ] **T22 实现最小双信号与三入口分流**
  - 依赖：T21
  - 文件：`src/ai_sdlc/core/verify_constraints.py`
  - 验收：T21 全部 GREEN；产品 raw additions ≤80、helper ≤2、无新模块/配置/公开抽象。

## Batch 3：验收与交付

- [ ] **T31 完成本地完整验收**
  - 依赖：T22
  - 验收：focused pytest、Ruff、full pytest、constraints、program validate/truth、diff-check 全绿；
    真实 Agent Store 以 current-source、`python -B` 连续双跑，framework-only findings 为0，且前后
    status/diff/dirty-path 三类指纹完全一致。
    full pytest 必须确认 33 个既有 framework fixture 不再因缺少身份信号失败；yaml-store permission 用例
    即使 isolated rerun 通过也不豁免，仍由 full-suite gate 约束。

- [ ] **T32 完成本地对抗代码评审**
  - 依赖：T31
  - 验收：LEAN/SAFETY 对同一 committed+clean implementation identity 均 PASS0/findings=0；
    任何 finding 均在同一分支最小修复并使旧 verdict 失效。

- [ ] **T33 完成 implementation PR 与 fresh-main 验收**
  - 依赖：T32
  - 验收：Codex review 无可操作问题、required checks 全绿、merge 成功；detached fresh-main 重跑
    focused/full/constraints/Agent Store 隔离验收全部通过。
