# 001 Spec 实现偏差总表

**工作项**：`001-ai-sdlc-framework`  
**日期**：2026-03-27  
**目的**：把 `spec.md` 与当前实现之间的合同偏差收敛为单一真值表，作为后续 remediation 的执行与回填依据。

## 口径

- 只登记 **相对 `spec.md` 仍存在偏差** 的 FR；未列出的 FR 视为当前已基本对齐或仅存在非合同级增量扩展。
- `偏差类型` 采用：
  - `接口漂移`：命令/函数名、参数或对外形态与 spec 不一致
  - `语义替换`：实现落成了另一种能力，不等于 spec 原合同
  - `部分实现`：已有局部能力，但缺编排、持久化、统一拦截或端到端闭环
  - `文档漂移`：实现存在，但 plan/tasks/docs 对外表述未同步
- `修复批次` 以 [`tasks.md`](tasks.md) 新增的 Batch 11 / Batch 12 为准；每批结束后必须同步回填本表状态、traceability 与 backlog。

## 偏差矩阵

| FR | spec 合同摘要 | 当前实现 / 证据 | 偏差类型 | 修复批次 | 当前状态 |
|----|---------------|-----------------|----------|----------|----------|
| FR-010~012 | `PrdStudio.review(prd_content)` 完成 7 项检查并输出结构化摘要 | [`src/ai_sdlc/studios/prd_studio.py`](../../src/ai_sdlc/studios/prd_studio.py) 现已提供 `PrdStudio.review(prd_content)` 与 `review_path()`；兼容保留 `check_prd_readiness(prd_path)`；通过就绪检查后输出 `structured_output`（项目名、目标、角色、功能、验收标准），见 [`tests/unit/test_prd_studio.py`](../../tests/unit/test_prd_studio.py) | 接口漂移, 部分实现 | Batch 12 | closed |
| FR-020~023 | `GovernanceGuard.check()` 检查 6 项治理前置条件；`freeze()` 写入 `governance.yaml` | [`src/ai_sdlc/gates/governance_guard.py`](../../src/ai_sdlc/gates/governance_guard.py) 现已提供 `GovernanceGuard.check()` / `freeze()`：按 6 项治理前置条件校验，并写入 `.ai-sdlc/work-items/<WI>/governance.yaml`；对应 contract tests 见 [`tests/unit/test_governance_guard.py`](../../tests/unit/test_governance_guard.py) | 语义替换, 部分实现 | Batch 11 | closed |
| FR-030 | docs 分支名应为 `feature/<work-item-id>-docs` | [`src/ai_sdlc/branch/branch_manager.py`](../../src/ai_sdlc/branch/branch_manager.py) 现已以 `feature/<WI>-docs` 为主名称；`switch_to_docs()` 保留 `design/<WI>-docs` legacy fallback，见 [`tests/unit/test_branch_manager.py`](../../tests/unit/test_branch_manager.py) | 接口漂移 | Batch 12 | closed |
| FR-033 | `baseline_recheck()` 应确认 docs 产物完整可访问 | [`src/ai_sdlc/branch/branch_manager.py`](../../src/ai_sdlc/branch/branch_manager.py) 的 `check_baseline()` 现已覆盖 `spec.md`、`plan.md`、`tasks.md`；`switch_to_dev()` 失败信息同步更新，见 [`tests/unit/test_branch_manager.py`](../../tests/unit/test_branch_manager.py) | 部分实现 | Batch 12 | closed |
| FR-034 | dev 分支必须拦截对 `spec.md` / `plan.md` 的写操作 | [`src/ai_sdlc/branch/file_guard.py`](../../src/ai_sdlc/branch/file_guard.py) 现已安装进程级守卫，统一拦截对受保护文档的 `Path.write_text()` / `Path.write_bytes()` / `open(..., write mode)` / `Path.replace()` / `Path.rename()`；[`src/ai_sdlc/generators/template_gen.py`](../../src/ai_sdlc/generators/template_gen.py) 继续走 guard-aware 写入口。对应 contract tests 见 [`tests/unit/test_file_guard.py`](../../tests/unit/test_file_guard.py) 与 [`tests/unit/test_branch_manager.py`](../../tests/unit/test_branch_manager.py) | 部分实现 | Batch 11 | closed |
| FR-040~045 | `Executor.run(tasks_file)` 按批次执行任务、写日志、commit、熔断、生成收尾产物 | [`src/ai_sdlc/core/executor.py`](../../src/ai_sdlc/core/executor.py) 现已提供 `Executor.run(tasks_file)`；[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py) 会在 execute 阶段真实驱动批次执行、写 `task-execution-log.md`、按 `pipeline.yml` 切批与熔断、执行 per-batch commit，并在 CLOSE 前生成 `development-summary.md`；对应 contract tests 见 [`tests/unit/test_executor.py`](../../tests/unit/test_executor.py)、[`tests/integration/test_cli_run.py`](../../tests/integration/test_cli_run.py) | 部分实现 | Batch 11 | closed |
| FR-052, FR-054 | `ContextManager.load_resume_pack()` 加载恢复包；`checkpoint.yml` 加载做合法性校验 | [`src/ai_sdlc/context/state.py`](../../src/ai_sdlc/context/state.py) 现已提供 `load_resume_pack()`、`ResumePackNotFoundError` / `ResumePackError` / `CheckpointLoadError`，并在 strict 模式校验 `checkpoint.yml` 的 YAML、`current_stage` 与 `spec_dir`；[`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py) 的 `recover` 已改为“加载恢复包”为主路径，reconcile 只做兼容性补写；对应 contract tests 见 [`tests/unit/test_context_state.py`](../../tests/unit/test_context_state.py)、[`tests/integration/test_cli_recover.py`](../../tests/integration/test_cli_recover.py) | 语义替换, 部分实现 | Batch 11 | closed |
| FR-061~063 | INIT / REFINE / EXECUTE Gate 应按 spec 执行完整门禁合同 | [`src/ai_sdlc/gates/pipeline_gates.py`](../../src/ai_sdlc/gates/pipeline_gates.py) 现已补齐 INIT 的 constitution / tech-stack / decisions / principles / source attribution，REFINE 的 user story 场景校验，以及 EXECUTE 的 build check；[`src/ai_sdlc/cli/sub_apps.py`](../../src/ai_sdlc/cli/sub_apps.py) 也改为从 checkpoint / execute_progress 构造真实 gate context，见 [`tests/unit/test_gates.py`](../../tests/unit/test_gates.py) | 语义替换, 部分实现 | Batch 12 | closed |
| FR-073, FR-083 | `ai-sdlc index` 应重建 `repo-facts.json`、`key-files.json` 等自动索引 | [`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py) 的 `index_command()` 现已执行 full scan，重建 `repo-facts.json` 与 extended indexes（至少含 `key-files.json`），见 [`tests/integration/test_cli_index_gate.py`](../../tests/integration/test_cli_index_gate.py) | 部分实现 | Batch 12 | closed |
| FR-074 | CLI 形态应为 `ai-sdlc gate <stage>` | [`src/ai_sdlc/cli/sub_apps.py`](../../src/ai_sdlc/cli/sub_apps.py) 现已显式注册 `gate init/refine/design/decompose/verify/execute/close` aliases，同时保留 `gate check <stage>` 兼容形态，见 [`tests/integration/test_cli_index_gate.py`](../../tests/integration/test_cli_index_gate.py) | 接口漂移 | Batch 12 | closed |
| FR-081 | 状态机所有转换必须持久化到 `work-item.yaml.status` | [`src/ai_sdlc/core/state_machine.py`](../../src/ai_sdlc/core/state_machine.py) 现已提供 `save_work_item()` / `load_work_item()` / `transition_work_item()`，把合法状态转换写回 `.ai-sdlc/work-items/<WI>/work-item.yaml`；非法转换不落盘，文件系统夹具覆盖跨阶段链条，见 [`tests/unit/test_state_machine.py`](../../tests/unit/test_state_machine.py) 与 [`tests/flow/test_new_requirement_flow.py`](../../tests/flow/test_new_requirement_flow.py) | 部分实现 | Batch 11 | closed |

## 执行规则

1. Batch 11 只修核心闭环：`FR-020~023`、`FR-034`、`FR-040~045`、`FR-052/054`、`FR-081`（并顺带消除 `recover` surface 的相关漂移）。
2. Batch 12 再清理接口形态漂移和剩余语义缩减：`FR-010~012`、`FR-030`、`FR-033`、`FR-061~063`、`FR-073/083`、`FR-074`。
3. 每批结束后必须同时完成：
   - contract-level 测试
   - 本表状态回填
   - FR traceability 更新
   - [`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 对应条目更新
