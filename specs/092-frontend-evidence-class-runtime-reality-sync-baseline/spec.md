# 功能规格：Frontend Evidence Class Runtime Reality Sync Baseline

**功能编号**：`092-frontend-evidence-class-runtime-reality-sync-baseline`  
**创建日期**：2026-04-09  
**状态**：formal baseline 已冻结；runtime reality sync 已验证  
**输入**：[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`](../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md)、[`../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md`](../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md)、[`../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`](../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)

> 口径：`092` 不是新的 runtime feature baseline，而是一条 framework honesty-sync carrier。它把当前仓库中已经存在的 `frontend_evidence_class` runtime reality 正式落盘：`verify constraints`、`program validate`、manifest sync、`program status`/`status --json` bounded surfacing，以及 `workitem close-check` late resurfacing 都已存在可执行实现。`092` 不新增行为，只把“现有代码已经做了什么”与“docs-only contract 当时只冻结了什么”区分清楚。

## 问题定义

到 `091` 为止，`frontend_evidence_class` 的 runtime 链路在代码里已经形成了完整主干：

- `verify constraints` 读取 `spec.md` footer 并产出 `frontend_evidence_class_authoring_malformed`
- `program validate` 对 `program-manifest.yaml specs[].frontend_evidence_class` 执行 mirror drift 校验
- `program frontend-evidence-class-sync` 执行显式 manifest mirror writeback
- `program status` / `status --json` 输出 bounded frontend evidence class summary
- `workitem close-check` 在 close-stage 对 unresolved blocker 做 bounded late resurfacing

但 `086`、`087`、`088`、`090` 本身都被冻结成 docs-only / prospective-only contract。继续在这个基础上往前做新实现，会留下一个更基础的框架问题：machine truth 会继续把“已经实现”描述成“未来实现”，导致后续 baseline 很难判断自己到底是在补实现，还是在补 reality sync。

因此 `092` 的目标不是再落一个新的 runtime slice，而是先把已经存在的 runtime 面收成一条合法 carrier，明确：

- 哪些 runtime surface 已经是当前 truth
- 哪些 docs-only baseline 仍保持为 historical contract，而不是当前实现授权面
- `090` 的 sequencing 现在应被读作“当前主链已落到 close-check resurfacing”，不是继续假设 validate / sync / status 仍未实现

## 范围

- **覆盖**：
  - 新建 `092` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `92`
  - 记录当前 `frontend_evidence_class` runtime reality 已覆盖的 surfaces
  - 明确 `086`、`087`、`088`、`090` 的 docs-only truth 与当前代码 reality 的关系
  - 用 fresh verification 重新证明当前 runtime 主链仍然可执行
- **不覆盖**：
  - 修改 `src/`、`tests/`、`program-manifest.yaml`
  - 改写 `086`、`087`、`088`、`090` 原始 docs-only spec 的 historical wording
  - 新增新的 runtime behavior、diagnostics family、CLI surface 或 writeback mode
  - retroactively 改义 `068` ~ `071`

## 已锁定决策

- `092` 是 honesty-sync carrier，不是 feature implementation carrier
- `085` 的 verify first cut、`086` 的 validate drift、`087` 的 explicit sync、`088` 的 bounded status、`091` 的 close-stage resurfacing，都按“当前已实现 reality”记录
- `086`、`087`、`088`、`090` 继续保留其 historical docs-only / prospective-only 身份；`092` 只额外声明当前仓库 reality 已经走到哪里
- 后续如继续推进 `frontend_evidence_class`，应在 `092` 之上判断是新增 feature，还是单纯的 truth sync / closeout

## 当前 Runtime Reality

### 1. Verify constraints

当前 runtime 已在 `verify constraints` 读取 future frontend work item `spec.md` footer 的 `frontend_evidence_class`，并对以下 authoring 错误产出 `frontend_evidence_class_authoring_malformed`：

- `missing_footer_key`
- `empty_value`
- `invalid_value`
- `duplicate_key`
- `body_footer_conflict`

对应代码与回归面：

- `src/ai_sdlc/core/verify_constraints.py`
- `tests/unit/test_verify_constraints.py`

### 2. Program validate

当前 runtime 已在 `program validate` 执行 manifest mirror drift 校验，canonical source 认 `spec.md` footer，mirror source 认 `program-manifest.yaml specs[].frontend_evidence_class`，并已覆盖：

- `mirror_missing`
- `mirror_invalid_value`
- `mirror_stale`

对应代码与回归面：

- `src/ai_sdlc/core/program_service.py`
- `tests/integration/test_cli_program.py`

### 3. Explicit sync / writeback

当前 runtime 已存在显式 manifest sync 路径，用于把 canonical footer truth 同步回 `program-manifest.yaml` 的 `specs[].frontend_evidence_class`。该路径不是 opportunistic write，也不在 `program validate` 或 `program status` 中偷写。

对应代码与回归面：

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/integration/test_cli_program.py`

### 4. Bounded status surfacing

当前 runtime 已在 `program status` / `status --json` 输出 bounded frontend evidence class summary，只暴露 compact family/token，不展开 full diagnostics payload。

对应代码与回归面：

- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/integration/test_cli_program.py`
- `tests/integration/test_cli_status.py`

### 5. Close-stage resurfacing

当前 runtime 已在 `workitem close-check` 对 unresolved `frontend_evidence_class` blocker 做 bounded late resurfacing，不承担 first-detection，不做 writeback，不泄露 full diagnostics payload。

对应代码与回归面：

- `src/ai_sdlc/core/close_check.py`
- `tests/integration/test_cli_workitem_close_check.py`

## 用户故事与验收

### US-092-1 — Maintainer 需要知道哪些 runtime 已经存在

作为 **maintainer**，我希望有一条单独 baseline 能明确列出 `frontend_evidence_class` 当前已经实现的 runtime surfaces，这样我不会继续把 validate / sync / status / close-check 误判成“尚未实现的 future cut”。

**验收**：

1. Given 我阅读 `092`，When 我判断下一步工作，Then 我知道 `program validate`、manifest sync、bounded status 与 close-check 已经存在
2. Given 我阅读 `092`，When 我对照 `086` ~ `090`，Then 我知道那些 baseline 仍是 historical contract，不是当前实现授权面

### US-092-2 — Reviewer 需要把 docs-only contract 与 reality 分开

作为 **reviewer**，我希望 `092` 明确区分“当时冻结的 prospective contract”和“当前代码 reality”，这样我能判断后续 baseline 是在补实现、补 closeout，还是只在补 honesty sync。

**验收**：

1. Given 我看到 `086` / `087` / `088` / `090` 的 docs-only wording，When 我同时阅读 `092`，Then 我不会误判当前仓库仍停在 future-only 阶段
2. Given 我需要 review 后续改动，When 我对照 `092`，Then 我能先判断当前 reality 已到哪一层

## 功能需求

| ID | 需求 |
|----|------|
| FR-092-001 | `092` 必须明确记录 `frontend_evidence_class` 的 current runtime reality 已覆盖 verify / validate / sync / status / close-check 五类 surface |
| FR-092-002 | `092` 必须明确 `086`、`087`、`088`、`090` 继续保留 docs-only / prospective-only 的 historical 身份 |
| FR-092-003 | `092` 不得把 honesty sync 伪装成新的 runtime feature implementation |
| FR-092-004 | `092` 不得修改任何 production code、tests 或 `program-manifest.yaml` |
| FR-092-005 | `092` 必须用 fresh verification 证明当前 runtime 主链仍然可执行 |
| FR-092-006 | `092` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `91` 推进到 `92` |

## 成功标准

- **SC-092-001**：reviewer 能从 `092` 一次看清 `frontend_evidence_class` 当前已实现的 runtime chain
- **SC-092-002**：`092` 不新增任何 runtime 行为，只同步 machine truth
- **SC-092-003**：fresh verification 证明 verify / validate / status / close-check 相关回归仍通过
- **SC-092-004**：本轮 diff 仅触及 `specs/092/...` 与 `project-state.yaml`

---
related_doc:
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
