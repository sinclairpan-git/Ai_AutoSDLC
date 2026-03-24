# SPEC 拆分与 Program 并行执行规范

本规范用于回答三个问题：

1. 什么时候一个 PRD 只用一个 SPEC。
2. 什么时候必须拆成多个 SPEC，并如何声明依赖。
3. 并发开发后，如何由 Program Integrator 收口、验收、归档与提交。

## 1. 单 SPEC 与多 SPEC 判定

### 1.1 适合单 SPEC（倾向同时满足）

- 单一发布单元，本期范围可在一个 `specs/NNN-*` 中清晰定义。
- 领域/数据模型强耦合，拆分会导致共享文件高频冲突。
- 无法通过契约先行将依赖切开。

### 1.2 必须拆分多 SPEC（满足任一条）

- 能力域可独立验收，且有不同发布节奏。
- 文件、接口、数据边界可隔离，能满足 `rules/multi-agent.md` 的并行条件。
- 单 SPEC 任务规模过大（如任务数过高、并行组无法安全划分）。

## 2. Program Manifest 约定

使用 `program-manifest.yaml` 作为程序级调度输入。每个 spec 节点至少包含：

- `id`: 唯一标识
- `path`: `specs/NNN-*` 目录
- `depends_on`: 依赖 spec id 列表（DAG）
- `branch_slug`（建议）: 分支命名短标识

推荐额外维护：

- `parent_prd_ref`
- `produces_contracts` / `consumes_contracts`

## 3. Program 命令使用

- `ai-sdlc program validate`: 校验 manifest（重复、缺失、环依赖、路径）
- `ai-sdlc program status`: 查看每个 spec 的阶段提示与任务完成度
- `ai-sdlc program plan`: 输出拓扑顺序与可并行 tiers

## 4. 收口 Agent（Program Integrator）

Program Integrator 负责跨 spec 收口，不替代单 spec 的 Agent-Main。

职责：

1. 按 DAG 排序生成合并顺序。
2. 每一步合并前后执行验证（`rules/verification.md`）。
3. 汇总 PRD 追溯矩阵，确认 FR/SC 覆盖完整。
4. 完成归档（execution-log / summary）后再推进。

## 5. 强制约束（与工程规范对齐）

- 不允许绕过 `rules/quality-gate.md` 与 `rules/verification.md`。
- 并发执行必须遵守 `rules/multi-agent.md` 的隔离要求。
- 归档先于继续，遵守 `rules/pipeline.md`。
