# 功能规格：Execute Authorization Preflight Guard Baseline

**功能编号**：`116-execute-authorization-preflight-guard-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：Remediate `FD-2026-04-07-003` by freezing and implementing a canonical execute-authorization preflight that prevents treating plan freeze as execute authorization before `tasks.md` exists and repo truth has entered execute. 参考：`docs/framework-defect-backlog.zh-CN.md`、`docs/框架自迭代开发与发布约定.md`、`USER_GUIDE.zh-CN.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/core/workitem_truth.py`

> 口径：`116` 不是新的 direct-formal scaffold 能力，也不是只补一层文案提醒。它要把 `FD-2026-04-07-003` 中暴露出的阶段漂移正式落成可复用、可测试的 preflight truth，使仓库能够稳定区分“formal docs 已冻结”和“已经获得 execute 授权”。

## 问题定义

`FD-2026-04-07-003` 记录了同族回归：当 `spec.md` 与 `plan.md` 已冻结时，执行侧仍可能把“implementation plan 已完成”外推成“下一步可以直接进入实现”，绕过 `tasks.md` 与显式 execute 授权。当前规则文本虽然已在文档中写明 `plan freeze != execute authorization`，但仓库内缺少一个稳定、可消费的 preflight truth surface 去回答两个核心问题：

1. 当前 active work item 是否已经具备 `tasks.md` 这一法定 execute 前置；
2. 当前 repo checkpoint 是否真的已经进入 `execute`，而不只是停留在 `review / verify / docs-only`。

如果这两个问题仍需要依赖聊天记忆或人工口头判断，同类误推进就还会复发。

## 范围

- **覆盖**：
  - 纠正 `116` formal docs，使其与 `FD-2026-04-07-003` 的真实目标一致
  - 新增一个可复用的 execute authorization preflight core helper
  - 将 preflight 结果接入 `status --json` 与 `status` 可见 surface
  - 为“缺少 `tasks.md`”与“`tasks.md` 已存在但尚未进入 execute”补自动化回归
- **不覆盖**：
  - 修改宿主 skill 本身的规则仓
  - 试图从聊天记录直接推断“用户是否口头授权”
  - 改写 `SDLCRunner` 的 gate 顺序或新增新的 pipeline stage
  - 扩大到 `program` 子系统的其他 execute confirmation contract

## 已锁定决策

- `tasks.md` 缺失必须被视为 execute blocker，不能再仅作为文档提醒
- “显式 execute 授权”在仓库真值层先以 `checkpoint.current_stage` 是否进入 `execute`（或其后续合法阶段）为准，不再依赖宿主 workflow 提示
- preflight 结果必须是 bounded、可测试、可被 CLI/status surface 消费的结构化输出
- `workitem truth-check` 保留其 revision truth 职责；`116` 在其之上补 execute authorization preflight，而不是重写 truth classification

## 用户故事与验收

### US-116-1 — Framework Maintainer 需要稳定判断当前能否进入实现

作为 **framework maintainer**，我希望仓库能给出一个稳定的 execute authorization preflight，这样在 `spec.md / plan.md` 已冻结时，我不会再把“下一步”误推进成编码。

**验收**：

1. Given active work item 只有 `spec.md` 与 `plan.md`，When 读取 execute authorization surface，Then 结果必须是 blocked，并明确指出缺少 `tasks.md`
2. Given active work item 已有 `tasks.md`，但 checkpoint 仍处于 `verify` 或其他 pre-execute 阶段，When 读取 execute authorization surface，Then 结果仍必须是 blocked，并明确指出尚未进入 execute

### US-116-2 — Operator 需要 status surface 暴露 repo 级 execute 真值

作为 **operator**，我希望 `ai-sdlc status` 与 `ai-sdlc status --json` 能直接展示当前 work item 的 execute authorization 状态，这样我不需要再凭规则文本或对话上下文去猜当前是 docs-only 还是 execute。

**验收**：

1. Given 当前 repo 有 active checkpoint 与 concrete `spec_dir`，When 执行 `ai-sdlc status --json`，Then 输出必须包含 bounded 的 `execute_authorization` summary
2. Given execute preflight 被 blocker 阻断，When 执行 `ai-sdlc status`，Then 文本输出必须显式展示 blocker 状态，而不是默认暗示可以开始实现

## 边界情况

- `spec.md / plan.md / tasks.md` 不完整时，preflight 应返回 blocker 或 unavailable，而不是误报 ready
- 当前 checkpoint 没有关联 concrete `spec_dir` 时，preflight 只能给出 unavailable，不能伪造 execute readiness
- 当 current stage 已在 `close` 等 execute 之后阶段时，preflight 可以视为已具备过 execute authorization，但不能回退成“未授权”

## 功能需求

| ID | 需求 |
|----|------|
| FR-116-001 | 系统必须为 active work item 提供结构化的 execute authorization preflight 结果 |
| FR-116-002 | 当 active work item 缺少 `tasks.md` 时，preflight 必须返回 blocker，并给出稳定 reason code |
| FR-116-003 | 当 `tasks.md` 已存在但 checkpoint 尚未进入 `execute` 或后续合法阶段时，preflight 必须返回 blocker，并给出稳定 reason code |
| FR-116-004 | 系统必须将 execute authorization preflight 接入 `ai-sdlc status --json` 与 `ai-sdlc status` 的 bounded surface |
| FR-116-005 | `116` 必须补自动化回归，覆盖“缺少 `tasks.md`”与“缺少 persisted execute authorization”两类场景 |

## 成功标准

- **SC-116-001**：当 active work item 缺少 `tasks.md` 时，status surface 返回 `blocked`，且 reason code 为稳定 machine token
- **SC-116-002**：当 `tasks.md` 已存在但 checkpoint.current_stage 仍为 `verify` 时，status surface 返回 `blocked`
- **SC-116-003**：当 `tasks.md` 已存在且 checkpoint.current_stage 已进入 `execute` 或 `close` 时，status surface 返回 `ready`
- **SC-116-004**：`ai-sdlc status --json` 返回包含 `execute_authorization` 的 bounded payload
- **SC-116-005**：与 `116` 相关的 unit/integration focused tests 全部通过

---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "src/ai_sdlc/rules/pipeline.md"
  - "src/ai_sdlc/core/workitem_truth.py"
frontend_evidence_class: "framework_capability"
