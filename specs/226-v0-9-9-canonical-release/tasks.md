# 任务分解：v0.9.9 Canonical Release

**编号**：`226-v0-9-9-canonical-release`
**来源**：`spec.md` + `plan.md`
**当前阶段**：formal baseline 已批准；尚未启动生产实现

## Checklist（供 close-check 读取）

- [x] T11 canonical formal baseline 已冻结。
- [x] T12 实施计划已由用户明确批准。
- [x] T21 聚合显式依赖闭包 readiness。
- [ ] T22 扩展既有 truth audit CLI。
- [ ] T23 接入 PR/tag 工作流门禁。
- [ ] T31 同步 v0.9.9 release truth。
- [ ] T32 完成终局本地验证与 truth 刷新。

## Batch 1：formal baseline

### Task 1.1 冻结唯一 canonical WI226

- task_id: T11
- status: done
- goal: 冻结 WI226 的显式发布范围、历史主线组成和 formal 五层证据，不启动生产实现。
- depends: none
- scope:
  - program-manifest.yaml
  - .ai-sdlc/project/config/project-state.yaml
  - specs/226-v0-9-9-canonical-release/
  - tests/integration/test_repo_program_manifest.py
- acceptance:
  - WI226 声明 `release_candidate` role 与 WI219、WI220、WI221、WI222、WI224、WI225 六个显式依赖。
  - Formal 记录 `v0.9.8@4f3e55c3`、初始远端主线锚点 `8f9df406`、18 个 first-parent carrier 和 PR #200 的 partial 边界。
  - inventory 期望只同步实际新增五层后的快照，不改变 release truth 或历史 blocker。
- verify:
  - uv run ai-sdlc program validate
  - uv run ai-sdlc program truth sync --execute --yes
  - uv run ai-sdlc verify constraints
  - uv run pytest tests/integration/test_repo_program_manifest.py -q
  - git diff --check

### Task 1.2 实施计划终审与用户批准

- task_id: T12
- status: done
- goal: 由用户审阅同一份 canonical 计划并明确批准进入 T21，不扩展设计或创建替代工作项。
- depends:
  - T11
- scope:
  - specs/226-v0-9-9-canonical-release/
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/work-items/226-v0-9-9-canonical-release/codex-handoff.md
- acceptance:
  - 用户已明确批准 brief 中的终局整改及后续受限实现计划。
  - 批准只激活 T21；T22、T23、T31、T32 仍保持 blocked，直到各自前置任务完成。
- verify:
  - 用户批准记录
  - uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T21 生产实现" --json

## Batch 2：release-candidate truth gate

### Task 2.1 TDD 聚合显式依赖闭包 readiness

- task_id: T21
- status: done
- goal: 复用现有逐规格 readiness，为 WI226 显式依赖闭包建立唯一、可重复的 release-candidate 判定。
- depends:
  - T12
- scope:
  - src/ai_sdlc/core/program_service.py
  - tests/unit/test_program_service.py
- acceptance:
  - 全局 truth blocked 且闭包内均 ready 时聚合成功。
  - 相关 blocker、snapshot stale、角色缺失和传递/重复依赖均按既有 readiness 合同处理。
  - 不读取 Git range、提交消息或 execution log，不新增结果类型、schema 或 ledger。
- verify:
  - uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'
  - uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'

### Task 2.2 TDD 扩展既有 truth audit CLI

- task_id: T22
- status: todo
- goal: 在既有 `program truth audit` 中增加可选 WI 审计入口，同时保持无参数路径兼容。
- depends:
  - T21
- scope:
  - src/ai_sdlc/cli/program_cmd.py
  - tests/integration/test_cli_program.py
- acceptance:
  - `--wi` 审计输出根 WI、闭包、state、detail 和去重后的 next actions。
  - 无 `--wi` 时既有输出和退出码不变；加载或参数错误维持退出码 2。
- verify:
  - uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
  - uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit'

### Task 2.3 接入不可跳过的 PR/tag 工作流门禁

- task_id: T23
- status: blocked
- goal: 让 PR Checks 与 Release Build 在同一命令、同一失败语义下消费 WI226 readiness。
- depends:
  - T22
- scope:
  - .github/workflows/pr-checks.yml
  - .github/workflows/release-build.yml
  - tests/integration/test_github_workflows.py
- acceptance:
  - 两个工作流均运行 `uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release`。
  - Release Build 在 build、attestation 与 upload 之前运行该门禁，无 fallback、continue-on-error 或条件跳过。
- verify:
  - uv run pytest tests/integration/test_github_workflows.py -q -k 'release_candidate_truth or release_build'
  - uv run pytest tests/integration/test_github_workflows.py -q

## Batch 3：v0.9.9 release truth

### Task 3.1 同步版本、指南、资产名和发布说明

- task_id: T31
- status: blocked
- goal: 只同步当前 v0.9.9 入口与真实发布说明，保留明确的 v0.9.8 历史叙述。
- depends:
  - T23
- scope:
  - pyproject.toml
  - uv.lock
  - src/ai_sdlc/__init__.py
  - src/ai_sdlc/core/verify_constraints.py
  - README.md
  - USER_GUIDE.zh-CN.md
  - packaging/offline/
  - docs/pull-request-checklist.zh.md
  - docs/框架自迭代开发与发布约定.md
  - docs/releases/v0.9.9.md
  - program-manifest.yaml
  - tests/unit/test_verify_constraints.py
  - tests/integration/test_github_workflows.py
  - tests/integration/test_offline_bundle_scripts.py
  - tests/integration/test_repo_program_manifest.py
- acceptance:
  - 创建 `docs/releases/v0.9.9.md` 的同一变更批次，才更新 `program-manifest.yaml` 的 `release_doc/release` source_registry 和 `tests/integration/test_repo_program_manifest.py` 的 `range(0, 10)` 与 inventory。
  - 在 release note 实际存在前，不得提前登记它；登记后预期 inventory 为 1180/1180 mapped、unmapped 0、missing 6、release layer 45。
  - 所有当前版本入口与一致性合同均指向 `0.9.9`，但历史比较叙述不被误改。
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q
  - uv run ai-sdlc verify constraints
  - uv run pytest tests/integration/test_repo_program_manifest.py -q

### Task 3.2 完成终局本地验证和 truth 刷新

- task_id: T32
- status: blocked
- goal: 在不改写全局历史 blocker 的前提下完成本地交付证据，并刷新 WI226 的真实 snapshot。
- depends:
  - T31
- scope:
  - specs/226-v0-9-9-canonical-release/
  - program-manifest.yaml
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/work-items/226-v0-9-9-canonical-release/codex-handoff.md
- acceptance:
  - Ruff、focused tests、全量 pytest、constraints 通过；全局 truth 仍保留 16 blocker，WI226 scoped audit ready。
  - task-execution-log 只记录实际发生的验证结果，不预写 merge 或 release 成功。
- verify:
  - uv run ruff check src tests
  - uv run pytest -q
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program truth sync --execute --yes
  - uv run ai-sdlc program truth audit
  - uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release
  - git diff --check

## 固定止损规则

- 生产代码净新增 `>150` 行、实施 `>1` 人日、需要新 schema/ledger/waiver 或第三轮代码修复：立即 No-Go。
- API/网络观察失败不算代码修复轮次；在同一精确 HEAD 重试。
- 范围外 finding 进入既有 backlog，不创建 WI226 的例外、替代设计或第二 PR。

## Post-release handoff

T32 结束 repository executable/checklist 工作。之后仅在 GitHub 留存 release evidence：同一精确 HEAD 的独立 review、required checks、merge 与 `origin/main` 核验、tag/main SHA 一致性、三平台资产、SHA256 checksum、attestation、release smoke 和 12-route 自然回执。不得为回写这些外部结果创建第二个 closeout PR。
