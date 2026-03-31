# 任务分解：Direct Formal Work Item Entry

**编号**：`008-direct-formal-workitem-entry` | **日期**：2026-03-31  
**来源**：plan.md + spec.md（FR-008-001 ~ FR-008-012 / SC-008-001 ~ SC-008-005）

---

## 分批策略

```text
Batch 1: formal work item freeze + direct-formal policy baseline
Batch 2: scaffold helper and parser-friendly formal skeleton generation
Batch 3: direct-formal CLI entry and command discovery
Batch 4: docs alignment + focused regression + close-out
```

---

## Batch 1：formal work item freeze + direct-formal policy baseline

### Task 1.1 冻结正式 work item 真值并回挂 backlog

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：docs/framework-defect-backlog.zh-CN.md, specs/008-direct-formal-workitem-entry/spec.md, specs/008-direct-formal-workitem-entry/plan.md, specs/008-direct-formal-workitem-entry/tasks.md
- **可并行**：否
- **验收标准**：
  1. `FD-2026-03-31-003` 明确挂到 `008-direct-formal-workitem-entry`。
  2. `008` 直接以 formal `spec.md / plan.md / tasks.md` 作为 canonical 文档，不再先落一套 `docs/superpowers/*`。
  3. `tasks.md` 使用 parser-friendly 结构。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 1.2 冻结 direct-formal canonical path 语义

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, docs/USER_GUIDE.zh-CN.md
- **可并行**：否
- **验收标准**：
  1. 新 framework capability 的 canonical spec/plan/tasks 默认位于 `specs/<WI>/`。
  2. `docs/superpowers/*` 被明确降为 design input / auxiliary reference，而不是 canonical 最终落点。
  3. 文档不再暗示“必须先写 `docs/superpowers/*` 再 formalize”。
- **验证**：规则/文档对账 + `uv run ai-sdlc verify constraints`

---

## Batch 2：scaffold helper and parser-friendly formal skeleton generation

### Task 2.1 新增 work item scaffold helper

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：src/ai_sdlc/core/workitem_scaffold.py, templates/spec-template.md, templates/plan-template.md, templates/tasks-template.md, tests/unit/test_workitem_scaffold.py
- **可并行**：否
- **验收标准**：
  1. helper 能一次性生成 parser-friendly `spec.md / plan.md / tasks.md` skeleton。
  2. 生成逻辑复用现有模板，不另造第二套模板。
  3. 可选挂接 `related_doc / related_plan` 或等价引用字段，而不是强制复制 external design 正文。
- **验证**：`uv run pytest tests/unit/test_workitem_scaffold.py -q`

### Task 2.2 锁定 formal skeleton 的稳定输出

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/workitem_scaffold.py, tests/unit/test_workitem_scaffold.py
- **可并行**：否
- **验收标准**：
  1. 生成结果文件名、front matter、标题和基本字段顺序稳定，适合 snapshot tests。
  2. 生成的 `tasks.md` 不依赖外部 superpowers 文件才能被 parser 读取。
  3. direct-formal helper 不会创建第二套 canonical docs。
- **验证**：`uv run pytest tests/unit/test_workitem_scaffold.py -k "snapshot or parser or related" -q`

---

## Batch 3：direct-formal CLI entry and command discovery

### Task 3.1 在 workitem CLI 增加 direct-formal init 命令

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/cli/workitem_cmd.py, src/ai_sdlc/cli/main.py, tests/integration/test_cli_workitem_init.py
- **可并行**：否
- **验收标准**：
  1. 存在 `ai-sdlc workitem init` 或等价 direct-formal 命令。
  2. 命令直接生成 `specs/<WI>/spec.md + plan.md + tasks.md`，不要求先有 `docs/superpowers/*`。
  3. 命令输出强调 canonical formal path，而不是外部 design path。
- **验证**：`uv run pytest tests/integration/test_cli_workitem_init.py -q`

### Task 3.2 补齐 command discovery 与 negative coverage

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：src/ai_sdlc/cli/command_names.py, tests/unit/test_command_names.py, tests/integration/test_cli_workitem_init.py
- **可并行**：否
- **验收标准**：
  1. command discovery 能列出 direct-formal init 命令。
  2. negative coverage 包括：重复初始化同一 WI、缺关键参数、试图写第二套 canonical docs。
  3. CLI 不会把 `docs/superpowers/*` 表达成必需前置。
- **验证**：`uv run pytest tests/unit/test_command_names.py tests/integration/test_cli_workitem_init.py -k "init or command" -q`

---

## Batch 4：docs alignment + focused regression + close-out

### Task 4.1 收紧用户文档与操作约定

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T32
- **文件**：docs/USER_GUIDE.zh-CN.md, docs/框架自迭代开发与发布约定.md, src/ai_sdlc/rules/pipeline.md
- **可并行**：否
- **验收标准**：
  1. 用户文档把 direct-formal init 作为新 framework capability 的默认入口。
  2. 文档明确 external design docs 只是 reference，不再要求双轨产物。
  3. rules、guide、CLI discoverability 三者表述一致。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 4.2 跑 focused regression 并冻结新的 single-canonical-doc-set guardrail

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：tests/unit/test_workitem_scaffold.py, tests/integration/test_cli_workitem_init.py, tests/unit/test_command_names.py, docs/USER_GUIDE.zh-CN.md
- **可并行**：否
- **验收标准**：
  1. direct-formal scaffold focused suite 全部通过。
  2. `uv run ai-sdlc verify constraints` 通过。
  3. 文档与 CLI 不再要求“先写 superpowers 再 formalize”。
- **验证**：`uv run pytest tests/unit/test_workitem_scaffold.py tests/integration/test_cli_workitem_init.py tests/unit/test_command_names.py -q`, `uv run ai-sdlc verify constraints`
