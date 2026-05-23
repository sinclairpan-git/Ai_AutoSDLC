---
related_doc:
  - "docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md"
---
# 任务分解：生产反馈驱动的任务守卫、注释规范与半途接入优化

**编号**：`183-production-feedback-guard-adoption` | **日期**：2026-05-23
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline and adversarial review
Batch 2: executable task schema
Batch 3: next executable task guard
Batch 4: adapter wording and user-facing workflow state
Batch 5: comment and text quality policies
Batch 6: brownfield adopt
Batch 7: release closure
```

## 固定批次门禁

除 Batch 1 的文档评审外，Batch 2-7 每批完成后都必须满足以下门禁，才能进入下一批：

1. 本批实现完成，相关 `tasks.md` 状态和 `task-execution-log.md` 已同步。
2. 本批声明的 focused tests 已通过。
3. 若本批影响共享行为，补跑相关集成测试或 `uv run ai-sdlc verify constraints`。
4. 两个对抗 agent 分别从 UX 和 AI-native / AI-coding 角度评审本批生成物，无必须修订项。
5. 如果对抗 agent、PR review 或 CI 提出阻塞问题，必须修复、重测、复审后才能继续。

---

## Batch 1：formal baseline and adversarial review

### Task 1.1 冻结已评审归档文档

- task_id: T11
- status: done
- priority: P0
- depends: none
- scope:
  - docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md
- acceptance:
  - 归档文档包含 adapter 口径、task guard、注释规范、中文编码、brownfield adopt 全部生产反馈。
  - 两个对抗 agent 二轮评审均无必须修订项。
- verify:
  - 人工核对二轮 agent 结论。
  - git diff -- docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md
- notes:
  - 本任务已在创建 formal work item 前完成，后续 execution log 需记录提交哈希。

### Task 1.2 完成 formal spec / plan / tasks 并通过对抗评审

- task_id: T12
- status: done
- priority: P0
- depends: T11
- scope:
  - specs/183-production-feedback-guard-adoption/spec.md
  - specs/183-production-feedback-guard-adoption/plan.md
  - specs/183-production-feedback-guard-adoption/tasks.md
  - specs/183-production-feedback-guard-adoption/task-execution-log.md
  - program-manifest.yaml
- acceptance:
  - spec 明确三类用户故事和 FR / SC。
  - plan 明确阶段、验证策略、回退策略。
  - tasks 拆分到可实现批次，并包含 scope / acceptance / verify。
  - 两个对抗 agent 对四件套无必须修订项。
- verify:
  - uv run ai-sdlc verify constraints
  - 两个对抗 agent 二轮评审。
- notes:
  - 进入 Batch 2 前必须关闭本任务。

## Batch 2：executable task schema

### Task 2.1 冻结 executable task schema contract

- task_id: T21
- status: done
- priority: P0
- depends: T12
- scope:
  - specs/183-production-feedback-guard-adoption/plan.md
  - specs/183-production-feedback-guard-adoption/tasks.md
  - src/ai_sdlc/core/executable_task.py
  - tests/unit/test_executable_task.py
- acceptance:
  - 明确定义 heading 规则：本期仅 `### Task <major>.<minor> <title>` 可作为任务块入口；任何后续兼容格式必须进入显式兼容列表并补测试。
  - 明确定义 `task_id` 正则、重复 id 处理、未知字段策略、字段边界和多行列表解析规则。
  - 明确定义 `scope` 支持 repo-relative path 和受限 glob，不允许绝对路径或越权路径。
  - 明确定义 `acceptance / verify` 的多行解析方式和缺字段错误。
- verify:
  - uv run pytest tests/unit/test_executable_task.py -q
- notes:
  - 本任务先写测试和 schema contract，避免 parser 实现靠现场猜。

### Task 2.2 实现 executable task parser

- task_id: T22
- status: done
- priority: P0
- depends: T21
- scope:
  - src/ai_sdlc/core/executable_task.py
  - tests/unit/test_executable_task.py
- acceptance:
  - parser 能从 `tasks.md` 解析 task id、status、goal、scope、acceptance、verify、notes。
  - task id 正则、重复 id、缺字段、多行列表、无效状态均有测试覆盖。
  - `needs-review`、`blocked`、`done` 的可执行规则符合 spec。
  - 两个对抗 agent 对 schema 与 parser 测试无必须修订项后，才能进入 Batch 3。
- verify:
  - uv run pytest tests/unit/test_executable_task.py -q

### Task 2.3 识别模板任务和占位任务

- task_id: T23
- status: done
- priority: P0
- depends: T22
- scope:
  - src/ai_sdlc/core/executable_task.py
  - tests/unit/test_executable_task.py
- acceptance:
  - 含“待补充”“TODO”“placeholder”等占位内容的任务不可执行。
  - 指向示例路径、占位模板任务、缺验证方式、缺 scope 的任务不可执行；真实任务明确声明要修改模板文件时允许。
  - 错误信息能说明具体缺失字段或占位原因。
  - 两个对抗 agent 对模板/占位识别无必须修订项。
- verify:
  - uv run pytest tests/unit/test_executable_task.py -q

## Batch 3：next executable task guard

### Task 3.1 实现自动准备最小任务

- task_id: T31
- status: done
- priority: P0
- depends: T22,T23
- scope:
  - src/ai_sdlc/core/task_preparation.py
  - src/ai_sdlc/core/task_guard.py
  - tests/unit/test_task_preparation.py
- acceptance:
  - 缺 active work item 时自动创建最小 work item 候选，不要求用户理解 checkpoint / stage。
  - 缺 `plan.md / tasks.md` 时自动生成最小 plan/tasks 候选。
  - 紧急小修自动生成极简 task，且包含 scope、acceptance、verify。
  - 在 task executable 前不得修改产品代码。
- verify:
  - uv run pytest tests/unit/test_task_preparation.py -q

### Task 3.2 实现 guard preflight

- task_id: T32
- status: done
- priority: P0
- depends: T31
- scope:
  - src/ai_sdlc/core/task_guard.py
  - src/ai_sdlc/core/execute_authorization.py
  - tests/unit/test_task_guard.py
- acceptance:
  - 有可执行任务时返回 `ALLOW_CODE_WITH_TASK`。
  - 缺 active work item、缺 plan/tasks、只有模板任务时返回 `BLOCK_CODE_PREPARE_TASKS` 并附自动准备动作。
  - 产品代码修改主路径必须把 `BLOCK_CODE_PREPARE_TASKS` 视为硬阻断。
  - 用户可见文案不暴露内部状态名。
- verify:
  - uv run pytest tests/unit/test_task_guard.py -q

### Task 3.3 实现 during / postflight 范围检查

- task_id: T33
- status: done
- priority: P1
- depends: T32
- scope:
  - src/ai_sdlc/core/task_guard.py
  - tests/unit/test_task_guard.py
  - tests/integration/test_cli_workitem_guard.py
- acceptance:
  - during 阶段能识别 diff 是否超出 task scope。
  - postflight 不宣称机器理解自然语言 acceptance；只要求可验证证据模型：changed paths、allowed companion files、verification command、execution log entry。
  - 明确伴随文件分类：product、test、doc、snapshot、migration、config、generated。
  - 伴随文件超出业务 scope 时必须被规则允许、写入 log，或要求更新任务。
- verify:
  - uv run pytest tests/unit/test_task_guard.py tests/integration/test_cli_workitem_guard.py -q

### Task 3.4 暴露 CLI / status surface

- task_id: T34
- status: done
- priority: P1
- depends: T32,T33
- scope:
  - src/ai_sdlc/cli/workitem_cmd.py
  - src/ai_sdlc/telemetry/readiness.py
  - tests/integration/test_cli_workitem_guard.py
- acceptance:
  - CLI 能输出当前 next executable task 或自动准备任务建议。
  - status surface 能显示 workflow guarded 状态，但普通文案不使用内部术语。
  - 不能要求用户手动跑 `adapter status` 或 `run --dry-run` 才能继续。
  - 两个对抗 agent 对 Batch 3 生成物无必须修订项。
- verify:
  - uv run pytest tests/integration/test_cli_workitem_guard.py -q

## Batch 4：adapter wording and user-facing workflow state

### Task 4.1 调整 adapter / init / status 用户口径

- task_id: T41
- status: done
- priority: P0
- depends: T34
- scope:
  - src/ai_sdlc/adapters/codex/AI-SDLC.md
  - src/ai_sdlc/adapters/cursor/AI-SDLC.md
  - src/ai_sdlc/adapters/claude_code/AI-SDLC.md
  - AGENTS.md
  - USER_GUIDE.zh-CN.md
  - src/ai_sdlc/cli/beginner_guidance.py
  - tests/integration/test_cli_status.py
- acceptance:
  - 用户主路径不再把不可验证宿主加载表述为失败或待处理阻塞。
  - 文案聚焦“项目规则已安装，写代码前会先确认当前任务”。
  - 仍保留内部诊断，供排障使用。
  - 两个对抗 agent 对 adapter / status 用户口径无必须修订项。
- verify:
  - uv run pytest tests/integration/test_cli_status.py -q
  - uv run ai-sdlc verify constraints

## Batch 5：comment and text quality policies

### Task 5.1 实现注释语言信号链路

- task_id: T51
- status: todo
- priority: P0
- depends: T12
- scope:
  - src/ai_sdlc/core/comment_policy.py
  - src/ai_sdlc/adapters/codex/AI-SDLC.md
  - AGENTS.md
  - templates/tasks-template.md
  - tests/unit/test_comment_policy.py
- acceptance:
  - adapter prompt 要求 AI 根据当前或近期用户主要沟通语言决定新增注释语言。
  - task notes / execution log 能记录本次 comment language 决策和兜底来源。
  - 项目默认语言作为兜底，不覆盖清晰的当前对话语言。
- verify:
  - uv run pytest tests/unit/test_comment_policy.py -q

### Task 5.2 落地注释策略与原注释保护

- task_id: T52
- status: todo
- priority: P0
- depends: T51
- scope:
  - src/ai_sdlc/core/comment_policy.py
  - rules/code-review.md
  - src/ai_sdlc/rules/code-review.md
  - templates/tasks-template.md
  - tests/unit/test_comment_policy.py
- acceptance:
  - 策略覆盖 Java、Go、Python、Vue2、JavaScript、TypeScript。
  - 必要注释、禁止注释、原注释保护、删除注释记录原因均有测试或文档约束。
  - Java / Python / TypeScript 规则避免对普通内部方法或类型清晰字段制造噪音注释。
  - 两个对抗 agent 对注释策略无必须修订项。
- verify:
  - uv run pytest tests/unit/test_comment_policy.py -q
  - uv run ai-sdlc verify constraints

### Task 5.3 实现简体中文和编码质量检查

- task_id: T53
- status: todo
- priority: P0
- depends: T52
- scope:
  - src/ai_sdlc/core/text_quality.py
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_text_quality.py
  - tests/integration/test_cli_verify_constraints.py
- acceptance:
  - 检查覆盖 UTF-8 decode、BOM、替换字符、常见 mojibake pattern。
  - 明确 finding 分级：新增/修改范围内 UTF-8 decode 失败、替换字符和高置信 mojibake 为 blocker；BOM、疑似繁体、低置信乱码为 warning，除非项目显式升级为 blocker。
  - 只检查新增或修改中文片段，支持白名单和繁体项目例外。
  - 白名单必须支持归档文档中的 mojibake 示例，避免测试/说明文本被误报为生产乱码。
  - 测试夹具覆盖常见 UTF-8 / GBK 错读样例。
  - diff-based text extraction 有测试，避免退化成全文件扫描。
  - 两个对抗 agent 对中文编码检查无必须修订项。
- verify:
  - uv run pytest tests/unit/test_text_quality.py tests/integration/test_cli_verify_constraints.py -q

## Batch 6：brownfield adopt

### Task 6.1 实现 adoption models 与 source discovery

- task_id: T61
- status: todo
- priority: P0
- depends: T21
- scope:
  - src/ai_sdlc/core/adoption.py
  - tests/unit/test_adoption.py
- acceptance:
  - 定义 AdoptionSource、AdoptionMap、confidence、continue point 基础模型。
  - 自动发现候选任务源，但默认忽略大目录和构建产物。
  - 扫描预算明确：默认候选文件数、单文件最大读取字节数、最近 commit 数均有上限且可配置。
  - 非 git 项目或无有效 git 历史时，降级使用文件系统、JSON/Markdown 任务源和项目结构，不要求用户补 git 信息。
  - 不覆盖用户原任务文件。
- verify:
  - uv run pytest tests/unit/test_adoption.py -q

### Task 6.2 实现 JSON schema inference

- task_id: T62
- status: todo
- priority: P0
- depends: T61
- scope:
  - src/ai_sdlc/core/adoption.py
  - tests/unit/test_adoption.py
- acceptance:
  - 自动识别 id、title、description、status、progress、children、dependencies、files、owner、时间和 blocker 字段。
  - 字段缺失时给出置信度而不是失败。
  - 支持嵌套任务和扁平任务列表。
- verify:
  - uv run pytest tests/unit/test_adoption.py -q

### Task 6.3 实现 markdown / issue / git source adapters

- task_id: T63
- status: todo
- priority: P0
- depends: T61
- scope:
  - src/ai_sdlc/core/adoption.py
  - tests/unit/test_adoption.py
- acceptance:
  - 支持 README/TODO、markdown 计划、issue export、branch、diff、最近 commit、测试和项目结构作为事实源。
  - 默认忽略大目录和构建产物，最近 commit、候选文件数和单文件读取大小有数量边界。
  - 非 git 项目必须自动跳过 git source adapter，并保留其他 source adapter 的导入能力。
  - 不覆盖用户原任务文件。
- verify:
  - uv run pytest tests/unit/test_adoption.py -q

### Task 6.4 实现置信度评分与 adoption map

- task_id: T64
- status: todo
- priority: P0
- depends: T62,T63
- scope:
  - src/ai_sdlc/core/adoption.py
  - tests/unit/test_adoption.py
- acceptance:
  - confidence scoring 明确来源：字段完整度、状态可归一化、文件路径命中、commit/diff 相关度、更新时间。
  - 高置信自动导入，中置信摘要确认，低置信 `needs-review` 且不可作为 active task。
  - adoption map 记录 external id、AI-SDLC task id、状态、来源、置信度。
- verify:
  - uv run pytest tests/unit/test_adoption.py -q

### Task 6.5 实现桥接产物与继续点推荐

- task_id: T65
- status: todo
- priority: P0
- depends: T64
- scope:
  - src/ai_sdlc/core/adoption.py
  - tests/unit/test_adoption.py
  - tests/integration/test_cli_adopt.py
- acceptance:
  - 多个进行中任务按 diff、commit、更新时间和依赖状态推荐继续点。
  - JSON 无法识别时降级生成临时继续点。
  - 无 git 历史时按任务源更新时间、文件路径命中和用户最近输入推断继续点，不把补充证据压力转嫁给用户。
  - 生成 bridge docs 与 checkpoint 候选，不覆盖原任务文件。
  - 两个对抗 agent 对 adopt core 生成物无必须修订项。
- verify:
  - uv run pytest tests/unit/test_adoption.py tests/integration/test_cli_adopt.py -q

### Task 6.6 暴露“接入已有项目”CLI

- task_id: T66
- status: todo
- priority: P1
- depends: T65
- scope:
  - src/ai_sdlc/cli/main.py
  - src/ai_sdlc/cli/adopt_cmd.py
  - USER_GUIDE.zh-CN.md
  - tests/integration/test_cli_adopt.py
- acceptance:
  - 用户可运行 `ai-sdlc adopt .` 或等价入口。
  - 中文文案使用“接入已有项目”，不要求用户理解 `checkpoint / stage / reconcile`。
  - 输出摘要说明原任务文件不会被改动。
  - 用户可用自然语言纠偏，例如“不是这个，先做支付回调”。
  - 两个对抗 agent 对 adopt CLI 用户体验无必须修订项。
- verify:
  - uv run pytest tests/integration/test_cli_adopt.py -q

## Batch 7：release closure

### Task 7.1 全量验证、PR 和补丁发布

- task_id: T71
- status: todo
- priority: P0
- depends: T34,T41,T53,T66
- scope:
  - pyproject.toml
  - src/ai_sdlc/__init__.py
  - docs/releases/
  - README.md
  - USER_GUIDE.zh-CN.md
  - packaging/offline/README.md
- acceptance:
  - `uv run pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 通过。
  - PR 已创建并请求 Codex review。
  - GitHub required checks 通过，review 无未处理阻塞。
  - 如对抗 agent、PR review 或 CI 发现问题，必须修复、重测、重新评审后才能发布。
  - 两个对抗 agent 对最终实现和发布材料无必须修订项。
  - 发布新的 patch 版本并完成 release notes。
- verify:
  - uv run pytest
  - uv run ruff check src tests
  - uv run ai-sdlc verify constraints
  - gh pr checks
  - gh release view
