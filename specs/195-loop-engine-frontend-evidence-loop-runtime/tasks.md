---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
  - "specs/192-loop-engine-requirement-loop-runtime/spec.md"
  - "specs/193-loop-engine-design-contract-loop-runtime/spec.md"
  - "specs/194-loop-engine-implementation-loop-runtime/spec.md"
---
# 任务分解：Loop Engine Frontend Evidence Loop Runtime

**编号**：`195-loop-engine-frontend-evidence-loop-runtime` | **日期**：2026-07-01
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline freeze and linkage
Batch 2: frontend-evidence models, store, and ingestion runtime
Batch 3: close gate, CLI, and status/list
Batch 4: docs, constraints, final regression, PR review
```

---

## Batch 1：formal baseline freeze and linkage

### Task 1.1 冻结 frontend-evidence formal docs

- **任务编号**：T11
- **状态**：done
- **优先级**：P0
- **依赖**：WI-194 已合并
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md, program-manifest.yaml, .ai-sdlc/project/config/project-state.yaml
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 WI-195 只交付 `frontend-evidence` loop
  2. `spec.md` 明确不调用模型、不要求 CI 模型访问、不硬编码 GitHub 或单一前端栈
  3. `plan.md` 覆盖 runtime、CLI、status/list、docs/constraints 四阶段
  4. `tasks.md` 有可执行任务、文件范围和验证命令
  5. spec footer 声明 frontend evidence class 并与 manifest truth 同步
- **验证**：`git diff --check`、`uv run ai-sdlc program frontend-evidence-class-sync --spec-id 195-loop-engine-frontend-evidence-loop-runtime --execute --yes`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc verify constraints`

---

## Batch 2：frontend-evidence models, store, and ingestion runtime

### Task 2.1 新增 frontend-evidence artifact models and store

- **任务编号**：T21
- **状态**：done
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/core/frontend_evidence_models.py, src/ai_sdlc/core/frontend_evidence_store.py, tests/unit/test_frontend_evidence_loop.py
- **可并行**：否
- **验收标准**：
  1. 定义 input、snapshot、report、close、current pointer、command result 模型
  2. artifact 路径固定在 `.ai-sdlc/loops/frontend-evidence/<loop-id>/`
  3. 显式 loop id、artifact path、current pointer 均做项目内安全校验
  4. 长期 artifact 包含 schema_version、artifact_kind、created_by、created_at、ai_sdlc_version
- **验证**：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`

### Task 2.2 实现 start runtime and browser gate artifact ingestion

- **任务编号**：T22
- **状态**：done
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/frontend_evidence_loop.py, tests/unit/test_frontend_evidence_loop.py
- **可并行**：否
- **验收标准**：
  1. `start_frontend_evidence_loop` 要求同一 work item 的 implementation loop 已关闭且要求前端证据
  2. 默认读取 `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`，支持显式 `--artifact-path`
  3. 校验 YAML mapping、execution context、runtime session、artifact records、bundle input、gate namespace 和 work item scope
  4. `passed` 生成 passed report，`passed_with_advisories` 生成 needs_user report，blocked/incomplete/malformed 生成 needs_fix 或 blocked report
  5. `--dry-run` 不写 artifact
- **验证**：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`

---

## Batch 3：close gate, CLI, and status/list

### Task 3.1 实现 close gate

- **任务编号**：T31
- **状态**：done
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/core/frontend_evidence_loop.py, tests/unit/test_frontend_evidence_loop.py
- **可并行**：否
- **验收标准**：
  1. 无 blocker 且无 warning 的 passed report 可 `close --yes`
  2. warning 存在时必须 `close --yes --allow-warnings`
  3. blocker、missing report、malformed artifact、未传 `--yes` 均 fail-closed
  4. close 后写入 `frontend-evidence-close.json`，loop-run 状态为 `closed`，next action 指向 local PR review
- **验证**：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`

### Task 3.2 接入 CLI

- **任务编号**：T32
- **状态**：done
- **优先级**：P0
- **依赖**：T22, T31
- **文件**：src/ai_sdlc/cli/loop_cmd.py, tests/integration/test_cli_loop.py
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc loop frontend-evidence start/status/close` 可用
  2. human 输出包含 Result、Next、Gate status、Blockers、Warnings、Artifacts
  3. `--json` 输出可解析且不混入 Rich 文本
  4. 失败命令返回非零退出码
- **验证**：`uv run pytest tests/integration/test_cli_loop.py -q`

### Task 3.3 接入 loop status/list

- **任务编号**：T33
- **状态**：done
- **优先级**：P1
- **依赖**：T22, T31
- **文件**：src/ai_sdlc/core/loop_status.py, tests/unit/test_loop_status.py
- **可并行**：否
- **验收标准**：
  1. `get_loop_status(..., loop_type="frontend-evidence")` 读取 current pointer
  2. `list_loops(..., loop_type="frontend-evidence")` 列出历史 runs 并标记 current
  3. malformed current target 返回 blocker，不隐藏其他合法历史 run
  4. local-pr-review、requirement、design-contract、implementation 既有行为不回归
- **验证**：`uv run pytest tests/unit/test_loop_status.py -q`

---

## Batch 4：docs, constraints, final regression, PR review

### Task 4.1 对齐用户文档和约束面

- **任务编号**：T41
- **状态**：done
- **优先级**：P1
- **依赖**：T32, T33
- **文件**：README.md, src/ai_sdlc/core/verify_constraints.py, tests/unit/test_verify_constraints.py
- **可并行**：否
- **验收标准**：
  1. README 说明 frontend-evidence loop 位于 implementation 与 local PR review 之间
  2. README 说明 browser gate 仍由本地 `program browser-gate-probe --execute` 执行
  3. verify constraints 覆盖 runtime、CLI、用户文档 surface
  4. 文档明确本 loop 不调用模型、不依赖 GitHub、不写前端代码
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`、`uv run ai-sdlc verify constraints`

### Task 4.2 完成最终回归与 PR 收口

- **任务编号**：T42
- **状态**：done
- **优先级**：P0
- **依赖**：T41
- **文件**：specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md, program-manifest.yaml, .ai-sdlc/state/codex-handoff.md
- **可并行**：否
- **验收标准**：
  1. focused tests、ruff、mypy、diff check、verify constraints、program truth sync 通过
  2. `uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime` 通过
  3. 分支已提交、推送、开 PR、请求 Codex review
  4. Codex review 无 actionable issues 且 required checks 通过后合并
- **验证**：
  - `uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - `uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
  - `uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - `git diff --check`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

## 全局约束

1. 本 PR 只交付 `frontend-evidence` loop，不重新实现 frontend browser gate。
2. 本 loop 不得调用模型、provider、Codex 云端 review 或 CI 模型请求。
3. 本 loop 不得修改业务代码或前端代码。
4. 不得把 GitHub、远端 PR diff、远端 preview URL 作为必需前提。
5. 不得把 Vue3 PrimeVue、企业内网、本地文件或 GitHub Pages 任一场景硬编码为唯一合法路径。
6. 每批完成后必须更新 `task-execution-log.md` 和 handoff。
