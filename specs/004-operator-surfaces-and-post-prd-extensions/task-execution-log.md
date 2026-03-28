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

- **已完成 git 提交**：否
- **提交哈希**：`N/A`
- **是否继续下一批**：阻断，待本批代码与归档一并提交后再决定后续 work item。
