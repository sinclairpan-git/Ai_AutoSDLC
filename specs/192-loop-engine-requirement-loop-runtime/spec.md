# PRD：Loop Engine Requirement Loop Runtime

**功能编号**：`192-loop-engine-requirement-loop-runtime`
**创建日期**：2026-06-30
**状态**：formal baseline 已冻结，进入实现
**输入**：五类 Loop 总目标中的 `requirement` loop；`local-pr-review` 已由 WI-189 完成，`loop status/list` 与 next guidance 已由 WI-190/WI-191 完成。

## 1. 背景

五类 Loop 的总目标是让 AI-SDLC 能把需求从输入、设计合同、实现、前端证据、本地对抗 review 串成可恢复、可审计、可验收的闭环。WI-189 已经完整落地 `local-pr-review`，但 `requirement` 仍停留在既有 PRD Studio、work item scaffold 和阶段门禁的零散能力中，没有一个统一的 Loop Engine runtime。

当前缺口是：用户输入一个需求后，系统能生成 formal docs，但缺少可持久化的 requirement loop run，无法稳定回答“需求输入是什么、还缺哪些澄清、验收清单是否存在、是否已经冻结、下一步是否可以进入 design-contract loop”。WI-192 只交付第一类 `requirement` loop，为后续 `design-contract`、`implementation`、`frontend-evidence` loop 提供上游入口。

## 2. 产品目标

1. 新增一个可执行的 `requirement` Loop，覆盖需求捕获、澄清问题、验收清单、冻结确认和下一步指引。
2. 复用 Loop Engine artifact schema 和 `.ai-sdlc/loops/<loop-type>/<loop-id>/` 布局，不创建第二套 canonical docs。
3. 默认面向技术小白输出 Result / Next / 可复制命令；`--json` 面向专业用户和自动化输出完整结构化状态。
4. 保持只读/写入边界清晰：requirement loop 只写需求治理 artifact，不调用模型、不改业务代码、不启动 review provider。
5. 冻结后的 requirement loop 必须指向下一类 `design-contract` loop，而不是直接进入实现。

## 3. 范围

### 3.1 覆盖范围

1. 新增 `ai-sdlc loop requirement start`，从 `--idea` 或 `--input-file` 捕获需求，生成 requirement loop artifacts。
2. 新增 `ai-sdlc loop requirement status`，读取当前 requirement loop。
3. 新增 `ai-sdlc loop requirement freeze`，在存在验收清单且用户显式确认后冻结需求。
4. 扩展 `ai-sdlc loop status/list --type requirement`，让统一 Loop 状态面能读取 requirement loop。
5. 生成以下 artifacts：
   - `.ai-sdlc/loops/requirement/<loop-id>/loop-run.json`
   - `.ai-sdlc/loops/requirement/<loop-id>/requirement-intake.json`
   - `.ai-sdlc/loops/requirement/<loop-id>/requirement-brief.md`
   - `.ai-sdlc/loops/requirement/<loop-id>/clarification-questions.md`
   - `.ai-sdlc/loops/requirement/<loop-id>/acceptance-checklist.md`
   - `.ai-sdlc/loops/requirement/<loop-id>/requirement-freeze.json`（freeze 后）
   - `.ai-sdlc/loops/requirement/current-requirement.json`
6. Requirement loop 的 next guidance 必须说明后续命令是否写 artifact、是否调用模型、是否修改代码。

### 3.2 明确不覆盖

1. 不调用 GPT、Claude、DeepSeek、GLM、Codex 或任何模型服务。
2. 不把 requirement loop 伪装成需求质量自动评审；它是本地结构化捕获和冻结。
3. 不生成 design-contract、implementation 或 frontend-evidence 的实现 artifact；冻结后只指向下一步。
4. 不自动创建、修改业务代码或前端代码。
5. 不替代人工需求确认；`freeze` 必须显式确认。
6. 不把 GitHub、GitLab、Gitee 或远端 issue 系统写死为需求来源；远端需求来源后续通过 source adapter 扩展。

## 4. 用户场景与测试

### 用户故事 1 - 捕获一个新需求（优先级：P0）

作为只会描述想法的用户，我希望执行一条命令就能把需求保存成可恢复的 requirement loop，并看到还需要补充什么，以便需求不会只停留在聊天记录里。

**独立测试**：在初始化项目中执行 `ai-sdlc loop requirement start --idea "..." --acceptance "..." --json`，断言生成 loop-run、intake、brief、questions、acceptance checklist 和 current pointer。

**验收场景**：

1. **Given** 项目已初始化，**When** 用户执行 `ai-sdlc loop requirement start --idea "订单后台需要审批流" --acceptance "审批节点可配置"`，**Then** 系统必须生成 requirement loop artifact，并输出 Result / Next / loop id / artifact path。
2. **Given** 用户没有传 `--acceptance`，**When** start 运行，**Then** loop 状态必须为 `needs_user`，Next 必须提示补充验收标准，不得直接进入 design-contract。
3. **Given** 用户使用 `--dry-run`，**When** start 运行，**Then** 系统只展示将写入的 artifact，不得实际写 `.ai-sdlc/loops/requirement`。

### 用户故事 2 - 小白可理解的澄清与验收清单（优先级：P0）

作为技术小白，我希望系统用普通语言告诉我缺少哪些需求信息和验收标准，而不是只给内部 schema。

**独立测试**：构造只有 idea、无验收标准的 start，断言 `clarification-questions.md` 与 human 输出都包含普通语言问题和下一条命令。

**验收场景**：

1. **Given** 需求没有明确用户角色、成功标准或边界，**When** start 生成 artifact，**Then** clarification questions 必须列出缺口。
2. **Given** 输出 human 视图，**When** 用户阅读，**Then** 必须看到 Result、Next、clarification count、acceptance count 和可复制命令。
3. **Given** 输出 JSON，**When** 自动化读取，**Then** 必须包含 `requirement.summary`、`clarification_count`、`acceptance_count`、`source_kind` 和 artifact paths。

### 用户故事 3 - 冻结需求并进入下一类 Loop（优先级：P0）

作为框架维护者，我希望只有验收清单存在且用户显式确认后才能冻结 requirement loop，以便后续 design-contract 不建立在未确认需求上。

**独立测试**：先 start 一个有验收标准的 loop，再执行 `ai-sdlc loop requirement freeze --yes --json`，断言 loop-run 状态变为 `closed`、写入 `requirement-freeze.json`，next action 指向 design-contract loop。

**验收场景**：

1. **Given** 当前 requirement loop 有至少一条 acceptance，**When** 用户执行 `freeze --yes`，**Then** 系统必须写入 freeze artifact，并将 loop status 置为 `closed`。
2. **Given** 当前 requirement loop 没有 acceptance，**When** 用户执行 freeze，**Then** 系统必须 fail-closed 到 `needs_user`，不得冻结。
3. **Given** loop 已冻结，**When** 用户执行 `ai-sdlc loop status --type requirement`，**Then** Next 必须指向 design-contract loop，而不是实现代码。

### 用户故事 4 - 统一 Loop 状态面读取 requirement（优先级：P1）

作为专业用户或 IDE，我希望 `loop status/list` 不再只读 local-pr-review，也能通过 `--type requirement` 读取 requirement loop。

**独立测试**：构造两个 requirement loop，执行 `ai-sdlc loop list --type requirement --json`，断言 items 按更新时间稳定排序，并标记 current。

**验收场景**：

1. **Given** 当前 requirement loop 存在，**When** 执行 `ai-sdlc loop status --type requirement --json`，**Then** JSON 必须包含通用 `LoopSummary` 和 requirement 扩展字段。
2. **Given** 多个历史 requirement loop，**When** 执行 `loop list --type requirement`，**Then** 系统必须列出历史 run，坏 artifact 不得隐藏好 artifact。
3. **Given** 用户仍使用默认 `loop status`，**When** 未指定 `--type`，**Then** 既有 local-pr-review 行为不变。

## 5. 边界情况

1. 未初始化项目：输出 `ai-sdlc init .`，不得 traceback。
2. `--idea` 与 `--input-file` 都缺失：进入 blocked，给出 start 命令示例。
3. `--input-file` 不存在或不可读：blocked，指出文件路径。
4. idea 为空白：blocked。
5. acceptance 为空或只有空白：不计入验收清单。
6. current pointer 损坏：status/list 输出 blocked repair guidance。
7. loop-run schema 不兼容：list 不隐藏其他合法 run。
8. freeze 未加 `--yes`：blocked，要求显式确认。
9. freeze 已冻结 loop：幂等返回 closed summary，不重复改写非必要 artifact。
10. Windows/PowerShell：输出命令保持可复制，不要求 POSIX shell。

## 6. 需求

### 功能需求

- **FR-192-001**：系统必须新增 `ai-sdlc loop requirement start/status/freeze` 命令。
- **FR-192-002**：`start` 必须支持 `--idea` 和 `--input-file` 两类本地需求来源，且不得硬编码远端 SaaS。
- **FR-192-003**：`start --dry-run` 必须展示将生成的 artifact 和状态，不得写文件。
- **FR-192-004**：`start` 必须写入 `LoopRun(loop_type=requirement)` 和 requirement-specific intake artifact。
- **FR-192-005**：requirement artifacts 必须包含 schema version、artifact kind、created_by、created_at 和 ai_sdlc_version。
- **FR-192-006**：系统必须生成 plain markdown 的 requirement brief、clarification questions 和 acceptance checklist。
- **FR-192-007**：没有 acceptance criteria 时，loop 必须为 `needs_user`，不能冻结或进入下一 loop。
- **FR-192-008**：存在 acceptance criteria 时，start 后状态可为 `needs_review`，Next 指向 `ai-sdlc loop requirement freeze --yes`。
- **FR-192-009**：`freeze --yes` 必须写入 `requirement-freeze.json`，并将 loop-run 更新为 `closed`。
- **FR-192-010**：`freeze` 不得修改业务代码，不得调用模型。
- **FR-192-011**：`status` 必须读取 current requirement pointer，不写 artifact。
- **FR-192-012**：`loop status/list --type requirement` 必须读取 requirement loop，并保留默认 local-pr-review 行为。
- **FR-192-013**：human 输出必须包含 Result / Next / loop id / requirement summary / clarification count / acceptance count / artifact paths。
- **FR-192-014**：JSON 输出必须包含通用 loop 字段、requirement 扩展字段、next_guidance 和 artifact paths。
- **FR-192-015**：malformed requirement artifacts 必须 fail-readable，不得导致 list 整体崩溃。
- **FR-192-016**：README 或相关文档必须说明 requirement loop 是需求冻结入口，冻结后下一步是 design-contract loop。

### 关键实体

- **RequirementIntake**：需求输入 artifact，记录 source kind、source path、idea、summary、clarification questions、acceptance criteria 和 work item id。
- **RequirementFreeze**：冻结确认 artifact，记录 loop id、accepted_by、accepted_at、acceptance count、source artifact 和 next loop type。
- **RequirementLoopSummary**：`LoopSummary` 的 requirement 扩展字段，包含 source kind、summary、clarification count、acceptance count、frozen。
- **CurrentRequirementPointer**：当前 requirement loop 指针，位于 `.ai-sdlc/loops/requirement/current-requirement.json`。

## 7. 成功标准

- **SC-192-001**：`ai-sdlc loop requirement start --idea ... --acceptance ... --json` 能生成 requirement loop artifacts，并由 status 恢复。
- **SC-192-002**：无 acceptance 的 requirement loop 不能 freeze，输出 needs_user 和可复制下一步。
- **SC-192-003**：有 acceptance 的 requirement loop 执行 `freeze --yes` 后状态为 `closed`，next guidance 指向 design-contract。
- **SC-192-004**：`ai-sdlc loop status/list --type requirement --json` 能读取 requirement loops，且默认 local-pr-review 行为不回归。
- **SC-192-005**：focused unit/integration tests、ruff、mypy、`uv run ai-sdlc verify constraints` 和 workitem close-check 通过。
