# PRD：Loop Engine Implementation Loop Runtime

**功能编号**：`194-loop-engine-implementation-loop-runtime`
**创建日期**：2026-07-01
**状态**：本地实现与验证已完成，等待提交、PR、Codex review 与合并收口
**输入**：五类 Loop 总目标中的 `implementation` loop；`local-pr-review` 已由 WI-189 完成，`loop status/list` 与 next guidance 已由 WI-190/WI-191 完成，`requirement` loop 已由 WI-192 完成，`design-contract` loop 已由 WI-193 完成。

## 1. 背景

五类 Loop 的目标是把需求、设计合同、实现、前端证据和本地对抗 review 串成可恢复、可审计、可验收的闭环。WI-193 已经能在实现前检查并关闭 design-contract，但关闭后仍缺少一个一等的 `implementation` runtime 来承接正式任务执行。

当前缺口是：代码实现通常由开发者或 AI 开发 agent 在本地仓完成，任务完成情况、验证命令、证据文件、阻断原因和下一步去向散落在聊天记录、提交信息或人工笔记中。这样会导致实现阶段难以判断 P0/P1 是否全部落地，也难以决定是否应进入 `frontend-evidence` 或 `local-pr-review`。WI-194 交付第三类 `implementation` loop，用本地 deterministic artifact 记录实现执行状态和验证证据。

## 2. 产品目标

1. 新增一个可执行的 `implementation` Loop，必须在同 work item 的已关闭 design-contract loop 之后才能启动。
2. 从 canonical `tasks.md` 读取 P0/P1 实现任务，生成 implementation task snapshot，并持续记录任务状态、证据、验证命令和阻断说明。
3. 关闭 implementation loop 前必须证明所有 P0/P1 任务已完成且具备验证证据；否则 fail-closed。
4. 默认面向技术小白输出 Result / Next / task summary / blocker / 可复制命令；`--json` 面向专业用户和自动化输出完整结构化报告。
5. 保持本地、确定性和实现阶段记录边界：P0 不调用模型、不替用户生成代码、不启动 PR review provider、不硬编码 GitHub/GitLab/Gitee 或远端 PR。
6. close 后根据 work item 证据给出下一步：如涉及前端或浏览器证据则指向 `frontend-evidence`，否则指向 `local-pr-review`。

## 3. 范围

### 3.1 覆盖范围

1. 新增 `ai-sdlc loop implementation start`，读取指定 work item 和已关闭 design-contract loop，生成 implementation artifacts。
2. 新增 `ai-sdlc loop implementation record`，按 task id 记录 `pending` / `in_progress` / `done` / `blocked` 状态、证据路径、验证命令和备注。
3. 新增 `ai-sdlc loop implementation status`，读取当前 implementation loop。
4. 新增 `ai-sdlc loop implementation close`，仅当所有 required P0/P1 任务完成且具备验证证据后关闭。
5. 扩展 `ai-sdlc loop status/list --type implementation`，让统一 Loop 状态面能读取 implementation loop。
6. 生成以下 artifacts：
   - `.ai-sdlc/loops/implementation/<loop-id>/loop-run.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-input.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-tasks.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-progress.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/verification-evidence.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-report.json`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-report.md`
   - `.ai-sdlc/loops/implementation/<loop-id>/implementation-close.json`（close 后）
   - `.ai-sdlc/loops/implementation/current-implementation.json`
7. P0 检查项必须至少覆盖：
   - work item 是否为 canonical `specs/<wi>/`
   - 上游 design-contract loop 是否存在、可读、已关闭，且属于同一 work item
   - `tasks.md` 是否存在且能解析出 P0/P1 task id
   - `record` 是否只接受 task snapshot 中存在的 task id
   - `done` task 是否至少记录一条 evidence 或 verification command
   - close 是否阻断未完成、blocked、缺证据或缺验证命令的 required task
   - close 后 next guidance 是否进入 `frontend-evidence` 或 `local-pr-review`，而不是直接声称交付完成

### 3.2 明确不覆盖

1. 不调用 GPT、Claude、DeepSeek、GLM、Codex 或任何模型服务。
2. 不自动修改业务代码，不替代开发 agent 的实现工作；它只记录实现执行状态和证据。
3. 不自动运行测试命令；P0 只记录用户或开发 agent 提供的验证命令和证据，后续可扩展自动执行。
4. 不执行 frontend evidence loop、不启动浏览器验证。
5. 不执行 local adversarial PR review；该能力仍由 `pr-review` loop 负责。
6. 不硬编码 GitHub PR、远端 diff 或 CI；本地仓、公司内网、离线仓和托管平台仓都应通过本地 artifact 记录。
7. 不把 implementation close 等同于质量完美；它只证明 required implementation tasks 已被本地记录为完成且有验证证据。

## 4. 用户场景与测试

### 用户故事 1 - 从已关闭设计合同启动实现闭环（优先级：P0）

作为技术小白或 AI 开发 agent，我希望 design-contract 关闭后执行一条命令就能启动实现跟踪，以便知道接下来要完成哪些 P0/P1 任务。

**独立测试**：构造同 work item 的 closed design-contract artifact 和 `tasks.md`，执行 `ai-sdlc loop implementation start --wi specs/demo --json`，断言生成 loop-run、input、tasks、progress、report 和 current pointer。

**验收场景**：

1. **Given** work item 存在已关闭且同 work item 的 design-contract loop，**When** 用户执行 `implementation start`，**Then** 系统必须生成 implementation loop artifacts，并输出 required task count 和下一条 record 命令。
2. **Given** 用户执行 `start --dry-run`，**When** 命令完成，**Then** 系统只预览将读取的 upstream design-contract 和 task snapshot，不写 `.ai-sdlc/loops/implementation`。
3. **Given** design-contract 缺失、未关闭或属于其他 work item，**When** 执行 start，**Then** 系统必须 blocked，提示先完成 `ai-sdlc loop design-contract close --yes`。

### 用户故事 2 - 记录实现进展和验证证据（优先级：P0）

作为专业开发者或 AI 开发 agent，我希望按任务记录实现状态、证据和验证命令，以便 implementation loop 能证明 P0/P1 是否真实完成。

**独立测试**：启动 implementation loop 后执行 `record --task-id T21 --status done --evidence src/demo.py --verification "uv run pytest tests/unit/test_demo.py -q"`，断言 progress、verification-evidence 和 report 同步更新。

**验收场景**：

1. **Given** 当前 implementation loop 已启动，**When** 用户记录某个 required task 为 `done` 且提供 evidence/verification，**Then** progress 必须保存任务状态、证据、验证命令、更新时间和备注。
2. **Given** task id 不存在于 task snapshot，**When** 执行 record，**Then** 系统必须 fail-readable，不得写入未知任务。
3. **Given** 用户把 task 记录为 `blocked`，**When** 查看 status，**Then** Next 必须指向解除该 blocker，而不是 close 或 PR review。

### 用户故事 3 - 关闭实现闭环并决定下一类 Loop（优先级：P0）

作为框架维护者，我希望 implementation loop 只有在 required tasks 全部完成并有证据时才能关闭，以便后续 frontend-evidence 或 local-pr-review 不接收半成品。

**独立测试**：所有 required tasks 均 record done 且带 evidence/verification 后，执行 `ai-sdlc loop implementation close --yes --json`，断言 loop-run 状态为 `closed`、写入 close artifact，next action 指向下一类 loop。

**验收场景**：

1. **Given** required P0/P1 tasks 未全部 done，**When** 执行 close，**Then** 系统必须 fail-closed，指出 incomplete task id。
2. **Given** required task 为 done 但缺少 evidence 或 verification command，**When** 执行 close，**Then** 系统必须 fail-closed，指出缺证据任务。
3. **Given** 所有 required tasks 完成且 work item 含前端/浏览器证据信号，**When** close 成功，**Then** Next 必须指向 `frontend-evidence`。
4. **Given** 所有 required tasks 完成且没有前端证据信号，**When** close 成功，**Then** Next 必须指向 `local-pr-review`。

### 用户故事 4 - 统一 Loop 状态面读取 implementation（优先级：P1）

作为 IDE、专业用户或自动化工具，我希望 `loop status/list` 能读取 implementation loops，以便中断后恢复实现进度。

**独立测试**：构造两个 implementation loop，执行 `ai-sdlc loop list --type implementation --json`，断言 items 按更新时间稳定排序，并标记 current。

**验收场景**：

1. **Given** 当前 implementation loop 存在，**When** 执行 `ai-sdlc loop status --type implementation --json`，**Then** JSON 必须包含通用 `LoopSummary` 和 implementation 扩展字段。
2. **Given** current pointer 损坏，**When** 执行 status/list，**Then** 输出 repair guidance，不得 traceback。
3. **Given** 用户仍使用默认 `loop status`，**When** 未指定 `--type`，**Then** 既有 local-pr-review 默认行为不回归。

## 5. 边界情况

1. 未初始化项目：输出 `ai-sdlc init .`，不得 traceback。
2. 未提供 `--wi` 且当前 checkpoint 不能解析 work item：blocked，提示传入 `--wi specs/<wi>`。
3. `--wi` 不存在、不在 `specs/<wi>/` 或越出仓库：blocked。
4. design-contract current pointer 损坏：blocked，提示修复 design-contract artifact 或显式传入 `--design-contract-loop-id`。
5. 显式 design-contract loop id 不存在、未关闭、loop type 错误或 work item 不一致：blocked。
6. `tasks.md` 缺失、没有 P0/P1 task、任务 id 不可解析：blocked。
7. `record` 未传 task id、status 非法、task 不存在：blocked，不写 progress。
8. `record --status done` 未传 evidence 且未传 verification：blocked，避免无证据完成。
9. `close` 未加 `--yes`：blocked，要求显式确认。
10. `close` 已关闭 loop：幂等返回 closed summary，不重复改写非必要 artifact。
11. loop-run schema 不兼容：status/list fail-readable，不隐藏其他合法 run。
12. Windows/PowerShell：输出命令保持可复制，不要求 POSIX shell。

## 6. 需求

### 功能需求

- **FR-194-001**：系统必须新增 `ai-sdlc loop implementation start/record/status/close` 命令。
- **FR-194-002**：`start` 必须支持 `--wi specs/<wi>`，未传时可尝试读取当前 checkpoint，但解析失败必须 fail-readable。
- **FR-194-003**：`start` 必须要求同 work item 的 design-contract loop 已关闭；未关闭不得生成 implementation artifact。
- **FR-194-004**：`start --dry-run` 必须展示将读取的 docs、upstream design-contract 和 artifact path，不得写文件。
- **FR-194-005**：`start` 必须写入 `LoopRun(loop_type=implementation)` 和 implementation-specific artifacts。
- **FR-194-006**：implementation artifacts 必须包含 schema version、artifact kind、created_by、created_at 和 ai_sdlc_version。
- **FR-194-007**：系统必须从 `tasks.md` 解析 P0/P1 required tasks，生成 `implementation-tasks.json`。
- **FR-194-008**：系统必须维护 `implementation-progress.json` 和 `verification-evidence.json`，记录每个 task 的状态、证据、验证命令、备注和更新时间。
- **FR-194-009**：`record` 必须拒绝未知 task id、非法 status 和 done-without-evidence。
- **FR-194-010**：`record` 必须刷新 `implementation-report.json` 和 `implementation-report.md`。
- **FR-194-011**：`close --yes` 必须在 required tasks 全部 done 且均有 evidence/verification 时写入 `implementation-close.json` 并将 loop-run 更新为 `closed`。
- **FR-194-012**：`close` 不得修改业务代码，不得调用模型。
- **FR-194-013**：`status` 必须读取 current implementation pointer，不写 artifact。
- **FR-194-014**：`loop status/list --type implementation` 必须读取 implementation loop，并保留默认 local-pr-review 行为。
- **FR-194-015**：human 输出必须包含 Result / Next / loop id / work item / required task count / done count / blocked count / report path。
- **FR-194-016**：JSON 输出必须包含通用 loop 字段、implementation 扩展字段、next_guidance 和 artifact paths。
- **FR-194-017**：malformed implementation artifacts 必须 fail-readable，不得导致 list 整体崩溃。
- **FR-194-018**：README 或相关文档必须说明 implementation loop 是实现执行证据闭环，关闭后下一步是 frontend-evidence 或 local-pr-review。
- **FR-194-019**：verify constraints 或 focused tests 必须覆盖 implementation core runtime、CLI surface 和 user docs。

### 关键实体

- **ImplementationInput**：启动输入 artifact，记录 work item、spec/plan/tasks path、design-contract loop id、dry-run 参数和 source metadata。
- **ImplementationTaskItem**：从 `tasks.md` 解析出的 task snapshot，包含 task id、title、priority、required、files、acceptance summary 和 verification hints。
- **ImplementationTaskProgress**：单个 task 的执行状态，包含 status、evidence、verification commands、note、updated_at。
- **ImplementationVerificationEvidence**：验证证据集合，按 task id 聚合 evidence path、verification command 和 operator note。
- **ImplementationReport**：实现进展报告，记录 status、blockers、task counts、next action、required tasks 是否全部完成。
- **ImplementationClose**：关闭确认 artifact，记录 loop id、closed_by、closed_at、report artifact、required task count 和 next loop type。
- **ImplementationLoopSummary**：`LoopSummary` 的 implementation 扩展字段，包含 work item id、work item path、required task count、done count、blocked count、evidence count、closed。
- **CurrentImplementationPointer**：当前 implementation loop 指针，位于 `.ai-sdlc/loops/implementation/current-implementation.json`。

## 7. 成功标准

- **SC-194-001**：`ai-sdlc loop implementation start --wi specs/<wi> --json` 能在 closed design-contract 后生成 implementation loop artifacts，并由 status 恢复。
- **SC-194-002**：未关闭或跨 work item 的 design-contract 不能启动 implementation loop，输出 blocked 和可复制下一步。
- **SC-194-003**：`record` 能更新 task progress、verification evidence 和 report；未知 task 或缺证据 done 必须阻断。
- **SC-194-004**：required tasks 未全部完成或缺证据时，`close --yes` 不能关闭；全部完成后状态为 `closed`。
- **SC-194-005**：`ai-sdlc loop status/list --type implementation --json` 能读取 implementation loops，且默认 local-pr-review 行为不回归。
- **SC-194-006**：focused unit/integration tests、ruff、mypy、`uv run ai-sdlc verify constraints` 和 workitem close-check 通过。

## 8. 本 PR 的完成边界

WI-194 完成后，只能声称 `implementation` loop 已落地。不得声称 `frontend-evidence` 或五类 Loop 端到端全部完成。下一步必须在 PR + Codex review + checks + merge 后，才进入 `frontend-evidence` loop 的独立 work item。
---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
  - "specs/192-loop-engine-requirement-loop-runtime/spec.md"
  - "specs/193-loop-engine-design-contract-loop-runtime/spec.md"
---
