# 功能规格：AI-SDLC 原 PRD 外新增能力与 Operator Surfaces

**功能编号**：`004-operator-surfaces-and-post-prd-extensions`  
**创建日期**：2026-03-28  
**状态**：草案  
**输入**：当前仓库已实现能力（Program / Telemetry / Stage / Doctor / Scan / IDE Adapter / Offline Packaging）；缺口收敛总表 RG-020 ~ RG-023（仅承接原 PRD 外新增能力）

> 口径：本 spec 只承接**原 PRD 之外、但仓库已实现并形成事实标准**的后续新增能力，不用于回填原 PRD 旧债。

## 范围

- **覆盖**：
  - 原 PRD 之外、已在仓库落成事实标准的后续新增能力
  - Program Manifest 与多 spec 编排
  - Telemetry operator surfaces 与 bounded status/doctor 合同
  - `doctor` / `scan` / `stage` 等 operator CLI
  - IDE Adapter / `project-config.yaml` 运行时合同
  - 离线打包与安装分发合同
- **不覆盖**：
  - 原 PRD 旧债的回填与分流
  - 原 PRD 主闭环中的 core routing / governance / execute 合同
  - `002` 中的具体 Studio / Parallel / Refresh runtime 行为

## 用户故事与验收

### US-004-1 — Program Integrator 跨 spec 编排

作为**Program Integrator**，我希望通过 `program-manifest` 查看依赖、状态与集成计划，以便在多 spec 并发开发后执行受保护的收口。

**验收**：

1. Given 多个 spec 节点，When 执行 `program validate`，Then 能发现 path / deps / cycle 问题
2. Given manifest 合法，When 执行 `program status` / `program plan`，Then 能看到每个 spec 的阶段提示与依赖阻塞
3. Given 所有节点达到可集成条件，When 执行 guarded integrate，Then 能输出执行计划与 gate 结果

### US-004-2 — Operator 读取受控状态而不产生副作用

作为**运维 / 框架维护者**，我希望 `doctor`、`status --json`、`scan` 等 surface 在读状态时保持边界清晰，以便诊断不会隐式改变仓库。

**验收**：

1. Given 未初始化或部分初始化状态，When 执行 read-only operator surface，Then 不得偷偷生成无关状态文件
2. Given 诊断输出，When 读取结果，Then 能区分 read-only surface 与 mutating command

### US-004-3 — Telemetry 可作为 operator 证据面

作为**框架维护者**，我希望 telemetry 的本地证据、reports 与 operator CLI 有正式合同，以便治理面可审计。

**验收**：

1. Given telemetry 未初始化，When 执行 bounded status/doctor，Then 返回有限状态而非触发深度初始化
2. Given 需要人工记录证据，When 执行 telemetry manual commands，Then 写入 canonical store

### US-004-4 — IDE Adapter 与本地配置契约稳定

作为**多 IDE 使用者**，我希望 IDE adapter 的触发时机、生成文件与缺省行为稳定，以便 CLI 与编辑器集成可预测。

**验收**：

1. Given 初始化后的项目，When 触发 IDE adaptation，Then `project-config.yaml` 与 adapter 文件按契约生成
2. Given 缺失本地配置文件，When 读取配置，Then 回落到默认模型，而不是报错

### US-004-5 — 离线分发可作为正式交付面

作为**企业内网用户**，我希望离线 bundle 的构建、安装与平台兼容性有正式约束，以便离线环境可重复部署。

**验收**：

1. Given 构建离线 bundle，When 在同 OS/CPU 环境安装，Then CLI 可用
2. Given 跨平台 bundle 被误用，When 查看文档或检查输出，Then 有明确限制说明

## 功能需求

### Program Orchestration

| ID | 需求 |
|----|------|
| FR-004-001 | 系统必须定义 `program-manifest` 的 schema、依赖校验、cycle 检测与 path 校验合同 |
| FR-004-002 | 系统必须提供 Program 级 `validate`、`status`、`plan`、`integrate` surfaces |
| FR-004-003 | `program integrate --execute` 必须受显式确认与 execute gates 保护 |
| FR-004-004 | Program 状态面必须能表达 `blocked_by`、阶段提示与最小收口条件 |

### Telemetry Operator Surfaces

| ID | 需求 |
|----|------|
| FR-004-005 | bounded `status --json` / `doctor` telemetry surface 必须保持只读与有界，不得触发深度重建 |
| FR-004-006 | manual telemetry commands 必须经 canonical writer 写入事件、证据、评估与违规对象 |
| FR-004-007 | telemetry 本地 traces 与 project reports 必须区分存储边界与语义边界 |

### Operator CLI

| ID | 需求 |
|----|------|
| FR-004-008 | `doctor` 必须输出环境、PATH、telemetry readiness 等只读诊断 |
| FR-004-009 | `scan` 必须提供深度扫描 surface，并明确其为 operator/analysis 命令 |
| FR-004-010 | `stage` surfaces 必须表达阶段清单、dry-run 与阶段状态，而不替代 full runner |

### IDE Adapter 与本地配置

| ID | 需求 |
|----|------|
| FR-004-011 | IDE adapter 的触发时机、输出位置与幂等行为必须形成正式合同 |
| FR-004-012 | `.ai-sdlc/project/config/project-config.yaml` 缺失时必须回落到默认模型，并允许运行时重建 |

### Offline Distribution

| ID | 需求 |
|----|------|
| FR-004-013 | 离线 bundle 的构建产物、安装入口与适用平台必须被正式定义 |
| FR-004-014 | 离线安装合同必须明确“同 OS/CPU 构建并安装”的兼容性边界 |
| FR-004-015 | Operator surfaces 与离线分发文档必须明确哪些命令只读、哪些命令会修改仓库状态 |

## 成功标准

- **SC-004-001**：Program manifest 的 path / dep / cycle 错误可被 `program validate` 发现
- **SC-004-002**：guarded `program integrate --execute` 在条件不满足时返回明确 gate failure
- **SC-004-003**：Telemetry bounded status/doctor 在未初始化状态下保持只读
- **SC-004-004**：`doctor` / `scan` / `stage` 三类 surfaces 的边界在文档中被锁定
- **SC-004-005**：IDE adapter 与 `project-config.yaml` 的缺省 / 重建行为可被一致描述
- **SC-004-006**：离线 bundle 的适用平台、安装入口与限制条件被正式锁定
