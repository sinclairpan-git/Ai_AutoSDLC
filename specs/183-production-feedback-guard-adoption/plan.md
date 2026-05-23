---
related_doc:
  - "docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md"
---
# 实施计划：生产反馈驱动的任务守卫、注释规范与半途接入优化

**编号**：`183-production-feedback-guard-adoption` | **日期**：2026-05-23 | **规格**：specs/183-production-feedback-guard-adoption/spec.md

## 概述

本 work item 将生产反馈归档落地为 AI-SDLC 的正式治理能力。核心策略是放弃不可证明的 adapter `verified_loaded` 主路径，把控制点放到“代码修改必须绑定可执行任务”。实现顺序优先建立 `tasks.md` 可执行 schema 与 task guard，再补注释/编码质量底线，最后实现 brownfield adopt 半途接入。

## 技术背景

**语言/版本**：Python 3.11+
**主要依赖**：Typer CLI、Pydantic models、现有 gate / verify / workitem / telemetry 模块
**存储**：Markdown formal docs、`.ai-sdlc/state/`、`.ai-sdlc/adoption/`、`program-manifest.yaml`
**测试**：pytest 单元测试、CLI 集成测试、verify constraints、必要时补 fixture
**目标平台**：macOS、Linux、Windows PowerShell
**约束**：

- 不依赖外部 AI 宿主返回 `AGENTS.md` 加载证明。
- 不覆盖用户原始任务进度文件。
- 不强制全仓库历史中文和注释清洗，只检查新增或修改范围。
- 不用规则噪音替代真正可验证的代码修改控制点。
- 每个阶段产物必须通过两个对抗 agent 评审，无必须修订项后才能继续。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Persist decisions to the repository | 所有方案、评审结论、实现证据写入 `docs/`、`specs/182-*` 与 execution log。 |
| Prefer contract-level verification before closure | 先定义 executable task schema、guard contract、adoption map contract，再实现 CLI 与检查。 |
| Keep docs and code traceable | 每批任务与 `tasks.md`、execution log、测试命令、PR review 绑定。 |

## 项目结构

### 文档结构

```text
docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md
specs/183-production-feedback-guard-adoption/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 预计源码结构

```text
src/ai_sdlc/core/
├── executable_task.py              # 解析并判定 tasks.md 可执行任务
├── task_guard.py                   # preflight / during / postflight 守卫
├── comment_policy.py               # 注释策略与技术栈规则
├── text_quality.py                 # 简体中文、UTF-8、乱码检查
└── adoption.py                     # brownfield adopt 核心模型与映射

src/ai_sdlc/cli/
├── workitem_cmd.py                 # 暴露 guard / task 检查或复用 workitem 子命令
├── commands.py                     # 用户可见 status / init 文案调整
└── adopt_cmd.py                    # 接入已有项目入口（如采用独立模块）

tests/unit/
tests/integration/
```

实际落点以现有模块边界为准，优先复用 `execute_authorization.py`、`plan_check.py`、`workitem_truth.py`、`verify_constraints.py`、`existing_project_init.py` 等已有能力，不做大规模重构。

## 阶段计划

### Phase 0：正式文档冻结与对抗评审

**目标**：将归档方案转为正式 `spec / plan / tasks`，通过两个对抗 agent 评审。
**产物**：本目录四件套、评审结论、execution log。
**验证方式**：两个对抗 agent 均无必须修订项；`uv run ai-sdlc verify constraints`。
**回退方式**：回退本 work item 文档改动，不影响运行时代码。

### Phase 1：Executable Task Schema 与 Guard 核心

**目标**：实现可解析任务模型和 preflight / during / postflight guard。
**产物**：任务解析、可执行判定、guard 结果、CLI/status surface、测试。
**验证方式**：单元测试覆盖字段缺失、模板任务、重复 id、状态枚举、scope 越界、postflight log。
**回退方式**：产品代码修改主路径必须硬阻断 `BLOCK_CODE_PREPARE_TASKS`；如需兼容旧流程，只能在诊断命令中降级为 advisory，不得允许代码修改绕过 executable task。

### Phase 2：Adapter 口径与用户可见文案

**目标**：把不可证明宿主加载从用户主路径移除，聚焦 workflow guarded。
**产物**：init/status/adapter 模板文案、README/USER_GUIDE 更新、约束检查。
**验证方式**：CLI snapshot / integration tests；verify constraints。
**回退方式**：恢复旧文案，不影响 task guard 内核。

### Phase 3：注释与中文编码质量底线

**目标**：实现注释策略、原注释保护要求、简体中文 UTF-8 防乱码检查。
**产物**：policy 文档/模板、检查器、测试夹具。
**验证方式**：Java/Go/Python/Vue2/JS/TS 样例测试；乱码/BOM/mojibake/简繁测试。
**回退方式**：检查器分级上线；新增/修改范围内 UTF-8 decode 失败、替换字符和高置信 mojibake 作为 blocker，BOM、疑似繁体和低置信乱码先作为 warning/advisory，避免误伤生产。

### Phase 4：Brownfield Adopt 半途接入

**目标**：实现“接入已有项目”扫描、adoption map、桥接产物和继续点推荐。
**产物**：adoption models、scanner、CLI、bridge docs、状态映射、测试。
**验证方式**：JSON 进度、README TODO、issue export、多个 in-progress、无法识别 JSON、非 git 项目、大目录忽略、扫描预算等测试。
**回退方式**：adopt 不改用户原文件；失败时只输出临时建议。

### Phase 5：收口、PR、发布补丁版本

**目标**：完成全量验证、PR、review、CI、补丁版本发布。
**产物**：PR、review 处理记录、release notes、版本更新。
**验证方式**：`uv run pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、GitHub checks、Codex review。
**回退方式**：不发布或撤回 release；保持 PR 未合并。

## 工作流计划

### 工作流 A：文档与评审闭环

**范围**：正式文档、对抗评审、任务拆解。
**影响范围**：`docs/`、`specs/182-*`。
**验证方式**：两个 agent 评审无阻塞；verify constraints。
**回退方式**：还原文档提交。

### 工作流 B：Guard 最小闭环

**范围**：executable task schema、preflight、during、postflight。
**影响范围**：core/task parsing、status/guard surfaces、tests。
**验证方式**：focused pytest + CLI tests。
**回退方式**：保留 parser，关闭阻塞行为。

### 工作流 C：质量底线

**范围**：注释、原注释保护、中文编码检查。
**影响范围**：policy、verify/check、templates、tests。
**验证方式**：语言样例和编码样例测试。
**回退方式**：降级为 warning。

### 工作流 D：Brownfield Adopt

**范围**：已有项目事实源扫描、映射、桥接、继续点。
**影响范围**：CLI、core adoption、tests、docs。
**验证方式**：fixture-based CLI integration tests。
**回退方式**：adopt 只读输出，不写桥接产物。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `tasks.md` 可执行判定 | `tests/unit/test_executable_task.py` | CLI guard fixture |
| Guard preflight/during/postflight | `tests/unit/test_task_guard.py` | `tests/integration/test_cli_task_guard.py` |
| Adapter 用户口径 | CLI integration snapshot | `verify constraints` 文档 token 检查 |
| 注释策略 | policy unit tests | 语言样例 fixture |
| 中文编码检查 | mojibake/BOM fixture tests | Windows PowerShell smoke |
| Brownfield adopt | JSON/README/git fixture integration | adoption map schema tests |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| Guard 是否一开始硬阻塞产品代码修改 | 已收敛：产品代码修改主路径必须硬阻断；仅只读诊断命令可 advisory 展示 | Phase 1 |
| adopt CLI 命令是否独立为 `ai-sdlc adopt` 或挂在 `workitem adopt` | 待实现前看 Typer 结构 | Phase 4 |
| 中文简繁检测是否引入第三方库 | 倾向先内置 pattern + 白名单，避免新增依赖 | Phase 3 |

## 实施顺序建议

1. 冻结本 formal work item，并通过两个对抗 agent 评审。
2. 实现 executable task parser 和 schema 测试。
3. 实现 task guard preflight/during/postflight 与 focused CLI/status surface。
4. 调整 adapter 用户口径，移除 `verified_loaded` 主路径阻塞表述。
5. 实现注释策略与中文编码检查。
6. 实现 brownfield adopt。
7. 全量验证、PR、review、CI、补丁发布。
