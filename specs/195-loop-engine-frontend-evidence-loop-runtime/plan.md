# 实施计划：Loop Engine Frontend Evidence Loop Runtime

**编号**：`195-loop-engine-frontend-evidence-loop-runtime` | **日期**：2026-07-01 | **规格**：specs/195-loop-engine-frontend-evidence-loop-runtime/spec.md

## 概述

交付 `frontend-evidence` 一等闭环。该 loop 位于 implementation close 之后、local PR review 之前，先通过 provider-first doctor 判断当前机器可用的浏览器证据来源，再消费本地前端 browser gate artifact，生成稳定 Loop Engine artifact，并通过 close gate 保证前端质量证据不会丢失或被误判。

## 技术背景

**语言/版本**：Python 3.11+，Typer CLI，Pydantic v2。
**主要依赖**：现有 `frontend_browser_gate_runtime`、`frontend_gate_verification`、`ProgramService` browser gate artifact contract、Loop Engine artifact store；Codex browser、浏览器 MCP/插件、企业 E2E 工具通过项目内 artifact contract 接入，不作为 runtime 硬依赖。
**存储**：`.ai-sdlc/loops/frontend-evidence/<loop-id>/` 和 `.ai-sdlc/loops/frontend-evidence/current-frontend-evidence.json`。
**测试**：pytest unit/integration、ruff、mypy、verify constraints、workitem close-check。
**目标平台**：macOS、Linux、Windows PowerShell/cmd；不依赖 CI 网络访问模型。
**约束**：不调用模型、不调用云端 PR review、不写业务/前端代码、不硬编码 GitHub 或远端 preview，不把 Vue3 PrimeVue 当成唯一合法前端栈，不把 Playwright 当成唯一合法浏览器 provider。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 本地 artifact truth 优先 | 只消费 `.ai-sdlc/memory/frontend-browser-gate/latest.yaml` 或显式项目内 artifact path，并把引用写入 loop report |
| Fail-closed | 缺失、损坏、scope drift、namespace drift、quality blocker、transient failure 均阻断 close |
| 小白可执行 | human 输出包含 Result/Next/Blocker/Artifacts，不要求用户理解内部 schema |
| 高级可自动化 | 所有命令支持 `--json`，字段稳定且无 Rich 文本 |
| 适配多场景 | artifact contract 记录 provider/style/source，不依赖 GitHub、远端 URL、单一前端栈或单一浏览器 provider |

## 项目结构

### 文档结构

```text
specs/195-loop-engine-frontend-evidence-loop-runtime/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/frontend_evidence_models.py
src/ai_sdlc/core/frontend_evidence_store.py
src/ai_sdlc/core/frontend_evidence_loop.py
src/ai_sdlc/core/loop_status.py
src/ai_sdlc/cli/loop_cmd.py
src/ai_sdlc/core/verify_constraints.py
README.md
tests/unit/test_frontend_evidence_loop.py
tests/unit/test_loop_status.py
tests/integration/test_cli_loop.py
tests/unit/test_verify_constraints.py
```

## 阶段计划

### Phase 0：需求与设计冻结

**目标**：替换初始化模板，冻结 frontend-evidence 的真实 PRD、实施计划、任务拆解和归档规则。
**产物**：spec.md / plan.md / tasks.md / task-execution-log.md / program-manifest.yaml。
**验证方式**：`git diff --check`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc verify constraints`。
**回退方式**：回退 WI-195 文档和 manifest 变更。

### Phase 1：核心模型与 artifact store

**目标**：定义 FrontendEvidenceInput、Snapshot、Report、Close、CurrentPointer 和 artifact path helper。
**产物**：`frontend_evidence_models.py`、`frontend_evidence_store.py`、unit tests。
**验证方式**：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`。
**回退方式**：删除新增模型/store 文件和测试。

### Phase 2：start/close runtime

**目标**：实现 implementation gate、browser gate artifact ingestion、report classification、close gating。
**产物**：`frontend_evidence_loop.py`、unit tests。
**验证方式**：unit tests 覆盖 pass、advisory、blocked、malformed、scope mismatch、close gating。
**回退方式**：移除 runtime 接入，保留文档说明未完成。

### Phase 3：CLI 与统一 status/list

**目标**：注册 `ai-sdlc loop frontend-evidence doctor/start/status/close`，扩展 `loop status/list --type frontend-evidence`。
**产物**：`loop_cmd.py`、`loop_status.py`、integration tests。
**验证方式**：`uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`。
**回退方式**：移除 Typer 子命令和 status/list 分支。

### Phase 4：文档、约束与最终收口

**目标**：README 与 verify constraints 对齐，跑完整 focused regression，提交、PR、Codex review、checks、merge。
**产物**：README、verify constraints、execution log、handoff、PR。
**验证方式**：focused pytest、ruff、mypy、verify constraints、truth sync、workitem close-check、GitHub checks、Codex review。
**回退方式**：PR 不合并或 revert feature commit。

## 工作流计划

### 工作流 A：用户执行 frontend evidence loop

**范围**：implementation loop 已关闭且需要前端证据。
**影响范围**：只写 `.ai-sdlc/loops/frontend-evidence/`。
**验证方式**：start writes artifact，status/list reads artifact，close enforces gates。
**回退方式**：删除该 loop id 目录和 current pointer。

### 工作流 A1：浏览器证据 provider-first readiness

**范围**：用户没有 browser gate artifact，或不确定当前电脑能否做浏览器 E2E。
**影响范围**：只读检查项目内 artifact、package manager、Node、显式 provider 选择和环境声明；不安装依赖，不写业务代码。
**验证方式**：`doctor --provider auto` 优先已有 artifact/已配置 provider；`doctor --provider codex-browser` 和 `--provider browser-mcp` 输出 artifact 导入路径；`doctor --provider playwright` 才展示具体 npm/pnpm/yarn 安装命令。
**回退方式**：无写入；用户可改用其他 provider 或显式 `--artifact-path`。

### 工作流 B：质量阻塞修复

**范围**：browser gate 返回 blocked/incomplete 或 artifact 不可信。
**影响范围**：loop report 给出 blocker 和下一步，不写代码。
**验证方式**：close 返回非零，next action 指向 browser gate rerun或 artifact 修复。
**回退方式**：用户修复前端或重新运行 browser gate 后重新 start。

### 工作流 C：告警确认关闭

**范围**：browser gate `passed_with_advisories`。
**影响范围**：close artifact 记录 warnings 和 allow flag。
**验证方式**：不带 `--allow-warnings` 失败，带 flag 成功。
**回退方式**：删除 close artifact 后重新 close。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| artifact ingestion | unit tests 构造 browser gate YAML | CLI start JSON |
| implementation gate | unit tests 构造 closed/non-closed implementation loop | integration CLI |
| quality blocker fail-closed | unit tests blocked/incomplete/advisory | close command exit code |
| status/list | loop_status unit tests | CLI human output snapshots |
| provider doctor | frontend_evidence unit tests | CLI doctor human/JSON |
| docs/constraints | verify constraints unit tests | `uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否在本 loop 内主动运行 browser gate | 已决：不主动运行；doctor 做 provider-first readiness，start 只消费 artifact | 无 |
| 是否支持非 latest artifact | 已决：P0 支持显式 `--artifact-path` | 无 |
| 是否硬推 Playwright | 已决：不得硬推；Codex browser、browser MCP、external artifact 优先于可选 Playwright 安装 | 无 |
| 是否支持其他未来证据格式 | P2 留 source contract，不在本 PR 实现多格式解析 | 不阻塞 P0/P1 |

## 实施顺序建议

1. 冻结 WI-195 文档和 manifest。
2. 新增 models/store 和 focused unit tests。
3. 实现 start/close runtime。
4. 接入 provider-first doctor、CLI 和 status/list。
5. 对齐 README/verify constraints，跑最终验证。
6. 提交、推送、开 PR、请求 Codex review，处理 review/checks 后合并。
