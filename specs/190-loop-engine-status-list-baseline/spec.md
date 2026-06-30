# PRD：Loop Engine Status/List Baseline

**功能编号**：`190-loop-engine-status-list-baseline`
**创建日期**：2026-06-29
**状态**：已拆解，等待执行
**上游来源**：`189-loop-engine-local-adversarial-pr-review` P1：`ai-sdlc loop status/list`
**目标读者**：Codex 开发 agent、AI-SDLC 框架维护者、普通项目操作者

## 1. 背景

WI-189 已完成 P0 本地对抗 PR Review Loop：`ai-sdlc pr-review` 可以生成本地 review pack、调用 mock/local-agent provider、落盘 `review-run.json`、`findings.json`、`resolution.yaml` 和 final report，并支持 `pr-review status` 恢复当前 review。

但当前状态面仍局限在 `pr-review` 命令组。随着 Loop Engine 继续扩展到 requirement、design-contract、implementation、frontend-evidence 和 local-pr-review 五类 loop，用户需要一个统一的只读入口来回答三个问题：

1. 当前正在推进哪个 loop？
2. 它处于什么状态，下一步该执行什么？
3. 历史 loop run 和 artifact 在哪里，是否存在损坏或不一致？

WI-190 的目标是新增 `ai-sdlc loop status/list` 的 P1 基线。第一版只读取已存在的 local PR review artifact，不新增模型调用，不修改代码，不执行修复，不替代 `pr-review` 的专用命令。

## 2. 产品目标

### 2.1 总目标

为 AI-SDLC Loop Engine 提供统一、只读、可恢复、可机器消费的状态查询入口，让普通用户和开发 agent 不必知道底层 artifact 布局，也能看懂当前结果、下一步和历史 run 列表。

### 2.2 质量目标

1. 降低使用成本：普通用户可以通过 `ai-sdlc loop status` 看懂当前 loop，而不是记住每类 loop 的内部 artifact。
2. 提升恢复能力：长任务中断后，统一入口能指向当前 run、artifact、unresolved counts 和下一条命令。
3. 提升审计能力：`loop list --json` 能给自动化工具读取历史 loop run 列表。
4. 保持边界清晰：status/list 只读，不发起模型请求，不启动 reviewer，不改写 `.ai-sdlc/` 状态。

## 3. 范围

### 3.1 覆盖范围

1. 新增 `ai-sdlc loop` 命令组。
2. 新增 `ai-sdlc loop status [--json]`，默认展示当前 local PR review loop 的摘要。
3. 新增 `ai-sdlc loop list [--json] [--type local-pr-review]`，列出本地仓库已落盘的 local PR review runs。
4. 复用 WI-189 的 `ReviewRun`、`ReviewPack`、`ReviewFindings`、`LoopStatus`、`LoopType` schema。
5. 对缺失、损坏、schema 不兼容的 artifact 给出 plain-language blocker 和下一步。
6. 保证 `loop status/list` 是严格只读命令，不触发 adapter 写入、不调用模型、不生成新的 review run。

### 3.2 明确不覆盖

1. 不实现 requirement/design/frontend/implementation loop 的专用执行逻辑。
2. 不新增模型调用，不调用 Codex 云端 PR review，不要求 CI 发起模型请求。
3. 不读取 GitHub/GitLab 远端 PR diff。
4. 不生成 fix plan，不修改代码，不自动 rerun review。
5. 不实现 attestation、artifact 签名、历史 finding 去重或跨仓聚合。
6. 不把 `loop list` 当成合规审计的强证明；它只是本地 artifact 的只读索引。

## 4. 用户场景与测试

### 用户故事 1 - 查看当前 loop 状态（优先级：P0）

作为普通 AI-SDLC 用户，我希望执行 `ai-sdlc loop status` 就能看到当前 loop 的类型、状态、review id、未解决问题数量、artifact 路径和下一步命令，以便中断后能继续工作。

**优先级说明**：这是 Loop Engine 横向扩展的最小入口，直接承接 WI-189 P1，且对用户恢复长任务最有价值。

**独立测试**：在 fixture 仓库中先通过 `pr-review start --provider mock-reviewer` 生成当前 review，再执行 `ai-sdlc loop status --json`，断言输出包含 `loop_type=local-pr-review`、`review_id`、`status`、`verdict`、unresolved counts、artifact paths 和 `next_action`。

**验收场景**：

1. **Given** 当前仓库存在 `.ai-sdlc/reviews/pr/current-review.json` 且指向合法 `review-run.json`，**When** 用户执行 `ai-sdlc loop status`，**Then** CLI 必须展示 Result、Next、loop type、review id、status、verdict、unresolved counts 和 artifact path。
2. **Given** 当前 review 的状态为 `needs_fix`，**When** 用户执行 `ai-sdlc loop status --json`，**Then** JSON 必须包含下一步 `ai-sdlc pr-review fix` 或等价的 persisted next action。
3. **Given** 当前没有任何 review run，**When** 用户执行 `ai-sdlc loop status`，**Then** 系统必须输出 no current loop，并建议 `ai-sdlc pr-review start`，不得输出 traceback。

### 用户故事 2 - 列出历史 loop runs（优先级：P0）

作为框架维护者或高级用户，我希望执行 `ai-sdlc loop list` 查看本地所有 local PR review loop runs，以便确认历史 run、当前 run 和 artifact 位置。

**优先级说明**：`status` 只能回答当前状态，`list` 是 Loop Engine 审计和恢复的最小索引。

**独立测试**：构造两个 review run 目录和 current pointer，执行 `ai-sdlc loop list --json`，断言返回两个条目、当前条目标记 `is_current=true`，并按 `updated_at` 或稳定 fallback 排序。

**验收场景**：

1. **Given** `.ai-sdlc/reviews/pr/` 下存在多个 `review-run.json`，**When** 用户执行 `ai-sdlc loop list`，**Then** 系统必须列出每个 run 的 loop type、review id、status、verdict、updated_at、head commit 短哈希和 next action。
2. **Given** 用户执行 `ai-sdlc loop list --json`，**When** 自动化工具读取输出，**Then** JSON 必须包含稳定的 `items[]` 数组和 `current_loop_id/current_review_id` 字段。
3. **Given** 某个历史 run artifact 损坏，**When** 执行 list，**Then** 系统必须把该条目标记为 `blocked` 或 `malformed` 摘要，不得因为一个坏 artifact 隐藏其他合法 runs。

### 用户故事 3 - 只读和防副作用（优先级：P0）

作为企业用户，我希望 `loop status/list` 只是本地只读查询，不会启动模型、修改 `.ai-sdlc/`、触发 adapter 写入或改变 current review pointer，以便安全地在排查和审计时使用。

**优先级说明**：Loop status/list 是高频查询命令，一旦带副作用会破坏用户信任，也会污染框架状态。

**独立测试**：在包含 current review 的 fixture 仓库中记录 `.ai-sdlc/` 文件快照，分别执行 `loop status`、`loop status --json`、`loop list`、`loop list --json`，断言文件内容和 mtime 不发生语义性变化，且 provider runner 未被调用。

**验收场景**：

1. **Given** 当前仓库有合法 review run，**When** 用户执行 `ai-sdlc loop status`，**Then** 系统不得创建新 run、不得写 current pointer、不得调用 provider command。
2. **Given** 当前命令是 `loop`，**When** CLI global callback 运行，**Then** 不得触发 IDE adapter 写入。
3. **Given** 用户在 CI 中只读执行 `ai-sdlc loop list --json`，**When** 输出历史 runs，**Then** 命令不得发起任何模型请求。

### 用户故事 4 - 面向未来 loop 类型的统一外壳（优先级：P1）

作为 AI-SDLC 框架维护者，我希望 `loop status/list` 的输出结构能容纳未来 requirement、design-contract、implementation 和 frontend-evidence loop，以便后续扩展不破坏已经集成的工具。

**优先级说明**：本 WI 不落地其他 loop 的执行逻辑，但应避免把输出结构写死成 `pr-review` 专属格式。

**独立测试**：单元测试中构造不同 `loop_type` 的 summary 对象，断言 JSON schema 字段仍包含通用 `loop_id/type/status/next_action/artifacts`，local PR review 扩展字段位于可选子结构中。

**验收场景**：

1. **Given** status/list 输出 local PR review，**When** 用户读取 JSON，**Then** 通用字段不得依赖 `review_id` 才能解释状态。
2. **Given** 未来新增 frontend evidence adapter，**When** 复用 summary 输出模型，**Then** 不需要破坏 `loop list --json` 的顶层字段。

## 5. 边界情况

1. `.ai-sdlc` 不存在：输出未初始化 blocker 和 `ai-sdlc init .`。
2. `current-review.json` 缺失：输出 no current loop 和 `ai-sdlc pr-review start`。
3. current pointer 不是 JSON object：blocked，提示 rerun `pr-review start`。
4. pointer 指向的 `review-run.json` 不存在：blocked，提示 rerun `pr-review start`。
5. `review-run.json` schema 不兼容：blocked，输出 artifact path 和 schema 错误摘要。
6. `review-run.json` 合法但 `findings_path` 缺失：status/list 仍展示 run 摘要，并把 findings 标记为 missing。
7. 多个历史 run 中部分损坏：list 继续展示其他合法 runs，并对损坏条目单独标记。
8. Windows 路径：输出使用 repo-relative path 或可解析 path，不因反斜杠导致 JSON 不稳定。

## 6. 需求

### 功能需求

- **FR-190-001**：系统必须新增 `ai-sdlc loop` 命令组，并注册 `status` 与 `list` 子命令。
- **FR-190-002**：`ai-sdlc loop status` 必须读取当前 local PR review pointer，并输出统一 loop summary。
- **FR-190-003**：`ai-sdlc loop status --json` 必须输出稳定 JSON object，不混入 Rich 文本。
- **FR-190-004**：`ai-sdlc loop list` 必须扫描 `.ai-sdlc/reviews/pr/*/review-run.json` 并输出本地历史 local PR review runs。
- **FR-190-005**：`ai-sdlc loop list --json` 必须输出稳定 `items[]`，每个 item 至少包含 `loop_id`、`loop_type`、`status`、`review_id`、`is_current`、`updated_at`、`next_action`、artifact paths。
- **FR-190-006**：status/list 必须复用 WI-189 的 Pydantic schema，不得用不受控字符串拼接解析 artifact。
- **FR-190-007**：status/list 必须对 malformed/missing artifact fail-readable：返回 blocked/malformed 摘要和下一步，但不得隐藏其他合法 list items。
- **FR-190-008**：human 输出必须包含 Result 和 Next；存在 blocker 时必须包含 plain-language blocker。
- **FR-190-009**：`loop status/list` 必须严格只读，不得创建或修改 `.ai-sdlc/loops`、`.ai-sdlc/reviews`、current pointer、review pack、findings、resolution 或 final report。
- **FR-190-010**：`loop` 命令必须加入 CLI read-only bypass，避免 global adapter hook 对 status/list 产生写入副作用。
- **FR-190-011**：status/list 不得调用 provider command、local-agent、mock-reviewer、Codex 云端 PR review 或任何模型服务。
- **FR-190-012**：status/list 的输出模型必须保留通用 loop 字段，使未来 loop type 可以扩展而不破坏现有 JSON 顶层结构。
- **FR-190-013**：command discovery tests 必须包含 `ai-sdlc loop status` 和 `ai-sdlc loop list`。
- **FR-190-014**：`python -m ai_sdlc --help` fallback 必须包含 `loop`。

### 关键实体

- **LoopSummary**：当前或历史 loop 的通用只读摘要，包含 `loop_id`、`loop_type`、`status`、`next_action`、`updated_at`、`artifacts`。
- **LocalPRReviewLoopSummary**：LoopSummary 的 local PR review 扩展，包含 `review_id`、`verdict`、unresolved counts、base/head refs、base/head commits、provider/model 摘要。
- **LoopStatusResult**：`loop status` 的输出对象，包含 current summary、blocker、next action。
- **LoopListResult**：`loop list` 的输出对象，包含 current ids、items、malformed item count。
- **MalformedLoopArtifact**：无法 schema validate 的历史 artifact 摘要，保留 path、error、next action。

## 7. 成功标准

- **SC-190-001**：在 fixture 仓库中，`pr-review start --provider mock-reviewer` 后执行 `loop status --json` 能读出同一个 review id、loop id、status、verdict 和 next action。
- **SC-190-002**：`loop list --json` 能列出至少两个历史 review run，并正确标记 current item。
- **SC-190-003**：损坏的 `review-run.json` 不导致 `loop list` 整体崩溃，输出中必须包含 malformed 摘要。
- **SC-190-004**：`loop status/list` 前后 `.ai-sdlc/` 下既有 artifact 内容不变，且没有新建 review run。
- **SC-190-005**：CLI command discovery 包含 `ai-sdlc loop status` 与 `ai-sdlc loop list`。
- **SC-190-006**：focused tests 和 `uv run ai-sdlc verify constraints` 通过，且没有引入 CI 模型调用或云端 PR review 依赖。
