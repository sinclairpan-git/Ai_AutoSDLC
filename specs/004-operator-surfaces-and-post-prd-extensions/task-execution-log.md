# 004-operator-surfaces-and-post-prd-extensions 任务执行归档

> 本文件遵循 [`templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/004-operator-surfaces-and-post-prd-extensions/` 相关的实现任务，在本文件**末尾**追加新批次章节。
- 批次结束顺序：验证（pytest + ruff + 必要只读校验）→ 归档本文 → git commit。

## 2. 批次记录

### Batch 2026-03-28-001 | 004 Batch 6 Task 6.1-6.2（latest/readiness freshness）

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `6.1`、Task `6.2`；[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-27-013`
- **目标**：把 `status/readiness` 的 latest/current 新鲜度真值从 `mtime` 猜测收敛到 canonical index / cursor 或其只读派生结果，并完成 `004` 第二波 backlog 对账收口。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、`src/ai_sdlc/telemetry/readiness.py`、`src/ai_sdlc/telemetry/store.py`
- **激活的规则**：TDD；fresh verification；bounded/read-only operator surface；台账单一真值。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **R1（status freshness 红灯）**
  - 命令：`uv run pytest tests/integration/test_cli_status.py -q -k "latest_summary_falls_back_to_canonical_snapshots_without_indexes or fallback_latest_scope_ids_ignore_misleading_mtime"`
  - 结果：先红后绿；实现前可复现“删掉 indexes 后 latest summary 归零”与“伪造 `mtime` 会带偏 latest/current”。
- **V1（004 backlog remediation 验证集）**
  - 命令：`uv run pytest tests/unit/test_telemetry_store.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`
  - 结果：**50 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/telemetry/store.py tests/unit/test_telemetry_store.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 2.3 任务记录

##### Task 6.1 | latest/current/readiness canonical freshness（FD-2026-03-27-013）

- **改动范围**：`src/ai_sdlc/telemetry/store.py`、`src/ai_sdlc/telemetry/readiness.py`、`tests/unit/test_telemetry_store.py`、`tests/integration/test_cli_status.py`
- **改动内容**：
  - 新增 `TelemetryStore.derive_index_payloads()`，把 `rebuild_indexes()` 当前依赖的 canonical 派生逻辑抽成只读函数，供 read surface 在不写盘的情况下复用。
  - `readiness.py` 的 latest summary / current latest scope id 在 index 文件缺失或无效时，改为回退到内存派生索引，而不是目录 `mtime`、manifest key 顺序或其他非真值信号。
  - 保留 writer 侧“写后刷新 indexes”的现有机制，但把 read surface 的 fallback 真值与 writer/rebuild 使用的逻辑统一为同一份导出结果。
- **新增/调整的测试**：
  - integration：补“无 indexes 仍能看见 open violations / artifacts / timeline cursor”“伪造 `mtime` 不会带偏 latest/current”两类回归，并把旧的 manifest/mtime 猜测测试改成吃真实 cursor / trace timestamp。
  - unit：补 `derive_index_payloads()` 的 canonical latest truth 回归。
- **执行的命令**：见 R1 / V1 / Lint / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。latest/current/readiness 的 fallback 真值已不再依赖 `mtime` 猜测，fresh write 后的 operator surface 能在无手工 rebuild 时反映真实状态。

##### Task 6.2 | 004 Batch 6 backlog/document 收口

- **改动范围**：[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **改动内容**：
  - 创建 `004` 的正式 `task-execution-log.md`，补齐 Batch 6 的验证证据、代码审查与同步状态。
  - 将 `FD-2026-03-27-013` 在 backlog 与 `tasks.md` 中统一关闭，移出“下一波待修优先级”。
  - 保持 `spec.md` / `plan.md` / `tasks.md` 对 bounded operator surface 的“只读但新鲜”合同口径一致，不另开 mixed spec。
- **新增/调整的测试**：无新增运行时代码测试；收口依赖 V1 / 只读校验结果。
- **执行的命令**：见 V1 / Lint / 治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。`004` 的 backlog、任务和 execution evidence 已统一到同一 freshness 真值。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批没有把 `004` 扩成写路径重构，而是把 latest/current 的读取真值收敛回 canonical index / cursor 及其只读派生结果，符合 backlog 的“只读但新鲜”边界。
- **代码质量**：`derive_index_payloads()` 让 writer 的落盘索引和 read surface 的 fallback 复用同一套导出逻辑，减少 duplicated freshness semantics。
- **测试质量**：先用红灯证明 `mtime` 猜测和 latest summary 归零是真实缺口，再用 unit + integration 回归固定删索引 / 伪造 `mtime` / fresh write 三类场景。
- **结论**：无新的阻塞项；允许关闭 `FD-2026-03-27-013` 并结束 `004` Batch 6。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `6.1` / `6.2` 已补完成说明并统一 Batch 6 收口口径）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-27-013` 已关闭，顶部待修清单已清空）。
- `related_plan`（如存在）同步状态：`已对账`（`004` 的 plan/spec/tasks 对 bounded/read-only/freshness 合同无新增漂移）。

#### 2.6 自动决策记录（如有）

- AD-001：本轮只把 read surface 的 fallback 真值收紧到 canonical 派生索引，不同步把 writer 的 `rebuild_indexes()` 改成增量更新 → 理由：`FD-2026-03-27-013` 的核心是 correctness / truth-source 缺口，先收 correctness，再视需要另开性能优化批次更稳。

#### 2.7 批次结论

- `004` Batch 6 已完成 latest/current/readiness freshness 的 backlog remediation，`FD-2026-03-27-013` 不再属于待修项；当前 backlog 第一、第二波都已清空。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`a64d956`（`fix: derive fresh telemetry status indexes`）
- **是否继续下一批**：阻断，待本批代码与归档一并提交后再决定后续 work item。

### Batch 2026-03-30-001 | 004 Task 2.3（manual telemetry canonical writer commands）

#### 3.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `2.3`；[`spec.md`](spec.md) `FR-004-006`
- **目标**：补齐 manual telemetry CLI 的 `record-evaluation` / `record-violation`，让四类 manual records 都经 canonical writer + scope validation 路径写入。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../src/ai_sdlc/cli/telemetry_cmd.py`](../../src/ai_sdlc/cli/telemetry_cmd.py)、[`../../src/ai_sdlc/telemetry/contracts.py`](../../src/ai_sdlc/telemetry/contracts.py)、[`../../src/ai_sdlc/telemetry/runtime.py`](../../src/ai_sdlc/telemetry/runtime.py)、[`../../src/ai_sdlc/telemetry/writer.py`](../../src/ai_sdlc/telemetry/writer.py)
- **激活的规则**：TDD；canonical writer 单一路径；scope-chain validation；docs/tasks/plan traceability 同步
- **验证画像**：`code-change`

#### 3.2 统一验证命令

- **R1（FR-004-006 红灯）**
  - 命令：`uv run pytest tests/integration/test_cli_telemetry.py -k 'record_evaluation or record_violation' -q`
  - 结果：**2 failed**；实现前可稳定复现 `record-evaluation` / `record-violation` 缺失。
- **V1（manual telemetry integration）**
  - 命令：`uv run pytest tests/integration/test_cli_telemetry.py -q`
  - 结果：**19 passed**。
- **V2（004 operator targeted regression）**
  - 命令：`uv run pytest tests/unit/test_program_service.py tests/unit/test_ide_adapter.py tests/unit/test_project_config.py tests/unit/test_telemetry_store.py tests/integration/test_cli_program.py tests/integration/test_cli_doctor.py tests/integration/test_cli_stage.py tests/integration/test_cli_ide_adapter.py tests/integration/test_cli_status.py tests/integration/test_cli_telemetry.py -q`
  - 结果：**112 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/cli/telemetry_cmd.py tests/integration/test_cli_telemetry.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 3.3 任务记录

##### Task 2.3 | manual telemetry canonical writer commands

- **改动范围**：[`../../src/ai_sdlc/cli/telemetry_cmd.py`](../../src/ai_sdlc/cli/telemetry_cmd.py)、[`../../tests/integration/test_cli_telemetry.py`](../../tests/integration/test_cli_telemetry.py)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 在 `telemetry` CLI 中新增 `record-evaluation` 与 `record-violation`，直接复用现有 `Evaluation` / `Violation` contract、`RuntimeTelemetry.validate_manual_scope()` 与 `TelemetryWriter.write_evaluation()` / `write_violation()`。
  - 保持 `manual telemetry` 的写入路径与已有 `record-event` / `record-evidence` 一致，不引入旁路 store、手写 snapshot 或独立 index 更新逻辑。
  - 在 integration tests 中补 run-scope evaluation 与 step-scope violation 正向回归，验证 current snapshot 落点与 `open-violations` index 会跟随 canonical write 刷新。
  - 在 `004` 的 `plan.md` / `tasks.md` 中补回 `FR-004-006` 的正式映射，避免 spec 需求存在而任务/验证矩阵缺位。
  - 在用户手册中把 manual telemetry 示例补齐为四类对象，并明确 CLI 采用 `evaluation` 命名，不额外引入 `assessment` 别名。
- **新增/调整的测试**：
  - integration：新增 `record-evaluation`、`record-violation` 正向回归，并通过整套 telemetry CLI 回归确认旧命令未受影响。
  - 无新增 store/runtime 单测；依赖现有 canonical writer / scope validation 覆盖。
- **执行的命令**：见 R1 / V1 / V2 / Lint / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。`FR-004-006` 当前已不再存在“manual telemetry 只支持 event/evidence”的实现缺口。

#### 3.4 代码审查（摘要）

- **规格对齐**：本批只补 `FR-004-006` 缺口，没有扩写 telemetry schema 或引入第二套 writer 路径，符合 `004` 的 operator/formalization 边界。
- **代码质量**：CLI 层保持薄封装，状态与 parent-chain 校验继续由现有 contract/runtime/store 负责，没有把验证逻辑复制到命令层。
- **测试质量**：先用红灯证明命令缺失，再用 integration 回归锁定 run/step scope、snapshot 落盘和 open-violations index 刷新。
- **结论**：无新的阻塞项；允许把 `FR-004-006` 从“真实实现缺口”降为“已实现并可回归验证”。

#### 3.5 任务/计划同步状态

- `plan.md` 同步状态：`已同步`（Phase 2 / Workflow B / 关键路径验证矩阵已纳入 manual telemetry canonical writer surface）。
- `tasks.md` 同步状态：`已同步`（新增 Task `2.3` 并补完成说明）。
- `USER_GUIDE.zh-CN.md` 同步状态：`已同步`（manual telemetry 命令示例已扩成四类对象）。
- `004` 剩余开放项：`scan` operator/analysis 边界、offline smoke contract、Task Batch 1-5 历史 execution evidence 仍待继续补齐。

#### 3.6 自动决策记录（如有）

- AD-001：本轮 CLI 采用 `record-evaluation`，不新增 `record-assessment` 别名 → 理由：现有 contract / writer / report / report artifact 统一使用 `evaluation` 术语；此时引入 alias 会增加对外命名分叉而不增加能力。

#### 3.7 批次结论

- `FR-004-006` 已落地；`004` 仍未整体 close，但“manual telemetry commands 缺 assessment/violation”这一真实实现缺口已关闭。

#### 3.8 归档后动作

- **已完成 git 提交**：否（待本批代码与归档一并提交）
- **提交哈希**：待提交
- **是否继续下一批**：可继续，建议优先转入 `FR-004-009` / `FR-004-015` 的 operator boundary formalization。

### Batch 2026-03-30-002 | 004 Task 2.2（scan operator/analysis boundary formalization）

#### 4.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `2.2`；[`spec.md`](spec.md) `FR-004-009`、`FR-004-015`
- **目标**：把 `scan` 从“会隐式触发 adapter 写路径的 CLI”收敛成真正的 operator/analysis 命令，并补齐对外文档边界。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`../../src/ai_sdlc/integrations/ide_adapter.py`](../../src/ai_sdlc/integrations/ide_adapter.py)
- **激活的规则**：TDD；operator/analysis boundary clarity；IDE adapter 写路径隔离；docs/tasks 同步
- **验证画像**：`code-change`

#### 4.2 统一验证命令

- **R1（scan boundary 红灯）**
  - 命令：`uv run pytest tests/integration/test_cli_scan.py -q`
  - 结果：先红后绿；实现前 `initialized project` 下执行 `scan` 会触发 IDE adapter path，违背 analysis-only 边界。
- **V1（scan integration）**
  - 命令：`uv run pytest tests/integration/test_cli_scan.py -q`
  - 结果：**2 passed**。
- **V2（004 operator targeted regression）**
  - 命令：`uv run pytest tests/integration/test_cli_scan.py tests/integration/test_cli_stage.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_ide_adapter.py tests/integration/test_cli_telemetry.py tests/integration/test_cli_program.py tests/unit/test_program_service.py tests/unit/test_ide_adapter.py tests/unit/test_project_config.py tests/unit/test_telemetry_store.py -q`
  - 结果：**114 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/cli/main.py src/ai_sdlc/cli/commands.py tests/integration/test_cli_scan.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 4.3 任务记录

##### Task 2.2 | `scan` / `status --json` / `stage` 边界收口中的 scan formalization

- **改动范围**：[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`../../tests/integration/test_cli_scan.py`](../../tests/integration/test_cli_scan.py)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 在 CLI 全局 hook 中把 `scan` 归入不触发 IDE adapter 的 surface，避免进入隐式写路径。
  - 删除 `scan_command()` 内部的 `ensure_ide_adaptation(root)` 调用，保持 deep scan 只做读取与终端输出。
  - 新增 `test_cli_scan.py`，锁定两类契约：未初始化路径可直接扫描；已初始化项目下 `scan` 不得调用 adapter apply path。
  - 在用户手册中把 `scan` 明确标成 operator/analysis 命令，并写明它不会替代 `run` / `stage run`，也不会隐式初始化 `.ai-sdlc/` 或触发 adapter 写入。
- **新增/调整的测试**：
  - integration：新增 `scan` CLI 契约测试。
  - 通过 004 operator targeted regression 复核 `status` / `doctor` / `stage` / `telemetry` / `program` surface 未被带偏。
- **执行的命令**：见 R1 / V1 / V2 / Lint / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。`scan` 现已是正式的 operator/analysis surface，不再携带 IDE adapter 写副作用。

#### 4.4 代码审查（摘要）

- **规格对齐**：本批直接针对 `FR-004-009` 的“operator/analysis 命令”要求收口，没有把 `scan` 变成写路径 bootstrap surface。
- **代码质量**：通过同时收敛 main callback 与命令体内的本地调用，消除了双重 adapter apply 入口。
- **测试质量**：新的 integration test 不是只看输出，而是直接把 adapter path patch 成 forbidden，从而锁死了“不得写”的边界。
- **结论**：无新的阻塞项；`scan` 的 operator/analysis 合同已可通过自动化回归验证。

#### 4.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `2.2` 已补完成说明）。
- `USER_GUIDE.zh-CN.md` 同步状态：`已同步`（`scan` operator/analysis 边界已写明）。
- `004` 剩余开放项：offline smoke contract、Batch 1-5 历史 execution evidence、以及 `FR-004-015` 更完整的 operator mutation matrix 仍待继续补齐。

#### 4.6 自动决策记录（如有）

- AD-001：`scan` 直接定义为 analysis-only，而不是“允许 adapter idempotent 写入的半只读命令” → 理由：spec 已把 `scan` 与 `doctor/status` 并列为 operator surface；若保留隐式 adapter apply，则外部无法稳定判断其是否改仓库。

#### 4.7 批次结论

- `FR-004-009` 已从“文档口径不硬、真实行为有写副作用”收敛为自动化可验证的 operator/analysis contract；`FR-004-015` 仍剩更完整的 mutation/read-only matrix 需要后续补齐。

#### 4.8 归档后动作

- **已完成 git 提交**：否（待本轮代码与归档统一提交）
- **提交哈希**：待提交
- **是否继续下一批**：可继续，建议转入 offline smoke contract 与 004 历史 batch traceability 补齐。

### Batch 2026-03-30-003 | 004 Task 4.1（offline bundle manifest + smoke contract）

#### 5.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `4.1`；[`spec.md`](spec.md) `FR-004-013`、`FR-004-014`
- **目标**：把 offline bundle 的适用平台边界从 README 提示提升为 bundle manifest + installer validation，并补齐无网络 smoke。
- **预读范围**：[`../../packaging/offline/build_offline_bundle.sh`](../../packaging/offline/build_offline_bundle.sh)、[`../../packaging/offline/install_offline.sh`](../../packaging/offline/install_offline.sh)、[`../../packaging/offline/install_offline.ps1`](../../packaging/offline/install_offline.ps1)、[`../../packaging/offline/README.md`](../../packaging/offline/README.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **激活的规则**：TDD；offline smoke 不依赖真实网络；bundle 平台边界显式化；docs/tasks/log 同步
- **验证画像**：`code-change`

#### 5.2 统一验证命令

- **R1（offline manifest / installer 红灯）**
  - 命令：`uv run pytest tests/integration/test_offline_bundle_scripts.py -q`
  - 结果：先红后绿；实现前 bundle 不生成 manifest，installer 也不会拒绝 manifest platform mismatch。
- **V1（offline packaging smoke）**
  - 命令：`uv run pytest tests/integration/test_offline_bundle_scripts.py -q`
  - 结果：**3 passed**。
- **Lint**
  - 命令：`uv run ruff check packaging/offline tests/integration/test_offline_bundle_scripts.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 5.3 任务记录

##### Task 4.1 | offline bundle manifest + installer platform validation

- **改动范围**：[`../../packaging/offline/build_offline_bundle.sh`](../../packaging/offline/build_offline_bundle.sh)、[`../../packaging/offline/install_offline.sh`](../../packaging/offline/install_offline.sh)、[`../../packaging/offline/install_offline.ps1`](../../packaging/offline/install_offline.ps1)、[`../../packaging/offline/README.md`](../../packaging/offline/README.md)、[`../../packaging/offline/README_BUNDLE.txt`](../../packaging/offline/README_BUNDLE.txt)、[`../../tests/integration/test_offline_bundle_scripts.py`](../../tests/integration/test_offline_bundle_scripts.py)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - `build_offline_bundle.sh` 现在会生成 `bundle-manifest.json`，记录 `bundle_format_version`、`package_version`、`platform_os`、`platform_machine`，并随 `.tar.gz` / `.zip` 一起打包。
  - `install_offline.sh` 在 manifest 存在时会用当前 Python 读取并校验平台；若 OS/CPU 不匹配则明确拒绝安装；旧 bundle 缺 manifest 时保留 warning 兼容路径。
  - `install_offline.ps1` 同步补了 manifest 平台校验，保持 Windows 安装入口的合同一致。
  - 新增 `test_offline_bundle_scripts.py`，使用 fake Python / fake uv wrappers 在无网络条件下做脚本 smoke，覆盖 build 产物、manifest 落盘、mismatch 拒绝、matching platform 安装成功。
  - `README.md` / `README_BUNDLE.txt` 已把 `bundle-manifest.json` 与安装期平台校验写成正式合同。
- **新增/调整的测试**：
  - integration：新增 offline packaging smoke test 3 条。
  - 当前自动化仅执行 Linux/macOS shell installer；PowerShell 路径已更新，但本轮未在真实 Windows 环境执行。
- **执行的命令**：见 R1 / V1 / Lint。
- **测试结果**：通过。
- **是否符合任务目标**：符合。offline bundle 的平台限制不再只是文档建议，而是有 manifest 和 installer enforcement 的正式 contract。

#### 5.4 代码审查（摘要）

- **规格对齐**：本批直接把 `FR-004-013/014` 的“构建产物、安装入口、适用平台”做成 bundle 事实，而不是停留在 README 提醒。
- **代码质量**：offline smoke 通过 fake wrappers 隔离真实网络与真实 wheel 安装，能稳定覆盖脚本控制流而不污染工作区。
- **测试质量**：红灯先证明“manifest 缺失 / mismatch 未被拒绝”是实际缺口，绿灯后固定 build/install 两侧 contract。
- **结论**：无新的阻塞项；offline bundle contract 已进入可自动回归状态。

#### 5.5 任务/计划同步状态

- `plan.md` 同步状态：`已同步`（Phase 4 验证方式与开放问题已更新）。
- `tasks.md` 同步状态：`已同步`（Task `4.1` 已补完成说明）。
- `packaging/offline/README.md` 同步状态：`已同步`（bundle-manifest 与 installer 校验合同已写明）。
- `004` 剩余开放项：Batch 1-5 历史 execution evidence、以及更完整的 operator mutation/read-only matrix 仍待继续补齐。

#### 5.6 自动决策记录（如有）

- AD-001：旧 offline bundle 缺 `bundle-manifest.json` 时只 warning 不强制失败 → 理由：给历史产物保留兼容路径，同时让新 bundle 从现在开始具备强校验合同。

#### 5.7 批次结论

- `FR-004-013/014` 的平台边界已从文档建议升级为自动化可验证的 bundle/install contract；`004` 还未整体 close，但 offline distribution 不再缺 formal smoke。

#### 5.8 归档后动作

- **已完成 git 提交**：否（待本轮代码与归档统一提交）
- **提交哈希**：待提交
- **是否继续下一批**：可继续，建议转入 `004` Batch 1-5 历史 execution evidence 与 `FR-004-015` 的完整 mutation matrix。

### Batch 2026-03-30-004 | 004 Task 5.2（operator mutation/read-only matrix docs）

#### 6.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `5.2`；[`spec.md`](spec.md) `FR-004-015`
- **目标**：把 `004` 范围内 operator / offline surfaces 的只读、analysis、写路径边界写成用户可查的矩阵，并显式说明 IDE adapter hook 的副作用层。
- **预读范围**：[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`../../src/ai_sdlc/cli/stage_cmd.py`](../../src/ai_sdlc/cli/stage_cmd.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../src/ai_sdlc/cli/telemetry_cmd.py`](../../src/ai_sdlc/cli/telemetry_cmd.py)
- **激活的规则**：现状优先；文档必须表达真实 CLI 行为而不是理想行为；adapter hook 影响单独披露
- **验证画像**：`docs-only`

#### 6.2 统一验证命令

- **V1（operator matrix evidence set）**
  - 命令：`uv run pytest tests/integration/test_cli_stage.py tests/integration/test_cli_program.py tests/integration/test_cli_scan.py tests/integration/test_cli_telemetry.py -q`
  - 结果：**35 passed**。
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 6.3 任务记录

##### Task 5.2 | operator mutation/read-only matrix 文档收口

- **改动范围**：[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 新增 `Operator surface 读写矩阵`，覆盖 `status --json`、`doctor`、`scan`、`stage show/status/run`、`program validate/status/plan/integrate`、manual telemetry、offline build/install。
  - 把“命令主体行为”和“CLI 全局 IDE adapter hook 可能带来的幂等写入”拆开表述，避免把 `stage` / `program` 这类命令误记成绝对只读。
  - 保持 `scan`、`status --json`、`doctor` 的无 adapter/write 边界，与前面已落地的 `FR-004-005` / `FR-004-009` 收口一致。
- **新增/调整的测试**：无新增自动化；依赖现有 integration tests 作为行为证据。
- **是否符合任务目标**：符合。`FR-004-015` 的“哪些只读、哪些会改状态”现在已有统一文档矩阵可查。

#### 6.4 代码审查（摘要）

- **规格对齐**：文档矩阵只覆盖 `004` 范围内 surfaces，没有扩写到无关 CLI。
- **质量判断**：用“主定位 + 状态影响”两层描述，比简单写成只读/非只读更接近真实行为，特别适合解释 adapter hook 这类幂等副作用。
- **结论**：允许把 `FR-004-015` 从“口径不完整”收敛到“已有正式矩阵”，剩余问题主要转向历史 execution evidence 而非行为边界缺失。

#### 6.5 归档后动作

- **已完成 git 提交**：否（待本轮代码与归档统一提交）
- **提交哈希**：待提交
- **是否继续下一批**：可继续，建议最后集中补 `004` Batch 1-5 历史 execution evidence。
