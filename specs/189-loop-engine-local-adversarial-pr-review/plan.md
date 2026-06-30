# 实施计划：AI-SDLC Loop Engine and Local Adversarial PR Review

**编号**：`189-loop-engine-local-adversarial-pr-review`  
**日期**：2026-06-29  
**规格**：`specs/189-loop-engine-local-adversarial-pr-review/spec.md`  
**状态**：已随 2026-06-30 需求澄清修订；后续开发必须先按本计划重新拆解/补齐 `tasks.md`

## 概述

本计划把已冻结 PRD 落成 AI-SDLC 的 P0 本地对抗 PR Review 能力。实现重点是：新增 `ai-sdlc pr-review` 命令组、统一 loop/review artifact 模型、DiffSource adapter 合同、review pack 生成、schema validation、policy profile、`mock-reviewer`、`local-agent` provider/model runner 合同、beginner-friendly `doctor` 和 close/check 集成。

P0 不实现远端 SCM inline comment、多 reviewer 投票、artifact 签名，也不接入 Codex 云端 PR review。模型调用由用户本地开发环境中的独立 review agent 发起，默认使用当前会话/当前 CLI agent 已连接模型，也可显式选择 GPT、Claude、DeepSeek、GLM 或其他已连接模型；CI 只能读取本地 artifact 或 attestation，不能发起模型请求。任何远端 PR/MR、公司内网仓、本地 patch、本地 staged/unstaged diff 都必须通过 `DiffSourceDescriptor` 进入核心合同，不得写死 GitHub。

P2 的多 reviewer、组织 waiver、artifact 签名和远端 PR inline comments 同步必须通过显式 adapter、企业身份、SCM 写权限和签名密钥配置进入；缺失任一前置条件时必须 fail-closed，不得伪造评论写回、签名或组织审批成功。

## 技术背景

**语言/版本**：Python 3.11+  
**CLI**：Typer + Rich，新增 `src/ai_sdlc/cli/pr_review_cmd.py` 并在主 CLI 注册 `pr-review`。  
**数据模型**：Pydantic 或 dataclass + YAML/JSON serialization，优先遵循仓库现有 `core/` 模块风格。  
**存储**：`.ai-sdlc/loops/local-pr-review/<loop-id>/` 与 `.ai-sdlc/reviews/pr/<review-id>/`。  
**Diff Source 读取**：P0 通过本地 `local-git-range` adapter 使用现有 `src/ai_sdlc/branch/git_client.py` 或新增小型 Git helper 只读读取 base/head/diff；P1 通过同一 source adapter 合同接入 staged/unstaged、patch file、GitHub/GitLab/Gitee/self-hosted SCM 或公司内网 SCM。
**测试**：unit tests 覆盖模型/schema/policy/redaction/provider；integration tests 覆盖 CLI beginner path 和 artifact 生成。  
**目标平台**：macOS/Linux/Windows；Windows 命令发现和输出必须遵守已有 CLI 兼容策略。  
**约束**：模型调用只由本地独立 review agent 发起，不由 CI 发起；不使用 Codex 云端 PR review；reviewer P0 不改代码；核心 review 状态机不得依赖 GitHub PR、某个模型品牌或某个本地目录布局。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MVP 优先，范围严控 | P0 只做 `local-git-range` diff source、artifact、mock/local-agent provider-model 合同、doctor、schema/policy；staged/unstaged、patch、远端 SCM adapter、inline comment、多 reviewer、签名放 P1/P2。 |
| 关键路径必须可验证 | 每个 artifact schema、policy 阻断、provider runner 失败、secret/redaction、close verdict 都有 unit/integration tests。 |
| 改动声明范围、验证与回退 | 任务按模型、artifact、CLI、provider、close-check、docs 分批；每批可独立 git revert。 |
| 状态落盘，上下文外化 | LoopRun/ReviewRun/ReviewPack/Findings/Resolution/FinalReport 全部写入 `.ai-sdlc/`。 |
| 产品代码与开发框架隔离 | 只改 `src/ai_sdlc/`、`tests/`、`docs/`、`specs/189`，不混入本地运行态外部文件。 |

## 模块设计

### 模块 A：Loop / Review 数据模型

新增建议文件：

```text
src/ai_sdlc/core/loop_models.py
src/ai_sdlc/core/pr_review_models.py
```

职责：

1. 定义 `LoopRun`、`LoopRound`、`ReviewRun`、`ReviewPack`、`ReviewFinding`、`FindingResolution`、`LoopPolicyProfile`、`ProviderRunnerInvocation`、`SchemaValidationReport`。
2. 所有长期 artifact 必须有 `schema_version`、`artifact_kind`、`created_by`、`created_at`、`ai_sdlc_version`。
3. 提供 `validate_*` helper，缺字段、不兼容 version、非法 enum 直接返回 blocker。

### 模块 B：Artifact Store 与 Schema Validation

新增建议文件：

```text
src/ai_sdlc/core/loop_artifacts.py
src/ai_sdlc/core/pr_review_schema.py
```

职责：

1. 创建 `.ai-sdlc/loops/local-pr-review/<loop-id>/`。
2. 创建 `.ai-sdlc/reviews/pr/<review-id>/`。
3. 原子写入 `review-pack.json`、`findings.json`、`resolution.yaml`、`schema-validation.json`、`final-report.md`。
4. 支持 read-only status 恢复。
5. schema validation 失败时 fail-closed。

### 模块 C：Policy Profile

新增建议文件：

```text
src/ai_sdlc/core/loop_policy.py
```

建议配置路径：

```text
.ai-sdlc/project/config/loop-policy.yaml
```

P0 默认策略：

1. 未配置时使用 safe default。
2. 默认 provider 为 `local-agent`，默认 model selector 为 `current`；远程模型服务代码外发必须明确披露，是否需要确认由 policy 决定。
3. `max_rounds` 默认 2。
4. default close mode 为 strict：unresolved `BLOCKER` 或 `REQUIRED` 均阻断 clean close。
5. redaction strictness 默认 fail-closed for high-risk secret。

### 模块 D：Diff Source Adapter 与 Review Pack Builder

新增建议文件：

```text
src/ai_sdlc/core/pr_review_source.py
src/ai_sdlc/core/pr_review_pack.py
```

职责：

1. 解析 `DiffSourceDescriptor`；P0 支持 `local-git-range`，P1 通过同一合同扩展 staged/unstaged、patch file、SCM PR/MR、公司内网 adapter。
2. 解析 repo root、base ref、head ref、base/head commit、patch hash 或 SCM source metadata，并记录 source access status。
3. 生成 `diff.patch` 与 `changed-files.txt`；当 source 不唯一、不可访问或需要凭据时进入 `needs_user` / `blocked`。
4. 汇总 `diff_summary`、`work_item_refs`、formal docs bounded summary、`test_results_refs`、`policy_refs`、policy decisions。
5. 执行 secret/path/binary/large/generated file 预检。
6. 生成 `redaction-report.json` 和 diff coverage。
7. 不读取 implementation agent chat transcript；handoff 只能作为路径状态引用，不进入主观摘要。

### 模块 E：Provider Runner

新增建议文件：

```text
src/ai_sdlc/core/pr_review_provider.py
```

P0 provider/model：

1. `mock-reviewer`：测试用 provider，不访问网络，不调用模型，可按 fixture 输出 findings。
2. `local-agent`：本地 reviewer runner 合同。P0 必须支持用户配置的本地命令或等价 launcher；未显式选择模型时默认解析当前会话/当前 CLI agent 已连接模型，用户也可以显式选择其他已连接模型服务。输入为 review pack path、model selector、resolved model 和 allowlist，输出为 findings path；focused tests 必须覆盖“已配置本地命令可运行并生成合法 findings”“未配置进入 `needs_user`”“当前模型不可解析进入 `needs_user`”“显式模型不可用 fail-closed”“显式 model selector 被写入 invocation artifact”五条路径。`codex-local` 只可作为兼容 alias 或具体 adapter，不得作为唯一真实 provider。

Model resolution 规则：

1. 未传 `--model` 或 `--model current` 时，优先解析当前会话/当前 CLI agent 已连接模型；解析失败必须进入 `needs_user`，并给出配置/重试/显式选择模型的下一步。
2. 显式 CLI `--model <value>` 且 value 不是 `current` 时，必须验证该模型服务已连接且可用；失败时 fail-closed，不得 fallback 到 current 或 mock。
3. `.ai-sdlc/project/config/loop-policy.yaml` 与 provider config 可以提供默认模型候选，但只能在未显式指定模型且当前模型不可解析时作为有披露的候选或推荐命令，不能静默替换用户选择。
4. `ModelResolution` 必须记录 `resolution_source`、`status`、`blocker`、`code_egress`、`provider_id`、`provider_mode`、`model_selector`、`resolved_model`。
5. 模型不可用原因必须结构化区分：未连接、provider command 不存在、鉴权缺失、网络不可达、超时、rate limit、上下文过大、输出 schema 非法、policy 禁止。

标准退出码：

| 退出码 | 语义 |
|--------|------|
| `0` | findings 生成成功且 verdict clean 或无 fatal runner error |
| `10` | findings 生成成功且 changes required |
| `20` | reviewer blocked |
| 其他非零 | runner failure，loop blocked |

### 模块 F：PR Review Service

新增建议文件：

```text
src/ai_sdlc/core/pr_review_service.py
```

职责：

1. `doctor`：只读检查 init、diff source/Git/base、provider/model/policy/redaction/artifact writability。
2. `start`：解析 diff source，生成 run、review pack、schema validation，按 provider 启动 reviewer。
3. `status`：展示 current run、findings、resolution、next command。
4. `fix`：P0 只生成 `fix-plan.md`，不改代码。
5. `rerun`：检查 scope drift，重新生成 review pack 和 reviewer invocation。
6. `close`：根据 `fully_clean / risk_accepted / blocked` 规则生成 final report。
7. `doctor` 与 `start --dry-run` 必须保持只读预演语义：不得创建 review run、不得写 `.ai-sdlc/reviews/pr/<review-id>/`，也不得改写 current review 指针。

### 模块 G：CLI

新增建议文件：

```text
src/ai_sdlc/cli/pr_review_cmd.py
```

并在：

```text
src/ai_sdlc/cli/main.py
src/ai_sdlc/__main__.py
src/ai_sdlc/cli/command_names.py
```

注册 `pr-review`。

P0 命令：

```bash
ai-sdlc pr-review doctor
ai-sdlc pr-review start [--base <ref>] [--provider <provider>] [--model <selector>] [--dry-run] [--json]
ai-sdlc pr-review status [--json]
ai-sdlc pr-review fix [--max-rounds 2] [--dry-run] [--json]
ai-sdlc pr-review rerun [--json]
ai-sdlc pr-review close [--require-no-blockers] [--json]
```

Human 输出必须包含：

1. 当前结果 / Result。
2. 下一步 / Next。
3. plain-language blocker。
4. 可复制下一条命令。
5. artifact path。
6. diff source、provider/model 与代码外发提示。

### 模块 H：Close / Handoff / Verify 集成

改动建议：

```text
src/ai_sdlc/core/close_check.py
src/ai_sdlc/core/handoff.py
src/ai_sdlc/core/verify_constraints.py
```

职责：

1. `close-check` 可读取 PR review final report。
2. 区分 `fully_clean`、`risk_accepted`、`blocked`。
3. `handoff` 记录 current review id、unresolved counts、beginner-facing next command。
4. `verify constraints` 覆盖 schema surface、云端 PR review 禁用文档/代码 surface、CI 不发起模型请求文档 surface。

## 工作流设计

### 工作流 1：小白本地 PR Review

```text
ai-sdlc init .
ai-sdlc pr-review doctor
ai-sdlc pr-review start
ai-sdlc pr-review status
```

关键行为：

1. 自动检测安全 diff source；P0 优先 `local-git-range`，后续可检测 staged/unstaged、patch、SCM PR/MR。
2. source 唯一时给推荐命令；source 不唯一、不可访问或需要凭据时，用普通语言解释差异并给候选命令。
3. 无 provider 时提示配置或使用 `mock-reviewer --dry-run`。
4. 当前模型不可解析或显式模型不可用时，必须指出模型服务不可用原因，不得静默换模型。
5. 有 high-risk secret 时停止在 `needs_user`。
6. 每次输出都给 Result/Next。

### 工作流 2：有 findings 的修复闭环

```text
ai-sdlc pr-review fix --max-rounds 2
# implementation agent/user 修复
ai-sdlc pr-review rerun
ai-sdlc pr-review close
```

关键行为：

1. `fix` 只生成 fix plan。
2. rerun 重新生成 review pack。
3. scope drift 进入 `needs_user`。
4. unresolved `BLOCKER` / `REQUIRED` 阻断 clean close。

### 工作流 3：企业策略阻断代码外发

```text
ai-sdlc pr-review doctor
ai-sdlc pr-review start --provider local-agent --model current --provider-command "my-local-reviewer"
```

若 policy profile 禁止代码外发到远程模型服务，而当前 provider/model 会外发代码，则启动必须被阻断，输出 plain-language blocker 和下一步命令。若 policy 允许，GPT、Claude、DeepSeek、GLM 等模型都可以由本地独立 agent runner 使用。

## 数据与 Artifact 合同

### `review-pack.json`

必须包含：

```text
schema_version
artifact_kind
created_by
created_at
ai_sdlc_version
review_id
loop_id
diff_source
source_adapter
source_access_status
repo_root
base_ref
head_ref
base_commit
head_commit
changed_files
diff_summary
diff_coverage
work_item_refs
test_results_refs
policy_refs
policy_profile_id
policy_decisions
provider_mode
provider_id
model_selector
model_resolution_status
model_resolution_source
resolved_model
model_unavailable_reason
code_egress
redaction_report_path
reviewer_allowlist
```

### `source-resolution.json`

必须包含：

```text
schema_version
artifact_kind
source_kind
adapter_id
source_id
repo_root
base_ref
head_ref
patch_file
scm_host_type
access_status
requires_user_choice
unavailable_reason
blocker
next_command
```

### `model-resolution.json`

必须包含：

```text
schema_version
artifact_kind
provider_id
provider_mode
model_selector
resolved_model
resolution_source
status
unavailable_reason
code_egress
blocker
```

### `findings.json`

必须包含：

```text
schema_version
artifact_kind
review_id
verdict
findings[]
```

每个 finding 必须包含：

```text
id
severity
file
line
claim
evidence
risk
suggested_fix
confidence
resolution
```

### `final-report.md`

必须包含：

1. Verdict：`fully_clean` / `risk_accepted` / `blocked`。
2. Review id、head commit、base commit。
3. unresolved counts。
4. fixed / waived / not_applicable findings。
5. redaction / omission summary。
6. verification evidence。
7. next action。

## 实施顺序

1. Batch 1：模型、schema validation、artifact store。
2. Batch 2：policy profile、redaction/omission、review pack builder。
3. Batch 3：mock-reviewer 与 provider runner 合同。
4. Batch 4：CLI doctor/start/status。
5. Batch 5：fix/rerun/close 状态机。
6. Batch 6：close-check/handoff/verify/docs 集成。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Artifact schema | unit tests for model validation | malformed fixture integration tests |
| Policy blocks remote code egress | unit + CLI integration | doc surface check |
| Secret/redaction fail-closed | unit tests with fixtures | CLI doctor fixture |
| Diff source adapter contract | unit tests for local-git-range/patch/scm fixture descriptors | CLI doctor/start dry-run snapshot |
| Source unavailable fail-closed | unit + CLI fixture for missing patch/auth/adapter/network | Result/Next output snapshot |
| Base/source detection beginner UX | CLI integration | command output snapshot |
| Model unavailable fail-closed | provider runner fixture matrix | human/JSON unavailable reason snapshot |
| Provider runner failure | unit + integration mock runner | exit-code matrix |
| Configured `local-agent` runner | unit + integration fixture command | unconfigured `needs_user` path |
| Fix plan no code writes | integration test asserts no product diff | dry-run output |
| Close verdict | unit + close-check integration | final report snapshot |
| Doctor/dry-run read-only boundary | integration asserts no review artifact/current pointer writes | before/after tree snapshot |
| CI does not initiate model calls | verify constraints surface | workflow grep tests if workflows change |

## 开放设计决策

| 问题 | 决策 |
|------|------|
| `loop-policy.yaml` 是否独立 | P0 独立放在 `.ai-sdlc/project/config/loop-policy.yaml`，避免污染现有 project config。 |
| Schema 形式 | P0 使用 Pydantic/dataclass validation + fixture tests；P1 再导出 JSON Schema。 |
| `local-agent` host/model 集成 | P0 做 configurable local command runner 合同；未指定模型时默认当前会话/当前 CLI agent 已连接模型；显式 model selector 必须验证可用性，失败时 fail-closed；Codex/Claude/DeepSeek/GLM 等具体 host 深集成或 alias 另起 P1/P2。 |
| 远端 PR/MR diff 接入 | P0 核心只认 `DiffSourceDescriptor`；GitHub/GitLab/Gitee/self-hosted SCM、公司内网 SCM、patch file 都是 adapter，不得把 GitHub PR id 写进核心模型或状态机。 |
| 自动修复 | P0 不自动改代码；只生成 fix plan。 |

## 回退方式

每个 batch 应能独立 revert。P0 新命令默认 opt-in，不应影响现有 `init/run/stage/workitem/program` 路径。若出现风险，可先隐藏 CLI 注册或让 `pr-review` 返回 experimental guidance，不破坏旧用户流程。
