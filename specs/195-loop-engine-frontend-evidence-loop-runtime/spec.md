# 功能规格：Loop Engine Frontend Evidence Loop Runtime

**功能编号**：`195-loop-engine-frontend-evidence-loop-runtime`
**创建日期**：2026-07-01
**状态**：冻结
**来源**：Loop Engineering 五类一等闭环目标；WI-194 implementation close 后的 `frontend-evidence` 下一跳；现有 `program browser-gate-probe` 本地证据面。

## 范围

本工作项交付 Loop Engine 的 `frontend-evidence` 一等闭环。它把已有前端浏览器门禁证据纳入 `.ai-sdlc/loops/frontend-evidence/<loop-id>/`，并提供 `doctor/start/status/close/skip`、统一 `loop status/list --type frontend-evidence`、小白友好输出、JSON 输出和关闭门禁。

本工作项不重新实现前端生成、不把浏览器探测固定为 Playwright、不固定 Vue/PrimeVue/GitHub/远端预览站点，也不要求 CI 调用模型或运行浏览器。浏览器证据可以来自已有本地命令 `ai-sdlc program browser-gate-probe --execute`、Codex browser 控制能力、浏览器 MCP/插件、企业内网 E2E 工具或用户显式导入的项目内 artifact；本 loop 只做 provider readiness guidance、artifact ingestion 和确定性验收。

## 用户场景与测试

### 用户故事 1：本地前端证据进入 Loop Engine（优先级：P0）

作为只会跟着命令走的小白用户，我希望实现闭环关闭后，如果需求涉及前端，下一步能直接执行一个 `frontend-evidence` loop，把浏览器门禁结果变成清楚的通过、阻塞或告警状态。

**优先级说明**：这是五类 Loop 的缺口，也是 implementation loop 对前端需求的当前下一跳。

**独立测试**：构造已关闭 implementation loop 和 `frontend-browser-gate/latest.yaml`，执行 `ai-sdlc loop frontend-evidence start --wi specs/<work-item>`，检查 loop artifact、human 输出和 JSON 输出。

**验收场景**：

1. **Given** implementation loop 已关闭且 `requires_frontend_evidence=true`，**When** 用户执行 `frontend-evidence start`，**Then** 系统读取本地 browser gate artifact，写入 loop-run、input、snapshot、report 和 current pointer。
2. **Given** 未执行 browser gate 且没有可用 artifact，**When** 用户执行 `frontend-evidence start`，**Then** 系统返回可读 blocker，并推荐先执行 `ai-sdlc loop frontend-evidence doctor` 判断当前机器已有浏览器证据 provider。
3. **Given** 用户显式传入 `--artifact-path`，**When** 该路径指向项目内合法 YAML，**Then** 系统优先消费该 artifact，而不是写死 latest 路径。

### 用户故事 1A：浏览器 E2E 能力缺失时 provider-first 指引（优先级：P0）

作为小白用户或只会 vibe coding 的用户，我希望当前电脑没有 Playwright、Codex browser、浏览器 MCP 或企业 E2E artifact 时，系统能先告诉我有哪些可用路径和具体下一步，而不是硬推某一个工具。

**优先级说明**：前端 loop 的真实可用性取决于本地浏览器证据来源；该路径必须兼容 Codex、非 Codex、本地仓、公司内网仓和 GitHub 仓。

**独立测试**：执行 `ai-sdlc loop frontend-evidence doctor --provider auto --json`、`--provider codex-browser`、`--provider playwright`，验证推荐 provider、可选安装命令、artifact 导入路径和 fail-readable 输出。

**验收场景**：

1. **Given** `.ai-sdlc/memory/frontend-browser-gate/latest.yaml` 已存在，**When** 用户执行 `frontend-evidence doctor --provider auto`，**Then** 系统优先推荐 `external-artifact` 或已有 artifact 路径，不推荐安装 Playwright。
2. **Given** 用户使用 Codex 且已有 browser 控制能力，**When** 用户执行 `frontend-evidence doctor --provider codex-browser`，**Then** 系统提示用 Codex browser 产生兼容 browser gate artifact，再用 `start --artifact-path` 导入，不要求安装 Playwright。
3. **Given** 用户已有浏览器 MCP/插件，**When** 用户执行 `frontend-evidence doctor --provider browser-mcp`，**Then** 系统提示用该插件产生或转换项目内 artifact，并保留 `start --artifact-path` 兜底。
4. **Given** 用户没有任何可用 provider 且明确选择 Playwright，**When** 用户执行 `frontend-evidence doctor --provider playwright`，**Then** 系统按项目 package manager 输出 npm/pnpm/yarn 的具体安装命令，但不得自动执行安装。
5. **Given** 用户选择不安装任何浏览器 runtime，**When** 用户已有企业内网 E2E、Cypress、Selenium、手工截图验收或其他 agent artifact，**Then** 系统必须允许显式导入项目内兼容 artifact；不能因为不是 Playwright 而拒绝。
6. **Given** 用户无法安装浏览器插件、无法启用 Codex/browser MCP 控制浏览器、也无法生成兼容 artifact，**When** 用户明确执行 `frontend-evidence skip --reason ... --yes`，**Then** 系统必须写入风险接受 artifact 并允许进入 local PR review，不得把用户硬卡在 frontend-evidence loop。

### 用户故事 1B：无法采集浏览器证据时可显式跳过（优先级：P0）

作为无法安装浏览器插件或无法控制浏览器的普通用户，我希望前端证据 loop 可以显式跳过并继续后续 PR review，而不是因为本机环境限制无法完成 SDLC。

**优先级说明**：Loop 提供质量提升，但不能把本地环境能力缺口变成不可恢复阻塞；跳过必须可审计，不能伪装成通过。

**独立测试**：在没有 browser gate artifact 的仓库中执行 `ai-sdlc loop frontend-evidence skip --wi specs/<work-item> --reason "..." --yes --json`，验证 loop closed、`skipped=true`、close artifact 记录 reason，下一步为 `ai-sdlc pr-review start`。

**验收场景**：

1. **Given** implementation loop 已关闭且要求前端证据，**When** 用户执行 skip 且没有 `--yes`，**Then** 系统返回 fail-readable，不写 artifact。
2. **Given** 用户执行 skip 但没有提供具体 `--reason`，**When** CLI 校验输入，**Then** 系统返回 fail-readable，不写 artifact。
3. **Given** 用户确认无法采集浏览器证据并执行 `skip --reason ... --yes`，**When** 命令成功，**Then** 系统写入 `frontend-evidence-input/snapshot/report/close/loop-run/current pointer`，其中 close artifact 记录 `skipped=true`、`skip_reason`、确认人和风险说明。
4. **Given** frontend-evidence loop 已 skip closed，**When** 用户执行 `loop status --type frontend-evidence`，**Then** 输出必须显示 skipped 状态和 skip reason，下一步指向 local PR review。

### 用户故事 2：质量阻塞 fail-closed（优先级：P0）

作为专业前端或测试工程师，我希望空白页、浏览器 fatal console/page error、证据缺失、scope drift、运行时 transient failure 都不能被关闭，避免把不可信前端放进 PR review。

**优先级说明**：这是质量提升的核心收益。

**独立测试**：分别构造 `overall_gate_status=incomplete/blocked`、缺失 receipt、fatal console/page error、artifact namespace drift，验证 start 或 close 返回非零并写入 blocker。

**验收场景**：

1. **Given** browser gate artifact 显示 blank page、fatal console/page error 或 `actual_quality_blocker`，**When** 执行 `frontend-evidence start`，**Then** loop 状态为 `needs_fix`，报告包含 blocker 和修复命令。
2. **Given** browser gate artifact malformed 或与当前 work item scope 不一致，**When** 执行 `frontend-evidence start`，**Then** loop 状态为 `blocked` 或命令失败可读，不允许 close。
3. **Given** latest artifact 来自另一个 spec，**When** 用户未显式传入正确 artifact，**Then** 系统不得误用该 artifact，应提示重新运行或指定 artifact。

### 用户故事 3：告警态可显式确认关闭（优先级：P0）

作为团队负责人，我希望轻量视觉、a11y 或交互告警可以被记录并显式确认，但不能被静默忽略。

**优先级说明**：不把 advisory 当 blocker，同时保留审计证据。

**独立测试**：构造 `passed_with_advisories` artifact，验证 close 无 `--allow-warnings` 失败，带 `--allow-warnings --yes` 后成功写入 close artifact。

**验收场景**：

1. **Given** browser gate 通过但存在 advisory，**When** 用户执行 `close --yes`，**Then** close fail-readable 并提示 `--allow-warnings`。
2. **Given** browser gate 通过但存在 advisory，**When** 用户执行 `close --yes --allow-warnings`，**Then** loop 关闭，close artifact 记录 warning count、warning reason codes 和确认人。
3. **Given** browser gate 完全通过，**When** 用户执行 `close --yes`，**Then** loop 关闭，下一步指向 local PR review。

### 用户故事 4：统一 status/list 与适配性（优先级：P1）

作为 AI-SDLC 用户，我希望 `loop status/list` 能看到前端证据闭环，不管我的代码仓在本地、公司内网还是 GitHub。

**优先级说明**：一等闭环必须进入统一导航面。

**独立测试**：执行 `ai-sdlc loop status --type frontend-evidence` 与 `ai-sdlc loop list --type frontend-evidence`，验证 current、history、malformed artifact、human/JSON 输出。

**验收场景**：

1. **Given** 当前 frontend-evidence loop 存在，**When** 查询 status，**Then** 输出 gate run、work item、overall status、blockers、warnings、desktop/mobile/trace 等证据路径。
2. **Given** 历史 frontend-evidence loops 存在但 current pointer 缺失，**When** 查询 list，**Then** 历史项只提供 inspect guidance，不误导用户关闭旧 loop。
3. **Given** artifact 损坏，**When** 查询 status/list，**Then** 输出 blocked repair guidance，不输出 Python traceback。

### 用户故事 5：未来证据来源可扩展（优先级：P2）

作为框架维护者，我希望本 loop 不把证据来源硬编码为单一路径或单一前端栈，后续可接入其他本地浏览器证据、截图证据或企业内网测试 artifact。

**优先级说明**：满足不同用户代码仓与部署环境的适配性，P2 可以先通过 artifact contract 留口。

**独立测试**：模型和 store 中记录 source type、artifact path、gate run id、provider/style fields，代码不依赖 GitHub PR 或远端 URL。

**验收场景**：

1. **Given** 用户传入项目内 browser gate artifact，**When** start，**Then** report 记录 source type、source path 和 source linkage。
2. **Given** artifact 中 provider/style/frontend stack 不同，**When** start，**Then** loop 只记录并展示，不因为不是默认 Vue3 PrimeVue 而失败。

## 边界情况

- `.ai-sdlc/memory/frontend-browser-gate/latest.yaml` 缺失、不是 YAML、不是 mapping。
- latest artifact 合法但属于另一个 work item/spec。
- artifact 内 `execution_context`、`runtime_session`、`artifact_records`、`bundle_input` schema 不合法。
- artifact namespace 不在 `.ai-sdlc/artifacts/frontend-browser-gate/<gate-run-id>/`。
- required probe receipt 缺失、unexpected receipt、evidence missing、transient run failure。
- console/page error、blank/near-blank body、actual quality blocker。
- 只有 advisory warnings。
- implementation loop 未关闭、work item 不匹配、implementation report 不要求前端证据。
- current pointer 指向缺失或 malformed artifact。
- Codex/browser MCP/企业 E2E provider 存在但 CLI 无法自动探测，只能由用户显式 `--provider` 或导入 artifact 声明。
- Playwright 未安装、Node/package manager 缺失、浏览器 runtime 缺失，但用户已有其他 browser provider。
- 用户既不能安装浏览器插件，也不能使用 Codex/browser MCP 或企业 E2E artifact，此时必须允许显式 skip，不得硬卡。

## 需求

### 功能需求

- **FR-001**：系统必须提供 `ai-sdlc loop frontend-evidence start`，支持 `--wi`、`--implementation-loop-id`、`--artifact-path`、`--loop-id`、`--dry-run`、`--json`。
- **FR-002**：`start` 必须要求同一 work item 的 implementation loop 已关闭，且 implementation report 标记 `requires_frontend_evidence=true`。
- **FR-003**：`start` 必须消费本地 browser gate artifact，默认路径为 `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`，但允许显式指定项目内 artifact path。
- **FR-004**：系统必须校验 artifact schema、scope linkage、gate run namespace、required receipts 和 source path 安全性。
- **FR-005**：系统必须写入 `.ai-sdlc/loops/frontend-evidence/<loop-id>/loop-run.json`、`frontend-evidence-input.json`、`frontend-evidence-snapshot.json`、`frontend-evidence-report.json`、`frontend-evidence-report.md` 和 current pointer。
- **FR-006**：系统必须把 `passed` 映射为 `passed`，把 `passed_with_advisories` 映射为 `needs_user`，把 `blocked/incomplete` 或 artifact 校验失败映射为 `needs_fix` 或 `blocked`。
- **FR-007**：系统必须把 blocker、warning、reason code、check receipt、screenshot/trace/artifact refs、gate run id、provider/style fields 写入 report。
- **FR-008**：系统必须提供 `ai-sdlc loop frontend-evidence status`，并复用统一 `loop status --type frontend-evidence`。
- **FR-009**：系统必须提供 `ai-sdlc loop frontend-evidence close --yes [--allow-warnings]`，只有无 blocker 且无未确认 warning 时才能关闭。
- **FR-010**：close 成功后必须写入 `frontend-evidence-close.json`，loop-run 状态改为 `closed`，下一步指向 `ai-sdlc pr-review start`。
- **FR-011**：human 输出必须包含 `Result`、`Next`、`Loop ID`、`Work item`、`Gate status`、`Blockers`、`Warnings`、`Artifacts`，小白用户无需理解内部 schema 也能知道下一步。
- **FR-012**：JSON 输出不得混入 Rich 文本，字段必须稳定可解析。
- **FR-013**：本 loop 不得调用模型、不得调用 Codex 云端 review、不得要求 CI 调用模型、不得假设 GitHub PR。
- **FR-014**：本 loop 不得写业务代码或前端代码，只写 `.ai-sdlc/loops/frontend-evidence/` 及 current pointer。
- **FR-015**：系统必须接入 `verify constraints` 和 README，防止文档宣称的 command surface 与实现漂移。
- **FR-016**：系统必须提供只读 `ai-sdlc loop frontend-evidence doctor`，支持 `--provider auto|codex-browser|browser-mcp|external-artifact|playwright`、`--frontend-dir`、`--browser`、`--json`。
- **FR-017**：`doctor --provider auto` 必须 provider-first：已有 artifact 或已配置 browser provider 优先，Playwright 只能作为可选 provider，不能被硬编码为唯一推荐。
- **FR-018**：当用户显式选择 `codex-browser` 或 `browser-mcp` 时，系统必须说明该 provider 负责产生浏览器证据 artifact，`frontend-evidence` 负责导入和验收 artifact，不得要求安装 Playwright。
- **FR-019**：当用户显式选择 `playwright` 时，系统必须输出 npm/pnpm/yarn 对应的具体安装命令和浏览器安装命令；自动安装必须另有显式确认，不得静默执行。
- **FR-020**：缺失 browser gate artifact 时，`start` 必须优先引导用户执行 `frontend-evidence doctor`，避免把 provider 缺失、artifact 未导入和 Playwright 缺失混为一类问题。
- **FR-021**：系统必须提供 `ai-sdlc loop frontend-evidence skip --wi <work-item> --reason <text> --yes`，用于用户无法采集浏览器证据时显式跳过。
- **FR-022**：`skip` 必须要求 closed same-work-item implementation loop、明确 `--reason` 和 `--yes`；缺任一条件不得写入 artifact。
- **FR-023**：`skip` 成功后必须写入 close artifact，记录 `skipped=true`、`skip_reason`、`skip_risk_acknowledgement`、`closed_by`，并把 loop 状态置为 `closed`、下一步指向 local PR review。
- **FR-024**：`loop status/list --type frontend-evidence` 必须展示 skipped 与 skip reason，避免把跳过误读为浏览器证据通过。

### 关键实体

- **FrontendEvidenceInput**：一次 loop start 的输入快照，包括 work item、implementation loop、source artifact path 和 source type。
- **FrontendEvidenceSnapshot**：从 browser gate artifact 提取的证据快照，包括 gate run、overall status、runtime state、execution context、receipts 和 artifact refs。
- **FrontendEvidenceReport**：验收报告，包括 loop status、gate status、blockers、warnings、reason codes、证据路径和 next action。
- **FrontendEvidenceClose**：关闭确认，包括确认人、是否允许 warnings、report path 和下一步 loop。
- **FrontendEvidenceCurrentPointer**：当前 frontend-evidence loop 指针。
- **FrontendEvidenceProviderCheck**：只读 provider readiness 结果，包括 provider id、是否可用、是否被选中、安装命令、运行命令、替代路径和安全提示。
- **FrontendEvidenceDoctorResult**：provider-first 诊断结果，包括 requested provider、recommended provider、artifact 可用性、provider 候选和 next guidance。
- **FrontendEvidenceSkipOptions**：显式跳过输入，包括 work item、implementation loop、skip reason、确认人和 `--yes`。

## 成功标准

### 可度量结果

- **SC-001**：`tests/unit/test_frontend_evidence_loop.py` 覆盖 pass、advisory、blocked、missing artifact、scope mismatch、malformed artifact、close gating。
- **SC-002**：`tests/integration/test_cli_loop.py` 覆盖 `frontend-evidence start/status/close` human 与 JSON 输出。
- **SC-003**：`tests/unit/test_loop_status.py` 覆盖 `loop status/list --type frontend-evidence` current、history 和 malformed pointer。
- **SC-004**：`tests/unit/test_verify_constraints.py` 覆盖 README/CLI/constraint surface。
- **SC-005**：`tests/unit/test_frontend_evidence_loop.py` 与 `tests/integration/test_cli_loop.py` 覆盖 provider-first doctor，不硬推 Playwright，并覆盖显式 Playwright 安装命令展示。
- **SC-006**：`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py` 和 release E2E 覆盖 skip 路径，证明无浏览器控制能力时不会硬卡。
- **SC-007**：focused regression、ruff、mypy、`uv run ai-sdlc verify constraints`、`workitem close-check`、Codex review、required checks 全部通过后才合并。

---
frontend_evidence_class: framework_capability
---
