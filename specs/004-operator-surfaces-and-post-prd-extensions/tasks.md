# 任务分解：AI-SDLC 原 PRD 外新增能力与 Operator Surfaces

**编号**：`004-operator-surfaces-and-post-prd-extensions` | **日期**：2026-03-28  
**来源**：plan.md + spec.md（RG-020 ~ RG-023 / FR-004-001 ~ FR-004-015）

---

## 分批策略

```text
Batch 1: Program manifest contracts
Batch 2: Telemetry bounded status / doctor / stage / scan surfaces
Batch 3: IDE adapter / project-config contracts
Batch 4: Offline distribution contracts
Batch 5: Final traceability and operator regression
Batch 6: backlog remediation for latest/readiness freshness
```

---

## Batch 1：Program manifest contracts

### Task 1.1 — 锁定 program-manifest schema、blocked_by 与 topo/integration 计划合同

- **优先级**：P1
- **依赖**：无
- **输入**：[`src/ai_sdlc/models/program.py`](../../src/ai_sdlc/models/program.py)、[`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)
- **验收标准**：
  1. path / dep / cycle / blocked_by 行为与 spec 对齐。
  2. integration dry-run / execute gate 条件明确。
- **验证**：`uv run pytest tests/unit/test_program_service.py -v`

### Task 1.2 — 对齐 `program validate/status/plan/integrate` CLI 对外合同

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)
- **验收标准**：
  1. validate/status/plan/integrate 输出和 exit code 稳定。
  2. `--execute` 受 guarded gate 与显式确认保护。
- **验证**：`uv run pytest tests/integration/test_cli_program.py -v`

---

## Batch 2：Read-only operator surfaces

### Task 2.1 — 锁定 bounded telemetry status / doctor 的只读边界

- **优先级**：P1
- **依赖**：无
- **输入**：[`src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`src/ai_sdlc/cli/doctor_cmd.py`](../../src/ai_sdlc/cli/doctor_cmd.py)、[`tests/integration/test_cli_doctor.py`](../../tests/integration/test_cli_doctor.py)
- **验收标准**：
  1. doctor / bounded status 不触发深度初始化或无关写入。
  2. resolver/readiness probe 保持有界读取。
- **验证**：定向 integration tests

### Task 2.2 — 明确 `stage` / `scan` / `status --json` 与 full runner 的边界

- **优先级**：P1
- **依赖**：Task 2.1
- **输入**：[`src/ai_sdlc/cli/stage_cmd.py`](../../src/ai_sdlc/cli/stage_cmd.py)、[`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、相关 integration tests
- **验收标准**：
  1. `stage` surface 只表达阶段清单 / dry-run / status，不替代 full runner。
  2. `scan` / `status --json` 明确只读或 analysis 边界。
- **验证**：`uv run pytest tests/integration/test_cli_stage.py tests/integration/test_cli_status.py -v`

---

## Batch 3：IDE adapter / project-config

### Task 3.1 — 锁定 IDE detection、输出位置与幂等行为

- **优先级**：P1
- **依赖**：无
- **输入**：[`src/ai_sdlc/integrations/ide_adapter.py`](../../src/ai_sdlc/integrations/ide_adapter.py)、[`tests/unit/test_ide_adapter.py`](../../tests/unit/test_ide_adapter.py)、[`tests/integration/test_cli_ide_adapter.py`](../../tests/integration/test_cli_ide_adapter.py)
- **验收标准**：
  1. 各 IDE marker / env detection 稳定。
  2. adapter apply 不覆盖用户修改。
  3. read-only commands 不会意外触发 adapter 写入。
- **验证**：unit + integration tests

### Task 3.2 — 锁定 `project-config.yaml` 缺失时的默认回退与重建

- **优先级**：P1
- **依赖**：Task 3.1
- **输入**：[`src/ai_sdlc/models/project.py`](../../src/ai_sdlc/models/project.py)、`core/config`、相关 tests
- **验收标准**：
  1. 缺失本地配置时回落到默认模型，而不是报错。
  2. 运行时允许重建配置并保持幂等。
- **验证**：定向 unit/integration tests

---

## Batch 4：Offline distribution

### Task 4.1 — 锁定离线 bundle 构建产物、安装入口与平台限制

- **优先级**：P1
- **依赖**：无
- **输入**：[`packaging/offline/build_offline_bundle.sh`](../../packaging/offline/build_offline_bundle.sh)、[`packaging/offline/install_offline.sh`](../../packaging/offline/install_offline.sh)、[`packaging/offline/install_offline.ps1`](../../packaging/offline/install_offline.ps1)、[`packaging/offline/install_offline.bat`](../../packaging/offline/install_offline.bat)、[`packaging/offline/README.md`](../../packaging/offline/README.md)
- **验收标准**：
  1. 构建产物、安装入口、适用平台和限制条件写清楚。
  2. “同 OS/CPU 构建并安装”的边界被明确表达。
- **验证**：脚本 smoke + 文档复核

---

## Batch 5：Final traceability

### Task 5.1 — 004 traceability / operator regression / docs 对账收口

- **优先级**：P1
- **依赖**：Task 1.2, Task 2.2, Task 3.2, Task 4.1
- **验收标准**：
  1. `spec.md`、`plan.md`、`tasks.md` 三者对齐。
  2. program / doctor / stage / ide adapter 关键 integration tests 通过。
  3. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：定向 integration + 全量 `pytest` + `ruff`

---

## Batch 6：backlog remediation（latest/readiness freshness）

> **说明**：本批承接 `FD-2026-03-27-013`，把 bounded operator surface 的 latest/current 新鲜度问题挂回 `004` 正式任务，而不是继续留在临时 telemetry 设计上下文中。

### Task 6.1 — latest/current/readiness 跟随 canonical write 即时刷新（FD-2026-03-27-013）

- **优先级**：P1
- **依赖**：Task 5.1
- **输入**：[`src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`src/ai_sdlc/telemetry/store.py`](../../src/ai_sdlc/telemetry/store.py)、[`src/ai_sdlc/telemetry/writer.py`](../../src/ai_sdlc/telemetry/writer.py)、[`tests/integration/test_cli_status.py`](../../tests/integration/test_cli_status.py)、[`tests/integration/test_cli_doctor.py`](../../tests/integration/test_cli_doctor.py)、[`tests/unit/test_telemetry_store.py`](../../tests/unit/test_telemetry_store.py)
- **验收标准**：
  1. fresh event / violation / artifact 写入后，`status --json` 的 latest/current/open-violations summary 无需手工 rebuild 即可反映真实状态。
  2. latest/current 的 recency 信号来自随写入同步维护的 canonical index / cursor，而不是目录 `mtime`、dict 顺序或其他不稳定猜测。
  3. 在保持即时刷新的同时，`status --json` / `doctor` 仍维持 bounded、read-only、不 deep scan 的 operator 边界。
- **验证**：`uv run pytest tests/unit/test_telemetry_store.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -v`

### Task 6.2 — 004 第二波 backlog 对账收口

- **优先级**：P1
- **依赖**：Task 6.1
- **验收标准**：
  1. `FD-2026-03-27-013` 的 backlog、`tasks.md` 与 operator regression 证据使用同一套新鲜度口径。
  2. `spec.md` / `plan.md` / `tasks.md` 对 bounded status/doctor 的“只读但新鲜”合同保持一致。
  3. 本批收口不会重新引入“helper 已修、真实 CLI 仍旧陈旧”的双轨状态。
- **验证**：定向 integration + `verify constraints`
