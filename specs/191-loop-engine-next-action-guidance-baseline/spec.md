# PRD：Loop Engine Next Action Guidance Baseline

**功能编号**：`191-loop-engine-next-action-guidance-baseline`
**创建日期**：2026-06-30
**状态**：已拆解，等待执行
**上游来源**：WI-189 `local adversarial PR review` + WI-190 `loop status/list`
**目标读者**：Codex 开发 agent、AI-SDLC 框架维护者、普通项目操作者

## 1. 背景

WI-189 已落地本地独立 PR Review Loop：`ai-sdlc pr-review doctor/start/status/fix/rerun/close` 可以在用户本地仓库生成 review pack、调用本地独立 review agent、记录 findings/resolution/final report，并默认使用用户当前配置模型或显式指定模型。

WI-190 已落地 `ai-sdlc loop status/list` 只读状态面：用户能读取当前 local PR review run、历史 run、unresolved counts 和 artifact paths，且 loop 命令不调用模型、不写 artifact、不启动 provider。

当前缺口是：`next_action` 仍主要是一段字符串。普通用户看到 `Run ai-sdlc pr-review fix.`、`Rerun ai-sdlc pr-review start.` 或 `Check the base/head refs.` 时，仍不一定知道：

1. 这是可以直接复制执行的命令，还是需要先处理的说明。
2. 该下一步是否会写入 artifact、调用模型、修改代码或只读检查。
3. 为什么推荐这一步，以及失败时应该查看哪个 artifact。
4. 自动化工具如何稳定读取下一步，而不是解析自然语言字符串。

WI-191 的目标是把 `loop status/list` 的下一步从单一字符串升级为 **结构化、可解释、小白友好、机器可消费的 Next Action Guidance**。它仍然保持 `loop` 命令只读；真正的模型调用只可能发生在用户后续显式执行的 `pr-review start/rerun` provider 流程中。

## 2. 产品目标

### 2.1 总目标

让用户在中断恢复或审计 local PR review loop 时，不只看到“下一步字符串”，而是看到明确的推荐命令、原因、影响范围、安全边界和 artifact 依据，从而把 `loop status/list` 变成可行动的本地闭环导航入口。

### 2.2 质量目标

1. 降低学习成本：普通用户无需理解 `ReviewRun` 内部状态，也能知道下一步先跑 `doctor`、`fix`、`rerun` 还是 `close`。
2. 提升恢复质量：每个 guidance 必须说明来源 artifact 和推荐原因，避免长任务恢复时误操作。
3. 提升自动化稳定性：JSON 输出提供结构化字段，自动化工具不再解析自然语言 `next_action`。
4. 保持兼容性：现有 `next_action` 字符串继续存在，不破坏 WI-190 用户和测试。
5. 保持边界清晰：`loop status/list` 只做推导和展示，不执行下一步、不调用模型、不写入 `.ai-sdlc/`。

## 3. 范围

### 3.1 覆盖范围

1. 新增 `LoopNextActionGuidance` 或等价 Pydantic 输出模型。
2. 在 `LoopStatusResult`、`LoopListResult` 和 `LoopSummary` 的 JSON 输出中增加结构化 next guidance，同时保留原 `next_action` 字段。
3. 为 local PR review 的关键状态推导 guidance：
   - 未初始化项目。
   - 没有 current review。
   - current pointer 或 `review-run.json` 损坏。
   - review 状态为 `needs_fix`。
   - review 状态为 `needs_review` 或需要 rerun。
   - review 状态为 `passed`。
   - review 状态为 `blocked` 或 `needs_user`。
   - review 状态为 `closed`。
4. human 输出展示 `Next command`、`Why`、`Effects`、`Model call`、`Writes artifacts`、`Writes code`、`Evidence`。
5. `loop list --json` 的每个 item 带独立 guidance；current item 可以给 PR-review follow-up，非 current 历史 item 必须是 inspect-only guidance，因为 `pr-review fix/rerun/close` 只作用于 current pointer。
6. 更新 README、PR checklist 或 verify constraints，明确 guidance 是只读推导，不是执行器。

### 3.2 明确不覆盖

1. 不新增 `ai-sdlc loop run`、`loop resume` 或自动执行下一步命令。
2. 不让 `loop status/list` 调用 GPT、Claude、DeepSeek、GLM、Codex 或其他模型服务。
3. 不让 `loop status/list` 启动 `local-agent`、`mock-reviewer` 或任何 provider command。
4. 不修改 `pr-review start/fix/rerun/close` 的核心状态机语义。
5. 不新增 GitHub/GitLab 远端 PR API 调用。
6. 不自动修复代码；`pr-review fix` 仍只生成 fix plan / resolution scaffold，不改代码。
7. 不把 guidance 当成合规审计强证明；它只是本地 artifact truth 的可行动解释。

## 4. 用户场景与测试

### 用户故事 1 - 当前 loop 的可执行下一步（优先级：P0）

作为普通 AI-SDLC 用户，我希望 `ai-sdlc loop status` 不只告诉我当前状态，还告诉我下一条推荐命令、为什么执行它、是否会调用模型或写 artifact，以便我能安全恢复本地 PR review 闭环。

**优先级说明**：这是 WI-190 状态面的直接下一层价值；没有结构化 guidance，status/list 仍然更像 artifact 索引，而不是闭环导航入口。

**独立测试**：构造 `needs_fix` review run，执行 `ai-sdlc loop status --json`，断言 `next_guidance.command` 为 `ai-sdlc pr-review fix`，`writes_artifacts=true`，`writes_code=false`，`requires_model=false`，并保留 `next_action` 字符串。

**验收场景**：

1. **Given** 当前 review 状态为 `needs_fix` 且有 unresolved blocker/required，**When** 用户执行 `ai-sdlc loop status`，**Then** human 输出必须展示推荐命令 `ai-sdlc pr-review fix`、推荐原因、artifact 依据和不会直接修改代码的说明。
2. **Given** 当前 review 状态为 `passed`，**When** 用户执行 `ai-sdlc loop status --json`，**Then** `next_guidance.command` 必须指向 `ai-sdlc pr-review close`，并标明该命令写 final report 但不调用模型。
3. **Given** 当前 review 状态为 `needs_user`，**When** 用户执行 status，**Then** guidance 必须优先解释 blocker 和人工处理动作，不得给出会掩盖风险的 close 命令。

### 用户故事 2 - 无 current review 时先 doctor 再 start（优先级：P0）

作为技术小白，我希望在没有当前 review run 时，系统先建议我做本地 readiness 检查，而不是直接要求我理解 base branch、provider 和模型配置。

**优先级说明**：用户第一次使用本地 PR review 最容易卡在 base/provider/model 配置。先 `doctor` 能降低学习成本并减少误启动。

**独立测试**：在已初始化但无 `.ai-sdlc/reviews/pr/current-review.json` 的 fixture 中执行 `loop status --json`，断言 guidance 推荐 `ai-sdlc pr-review doctor --base <branch>`，alternative 包含 `ai-sdlc pr-review start --base <branch>`。

**验收场景**：

1. **Given** 项目已初始化但没有 current review，**When** 用户执行 `ai-sdlc loop status`，**Then** `Next command` 必须优先建议 `ai-sdlc pr-review doctor --base <branch>`。
2. **Given** 用户读取 JSON，**When** 自动化工具展示引导，**Then** guidance 必须包含 `alternatives`，其中可包含 `ai-sdlc pr-review start --base <branch>`。
3. **Given** 项目未初始化，**When** 用户执行 `ai-sdlc loop status`，**Then** guidance 必须建议 `ai-sdlc init .`，且不得输出 Python traceback。

### 用户故事 3 - 机器可消费的 guidance 合同（优先级：P0）

作为 IDE、门户或上层自动化工具，我希望从 `loop status/list --json` 读取稳定结构，而不是解析 `next_action` 文本，以便可靠渲染按钮、风险提示和恢复入口。

**优先级说明**：Loop Engine 后续会接 requirement/design/frontend 等多类 loop；从本地 PR review 开始建立通用 guidance 合同，可以避免未来再次破坏 JSON。

**独立测试**：执行 `loop list --json`，断言顶层 result 和每个 item 都包含 `next_guidance`，字段为稳定 snake_case，且非 current item 不给 `pr-review fix/rerun/close` 命令。

**验收场景**：

1. **Given** `loop status --json` 输出 ready，**When** 工具解析 JSON，**Then** 顶层必须包含 `next_guidance`，当前 loop 也必须包含自己的 `next_guidance`。
2. **Given** `loop list --json` 包含多个历史 run，**When** 工具读取 items，**Then** 每个 item 必须包含 `next_guidance.command`、`reason`、`requires_model`、`writes_artifacts`、`writes_code`、`evidence`，且非 current item 的 guidance 必须是只读 inspect-only。
3. **Given** 未来新增其他 loop type，**When** 复用 guidance 模型，**Then** 不需要依赖 local PR review 专属字段才能表达下一步。

### 用户故事 4 - 只读边界和模型调用边界（优先级：P0）

作为企业用户，我希望 `loop status/list` 的 guidance 不会因为计算下一步而启动 provider、调用模型或写入 artifact，以便该命令可安全用于本地排查和 CI artifact 读取。

**优先级说明**：WI-190 的核心信任边界必须保持，否则 guidance 会把只读状态面变成隐式执行器。

**独立测试**：在含 current review 的 fixture 中记录 `.ai-sdlc/` 快照，分别执行 `loop status --json`、`loop list --json`，断言文件内容不变，并 patch provider runner 确认未调用。

**验收场景**：

1. **Given** guidance 推导出 `pr-review rerun` 可能调用模型，**When** 用户只执行 `loop status`，**Then** 模型调用不得发生，只能在输出中标明后续命令可能调用本地独立 review agent。
2. **Given** guidance 推导出 `pr-review fix` 会写 artifact，**When** 用户只执行 `loop list`，**Then** `.ai-sdlc/reviews/pr` 不得新增或修改文件。
3. **Given** CI 读取 `loop list --json`，**When** 输出 guidance，**Then** CI 不得因此发起任何模型请求。

### 用户故事 5 - 历史 run 的恢复提示（优先级：P1）

作为框架维护者或高级用户，我希望 `loop list` 中每个 run 都能显示安全的下一步，以便快速判断 current run 可执行什么、历史 run 应查看什么、哪个 artifact 损坏。

**优先级说明**：P0 先保证当前 status，P1 扩展到 list item，便于审计和工具集成。

**独立测试**：构造一个 current `needs_fix` run 和一个非 current `passed` run，执行 `loop list --json`，断言 current item 给 `pr-review fix`，非 current item 给 inspect-only guidance。

**验收场景**：

1. **Given** 历史 run 状态不同，**When** 执行 `ai-sdlc loop list`，**Then** current run 的 human 摘要可以显示对应 PR-review `Next command`，非 current run 必须显示 inspect-only command。
2. **Given** 某个历史 run artifact malformed，**When** 执行 list，**Then** artifact error 必须有 guidance，建议 inspect/remove/rerun，而不是让用户猜。

## 5. 边界情况

1. `.ai-sdlc` 不存在：guidance command 为 `ai-sdlc init .`，requires_model=false，writes_artifacts=true。
2. `current-review.json` 缺失：优先建议 `ai-sdlc pr-review doctor --base <branch>`，并提供 start alternative。
3. current pointer malformed：guidance 建议检查或重新生成 current review，不得建议 close。
4. `review-run.json` 缺失或 schema 不兼容：guidance 指向 artifact path，并建议 rerun `pr-review start`。
5. `needs_fix` 但 unresolved counts 全为 0：guidance 应提示检查 findings/resolution 一致性或 rerun，不得盲目 close。
6. `passed` 但 final report 缺失：guidance 建议 `ai-sdlc pr-review close`。
7. `closed` 且 final report 存在：guidance 应标记 no action needed 或 inspect final report。
8. `blocked`/`needs_user` 有 blocker：guidance 必须以 blocker 优先，不覆盖为通用命令。
9. `model_selector=current`：guidance 可展示模型来源信息，但不得在 loop 命令中解析或调用模型。
10. Windows 路径和 PowerShell 用户：human 输出中的命令必须保持可复制，JSON 路径保持 repo-relative POSIX 风格。

## 6. 需求

### 功能需求

- **FR-191-001**：系统必须新增结构化 next guidance 输出模型，至少包含 `command`、`reason`、`requires_model`、`writes_artifacts`、`writes_code`、`evidence`、`alternatives`。
- **FR-191-002**：系统必须保留既有 `next_action` 字符串字段，避免破坏 WI-190 的兼容合同。
- **FR-191-003**：`loop status --json` 顶层必须包含 `next_guidance`。
- **FR-191-004**：`LoopSummary` 或等价 item 输出必须包含当前 loop 自身的 `next_guidance`。
- **FR-191-005**：`loop list --json` 的每个合法 item 必须包含 `next_guidance`。
- **FR-191-005A**：非 current `loop list` item 的 `next_guidance` 不得推荐 `ai-sdlc pr-review fix`、`ai-sdlc pr-review rerun` 或 `ai-sdlc pr-review close`，因为这些命令作用于 current review pointer。
- **FR-191-006**：no current review 时，guidance 必须优先推荐 `ai-sdlc pr-review doctor --base <branch>`，并可提供 start alternative。
- **FR-191-007**：`needs_fix` 时，guidance 必须推荐 `ai-sdlc pr-review fix`，并标明不调用模型、不修改代码、会写 fix plan/resolution artifacts。
- **FR-191-008**：`passed` 时，guidance 必须推荐 `ai-sdlc pr-review close`，并标明会写 final report、不调用模型。
- **FR-191-009**：需要复审或 rerun 时，guidance 必须推荐 `ai-sdlc pr-review rerun`，并标明该后续命令可能调用本地独立 review agent 和用户配置模型。
- **FR-191-010**：`blocked`/`needs_user` 时，guidance 必须优先展示 blocker 和人工处理动作，不得自动建议 close。
- **FR-191-011**：human 输出必须展示 next guidance 的命令、原因、影响和证据，不得只输出结构化 JSON。
- **FR-191-012**：guidance 推导必须只读取本地 artifact，不得写入 `.ai-sdlc/`。
- **FR-191-013**：guidance 推导不得调用 provider command、local-agent、mock-reviewer、Codex 云端 PR review 或任何模型服务。
- **FR-191-014**：文档和 verify constraints 必须说明 guidance 是只读导航，不是自动执行器，也不是 AI review 或人工确认的替代品。

### 关键实体

- **LoopNextActionGuidance**：从本地 loop artifact 推导出的下一步说明，包含可执行命令、原因、影响范围、模型调用提示和证据引用。
- **GuidanceEvidenceRef**：guidance 使用的 artifact 或字段依据，例如 current pointer、review-run path、status、unresolved counts、final report path。
- **GuidanceEffect**：下一步命令的副作用摘要，例如是否调用模型、是否写 artifact、是否修改代码。
- **GuidanceAlternative**：可选但非首选的下一步，例如 no current 时的 `pr-review start`。

## 7. 成功标准

- **SC-191-001**：`loop status --json` 在 `needs_fix` fixture 中输出 `next_guidance.command=ai-sdlc pr-review fix`，且 `requires_model=false`、`writes_artifacts=true`、`writes_code=false`。
- **SC-191-002**：`loop status --json` 在 no current fixture 中优先推荐 `ai-sdlc pr-review doctor --base <branch>`。
- **SC-191-003**：`loop list --json` 的每个合法 item 都包含结构化 `next_guidance`，且不移除原 `next_action` 字段；非 current item 只给 inspect-only guidance。
- **SC-191-004**：`loop status/list` 前后 `.ai-sdlc/` 文件快照不变，且 provider runner 未被调用。
- **SC-191-005**：human 输出包含 `Next command`、`Why`、`Model call`、`Writes artifacts`、`Writes code` 和 `Evidence`。
- **SC-191-006**：focused tests、`git diff --check` 和 `uv run ai-sdlc verify constraints` 通过。
