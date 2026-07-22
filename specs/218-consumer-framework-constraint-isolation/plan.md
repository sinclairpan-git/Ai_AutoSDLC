# 消费项目与框架约束隔离 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`
> or `superpowers:executing-plans`. Steps use checkbox syntax in `tasks.md`.

**Goal:** 用一个私有双信号范围判定隔离 consumer 与 framework 约束，同时保持通用门禁和框架自验证。

**Architecture:** 不增加配置或身份模型；在现有 collect/report/context 三入口复用同一私有 helper，并以
显式 `if is_framework` 对现有 framework-owned 调用做机械分组。consumer 路径只投影实际执行的检查；
`SDLCRunner` 删除重复注入，`run` CLI summary 复用同一 scope guard，避免下游按内部 WI 编号重建结果。

**Tech Stack:** Python 3.11+、`tomllib`、`pathlib.Path`、pytest、Ruff、PowerShell、`uv run ai-sdlc`。

## Global Constraints

- Formal 与 implementation 分支分离；formal 归档并经 fresh-main 验收后才创建 implementation 分支。
- 产品精确只改 `src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/runner.py` 和
  `src/ai_sdlc/cli/run_cmd.py`，职责分别限定为 scope/canonical context 与回收行数、删除重复注入、复用
  `_repository_scope` 做 summary guard。
- 行为测试精确只扩展 `tests/unit/test_verify_constraints.py`、`tests/unit/test_runner_confirm.py`、
  `tests/unit/test_run_cmd.py`、`tests/integration/test_cli_run.py`；两个既有 integration 身份 fixture 例外保留。
- 三个产品文件合计 raw additions ≤80；新增私有 helper 目标 1 个且最多 2 个；不新增模块、配置、依赖或公开抽象。
- 不处理 telemetry，不更新 adapter template，不修改 Agent Store。
- 所有新测试先在未改产品的 implementation baseline 上取得预期 RED，再写最小 GREEN。
- framework 当前行为零未批准差异；consumer 通用门禁不减。

## File Map

| 文件 | 职责 |
|---|---|
| `specs/218-consumer-framework-constraint-isolation/spec.md` | PRD、范围、所有权与验收合同 |
| `specs/218-consumer-framework-constraint-isolation/plan.md` | 实施顺序与分支边界 |
| `specs/218-consumer-framework-constraint-isolation/tasks.md` | 可执行任务与 AC |
| `specs/218-consumer-framework-constraint-isolation/task-execution-log.md` | 证据、评审与验收账本 |
| `src/ai_sdlc/core/verify_constraints.py` | 私有 scope 判定、三入口机械分流、canonical context 防重建，并回收行数 |
| `src/ai_sdlc/core/runner.py` | 只删除 framework canonical warning 的重复注入 |
| `src/ai_sdlc/cli/run_cmd.py` | 只复用同一 `_repository_scope` 保护 `run` summary |
| `tests/unit/test_verify_constraints.py` | 身份矩阵、Agent Store、编号碰撞、canonical context 与门禁保留回归 |
| `tests/unit/test_runner_confirm.py` | consumer `014` runner negative 与 framework positive 回归 |
| `tests/unit/test_run_cmd.py` | consumer `014` summary guard 单元回归 |
| `tests/integration/test_cli_run.py` | consumer/framework `014` CLI summary 端到端回归 |
| `tests/integration/test_cli_verify_constraints.py` | 仅为明确验证 framework-only `003/012/018/073`、backlog/profile/doc-first surfaces 的既有 fixture 补 framework identity setup |
| `tests/integration/test_cli_index_gate.py` | 仅为明确验证 framework-only `018` surfaces 的既有 fixture 补 framework identity setup |
| `tests/integration/test_repo_program_manifest.py` | formal 新增 WI218 后的精确 inventory/close 计数 |

## Phase 1：Formal PRD 归档

1. 完成 canonical 四件套，移除 scaffold placeholder。
2. 对 PRD 运行 LEAN 与 SAFETY 两位独立 reviewer；交换意见后修订至同 identity PASS0。
3. 执行 formal-only constraints、program truth、manifest 和 diff scope 验证。
4. push formal branch、创建 PR、请求 Codex review，required checks 全绿后合并。
5. 在 detached fresh-main 对归档产物做 checksum、manifest、constraints 和 clean-tree 验收。

Formal PR 禁止修改 `src/**`、产品行为测试、workflow、依赖、版本或 release 表面；只允许 manifest exact
测试的机械计数随 WI218 四件套和 `stage: close-pending` summary 同步。该 summary 只保持 source inventory
完整；ProgramService status/execute gate 必须停在 `decompose_or_execute`，不得据此推断实施或关闭完成。

## Phase 2：TDD RED

从 formal merge 后的新 fresh-main 创建独立 implementation 分支。

测试先覆盖：

1. `both/neither/name-only/sentinel-only` 身份矩阵；
2. malformed/non-string pyproject × sentinel present/absent；
3. routing-census 参数化证明 common/framework helper 所有权；
4. Agent Store-shaped consumer fixture，并故意保留一个 common blocker；
5. consumer `003/012` 非空编号碰撞的 collect/report/context/release 投影；
6. consumer `014` 在 canonical context、`SDLCRunner` 与 `run` CLI summary 均不重建 framework
   attachment/warning，并以双身份信号 framework fixture 证明既有 `014` 行为保留；
7. 现有 PrimeVue consumer report/context 保留；
8. framework checkout 与既有 framework drift 测试保持。

在产品未改时，至少 Agent Store、consumer metadata/编号碰撞及 `014` 下游重建测试必须 RED；既有框架
测试保持 GREEN。verify constraints 新行为断言仍局限在 `test_verify_constraints.py`；`014` runner/summary
断言只写入 LC-02 精确允许的三个对应测试。上述两个 identity integration 例外文件只能在逐个明确的 framework fixture 内创建
`pyproject.toml`（`[project].name = "ai-sdlc"`）和 `src/ai_sdlc/__init__.py`；不得修改断言/预期输出，
不得使用 module/global autouse，且 downstream/relinked `003` 与 consumer `003/012` collision fixture 保持
无 framework identity。

## Phase 3：最小 GREEN

1. 新增 `_repository_scope(root) -> tuple[bool, str | None]` 或等价单一私有 helper。
2. `collect_constraint_blockers` 保持 common 无条件执行，把 framework-owned helper 放入一个显式条件块。
3. `build_constraint_report` 在 consumer 路径不构造内部 WI attachments，不投影 framework-only
   check objects、coverage 或 release surface。
4. `build_verification_gate_context` 使用同一判定，不重新加载或投影 framework-only attachment/context。
5. `SDLCRunner` 只删除重复 canonical warning 注入；`run_cmd.py` 只复用同一 `_repository_scope` 做 summary
   guard；`ProgramService` 通用路径不改。
6. 不建立 registry/dispatcher/role class；若三个产品文件合计 raw additions 超过 80，停止并压缩，不放宽合同。
7. 不增加“缺少双信号仍按 framework”之类的产品兼容 fallback；fixture 必须显式表达其仓库身份。

## Phase 4：验证与交付

按风险递增执行：

```powershell
uv run pytest -q tests/unit/test_verify_constraints.py tests/unit/test_runner_confirm.py tests/unit/test_run_cmd.py tests/integration/test_cli_run.py
uv run ruff check src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/core/runner.py src/ai_sdlc/cli/run_cmd.py tests/unit/test_verify_constraints.py tests/unit/test_runner_confirm.py tests/unit/test_run_cmd.py tests/integration/test_cli_run.py
uv run pytest -q
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
git diff --check
```

随后在不修改 Agent Store 的前提下执行真实 consumer 验收：

1. 从 implementation worktree 以 `uv run python -B` 启动，设置 `PYTHONDONTWRITEBYTECODE=1`，并把当前
   worktree 的 `src` 放入 `PYTHONPATH`；禁止调用会创建 telemetry/session 的 CLI。
2. 调用 `collect_constraint_blockers(Path('/Users/sinclairpan/project/Agent Store'))` 连续两次，要求结果完全
   相同且 framework-only findings 为0；common finding 单独分类，不伪装成隔离失败。
3. 运行前后比较 Agent Store 的 `git status --porcelain=v1 -uall` 原文 SHA256、
   `git diff --binary --no-ext-diff` SHA256，并对 `git ls-files -m -o --exclude-standard` 返回的每个 dirty path
   计算 path+content SHA256 清单；三类指纹必须完全相同。

最终 committed+clean identity 由 LEAN/SAFETY 双 reviewer 审查；修复意见只在同一分支最小修正并完整重验。

## 回退

implementation 产品与测试作为一个原子 commit。回退该 commit必须同时恢复 scope 逻辑和新增测试；formal
PRD 作为问题与决策记录保留，不因 implementation 回退而改写历史。
