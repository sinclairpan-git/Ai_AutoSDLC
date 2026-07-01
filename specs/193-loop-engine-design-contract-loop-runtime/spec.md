# PRD：Loop Engine Design Contract Loop Runtime

**功能编号**：`193-loop-engine-design-contract-loop-runtime`
**创建日期**：2026-07-01
**状态**：formal baseline 已冻结，进入实现
**输入**：五类 Loop 总目标中的 `design-contract` loop；`local-pr-review` 已由 WI-189 完成，`loop status/list` 与 next guidance 已由 WI-190/WI-191 完成，`requirement` loop 已由 WI-192 完成。

## 1. 背景

五类 Loop 的目标是把需求、设计合同、实现、前端证据和本地对抗 review 串成可恢复、可审计、可验收的闭环。WI-192 已经让需求能被捕获、验收清单化并冻结，但冻结需求进入实现前仍缺少一个一等的 `design-contract` runtime。

当前缺口是：`spec.md`、`plan.md`、`tasks.md`、测试计划、verification gate 和冻结需求之间的一致性主要靠人工阅读和后置 `close-check`。这会让用户在开始实现后才发现 PRD 未冻结、验收标准没有任务覆盖、计划引入未授权范围、任务没有验证命令或仍含模板占位。WI-193 交付第二类 `design-contract` loop，用本地 deterministic 检查在实现前发现合同缺口。

## 2. 产品目标

1. 新增一个可执行的 `design-contract` Loop，覆盖 formal docs 存在性、冻结状态、占位残留、需求/计划/任务/测试/验证命令覆盖和范围漂移检查。
2. 复用 Loop Engine artifact schema 和 `.ai-sdlc/loops/design-contract/<loop-id>/` 布局，不创建第二套 canonical docs。
3. 默认面向技术小白输出 Result / Next / blocker summary / 可复制命令；`--json` 面向专业用户和自动化输出完整结构化报告。
4. 保持本地、确定性和实现前边界：P0 不调用模型、不改业务代码、不运行 implementation agent、不启动 PR review provider。
5. 合同通过并显式关闭后，Next 才能指向 `implementation` loop；存在 blocker 时必须指向修订 `spec/plan/tasks/tests`，不得绕过进入代码实现。

## 3. 范围

### 3.1 覆盖范围

1. 新增 `ai-sdlc loop design-contract check`，读取指定 work item 或当前 checkpoint 的 `spec.md`、`plan.md`、`tasks.md`，生成合同检查 artifact。
2. 新增 `ai-sdlc loop design-contract status`，读取当前 design-contract loop。
3. 新增 `ai-sdlc loop design-contract close`，仅当最近一次 check 无 blocker 且用户显式确认后关闭合同。
4. 扩展 `ai-sdlc loop status/list --type design-contract`，让统一 Loop 状态面能读取 design-contract loop。
5. 生成以下 artifacts：
   - `.ai-sdlc/loops/design-contract/<loop-id>/loop-run.json`
   - `.ai-sdlc/loops/design-contract/<loop-id>/design-contract-input.json`
   - `.ai-sdlc/loops/design-contract/<loop-id>/coverage-matrix.json`
   - `.ai-sdlc/loops/design-contract/<loop-id>/design-contract-report.json`
   - `.ai-sdlc/loops/design-contract/<loop-id>/design-contract-report.md`
   - `.ai-sdlc/loops/design-contract/<loop-id>/design-contract-close.json`（close 后）
   - `.ai-sdlc/loops/design-contract/current-design-contract.json`
6. 检查项 P0 必须至少覆盖：
   - canonical docs 是否存在且位于 `specs/<wi>/`
   - `spec.md` 是否仍为草稿、是否含模板占位
   - `plan.md` / `tasks.md` 是否含模板占位
   - `spec.md` 中的功能需求与成功标准是否被 `tasks.md` 任务或验证描述引用
   - `tasks.md` 中 P0/P1 任务是否有验收标准和验证命令
   - `plan.md` 是否包含技术背景、阶段计划、验证策略和回退方式
   - 是否出现进入 implementation/frontend/local-pr-review 的未授权范围
7. check/close/status 的 next guidance 必须说明命令是否写 artifact、是否调用模型、是否修改代码。

### 3.2 明确不覆盖

1. 不调用 GPT、Claude、DeepSeek、GLM、Codex 或任何模型服务。
2. 不自动修订 `spec.md`、`plan.md`、`tasks.md` 或测试文件；只报告缺口和下一步。
3. 不执行 implementation loop、不修改业务代码、不生成实现补丁。
4. 不执行 frontend evidence loop、不启动浏览器验证。
5. 不替代 local adversarial PR review；该能力仍由 `pr-review` loop 负责。
6. 不硬编码 GitHub、GitLab、Gitee、公司内网或某个目录布局；P0 面向本地 `specs/<wi>/`，后续 source adapter 可扩展外部需求/设计来源。
7. 不把合同通过等同于需求质量完美；它只证明 formal design contract 在机器可检查范围内自洽。

## 4. 用户场景与测试

### 用户故事 1 - 小白用户一键检查设计合同（优先级：P0）

作为只会按 AI-SDLC 提示推进的用户，我希望执行一条命令就能知道当前 work item 是否可以进入实现，以便不用理解所有内部 artifact。

**独立测试**：在 fixture work item 中准备完整 `spec.md`、`plan.md`、`tasks.md`，执行 `ai-sdlc loop design-contract check --wi specs/demo --json`，断言生成 loop-run、coverage matrix、report、current pointer，且状态为 `passed`。

**验收场景**：

1. **Given** work item 的 `spec.md`、`plan.md`、`tasks.md` 均完整且无 blocker，**When** 用户执行 `check`，**Then** 系统必须输出 Result / Next / loop id / report path，并提示可以 close 合同。
2. **Given** 用户执行 `check --json`，**When** 自动化读取输出，**Then** JSON 必须包含 `design_contract.status`、`blocker_count`、`coverage_matrix_path`、`report_path` 和 `next_guidance`。
3. **Given** 用户执行 `check --dry-run`，**When** 命令完成，**Then** 系统只预览将检查的 docs 和 artifact path，不得写 `.ai-sdlc/loops/design-contract`。

### 用户故事 2 - 发现合同缺口并阻断实现（优先级：P0）

作为框架维护者，我希望 design-contract loop 能在实现前发现需求、计划和任务之间的缺口，以便避免实现阶段才返工。

**独立测试**：构造 `spec.md` 包含 `FR-DEMO-001` 和 `SC-DEMO-001`，但 `tasks.md` 未引用这些编号，执行 check 后断言状态为 `needs_fix`，并输出 blocker。

**验收场景**：

1. **Given** `spec.md` 包含 P0 功能需求或成功标准但 `tasks.md` 没有覆盖，**When** 执行 check，**Then** loop 必须进入 `needs_fix`，报告缺失覆盖项。
2. **Given** `plan.md` 或 `tasks.md` 仍含模板占位或示例残留，**When** 执行 check，**Then** loop 必须进入 `needs_fix`，指出具体文件。
3. **Given** `plan.md` 引入 spec 未授权的实现、前端或 review 范围，**When** 执行 check，**Then** 系统必须报告 scope drift，不得提示进入 implementation。

### 用户故事 3 - 关闭设计合同并进入实现 Loop（优先级：P0）

作为专业用户或 AI agent，我希望只有 check 通过且用户显式确认后才能关闭 design-contract，以便 implementation loop 有可审计的前置合同证据。

**独立测试**：先执行通过的 check，再执行 `ai-sdlc loop design-contract close --yes --json`，断言 loop-run 状态变为 `closed`、写入 close artifact，next action 指向 implementation loop。

**验收场景**：

1. **Given** 最近一次 check 无 blocker，**When** 用户执行 `close --yes`，**Then** 系统必须写入 `design-contract-close.json` 并将 loop 状态置为 `closed`。
2. **Given** 最近一次 check 有 blocker，**When** 用户执行 close，**Then** 系统必须 fail-closed，保持 `needs_fix`，不得关闭。
3. **Given** close 后执行 `ai-sdlc loop status --type design-contract`，**When** 用户查看 Next，**Then** Next 必须指向 implementation loop，而不是直接修改代码。

### 用户故事 4 - 统一 Loop 状态面读取 design-contract（优先级：P1）

作为 IDE、专业用户或自动化工具，我希望 `loop status/list` 能读取 design-contract loops，以便在中断后恢复和审计历史检查。

**独立测试**：构造两个 design-contract loop，执行 `ai-sdlc loop list --type design-contract --json`，断言 items 按更新时间稳定排序，并标记 current。

**验收场景**：

1. **Given** 当前 design-contract loop 存在，**When** 执行 `ai-sdlc loop status --type design-contract --json`，**Then** JSON 必须包含通用 `LoopSummary` 和 design-contract 扩展字段。
2. **Given** 多个历史 design-contract loop，**When** 执行 `loop list --type design-contract`，**Then** 系统必须列出历史 run，坏 artifact 不得隐藏好 artifact。
3. **Given** 用户仍使用默认 `loop status`，**When** 未指定 `--type`，**Then** 既有 local-pr-review 默认行为不回归。

## 5. 边界情况

1. 未初始化项目：输出 `ai-sdlc init .`，不得 traceback。
2. 未提供 `--wi` 且当前 checkpoint 不能解析 work item：blocked，提示传入 `--wi specs/<wi>`。
3. `--wi` 不存在或不在仓库内：blocked，指出路径。
4. `spec.md`、`plan.md` 或 `tasks.md` 缺失：needs_fix，指出缺失文件。
5. docs 仍为草稿或含模板占位：needs_fix。
6. `tasks.md` 没有任何任务或任务缺少验收/验证：needs_fix。
7. `spec.md` 没有可识别 FR/SC：needs_fix，提示补全编号化需求或成功标准。
8. current pointer 损坏：status/list 输出 blocked repair guidance。
9. loop-run schema 不兼容：list 不隐藏其他合法 run。
10. close 未加 `--yes`：blocked，要求显式确认。
11. close 已关闭 loop：幂等返回 closed summary，不重复改写非必要 artifact。
12. Windows/PowerShell：输出命令保持可复制，不要求 POSIX shell。

## 6. 需求

### 功能需求

- **FR-193-001**：系统必须新增 `ai-sdlc loop design-contract check/status/close` 命令。
- **FR-193-002**：`check` 必须支持 `--wi specs/<wi>`，未传时可尝试读取当前 checkpoint，但解析失败必须 fail-readable。
- **FR-193-003**：`check --dry-run` 必须展示将读取的 docs 和将生成的 artifact path，不得写文件。
- **FR-193-004**：`check` 必须写入 `LoopRun(loop_type=design-contract)` 和 design-contract-specific artifacts。
- **FR-193-005**：design-contract artifacts 必须包含 schema version、artifact kind、created_by、created_at 和 ai_sdlc_version。
- **FR-193-006**：系统必须生成 machine-readable `coverage-matrix.json` 和 `design-contract-report.json`。
- **FR-193-007**：系统必须生成 plain markdown 的 `design-contract-report.md`，面向小白用户说明 blocker、下一步和证据路径。
- **FR-193-008**：缺失 docs、占位残留、FR/SC 未被任务覆盖、任务缺少验收/验证时，loop 必须为 `needs_fix`，不能 close 或进入 implementation。
- **FR-193-009**：无 blocker 时，check 后状态可为 `passed`，Next 指向 `ai-sdlc loop design-contract close --yes`。
- **FR-193-010**：`close --yes` 必须写入 `design-contract-close.json`，并将 loop-run 更新为 `closed`。
- **FR-193-011**：`close` 不得修改业务代码，不得调用模型。
- **FR-193-012**：`status` 必须读取 current design-contract pointer，不写 artifact。
- **FR-193-013**：`loop status/list --type design-contract` 必须读取 design-contract loop，并保留默认 local-pr-review 行为。
- **FR-193-014**：human 输出必须包含 Result / Next / loop id / work item / blocker count / coverage summary / report path。
- **FR-193-015**：JSON 输出必须包含通用 loop 字段、design-contract 扩展字段、next_guidance 和 artifact paths。
- **FR-193-016**：malformed design-contract artifacts 必须 fail-readable，不得导致 list 整体崩溃。
- **FR-193-017**：README 或相关文档必须说明 design-contract loop 是 implementation 前置合同检查，关闭后下一步是 implementation loop。
- **FR-193-018**：verify constraints 或 focused tests 必须覆盖 design-contract core runtime、CLI surface 和 user docs。

### 关键实体

- **DesignContractInput**：合同检查输入 artifact，记录 work item path、spec/plan/tasks path、requirement loop id、dry-run 参数和 source metadata。
- **ContractCoverageItem**：单个 FR/SC/任务/验证项的覆盖记录，包含 source id、source file、covered_by、status 和 blocker。
- **DesignContractReport**：合同检查结果 artifact，记录 status、blockers、warnings、coverage summary、scope drift、placeholder findings 和 next action。
- **DesignContractClose**：关闭确认 artifact，记录 loop id、closed_by、closed_at、report artifact、blocker count 和 next loop type。
- **DesignContractLoopSummary**：`LoopSummary` 的 design-contract 扩展字段，包含 work item id、work item path、blocker count、warning count、coverage count、closed。
- **CurrentDesignContractPointer**：当前 design-contract loop 指针，位于 `.ai-sdlc/loops/design-contract/current-design-contract.json`。

## 7. 成功标准

- **SC-193-001**：`ai-sdlc loop design-contract check --wi specs/<wi> --json` 能生成 design-contract loop artifacts，并由 status 恢复。
- **SC-193-002**：缺少任务覆盖或模板占位的 design-contract loop 不能 close，输出 `needs_fix` 和可复制下一步。
- **SC-193-003**：无 blocker 的 design-contract loop 执行 `close --yes` 后状态为 `closed`，next guidance 指向 implementation loop。
- **SC-193-004**：`ai-sdlc loop status/list --type design-contract --json` 能读取 design-contract loops，且默认 local-pr-review 行为不回归。
- **SC-193-005**：focused unit/integration tests、ruff、mypy、`uv run ai-sdlc verify constraints` 和 workitem close-check 通过。

## 8. 本 PR 的完成边界

WI-193 完成后，只能声称 `design-contract` loop 已落地。不得声称 `implementation`、`frontend-evidence` 或五类 Loop 端到端全部完成。下一步必须在 PR + Codex review + checks + merge 后，才进入 `implementation` loop 的独立 work item。
