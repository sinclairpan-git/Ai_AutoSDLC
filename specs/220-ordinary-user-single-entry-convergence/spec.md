# 产品需求文档：普通用户单入口收敛

**功能编号**：`220-ordinary-user-single-entry-convergence`
**创建日期**：2026-08-29
**状态**：Formal 候选，等待用户批准生产实现
**类型**：CLI beginner UX + compatibility-preserving presentation convergence
**主线冻结基线**：`origin/main@e70ced9028ca967865386565f4e23eab999ef320`
**参赛版参考基线**：远端 `main@b6addbab22ab069ea1d6d7306fe1c676bd056333`

## 1. 问题、证据与用户价值

当前远端主线已经拥有完整的初始化、流水线、Loop、Program、Telemetry、Provenance、AgentOps 和本地评审能力，
但普通用户首次查看根帮助时会同时看到 9 个直接命令和 18 个顶层命令组；`run` 负责执行流水线，却只输出
阶段进度、最终阶段或 halt 文本，没有稳定呈现“当前 Loop、Result、Next、Blockers、Applicable Rules”；
`status` 默认终端面会聚合 checkpoint、handoff、active WI、governance、Program Truth、frontend 和 guard 等大量
诊断行，且当前顶层 `status` 只有 `--json`，没有将旧详细终端面迁出的 `--details`。

冻结证据：

| 证据 | 主线事实 | 对 P2 的含义 |
|---|---|---|
| 根命令注册 | `src/ai_sdlc/cli/main.py` 注册 9 个直接命令、18 个 Typer 组 | 复杂度是真实认知成本，但不是删除目标 |
| `run` | `src/ai_sdlc/cli/run_cmd.py` 约 728 行，执行语义和 AgentOps 上报已被大量测试覆盖 | 只补展示合同，不改 Runner、stage、上报或 exit code |
| `status` | `src/ai_sdlc/cli/commands.py::status_command` 默认渲染完整表格；`--json` 是既有机器合同 | 默认降噪，旧详细终端面迁到新增 `--details`，JSON 不改 |
| 高级能力使用 | 18 个命令组全部存在自动化测试；多数有文档或脚本引用 | 只能隐藏默认发现面，不能删除或重命名 |
| 参赛版远端主线 | 已验证 Result/Next/Blockers、最多两段规则、`status --details` 和隐藏低频命令可用 | 只借鉴外部行为；不复制代码、模型、路由器或提交历史 |

用户收益是让普通用户在 `init` 之后只需记住 `run`，就能看到可信结果和唯一下一步；`status` 作为只读查看入口
保持紧凑。高级用户和脚本继续使用原命令、参数、JSON 与退出码，不承担一次性迁移成本。

## 2. 目标与非目标

### 2.1 P0 目标

1. `ai-sdlc init .` 保持唯一初始化入口；已有项目仍可使用 `ai-sdlc adopt`。
2. `ai-sdlc run` 在既有执行/预演输出结束时稳定追加一个有界摘要：当前 Loop、Result、Next、Blockers、
   最多两条 Applicable Rules。
3. `ai-sdlc status` 默认输出同源的紧凑 Current Loop/Result/Next/Blockers；新增 `--details` 继续承载当前详细
   人类可读表格；`--json` 的键、值语义、副作用和退出码保持兼容。
4. 默认根帮助只展示普通用户入口；高级命令继续可直接调用，并在 README 提供分类索引。
5. 展示只消费现有 checkpoint、Loop status 和 status JSON surface，不新增持久化状态、第二聚合器或治理对象。

### 2.2 明确非目标

- 不把参赛版覆盖主线，不复制/cherry-pick 参赛版模块、测试或历史。
- 不把主线 `run` 改成只读 Loop router，不退休七阶段 Runner，不改变 `--mode`、`--dry-run` 或确认语义。
- 不实现跨五类 Loop 的 predecessor-chain 路由、动态专家、评分或新状态机；该能力仍属于 P4。
- 不删除、重命名或迁移 Program、Telemetry、Provenance、AgentOps、Loop、PR Review 等命令。
- 不新增 `advanced` 子命令、命令注册表、schema、ledger、certificate、receipt、缓存或配置开关。
- 不全面拆分 `run_cmd.py`、`commands.py` 或 `ProgramService`，不以 400/50 或 LOC 为交付目标。
- 不修改产品站、本地材料分支或参赛版仓库内容。
- 不在 Formal 阶段修改 `src/`、测试或生产文档；生产实现须再次获得用户批准。

## 3. 冻结默认合同

### 3.1 `run` 默认摘要

每次正常完成、dry-run open gate、preflight blocker 或 `PipelineHaltError` 都必须在保持原 exit contract 的前提下
得到以下语义字段；标题可中英双语，顺序固定：

1. **Current Loop**：优先使用现有单一 current Loop status；若没有可用 Loop artifact，诚实显示
   `pipeline/<checkpoint.current_stage>`，不得伪造五 Loop predecessor chain。
2. **Result**：本次 run 的实际结果，如 completed、open gates、blocked 或 halted；不得把 dry-run open gate 写成
   production success。
3. **Next**：最多一个首要动作；优先复用现有 reconcile/adapter/gate/workitem/Loop next action，不生成并列清单。
4. **Blockers**：去重后最多三条；无阻断显式显示 `None`。截断只影响默认终端摘要，详细诊断仍可由明确命令获取。
5. **Applicable Rules**：按当前 checkpoint stage 使用既有 `RulesLoader.get_active_rules()`，最多两条
   `name + title`；不输出整份规则正文，不新建规则选择器，规则不可读时作为说明而非新 blocker。

既有 stage progress、frontend attachment summary、AgentOps 上报和诊断信息不在本项删除。若摘要与执行结果冲突，
执行结果/exit code 是 authority，摘要必须修正而不是覆盖 authority。

### 3.2 `status` 默认与详细面

- 默认 `status` 使用同一内部展示投影输出 Current Loop、Result、Next、Blockers，不输出完整 property table、
  handoff/Program/frontend/guard 逐行诊断。
- `status --details` 精确保留当前默认详细终端面和 exit code；它是一次显式迁移桥，不是第二状态计算路径。
- `status --json` 继续直接输出既有 `build_status_json_surface()` 结果；不得更名、删键、改变状态语义、隐式初始化
  telemetry 或触发 adapter 写入。
- `--details --json` 返回参数错误，exit code 为 2；不猜测调用方意图。
- initialized 项目的默认/`--details` 继续返回 0，即使存在业务 blocker；不照搬参赛版的 blocked=1 行为。

### 3.3 Current Loop 的有界语义

P2 不新建完整五 Loop router。单一展示投影只允许：

1. 调用现有五类 `get_loop_status()` 读取 current pointer；
2. 恰好一个未关闭 current Loop 时展示其既有 type/id/status/next；
3. 多个未关闭 current Loop、任一 pointer malformed 或读取失败时 fail-closed，摘要报告歧义/阻断；
4. 没有未关闭 current Loop 时回退 `pipeline/<current_stage>`；不校验跨 Loop predecessor lineage，不推断
   frontend-evidence 是否必选。

这是一层无写入的展示投影，不持久化结果、不改变 Loop artifact，也不成为新的执行授权来源。

### 3.4 默认帮助与高级兼容矩阵

冻结的默认根帮助仅展示：

| 默认可见 | 用途 |
|---|---|
| `init` | 新项目初始化 |
| `adopt` | 已有项目接入 |
| `run` | 普通用户唯一日常入口 |
| `status` | 紧凑只读查看 |
| `recover` | 由 Result/Next 指引的恢复入口 |
| `self-update` | 安装版本维护 |

以下命令只从默认 help 隐藏，直接调用、参数解析和运行行为、exit contract 均不变：

- 诊断/维护：`doctor`、`index`、`scan`、`refresh`、`adapter`、`host-runtime`、`handoff`；
- authoring/governance：`workitem`、`stage`、`gate`、`rules`、`studio`、`program`、`verify`；
- observability/enterprise：`telemetry`、`provenance`、`trace`、`agentops`、`enterprise`；
- 专项 Loop/review：`loop`、`pr-review`。

根帮助文字必须明确“这里只展示常用入口；高级命令仍可调用”，README 提供上述分类和精确命令索引。P2 不为此
再创建 `advanced` 命令或动态帮助系统。

## 4. 兼容与失败矩阵

| 场景 | 默认人类输出 | 机器/高级合同 | exit contract |
|---|---|---|---|
| 未在项目内 | Result/Next 指向 `ai-sdlc init .` | 无新增 JSON | 保持 run/status 既有失败码 |
| initialized，无 Loop artifact | `pipeline/<stage>` + 现有下一步 | checkpoint 不改写 | 不变 |
| 单一 active Loop | 显示既有 type/id/status/next | Loop artifact 不改写 | 不变 |
| 多 active 或 malformed pointer | 明确 ambiguous/blocked，不猜路径 | 高级 `loop status` 仍可诊断 | 不变 |
| run 正常完成 | 五项摘要 + 既有进度/报告 | Runner/AgentOps 不变 | 0 |
| dry-run open gate | Result 明确 open gate，最多三条 blocker | dry-run 不升级为 execute | 0（保持现状） |
| reconcile/adapter preflight | 摘要给唯一修复动作 | 原提示和副作用边界不变 | 1 |
| Pipeline halt | Result=halted + 真实 blocker | 原上报仍执行 | 2 |
| status default | 四项紧凑摘要 | initialized status 仍为 0 | 0 |
| status `--details` | 旧完整表格 | 不创建第二计算路径 | 0 |
| status `--json` | 只输出 JSON | shape/语义/只读性不变 | 0 |
| 隐藏高级命令直接调用 | 不受默认 help 影响 | argv/参数/行为不变 | 不变 |

## 5. 功能需求

- **FR-220-001**：普通用户在 init 后只需使用 `run` 即可获得 §3.1 五项可信摘要。
- **FR-220-002**：`run` 摘要不得改变 Runner、gate、AgentOps、frontend attachment、dry-run 或 exit 语义。
- **FR-220-003**：Current Loop 必须遵守 §3.3 的单一投影与 fail-closed 规则；不得引入五 Loop 路由器。
- **FR-220-004**：Applicable Rules 只复用既有 stage-active rules，最多两条 name/title，不读取或倾倒全文。
- **FR-220-005**：`status` 默认紧凑；`--details` 承载旧终端面；`--json` 合同与只读边界不变。
- **FR-220-006**：默认 help 只展示 §3.4 六个入口；所有隐藏命令仍可直接调用且参数/exit contract 不变。
- **FR-220-007**：README、AGENTS/template adapter 指导和 CLI help 必须一致，不再要求普通用户先理解诊断命令。
- **FR-220-008**：实现最多新增一个内部、无持久化的默认展示投影边界；不得新增公共 schema/状态/配置。
- **FR-220-009**：只允许局部修改 `run/status/main/help/docs/tests`；越过范围必须停止并重新批准。

## 6. 用户故事与独立验收

### US-1：普通用户从一个日常入口得到下一步（P0）

作为首次使用者，我希望初始化后只运行 `ai-sdlc run`，就能知道当前在什么阶段、结果是什么、下一步做什么、
是否有阻断以及当前最相关的规则。

**独立验收**：在未初始化、open gate、正常完成、halt 四个 fixture 上执行真实 CLI，五项标题和优先级稳定，
Next 最多一项，rules 最多两项，exit code 与主线基线一致。

### US-2：存量操作者保留详细诊断与自动化（P0）

作为已有脚本/运维使用者，我希望默认界面变短，但仍能获取原完整 status 和 JSON，不需要迁移高级命令。

**独立验收**：同一 fixture 的变更前默认 status 与变更后 `status --details` 关键行一致；`status --json` 深比较
shape/值语义且命令前后工作树无新写入；所有高级命令的 `--help` 和代表性调用仍可达。

### US-3：维护者不再为入口优化重建治理系统（P0）

作为框架维护者，我希望单入口只是既有真值的展示投影，避免辅助实现和测试再次超过核心价值。

**独立验收**：diff 中没有新持久化文件/schema/config/命令组/路由器；新增内部投影只有 run/status 两个消费者，
且删除任一消费者即可连同投影原子回退。

## 7. 成功标准

- **SC-220-001**：普通用户新项目 E2E 只使用 `init` 和 `run`，即可获得可信 Result/Next，且无需手动运行
  `adapter status` 或 `run --dry-run` 排查入口。
- **SC-220-002**：`run` 的五项摘要在正常、open gate、preflight blocker、halt 路径全部有 characterization/RED
  和 GREEN；Next ≤1、Blockers ≤3、Applicable Rules ≤2。
- **SC-220-003**：默认根帮助从 27 个可见入口收敛到 §3.4 六个；18 个高级组和四个隐藏直接命令仍可调用。
- **SC-220-004**：`status --details` 保留旧详细终端语义；`status --json` 兼容测试、只读测试和既有 status 回归
  全部通过。
- **SC-220-005**：不存在第二状态聚合器、持久化对象、命令注册表、五 Loop router 或无消费者抽象。
- **SC-220-006**：README、用户指引、adapter guidance、CLI help 与 runtime 术语一致；不把建议写成已落地事实。
- **SC-220-007**：定向测试、全量 pytest、Ruff、constraints、manifest、三平台 required checks 和 exact-head
  独立 review 通过后才可合并。

## 8. ROI、预算与停止条件

| 切片 | 用户价值 | 预计投入 | ROI 决策 |
|---|---:|---:|---|
| P2A：run/status 默认摘要 + details 迁移桥 | 9.0/10 | 2–3 人日 | **P0，必须先做** |
| P2B：默认 help 六入口 + README 高级索引 | 7.5/10 | 1–2 人日 | **P1，P2A 稳定且仍在预算内才做** |
| 验证/文档/跨平台/评审 | 8.5/10 | 1 人日 | 必需交付成本 |
| 总计 | 9.0/10 | 4–6 人日 | 预计 ROI 1.5 |

停止/降级条件：

1. 需要删除/重命名高级命令、改变 JSON 或 exit contract：停止，转 `needs_user`。
2. 需要第二状态聚合器、持久化 summary、完整 predecessor-chain router 或新规则引擎：拒绝；回到既有
   checkpoint/Loop/status truth 的纯展示。
3. 单一投影模块预计超过 180 行、P2A 超过 3 人日或总投入预计超过 6 人日：先只交付 run 五项摘要和
   status `--details`，P2B help 隐藏单独再评估。
4. `run_cmd.py` 抽取不能被 run/status 复用或不能独立测试：不抽取。
5. 两轮定向对抗整改仍出现同类范围扩张：本 WI No-Go，不继续磨细枝末节。

回退方式：P2A、P2B 分为可独立 revert 的实现切片；隐藏命令只需恢复 Typer registration 的 `hidden` 标志，
摘要只需撤回内部投影和两个调用点，不涉及数据迁移。

---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
