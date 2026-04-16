---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
---
# 任务分解：Frontend P2 Page UI Schema Baseline

**编号**：`147-frontend-p2-page-ui-schema-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-147-001 ~ FR-147-012 / SC-147-001 ~ SC-147-005）

---

## 分批策略

```text
Batch 1: page-ui schema problem statement and structure boundary freeze
Batch 2: implementation order, upstream/downstream dependency, and non-goal freeze
Batch 3: development summary, docs-only validation, and global truth handoff readiness
Batch 4: page-ui schema model baseline slice
Batch 5: artifact materialization + validator/versioning slice
Batch 6: provider/kernel handoff + CLI surfaced diagnostics slice
```

---

## 执行护栏

- `147` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `147` 不得把 `068` page recipe truth 或 `073` provider/style first-phase truth 回写成 page schema 的唯一来源。
- `147` 不得混入 multi-theme/token governance、quality platform、cross-provider consistency、modern provider expansion。
- `147` 必须保持 provider-neutral，不得先站队单一 provider。
- `147` 必须明确它是 `145 Track A` 的 child，而不是新的顶层母级 planning item。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_page_ui_schema.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_page_ui_schema_models.py`、`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/generators/frontend_page_ui_schema_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`src/ai_sdlc/core/frontend_page_ui_schema.py`、`tests/unit/test_frontend_page_ui_schema_artifacts.py`、`tests/unit/test_frontend_page_ui_schema.py`、`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- `Batch 6` 只允许写入 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/sub_apps.py`、`src/ai_sdlc/cli/program_cmd.py`、`USER_GUIDE.zh-CN.md`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_rules.py`、`tests/integration/test_cli_program.py`、`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`、`specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。

## Batch 1：page-ui schema problem statement and structure boundary freeze

### Task 1.1 冻结 page schema / ui schema scope

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. canonical formal docs 已直接位于 `specs/147-frontend-p2-page-ui-schema-baseline/`
  2. `spec.md` 明确 page schema、ui schema、render slot、section anchor、schema versioning 的边界
  3. `spec.md` 明确 `147` 是 `145 Track A` 的正式承接
- **验证**：related docs 对账 review

### Task 1.2 冻结与 `068/073` 的关系

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `147` 不是重做 `068/073`
  2. `spec.md` 明确 schema truth 与 recipe/provider truth 的关系
  3. reviewer 可以直接从 formal docs 读出三者边界
- **验证**：boundary wording review

## Batch 2：implementation order, upstream/downstream dependency, and non-goal freeze

### Task 2.1 冻结 implementation slice 顺序

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 schema model/serialization、validator/versioning、provider/kernel consumption 的顺序
  2. `plan.md` 明确当前只停留在 formal baseline
  3. `plan.md` 明确后续 Track B/C/D 如何依赖 `147`
- **验证**：plan review

### Task 2.2 冻结 non-goals 与 downstream dependency

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T21
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`, `specs/147-frontend-p2-page-ui-schema-baseline/plan.md`, `specs/147-frontend-p2-page-ui-schema-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 theme/quality/provider expansion 不属于当前 child
  2. downstream tracks 可以把 `147` 作为 schema anchor 引用
  3. tasks 与 plan 不再存在模板占位或 scope 混乱
- **验证**：formal docs consistency review

## Batch 3：development summary, docs-only validation, and global truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`, `specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 记录当前是 docs-only child baseline freeze
  2. development summary 诚实说明 `147` 当前尚未进入 runtime implementation
  3. 两份文档可被 close-check / global truth 消费
- **验证**：execution log / summary review

### Task 3.2 运行 docs-only 门禁并确认 truth handoff readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`, `specs/147-frontend-p2-page-ui-schema-baseline/plan.md`, `specs/147-frontend-p2-page-ui-schema-baseline/tasks.md`, `specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`, `specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/147-frontend-p2-page-ui-schema-baseline` 通过
  3. `program truth sync` 后 `147` 能进入 global truth mirror
  4. `git diff --check` 通过
- **验证**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/147-frontend-p2-page-ui-schema-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`

## Batch 4：page-ui schema model baseline slice

### Task 4.1 先写 failing tests 固定 page/ui schema baseline 结构

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：`tests/unit/test_frontend_page_ui_schema_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 page schema、ui schema、section anchor、field block、render slot、schema versioning 的最小结构
  2. 单测明确覆盖 duplicate anchor / duplicate slot / unknown primary anchor 的失败路径
  3. 首次运行定向测试时必须出现预期失败，证明 schema models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_models.py -q`

### Task 4.2 实现 page/ui schema models 与 baseline builders

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_page_ui_schema.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型显式承载 page schema、ui schema、schema versioning、section anchor、field block、render slot
  2. baseline builder 以 `068` page recipes 与 `073` solution truth 为上游输入，保持 provider-neutral
  3. 实现只停留在结构化模型层，不引入 provider/theme/quality runtime
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_models.py -q`

### Task 4.3 Fresh verify 并归档 model batch

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_page_ui_schema_models.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/models/frontend_page_ui_schema.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_page_ui_schema_models.py` 与 `git diff --check` 通过
  3. execution log 追加当前 model batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_models.py -q`、`uv run ruff check src/ai_sdlc/models/frontend_page_ui_schema.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_page_ui_schema_models.py`、`git diff --check`

## Batch 5：artifact materialization + validator/versioning slice

### Task 5.1 先写 failing tests 固定 artifact root 与 validator contract

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_page_ui_schema_artifacts.py`, `tests/unit/test_frontend_page_ui_schema.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 canonical artifact root、manifest/versioning/page/ui schema 文件集合
  2. 单测明确覆盖 unknown recipe、unknown component、unknown state、unknown anchor/slot 的阻断路径
  3. 首次运行定向测试时必须出现预期失败，证明 artifact/validator 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py -q`

### Task 5.2 实现 artifact materialization 与 validator/versioning

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/generators/frontend_page_ui_schema_artifacts.py`, `src/ai_sdlc/generators/__init__.py`, `src/ai_sdlc/core/frontend_page_ui_schema.py`
- **可并行**：否
- **验收标准**：
  1. 生成器输出稳定的 `page-ui-schema` artifact root 与文件布局
  2. validator 能基于 UI Kernel 与 schema versioning contract 校验 recipe/component/state/anchor/slot 引用
  3. 诊断输出保持 machine-verifiable，可直接供后续 ProgramService/CLI handoff 消费
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py -q`

### Task 5.3 Fresh verify 并归档 artifact/validator batch

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/generators/frontend_page_ui_schema_artifacts.py src/ai_sdlc/generators/__init__.py src/ai_sdlc/core/frontend_page_ui_schema.py tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py` 与 `git diff --check` 通过
  3. execution log 追加当前 artifact/validator batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py -q`、`uv run ruff check src/ai_sdlc/generators/frontend_page_ui_schema_artifacts.py src/ai_sdlc/generators/__init__.py src/ai_sdlc/core/frontend_page_ui_schema.py tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_page_ui_schema.py`、`git diff --check`

## Batch 6：provider/kernel handoff + CLI surfaced diagnostics slice

### Task 6.1 先写 failing tests 固定 ProgramService handoff 与 CLI surface

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T53
- **文件**：`tests/unit/test_program_service.py`, `tests/integration/test_cli_rules.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 ProgramService 读取最新 solution snapshot 并生成 provider/kernel handoff 的 happy path 与 blocker path
  2. 集成测试明确覆盖 `rules materialize-frontend-page-ui-schema` 与 `program page-ui-schema-handoff`
  3. 首次运行定向测试时必须出现预期失败，证明 handoff/CLI surface 尚未实现
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py -q -k 'page_ui_schema or materialize_frontend_page_ui_schema or page_ui_schema_handoff'`

### Task 6.2 实现 ProgramService handoff、CLI surfaced diagnostics 与用户指南更新

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T61
- **文件**：`src/ai_sdlc/core/program_service.py`, `src/ai_sdlc/cli/sub_apps.py`, `src/ai_sdlc/cli/program_cmd.py`, `USER_GUIDE.zh-CN.md`, `specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. ProgramService 暴露 machine-verifiable page/ui schema handoff surface，并消费 solution snapshot / UI Kernel / schema validator
  2. CLI 能 materialize page-ui schema artifacts 并查看 handoff state / blocker / provider/style linkage
  3. development summary 诚实表达 `147` 已完成 runtime baseline，但 Track B/C/D/E 仍待后续工单承接
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py -q -k 'page_ui_schema or materialize_frontend_page_ui_schema or page_ui_schema_handoff'`

### Task 6.3 Final verify、truth refresh 与 close-out归档

- **任务编号**：T63
- **优先级**：P0
- **依赖**：T62
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 受影响的 unit/integration/ruff/verify constraints 通过
  2. `python -m ai_sdlc program truth sync --execute --yes` 后，`147` 的任务/收口状态按新 runtime 口径刷新
  3. execution log 追加本轮 runtime batches 的真实验证画像与 truth refresh 结果，不伪造 git clean/提交状态
- **验证**：`uv run pytest <affected suites>`、`uv run ruff check <affected files>`、`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`
