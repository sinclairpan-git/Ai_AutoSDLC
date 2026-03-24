# 多 Agent 并行协议

> 本规则在 DECOMPOSE 阶段的任务标记和 EXECUTE 阶段的批次执行中激活。
> 当运行环境支持多 Agent 并行时，协调多个 Agent 同时工作以提高效率。

## 术语边界（避免混淆）

- **Spec Agent-Main**：单个 `specs/NNN-*` 内部并行调度者（本文既有 Step P1~P4 角色）。
- **Program Integrator**：跨多个 spec 的程序级收口者，负责依赖顺序合并、验证、归档与发布。
  Program Integrator 规则详见 `docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md` 与
  CLI `ai-sdlc program integrate` 命令约束。

## 核心原则

```
并行提效，但绝不牺牲正确性。
每个 Agent 有明确边界，产出有交叉校验。
文件冲突是并行的死敌 — 消灭共享文件。
```

## 前置条件：能力检测

**不是所有环境都支持多 Agent 并行。** 在 Stage 0 INIT 阶段进行能力检测：

```
检测项：
  1. 当前 AI 工具是否支持多 Agent / 并行任务？
     - Cursor: 支持（background agents / Task tool）
     - Claude Code: 支持（parallel tool calls / 多终端）
     - Codex: 支持（并行 sandbox）
     - VS Code + Copilot: 有限支持（单线程为主）
     - 其他: 需评估

  2. 检测结果写入 checkpoint.yml：
     multi_agent:
       supported: true | false
       max_parallel: 3          # 建议并行数（保守值）
       tool_capability: "cursor-background-agents"

  3. 如果不支持 → 所有任务串行执行，[PA] 标记仅作为未来参考
     如果支持 → 在 EXECUTE 阶段启用并行调度
```

## Stage 3 DECOMPOSE：并行标记

### 任务并行级别

在 tasks.md 中，任务的并行标记从原有的 `[P]`（同批次内可并行）升级为两级：

```
标记    含义                            适用范围
────    ────                            ────────
[P]     批次内可并行（同一 Agent 内）      修改不同文件、无共享依赖的任务
[PA]    Agent 级可并行（不同 Agent 间）    完全独立的模块/服务/组件，可分配给不同 Agent
无标记   必须串行                          有依赖顺序的任务
```

### [PA] 标记的判定条件

**所有条件必须同时满足，才能标记 [PA]：**

```
条件 1：文件隔离
  两个任务修改的文件集合完全不重叠。
  不仅是"主文件"，还包括可能修改的配置文件、测试文件、共享类型定义等。

  ✅ Agent A 改 src/service/user/ + test/service/user/
     Agent B 改 src/service/order/ + test/service/order/

  ❌ Agent A 改 src/service/user/ + src/shared/types.ts
     Agent B 改 src/service/order/ + src/shared/types.ts
     → types.ts 重叠，不能标 [PA]

条件 2：接口隔离
  两个任务不互相调用对方正在开发的函数/接口。
  如果 A 的实现需要调用 B 的输出 → 不能并行。

  ✅ Agent A 实现用户注册 API
     Agent B 实现课程管理 API（两个 API 互不调用）

  ❌ Agent A 实现用户注册
     Agent B 实现报名（报名需调用用户注册的接口）
     → 有依赖，不能标 [PA]

条件 3：数据隔离
  两个任务不操作同一张数据库表（或同一状态存储）。
  如果都要改 user 表 → 不能并行（可能产生 migration 冲突）。

  ✅ Agent A 建 user 表 + 操作 user 表
     Agent B 建 course 表 + 操作 course 表

  ❌ Agent A 建 user 表
     Agent B 在 user 表上加字段
     → 同表操作，不能标 [PA]

条件 4：测试隔离
  两个任务的测试可以独立运行，互不影响。
  共享测试 fixture、全局 mock、数据库 seed → 不能并行。
```

### tasks.md 中的并行标注格式

```markdown
## Phase 3: 用户故事实现

### Parallel Group A（可分配给独立 Agent）
- [ ] T015 [PA] [US1] 实现用户注册服务 | src/service/user/**
- [ ] T016 [PA] [US1] 新增用户注册测试 | test/service/user/**
- [ ] T017 [PA] [US1] 实现用户注册 API  | src/controller/user/**

### Parallel Group B（可分配给独立 Agent）
- [ ] T018 [PA] [US2] 实现课程管理服务 | src/service/course/**
- [ ] T019 [PA] [US2] 新增课程管理测试 | test/service/course/**
- [ ] T020 [PA] [US2] 实现课程管理 API  | src/controller/course/**

### Sequential（必须串行，依赖 Group A + B 的输出）
- [ ] T021 [US3] 实现报名服务（依赖 user + course）| src/service/signup/**
- [ ] T022 [US3] 新增报名测试 | test/service/signup/**

### 并行元信息
- Parallel Groups: 2 (A, B)
- 可并行任务: 6 / 总任务 8
- 预计并行加速比: ~1.8x
- 文件隔离确认: ✅ Group A 和 B 无共享文件
- 接口隔离确认: ✅ Group A 和 B 无互相调用
- 数据隔离确认: ✅ Group A 和 B 操作不同表
```

## EXECUTE 阶段：并行调度

### 调度模式

```
模式 1：串行（默认，或多 Agent 不支持时）
  Batch 1 → Batch 2 → Batch 3 → ...
  所有批次由同一个 Agent 按顺序执行

模式 2：组内并行（推荐，多 Agent 支持时）
  当一个 Phase 包含多个 Parallel Group 时：
    Agent-Main: 协调者，负责调度和验收
    Agent-A: 执行 Parallel Group A
    Agent-B: 执行 Parallel Group B
    ...
  Group 全部完成后 → 合并验证 → 串行任务继续
```

### 并行执行协议

```
┌────────────────────────────────────────────────────────┐
│ Step P1：分发前准备                                      │
│                                                        │
│ 1. Agent-Main 读取 tasks.md，识别当前 Phase 的          │
│    Parallel Groups                                     │
│ 2. 为每个 Group 准备上下文包：                            │
│    ├── PRD 摘要（仅与该 Group 相关的用户故事）             │
│    ├── constitution.md（完整）                           │
│    ├── spec.md 中与该 Group 相关的章节                    │
│    ├── plan.md 中与该 Group 相关的模块设计                │
│    ├── data-model.md 中与该 Group 相关的表                │
│    ├── contracts/ 中与该 Group 相关的 API                │
│    ├── tech-stack.yml（完整）                            │
│    └── 该 Group 的任务列表（带文件路径）                   │
│ 3. 为每个 Group 明确定义文件边界：                        │
│    Agent-A 只能修改: [文件列表 A]                        │
│    Agent-B 只能修改: [文件列表 B]                        │
│    共享文件: [列表] → 全部由 Agent-Main 在合并时处理      │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Step P2：并行执行                                        │
│                                                        │
│ 每个 Agent 独立执行自己的 Group：                         │
│   1. 预读上下文包                                       │
│   2. TDD 循环（遵循 rules/tdd.md）                      │
│   3. 调试（遵循 rules/debugging.md）                    │
│   4. 代码审查（遵循 rules/code-review.md）              │
│   5. 记录 execution-log 的该 Group 部分                 │
│   6. 不执行 git commit（等待合并验证后统一提交）          │
│                                                        │
│ 每个 Agent 的约束：                                     │
│   ❌ 不能修改文件边界外的文件                             │
│   ❌ 不能修改共享文件（types.ts、配置文件等）              │
│   ❌ 不能 git commit（由 Main 统一提交）                 │
│   ❌ 不能修改 tasks.md（由 Main 统一更新）               │
│   ✅ 可以创建新文件（在自己的文件边界内）                  │
│   ✅ 可以运行自己 Group 的测试                           │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Step P3：合并验证（Agent-Main 执行）                      │
│                                                        │
│ 所有并行 Agent 完成后：                                  │
│                                                        │
│ 1. 文件冲突检测                                         │
│    git diff --name-only 检查是否有同一文件被多个 Agent 修改 │
│    冲突 → 阻断，人工介入                                 │
│    无冲突 → 继续                                        │
│                                                        │
│ 2. 编译/构建验证                                        │
│    合并后的代码能否编译通过？                              │
│    失败 → 分析哪个 Agent 的产出导致，由该 Agent 修复      │
│                                                        │
│ 3. 接口一致性检测                                       │
│    Agent A 暴露的接口签名 vs Agent B 期望调用的签名        │
│    如果后续串行任务需要调用并行任务的输出 → 验证接口匹配    │
│                                                        │
│ 4. 全量回归测试                                         │
│    运行所有 Group 的测试 + 已有的全量测试                  │
│    失败 → 定位到具体 Group → 该 Agent 修复               │
│                                                        │
│ 5. 逻辑一致性检查                                       │
│    ├── 术语一致：各 Agent 使用的命名是否一致？            │
│    ├── 数据流一致：A 的输出格式 = B 的期望输入格式？       │
│    ├── 错误处理一致：各模块的错误码、异常处理风格一致？     │
│    └── 日志格式一致：日志级别、格式是否统一？              │
│                                                        │
│ 6. 需求覆盖验证                                         │
│    所有 Parallel Group 的任务是否完整覆盖？               │
│    有没有需求溢出（做了 spec 没要求的东西）？              │
│    有没有重复实现（两个 Agent 做了同一件事）？             │
│                                                        │
│ 7. 合并后处理                                           │
│    ├── 处理共享文件（如需更新 types.ts → Main 统一写入）  │
│    ├── 更新 tasks.md（勾选所有并行任务）                  │
│    ├── 合并各 Agent 的 execution-log                    │
│    ├── git add + git commit                            │
│    └── 更新断点存档                                     │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Step P4：继续串行任务                                    │
│                                                        │
│ 并行 Group 全部完成并验证通过后：                         │
│ 继续执行 Sequential 任务（如有依赖并行 Group 输出的任务）  │
│ 由 Agent-Main 单线程执行                                │
└────────────────────────────────────────────────────────┘
```

### 共享文件处理策略

```
共享文件的类型和处理方式：

1. 类型定义文件（types.ts, models.d.ts）
   → 在并行前由 Main 预先创建接口定义骨架
   → 并行 Agent 只读不写
   → 合并后由 Main 根据实际实现更新

2. 配置文件（数据库 migration, 路由表, 依赖注入配置）
   → 并行前由 Main 预分配槽位（如路由前缀）
   → 每个 Agent 只修改自己的槽位
   → 合并后由 Main 检查无冲突

3. 全局常量/错误码
   → 并行前由 Main 统一分配范围
   → Agent A: 错误码 1000-1999
   → Agent B: 错误码 2000-2999
   → 合并后由 Main 检查无重叠

4. 第三方依赖文件（package.json, pom.xml, go.mod）
   → 并行 Agent 不直接修改
   → 各 Agent 在 execution-log 中记录"需要新增依赖 [xxx]"
   → 合并时由 Main 统一安装
```

### 并行执行的状态面板

```
┌─ AI-SDLC Pipeline ──────────────────────────────┐
│                                                  │
│  Feature: NNN-[short-name]                       │
│  Mode: auto | Parallel: 2 agents active          │
│                                                  │
│  ✅ INIT  ✅ REFINE  ✅ DESIGN  ✅ DECOMPOSE       │
│  ✅ VERIFY  ▶ EXECUTE  ○ CLOSE                   │
│                                                  │
│  当前：Stage 5 EXECUTE — Phase 3 并行执行          │
│                                                  │
│  Agent-A [Group A: 用户模块]                      │
│    ├─ T015 实现用户注册服务        ✅              │
│    ├─ T016 新增用户注册测试        ✅              │
│    └─ T017 实现用户注册 API        ▶ 执行中...     │
│    进度：████████░░░░ 2/3                         │
│                                                  │
│  Agent-B [Group B: 课程模块]                      │
│    ├─ T018 实现课程管理服务        ✅              │
│    ├─ T019 新增课程管理测试        ▶ 执行中...     │
│    └─ T020 实现课程管理 API        ○              │
│    进度：████░░░░░░░░ 1/3                         │
│                                                  │
│  等待合并验证：Group A ○  Group B ○               │
│                                                  │
└──────────────────────────────────────────────────┘
```

## 防重复与防溢出机制

### 防重复

```
检查时机：Step P3 合并验证 → 第 6 步

检查方法：
  1. 函数/类名去重：扫描所有新增代码，检查是否有两个 Agent 创建了同名函数/类
  2. 功能去重：对照 tasks.md，每个任务只被一个 Group 执行
  3. API 去重：检查是否有重复的路由路径

发现重复：
  → 保留先完成的 Agent 的版本
  → 删除后完成的重复部分
  → 记录到 execution-log
```

### 防溢出

```
检查时机：Step P3 合并验证 → 第 6 步

检查方法：
  1. 文件范围检查：每个 Agent 是否只修改了分配的文件？
  2. 功能范围检查：实现的功能是否超出了 tasks.md 中分配的任务？
  3. API 范围检查：是否创建了 contracts/ 中未定义的 API？
  4. 依赖范围检查：是否引入了 tech-stack.yml 未列出的依赖？

发现溢出：
  → 溢出部分不合并
  → 记录为 WARNING
  → 如果溢出部分对功能必要 → 记录为 AI 决策 + 事后补充到 spec
```

## 降级策略

```
并行执行过程中，如果遇到以下情况，自动降级为串行：

1. Agent 间检测到文件冲突 → 停止并行，切换为串行
2. 合并验证失败 > 2 次 → 停止并行，切换为串行
3. 某个 Agent 在调试循环中 > 2 轮 → 该 Agent 等待，其他 Agent 继续
4. 用户请求关闭并行 → 立即切换为串行

降级时的状态保持：
  → 已完成的 Group 保留成果
  → 未完成的 Group 由 Main 串行继续
  → execution-log 记录"并行 → 串行降级"及原因
```

## 配置

```yaml
# pipeline.yml
multi_agent:
  enabled: auto                  # auto = 自动检测 | true = 强制启用 | false = 禁用
  max_parallel_agents: 3         # 最大并行 Agent 数
  merge_strategy: main_verify    # main_verify = Main 统一验证 | immediate = 即时合并
  allow_shared_files: false      # 是否允许多 Agent 修改同一文件（强烈建议 false）
  fallback_to_serial: true       # 遇到问题时是否自动降级为串行
```

## 与批次协议的集成

当检测到 Parallel Groups 时，`batch-protocol.md` 的批次执行流程调整为：

```
原流程：
  Step 1 → Step 2 → Step 3 → Step 3.5 → Step 4 → Step 4.5 → Step 5 → Step 6

并行流程：
  Step 1（Main 预读 + 准备上下文包）
    → Step P1（分发）
    → Step P2（各 Agent 并行执行 Step 2 + Step 3 的定向测试）
    → Step P3（Main 合并验证 = Step 3 全量回归 + Step 3.5 审查）
    → Step 4（Main 归档）
    → Step 4.5（Main 验证）
    → Step 5（Main 提交）
    → Step 6（模式检查）
```
