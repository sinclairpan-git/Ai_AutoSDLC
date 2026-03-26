# 缺陷描述：CLI 升级后无法认领旧产物，流水线长期停留在 init

## 问题摘要

在旧版本 CLI 已经生成阶段产物的项目中，升级到 `0.2.4` 后重新执行 `ai-sdlc`，当前 CLI 无法根据既有产物自动回填 pipeline/checkpoint 状态，导致 `status`、`recover`、`run --dry-run` 仍显示 `init` 与 `Feature ID: unknown`，后续阶段被前置校验锁死。

该问题已经在本仓库通过最小复现确认，不是单一现场操作失误。

## 复现步骤

### 现场复现条件

- 项目目录已存在 `.ai-sdlc/`
- 已有旧版开发产物：
  - `product-requirements.md`
  - `spec.md`
  - `research.md`
  - `data-model.md`
  - `plan.md`
  - `tasks.md`
- 状态文件存在漂移：
  - `project-state.yaml` 中仍残留旧字段/旧阶段信息
  - `checkpoint.yml` 中 `current_stage: init`
  - `feature.id = unknown`
  - `completed_stages = []`

### 终端复现步骤

1. 在一个已初始化项目中保留上述根目录旧产物。
2. 令 `.ai-sdlc/state/checkpoint.yml` 处于“空白/过时”状态：
   - `current_stage = init`
   - `feature.id = unknown`
   - `feature.spec_dir = specs/unknown`
3. 运行以下命令：

```bash
ai-sdlc status
ai-sdlc recover
ai-sdlc run --dry-run
ai-sdlc stage run refine --dry-run
```

### 当前实际结果

- `ai-sdlc status`
  - `Pipeline Stage: init`
  - `Completed Stages: none`
  - `Feature ID: unknown`
- `ai-sdlc recover`
  - 只会“恢复”到 `init`
  - 不会扫描现有产物并回填阶段
- `ai-sdlc run --dry-run`
  - 输出 `Pipeline completed. Stage: init`
- `ai-sdlc stage run refine --dry-run`
  - 报 `前置阶段未完成: init`

### 期望结果

- CLI 至少应提供一种正式路径，让旧项目的既有产物被认领为合法阶段上下文，而不是永久停留在 `init/unknown`
- `status` / `recover` / `run` 的状态判断不应与磁盘上的合法产物长期分叉

## 根因

### 根因 1：当前 pipeline 真值只认 checkpoint

当前实现中：

- `status` 读取 `checkpoint.yml`
- `recover` 基于 `checkpoint.yml` 构建 resume pack
- `run` 从 `checkpoint.current_stage` 启动
- Runner 不会因为磁盘上存在 `spec.md` / `plan.md` / `tasks.md` 自动推断阶段

这导致“已有产物”与“checkpoint 真值”一旦分叉，CLI 只会相信 checkpoint。

### 根因 2：旧版状态信息没有兼容迁移

现场问题里，旧版 `project-state.yaml` 中的阶段信息没有被新版模型吸收；新版只关心 `status/project_name/version/...`，不会把旧字段自动迁移到 checkpoint。

因此，即使旧版本曾记录过阶段线索，新版也会静默忽略。

### 根因 3：旧版根目录产物布局与新版 `specs/<WI>/` 假设断层

当前实现广泛假设：

- `spec.md`
- `plan.md`
- `tasks.md`
- `research.md`
- `data-model.md`

位于 `specs/<WI>/` 下，并通过 `feature.spec_dir` 统一解析。

但现场旧项目的产物位于项目根目录。即使补齐 checkpoint，如果不同时兼容根目录旧布局，`recover/gate/verify` 仍会认不全。

## 影响范围

- 旧项目升级到 `0.2.4` 或更高版本的兼容性
- `status` / `recover` / `run` / `stage run` 的阶段判断
- 旧版项目的断点恢复与阶段延续
- 生产环境或历史项目的继续开发效率
- 用户对“已有产物可复用”这一规则承诺的信任

## 修复目标

### 目标 1：提供正式的状态对齐路径

为旧项目提供明确的 checkpoint 对齐能力，能够把“已有合法产物”回填为可继续执行的 pipeline 状态。

可接受形式包括：

- `recover` 内置 reconcile/backfill
- 单独命令，如 `checkpoint sync`
- 或其他显式、可验证、不会误判的入口

### 目标 2：兼容旧版根目录产物布局

至少要支持识别根目录旧布局下的：

- `product-requirements.md`
- `spec.md`
- `research.md`
- `data-model.md`
- `plan.md`
- `tasks.md`

并将其映射为合法的恢复上下文。

### 目标 3：避免继续制造双状态漂移

修复后应确保：

- `status` 展示的阶段
- `recover` 构建的恢复点
- `run` 的起始阶段

建立在同一条正式状态链上，而不是再增加第三套“猜测状态”。

## 验收标准

1. 给定“旧版根目录产物齐全 + 过时 checkpoint”的夹具，执行正式状态对齐入口后，`ai-sdlc status` 不再显示 `Feature ID: unknown` 与长期 `Pipeline Stage: init`。
2. 在同一夹具上，`ai-sdlc recover` 能恢复到与已有产物一致的阶段上下文，而不是机械停留在 `init`。
3. 在同一夹具上，`ai-sdlc run --dry-run` 不再只输出 `Stage: init`，而能从对齐后的阶段继续。
4. 在同一夹具上，若已有 `spec/plan/tasks` 满足门禁，后续阶段不再因为“前置阶段未完成: init”被永久锁死。
5. 若输入状态不足以安全判断阶段，CLI 必须给出明确、可操作的提示，而不是静默回落到 `init/unknown`。
6. 补充自动化回归测试，覆盖：
   - 根目录旧布局
   - `specs/<WI>/` 新布局
   - 旧 `project-state.yaml` 字段残留
   - stale / blank checkpoint

## 备注

- 本缺陷已同步登记到 [`docs/framework-defect-backlog.zh-CN.md`](../framework-defect-backlog.zh-CN.md) 的 `FD-2026-03-26-002`。
- 当前分支：`codex/framework-defect-backlog`
