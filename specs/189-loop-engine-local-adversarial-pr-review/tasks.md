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

### Task 1.1 Define Loop and Review data models

- task_id: T11
- status: done
- goal: 定义 Loop / Review 数据模型
- priority: P0
- scope:
  - src/ai_sdlc/core/loop_models.py
  - src/ai_sdlc/core/pr_review_models.py
  - tests/unit/test_pr_review_models.py
- acceptance:
  - 定义 LoopRun、LoopRound、ReviewRun、ReviewPack、ReviewFinding、FindingResolution、LoopPolicyProfile、ProviderRunnerInvocation、SchemaValidationReport。
  - 所有长期 artifact 模型包含 schema_version、artifact_kind、created_by、created_at、ai_sdlc_version。
  - severity、resolution、verdict、loop status 使用稳定 enum 或等价受控集合。
- verify:
  - uv run pytest tests/unit/test_pr_review_models.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行；这是后续 schema 与 artifact store 的基础。

### Task 1.2 Implement schema validation and artifact store

- task_id: T12
- status: done
- goal: 实现 schema validation 与 artifact store
- priority: P0
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/pr_review_schema.py
  - src/ai_sdlc/core/loop_artifacts.py
  - tests/unit/test_pr_review_schema.py
  - tests/unit/test_loop_artifacts.py
- acceptance:
  - schema validation 能阻断缺失必填字段、不兼容 schema version、非法 enum。
  - artifact store 能创建 .ai-sdlc/loops/local-pr-review/<loop-id>/ 与 .ai-sdlc/reviews/pr/<review-id>/。
  - 写入 JSON/YAML/Markdown artifact 使用原子或现有安全写入模式。
- verify:
  - uv run pytest tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行；后续 pack/provider/service 都依赖该持久化合同。

## Batch 2：policy profile、redaction、review pack builder

### Task 2.1 Implement LoopPolicyProfile

- task_id: T21
- status: done
- goal: 实现 LoopPolicyProfile
- priority: P0
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/loop_policy.py
  - tests/unit/test_loop_policy.py
- acceptance:
  - 默认策略 safe-by-default：default provider 为 local-agent，default model 为 current，远程模型服务代码外发必须披露，是否需要确认由 policy 决定；max rounds 默认 2，default close strict。
  - 支持读取 .ai-sdlc/project/config/loop-policy.yaml。
  - policy 与命令参数冲突时 policy 优先，并返回 plain-language blocker。
- verify:
  - uv run pytest tests/unit/test_loop_policy.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 可与 T22 设计并行；策略接口落地必须早于 redaction 决策接入。

### Task 2.2 Implement redaction and omission preflight

- task_id: T22
- status: done
- goal: 实现 redaction / omission 预检
- priority: P0
- depends:
  - T21
- scope:
  - src/ai_sdlc/core/pr_review_redaction.py
  - tests/unit/test_pr_review_redaction.py
- acceptance:
  - 检测 .env*、私钥、常见 token/key 模式、binary、large、generated files。
  - 生成 redaction-report.json 数据结构。
  - high-risk secret + 会外发代码的 provider/model 时返回 needs_user，除非 policy 和用户显式确认允许继续。
- verify:
  - uv run pytest tests/unit/test_pr_review_redaction.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；必须服从 LoopPolicyProfile。

### Task 2.3 Implement review pack builder

- task_id: T23
- status: done
- goal: 实现 review pack builder
- priority: P0
- depends:
  - T12
  - T21
  - T22
- scope:
  - src/ai_sdlc/core/pr_review_pack.py
  - tests/unit/test_pr_review_pack.py
- acceptance:
  - 生成 review-pack.json、diff.patch、changed-files.txt、redaction-report.json。
  - 记录 base/head ref、base/head commit、diff_summary、changed files、diff coverage、work_item_refs、test_results_refs、policy_refs、policy decisions、provider mode、model selector、model resolution status/source、resolved model、code egress、allowlist。
  - 不读取或写入 implementation agent chat transcript。
  - diff 过大时进入 needs_user 或分片记录，不静默丢弃。
- verify:
  - uv run pytest tests/unit/test_pr_review_pack.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；依赖 schema、policy、redaction 三个合同。

## Batch 3：provider runner 与 mock reviewer

### Task 3.1 Implement provider runner contract

- task_id: T31
- status: done
- goal: 实现 provider runner 合同
- priority: P0
- depends:
  - T12
  - T23
- scope:
  - src/ai_sdlc/core/pr_review_provider.py
  - tests/unit/test_pr_review_provider.py
- acceptance:
  - 标准化退出码 0/10/20/other。
  - 写入 reviewer-invocation.json，记录 command、argv、cwd、input/output paths、model selector、resolved model、code egress、allowlist、隔离状态、exit status。
  - 缺失 findings、非 JSON、schema validation 失败时 loop blocked。
  - local-agent 已配置本地 fixture command 时可运行并生成合法 findings。
  - local-agent 默认使用 model=current，并支持显式 model selector；provider invocation 必须记录 provider mode、model selector、model resolution source、resolved model 和 code egress。
  - model=current 必须按 CLI > policy > provider config > current agent/CLI 环境解析，无法解析时进入 needs_user。
  - local-agent 未配置或 model=current 无法解析时进入 needs_user，不得 fallback 到云端 PR review。
- verify:
  - uv run pytest tests/unit/test_pr_review_provider.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；provider runner 不得调用 Codex 云端 PR review。

### Task 3.2 Implement mock reviewer

- task_id: T32
- status: done
- goal: 实现 mock-reviewer
- priority: P0
- depends:
  - T31
- scope:
  - src/ai_sdlc/core/pr_review_provider.py
  - tests/unit/test_pr_review_provider.py
  - tests/fixtures/pr_review/
- acceptance:
  - mock-reviewer 不访问网络、不调用模型。
  - 支持输出 clean、changes_required、blocked、malformed findings fixture。
  - 可驱动 CLI integration tests。
- verify:
  - uv run pytest tests/unit/test_pr_review_provider.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；这是后续 CLI 集成的确定性测试 provider。

## Batch 4：pr-review doctor/start/status CLI

### Task 4.1 Implement PR Review service

- task_id: T41
- status: done
- goal: 实现 PR Review service
- priority: P0
- depends:
  - T23
  - T31
  - T32
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - tests/unit/test_pr_review_service.py
- acceptance:
  - doctor 检查 init、Git、base、provider、policy、redaction、artifact writability。
  - start 支持 dry-run 和 mock-reviewer。
  - status 可恢复 current run、findings、resolution、next command。
  - 所有失败返回 plain-language blocker。
  - doctor 与 start --dry-run 不创建 review run、不写 .ai-sdlc/reviews/pr/<review-id>/，不改写 current review 指针。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；CLI 层只编排 service，不复制业务逻辑。

### Task 4.2 Register ai-sdlc pr-review CLI

- task_id: T42
- status: done
- goal: 注册 ai-sdlc pr-review CLI
- priority: P0
- depends:
  - T41
- scope:
  - src/ai_sdlc/cli/pr_review_cmd.py
  - src/ai_sdlc/cli/main.py
  - src/ai_sdlc/__main__.py
  - src/ai_sdlc/cli/command_names.py
  - tests/integration/test_cli_pr_review.py
  - tests/unit/test_command_names.py
- acceptance:
  - ai-sdlc pr-review doctor/start/status 可用。
  - human 输出包含 Result / Next / plain-language blocker / next command / provider / model selector / resolved model / code egress。
  - --json 输出稳定。
  - python -m ai_sdlc --help fallback 包含 pr-review。
  - pr-review fix/rerun/close 在 help 和真实 CLI 路径可见；具体状态机验收由 T51-T53 覆盖。
- verify:
  - uv run pytest tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；真实 CLI surface 是 P0 验收面。

## Batch 5：fix/rerun/close 语义

### Task 5.1 Implement fix-plan and resolution flow

- task_id: T51
- status: done
- goal: 实现 fix-plan 与 resolution 流程
- priority: P0
- depends:
  - T41
  - T42
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - tests/unit/test_pr_review_service.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - fix 只生成 fix-plan.md 和 resolution.yaml，不修改代码。
  - 默认只包含 BLOCKER 和 REQUIRED。
  - ADVISORY 不进入自动修复计划。
  - max rounds 超限进入 needs_user。
  - ai-sdlc pr-review fix --json 与 human 输出都可通过真实 CLI integration test。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；reviewer agent 与 implementation agent 职责必须隔离。

### Task 5.2 Implement rerun and scope drift checks

- task_id: T52
- status: done
- goal: 实现 rerun 与 scope drift 检查
- priority: P0
- depends:
  - T51
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - tests/unit/test_pr_review_service.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - rerun 重新生成 review pack，不复用旧 diff。
  - head commit 变化后旧 report 不作为当前有效 review。
  - 非 finding 相关扩大范围报告 scope drift。
  - ai-sdlc pr-review rerun --json 与 human 输出都可通过真实 CLI integration test。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；rerun 是对抗 review 闭环的关键收敛点。

### Task 5.3 Implement close verdict

- task_id: T53
- status: done
- goal: 实现 close verdict
- priority: P0
- depends:
  - T51
  - T52
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - tests/unit/test_pr_review_service.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - 默认 close 阻断 unresolved BLOCKER 和 REQUIRED。
  - --require-no-blockers 输出 risk_accepted，不得标记 fully_clean。
  - final report 包含 verdict、commits、unresolved counts、redaction/omission summary、verification evidence、next action。
  - ai-sdlc pr-review close --json 与 human 输出都可通过真实 CLI integration test。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行落地；close verdict 必须 fail-closed。

## Batch 6：close-check、handoff、verify、docs 对齐

### Task 6.1 Integrate close-check and handoff

- task_id: T61
- status: done
- goal: 集成 close-check 与 handoff
- priority: P0
- depends:
  - T53
- scope:
  - src/ai_sdlc/core/close_check.py
  - src/ai_sdlc/core/handoff.py
  - tests/unit/test_close_check.py
  - tests/integration/test_cli_workitem_close_check.py
  - tests/integration/test_cli_handoff.py
- acceptance:
  - close-check 可读取 local PR review final report。
  - 区分 fully_clean、risk_accepted、blocked。
  - handoff 记录 current review id、unresolved counts、beginner-facing next command。
- verify:
  - uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_handoff.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 可与 T62 文档准备并行。

### Task 6.2 Align verify constraints and docs surface

- task_id: T62
- status: done
- goal: 对齐 verify constraints 与 docs/release surface
- priority: P0
- depends:
  - T42
  - T53
- scope:
  - src/ai_sdlc/core/verify_constraints.py
  - README.md
  - docs/pull-request-checklist.zh.md
  - tests/unit/test_verify_constraints.py
  - tests/integration/test_cli_verify_constraints.py
- acceptance:
  - verify constraints 覆盖云端 PR review 禁用、CI 不发起模型请求、schema/policy 文档 surface。
  - README 给出小白 3 步路径：init、pr-review doctor、pr-review start。
  - 文档说明本地模型 review 与 CI 确定性检查分工。
  - release notes 不使用未定版本占位；若本工作项进入明确版本发布，再以实际版本号创建或更新对应 docs/releases/vX.Y.Z.md。
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q
- notes:
  - 验收标准：见 acceptance 字段。
  - 可与 T61 并行；release note 只在明确发布版本时更新。

### Task 6.3 Final regression and execution log close-out

- task_id: T63
- status: done
- goal: 最终回归与执行日志收口
- priority: P0
- depends:
  - T61
  - T62
- scope:
  - specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md
- acceptance:
  - task-execution-log 记录所有批次、命令、结果和 residual risk。
  - git diff --check 通过。
  - uv run ai-sdlc verify constraints 通过。
  - focused tests 通过。
- verify:
  - git diff --check
  - uv run ai-sdlc verify constraints
  - focused pytest bundle
- notes:
  - 验收标准：见 acceptance 字段。
  - 不可并行；该任务是实现阶段最终收口任务。

## 实现前硬性边界

1. 不得调用 Codex 云端 PR review。
2. 不得在 CI workflow 中加入 GPT、Claude、DeepSeek、GLM、Codex 或其他模型调用；模型调用只能由本地独立 review agent 发起。
3. P0 不允许 reviewer 修改代码。
4. P0 不实现远端 PR inline comments。
5. 每个 batch 完成后必须更新 task-execution-log.md 和 handoff。
