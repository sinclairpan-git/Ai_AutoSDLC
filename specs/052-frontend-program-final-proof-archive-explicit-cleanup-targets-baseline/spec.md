# 功能规格：Frontend Program Final Proof Archive Explicit Cleanup Targets Baseline

**功能编号**：`052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`](../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md)

> 口径：`052` 不是直接进入 cleanup mutation 实现，而是先把 “explicit cleanup targets 应该以什么 canonical truth 进入链路” 冻结清楚。当前 work item 只定义单一真值形态、审批口径和语义边界，不修改 `ProgramService`、CLI 或 tests。

## 问题定义

`050` 已经冻结 final proof archive project cleanup 的 request/result/artifact baseline，并要求在没有安全且已定义的 cleanup action 时诚实返回 `deferred`。`051` 进一步冻结了当前事实：批准的 cleanup mutation allowlist 仍为空集合，因为仓库里还不存在被正式纳入真值链的 explicit cleanup targets。

因此，`052` 需要先回答未来实现之前的 formal truth 问题：

- cleanup target 应该以什么字段结构进入单一真值链
- cleanup target 的来源、审批和确认语义是什么
- “没有 target” 与 “target 为空列表” 的语义如何区分
- 哪些信号绝不能被当作 cleanup target inferred truth

本 work item 的目标是把上述问题冻结成 canonical docs，给后续 failing tests 和实现一个稳定前提。

## 范围

- **覆盖**：
  - 定义 explicit cleanup targets 的 canonical truth surface
  - 明确 cleanup target 必须并入 `050` final proof archive project cleanup artifact truth，不新增第二套 artifact
  - 定义 `cleanup_targets` 的最小字段、排序与校验约束
  - 定义 provenance / approval / operator confirmation 语义
  - 定义 `cleanup_targets` 缺失、空列表与已列出目标三种状态的边界
  - 明确未来实现必须先写 failing tests，再改 `ProgramService` / CLI
- **不覆盖**：
  - 修改 `050`/`051` 已冻结结论
  - 实现任何真实 workspace mutation
  - 修改 `src/ai_sdlc/core/program_service.py`
  - 修改 `src/ai_sdlc/cli/program_cmd.py`
  - 修改 `tests/unit/test_program_service.py`
  - 修改 `tests/integration/test_cli_program.py`
  - 依据 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名或 git working tree 状态推断 cleanup target

## 已锁定决策

- explicit cleanup targets 的 canonical truth 名称为 `cleanup_targets`
- `cleanup_targets` 必须作为 `050` final proof archive project cleanup artifact 的字段进入单一真值链，而不是独立新 artifact
- `cleanup_targets` 必须是有序列表；列表顺序即 operator-facing cleanup 展示顺序
- 每个 cleanup target 都必须显式记录来源与审批依据，不能由实现阶段推断补齐
- `cleanup_targets` 缺失表示“上游尚未 formalize target truth”；空列表 `[]` 表示“已 formalize 且当前批准 target 为空”
- 只有在 `cleanup_targets` 已 formalize 且 operator 明确确认后，未来 mutation work item 才能考虑执行真实 cleanup
- `052` 当前阶段只允许修改 `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/` 内文档与脚手架自动更新的 project state

## Cleanup Target Canonical Truth

`cleanup_targets` 定义为有序对象列表：

```yaml
cleanup_targets:
  - target_id: cleanup-thread-archive-report
    path: .ai-sdlc/reports/program/final-proof-archive/thread-archive/example.md
    target_kind: file
    cleanup_action: archive_or_remove
    source_artifact: final-proof-archive-project-cleanup
    justification: superseded by canonical final proof archive artifact
```

### 每个 target 的必填字段

| 字段 | 含义 |
|------|------|
| `target_id` | 稳定、可审计、在同一 artifact 内唯一的 target 标识 |
| `path` | 以仓库根为基准的 canonical path，不允许通配符 |
| `target_kind` | `file` 或 `directory` |
| `cleanup_action` | 被批准的 cleanup 动作名称；当前只定义语义，不授权立即执行 |
| `source_artifact` | 声明该 target 由哪个 canonical artifact 审批并输出 |
| `justification` | 解释该 target 为何可被 cleanup 的短文本理由 |

### 约束

- `path` 必须是显式路径，不允许 glob、前缀匹配、正则或派生推断
- 同一 `cleanup_targets` 列表内不得出现重复 `target_id` 或重复 `path`
- `target_kind=directory` 不自动授权递归删除语义；未来实现必须在 tests 中显式固定
- `cleanup_action` 是审批 truth，不等于“已经执行”
- 若 `cleanup_targets` 缺失，未来 execute 必须继续诚实返回 `deferred`
- 若 `cleanup_targets: []`，未来 execute 也必须诚实返回 `deferred`

## 用户故事与验收

### US-052-1 — Framework Maintainer 需要单一的 cleanup target truth

作为 **框架维护者**，我希望 cleanup targets 被定义为 `050` artifact 内的 canonical 字段，以便后续实现不会再创建第二套 cleanup truth。

**验收**：

1. Given 我阅读 `052` formal docs，When 我确认 target truth 位置，Then 我能明确看到 `cleanup_targets` 属于 `050` cleanup artifact
2. Given 我评审后续设计，When 我检查 artifact 设计，Then 我看不到新的旁路 cleanup artifact

### US-052-2 — Reviewer 需要阻止 inferred cleanup target

作为 **reviewer**，我希望 `052` 明确禁止通过目录命名、`written_paths` 或工作树状态推断 cleanup target，以便后续实现只能消费显式批准的目标。

**验收**：

1. Given 我阅读 `052`，When 我寻找 target 来源，Then 我只能看到显式字段和审批语义
2. Given 我准备 review 后续实现，When 我确认 non-goals，Then 我能明确知道哪些信号不能被视为 target truth

### US-052-3 — 后续实现者需要知道进入代码前的顺序

作为 **后续实现者**，我希望 `052` 明确区分缺失 target truth 与空 allowlist，并给出 test-first 顺序，以便下一子项可以直接进入 failing tests。

**验收**：

1. Given 我阅读 `052`，When 我查找边界语义，Then 我能区分 `cleanup_targets` 缺失与 `cleanup_targets: []`
2. Given 我继续推进实现，When 我查找下一步，Then 我能直接得到 `tests -> service -> CLI` 的顺序

## 功能需求

| ID | 需求 |
|----|------|
| FR-052-001 | `052` 必须将 explicit cleanup targets 定义为 `cleanup_targets` canonical truth surface |
| FR-052-002 | `052` 必须明确 `cleanup_targets` 属于 `050` final proof archive project cleanup artifact，而非新 artifact |
| FR-052-003 | `052` 必须规定 `cleanup_targets` 为有序列表，并将列表顺序定义为 operator-facing 展示顺序 |
| FR-052-004 | `052` 必须定义每个 cleanup target 的必填字段：`target_id`、`path`、`target_kind`、`cleanup_action`、`source_artifact`、`justification` |
| FR-052-005 | `052` 必须禁止使用 glob、目录命名、`written_paths`、reports 聚类、deliverables 归纳或 git working tree 状态推断 cleanup target |
| FR-052-006 | `052` 必须明确区分 `cleanup_targets` 缺失 与 `cleanup_targets: []` 的语义 |
| FR-052-007 | `052` 必须明确 `cleanup_action` 是被批准的动作语义，不等于已执行结果 |
| FR-052-008 | `052` 必须要求未来 mutation work item 先用 failing tests 固定 target/result semantics，再进入 service 和 CLI 实现 |
| FR-052-009 | `052` 必须保持 docs-only 范围，不修改 `src/` 或 `tests/` |
| FR-052-010 | `052` 必须把脚手架生成、证据对账与只读验证记录到 append-only `task-execution-log.md` |

## 关键实体

- **Cleanup Targets**：`050` cleanup artifact 内的有序 target truth 列表
- **Cleanup Target Entry**：单个 cleanup target 的 canonical truth 对象
- **Target Truth State**：`missing`、`empty`、`listed` 三种 cleanup target 状态
- **Cleanup Action Semantics**：被批准的动作语义，不代表执行完成

## 成功标准

- **SC-052-001**：formal docs 明确把 `cleanup_targets` 固定为 `050` cleanup artifact 的字段  
- **SC-052-002**：formal docs 明确列出 cleanup target 的最小字段与约束  
- **SC-052-003**：formal docs 明确禁止 inferred cleanup target  
- **SC-052-004**：formal docs 明确区分 `missing` 与 `empty` target truth 语义  
- **SC-052-005**：`task-execution-log.md` 追加记录脚手架、文档冻结与只读验证结果
