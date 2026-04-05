---
related_doc:
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/plan.md"
---
# 任务分解：Frontend Contract Sample Source Selfcheck Baseline

**编号**：`065-frontend-contract-sample-source-selfcheck-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-065-001 ~ FR-065-022 / SC-065-001 ~ SC-065-005）

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: sample fixture and scanner stability
Batch 3: CLI scan / verify self-check matrix
Batch 4: program honesty and remediation wording
Batch 5: fresh verification and archive
```

---

## 执行护栏

- `Batch 1` 只允许推进 `spec.md`、`plan.md`、`tasks.md` 与 `task-execution-log.md`。
- sample fixture 只能落在 `tests/fixtures/frontend-contract-sample-src/**`；运行时代码不得写死该路径。
- `065` 不得新增顶层 CLI 命令，不得引入新的 provider registry 或 runtime attachment 私有格式。
- `065` 不得让 `verify constraints`、`program status`、`program plan`、`program integrate --dry-run` 或 remediation helper 隐式触发 scan/materialization。
- `065` 不得把 sample fixture 提升为 runtime fallback、默认 remediation 路径或默认 `source_root`。
- invalid `source_root`、valid-but-empty `source_root`、missing artifact 与 drift 必须保持独立语义，不得互相折叠。
- runtime `recommended_commands` 只能使用 `<frontend-source-root>` 占位符，不得泄漏 fixture 实际路径或继续使用 `scan .`。
- 只有在用户明确要求进入实现，且 `065` formal docs 已通过只读门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 sample source 角色、合法落点与 non-goals

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `065` 是 `014` 下游 child work item
  2. `spec.md` 明确 sample source 是显式 self-check 输入源，而不是 runtime fallback
  3. `spec.md` 明确唯一合法 fixture 路径、truth order 与 out-of-scope
- **验证**：文档对账

### Task 1.2 冻结推荐文件面与验证矩阵

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出 fixture、scanner、verify、program wording 的推荐文件面
  2. `plan.md` 明确 `pass / drift / gap` 的最小验证矩阵
  3. `plan.md` 明确 `program` no-implicit-scan 边界
- **验证**：file-map review

### Task 1.3 冻结批次边界与实现护栏

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 将 docs-only freeze、fixture、scan/verify、自检矩阵、program wording 分成独立批次
  2. `tasks.md` 明确不得新增命令、不得 implicit materialize、不得默认 sample fallback
  3. 后续实现团队可直接按批次进入执行
- **验证**：tasks review

### Task 1.4 收紧 execution log 初始化状态

- **任务编号**：T14
- **优先级**：P1
- **依赖**：T13
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `task-execution-log.md` 不再保留与 `065` 无关的模板占位批次
  2. 当前状态被明确为“已初始化，待 execute 授权”
  3. execution log 可在后续批次 append-only 归档
- **验证**：文档对账

### Task 1.5 运行 docs-only 门禁

- **任务编号**：T15
- **优先级**：P1
- **依赖**：T14
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md`, `specs/065-frontend-contract-sample-source-selfcheck-baseline/plan.md`, `specs/065-frontend-contract-sample-source-selfcheck-baseline/tasks.md`, `specs/065-frontend-contract-sample-source-selfcheck-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `065` formal docs 对 sample source truth、honesty 边界和验证矩阵保持单一真值
  3. 当前 work item 仍停留在 docs/review 层，不提前宣称实现完成
- **验证**：`uv run ai-sdlc verify constraints`

---

## Batch 2：sample fixture and scanner stability

### Task 2.1 落下最小 sample fixture 集合

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T15
- **文件**：`tests/fixtures/frontend-contract-sample-src/match/UserCreate.vue`, `tests/fixtures/frontend-contract-sample-src/match/AccountEdit.tsx`, `tests/fixtures/frontend-contract-sample-src/drift/UserCreate.vue`, `tests/fixtures/frontend-contract-sample-src/empty/Plain.tsx`
- **可并行**：否
- **验收标准**：
  1. fixture 至少覆盖一个标准正例、一个多观察点页面、一个 drift 反例和一个 valid-but-empty source root
  2. fixture 只存在于测试夹具路径
  3. fixture 文件本身不引入运行时默认依赖
- **验证**：文件面 review

### Task 2.2 扩展 scanner 单测覆盖稳定排序与稳定空结果

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`tests/unit/test_frontend_contract_scanner.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `matched_files` 稳定排序与 `observations` 稳定排序
  2. 单测明确覆盖 valid-but-empty source root 的稳定空结果语义
  3. 单测明确覆盖 artifact envelope 在空结果场景下保持一致
- **验证**：`uv run pytest tests/unit/test_frontend_contract_scanner.py -q`

### Task 2.3 如有必要，最小收紧 scanner 实现以满足稳定语义

- **任务编号**：T23
- **优先级**：P1
- **依赖**：T22
- **文件**：`src/ai_sdlc/scanners/frontend_contract_scanner.py`
- **可并行**：否
- **验收标准**：
  1. invalid `source_root`、stable ordering、empty-result envelope 与现有 formal truth 一致
  2. 不引入 sample fallback 或额外命令面
  3. 与 `013` canonical contract 保持兼容
- **验证**：`uv run pytest tests/unit/test_frontend_contract_scanner.py -q`

---

## Batch 3：CLI scan / verify self-check matrix

### Task 3.1 扩展 scan 集成测试覆盖 invalid source root 与 empty artifact

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T23
- **文件**：`tests/integration/test_cli_scan.py`
- **可并行**：否
- **验收标准**：
  1. invalid 或 nonexistent `source_root` 的 CLI 行为被固定为显式失败
  2. valid-but-empty source root 的 CLI 行为被固定为成功生成稳定空 artifact
  3. `scan` export 仍保持 analysis-only，不触发 IDE adapter 或其他副作用写入
- **验证**：`uv run pytest tests/integration/test_cli_scan.py -q`

### Task 3.2 扩展 verify 集成测试覆盖 pass / drift / gap 三分语义

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`tests/integration/test_cli_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 未生成 artifact 时，`verify constraints` 继续暴露 `frontend_contract_observations` gap
  2. 显式扫描 `match` fixture 并生成 artifact 后，`verify constraints` 可进入 pass-ready 路径
  3. 显式扫描 `drift` fixture 并生成 artifact 后，`verify constraints` 返回 drift/mismatch blocker，而不是 gap
- **验证**：`uv run pytest tests/integration/test_cli_verify_constraints.py -q`

### Task 3.3 追加 focused verification，证明 sample 与真实接入共用同一后半段链路

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`tests/integration/test_cli_scan.py`, `tests/integration/test_cli_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确通过不同 `source_root` 证明后半段 `artifact -> verify` 逻辑不变
  2. 不新增第二套 verify 逻辑或 sample-only special case
  3. `pass / drift / gap` 报告语义稳定
- **验证**：`uv run pytest tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py -q`

---

## Batch 4：program honesty and remediation wording

### Task 4.1 收紧 remediation recommended command 为显式占位符

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. `frontend_contract_observations` remediation 使用 `uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir <spec-dir>`
  2. 运行时 surface 不再出现 `scan . --frontend-contract-spec-dir ...`
  3. 不泄漏 sample fixture 实际路径
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 更新 program 单测固定 no-implicit-scan 与占位符语义

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确断言 remediation 命令使用 `<frontend-source-root>` 占位符
  2. 单测明确断言 `program` readiness/gap 仍只由 artifact 是否存在决定
  3. 单测不把 sample fixture 引入 runtime truth model
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 更新 program 集成测试证明不隐式 materialize

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. `program status / plan / integrate --dry-run` 在无 artifact 时仍暴露 `frontend_contract_observations`
  2. `program` 输出不因为 fixture 存在而隐式 scan/materialize
  3. CLI output 中 remediation command 使用显式 `<frontend-source-root>` 占位符
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

---

## Batch 5：fresh verification and archive

### Task 5.1 执行 focused verification

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_contract_scanner.py`, `tests/integration/test_cli_scan.py`, `tests/integration/test_cli_verify_constraints.py`, `src/ai_sdlc/core/program_service.py`, `tests/unit/test_program_service.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. sample fixture、scan、verify、program wording 相关定向测试通过
  2. `uv run ai-sdlc verify constraints` 通过
  3. `git diff --check` 无格式问题
- **验证**：`uv run pytest tests/unit/test_frontend_contract_scanner.py tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`, `uv run ai-sdlc verify constraints`, `git diff --check`

### Task 5.2 追加 execution log 并同步批次状态

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`specs/065-frontend-contract-sample-source-selfcheck-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 追加记录 touched files、命令、结果与 batch 结论
  2. `tasks.md` 与 execution log 的 batch 状态一致
  3. 归档顺序符合“先验证，再归档，再 commit”
- **验证**：execution log review
