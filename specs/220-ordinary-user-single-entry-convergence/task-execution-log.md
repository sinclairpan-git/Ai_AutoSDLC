# 任务执行日志：普通用户单入口收敛

**功能编号**：`220-ordinary-user-single-entry-convergence`
**创建日期**：2026-08-29
**状态**：P2A/P2B 已完成；T43 第一轮 exact-head 对抗整改中

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

### Batch 2026-08-29-004 | T21 pure projection GREEN

- 新增 `src/ai_sdlc/cli/default_summary.py`，只包含内部不可变摘要与纯投影；未修改 `beginner_guidance.py`，
  因此不存在双 projection。
- `uv run pytest tests/unit/test_default_summary.py -q`：`6 passed in 0.36s`。
- `uv run ruff check src/ai_sdlc/cli tests/unit/test_default_summary.py`：PASS。
- 投影模块 121 行；无持久化、public schema/config/router，Next/Blockers/Rules 上限由 unit tests 锁定。
- T21 done；仅激活 T22。Program Truth 在 P2A 切片完成后统一刷新，避免每个微任务重复昂贵扫描。

### Batch 2026-08-29-005 | T22 run summary GREEN

- 在既有 run 分支上追加同一纯投影 renderer；未初始化、adapter/reconcile preflight、normal、open gate、halt
  均保留原输出与 exit contract。
- 修正既有 `test_run_outside_project` 假阳性：移除不受支持的 `CliRunner.invoke(cwd=...)`，改用真实 cwd；
  旧测试此前把 `TypeError` 的 exit 2 误认为业务失败。
- 六条关键路径测试 `6 passed in 1.49s`；run 全文件与 unit 回归 `45 passed in 9.12s`；
  default summary `6 passed in 0.37s`；Ruff PASS。
- 未改 Runner、ProgramService、Loop model、status JSON builder、frontend attachment 或 AgentOps 上报。
- T22 done；仅激活 T23。

### Batch 2026-08-29-006 | T23 status convergence GREEN

- `status` 默认路径仅消费既有 status surface、checkpoint 与五类只读 Loop status，输出 Current Loop/Result/Next/
  Blockers；不调用 IDE adaptation、resume rebuild 或详细 renderer。
- 新增 `--details` 承载原完整人类表格、handoff 和诊断摘要；既有 text assertions 原样迁移，不删除旧合同。
- `--json` 保持原 early return；`--details --json` 明确 exit 2，并输出互斥原因。
- 七条关键路径 `7 passed in 2.27s`；status 全文件 `57 passed in 46.98s`；Ruff PASS。
- 单一投影当前 147 行，仍低于 180 行停止线；未修改 status JSON builder 或持久化层。
- T23 done；仅激活 T24 adversarial ROI gate。

### Batch 2026-08-29-007 | T24 adversarial ROI gate

- exact-head：`24e05e106cc05448e0f986b7b29421ab3ca77933`；工作树在评审前干净。
- 新鲜范围统计：生产代码净增 304 行、删除 5 行；其中唯一投影 `default_summary.py` 为 147 行，低于 180 行
  止损线。投影仅由 run/status 两处消费，没有新增状态、持久化、API、schema、配置、规则引擎或 Loop router。
- 新鲜门禁：P2A 三文件组合回归 `102 passed in 57.69s`；目标 Ruff PASS；`verify constraints` 无 BLOCKER。
- 对抗复核：未发现 Critical/Important 可操作问题。独立 Codex review 客户端因 0.137.0 无法解析模型目录中的
  `max` 档位持续输出兼容噪声，按有界止损终止；其未形成产品 finding，本地 findings-first 复核覆盖输出真值、
  exit/JSON/只读边界、Loop fail-closed、单投影复用与范围膨胀。
- 残余风险：仅内置规则文件自身编码损坏时，标题读取可能失败；正常分发路径无证据触发，且不值得为该低概率
  场景扩大本切片测试/异常策略，留作出现真实故障证据后处理。
- ROI 裁决：**Go P2B**。P2A 在同日四个有界批次完成，低于 3 人日预算；价值目标完整达成且没有触发任一
  降级条件。P2B 仍限定 1–2 人日，只做 help 可见性元数据、module fallback 与 README 高级索引。
- Program Truth 刷新：snapshot hash=`928cd534732bf777b593cbcda72f1f852216505bb5e560ad6a1349fedc7a274c`；
  audit=`fresh/blocked`（预期 16 个历史 truth-check blocker）；inventory `1154/1154`、unmapped 0、missing 2；
  manifest 集成测试 `1 passed in 158.08s`。
- T24 done；仅激活 T31。下一步先写 console/module 六入口与高级命令直接可达性的 RED，不提前修改实现。

### Batch 2026-08-29-008 | T31 help visibility and compatibility RED

- 新增 console root visible allowlist：精确为 `init/adopt/run/status/recover/self-update`，并要求根帮助明确高级命令
  仍可直接调用。
- 新增 module ASCII fallback 同一 allowlist；新增 21 个高级顶层入口逐项 `--help` characterization。
- 对抗发现：既有 `command_names._walk_group()` 会跳过 `hidden` 命令；直接添加 Typer hidden 元数据会让 close-check
  使用的全量 command inventory 静默缩水。以 synthetic hidden command RED 锁住“help 隐藏不等于治理发现删除”。
- RED 结果：三条新行为按预期失败，21 个高级入口直接 `--help` 通过，合计 `3 failed, 1 passed in 1.80s`；
  Ruff PASS。
- 测试隔离：CliRunner 对非只读顶层组执行 `--help` 时会触发现有 adapter hook；改为在临时非项目目录验证，避免
  污染 checkout，未修改该既有 hook 行为。
- T31 done；仅激活 T32。T32 允许范围补入既有 `cli/command_names.py`，只移除 hidden 过滤，不新增注册表或第二
  帮助系统；这是满足已冻结 command inventory 兼容合同所需的两行级修正。

### Batch 2026-08-29-009 | T32 minimal help convergence GREEN

- console root help 仅通过 Typer `hidden=True` 收敛为六个入口；帮助正文明确高级命令仍可直接调用。未移动、删除、
  重命名命令或修改参数/实现。
- `python -m ai_sdlc --help` 的 ASCII fallback 同步为相同六入口和说明；无参数 module 路径继续复用该输出。
- `command_names._walk_group()` 不再把 help-hidden 当作 inventory 删除，close-check 继续看到 134 条叶子命令；
  `adapter status`、`program truth audit`、`loop status`、`pr-review doctor` 抽样均存在。
- README 新增有界 Advanced Command Index，按四类精确列出 21 个 help-hidden 顶层入口；测试逐项校验索引完整。
- T32 focused GREEN：先 `4 passed in 1.73s`；三文件完整回归加入 README 断言后 `16 passed in 5.27s`；
  目标 Ruff PASS，`git diff --check` PASS。
- T32 done；仅激活 T41。有界 guidance 对账只修改 `rg` 证明与 init/run/status 新合同冲突的文件。

### Batch 2026-08-29-010 | T41 bounded guidance reconciliation

- `rg` 复核 AGENTS、四个 adapter canonical guidance、USER_GUIDE、docs 和 README；AGENTS/adapter 已明确 init 后
  不要求手动执行 diagnostics，历史 release/defect/plan 记录不改。
- 唯一真实漂移位于 `USER_GUIDE.zh-CN.md` 常用命令表：将默认 `status` 修正为 Current Loop/Result/Next/
  Blockers 紧凑面，并新增 `status --details` 完整诊断入口；没有全库措辞优化。
- 新增有界用户指南断言；`test_cli_beginner_ux.py + test_ide_adapter.py` 为 `45 passed in 1.86s`；目标 Ruff
  与 `git diff --check` PASS。
- T41 done；仅激活 T42。下一步执行 clean init→run/兼容矩阵、full pytest、Ruff、constraints、Program validate、
  manifest 与工作树副作用检查。

### Batch 2026-08-29-011 | T42 full verification and regression reconciliation

- 首轮静态门禁：`uv run ruff check .` PASS；`verify constraints` 无 BLOCKER；`program validate` PASS。
- 首轮 full pytest：`3396 passed, 3 skipped, 5 failed in 1122.92s`。五个失败均为 WI220 新合同下的旧测试遗漏：
  三个默认 `status` 仍期待旧详细面/adapter 写入，两个 module 根帮助仍期待显示 help-hidden 命令。
- 按 systematic debugging 完成根因复核：对照已迁移的 status tests 与既有 module direct-help 模式，确认产品行为
  符合冻结 spec；只将详细面断言改为 `status --details`，将 loop/pr-review 改为 module 直接 `--help`，未改生产代码。
- 五条失败路径最小复测 `5 passed in 2.17s`；四个受影响文件完整回归 `65 passed in 7.57s`；目标 Ruff PASS。
- 第二轮 full pytest：`3401 passed, 3 skipped in 1055.59s`；全套无运行副作用，`git diff --check` PASS。
- Program Truth 刷新：snapshot hash=`2e6ae15c788ca0359c720ea8e27d14dc7caaee10cf2594f007b4c642516fbfe6`；
  audit=`fresh/blocked`（预期历史 blocker）；inventory `1154/1154`、unmapped 0、missing 2；manifest 集成测试
  `1 passed in 157.83s`。
- T42 本地出口通过；Windows/macOS/Linux required checks 按仓库协议在 T43 PR 上取得，避免把尚未发生的远端 CI
  写成已完成事实。T42 done；仅激活 T43。

### Batch 2026-08-29-012 | T43 exact-head review remediation round 1

- 独立评审 exact HEAD `8031d7885182bbaf669866deaa4c5318936aa05c`：0 Critical、3 Important；未批准 push/PR。
- 三类缺口均经代码与测试复现：run 未消费 status surface；malformed Loop 丢失既有修复动作；confirm pause 与
  required AgentOps 失败被摘要误报为 completed。没有采纳超出冻结范围的重构。
- RED：新增共享 run/status 真值、malformed next action、confirm pause、AgentOps final-result 测试；
  `6 failed, 43 passed in 9.45s`。
- 最小 GREEN：共享投影直接从既有 status surface 选择工作项动作；run 只读复用 fast status surface；跟踪既有
  confirm callback 的拒绝结果；AgentOps 上报成功后才渲染 completed，失败时保留 exit 2 并摘要为 blocked。
- 删除注释：`src/ai_sdlc/cli/commands.py` 的“只选取既有 status surface 中最具体的工作项下一步”随重复 `_status_next_actions()` 移除；等价意图迁移到 `default_summary.py` 的共享投影函数注释，避免 status/run 两处选择逻辑再次漂移。
- 聚焦回归 `49 passed in 10.09s`；目标 Ruff PASS。未改 Runner、schema、持久化、命令面或 Loop router。
- 相关子系统回归覆盖 default summary、五 Loop status、Runner confirm、run/status CLI 与 telemetry readiness：
  `193 passed in 60.76s`；全库 Ruff 与 `git diff --check` PASS。
- 首次 constraints 运行准确拦截上述 docstring 迁移记录缺少同一新增行的 path + summary；改为规范化单行删除原因后，
  `verify constraints: no BLOCKERs`。`program validate: PASS`。
- 整改提交后刷新 Program Truth：snapshot hash=`6104f6afabced2e1b6b75f48e3a3a5d28bc4281f13cf12b444303b17a43e43e0`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- 候选 `f4071c6d5784b60840459652acea47285eba276a` fresh 全量门禁：`3405 passed, 3 skipped in 1054.41s`；
  Ruff PASS；constraints no BLOCKERs；program validate PASS；manifest gate `1 passed in 155.94s`；truth audit
  `fresh/blocked`，阻断归因仍为上述 16 个历史 truth-check。
- 同一独立 reviewer 对 clean HEAD `41a2708feaa5c607660013dd06ca5c3739f771a6` 复审：0 Critical、0 Important；
  上轮三项全部闭合，未触发 scope/ROI/bloat stop-condition，结论 `Ready to push/open PR: Yes`。
- 唯一 Minor 为 `tasks.md` 顶部阶段与 handoff next step 滞后；随本记录同步修正，不开启第二轮产品代码整改或复审。

### Batch 2026-08-29-013 | PR #185 Python 3.11 colored-output test repair

- PR #185 Compatibility Gate 在 Ubuntu/macOS Python 3.11 各失败一项：
  `TestCliStatus.test_status_rejects_details_with_json`；业务 exit 2 和错误文案均正确。
- CI 的 Rich/Typer 彩色输出把 `--details` / `--json` 插入 ANSI 控制码，旧断言直接匹配原始 `result.output`，
  因终端颜色环境产生跨平台假失败；同一日志其余 `3404 passed, 3 skipped`。
- 仅将该测试断言改为 `click.unstyle()` 后压缩空白再比较；未修改生产代码或 CLI 合同。
- focused `1 passed in 0.83s`；status 全文件 `57 passed in 47.43s`；目标 Ruff 与 `git diff --check` PASS。
- 下一步：刷新 Program Truth、push 同一分支、重新请求 Codex review，并继续 heartbeat 直到 required checks 全绿。

### Batch 2026-08-29-014 | PR #185 Codex review remediation round 2

- Codex 对 exact HEAD `e9ee957d71f5ca94c59ae53683f6fbc8780369e6` 提出两项可操作问题：默认 status/run
  跳过 work-item truth，可能误报 `Next: None` / `Result: ready`；损坏且无可用备份的 checkpoint 会回落为
  `pipeline/init` / `ready`。
- 先验证投入产出：只启用 work-item diagnostics、继续跳过 Program Truth 与 truth ledger 的真实仓库采集耗时
  `5.08s`，未触发新增缓存、schema、持久化或第二套投影的必要性。采纳两处布尔开关修复，不扩张 readiness builder。
- RED：status 与 run 调用参数合同各失败；损坏 checkpoint 场景准确复现 `pipeline/init` / `ready` / `Next: None`。
- 最小 GREEN：默认 status/run 均加载有界 work-item diagnostics；status 对“文件存在但主文件和备份均无法加载”
  fail-closed 为 `pipeline/unavailable` / `blocked`，给出恢复有效 checkpoint 的动作。不存在 checkpoint 的新项目仍为
  `pipeline/init`，可用备份仍由既有 loader 自动接管。
- focused `2 passed`；status 全文件 `58 passed in 48.52s`；run + default summary + telemetry readiness
  `66 passed in 10.47s`；目标 Ruff 与 `git diff --check` PASS。
- Program Truth 刷新：snapshot hash=`8d14dc48d0ffd1ed1b1309ceec40191672f0b9ec6d58ad94ed0eaf5c1d13a837`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- `verify constraints` 无 BLOCKER；`program validate` PASS；manifest gate `1 passed in 163.75s`。
- 下一步：提交并 push 同一 WI220 分支，回复两项 review finding 后重新请求 Codex review。

### Batch 2026-08-29-015 | PR #185 checkpoint semantic validation closeout

- Codex 对 `409db4f658c762bbf099978b0a999cd8178d4b44` 复审确认前两项已闭合，并补充一个同边界的 P2：
  checkpoint 即使 YAML/Pydantic 可解析，未知 stage、缺失更新时间等 recovery invariant 仍可能被默认 status 误报 ready。
- finding 经 RED 复现为 `pipeline/bogus` / `ready`。整改复用既有 strict checkpoint loader 及其主文件→备份回退，
  只在 compact status caller 将最终验证失败投影为 unavailable/blocked；未新增校验器、状态或恢复分支。
- 同一测试同时覆盖语法损坏与语义损坏；focused `1 passed`，status 全文件 `58 passed in 47.51s`，
  checkpoint unit `14 passed`；目标 Ruff 与 `git diff --check` PASS。
- ROI/止损：本次生产改动仅切换既有 strict contract 并捕获既有两类 loader 异常；不继续扩展 checkpoint 诊断文案、
  新错误类型或第二套校验路径。下一步刷新 truth 与门禁后 push 复审。
- Program Truth 刷新：snapshot hash=`d8c3ed2ecbfcaaca288a2bb7e0ca4831978463644dff5525f874363ded0c9a60`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- `verify constraints` 无 BLOCKER；`program validate` PASS；manifest gate `1 passed in 164.13s`。

### Batch 2026-08-29-016 | PR #185 recovered-surface and details compatibility closeout

- Codex 对 `39c4f023e501a3f70da82c6c6cf0f953a8e9e7ce` 提出两个同 caller 边界的 P2：strict loader 从备份
  恢复时，先构造的 surface 仍可能来自被拒绝主 checkpoint；`status --details` 不应因 compact 修复而启用完整
  work-item truth。
- 两项均经 RED 复现。最小整改仅做 caller 隔离：compact 检测 strict recovery 与原始 non-strict checkpoint 不一致时
  丢弃不可信 surface；work-item truth 开关精确限定为 JSON 或 compact，details 保持迁移前设置。
- 未改 readiness builder、checkpoint loader、schema、缓存或持久化；没有为稀有恢复边界新增诊断系统。
- focused 三路径 `3 passed`；status 全文件 `59 passed in 47.69s`；checkpoint unit `14 passed`；
  目标 Ruff 与 `git diff --check` PASS。下一步刷新 truth 与出口门禁后 push exact-head 复审。
- Program Truth 刷新：snapshot hash=`5c96b9bfa6bc4f0602d280c5fd725dde2d122e390f3fbe10cd75d971743abc69`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- `verify constraints` 无 BLOCKER；`program validate` PASS；manifest gate `1 passed in 164.22s`。

### Batch 2026-08-29-017 | PR #185 multi-stage dry-run truth aggregation

- Codex 对 `cdc19b8b9e326dbf1b821c87493d6b0587da44bf` 提出 P1：较早 stage 为 RETRY、最终 stage 为 PASS 时，
  run 只看 `last_result` 会误报 completed。
- finding 经既有 open-gate 测试最小改造后 RED 复现；没有新增场景矩阵。整改直接复用已记录的 `stage_results`，
  聚合全部非 PASS stage 及失败消息，展示最后一个 open stage，摘要保持 `Result: open_gates`。
- 删除重复 `last_result` 状态和第二次 open-gate 判定；未改 Runner、gate retry、exit code、AgentOps stage facts 或
  非 dry-run 行为。生产净复杂度未增加第二套真值。
- focused `1 passed`；run 全文件 `41 passed in 10.44s`；目标 Ruff 与 `git diff --check` PASS。
- ROI 裁决：P1 为真实结果误报且修复复用既有列表，批准最小闭合；不扩展 dry-run renderer 或新增聚合模型。
- Program Truth 刷新：snapshot hash=`1c51b524fda1d1eb667c3ebef984da7849b02587ca59440554f88171ff421d9a`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- `verify constraints` 无 BLOCKER；`program validate` PASS；manifest gate `1 passed in 162.42s`。

### Batch 2026-08-29-018 | PR #185 malformed-backup fail-closed and CI closeout

- Codex 对 `8e79402a2073b3e82cb159e23d228d53fcac4564` 提出 P2：主 checkpoint 与备份均不可解析时，
  compact status 的非严格读取会逸出 `YamlStoreError`，而不是输出 `pipeline/unavailable` / blocked。
- finding 通过改造既有 unreadable-checkpoint 测试 RED 复现。整改在 compact caller 先做 strict recovery 预检；
  预检失败即跳过依赖 checkpoint 的派生 surface，且不再执行 raw checkpoint 读取。未改 loader、schema 或 readiness builder。
- 同一 exact head 的六个跨平台 Pytest 作业均只有一个共同失败：聚合全部 open-stage blocker 后把项目绝对路径带入
  beginner 输出，使既有 ingress 隔离断言误中测试目录名。整改仅把 gate message 中的项目根路径缩为 `.`，
  保留全部 stage 的 open-gate 真值与 blocker 聚合，不新增 renderer 或脱敏框架。
- malformed-backup focused `1 passed`；status 全文件 `59 passed`；beginner/run/status 相关文件 `108 passed`；
  目标 Ruff 与 `git diff --check` PASS。全量套件以 `-x -vv` 精确复现 CI 首个失败后止损；CI 日志确认每个矩阵
  `3406 passed, 3 skipped, 1 failed`，无需重复本地跑完 3410 项。
- ROI 裁决：两处均为现有 caller 的 fail-closed/输出边界修补；拒绝扩展 checkpoint 诊断系统或新增路径模型。
- Program Truth 刷新：snapshot hash=`776b7f049bb7cdd7a81cbefcf96814e6460ebe01ad6140d80d07743435c29578`；
  state=`blocked`（16 个既有历史 truth-check blocker），inventory `1154/1154`、unmapped 0、missing 2。
- `verify constraints` 无 BLOCKER；`program validate` PASS；manifest gate `1 passed in 163.94s`。
- 生命周期纠偏：T42 只承载已完成的本地验证，跨平台 required checks 明确归入 T43；T43 置为 doing。
- 下一步：完成首轮变更审计、全量门禁与 exact-head 复审；无 Critical/Important 后才 push/open PR。
