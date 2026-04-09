# 功能规格：Frontend Evidence Class Close-Check Runtime Implementation Baseline

**功能编号**：`091-frontend-evidence-class-close-check-runtime-implementation-baseline`  
**创建日期**：2026-04-09  
**状态**：formal baseline 已冻结；首批 implementation slice 进行中  
**输入**：[`../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`](../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md)、[`../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md`](../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)

> 口径：`091` 是 `089` 的首个 runtime implementation carrier。它只把 `frontend_evidence_class` 的 bounded late resurfacing 落到 `workitem close-check`，允许最小写面为 `src/ai_sdlc/core/close_check.py` 与 `tests/integration/test_cli_workitem_close_check.py`；它不改写 `089` 的 docs-only truth，不新增 owning surface，不实现 mirror writeback，不扩张 `status` / `program validate` / `close-check` 之外的输出面。

## 问题定义

`089` 已经 formalize 了 close-stage late resurfacing contract，但它自己是 docs-only baseline，不能直接承载 runtime 写面。当前仓库若继续把 `frontend_evidence_class` 的 close-check 实现直接堆进 `089`，会出现两层 truth 冲突：

- formal spec 说 `089` 不得改 `src/` 与 `tests/`
- 实际 diff 却在实现 `close_check.py` 与 integration test

因此需要一条新的 implementation carrier，把 `089` 的 bounded resurfacing contract 转成最小可执行 slice，并显式约束本轮只能实现：

- close-check 读取上游已派生的 authoring malformed / mirror drift truth
- close-check 仅以 bounded detail 复报 unresolved blocker
- integration test 覆盖 table / json 两个 close-stage surface

## 范围

- **覆盖**：
  - 新建 `091` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `91`
  - 在 `src/ai_sdlc/core/close_check.py` 实现 `frontend_evidence_class` 的 close-stage late resurfacing
  - 在 `tests/integration/test_cli_workitem_close_check.py` 添加 authoring malformed / mirror drift 定向回归
- **不覆盖**：
  - 修改 `089` 的 docs-only contract 本体
  - 修改 `program validate`、`program status`、`status --json`
  - 实现 `program-manifest.yaml` writeback 或 auto-heal
  - retroactively 改写 `068` ~ `071`

## 已锁定决策

- `091` 只消费 upstream derived truth，不承担 first-detection
- close-check surfacing 继续限制为 `problem_family`、`detection_surface` 与单个 compact token
- close-check 不展开 `source_of_truth_path`、`expected_contract_ref`、`human_remediation_hint`
- mirror drift fixture 必须使用合法 manifest YAML，避免用测试夹具错误冒充 runtime 语义

## 用户故事与验收

### US-091-1 — Reviewer 需要在 close-stage 看见 bounded blocker

作为 **reviewer**，我希望 `workitem close-check` 能在 close-stage 重述尚未解决的 `frontend_evidence_class` blocker，这样我不必切回上游 surface 才知道当前工单还不能 close。

**验收**：

1. Given 当前工单存在 `frontend_evidence_class_authoring_malformed`，When 运行 `workitem close-check --json`，Then 输出包含 `problem_family`、`verify constraints` 与 compact `error_kind`
2. Given 当前工单存在 `frontend_evidence_class_mirror_drift`，When 运行 `workitem close-check`，Then 输出包含 `problem_family`、`program validate` 与 compact drift token

### US-091-2 — Maintainer 需要确保 close-check 不越界

作为 **future maintainer**，我希望 `close-check` 只做 late resurfacing，这样它不会重新变成 validator 或 writeback surface。

**验收**：

1. Given `close-check` surfacing evidence-class blocker，When 对照 `091`，Then 我能确认它没有展开 full diagnostics payload
2. Given manifest fixture 非法缩进导致 YAML 解析失败，When 对照 `091`，Then 我知道应修复 fixture，而不是让 close-check 改义

## 功能需求

| ID | 需求 |
|----|------|
| FR-091-001 | `091` 必须把 `089` 的 close-stage late resurfacing contract 落到 `src/ai_sdlc/core/close_check.py` |
| FR-091-002 | `091` 必须只复报 `frontend_evidence_class_authoring_malformed` 与 `frontend_evidence_class_mirror_drift` 两类 blocker |
| FR-091-003 | `091` 必须确保 close-check 只输出 bounded detail，不得展开 `source_of_truth_path`、`expected_contract_ref`、`human_remediation_hint` |
| FR-091-004 | `091` 必须在 integration test 中覆盖 table 与 `--json` 两种 close-stage surface |
| FR-091-005 | `091` 必须将 manifest drift fixture 写成合法 YAML，并把 fixture 解析错误与 runtime semantics 明确分离 |
| FR-091-006 | `091` 只允许写 `src/ai_sdlc/core/close_check.py`、`tests/integration/test_cli_workitem_close_check.py` 与本工单文档 |
| FR-091-007 | `091` 不得修改 `program validate`、`program status`、`status --json`、`program-manifest.yaml` |
| FR-091-008 | `091` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `90` 推进到 `91` |

## 成功标准

- **SC-091-001**：`workitem close-check` 能 bounded resurfacing `frontend_evidence_class_authoring_malformed`
- **SC-091-002**：`workitem close-check` 能 bounded resurfacing `frontend_evidence_class_mirror_drift`
- **SC-091-003**：integration tests 证明 table / json 都不泄露 full diagnostics payload
- **SC-091-004**：本轮 diff 仅触及 `close_check.py`、对应 integration test、`091` 文档与 `project-state.yaml`

---
related_doc:
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "src/ai_sdlc/core/close_check.py"
  - "tests/integration/test_cli_workitem_close_check.py"
frontend_evidence_class: "framework_capability"
---
