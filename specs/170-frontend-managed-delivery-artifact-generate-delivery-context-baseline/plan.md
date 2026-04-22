# 实施计划：Frontend Managed Delivery Artifact Generate Delivery Context Baseline

**功能编号**：`170-frontend-managed-delivery-artifact-generate-delivery-context-baseline`  
**日期**：`2026-04-19`

## 1. 实施目标

在不扩张 `managed_delivery_apply` 责任边界的前提下，把 `artifact_generate` 稳定绑定到当前 delivery context，并让 dry-run / execute / generated file content 三个面保持一致。

## 2. 实施边界

- 只允许修改 `managed_delivery_apply` request builder、artifact payload content renderer 与 CLI guard surface；
- 不修改 `managed_delivery_apply` runtime executor 的总体流程；
- 不新增新的 managed target 路径或额外 scaffold 文件；
- 不改写 `167/168/169` handoff 本体，只消费其既有输出。

## 3. 验证

- `uv run python -m pytest tests/unit/test_program_service.py::test_build_frontend_managed_delivery_apply_request_materializes_public_bundle_from_truth tests/unit/test_program_service.py::test_build_frontend_managed_delivery_apply_request_materializes_artifact_generate_from_delivery_context tests/integration/test_cli_program.py::TestCliProgram::test_program_managed_delivery_apply_dry_run_materializes_request_from_truth_when_request_omitted tests/integration/test_cli_program.py::TestCliProgram::test_program_managed_delivery_apply_execute_truth_derived_accepts_ack_for_effective_change -q`
- `git diff --check`
- `uv run python -m ai_sdlc run --dry-run`

## 4. 风险与回退

- 若 TS content renderer 改动导致已有 execute runtime 产物格式漂移，则回退到仅最小调整 key rendering / string layout，不重写 payload 数据结构；
- 若 dry-run surface 丢失 `artifact_generate` 的原因来自 `decision_receipt` 而不是 CLI render，则优先修 request payload，而不是在 CLI 层硬编码补字串。
