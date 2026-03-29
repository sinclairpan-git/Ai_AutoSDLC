# 实施计划：AI-SDLC 原 PRD 外新增能力与 Operator Surfaces

**编号**：`004-operator-surfaces-and-post-prd-extensions` | **日期**：2026-03-28 | **规格**：specs/004-operator-surfaces-and-post-prd-extensions/spec.md

## 概述

本计划只承接原 PRD 之外的既成新增能力建制化：Program manifest、多 spec orchestration、Telemetry bounded status/doctor、manual telemetry canonical writer commands、`doctor` / `scan` / `stage` operator surfaces、IDE adapter / `project-config` 合同、离线分发。实现目标不是“补功能”，而是把已经存在的 operator / packaging 行为锁成正式 contract，并补齐缺少的验证与边界说明。

## 技术背景

**语言/版本**：Python 3.11+ + shell packaging scripts  
**主要依赖**：Typer、Pydantic v2、Rich、pytest、shell scripts  
**存储**：program manifest、telemetry local/index roots、`project-config.yaml`、offline bundle 目录  
**测试**：unit + integration；离线分发以 smoke / script verification 为主  
**目标平台**：macOS + Linux，离线 bundle 需明确同 OS/CPU 约束  
**约束**：不把原 PRD 旧债回填混入本计划

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 只 formalize 现有 operator/post-PRD surfaces，不扩大主闭环 |
| MUST-2 关键路径可验证 | 每个 operator surface 都至少要有 integration 契约测试 |
| MUST-3 范围声明与回退 | Program、Telemetry、IDE、Offline 四块可独立提交 |
| MUST-4 状态落盘 | manifest、readiness、adapter config、offline bundle 产物都有明确真值 |
| MUST-5 产品代码隔离 | CLI / service / integration / packaging 文档分层维护 |

## 项目结构

### 文档结构

```text
specs/004-operator-surfaces-and-post-prd-extensions/
├── spec.md
├── plan.md          ← 本文件
└── tasks.md         ← 本次补齐
```

### 源码结构

```text
src/ai_sdlc/
├── models/
│   ├── program.py                # program-manifest schema
│   └── project.py                # project-config / adapter state
├── core/program_service.py       # program validate/status/plan/integrate helpers
├── cli/
│   ├── program_cmd.py            # program CLI
│   ├── doctor_cmd.py             # doctor surface
│   ├── stage_cmd.py              # stage surfaces
│   └── commands.py               # status/json/scan/refresh shared entry
├── telemetry/readiness.py        # bounded status / doctor telemetry probes
├── integrations/ide_adapter.py   # IDE detection + adapter install
└── tests/
    ├── unit/test_program_service.py
    ├── unit/test_ide_adapter.py
    ├── integration/test_cli_program.py
    ├── integration/test_cli_doctor.py
    ├── integration/test_cli_stage.py
    └── integration/test_cli_ide_adapter.py

packaging/offline/
├── build_offline_bundle.sh
├── install_offline.sh
├── install_offline.ps1
├── install_offline.bat
└── README.md
```

## 阶段计划

### Phase 0：Program / operator contract inventory

**目标**：先锁定 Program、Telemetry、Doctor/Stage/Scan、IDE Adapter、Offline 的现有行为边界。  
**产物**：contract 清单与最小测试矩阵。  
**验证方式**：`test_program_service.py`、`test_cli_program.py`、`test_cli_doctor.py`。  
**回退方式**：文档与测试先行，不改运行时行为。

### Phase 1：Program manifest 与 guarded integrate contract

**目标**：把 manifest schema、blocked_by、guarded execute 条件与 report 输出定成正式合同。  
**产物**：`program.py`、`program_service.py`、`program_cmd.py` 增量。  
**验证方式**：program unit + integration tests。  
**回退方式**：dry-run 与 execute gate 分开提交。

### Phase 2：Telemetry bounded status / doctor / stage / scan 边界收敛

**目标**：明确只读 operator 与 mutating command 的边界，避免 read-only surface 产生副作用，并把 manual telemetry 写入统一收敛到 canonical writer。  
**产物**：`telemetry/readiness.py`、`doctor_cmd.py`、`stage_cmd.py`、`commands.py`、`telemetry_cmd.py` 增量与 integration tests。  
**验证方式**：doctor / stage / status-json / telemetry integration tests。  
**回退方式**：先收敛 bounded read，再处理输出说明。

### Phase 3：IDE adapter / project-config contract

**目标**：锁定 IDE detection、适配器输出位置、`project-config.yaml` 默认回退与重建路径。  
**产物**：`integrations/ide_adapter.py`、`models/project.py`、相关 tests。  
**验证方式**：unit + integration。  
**回退方式**：保持当前默认模型 fallback 可用。

### Phase 4：Offline distribution contract

**目标**：把离线 bundle 的构建、安装入口、平台限制与 operator 文档边界锁定。  
**产物**：`packaging/offline/*` 与配套说明。  
**验证方式**：脚本 smoke / README contract review。  
**回退方式**：文档与脚本分开提交。

## 工作流计划

### 工作流 A：Program orchestration

**范围**：manifest validate -> status -> plan -> guarded integrate  
**影响范围**：`models/program.py`、`core/program_service.py`、`cli/program_cmd.py`  
**验证方式**：`tests/unit/test_program_service.py` + `tests/integration/test_cli_program.py`  
**回退方式**：dry-run 路径与 execute guards 分离

### 工作流 B：Read-only operator surfaces

**范围**：bounded `status --json` / `doctor` / `stage show|status` / `scan` + manual `telemetry record-*` commands  
**影响范围**：`telemetry/readiness.py`、`cli/telemetry_cmd.py`、其他 CLI commands、integration tests  
**验证方式**：证明 read-only 不改 project state / adapter files / telemetry store；manual telemetry 写入不绕过 canonical writer  
**回退方式**：先 bounded read，再调输出

### 工作流 C：IDE + offline distribution

**范围**：IDE adapter apply contract、`project-config` fallback、offline build/install constraints  
**影响范围**：`integrations/ide_adapter.py`、`models/project.py`、`packaging/offline/*`  
**验证方式**：integration adapter tests + shell smoke  
**回退方式**：IDE 与 offline 分批

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| program validate/status/plan/integrate 契约 | `tests/integration/test_cli_program.py` | `tests/unit/test_program_service.py` |
| doctor / bounded status 保持只读 | `tests/integration/test_cli_doctor.py` | `tests/integration/test_cli_status.py` |
| manual telemetry canonical writer path | `tests/integration/test_cli_telemetry.py` | telemetry store/index assertions |
| stage surfaces 与 full runner 分离 | `tests/integration/test_cli_stage.py` | CLI help / docs 对账 |
| IDE adapter / project-config 默认回退 | `tests/unit/test_ide_adapter.py` | `tests/integration/test_cli_ide_adapter.py` |
| offline bundle 平台边界 | shell smoke + README contract | packaging script review |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `scan` 是否拆出独立 CLI 文件还是继续留在 `commands.py` | 待锁定 | Phase 2 |
| offline bundle smoke 放在 pytest 外还是 Make/script 验证 | 待锁定 | Phase 4 |

## 实施顺序建议

1. 先 formalize Program 与 read-only operator surfaces。
2. 再处理 IDE adapter / `project-config`。
3. 最后锁离线分发，因为它更多是交付契约和脚本边界，而不是主链运行态。
