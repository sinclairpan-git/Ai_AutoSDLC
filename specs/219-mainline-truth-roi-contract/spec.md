# 产品需求文档：主线真值复位与轻量 ROI 合同

**功能编号**：`219-mainline-truth-roi-contract`
**创建日期**：2026-08-25
**状态**：formal design review candidate
**类型**：mainline truth maintenance + delivery contract optimization
**冻结基线**：`origin/main@762527466119dde127d7488b73d5592e44afaaa6`（`v0.9.7`）

## 1. 问题与用户价值

`v0.9.7` 已发布并明确关闭 WI196 减重路线，但 fresh-main 仍保留上一轮关闭过程的活动指针：

- `.ai-sdlc/state/codex-handoff.md` 仍要求合并已经进入主线的 PR 173；
- `.ai-sdlc/state/checkpoint.yml` 的父 feature 仍是已 No-Go 的 WI204，linked WI 仍是已关闭的 WI218；
- fresh-main `ai-sdlc status --json` 把 WI204 报为 `branch_only_implemented`，并返回
  `BLOCK_CODE_PREPARE_TASKS`，要求继续一个已经结束的减重候选；
- 同一次 status 的 Program Truth 为 `fresh`，两个 release target 均 `ready`，说明问题集中在活动指针与
  continuity，而不是重建新的 truth ledger。

在本 WI 通过正式 `workitem link` 关联 WI219 后，checkpoint 已保存
`linked_wi_id=219-mainline-truth-roi-contract`，已有 canonical resolver
`active_work_item_id(checkpoint)` 也返回 WI219；但 readiness/status 与 execute authorization 仍各自直接读取
历史 `checkpoint.feature.id/spec_dir`，继续返回 WI204。这证明问题不是 link 写入失败，而是两个消费面绕过
既有 linked-first 语义。

同时，当前 formal work item 模板没有要求在编码前说明用户收益、最小替代方案、总投入和退出条件。
这使得模型可能在对抗修复中持续增加支撑、证明和治理实现，却没有显式比较投入产出。

本项要恢复“当前主线下一步”的可信度，并把 ROI 思考嵌入现有规格入口；它不建立新的治理运行时，也不
重新启动减重专项。

## 2. 目标与非目标

### 2.1 P0 目标

1. fresh-main 的 checkpoint、handoff、resume 和 status 对当前工作项给出一致、可恢复的下一步，不再要求
   继续 WI204、WI218 或 PR 173。
2. 保留现有 `workitem link`、handoff 和 checkpoint/reconcile 写入合同；以一个纯解析语义修正 readiness 与
   execute authorization 的消费偏差，不修改状态机或历史 checkpoint 身份。
3. 两套 canonical spec 模板都提供同一份轻量 ROI 与实现边界提示：普通 stage/spec 模板和
   `workitem init` direct-formal 模板。
4. ROI 提示保留模型自主选择方案的能力；LOC、支撑/核心比例、调用方数量只能触发说明，不能单独阻断。
5. 现有 work item 无需回填，消费项目不会因为缺少新段落而收到 blocker。

### 2.2 明确非目标

- 不实现 Diff-local Lean Advisory；它属于后续独立 P1。
- 不修改 Local PR Review 的 finding、waiver、close 或 provider 运行时。
- 不新增 `roi`、`lean`、`review` 命令，不新增 schema、状态、ledger、certificate、receipt 或 authority。
- 不在 link 时改写 `checkpoint.feature`；它继续保存历史 feature/branch/stage 身份。
- 不重启 WI196，不创建新的减重工作项，不重构 `ProgramService`、`program_cmd.py` 或 `run_cmd.py`。
- 不复制参赛版的模块、测试或历史，只借鉴已经验证的行为边界。
- 不清理历史 specs、旧 branch/worktree 或发布记录。
- 不在本项发布新版本、tag 或 Release。

## 3. 方案比较与冻结决策

| 方案 | 做法 | 收益 | 成本/风险 | 决策 |
|---|---|---|---|---|
| A. 只改 handoff 文案 | 手工移除 PR 173 和 WI218 文案 | 最便宜 | `status` 仍可能指向 WI204，不能证明运行真值 | 拒绝 |
| B. 复用现有真值语义 + 定向消费修正 + 模板提示 | 保留 link/handoff/reconcile 写入；让 readiness/execute 复用 linked-first 解析；扩展 spec 模板和 characterization tests | 解决当前事实并防止后续投入失控；无新状态运行时 | 需要 linked/no-linked 前后对账 | **采用** |
| C. 新建 ROI/Lean 治理引擎 | 增加评分、例外、生命周期和 close 门禁 | 自动化程度高 | 重复既有 Loop，重演治理膨胀 | No-Go |

## 4. 冻结设计

### 4.1 Track A：fresh-main 真值复位

1. 在 `origin/main@76252746` 的隔离 worktree 记录以下只读基线：
   `handoff show`、`status --json`、`workitem truth-check`、`program truth audit`、checkpoint 与 resume pack。
2. formal 阶段只把当前 linked WI 更新为 WI219，并用 `uv run ai-sdlc handoff update` 记录真实目标、状态、
   命令和下一步；不得直接手写无法由 CLI 表达的新状态。
3. 已验证 link 后出现以下稳定分叉：canonical active id 为 WI219，而 readiness binding、active work-item dir
   与 execute authorization 均为 WI204；这是本项 P0 的直接根因，不再把它误判为新状态机需求。
4. 冻结一个最小 active binding 方案：
   - `active_work_item_id(checkpoint)` 继续作为唯一 ID 解析入口；
   - 在同一 context/state 模块增加至多一个无 I/O、无持久化的 spec-dir 纯解析 helper：存在非空 linked WI
     时返回 `specs/<linked_wi_id>`，否则原样返回历史 `feature.spec_dir`；
   - resume filesystem fallback、readiness/status 与 execute authorization 三个既有消费方复用该 helper；
   - linked target 缺失或不完整时 fail-closed，不得回退历史 feature 目录；无 linked WI 时行为完全不变。
5. 仅修正 active id/spec-dir 的选择，不改变 checkpoint writer、branch/stage、status JSON schema、错误码、
   task guard、truth classifier 或 execute 授权规则。
6. WI219 关闭时，continuity 必须更新为终态或明确的下一正式工作项，不能再次留下“待合并已合并 PR”。

允许的真值文件仅为：

- `.ai-sdlc/project/config/project-state.yaml`（work item 序号机械更新）；
- `.ai-sdlc/state/checkpoint.yml`（仅通过现有 CLI 更新 linked WI/plan）；
- `.ai-sdlc/state/codex-handoff.md`；
- `.ai-sdlc/state/resume-pack.yaml`（仅由现有 continuity 入口更新时）；
- `.ai-sdlc/work-items/219-mainline-truth-roi-contract/codex-handoff.md`（如 CLI 生成）；
- `program-manifest.yaml`（`program truth sync` 机械结果）；
- `tests/integration/test_repo_program_manifest.py`（只允许把 root inventory/close tuple 机械更新为 WI219 formal
  层数；不得放宽完整性、unmapped、capability 或 release 断言）；
- 当前 adapter canonical 文件（仅框架入口机械刷新）。

允许的 Track A 产品/测试文件仅为：

- `src/ai_sdlc/context/state.py`；
- `src/ai_sdlc/telemetry/readiness.py`；
- `src/ai_sdlc/core/execute_authorization.py`；
- `tests/unit/test_context_state.py`；
- `tests/unit/test_telemetry_readiness.py`；
- `tests/unit/test_execute_authorization.py`；
- `tests/integration/test_cli_status.py` 或 `tests/integration/test_cli_workitem_link.py` 二选一，只有 unit 无法证明
  真实 CLI link→status 闭环时才允许。

不得修改 workitem link writer、Runner、ProgramService、status 展示格式或 checkpoint schema。产品净新增目标
为 30 LOC 以内、定向测试新增目标为 150 LOC 以内；它们是 re-review 信号，不是脱离风险与兼容性的机械
blocker。若必须超出，应先证明现有 helper 无法承载并重新审阅设计，不得边写边扩 scope。

### 4.2 Track B：轻量 ROI 与实现边界

以下字段加入 `templates/spec-template.md` 与 `src/ai_sdlc/templates/spec.md.j2`，语义必须一致：

1. **用户可观察收益或可复现风险**：不能只写“减少 LOC”或“更优雅”。
2. **现状证据**：命令、失败样例、真实重复路径或兼容合同。
3. **最小方案与备选方案**：说明为什么不采用更小或现有承载方式。
4. **总投入**：产品、测试/harness、CI、评审、迁移和长期维护一起估算。
5. **范围与退出条件**：新增公共面、依赖、持久化状态及回退/删除触发器。
6. **决策**：`implement`、`defer`、`needs-user` 或 `not-applicable`，附一段理由。

合同解释：

- 对微小修复或不适用事项允许一行 `not-applicable` 理由，不强迫制作评分表。
- 400/50、辅助代码大于核心、新公共抽象少于三个调用方等仅是风险信号。
- 只有未经授权的范围扩展、缺失可执行证据、可复现安全/隐私/数据/兼容/回归问题能够成为 blocker。
- 安全、兼容、迁移、恢复和外部协议实现可以合理超过一般支撑比例，但必须说明必要性和退出条件。
- 本项不新增解析器或 constraint blocker；模板内容供模型和现有 reviewer 使用。

允许的产品/测试文件仅为：

- `templates/spec-template.md`；
- `src/ai_sdlc/templates/spec.md.j2`；
- `tests/unit/test_workitem_scaffold.py`；
- 与 `spec.md.j2` 已有渲染路径直接对应的一个既有测试文件（只有覆盖缺口被证明时才允许）。

`src/ai_sdlc/core/workitem_scaffold.py` 只有在模板无法无代码变更生成该段落时才允许最小修改；不得增加
模型、Enum、持久化字段或公共 API。

## 5. 功能需求

- **FR-219-001**：formal 基线必须保留 origin/main SHA、tag、handoff/status/checkpoint 的可复现证据。
- **FR-219-002**：checkpoint linked WI 和 continuity 必须通过现有 CLI 更新，不得手写新的状态语义。
- **FR-219-003**：WI219 活动期间，正常 status 不得继续把 WI204/WI218 作为下一可执行工作项。
- **FR-219-004**：readiness/status、execute authorization 与 resume 必须按同一 linked-first active id/spec-dir
  语义解析；不得从 linked WI 静默回退历史 feature。
- **FR-219-005**：两套 spec 模板必须包含 §4.2 六项，并保持语义一致。
- **FR-219-006**：direct-formal scaffold 的新规格必须出现 ROI 段落，且既有 parser-friendly 结构不变。
- **FR-219-007**：既有规格和消费项目无需回填；`verify constraints` 不得因缺少 ROI 段落新增 blocker。
- **FR-219-008**：不得新增治理命令、工件类型、生命周期、评分或第二套状态机。
- **FR-219-009**：formal、实现和测试必须遵守 §4 的精确允许范围；若证据要求超出范围，先停止并重新评审，
  不得在本项顺手扩展状态机或治理面。

## 6. 用户故事与验收场景

### US-1：维护者从已发布主线获得真实下一步（P0）

作为框架维护者，我希望 fresh-main 不再让我继续已经关闭的 WI 或 PR，以便下一项特性从可信基线开始。

**独立验收**：构造历史 feature=WI204、linked=WI219 且两份 specs 同时存在的 checkpoint；复位后
readiness/status、execute authorization、resume 和 handoff 都选择 WI219，没有 WI204、WI218、PR 173 的
可执行指令，Program Truth 仍为 fresh。无 linked fixture 继续使用原 `feature.spec_dir`。

### US-2：模型在编码前比较价值与总投入（P0）

作为需求、开发或测试角色，我希望新规格在实现前说明收益、最小方案、总成本和退出条件，避免评审把
细枝末节扩张成比核心特性更大的实现。

**独立验收**：两个正式入口生成的新 spec 都包含 §4.2 六项；填写 `not-applicable` 不会触发新门禁。

### US-3：存量项目保持兼容（P0）

作为已有 AI-SDLC 项目维护者，我希望升级后不用批量改写历史 specs，也不会因为新模板提示而被阻断。

**独立验收**：现有 template/scaffold/constraints 测试保持通过，历史规格不发生机械回填。

## 7. 成功标准

- **SC-219-001**：fresh-main 基线明确复现当前 WI204 `branch_only_implemented` 与陈旧 PR 173 handoff。
- **SC-219-002**：使用现有 link/handoff 入口后，canonical resolver、branch lifecycle、workitem diagnostics、
  execute authorization、resume 与 handoff 的 active WI 均为 WI219；任何一个仍指向 WI204 都算失败。
- **SC-219-003**：Program Truth 同步/审计保持 fresh，release targets 继续 ready，source inventory 无新增
  unmapped source。
- **SC-219-004**：`workitem init` 新生成的 `spec.md` 含 §4.2 六项；相关单元测试精确验证。
- **SC-219-005**：普通 stage/spec 模板与 direct-formal 模板在 ROI 语义上无漂移。
- **SC-219-006**：未新增命令、schema、状态、ledger、certificate、receipt、waiver 或 close 权限。
- **SC-219-007**：状态/handoff/checkpoint targeted tests、template/scaffold tests、Ruff、constraints、
  program truth audit 与 diff-check 全绿。
- **SC-219-008**：实现 diff 不修改 ProgramService、Runner、status schema/展示、PR Review runtime、checkpoint
  writer 或历史 specs；不创建新的减重 work item。

## 8. ROI 与停止条件

| 项目 | 冻结值 |
|---|---|
| 用户价值 | 恢复下一步可信度；让未来每项实现显式比较总投入 |
| 预计投入 | formal 0.5–1 人日；active binding 修正 0.5–1 人日；模板与验收 0.5–1 人日 |
| 最小方案 | 现有 link/handoff 写入 + 一个共享纯解析 helper + 两个消费面修正 + 两份现有 spec 模板提示 |
| 主要风险 | 模板重复、把 advisory 误写成 blocker、顺手扩展状态机 |
| 停止条件 | 需要新状态机/新治理工件；需要修改 writer/schema/Runner/ProgramService；两轮定向修正仍无法统一 active WI |
| 回退 | 原子 revert 模板与真值更新；不影响历史 specs |

本项的成功不是新增一套 ROI 系统，而是以最小增量让正常开发在编码前回答正确的问题。
