---
related_plan: docs/FRAMEWORK_ROADMAP.zh-CN.md
---

# 任务分解：普通用户单入口收敛

**编号**：`220-ordinary-user-single-entry-convergence` | **日期**：2026-08-29
**来源**：`spec.md` + `plan.md`
**阶段**：P2A characterization/RED

## Batch 0：Formal freeze

### Task 0.1 冻结远端主线证据与最小合同

- task_id: T01
- status: done
- goal: 冻结主线/参赛版远端基线、run/status/help 真实行为、ROI 切片、兼容矩阵和停止条件。
- depends: none
- scope:
  - specs/220-ordinary-user-single-entry-convergence/spec.md
  - specs/220-ordinary-user-single-entry-convergence/plan.md
  - specs/220-ordinary-user-single-entry-convergence/tasks.md
  - specs/220-ordinary-user-single-entry-convergence/task-execution-log.md
- acceptance:
  - Formal 明确不复制参赛版、不替换 Runner、不实现五 Loop predecessor router。
  - P2A/P2B、4–6 人日预算、单一投影、两轮整改与降级条件可执行。
  - 默认 help、高级兼容、run/status/JSON/exit 矩阵无歧义。
- verify:
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program validate
  - git diff --check

### Task 0.2 Formal exact-head 独立评审

- task_id: T02
- status: done
- goal: 对同一 base/head 审核用户价值、真假边界、兼容遗漏和实现膨胀风险。
- depends:
  - T01
- scope:
  - specs/220-ordinary-user-single-entry-convergence/
- acceptance:
  - 无未关闭 Critical/Important；同类整改最多两轮。
  - 评审不得把 P4、P3、Program Truth 历史债务或参赛版代码迁移塞入 P2。
- verify:
  - exact-head read-only review against origin/main

### Task 0.3 用户批准生产实现

- task_id: T03
- status: done
- goal: 用户审阅 Formal 结论并明确批准或整改；批准前不进入 src/tests。
- depends:
  - T02
- scope:
  - specs/220-ordinary-user-single-entry-convergence/
- acceptance:
  - 用户明确回复批准生产实现，或给出需回写 Formal 的整改意见。
  - 等待批准期间 T11–T43 全部保持 blocked；批准后只将 T03 置为 done、T11 置为 todo。
- notes:
  - 当前 workitem guard 只选择首个 todo/doing，不解释 depends；后续任务必须在前项完成和 ROI 门禁通过后逐项激活，
    不得预先把未来生产任务批量置为 todo。
- verify:
  - 用户决策记录
  - uv run ai-sdlc workitem guard --wi specs/220-ordinary-user-single-entry-convergence --request "进入生产实现" --json

## Batch 1：P2A characterization / RED

### Task 1.1 冻结既有行为与五项摘要 RED

- task_id: T11
- status: done
- goal: 先证明主线缺少默认摘要/details，再锁定所有既有 exit/JSON/上报行为。
- depends:
  - T03
- scope:
  - tests/unit/test_default_summary.py
  - tests/integration/test_cli_run.py
  - tests/integration/test_cli_status.py
- acceptance:
  - normal/open/preflight/halt 的新摘要断言先因缺功能失败。
  - single/multiple/malformed/no-loop、rules 上限、status default/details/json 均有 RED/characterization。
  - RED 不通过改 production expectation、删旧断言或伪造 subprocess。
- verify:
  - uv run pytest tests/unit/test_default_summary.py tests/integration/test_cli_run.py tests/integration/test_cli_status.py -q

## Batch 2：P2A minimal GREEN

### Task 2.1 实现单一默认展示投影

- task_id: T21
- status: done
- goal: 以一个内部纯投影统一 current loop/result/next/blockers/rules 的优先级与有界输出。
- depends:
  - T11
- scope:
  - src/ai_sdlc/cli/default_summary.py
  - src/ai_sdlc/cli/beginner_guidance.py
  - tests/unit/test_default_summary.py
- acceptance:
  - `default_summary.py` 与 `beginner_guidance.py` 二选一承载投影，不形成双实现。
  - 无持久化/public schema/config/router；Current Loop 遵守 single/ambiguous/fallback 合同。
  - Next ≤1、Blockers ≤3、Applicable Rules ≤2。
- verify:
  - uv run pytest tests/unit/test_default_summary.py -q
  - uv run ruff check src/ai_sdlc/cli tests/unit/test_default_summary.py

### Task 2.2 接入 run 五项摘要

- task_id: T22
- status: done
- goal: 在不改变执行和上报语义的前提下覆盖 run 全部终态。
- depends:
  - T21
- scope:
  - src/ai_sdlc/cli/default_summary.py
  - src/ai_sdlc/cli/run_cmd.py
  - tests/integration/test_cli_run.py
- acceptance:
  - normal/open/preflight/halt 均呈现真实摘要；原 stage/frontend/AgentOps 行为和 exit code 不变。
  - 不全面拆分 `run_cmd.py`，不引入 `--json` 或新的执行选项。
- verify:
  - uv run pytest tests/integration/test_cli_run.py tests/unit/test_run_cmd.py -q

### Task 2.3 收敛 status default 并保留 details/json

- task_id: T23
- status: todo
- goal: 默认只显示四项摘要，新增 details 迁移桥，JSON 早返回合同不变。
- depends:
  - T21
- scope:
  - src/ai_sdlc/cli/commands.py
  - tests/integration/test_cli_status.py
- acceptance:
  - default 不再输出完整诊断表；`--details` 保留旧关键行。
  - `--json` shape/值语义/exit/无写入不变；`--json --details` exit 2。
  - initialized default/details 遇业务 blocker 仍 exit 0。
- verify:
  - uv run pytest tests/integration/test_cli_status.py tests/unit/test_cli_commands.py -q

### Task 2.4 P2A adversarial ROI gate

- task_id: T24
- status: blocked
- goal: 以新鲜 diff、测试和独立评审决定进入 P2B、降级或 No-Go。
- depends:
  - T22
  - T23
- scope:
  - src/ai_sdlc/cli/default_summary.py
  - src/ai_sdlc/cli/beginner_guidance.py
  - src/ai_sdlc/cli/run_cmd.py
  - src/ai_sdlc/cli/commands.py
  - tests/unit/test_default_summary.py
  - tests/integration/test_cli_run.py
  - tests/integration/test_cli_status.py
- acceptance:
  - 预计/实际 P2A ≤3 人日、单一投影 ≤180 行、无越界状态/API/schema。
  - 不满足时只保留 run 五项摘要/status details，暂停 P2B 并回写裁决。
- verify:
  - focused pytest + ruff + constraints + exact-head review

## Batch 3：P2B default help convergence（条件）

### Task 3.1 help visibility 与高级可达性 RED

- task_id: T31
- status: blocked
- goal: 锁定六个默认入口和全部隐藏命令的直接调用兼容。
- depends:
  - T24
- scope:
  - tests/unit/test_command_names.py
  - tests/integration/test_cli_beginner_ux.py
  - tests/integration/test_cli_module_invocation.py
- acceptance:
  - `ai-sdlc --help` 与 `python -m ai_sdlc --help` 可见集合都精确为 init/adopt/run/status/recover/self-update。
  - 18 个命令组与 doctor/index/scan/refresh 的 command discovery 和代表性 `--help` 仍通过。
- verify:
  - uv run pytest tests/unit/test_command_names.py tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_module_invocation.py -q

### Task 3.2 最小 hidden 元数据与高级索引 GREEN

- task_id: T32
- status: blocked
- goal: 不移动实现，只收敛默认 help 并提供 README 高级命令索引。
- depends:
  - T31
- scope:
  - src/ai_sdlc/cli/main.py
  - src/ai_sdlc/__main__.py
  - README.md
  - tests/unit/test_command_names.py
  - tests/integration/test_cli_beginner_ux.py
  - tests/integration/test_cli_module_invocation.py
- acceptance:
  - 只改 Typer hidden/help 元数据、module ASCII fallback 和文档；不新增 advanced 命令、注册表或配置。
  - 直接 argv、参数解析和 exit contract 不变。
- verify:
  - uv run pytest tests/unit/test_command_names.py tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_module_invocation.py -q

## Batch 4：一致性、全量验证与主线交付

### Task 4.1 有界 guidance 对账

- task_id: T41
- status: blocked
- goal: 只修正与 init/run/status 新合同直接冲突的用户/adapter 文案。
- depends:
  - T24
- scope:
  - AGENTS.md
  - src/ai_sdlc/templates/AGENTS.md.j2
  - src/ai_sdlc/templates/adapters/
  - docs/
- acceptance:
  - P2B Go 时，必须先完成 T31/T32；P2B 暂停时，以 T24 的 ROI/降级决策作为该分支的前置证据。
  - `rg` 证明确有漂移的文件才修改；不做全库措辞优化。
  - 规范正文、可选建议、已经落地继续分离。
- verify:
  - bounded documentation assertions + git diff review

### Task 4.2 新用户、高级兼容与全量验证

- task_id: T42
- status: blocked
- goal: 证明单入口收益和存量兼容同时成立。
- depends:
  - T41
- scope:
  - src/ai_sdlc/cli/
  - tests/
  - README.md
  - AGENTS.md
  - src/ai_sdlc/templates/
  - docs/
  - specs/220-ordinary-user-single-entry-convergence/
- acceptance:
  - clean init→run、status modes、advanced commands、full pytest、Ruff、constraints、manifest 全部通过。
  - Windows/macOS/Linux required checks 通过；工作树无运行副作用。
- verify:
  - uv run pytest -q
  - uv run ruff check .
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc program validate
  - uv run pytest tests/integration/test_repo_program_manifest.py -q
  - git diff --check

### Task 4.3 exact-head review、PR 与合并后真值

- task_id: T43
- status: blocked
- goal: 完成独立 review、Codex PR review、required checks、merge 和远端主线核验。
- depends:
  - T42
- scope:
  - specs/220-ordinary-user-single-entry-convergence/
  - .ai-sdlc/state/
  - .ai-sdlc/work-items/220-ordinary-user-single-entry-convergence/
  - program-manifest.yaml
- acceptance:
  - 无未关闭 Critical/Important；同类整改不超过两轮。
  - PR heartbeat 持续到 merged 或 user blocker；合并后核对 exact origin/main。
- verify:
  - local exact-head review + GitHub required checks + post-merge truth
