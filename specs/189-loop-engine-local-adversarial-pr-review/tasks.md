# 任务分解：AI-SDLC Loop Engine and Local Adversarial PR Review

**编号**：`189-loop-engine-local-adversarial-pr-review`
**日期**：2026-06-29
**来源**：已冻结 `spec.md` + `plan.md`；2026-06-30 用户澄清修订
**状态**：T11-T84、T91 已完成；Loop Engineering 本工作项当前冻结优先级需求已落地

## 分批策略

```text
Batch 1: core models, schema validation, artifact store
Batch 2: policy profile, redaction, review pack builder
Batch 3: provider runner and mock reviewer
Batch 4: pr-review doctor/start/status CLI
Batch 5: fix/rerun/close loop semantics
Batch 6: close-check, handoff, verify, docs alignment
Batch 7: 2026-06-30 source/model adaptability delta
Batch 8: P1 diff-source/attestation/history expansion
Batch 9: P2 enterprise contract and fail-closed surfaces
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
  - local-agent 支持 model=current 与显式 model selector；provider invocation 必须记录 provider mode、model selector、model resolution source、resolved model 和 code egress。
  - 当前模型默认解析、显式模型可用性校验和 fail-closed 语义以 T72 为当前需求真值。
  - local-agent 未配置或模型无法解析时进入 needs_user，不得 fallback 到云端 PR review。
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

## Batch 7：2026-06-30 source/model/UX 适配性补齐

> 本批任务来自 2026-06-30 用户澄清，扩展并覆盖 T23/T31/T41/T42/T62 中不足的验收面。进入任何后续开发前，必须先确认本批是否已拆到当前执行计划。

### Task 7.1 Add DiffSource adapter contract and source resolution artifacts

- task_id: T71
- status: done
- goal: 将 review 输入从 GitHub/本地 base 假设升级为 DiffSource adapter 合同
- priority: P0
- 验收标准：见 acceptance 字段。
- depends:
  - T11
  - T12
  - T23
- scope:
  - src/ai_sdlc/core/pr_review_models.py
  - src/ai_sdlc/core/pr_review_source.py
  - src/ai_sdlc/core/pr_review_pack.py
  - tests/unit/test_pr_review_models.py
  - tests/unit/test_pr_review_pack.py
  - tests/unit/test_pr_review_source.py
- acceptance:
  - 定义 DiffSourceDescriptor / SourceAdapterResolution 或等价模型，包含 source kind、adapter id、base/head、patch/scm metadata、access status、unavailable reason、blocker、next command。
  - P0 至少支持 local-git-range；patch file、staged/unstaged、SCM PR/MR 可作为 fixture 或 P1 adapter 合同保留，不得进入核心状态机硬编码。
  - review-pack.json 必须记录 diff_source、source_adapter、source_access_status；source-resolution.json 必须可由 schema validation 校验。
  - source 不唯一、不可访问、patch 缺失、SCM adapter 缺失、公司内网凭据缺失或远端不可达时 fail-closed 到 needs_user/blocked，并输出 plain-language blocker。
  - 核心 review pack、loop state、close-check 不得依赖 GitHub PR id 字段。
- verify:
  - uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py -q
- notes:
  - 这是本轮最高优先级补齐项；不能只通过 README 说明规避实现合同。

### Task 7.2 Fix model resolution to current-first and explicit fail-closed

- task_id: T72
- status: done
- goal: 修订 local-agent 模型解析合同
- priority: P0
- 验收标准：见 acceptance 字段。
- depends:
  - T31
- scope:
  - src/ai_sdlc/core/pr_review_provider.py
  - src/ai_sdlc/core/loop_policy.py
  - tests/unit/test_pr_review_provider.py
  - tests/unit/test_loop_policy.py
- acceptance:
  - 未传 --model 或 --model current 时，默认解析当前会话/当前 CLI agent 已连接模型。
  - 用户显式指定非 current 模型时，必须验证该模型服务已连接且可用。
  - 显式模型不可用时不得 fallback 到 current、policy default、provider default 或 mock-reviewer。
  - model-resolution.json 必须记录 provider id、provider mode、model selector、resolved model、resolution source、status、code egress、unavailable reason、blocker。
  - unavailable reason 至少覆盖未连接、provider command 不存在、鉴权缺失、网络不可达、超时、rate limit、上下文过大、输出 schema 非法、policy 禁止。
- verify:
  - uv run pytest tests/unit/test_pr_review_provider.py tests/unit/test_loop_policy.py -q
- notes:
  - 旧 T31 中的模型优先级已被本任务覆盖，不再作为当前需求真值。

### Task 7.3 Upgrade doctor/start UX for novice and professional users

- task_id: T73
- status: done
- goal: 让小白用户看懂 source/model/provider 问题，同时保留专业用户的结构化控制
- priority: P0
- 验收标准：见 acceptance 字段。
- depends:
  - T71
  - T72
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - src/ai_sdlc/cli/pr_review_cmd.py
  - tests/unit/test_pr_review_service.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - doctor/start human 输出必须包含 Result / Next / diff source / provider / model selector / resolved model / code egress / artifact path。
  - 未指定 source 时，唯一安全 source 给推荐命令；多个候选 source 时解释差异并要求选择。
  - 当前模型不可解析、显式模型不可用、provider 未配置、source 不可访问时，必须给出普通用户能复制的下一步命令和 mock-reviewer dry-run 预演命令。
  - --json 输出必须保留 source adapter、model resolution、policy decision、blocker、next command 字段。
  - 输出不得要求普通用户理解 merge-base、SCM API、provider internals 或 artifact schema 才能继续。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q
- notes:
  - 该任务优先验证 CLI 可理解性，不引入自动修复或 inline comment。

### Task 7.4 Align docs and verify constraints for adapter/model boundaries

- task_id: T74
- status: done
- goal: 对齐用户文档、约束检查和发布面，防止再次把需求误解成 GitHub/CI/固定模型流程
- priority: P0
- 验收标准：见 acceptance 字段。
- depends:
  - T71
  - T72
  - T73
- scope:
  - README.md
  - docs/pull-request-checklist.zh.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
  - tests/integration/test_cli_verify_constraints.py
  - specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md
- acceptance:
  - 文档明确本地 review agent 可以调用用户当前模型或显式选择的已连接模型；CI 不发起模型请求不等于禁止使用大模型。
  - 文档明确本地仓、公司内网仓、patch、GitHub/GitLab/Gitee/self-hosted SCM 都通过 DiffSource/SCM adapter 接入，不能要求 GitHub PR。
  - verify constraints 能检测“Codex 云端 PR review 替代本地 agent”“CI 发起模型请求”“远端 diff 写死 GitHub”“显式模型不可用静默 fallback”等违规 surface。
  - task-execution-log 记录本批修订、验证命令、残留风险和是否提交。
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q
  - uv run ai-sdlc verify constraints
- notes:
  - 这是实现后的文档/门禁收口任务；本轮用户要求先修订需求文档，不代表这些代码验收已经完成。

## 实现前硬性边界

1. 不得调用 Codex 云端 PR review。
2. 不得在 CI workflow 中加入 GPT、Claude、DeepSeek、GLM、Codex 或其他模型调用；模型调用只能由本地独立 review agent 发起。
3. P0 不允许 reviewer 修改代码。
4. 不得把远端 diff/PR 写死为 GitHub；所有输入源必须通过 DiffSource adapter 合同进入 review pack。
5. 显式模型不可用时必须 fail-closed，不得静默 fallback。
6. P0 不实现远端 PR inline comments。
7. 每个 batch 完成后必须更新 task-execution-log.md 和 handoff。

## Batch 8：P1 diff-source / attestation / history 扩展

### Task 8.1 Implement patch, staged, and unstaged DiffSource adapters

- task_id: T81
- status: done
- goal: 将 P1 的本地非分支输入源从合同升级为真实可用 adapter
- priority: P1
- 验收标准：见 acceptance 字段。
- depends:
  - T71
- scope:
  - src/ai_sdlc/core/pr_review_source.py
  - src/ai_sdlc/core/pr_review_pack.py
  - tests/unit/test_pr_review_source.py
  - tests/unit/test_pr_review_pack.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - `--diff-source patch --patch-file <path>` 可读取本地 patch 文件、计算 patch hash、解析 changed files，并生成 `diff.patch` / `changed-files.txt` / `review-pack.json`。
  - `--diff-source local-staged` 可读取 staged diff；无 staged diff 时 fail-closed 到 `needs_user`。
  - `--diff-source local-unstaged` 可读取 unstaged diff；无 unstaged diff 时 fail-closed 到 `needs_user`。
  - patch/staged/unstaged 不要求 GitHub PR id，不要求 CI 调模型，不读取实现 agent transcript。
- verify:
  - uv run pytest tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py tests/integration/test_cli_pr_review.py -q

### Task 8.2 Implement local review attestation

- task_id: T82
- status: done
- goal: 生成 CI 可只读检查的本地 review attestation
- priority: P1
- 验收标准：见 acceptance 字段。
- depends:
  - T53
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - src/ai_sdlc/cli/pr_review_cmd.py
  - src/ai_sdlc/core/pr_review_models.py
  - tests/unit/test_pr_review_models.py
  - tests/unit/test_pr_review_service.py
  - tests/integration/test_cli_pr_review.py
- acceptance:
  - 新增 `ai-sdlc pr-review attest`，只读当前 review-run/final report，写入 `.ai-sdlc/reviews/pr/latest-attestation.json`。
  - attestation 绑定 review id、loop id、head commit、verdict、unresolved blocker/required/advisory counts、artifact paths、generated_at。
  - head commit 不匹配、review 未 close、final report 缺失或 unresolved blocker 存在时 fail-closed。
  - 输出明确 CI 只能读取 attestation，不得发起模型请求。
- verify:
  - uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q

### Task 8.3 Preserve finding history mapping across rerun

- task_id: T83
- status: done
- goal: 降低 rerun 后 finding id 漂移导致的重复修复成本
- priority: P1
- 验收标准：见 acceptance 字段。
- depends:
  - T52
- scope:
  - src/ai_sdlc/core/pr_review_service.py
  - src/ai_sdlc/core/pr_review_models.py
  - tests/unit/test_pr_review_service.py
- acceptance:
  - rerun 后写入 `finding-history.json` 或等价 artifact，记录 previous/current finding signature 映射。
  - finding signature 至少包含 severity、file、line、claim/risk 的稳定摘要。
  - 历史 artifact 不改变 reviewer findings 原文，不替代人工 waiver。
- verify:
  - uv run pytest tests/unit/test_pr_review_service.py -q

### Task 8.4 Align P1 docs and constraints

- task_id: T84
- status: done
- goal: 对齐 P1 命令、adapter 和 attestation 文档/门禁
- priority: P1
- 验收标准：见 acceptance 字段。
- depends:
  - T81
  - T82
  - T83
- scope:
  - README.md
  - docs/pull-request-checklist.zh.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
  - tests/integration/test_cli_verify_constraints.py
  - specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md
- acceptance:
  - 文档展示 patch/staged/unstaged 和 `pr-review attest` 的小白路径与专业 JSON 路径。
  - verify constraints 覆盖 attestation 只读 CI、patch/staged/unstaged source adapter、finding-history artifact。
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q
  - uv run ai-sdlc verify constraints

## Batch 9：P2 enterprise contract and fail-closed surfaces

### Task 9.1 Record P2 enterprise boundaries without fake SCM writes

- task_id: T91
- status: done
- goal: 把 P2 能力边界落成可审计合同，防止伪实现或硬编码 GitHub
- priority: P2
- 验收标准：见 acceptance 字段。
- depends:
  - T81
  - T82
- scope:
  - specs/189-loop-engine-local-adversarial-pr-review/plan.md
  - specs/189-loop-engine-local-adversarial-pr-review/tasks.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
- acceptance:
  - 多 reviewer、组织 waiver、artifact 签名、远端 PR inline comments 均必须通过 adapter/policy contract 进入，未配置时 fail-closed。
  - 不得在无企业身份、SCM 写权限或签名密钥时伪造成功。
  - GitHub/GitLab/Gitee/self-hosted SCM 都只能作为 adapter，不得进入核心状态机。
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
