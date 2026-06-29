# 任务分解：AI-SDLC Loop Engine and Local Adversarial PR Review

**编号**：`189-loop-engine-local-adversarial-pr-review`  
**日期**：2026-06-29  
**来源**：已冻结 `spec.md` + `plan.md`  
**状态**：可执行任务分解已冻结，等待用户明确进入实现

## 分批策略

```text
Batch 1: core models, schema validation, artifact store
Batch 2: policy profile, redaction, review pack builder
Batch 3: provider runner and mock reviewer
Batch 4: pr-review doctor/start/status CLI
Batch 5: fix/rerun/close loop semantics
Batch 6: close-check, handoff, verify, docs alignment
```

## Batch 1：核心模型、schema validation、artifact store

### Task 1.1 定义 Loop / Review 数据模型

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`src/ai_sdlc/core/loop_models.py`、`src/ai_sdlc/core/pr_review_models.py`、`tests/unit/test_pr_review_models.py`
- **可并行**：否
- **验收标准**：
  1. 定义 `LoopRun`、`LoopRound`、`ReviewRun`、`ReviewPack`、`ReviewFinding`、`FindingResolution`、`LoopPolicyProfile`、`ProviderRunnerInvocation`、`SchemaValidationReport`。
  2. 所有长期 artifact 模型包含 `schema_version`、`artifact_kind`、`created_by`、`created_at`、`ai_sdlc_version`。
  3. severity、resolution、verdict、loop status 使用稳定 enum 或等价受控集合。
- **验证**：`uv run pytest tests/unit/test_pr_review_models.py -q`

### Task 1.2 实现 schema validation 与 artifact store

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`src/ai_sdlc/core/pr_review_schema.py`、`src/ai_sdlc/core/loop_artifacts.py`、`tests/unit/test_pr_review_schema.py`、`tests/unit/test_loop_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. schema validation 能阻断缺失必填字段、不兼容 schema version、非法 enum。
  2. artifact store 能创建 `.ai-sdlc/loops/local-pr-review/<loop-id>/` 与 `.ai-sdlc/reviews/pr/<review-id>/`。
  3. 写入 JSON/YAML/Markdown artifact 使用原子或现有安全写入模式。
- **验证**：`uv run pytest tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py -q`

## Batch 2：policy profile、redaction、review pack builder

### Task 2.1 实现 LoopPolicyProfile

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`src/ai_sdlc/core/loop_policy.py`、`tests/unit/test_loop_policy.py`
- **可并行**：可与 T22 设计并行，落地需在 T22 前完成策略接口
- **验收标准**：
  1. 默认策略 safe-by-default：external provider 需确认，max rounds 默认 2，default close strict。
  2. 支持读取 `.ai-sdlc/project/config/loop-policy.yaml`。
  3. policy 与命令参数冲突时 policy 优先，并返回 plain-language blocker。
- **验证**：`uv run pytest tests/unit/test_loop_policy.py -q`

### Task 2.2 实现 redaction / omission 预检

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/pr_review_redaction.py`、`tests/unit/test_pr_review_redaction.py`
- **可并行**：否
- **验收标准**：
  1. 检测 `.env*`、私钥、常见 token/key 模式、binary、large、generated files。
  2. 生成 `redaction-report.json` 数据结构。
  3. high-risk secret + external provider 未确认时返回 `needs_user`。
- **验证**：`uv run pytest tests/unit/test_pr_review_redaction.py -q`

### Task 2.3 实现 review pack builder

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T12、T21、T22
- **文件**：`src/ai_sdlc/core/pr_review_pack.py`、`tests/unit/test_pr_review_pack.py`
- **可并行**：否
- **验收标准**：
  1. 生成 `review-pack.json`、`diff.patch`、`changed-files.txt`、`redaction-report.json`。
  2. 记录 base/head ref、base/head commit、`diff_summary`、changed files、diff coverage、`work_item_refs`、`test_results_refs`、`policy_refs`、policy decisions、allowlist。
  3. 不读取或写入 implementation agent chat transcript。
  4. diff 过大时进入 `needs_user` 或分片记录，不静默丢弃。
- **验证**：`uv run pytest tests/unit/test_pr_review_pack.py -q`

## Batch 3：provider runner 与 mock reviewer

### Task 3.1 实现 provider runner 合同

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T12、T23
- **文件**：`src/ai_sdlc/core/pr_review_provider.py`、`tests/unit/test_pr_review_provider.py`
- **可并行**：否
- **验收标准**：
  1. 标准化退出码 `0/10/20/other`。
  2. 写入 `reviewer-invocation.json`，记录 command、argv、cwd、input/output paths、allowlist、隔离状态、exit status。
  3. 缺失 findings、非 JSON、schema validation 失败时 loop blocked。
  4. `codex-local` 已配置本地 fixture command 时可运行并生成合法 findings。
  5. `codex-local` 未配置时进入 `needs_user`，不得 fallback 到云端 PR review。
- **验证**：`uv run pytest tests/unit/test_pr_review_provider.py -q`

### Task 3.2 实现 mock-reviewer

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`src/ai_sdlc/core/pr_review_provider.py`、`tests/unit/test_pr_review_provider.py`、`tests/fixtures/pr_review/`
- **可并行**：否
- **验收标准**：
  1. `mock-reviewer` 不访问网络、不调用模型。
  2. 支持输出 clean、changes_required、blocked、malformed findings fixture。
  3. 可驱动 CLI integration tests。
- **验证**：`uv run pytest tests/unit/test_pr_review_provider.py -q`

## Batch 4：pr-review doctor/start/status CLI

### Task 4.1 实现 PR Review service

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T23、T31、T32
- **文件**：`src/ai_sdlc/core/pr_review_service.py`、`tests/unit/test_pr_review_service.py`
- **可并行**：否
- **验收标准**：
  1. `doctor` 检查 init、Git、base、provider、policy、redaction、artifact writability。
  2. `start` 支持 dry-run 和 mock-reviewer。
  3. `status` 可恢复 current run、findings、resolution、next command。
  4. 所有失败返回 plain-language blocker。
  5. `doctor` 与 `start --dry-run` 不创建 review run、不写 `.ai-sdlc/reviews/pr/<review-id>/`，不改写 current review 指针。
- **验证**：`uv run pytest tests/unit/test_pr_review_service.py -q`

### Task 4.2 注册 `ai-sdlc pr-review` CLI

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/cli/pr_review_cmd.py`、`src/ai_sdlc/cli/main.py`、`src/ai_sdlc/__main__.py`、`src/ai_sdlc/cli/command_names.py`、`tests/integration/test_cli_pr_review.py`、`tests/unit/test_command_names.py`
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc pr-review doctor/start/status` 可用。
  2. human 输出包含 Result / Next / plain-language blocker / next command。
  3. `--json` 输出稳定。
  4. `python -m ai_sdlc --help` fallback 包含 `pr-review`。
  5. `pr-review fix/rerun/close` 在 help 和真实 CLI 路径可见；具体状态机验收由 T51-T53 覆盖。
- **验证**：`uv run pytest tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py -q`

## Batch 5：fix/rerun/close 语义

### Task 5.1 实现 fix-plan 与 resolution 流程

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T41、T42
- **文件**：`src/ai_sdlc/core/pr_review_service.py`、`tests/unit/test_pr_review_service.py`、`tests/integration/test_cli_pr_review.py`
- **可并行**：否
- **验收标准**：
  1. `fix` 只生成 `fix-plan.md` 和 `resolution.yaml`，不修改代码。
  2. 默认只包含 `BLOCKER` 和 `REQUIRED`。
  3. `ADVISORY` 不进入自动修复计划。
  4. max rounds 超限进入 `needs_user`。
  5. `ai-sdlc pr-review fix --json` 与 human 输出都可通过真实 CLI integration test。
- **验证**：`uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`

### Task 5.2 实现 rerun 与 scope drift 检查

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/core/pr_review_service.py`、`tests/unit/test_pr_review_service.py`、`tests/integration/test_cli_pr_review.py`
- **可并行**：否
- **验收标准**：
  1. rerun 重新生成 review pack，不复用旧 diff。
  2. head commit 变化后旧 report 不作为当前有效 review。
  3. 非 finding 相关扩大范围报告 scope drift。
  4. `ai-sdlc pr-review rerun --json` 与 human 输出都可通过真实 CLI integration test。
- **验证**：`uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`

### Task 5.3 实现 close verdict

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T51、T52
- **文件**：`src/ai_sdlc/core/pr_review_service.py`、`tests/unit/test_pr_review_service.py`、`tests/integration/test_cli_pr_review.py`
- **可并行**：否
- **验收标准**：
  1. 默认 close 阻断 unresolved `BLOCKER` 和 `REQUIRED`。
  2. `--require-no-blockers` 输出 `risk_accepted`，不得标记 `fully_clean`。
  3. final report 包含 verdict、commits、unresolved counts、redaction/omission summary、verification evidence、next action。
  4. `ai-sdlc pr-review close --json` 与 human 输出都可通过真实 CLI integration test。
- **验证**：`uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`

## Batch 6：close-check、handoff、verify、docs 对齐

### Task 6.1 集成 close-check 与 handoff

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T53
- **文件**：`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/core/handoff.py`、`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`、`tests/integration/test_cli_handoff.py`
- **可并行**：可与 T62 文档准备并行
- **验收标准**：
  1. close-check 可读取 local PR review final report。
  2. 区分 `fully_clean`、`risk_accepted`、`blocked`。
  3. handoff 记录 current review id、unresolved counts、beginner-facing next command。
- **验证**：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_handoff.py -q`

### Task 6.2 verify constraints 与 docs/release surface

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T42、T53
- **文件**：`src/ai_sdlc/core/verify_constraints.py`、`README.md`、`docs/pull-request-checklist.zh.md`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`
- **可并行**：可与 T61 并行
- **验收标准**：
  1. verify constraints 覆盖云端 PR review 禁用、CI no-model、schema/policy 文档 surface。
  2. README 给出小白 3 步路径：`init`、`pr-review doctor`、`pr-review start`。
  3. 文档说明本地模型 review 与 CI 确定性检查分工。
  4. release notes 不使用未定版本占位；若本工作项进入明确版本发布，再以实际版本号创建或更新对应 `docs/releases/vX.Y.Z.md`。
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`

### Task 6.3 最终回归与执行日志收口

- **任务编号**：T63
- **优先级**：P0
- **依赖**：T61、T62
- **文件**：`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. task-execution-log 记录所有批次、命令、结果和 residual risk。
  2. `git diff --check` 通过。
  3. `uv run ai-sdlc verify constraints` 通过。
  4. focused tests 通过。
- **验证**：`git diff --check` + `uv run ai-sdlc verify constraints` + focused pytest bundle。

## 实现前硬性边界

1. 不得调用 Codex 云端 PR review。
2. 不得在 CI workflow 中加入 GPT/Codex 调用。
3. P0 不允许 reviewer 修改代码。
4. P0 不实现远端 PR inline comments。
5. 每个 batch 完成后必须更新 `task-execution-log.md` 和 handoff。
