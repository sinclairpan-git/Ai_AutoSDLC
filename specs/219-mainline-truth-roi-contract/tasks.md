# 任务分解：主线真值复位与轻量 ROI 合同

**编号**：`219-mainline-truth-roi-contract`
**来源**：`spec.md`
**阶段**：execute

## Batch 1：Formal 规格

- [x] **T11 建立 origin/main 隔离基线**
  - 验收：worktree HEAD 精确等于 `origin/main@76252746`；状态/handoff/checkpoint targeted baseline 全绿。
  - 证据：`63 passed in 38.46s`；`verify constraints: no BLOCKERs`。

- [x] **T12 复现当前真值与 continuity 漂移**
  - 依赖：T11
  - 验收：记录 WI204 `branch_only_implemented`、`BLOCK_CODE_PREPARE_TASKS`、陈旧 PR 173 handoff；同时
    证明 Program Truth=`fresh`、release targets=`ready`。
  - 补充证据：link WI219 后 canonical resolver 返回 WI219，但 readiness binding、active dir 和 execute
    authorization 仍返回 WI204，根因限定为 linked-first 消费分叉。

- [x] **T13 冻结 formal 规格与 scope/ROI 停止条件**
  - 依赖：T12
  - 历史验收：首轮把 Track A 限为一个共享纯解析语义、三个显式消费方和定向测试；该范围已由 T15 与
    `spec.md` §4.1 的完整 consumer matrix 取代，不修改 writer/schema/Runner/ProgramService 的边界保持不变。
  - Formal inventory：WI219 新增 5 个已映射 layer，close 暂为 218/217；只机械更新 root manifest tuple，
    保留 missing=1，不放宽任何完整性断言。

- [x] **T14 首轮独立对抗合议**
  - 依赖：T13
  - 结论：`REJECT`；有效阻断为 formal truth 分类、status 消费面遗漏、committed handoff 陈旧、adapter
    allowlist 漏洞与双模板语义验收不足。optional-link Critical 经 WI198 证据复核后撤回。

- [x] **T15 Formal 整改与同候选验证**
  - 依赖：T14
  - 验收：规格冻结 behind-only base、formal-control classification、完整 consumer matrix、semantic-set test；
    删除 adapter escape hatch；canonical/scoped handoff 不再记录已提交前状态。
  - 证据：formal required/forbidden 自审 PASS；targeted suite `79 passed`；constraints 无 BLOCKER；Ruff PASS；
    post-commit continuity refresh 由 T16 候选 identity 提交完成。

- [x] **T16 原三席 round 2 同 identity 复审**
  - 依赖：T15
  - 验收：三个 reviewer 审同一 base/head；任一有效 Critical/Important 未关闭则不批准且不进入第三轮。
  - 证据：三席冻结审阅 `76252746..a5fe086e`；交叉质询后均为 `APPROVE`，无可操作
    Critical/Important；路径级 formal allowlist 与历史 T13 文案仅保留 advisory。

- [x] **T17 用户审阅并批准 formal 规格**
  - 依赖：T16
  - 验收：合议通过后用户明确批准；批准前没有产品或特性测试实现任务。
  - 证据：用户于 2026-08-25 明确回复“批准”。

## Batch 2：A0 truth baseline/classification

- [x] **T20 stale-local-main 与 formal-control RED**
  - 依赖：T17
  - 范围：`tests/integration/test_cli_workitem_truth_check.py`
  - 验收：behind-only 四类 Git fixture 与 formal allowlist/范围外路径用例先以预期原因失败；测试前后 refs 不变。

- [x] **T21 behind-only base 与 exact formal-control GREEN**
  - 依赖：T20
  - 范围：`src/ai_sdlc/core/workitem_truth.py`
  - 验收：WI219 formal candidate 为 `formal_freeze_only`；任一范围外实现/测试/配置/产品文档为
    `branch_only_implemented`；无 fetch/ref 写入、无 GitClient 或新状态修改。

- [x] **T22 A0 Go/No-Go 与提交**
  - 依赖：T21
  - 验收：truth-check 定向测试与 Ruff 全绿；冻结边界未越过；A0 独立提交。

## Batch 3：A1 linked-first active binding

- [x] **T30 active spec-dir helper 与 consumer matrix RED**
  - 依赖：T22
  - 范围：`tests/unit/test_context_state.py`、`tests/unit/test_telemetry_readiness.py`、
    `tests/unit/test_execute_authorization.py`；只有 unit 证据不足时才修改 `tests/integration/test_cli_status.py`。
  - 验收：valid/no-link/missing/partial、branch-stage、main+close 与 strict-load 矩阵先复现历史 feature 泄漏。

- [x] **T31 单一 linked-first id/spec-dir GREEN**
  - 依赖：T30
  - 范围：`src/ai_sdlc/context/state.py`、`src/ai_sdlc/telemetry/readiness.py`、
    `src/ai_sdlc/core/execute_authorization.py`
  - 验收：resume/status/execute 全部复用一个无 I/O spec-dir helper；missing/partial fail-closed；legacy 无 link
    行为、错误文本、writer/schema/status 格式保持不变。

- [x] **T32 A1 Go/No-Go 与提交**
  - 依赖：T31
  - 验收：三组 unit、必要的 status CLI 与 Ruff 全绿；无第二 resolver、无 silent fallback；A1 独立提交。

### Task 3.1 linked-first active binding 收口

- task_id: T31X
- status: done
- goal: 完成 A1 的回归、ROI 复核、独立提交和证据记录。
- depends:
  - T22
- scope:
  - src/ai_sdlc/context/state.py
  - src/ai_sdlc/telemetry/readiness.py
  - src/ai_sdlc/core/execute_authorization.py
- acceptance:
  - 全部 active-WI consumer 使用 linked-first id/spec-dir，missing linked target fail-closed。
  - 不修改 writer、schema、status 格式或 backlog guard 本体。
- verify:
  - uv run pytest tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q
  - uv run ruff check src/ai_sdlc/context/state.py src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/core/execute_authorization.py tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py

## Batch 4：B 双模板 ROI semantic set

### Task 4.1 双模板 ROI semantic set

- task_id: T40B
- status: done
- goal: 先以两条真实生成路径复现语义缺口，再只修改两份现有模板完成 GREEN。
- depends:
  - T31X
- scope:
  - templates/spec-template.md
  - src/ai_sdlc/templates/spec.md.j2
- acceptance:
  - direct-formal 与 stage/native 输出均包含六项提示、四个 decision、轻量例外、risk-only 数值和 blocker 边界。
  - 不新增 parser、constraint blocker、Python 公共面或持久化字段。
- verify:
  - uv run pytest tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py tests/integration/test_cli_workitem_init.py -q
  - uv run ruff check tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py

- [x] **T40 两条真实 render/scaffold semantic RED**
  - 依赖：T32
  - 范围：`tests/unit/test_workitem_scaffold.py`、`tests/unit/test_doc_gen.py`
  - 验收：生成结果缺少六项提示、四个 decision、轻量例外、risk-only 数值与 blocker 边界时稳定失败。

- [x] **T41 两份现有模板最小 GREEN**
  - 依赖：T40
  - 范围：`templates/spec-template.md`、`src/ai_sdlc/templates/spec.md.j2`
  - 验收：两路径 canonical semantic set 一致；不新增 parser、constraint blocker、Python 公共面或持久化字段。

- [x] **T42 B Go/No-Go 与提交**
  - 依赖：T41
  - 验收：scaffold/render/workitem-init 测试与 Ruff 全绿；B 独立提交。

## Batch 5：统一验证与交付

### Task 5.1 统一验证与主线交付

- task_id: T50V
- status: doing
- goal: 对 A0/A1/B exact HEAD 完成回归、ROI 复核、continuity 和主线 PR 闭环。
- depends:
  - T40B
- scope:
  - specs/219-mainline-truth-roi-contract/
  - .ai-sdlc/state/
  - .ai-sdlc/work-items/219-mainline-truth-roi-contract/
  - program-manifest.yaml
  - tests/integration/test_repo_program_manifest.py
  - src/ai_sdlc/core/workitem_truth.py
  - src/ai_sdlc/context/state.py
  - src/ai_sdlc/telemetry/readiness.py
  - src/ai_sdlc/core/execute_authorization.py
  - tests/integration/test_cli_workitem_truth_check.py
  - tests/unit/test_context_state.py
  - tests/unit/test_telemetry_readiness.py
  - tests/unit/test_execute_authorization.py
  - tests/unit/test_doc_gen.py
  - tests/unit/test_workitem_scaffold.py
- acceptance:
  - focused/full pytest、Ruff、constraints、Program Truth、manifest 与 diff-check 全绿。
  - exact-head 只读 review 无可操作问题，required checks 通过后合并主线。
- verify:
  - uv run pytest -q
  - uv run ruff check .
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program truth audit

- [x] **T50 focused/full verification 与 ROI 复核**
  - 依赖：T42
  - 验收：focused/full pytest、Ruff、constraints、Program Truth audit、diff-check 全绿；记录产品/测试净新增与
    冻结范围差异。

- [x] **T51 continuity 与 Program Truth 收口**
  - 依赖：T50
  - 验收：task log、plan/tasks、manifest、root tuple 与 canonical/scoped handoff 准确；工作树干净。

- [ ] **T52 本地只读 review 与主线 PR 流程**
  - 依赖：T51
  - 验收：exact-head 本地 review 无可操作问题；随后 push/PR/Codex review/required checks 按仓库协议闭环。

- [x] **T53 exact-head review 定向整改**
  - 依赖：T51
  - 验收：rename 来源路径进入 truth inventory；linked ID 和 resolved path 均 fail-closed；formal-only 文案不再
    谎称 execution log 缺失；双模板语义测试的重复支撑显著下降。
