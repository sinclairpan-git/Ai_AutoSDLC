# CLI 规格（草案）：`ai-sdlc workitem plan-check`

> **状态**：**已实现** CLI `ai-sdlc workitem plan-check`（[`src/ai_sdlc/core/plan_check.py`](../src/ai_sdlc/core/plan_check.py)、[`src/ai_sdlc/cli/workitem_cmd.py`](../src/ai_sdlc/cli/workitem_cmd.py)）；本页仍作行为与退出码约定说明。测试见 `tests/unit/test_plan_check.py`、`tests/integration/test_cli_workitem_plan_check.py`。

## 目的

只读比对：

- **A**：工作项目录下 `tasks.md` / `plan.md` 中声明的进度、或外部计划文件（如 `related_plan` 指向的 Markdown）frontmatter 中的 `todos`；
- **B**：当前 Git 工作区已变更路径（或最近一次 commit 范围，由 `--since` 约定）；

输出 **差异报告**，**默认不写库**、不改 checkpoint。

## 建议命令形式

```text
ai-sdlc workitem plan-check [--wi <path-to-specs-WI-dir>] [--plan <path>] [--json]
```

| 参数 | 说明 |
|------|------|
| `--wi` | 指向 `specs/NNN-xxx/`；读取其中 `tasks.md`、`plan.md` 的 frontmatter（含 `related_plan`）。 |
| `--plan` | 显式指定计划文件；与 `--wi` 二选一或合并策略由实现定义。 |
| `--json` | 机器可读输出（CI 用）。 |

## 退出码（建议）

| 码 | 含义 |
|----|------|
| 0 | 无冲突：未发现「计划标 pending 但对应路径已有变更」等明显漂移（具体规则实现时细化）。 |
| 1 | 发现漂移或无法解析 frontmatter / 路径不存在。 |
| 2 | 用户错误（参数非法）。 |

## 与 `preflight` / `verify constraints` 的关系

- **plan-check**：偏 **元数据一致性**（计划 ↔ Git / tasks 勾选）。
- **preflight**（若存在）：偏 **门禁与文件真值**（constitution、checkpoint、specs 目录）。
- 二者可串联：先 `plan-check`，再 `preflight`，均在 `run` 真执行前可选调用。

## 非目标

- 不替代 `pytest` / `ruff`。
- 不自动修改计划文件；若提供 `--fix` 属 **P2** 讨论范围。
