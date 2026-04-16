---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
---
# 任务分解：Frontend P2 Multi Theme Token Governance Baseline

**编号**：`148-frontend-p2-multi-theme-token-governance-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-148-001 ~ FR-148-018 / SC-148-001 ~ SC-148-006）

---

## 分批策略

```text
Batch 1: Track B problem statement and single-truth boundary freeze
Batch 2: runtime decomposition, owner boundary, and style editor boundary freeze
Batch 3: adversarial expert-agent review and finding absorption
Batch 4: development summary, docs-only verification, and truth handoff readiness
Batch 5: theme governance model baseline slice
Batch 6: artifact materialization + validator/guardrails slice
Batch 7: ProgramService/CLI/verify handoff + final truth refresh slice
```

---

## 执行护栏

- `148` 当前批次只允许 docs-only formal baseline freeze 与专家评审，不得进入 `src/` / `tests/`。
- `148` 不得把 `073` 的 `style_pack_manifest`、`provider_manifest.style_support_matrix` 或 `solution_snapshot` 回写为第二套 theme truth。
- `148` 不得把 `147` 的 schema anchor 重新包装成 style truth，也不得绕过 `147` 直接使用 DOM selector / provider-specific path。
- `148` 不得放松 `017` 的 minimal token / naked-value rules；custom theme token 只能通过结构化 override envelope 扩展。
- `148` 不得混入 `quality platform`、`cross-provider consistency`、`modern provider expansion`、React exposure 或公开 provider choice surface。
- `148` 不得把“开放式 style editor”包装成 Track B；任何 editor surface 都必须受控、可审计、可回退。
- `Batch 5` 只允许写入 `src/ai_sdlc/models/frontend_theme_token_governance.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_theme_token_governance_models.py`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- `Batch 6` 只允许写入 `src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`src/ai_sdlc/core/frontend_theme_token_governance.py`、`tests/unit/test_frontend_theme_token_governance_artifacts.py`、`tests/unit/test_frontend_theme_token_governance.py`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- `Batch 7` 只允许写入 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/sub_apps.py`、`src/ai_sdlc/cli/program_cmd.py`、`USER_GUIDE.zh-CN.md`、`tests/unit/test_program_service.py`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_rules.py`、`tests/integration/test_cli_program.py`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/development-summary.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。

## Batch 1：Track B problem statement and single-truth boundary freeze

### Task 1.1 冻结 Track B scope 与问题定义

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `148` 承接的是 `145 Track B`
  2. `spec.md` 明确 multi-theme/token governance、自定义 theme token 与 style editor boundary 的问题定义
  3. `spec.md` 不再存在模板占位或 direct-formal 脚手架残留
- **验证**：related docs 对账 review

### Task 1.2 冻结 `017/073/147` 单一真值边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `017` 是 token floor、`073` 是 style solution truth、`147` 是 schema anchor
  2. `spec.md` 明确 `148` 不另造第二套 style pack inventory 或 schema truth
  3. reviewer 可以直接从 formal docs 读出四者边界
- **验证**：boundary wording review

## Batch 2：runtime decomposition, owner boundary, and style editor boundary freeze

### Task 2.1 冻结 runtime slice 顺序与计划结构

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 models、artifacts、validator/guardrails、ProgramService/CLI/verify handoff 的顺序
  2. `plan.md` 明确当前批次只停留在 formal baseline 与 expert review
  3. `plan.md` 明确后续 Track C/D 如何依赖 `148`
- **验证**：plan review

### Task 2.2 冻结 owner boundaries 与 style editor boundary

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 三件套明确 `073/147/148/Track C/Track D` 的 owner boundary
  2. style editor boundary 被定义为受控操作面，而不是开放式编辑器
  3. tasks 与 plan 中不再存在 scope overlap 或命名漂移
- **验证**：formal docs consistency review

## Batch 3：adversarial expert-agent review and finding absorption

### Task 3.1 触发 UX 专家对抗评审

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/tasks.md`
- **可并行**：是（与 T32）
- **验收标准**：
  1. UX 专家以对抗式角度评估 theme/token governance、custom override 与 style editor boundary
  2. 评审结果明确列出高风险 UX 缺口、歧义或后续实现风险，并覆盖 theme 选择、effective theme 阅读、diff/override、回退路径与降级提示可理解性
  3. 评审不接受“以后再看”的模糊表述
- **验证**：expert review findings

### Task 3.2 触发 AI-Native framework 专家对抗评审

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/tasks.md`
- **可并行**：是（与 T31）
- **验收标准**：
  1. AI-Native framework 专家以对抗式角度评估 Track B 是否真正接入 AI-SDLC 主链
  2. 评审结果明确列出 truth duplication、pipeline injection gap、verify gap、machine-verifiable handoff gap 或 downstream handoff risk
  3. 评审不接受“靠对话记忆补齐”的隐性依赖
- **验证**：expert review findings

### Task 3.3 吸收专家 findings 并清零模板缺口

- **任务编号**：T33
- **优先级**：P0
- **依赖**：T31、T32
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/tasks.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. 所有专家提出的有效 gap 都被落回 formal docs 或明确记录为后续 runtime 决议项
  2. 评审后文档不再保留模板占位、冲突边界或未解释的 handoff 空洞
  3. `task-execution-log.md` 记录专家结论与吸收结果
- **验证**：finding-to-doc mapping review

## Batch 4：development summary, docs-only verification, and planning-layer truth handoff readiness

### Task 4.1 初始化 execution log 与 development summary

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T33
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 记录当前批次是 Track B docs-only baseline freeze + expert review
  2. development summary 诚实说明 `148` 当前尚未进入 runtime implementation
  3. 两份文档可被 close-check / global truth 消费
- **验证**：execution log / summary review

### Task 4.2 运行 docs-only 门禁并刷新 planning-layer truth

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/plan.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/tasks.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/development-summary.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `python -m ai_sdlc adapter status` 与 `python -m ai_sdlc run --dry-run` 通过
  2. `uv run ai-sdlc verify constraints` 与 `python -m ai_sdlc workitem close-check --wi specs/148-frontend-p2-multi-theme-token-governance-baseline` 通过
  3. `python -m ai_sdlc program truth sync --execute --yes` 后，`148` 进入 current truth mirror，但口径明确停留在 planning-layer baseline
  4. `git diff --check` 通过
  5. 文档结论保持为 `baseline frozen, runtime pending`，不提前宣称 runtime close-ready
- **验证**：`python -m ai_sdlc adapter status`、`python -m ai_sdlc run --dry-run`、`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/148-frontend-p2-multi-theme-token-governance-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`

## Batch 5：theme governance model baseline slice

### Task 5.1 先写 failing tests 固定 Track B models 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T42
- **文件**：`tests/unit/test_frontend_theme_token_governance_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 theme governance set、token mapping、custom override envelope、style editor boundary contract 的最小结构
  2. 单测明确覆盖 duplicate mapping、unknown scope、illegal namespace、requested/effective mismatch 的失败路径
  3. 首次运行定向测试时必须出现预期失败，证明 Track B models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_models.py -q`

### Task 5.2 实现 theme governance models 与 baseline builders

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/models/frontend_theme_token_governance.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型显式承载 Track B 的 theme governance set、token mapping、custom override envelope 与 style editor boundary contract
  2. baseline builder 明确继承 `017/073/147` 的输入，不复制 style pack inventory 或 schema truth
  3. 实现只停留在结构化模型层，不引入 quality/cross-provider/provider expansion runtime
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_models.py -q`

### Task 5.3 Fresh verify 并归档 model batch

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_theme_token_governance_models.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/models/frontend_theme_token_governance.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_theme_token_governance_models.py` 与 `git diff --check` 通过
  3. execution log 追加当前 model batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_models.py -q`、`uv run ruff check src/ai_sdlc/models/frontend_theme_token_governance.py src/ai_sdlc/models/__init__.py tests/unit/test_frontend_theme_token_governance_models.py`、`git diff --check`

## Batch 6：artifact materialization + validator/guardrails slice

### Task 6.1 先写 failing tests 固定 artifact root 与 validator contract

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T53
- **文件**：`tests/unit/test_frontend_theme_token_governance_artifacts.py`, `tests/unit/test_frontend_theme_token_governance.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 canonical artifact root、theme manifest/token mapping/override policy/style editor boundary 文件集合
  2. 单测明确覆盖 unknown schema anchor、unsupported provider/style pair、illegal override namespace、token floor bypass 的阻断路径
  3. 首次运行定向测试时必须出现预期失败，证明 artifact/validator 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py -q`

### Task 6.2 实现 artifact materialization 与 validator/guardrails

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T61
- **文件**：`src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py`, `src/ai_sdlc/generators/__init__.py`, `src/ai_sdlc/core/frontend_theme_token_governance.py`
- **可并行**：否
- **验收标准**：
  1. 生成器输出稳定的 `governance/frontend/theme-token-governance/` artifact root 与固定文件布局
  2. validator 能基于 `017/073/147` 校验 token mapping、override legality、provider style support 与 schema anchor 引用
  3. 诊断输出保持 machine-verifiable，可直接供后续 ProgramService/CLI/verify 消费
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py -q`

### Task 6.3 Fresh verify 并归档 artifact/validator batch

- **任务编号**：T63
- **优先级**：P0
- **依赖**：T62
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py -q` 通过
  2. `uv run ruff check src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py src/ai_sdlc/generators/__init__.py src/ai_sdlc/core/frontend_theme_token_governance.py tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py` 与 `git diff --check` 通过
  3. execution log 追加当前 artifact/validator batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py -q`、`uv run ruff check src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py src/ai_sdlc/generators/__init__.py src/ai_sdlc/core/frontend_theme_token_governance.py tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py`、`git diff --check`

## Batch 7：ProgramService/CLI/verify handoff + final truth refresh slice

### Task 7.1 先写 failing tests 固定 ProgramService handoff、CLI 与 verify gate

- **任务编号**：T71
- **优先级**：P0
- **依赖**：T63
- **文件**：`tests/unit/test_program_service.py`, `tests/unit/test_verify_constraints.py`, `tests/integration/test_cli_rules.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 ProgramService 读取最新 solution snapshot、page-ui-schema handoff 并生成 theme governance handoff 的 happy path 与 blocker path
  2. 单测明确覆盖 `verify constraints` 对 style support duplication、unknown anchor、token floor bypass 的阻断
  3. 集成测试明确覆盖 `rules materialize-frontend-theme-token-governance` 与 `program theme-token-governance-handoff`
  4. 首次运行定向测试时必须出现预期失败，证明 handoff/CLI/verify surface 尚未实现
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py -q -k 'theme_token_governance or materialize_frontend_theme_token_governance or theme_token_governance_handoff'`

### Task 7.2 实现 ProgramService handoff、CLI surfaced diagnostics 与 verify integration

- **任务编号**：T72
- **优先级**：P0
- **依赖**：T71
- **文件**：`src/ai_sdlc/core/program_service.py`, `src/ai_sdlc/core/verify_constraints.py`, `src/ai_sdlc/cli/sub_apps.py`, `src/ai_sdlc/cli/program_cmd.py`, `USER_GUIDE.zh-CN.md`, `specs/148-frontend-p2-multi-theme-token-governance-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. ProgramService 暴露 machine-verifiable theme governance handoff surface，并消费 `017/073/147` 的上游 truth
  2. CLI 能 materialize Track B artifacts 并查看 handoff state / blocker / requested/effective theme/override diagnostics
  3. `verify constraints` 能识别 theme truth duplication、unknown anchor、illegal override namespace 与 token floor bypass
  4. development summary 诚实表达 `148` 的 runtime baseline 进展，并明确 Track C/D/E 仍待后续工单承接
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py -q -k 'theme_token_governance or materialize_frontend_theme_token_governance or theme_token_governance_handoff'`

### Task 7.3 Final verify、truth refresh 与 close-out 归档

- **任务编号**：T73
- **优先级**：P0
- **依赖**：T72
- **文件**：`specs/148-frontend-p2-multi-theme-token-governance-baseline/task-execution-log.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. 受影响的 unit/integration/ruff/verify constraints 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/148-frontend-p2-multi-theme-token-governance-baseline` 与 `python -m ai_sdlc program truth sync --execute --yes` 只在 runtime slices 完成后执行，并按新 runtime 口径刷新 `148` 的任务/收口状态
  3. execution log 追加本轮 runtime batches 的真实验证画像与 truth refresh 结果，不伪造 git clean/提交状态
- **验证**：`uv run pytest tests/unit/test_frontend_theme_token_governance_models.py tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py tests/unit/test_program_service.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py -q -k 'theme_token_governance or materialize_frontend_theme_token_governance or theme_token_governance_handoff'`、`uv run ruff check src/ai_sdlc/models/frontend_theme_token_governance.py src/ai_sdlc/generators/frontend_theme_token_governance_artifacts.py src/ai_sdlc/core/frontend_theme_token_governance.py src/ai_sdlc/core/program_service.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/sub_apps.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_frontend_theme_token_governance_models.py tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_theme_token_governance.py tests/unit/test_program_service.py tests/unit/test_verify_constraints.py tests/integration/test_cli_rules.py tests/integration/test_cli_program.py`、`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`
