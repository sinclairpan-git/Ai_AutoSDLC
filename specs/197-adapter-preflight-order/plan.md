---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：Adapter Mutation 与 Workitem Preflight 顺序修复

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute this plan task-by-task.

**Goal:** 修复 WI-196 GAP-07，使 `workitem init` 先判断真实用户工作树，再执行同一自动 adapter hook，保持其他 CLI 行为不变。
**Architecture:** 根 callback 对整个 `workitem` 组不执行 hook；`workitem_app` callback 对合法非 `init` 子命令在 handler 前执行原 hook，`init` 则在 `_ensure_workitem_init_git_preflight` 成功后执行。无效 `init` 和脏树 `init` 均 fail-closed 为零 adapter 写入。
**Tech Stack:** Python 3.11、Typer/Click、pytest、`unittest.mock`、GitClient、uv、Ruff。

## Global Constraints

- 基线为 `origin/main@4dd0f1c9cdcc26a359dd0d724f365a3168d66fe8`。
- 只实现 WI-196 GAP-07/T51；GAP-10 仅做 fail-closed 影响分析，不在本项关闭。
- 保留自动 adapter、docs branch 和 clean-tree preflight；禁止白名单忽略 adapter 写入。
- 产品新增 ≤25 LOC，测试新增 ≤80 LOC；不新增产品文件、公共抽象、依赖或配置。
- 受影响契约：CC-01、CC-02、CC-05、CC-06、CC-07。
- 新增注释使用简体中文，只解释调用顺序和副作用边界。
- 每个生产改动前必须出现对应 RED；修复后先 focused GREEN，再全量验证。
- 当前 docs branch 只冻结合同；实现必须切到 dev branch。

## 1. 文件与接口边界

```text
src/ai_sdlc/cli/main.py
  _global_before_command(ctx, version) -> None
  将 workitem 登记为由子应用自主管理 adapter 时机

src/ai_sdlc/cli/workitem_cmd.py
  workitem_app callback(ctx) -> None
  workitem_init(...) -> None
  _ensure_workitem_init_git_preflight(root, work_item_id) -> None

tests/integration/test_cli_workitem_init.py
  真实 callback → adapter 写入 → preflight 的 characterization

tests/unit/test_cli_hooks.py
  既有 adapter 异常与 PermissionError 合同，仅回归不扩展范围
```

允许修改的产品文件只有 `main.py` 与 `workitem_cmd.py`；允许修改的测试文件只有上述两个。若需要第五个文件，先停止并重新做 NC-02 影响分析。

## 2. Task 1：冻结文档与设计门禁

1. 生成 WI-197 四件套并登记 `program-manifest.yaml`、`next_work_item_seq=198`。
2. 把 observed/expected、NC、CC、GAP-10 非影响、预算、验证和回退写入 canonical 文档。
3. 计算 `spec.md + plan.md + tasks.md` 内容哈希。
4. 由兼容安全 Agent 与精简效率 Agent 独立只读评审同一哈希。
5. 任一 finding 成立即修订并重跑双评审；双 PASS 前不切 execute。

验证：

```bash
uv run ai-sdlc verify constraints
git diff --check
```

## 3. Task 2：RED characterization

**目标测试：** `tests/integration/test_cli_workitem_init.py`

1. 扩展 autouse patch，使常规用例同时隔离 root hook 与 workitem group/init hook。
2. 新增 clean→dirty preflight characterization：fake adapter 写入 Git 可见 proof receipt；首次合法 clean 调用期望成功，当前实现应因 adapter 先写而 RED。
3. 增强真实用户脏树场景：exit 1、adapter/proof 零写入；清理用户脏文件后重试，adapter 一次并成功。
4. 新增缺失 `--title` 场景：保持解析错误/退出码，adapter 零次；当前实现会先调用而 RED。
5. 新增一个非 `init` workitem 子命令场景：adapter 在 handler 前恰好一次，防止整个组被静默跳过。
6. 记录完整 RED 命令、关键失败输出和失败原因；fixture/patch 错误不算 RED。

RED 命令：

```bash
uv run pytest tests/integration/test_cli_workitem_init.py -k "adapter_before_clean_tree_preflight or missing_title or non_init" -q
```

## 4. Task 3：最小 GREEN

1. 在 `main.py` 把整个 `workitem` 组标记为子应用自主管理；不得用 `sys.argv` 或进程全局状态识别二级命令。
2. 在 `workitem_cmd.py` 增加私有 group callback：合法非 `init` 子命令在 handler 前调用现有 hook，`init` 路径跳过。
3. 在 `workitem_init` 的 clean-tree preflight 成功后立即调用同一 hook，再进入 scaffold。
4. 保持参数/handler/preflight exit code 与文本；只采用已冻结的零写入 expected delta。
5. 运行全部 RED 用例和两个 focused 文件，确认 GREEN。

GREEN 命令：

```bash
uv run pytest tests/integration/test_cli_workitem_init.py -k "adapter_before_clean_tree_preflight or missing_title or non_init" -q
uv run pytest tests/integration/test_cli_workitem_init.py tests/unit/test_cli_hooks.py -q
```

## 5. Task 4：兼容补强与重构检查

1. 确认真实用户脏树和无效 `init` 都在 adapter 调用前失败，干净重试才持久化 proof。
2. 确认合法 `init` 与非 `init` workitem 子命令各调用一次，其他顶层命令没有 diff。
3. 检查 GAP-10 proof carrier、digest/path 校验、persisted field schema 与 release blocker 均未改动。
4. 统计产品/测试新增 LOC，超过预算即停止并缩小实现。
5. 删除只为测试服务的生产分支或重复 helper；不做相邻重构。

## 6. Task 5：验证、证据与评审

依次运行：

```bash
uv run pytest tests/integration/test_cli_workitem_init.py tests/unit/test_cli_hooks.py -q
uv run pytest -q
uv run ruff check src tests
uv run ai-sdlc verify constraints
git diff --check
```

然后：

1. 把 RED/GREEN、全量测试、LOC、回退和 GAP-10 非影响证据追加到 `task-execution-log.md`。
2. 实现者自审并提交一个 conventional commit。
3. 对任务 diff 做 spec-compliance + code-quality 独立 review；修复所有 Critical/Important 后复审。
4. 对完整 branch 做最终只读 review。
5. 推送 PR，按 `AGENTS.md` 请求 Codex review 并维持 heartbeat；checks/review 全绿后合并。

## 7. 回退与完成判定

- 本项通过单独 revert 实现提交回退，不修改 adapter proof 或 work item schema。
- 文档、RED test 与执行证据可保留用于重新实现。
- 只有 PR 合并、main 验证、program truth fresh 且 WI-196 GAP Evidence Index 指向本项证据后，T51 才关闭。
