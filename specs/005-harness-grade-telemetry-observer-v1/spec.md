# 功能规格：Harness-Grade Telemetry & Observer V1

**功能编号**：`005-harness-grade-telemetry-observer-v1`  
**创建日期**：2026-03-30  
**状态**：已冻结（V1 baseline）  
**输入**：[`../../docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md`](../../docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md)、[`../../docs/superpowers/plans/2026-03-30-harness-grade-telemetry-observer-v1.md`](../../docs/superpowers/plans/2026-03-30-harness-grade-telemetry-observer-v1.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-30-001` / `FD-2026-03-30-002`

> 口径：本 spec 承接新的 framework self-hosting telemetry/observer 能力，目标是把现有 runtime-first telemetry 升级成 harness-grade baseline；它不是 `004` 的续补，也不是外部业务仓 rollout。

## 范围

- **覆盖**：
  - `self_hosting` profile 下的 V1 harness-grade telemetry baseline
  - profile / mode / trace-context / source-closure / gate-capable payload 的正式合同
  - `command execution`、`test result`、`patch apply`、`file write`、`worker lifecycle`、`trace context propagation` 六类 collector baseline
  - `coverage evaluation`、`constraint / mismatch finding`、`unknown / unobserved / coverage_gap` 的 observer baseline
  - `violation`、`audit summary`、`gate decision payload` 的 V1 治理闭环
  - `verify / close / release` 收口面对高置信 observer 结果的消费
  - bounded `status --json` / `doctor` 与最小 manual telemetry CLI surface
- **不覆盖**：
  - `external_project` 的首期 rollout
  - 全量 `file_read` 自动采集
  - 完整会话全文采集
  - 常驻实时 observer
  - 跨 session viewer / replay 平台
  - 复杂 root cause 自动推断与 improvement proposal 自动生成

## 已锁定决策（must-before-v1）

- V1 manual telemetry surface 明确锁定为最小 CLI：`open-session`、`close-session`、`record-event`、`record-evidence`、`record-evaluation`、`record-violation`
- `incident report` 在 V1 锁定为 `contract-preserved deferred artifact`
- `evaluation summary` 在 V1 锁定为 `contract-preserved deferred artifact`，不作为 V1 正式治理输出强制启用

## 用户故事与验收

### US-005-1 — Framework Maintainer 需要可信事实层

作为**框架维护者**，我希望关键执行边界能自动落成 append-only raw trace，以便后续解释与治理建立在单一事实层之上，而不是执行者自报。

**验收**：

1. Given 进入框架自迭代执行链，When 发生命令、测试、patch、文件写入与 worker 生命周期事件，Then raw trace 能以统一主键链和来源语义落盘
2. Given 发生事实层缺口，When observer 分析，Then 系统返回 `unknown / unobserved / coverage_gap`，而不是伪造完整结论

### US-005-2 — Observer 需要独立于执行者产生治理对象

作为**observer / framework reviewer**，我希望解释层和治理层从 facts 独立派生，以便结论不被执行 agent 自我美化。

**验收**：

1. Given 同一事实层和同一 `observer_version / policy / profile / mode`，When 重跑 observer，Then 得到相同结构化结果
2. Given 证据不足，When 运行 observer，Then 能正式输出“不能判断”的结构化对象

### US-005-3 — Gate Consumer 需要只消费高置信治理对象

作为**verify / close / release gate**，我希望只消费带 `confidence`、`evidence refs` 与 `source closure` 的治理对象，以便收口阻断可追溯。

**验收**：

1. Given observer 产出高置信且来源闭包成立的 blocker 候选，When 到达 `verify / close / release`，Then gate 可消费它
2. Given 只有 raw trace 或来源闭包不成立，When 到达收口面，Then gate 不得直接阻断

### US-005-4 — Framework Self-Hosting 需要低摩擦默认模式

作为**框架自迭代执行者**，我希望默认是轻量采集常开、`execute` 不默认阻断，以便简单任务不被事故调查模式拖慢。

**验收**：

1. Given 日常 `execute`，When 运行 V1 telemetry baseline，Then 自动采集常开但默认不进入 execute blocker
2. Given `verify / close / release`，When observer 产出高置信治理结果，Then 自动阻断只在这些收口面生效

## 功能需求

### Shared Kernel Contracts

| ID | 需求 |
|----|------|
| FR-005-001 | 系统必须冻结 `profile`、`mode`、`confidence`、`trigger_point_type`、`source_closure_status`、`governance_review_status` 等 V1 枚举合同 |
| FR-005-002 | 系统必须定义稳定的 `TraceContext`，至少覆盖 `goal_session_id`、`workflow_run_id`、`step_id`、`worker_id`、`agent_id`、`parent_event_id` |
| FR-005-003 | `Raw Trace Store` 必须保持 append-only，并作为唯一事实真值层 |
| FR-005-004 | `gate decision payload` 从 V1 起必须是 gate-capable，并携带 `decision subject`、`confidence`、`evidence refs`、`source_closure_status`、`observer version`、`policy/profile/mode` |

### Runtime Binding And Collection

| ID | 需求 |
|----|------|
| FR-005-005 | `self_hosting` 与 `mode` 必须在 `session/run` 启动时显式绑定，并允许受控升级 |
| FR-005-006 | 任何 mode 切换都必须留下最小结构化记录：`old_mode`、`new_mode`、`changed_at`、`changed_by`、`reason`、`applicable_scope` |
| FR-005-007 | V1 collector baseline 必须自动采集 `command execution`、`test result`、`patch apply`、`file write`、`worker lifecycle`、`trace context propagation` |
| FR-005-008 | collector 不得产生 `coverage_gap`、`violation` 或 blocker 语义；它只能采集事实，不做高层解释 |

### Observer And Governance

| ID | 需求 |
|----|------|
| FR-005-009 | observer 必须在 `step / batch` 结束后异步触发，且不得先于 raw trace append 完成开始分析 |
| FR-005-010 | observer 至少必须产出 `coverage evaluation`、`constraint / mismatch finding`、`unknown / unobserved / coverage_gap` |
| FR-005-011 | observer 结果在固定 `observer_version + policy + profile + mode` 下必须可重复计算 |
| FR-005-012 | V1 治理层至少必须产出 `violation`、`audit summary`、`gate decision payload`；`evaluation summary` 与 `incident report` 保持 `contract-preserved deferred artifact` |

### Gate And Bounded Surfaces

| ID | 需求 |
|----|------|
| FR-005-013 | 自动阻断只允许先落在 `verify / close / release` 等收口面，`execute` 默认保持 advisory-only |
| FR-005-014 | `Gate Consumer` 不得直接扫描 raw trace，只能消费满足最小条件的结构化治理对象 |
| FR-005-015 | `status --json` 与 `doctor` 必须保持 bounded、read-only、无 deep scan / implicit rebuild / implicit init |
| FR-005-016 | V1 manual telemetry surface 必须锁定为最小 CLI：`open-session`、`close-session`、`record-event`、`record-evidence`、`record-evaluation`、`record-violation` |

### Explicit Deferrals

| ID | 需求 |
|----|------|
| FR-005-017 | `external_project` rollout 必须后置，但不得因此分叉底层内核 |
| FR-005-018 | deferred 能力必须保留 schema slots、payload contracts 与兼容扩展点，不得通过删模型语义来“先落地” |

## 成功标准

- **SC-005-001**：facts 能通过统一 trace contracts 稳定落盘，并保持 parent-chain / source refs 可解析
- **SC-005-002**：observer 能对同一事实层重复产出相同结构化结果，并能正式拒绝下结论
- **SC-005-003**：`verify / close / release` 只消费高置信、可追溯、来源闭包成立的治理对象
- **SC-005-004**：`execute` 默认不阻断，简单任务不会被 observer 误升级成事故调查模式
- **SC-005-005**：`status --json` / `doctor` 仍保持 bounded read-only，不因 V1 baseline 引入新的隐式写副作用
- **SC-005-006**：paired positive / negative smoke 至少覆盖 `source closure`、`gate consumption`、`mode/profile drift`、`collector boundary`
