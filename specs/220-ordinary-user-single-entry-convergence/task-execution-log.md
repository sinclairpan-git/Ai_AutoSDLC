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
- T01 Formal evidence/contract freeze：完成。
- T02 第一轮 exact-head review：候选 `602365c6`；发现两项 P2：新增 Markdown 行尾空格导致范围
  `git diff --check` 失败，以及 T41 无条件依赖 T32 导致 P2A-only 降级路径无法收口。
- 第一轮聚焦整改：删除四份 Formal 文档的行尾空格；将 T41 基础依赖改为 T24/T31，并在 acceptance 中
  明确 P2B Go 必须先完成 T32、P2B 暂停则以 T31 降级决策为前置证据。整改后 diff-check、guard 和
  plan-check 通过。
- T02 第二轮 exact-head review：候选 `e5c6bb97`；确认行尾空格已修复，但发现 Program Truth 需在
  Formal 整改后刷新，且 T31 仍会阻塞 P2B 暂停路径。
- 第二轮也是最后一轮聚焦整改：T41 仅以拥有 Go/暂停裁决的 T24 为静态依赖；P2B Go 时 acceptance
  条件要求先完成 T31/T32，暂停时直接使用 T24 的降级证据；随后刷新 Program Truth。
- 最终 exact-head review：候选 `e0383b53`；P2A 无新增问题，Program Truth 为 `fresh/blocked`，但发现 P2B
  未覆盖普通用户 fallback `python -m ai_sdlc --help` 的硬编码 module help；另有一行 truth 状态未回写。
- ROI 裁决：module fallback 是既有普通用户安装恢复合同，不属于低价值扩张；以一个既有入口文件和一条既有
  integration test 补齐 console/module 同合同。若此后再出现新的范围项，则执行 No-Go，不继续整改。
- 用户生产实现批准：待 T03；当前明确未授权。
- Program Truth：整改后 sync/audit 已得 `snapshot=fresh`、整体 `blocked`；`1154/1154` mapped、unmapped 0、
  missing 2，16 个历史 provenance blocker 原样保留，不属于 P2 修复。
- 停止性 exact-head 复核：候选 `eea14a30e3234e20a9b2f264c8ca304687751f95`；确认 T41 仅静态依赖
  T24，P2B Go 时才要求 T31/T32，P2A-only 降级路径不被阻塞；console/module 两条 help 入口均已纳入
  P2B 冻结范围与测试；Program Truth snapshot 自校验、authoring hash 和 WI220 source inventory 一致；无新增
  Critical/Important，按停止条件不再发现或扩张范围。独立评审客户端尾端因模型清单兼容告警未正常输出
  final，但其只读证据检查已完成；由同口径本地 findings-first 复核收口，不重启大评审。
- 最终 guard 负控制发现：T03=blocked 时，guard 会按既有契约跳到首个 todo 的 T11；`depends` 不是运行时门禁。
  这是任务状态建模遗漏，不是新增产品范围。整改不修改 guard：T11–T43 全部置为 blocked；用户批准后只激活
  T11，后续任务在前项完成和 ROI 决策后逐项激活。负控制必须返回 `BLOCK_CODE_PREPARE_TASKS` 且不绑定任务。

#### 2.5 ROI 裁决

- 采用：一个内部纯展示投影、run/status 两个消费者、status details 迁移桥、条件 help 隐藏。
- 拒绝：参赛版覆盖/复制、完整 Loop router、第二 aggregator、advanced 子系统、命令删除、全仓瘦身。
- 当前判断：P2A 高 ROI；P2B 仅在 P2A 稳定且预算内执行。

#### 2.6 任务/计划同步与处置

- `tasks.md`：T01/T02 done；T03 blocked；T11–T43 全部 blocked，等待逐项授权激活。
- branch disposition：`retained(Formal accepted; production approval pending)`。
- worktree disposition：`retained(Formal accepted; production approval pending)`。
- 下一步：刷新并验证 Program Truth 后停在 T03；用户明确批准生产实现后，才进入 P2A characterization/RED。

### Batch 2026-08-29-002 | T03 production approval and T11 activation

- 用户明确批准生产实现；T03 从 blocked 置为 done。
- 按逐项授权规则仅将 T11 置为 todo；T21–T43 继续 blocked。
- 当前允许范围仅为既有行为 characterization 与 P2A RED 测试；尚未授权写入生产实现。
- 下一步：锁定 run/status/Loop/JSON/exit 基线，写出会因缺少默认摘要或 `status --details` 而失败的真实 CLI 测试。

### Batch 2026-08-29-003 | T11 characterization and RED

- 既有基线：normal/open/preflight/halt、status text/json 七条代表性测试 `7 passed in 3.42s`。
- 新增纯投影 RED：no-loop fallback、single current、multiple current、malformed pointer、Next/Blockers/Rules 上限、
  仅提升 `blocking=true` status item，共六条。
- 新增 CLI RED：run normal/open/preflight/halt 五项摘要，status default compact、`--details` 迁移桥和
  `--details --json` 明确互斥，共七条。
- 首轮结果：`12 failed, 1 passed in 1.80s`；随后修正互斥测试的假阳性，要求明确错误文本，单测按预期 RED。
- T11 done；仅激活 T21。下一步先实现不超过 180 行的单一纯投影并只跑 unit GREEN，不提前接入 run/status。
