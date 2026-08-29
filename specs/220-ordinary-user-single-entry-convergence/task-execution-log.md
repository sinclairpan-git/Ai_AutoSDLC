# 任务执行日志：普通用户单入口收敛

**功能编号**：`220-ordinary-user-single-entry-convergence`  
**创建日期**：2026-08-29  
**状态**：Formal 候选；生产实现未授权

## 1. 归档规则

- 本文件只记录 WI220 的真实批次证据；后续批次追加，不重写历史裁决。
- 每批记录任务编号、改动范围、命令/结果、评审、ROI、任务同步和分支/worktree disposition。
- Formal、P2A、P2B 分批提交；产品实现前必须有用户明确批准。
- 同类对抗整改最多两轮；越过冻结范围或 6 人日预算时降级/No-Go，不继续堆支撑实现。
- 参赛版只记录远端行为证据，不复制代码、测试或历史。

## 2. 批次记录

### Batch 2026-08-29-001 | T01 Formal evidence and contract freeze

#### 2.1 批次范围

- 覆盖任务：T01
- 分支：`feature/220-ordinary-user-single-entry-convergence-docs`
- 基线：主线 `origin/main@e70ced9028ca967865386565f4e23eab999ef320`
- 参考：参赛版远端 `main@b6addbab22ab069ea1d6d7306fe1c676bd056333`
- 改动范围：WI220 四份 Formal 文档、workitem sequence/manifest、continuity，以及根 manifest inventory 的两条
  机械数量断言；无 `src/` 或特性 tests 实现。

#### 2.2 证据与决策

- 主线根帮助真实展示 9 个直接命令和 18 个 Typer 命令组；18 个组全部有测试引用，不能按“看起来复杂”删除。
- 主线 `run` 保留七阶段执行、frontend attachment 和 AgentOps 责任；P2 只补有界终态摘要。
- 主线顶层 `status` 当前只有 `--json`；参赛版远端证明 `--details` 迁移桥可行，但其 blocked exit=1 不适用于
  主线，因此只借鉴展示分流，不复制 exit 语义。
- 参赛版远端还实现了完整五 Loop predecessor router；该实现会把 P2 拉入 P4 范围，Formal 明确拒绝迁移。
- 高级命令采用 help 隐藏 + README 分类索引，直接调用兼容；不新建 `advanced` 命令或注册表。
- P2A/P2B 总预算 4–6 人日；P2A 超 3 人日或投影超 180 行时降级，第三轮同类整改 No-Go。

#### 2.3 已执行命令

- `git rev-parse HEAD` / `git rev-parse origin/main`：均为 `e70ced9028ca967865386565f4e23eab999ef320`。
- `uv run ai-sdlc --help`：确认当前 27 个可见入口。
- `uv run ai-sdlc run --help`：当前仅 `--mode`、`--dry-run`。
- `uv run ai-sdlc status --help`：当前仅 `--json`。
- `rg` command usage inventory：18 个顶层组均存在测试覆盖，文档/脚本引用从 0 到 54 个文件不等。
- `git ls-remote https://github.com/SinclairPan/Ai_AutoSDLC.git refs/heads/main`：
  `b6addbab22ab069ea1d6d7306fe1c676bd056333`。
- Formal 写入前基线：`uv run ai-sdlc verify constraints` 无 blocker；`uv run ai-sdlc program validate` PASS。
- `uv run ai-sdlc workitem guard --wi ... --json`：parser 结构修正后绑定 T01，无 errors；生产任务不在当前 scope。
- `uv run ai-sdlc workitem plan-check --wi ... --json`：`drift=false`，related plan 指向冻结路线图。
- `uv run ai-sdlc program truth sync --execute --yes`：snapshot=`blocked`，inventory `1154/1154`、unmapped 0、
  missing 2；16 个历史 provenance blocker 原样保留。
- `uv run ai-sdlc program truth audit`：exit 1，`state=blocked`、`snapshot state=fresh`；这是预期诚实真值。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：`1 passed in 161.89s`。
- `git diff --check`：PASS。

#### 2.4 评审与验证状态

- 宪章/规格对齐：已冻结 MVP、验证、回退、无新状态、docs/dev 分支边界。
- T01 Formal evidence/contract freeze：完成；exact-head review 待 T02。
- 用户生产实现批准：待 T03；当前明确未授权。
- Program Truth：待 Formal 最终内容后执行 sync/audit；历史 provenance blocker 必须保持诚实，不属于 P2 修复。

#### 2.5 ROI 裁决

- 采用：一个内部纯展示投影、run/status 两个消费者、status details 迁移桥、条件 help 隐藏。
- 拒绝：参赛版覆盖/复制、完整 Loop router、第二 aggregator、advanced 子系统、命令删除、全仓瘦身。
- 当前判断：P2A 高 ROI；P2B 仅在 P2A 稳定且预算内执行。

#### 2.6 任务/计划同步与处置

- `tasks.md`：T01 done；T02 todo；T03 blocked；生产任务全部 todo。
- branch disposition：`retained(Formal review pending)`。
- worktree disposition：`retained(Formal review pending)`。
- 下一步：完成 Formal 新鲜验证、exact-head 独立评审和必要整改；随后停下请用户决策。
