# 功能规格：Frontend Program Final Proof Archive Project Cleanup Mutation Baseline

**功能编号**：`051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)

> 口径：本 work item 不是继续把 `050` 的 deferred baseline 偷渡成真实 cleanup mutation 实现，而是把“当前还没有被正式批准的 cleanup target formal truth”冻结成单一结论。`051` 在当前阶段只记录边界、证据和后续接力条件，不新增 request/result contract，不新增第二套 artifact truth，也不授权任何真实 workspace mutation。

## 问题定义

`050` 已经把 frontend final proof archive project cleanup 的 request/result/artifact baseline 固定下来，并明确：

- project cleanup 只能消费 `049` thread archive execute truth
- project cleanup 只能在显式确认后的 execute 路径运行
- 当前 baseline 只会写 canonical cleanup artifact，不会执行真实 workspace cleanup mutation
- 若没有安全且已定义的 cleanup action，结果必须诚实回报为 `deferred`

在这个前提下，`051` 需要先回答一个更基本的问题：当前仓库里是否已经存在可被正式承接的 cleanup target formal truth。对 `050` spec、`ProgramService`、CLI tests、仓库 `.ai-sdlc/` 面和现有报告路径做完证据审阅后，结论是：

- 上游 truth 里没有显式、稳定、可审计的 `cleanup_targets`
- `written_paths` 不是 cleanup target formal truth
- reports / deliverables / `.ai-sdlc` 目录中也没有被正式批准为 cleanup mutation 输入的目标集合
- 因此当前没有任何真实 cleanup mutation 可以被 `051` 合法承接

因此，本 work item 要解决的是：

- 把 “当前批准的 cleanup mutation allowlist 为空集合” 冻结成单一 formal truth
- 保持 `050` 的 deferred honesty boundary，不伪造 real mutation implementation
- 为未来 child work item 规定清晰接力顺序：先把 cleanup target 入真值链，再写 failing tests，再做实现

## 范围

- **覆盖**：
  - 将 `051` 正式定义为 `050` 下游的 boundary-freeze child work item
  - 锁定 `051` 只消费 `050` final proof archive project cleanup artifact truth
  - 锁定当前批准的 cleanup mutation allowlist 为空集合
  - 锁定 `050` 的 deferred honesty boundary 继续有效
  - 锁定未来 child work item 的接力前提与真值顺序
- **不覆盖**：
  - 改写 `050` 已冻结的 cleanup request/result/artifact contract
  - 引入新的 project cleanup request 通道、第二套 cleanup artifact 或旁路 truth
  - 根据 `.ai-sdlc/`、reports、`written_paths`、目录命名或操作者意图去猜测 cleanup target
  - 执行任何真实 workspace mutation、递归删除、worktree 清理、git mutation 或 janitor 行为
  - 在当前 work item 中修改 `src/`、`tests/` 或 CLI surface

## 已锁定决策

- `051` 只能消费 `050` final proof archive project cleanup artifact truth，不得绕开 `050`
- `051` 不新增真实 cleanup mutation request/result contract，不新增第二套 cleanup truth
- 当前批准的 cleanup mutation allowlist 是空集合；没有显式 formal truth 的动作一律不执行
- `050` 的 deferred honesty boundary 在当前阶段继续成立，不得伪造 `executed` cleanup
- `051` 不得把 `.ai-sdlc/` 目录、reports、deliverables、`written_paths` 或工作树脏文件推断成 cleanup target
- `051` 当前阶段只允许修改 `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/` 内文档，并以 append-only 方式记录证据与结论
- 若未来需要 real mutation，必须先新增 child work item，把 explicit cleanup target formal truth 纳入上游链路，再进入测试和实现

## 用户故事与验收

### US-051-1 — Framework Maintainer 需要知道当前没有被批准的 cleanup mutation

作为 **框架维护者**，我希望 `051` 明确记录“当前没有被正式批准的 cleanup target”，以便后续实现不会基于猜测继续写 mutation 代码。

**验收**：

1. Given 我查看 `051` formal docs，When 我确认当前 allowlist，Then 我能明确读到它是空集合
2. Given 我查看 `051` 的 non-goals，When 我寻找当前实现入口，Then 我能明确读到当前阶段不允许修改 `src/` 或 `tests/`

### US-051-2 — Reviewer 需要知道 `050` 的 deferred 边界仍然有效

作为 **reviewer**，我希望 `051` 明确指出 `050` 的 deferred honesty boundary 仍然成立，以便 review 时不会把“未定义 mutation”误判成“待补代码”。

**验收**：

1. Given 我查看 `051` formal docs，When 我查找当前结论，Then 我能确认没有任何真实 cleanup mutation 被正式放行
2. Given 我查看 `051` 的 success criteria，When 我确认交付结果，Then 我能看到当前 work item 的完成条件是边界冻结而不是代码实现

### US-051-3 — 后续子项执行者需要明确接力顺序

作为 **后续子项执行者**，我希望 `051` 明确 future child work item 的前置条件，以便后续工作先把 cleanup target 入真值链，再进入 failing tests 和实现。

**验收**：

1. Given 我查看 `051` formal docs，When 我寻找后续动作，Then 我能看到必须先 formalize cleanup target truth
2. Given 我准备继续实现，When 我确认顺序，Then 我能直接得到 “truth -> failing tests -> service -> CLI” 的接力路径

## 当前批准的 mutation allowlist

```text
[]
```

解释：

- 当前没有任何 cleanup target 被正式写入 `050` 下游 truth
- 当前没有任何目录、文件或 report path 被批准为 `051` 可执行的 mutation target
- 任何真实 cleanup mutation 在当前阶段都必须保持未执行，并由 `050` 的 deferred 语义诚实回报

## 功能需求

| ID | 需求 |
|----|------|
| FR-051-001 | `051` 必须作为 `050` 下游的 boundary-freeze child work item 被正式定义 |
| FR-051-002 | `051` 必须明确自己只消费 `050` cleanup artifact truth |
| FR-051-003 | `051` 必须把当前批准的 cleanup mutation allowlist 冻结为空集合 |
| FR-051-004 | `051` 必须明确 `050` 的 deferred honesty boundary 在当前阶段继续有效 |
| FR-051-005 | `051` 必须明确 `.ai-sdlc/`、reports、`written_paths`、deliverables 与工作树脏状态都不是 cleanup target formal truth |
| FR-051-006 | `051` 必须明确当前 work item 不进入 `ProgramService`、CLI 或 tests 的实现修改 |
| FR-051-007 | `051` 必须明确未来 real mutation child work item 的前置条件是先 formalize explicit cleanup target truth |
| FR-051-008 | `051` 必须要求未来实现先以 failing tests 固定 cleanup target / result 语义，再进入 service/CLI 编码 |
| FR-051-009 | `051` 必须将证据审阅、边界收紧与结论记录到 append-only `task-execution-log.md` |
| FR-051-010 | `051` 必须允许通过只读校验完成交付，不伪造额外 side effect |

## 关键实体

- **Program Frontend Final Proof Archive Project Cleanup Artifact**：`051` 的唯一上游 cleanup truth
- **Cleanup Target Formal Truth**：未来若要允许真实 mutation，必须先被显式纳入上游链路的 target 集合；当前不存在
- **Deferred Honesty Boundary**：`050` 在“没有安全且已定义的 cleanup action”时必须返回 `deferred` 的诚实边界，当前仍生效

## 成功标准

- **SC-051-001**：`051` formal docs 明确表达当前批准的 cleanup mutation allowlist 为空集合  
- **SC-051-002**：reviewer 能从 `051` 直接读出 `050` 的 deferred honesty boundary 继续有效  
- **SC-051-003**：formal docs 明确说明当前没有任何 `src/` / `tests/` 实现修改被放行  
- **SC-051-004**：`task-execution-log.md` 追加记录证据审阅命令、结论与只读验证结果  
- **SC-051-005**：future child work item 可以从 `051` 直接接力，先 formalize cleanup target truth，再进入 failing tests 和实现
