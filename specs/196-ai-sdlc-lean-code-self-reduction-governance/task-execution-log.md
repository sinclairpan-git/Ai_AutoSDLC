# 任务执行日志：AI-SDLC 精简代码治理与框架自身减重计划

**功能编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**创建日期**：2026-07-12
**状态**：双 Agent 对抗评审中

## 1. 归档规则

- 本文件只记录 Work Item 196 治理总项；后续产品减重使用各自子工作项日志。
- 每批必须记录范围、命令、结果、风险、回退和任务同步状态。
- 本工作项不得修改 `src/ai_sdlc/`、`tests/`、runtime rules、provider 或 workflow。
- 代码/功能实现不得以“完善计划”为由混入本分支。

## 2. Batch 2026-07-12-001：独立分支、基线与 canonical scaffold

### 2.1 范围

- 覆盖任务：T11、T12。
- 基线 revision：`c0f333c82c6f096ea8e74e57378eb7d7368f276c`。
- 独立 worktree：`.worktrees/196-lean-code-self-reduction-governance`。
- 独立分支：`feature/196-ai-sdlc-lean-code-self-reduction-governance-docs`。

### 2.2 执行命令与结果

- `git worktree add .worktrees/196-lean-code-self-reduction-governance -b codex/196-lean-code-self-reduction-governance main`
  - 结果：成功创建隔离 worktree；随后因 canonical `workitem init` 分支前置重命名为 `feature/196-ai-sdlc-lean-code-self-reduction-governance-docs`。
- `uv sync --frozen`
  - 结果：成功创建 Python 3.11.15 虚拟环境并按锁文件安装依赖。
- `uv run pytest`
  - 结果：`3145 passed, 3 skipped in 443.28s`。
- `uv run ai-sdlc workitem init ...`
  - 首次结果：adapter hook 改写 `.cursor/rules/ai-sdlc.mdc`，与 workitem init 的 clean-tree preflight 冲突，命令被安全阻断。
  - 处置：用 `apply_patch` 恢复 adapter 与测试触发的 resume-pack 路径副作用；未提交或 stash 无关变化。
  - 第二次结果：使用仓库集成测试同样的 `CliRunner + patch(run_ide_adapter_if_initialized)` 方式，只抑制无关 adapter hook，canonical branch preflight、scaffolder 和 manifest sync 完整执行；四件套创建成功，`program-manifest.yaml` 登记成功。

### 2.3 基线事实

- 产品 Python：215 文件、107,482 行；61 文件超过 400 行，51 文件超过 500 行，15 文件不少于 1,000 行。
- 产品函数：3,348 个；357 个超过 50 行，159 个不少于 100 行。
- 测试 Python：189 文件、109,872 行；55 文件超过 400 行，21 文件不少于 1,000 行。
- 静态结构重复只作为工作包候选信号，不能直接视为可删除代码；任何删除仍需 Golden/differential evidence。

### 2.4 风险与决策

- 决策 D-001：不绕过 docs branch preflight；按 CLI 接受的 `feature/<wi>-docs` 命名分支。
- 决策 D-002：不把 adapter 自动升级混入本治理项目。
- 决策 D-003：本工作项只创建治理四件套，不修改产品代码。
- 风险 R-001：全量测试会重写 root-bound `resume-pack.yaml` 绝对路径；每次验证后必须检查并恢复非项目副作用。
- 风险 R-002：CLI adapter hook 与 clean-tree preflight 存在顺序冲突；本工作项只记录现象，不顺带修复。
- 风险 R-003：checkpoint 通过 `linked_wi_id` 关联到 196 后，handoff CLI 仍从旧 `feature=189` 派生 resume-pack 工作集；本分支保留 checkpoint 历史 feature/stage，只将 resume-pack 的当前 spec/plan/tasks/branch 指针纠正到 196。

### 2.5 任务同步

- T11：已完成。
- T12：已完成；基线统计与全量测试证据均已复核。
- 是否进入产品实现：否。

## 3. Batch 2026-07-12-002：原则、兼容契约与路线图

### 3.1 范围

- 覆盖任务：T21、T22、T23、T31、T32、T33。
- 改动：将 scaffold 占位内容重写为 Work Item 196 专用治理规范。

### 3.2 产出（首版，已由 Batch 2026-07-12-004 修订）

- `spec.md`：LP-01～LP-12、CC-01～CC-08、L1～L4、FR-001～FR-018、成功标准和冻结决策。
- `plan.md`：首版 WP-01～WP-08；混责问题已在首轮对抗评审后重构。
- `tasks.md`：docs-only 路径约束、四批治理任务和需求追踪矩阵。

### 3.3 当时状态（已失效）

- 文档编写：完成。
- 占位符自审：待执行。
- program truth / handoff：待同步。
- constraints / diff-check：待执行。
- 独立只读评审：待执行。
- 原“用户审核”路径已被用户明确改为双 Agent 对抗评审。

## 4. Batch 2026-07-12-003：自审、关联与提交前验证

### 4.1 覆盖任务

- T41、T42；当时 T43 仍指向用户审核，现已由双 Agent gate 替代。

### 4.2 命令与结果

- 文档契约脚本：当时版本 LP=12、CC=8、FR=18、SC=8，结果 PASS；后续规格变更使该证据失效，最终树必须重跑。
- `git diff --check`：PASS。
- 产品路径白名单检查：`src/ai_sdlc/`、`tests/`、`rules/`、`providers/`、`.github/workflows/` 无变更。
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`。
- `workitem plan-check --wi ...`：不适用；196 不引用外部 `related_plan`，canonical plan 即本目录 `plan.md`。
- 提交前 `workitem truth-check --wi ...`：按预期返回未在 HEAD 找到四件套；该命令只读取 revision，不读取未提交文件，提交后必须重跑。
- `workitem link`：checkpoint 的 `linked_wi_id` / `linked_plan_uri` 已关联到 196。
- `handoff update`：canonical 与 scoped handoff 已生成；resume-pack 的旧 feature 派生指针已纠正为 196。
- 提交后 `workitem truth-check --wi ...`：PASS；HEAD `4b572c28` 中四件套完整，分支相对 main 为 ahead 2 / behind 0，分类为 `branch_only_implemented`。
- `program truth sync --execute --yes`：成功写入 `program-manifest.yaml`；196 的 spec/plan/tasks/execution/close inventory 已登记，snapshot state 为 `migration_pending`。

### 4.3 自审结论

- 规格覆盖：LP、CC、FR、SC 均有任务或验证映射。
- 占位符：扫描未发现实际占位内容；`SC-001` 中只保留机器检查的禁止项定义。
- 范围：保持 docs-only，没有产品实现。
- 兼容：没有删除或改变公共功能。
- 当前结论：允许提交治理基线；提交后继续 revision truth/program truth 验证。

### 4.4 Program Truth 外部风险

- `frontend-mainline-delivery` audit 因既有 `frontend_inheritance:generation` / `frontend_inheritance:quality` 阻断。
- `agent-adapter-verified-host-ingress` audit 因既有 `adapter_canonical_consumption:unverified` 阻断。
- source inventory 为 1008/1041 mapped，包含历史 release/source 映射缺口。
- 以上均不由 Work Item 196 引入；当前 docs-only 分支不修改运行时，后续统一登记为 GAP-09～GAP-11，并分别由独立子工作项修复。196 的四件套映射已 materialized。

## 5. Batch 2026-07-12-004：缺口与减重统一、双 Agent 首轮评审

### 5.1 方向变更

- 用户要求将框架缺口与自身减重列入同一套原则、计划和任务分解，并在后续独立子项中修复。
- 用户不承担四件套逐条评审；两个本地独立只读 Agent 分别从兼容安全和精简效率维度循环评审。
- 只有两个 Agent 对同一 review target hash 明确 PASS，才允许启动首个实现子项；L4 变更仍需用户批准。

### 5.2 首轮评审目标与结论

- 哈希算法：对 `spec.md`、`plan.md`、`tasks.md` 的 SHA-256 清单排序后再次 SHA-256。
- 首轮 target hash：`7eccba7131917147b3eec7dceefda84f9396dfe58df00fdafd5c8f26d548027d`。
- Agent A：`compat_safety_review`；维度为兼容、安全、回退和治理状态；结论 `FAIL`。
- Agent B：`lean_efficiency_review`；维度为 YAGNI、减重力度、量化预算和关键路径；结论 `FAIL`。

### 5.3 Findings 处置

| Finding | 核验 | 处置 |
|---|---|---|
| Golden 与首个 L2 基础包循环依赖 | 成立 | GAP-07/GAP-08 各自先写定向 characterization；通用 WP-01 分 A/B 两阶段，只约束后续减重包 |
| WP-00 混合多个独立领域 | 成立 | 取消 WP-00；T51/T52/T53A/T53B/T54 各自独立 WI/branch/PR |
| WP-08 混合门禁升级和两套旧实现删除 | 成立 | 取消 WP-08；门禁生命周期归 WP-02，旧实现删除分别归 WP-06/WP-07 |
| program truth 历史债务不应成为减重总前置 | 成立 | 拆为 GAP-09～GAP-11，仍统一跟踪和修复，但默认移出减重关键路径 |
| 缺少量化 reduction budget 和停止投资规则 | 成立 | 新增 RC-01～RC-10、保护成本/临时膨胀上限和逐包结果阈值 |
| WP-01 可能先造通用证据框架 | 成立 | 限定目标切片，reuse-first，禁止新通用 executor/DSL，纳入 RC-06 |
| WP-05 预设 Python → YAML/JSON | 成立 | 改为候选 go/no-go，格式不预设，预测不达标直接 No-Go |
| WP-06 被无关低风险任务串行阻塞 | 成立 | 只依赖 WP-01A 和有文件/契约重叠证据的子项 |
| 工作包缺进入/完成/停止/回退 | 成立 | `plan.md` 为每个缺陷与 WP 补齐统一合同 |
| Golden 只证明确定性、不证明等价 | 成立 | 补 transcript、配置优先级、副作用、allowlist、旧/新零差异与回退演练 |
| 双 Agent PASS 无同版本协议 | 成立 | 冻结三目标文件内容哈希和 review record schema；目标变化使双 PASS 失效 |
| handoff 仍指向用户审核/WP-01 | 成立 | 最终双 PASS 后用 canonical handoff CLI 同步为 GAP-07；同步前作为当前风险 |
| LP/FR/SC 重复、LP/CC 未直接追踪 | 成立 | FR 收敛为 12 条；追踪矩阵直接列 GAP/LP/CC/RC/FR/SC |
| 所有 WP 必须先关闭全部 program truth 债务 | 拒绝 | 会把无关历史清仓串入关键路径；改为逐切片 impact analysis，只有实际污染 fixture/入口/smoke 才阻断 |

### 5.4 修订结果

- 统一台账调整为 GAP-01～GAP-11，保留缺口与减重同一真值源。
- 路线图收敛为两个原子基础缺陷、WP-01～WP-07 和三个独立关联治理债务。
- `tasks.md` 使用 T51～T67 建立 gap → package → evidence 追踪，取消混责 T68。
- Reduction Contract 将 gate/harness/facade 新增代码计入成本，禁止用“结构准备”无限续投。

### 5.5 最终评审记录

- review target hash：三目标文件稳定后计算。
- 兼容安全 Agent：首轮 FAIL；最终 verdict 必须对新哈希重跑。
- 精简效率 Agent：首轮 FAIL；最终 verdict 必须对同一新哈希重跑。
- 最终结论：两个 Agent 对同一新哈希 PASS 后记录。

### 5.6 Gap Evidence Index

| Gap | 当前状态 | 责任子项 | 当前证据索引 | 关闭证据类型 |
|---|---|---|---|---|
| GAP-01 | planned | T62A～T62C | `spec.md` §3、`plan.md` §6 | gate report、warning/blocker fixtures |
| GAP-02 | planned | T61A/T61B | `spec.md` §5、`plan.md` §5 | surface manifest、Golden/DifferentialResult |
| GAP-03 | planned | T66 | `program_service.py`、基线统计 | domain/shadow/release/deletion receipts |
| GAP-04 | planned | T67 | `program_cmd.py`、33 命令、相似度审计 | family matrix、surface/shadow/deletion receipts |
| GAP-05 | planned | T63/T64 | `models/frontend_*`、`telemetry/*`、store/test 候选 | duplicate family before/after |
| GAP-06 | planned | T65 | 6 个 `build_p*_baseline` builder | consumer graph、Go/No-Go receipt |
| GAP-07 | closed | T51 / WI-197 | `specs/197-adapter-preflight-order/task-execution-log.md` §6.3～6.7、PR `#121`、merge `4802596f` | RED/GREEN、full/CI、双 Agent、Codex、mainline targeted/truth |
| GAP-08 | closed | T52 / WI-198 | `specs/198-linked-wi-resume/task-execution-log.md` §3～§8、PR `#122`、merge `68150d3f` | RED/GREEN、recover/handoff、双 Agent、Codex、mainline truth |
| GAP-09 | closed | T53A / WI-199 | PR `#123`、merge `208a34c8` | framework capability 与 consumer inheritance 分离、mainline truth |
| GAP-10 | closed | T53B / WI-200 | PR `#124`、merge `c737eda0` | repository capability 与 session consumption 分离、mainline truth |
| GAP-11 | closed | T54 / WI-201 | PR `#125`、merge `d19c8b7d` | inventory complete、unmapped=0、missing=0、mainline truth |

## 6. Batch 2026-07-12-005：第二轮评审与合同适用性修订

### 6.1 第二轮结论

- review target hash：`6c9b68eff0c2f259ad89a9493d10c418e3833b83bd8bd71225bc0bfafc32db5f`。
- `compat_safety_review`：`FAIL`。
- `lean_efficiency_review`：`FAIL`。
- 两个 Agent 均独立复算同一哈希后给出结论。

### 6.2 Findings 处置

| Finding | 核验 | 处置 |
|---|---|---|
| RC-01～RC-10 错误覆盖缺陷/truth/保护设施 | 成立 | 新增 NC-01～NC-06 和适用矩阵；缺陷/truth 不承担减重阈值，WP-01/02 只承担保护成本相关 RC |
| WP-01B 未成为候选 PR 强制门 | 成立 | T61A/T61B 改为候选 WI 内 embedded gate；Phase B 绑定 candidate hash，未通过不得 merge/close |
| truth 债务影响分析 fail-open | 成立 | 统一为 fail-closed；缺失/不确定默认阻断，只有肯定非影响证据才排除依赖 |
| WP 缺非目标/具体验证/evidence 约束 | 成立 | 各 WP 增加非目标；冻结最低全量命令、子 WI targeted command 要求与 evidence URI 模板 |
| L3 删除旧实现后无可用回退 | 成立 | 分为删旧前 route/facade 回切与删旧后 revert deletion PR + release rollback，两种均需 receipt |
| 结构切片可原样搬家通过 | 成立 | RC-04 增加 LOC/复杂度/依赖边/重复分支量化阈值；纯移动 No-Go |
| RC-06 漏算 test/fixture/Golden 维护成本 | 成立 | 产品、test、harness、normalizer LOC 合并计费，并限制 fixture 数和 snapshot 体积 |
| T51/T52 无依据串行 | 成立 | 改为两个独立首批子项，可独立或并行；两项关闭后汇合到 WP-01A |
| 哈希算法描述不够精确 | 成立 | `plan.md` 固定 worktree cwd、相对路径和精确复算命令 |

### 6.3 下一门禁

- 三目标文件变化已使第二轮 verdict 失效。
- 重新计算 target hash 后，两个原 Agent 必须进行第三轮同哈希复审。

## 7. Batch 2026-07-12-006：第三轮评审与最终兼容边界修订

### 7.1 第三轮结论

- review target hash：`dc63d2a1aada243409013782e4b07b36ca2136e431a11b02d810cb7f58b0cb1c`。
- `lean_efficiency_review`：`PASS`，未发现可操作问题。
- `compat_safety_review`：`FAIL`；因此精简 Agent 的 PASS 随目标变化失效。

### 7.2 Findings 处置

| Finding | 核验 | 处置 |
|---|---|---|
| RC 适用矩阵未让所有 WP 选择受影响 CC | 成立 | 所有 WP 增加 impact-selected CC；WP-02 强制 CC-01/02/03/05/07 和 versioned expected delta |
| RC-09 引用了子项不适用的 RC | 成立 | 改为只校验矩阵适用 RC-04～07，并检查是否使组合终态 RC-08 不可达 |
| 声称机器 execute gate 已存在但无实现入口 | 成立 | 明确分期：WP-02 blocking gate 前由两个本地只读 Agent fail-closed；落地后改为机器解析 |
| WP-05 No-Go 同时被写成完成与停止 | 成立 | 冻结 `cancelled_no_go`；只关闭候选评估，不计减重成果、不关闭 GAP-06 |

### 7.3 下一门禁

- 三目标文件变化使第三轮结论全部失效。
- 新 target hash 计算后，两个原 Agent 进行第四轮同哈希复审。

## 8. Batch 2026-07-13-007：第四轮评审与门禁收口

### 8.1 第四轮结论

- review target hash：`948fc85838378d117e8b6344af86f7c66368a38dfb67088f9bc4bb0d77cd45c8`。
- `compat_safety_review`：`FAIL`，2 个 WARNING。
- `lean_efficiency_review`：`FAIL`，2 个 WARNING。

### 8.2 Findings 处置

| Finding | 核验 | 处置 |
|---|---|---|
| T62C 未明确实现合同解析/execute blocker | 成立 | 纳入 WP-02/T62C 范围、完成条件和关闭证据 |
| WP-02 漏 CC-06，T62B/C 漏 RC 追踪 | 成立 | 强制 CC-01/02/03/05/06/07；RC 追踪覆盖 T62A～T62C |
| 六个 baseline 均 No-Go 后无聚合终态 | 成立 | 冻结有限候选集；新增 `closed_no_viable_reduction`，不计减重成果，实质变化才可重开 |
| 机器门前所有 L1/L2 强制双 Agent 过重 | 成立 | 普通 L1/L2 使用一个独立合同 reviewer；仅 L3 或 CC-05/CC-06 高风险项使用双 Agent |

### 8.3 下一门禁

- 三目标文件变化使第四轮结论失效。
- 新 target hash 计算后，两个原 Agent 进行第五轮同哈希复审。

## 9. Batch 2026-07-13-008：第五轮评审与双规则族生命周期修订

### 9.1 第五轮结论

- review target hash：`c47dfc7e36e3623335ec731c60969bc12aa5a7e8064d72d875d6c83cda3463ed`。
- `compat_safety_review`：`FAIL`，1 个 BLOCKER。
- `lean_efficiency_review`：`FAIL`，1 个 WARNING。

### 9.2 Findings 处置

| Finding | 核验 | 处置 |
|---|---|---|
| T62C 回退会形成 admission 空窗 | 成立 | 代码指标与合同 admission 使用独立状态/开关；机器门非 `active + verified` 自动恢复风险分层 reviewer |
| 合同解析到 T62C 才首次出现并直接阻断 | 成立 | 合同规则与代码指标共用 T62A report、T62B warning、T62C blocking 生命周期，分别校准和降级 |

### 9.3 下一门禁

- 三目标文件变化使第五轮结论失效。
- 新 target hash 计算后，两个原 Agent 进行第六轮同哈希复审。

## 10. Batch 2026-07-13-009：第六轮同哈希双 PASS

### 10.1 Review Target

- target：`spec.md + plan.md + tasks.md`。
- target hash：`dcd2231b3a075b7ce0d5afe51e1129a0e4356662a7f61f326cb3c7d7c472e67b`。
- 复算时间：`2026-07-13T04:52:50Z`。

### 10.2 Final Review Records

| agent_id | dimension | reviewed_at | findings | disposition | verdict | evidence_uri |
|---|---|---|---|---|---|---|
| `compat_safety_review` / Chandrasekhar | 兼容、安全、回退、状态 | `2026-07-13T04:52:50Z` | 未发现可操作问题 | 无待处置项 | `PASS` | 本任务第六轮 Agent verdict；target hash 如上 |
| `lean_efficiency_review` / Mencius | YAGNI、减重力度、预算、关键路径 | `2026-07-13T04:52:50Z` | 未发现可操作问题 | 无待处置项 | `PASS` | 本任务第六轮 Agent verdict；target hash 如上 |

### 10.3 收敛结论

- 两个 Agent 对同一目标哈希均明确 `VERDICT: PASS`。
- T33 完成；治理文档不再等待用户逐条评审。
- 后续只追加执行日志、truth 和 handoff，不修改 review target；如目标三文件变化，双 PASS 自动失效并重新评审。

## 11. Batch 2026-07-13-010：文档减重删除说明

- `uv run ai-sdlc verify constraints` 首次执行被 comment preservation policy 阻断；根因是该策略把 Markdown 标题和加粗标签识别为说明性注释，而本次对抗评审将首版长结构收敛为更短的统一合同结构。
- removed comment reason: specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md 的首版标题、目标、产物、限制、验证和回退内容没有静默丢失，而是合并进新版依赖图、NC/CC/RC 合同、WP-01～WP-07 原子包和停止/回退总则；被移除内容摘要 token 为 `*日期**：2026-0`, `#3.宪章检查`, `#4.文档结构`, `#5.治理架构`, `#6.基线与度量模型`, `##6.1基线维度`, `##6.2评价规则`, `#7.工作包路线图`, `##WP-01：兼容观测`, `*目标**：建立后续减重`, `*产物**：`, `*进入条件**：196通`, `*完成条件**：同一re`, `*回退**：删除新增观测`, `##WP-02：Lean`, `*目标**：机器化采集规`, `*产物**：结构化报告、`, `*完成条件**：在本仓库`, `*回退**：关闭gate`, `##WP-03：低风险h`, `*目标**：处理完全相同`, `*限制**：不改变公共模`, `*验证**：定向测试、G`, `*回退**：按重复族逐c`, `##WP-04：Loop`, `*目标**：复用loop`, `*限制**：不同loop`, `*验证**：旧/新sto`, `*回退**：保留原sto`, `##WP-05：静态ba`, `*目标**：将大段静态P`, `*限制**：字段、顺序语`, `*验证**：序列化快照、`, `*回退**：loader`, `##WP-06：Prog`, `*目标**：将manif`, `*限制**：不删除fac`, `*验证**：每移动一个领`, `*回退**：facade`, `##WP-07：Prog`, `*目标**：将经过证明的`, `*限制**：所有现有33`, `*切换顺序**：`, `##WP-08：增量门禁`, `*目标**：将repor`, `*回退**：恢复兼容ad`, `##阶段A：Report`, `##阶段B：Change`, `#10.停止条件`。
- removed comment reason: specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md 的首版范围、分节式 LP、用户故事和边界章节已合并进统一问题台账、紧凑 LP 列表、CC/NC/RC 合同、FR/SC 与冻结决策；被移除内容摘要 token 为 `#3.范围`, `##3.2本工作项明确不`, `##LP-02：只删除已`, `##LP-03：不为未来`, `##LP-04：数据优先`, `##LP-05：公共入口`, `##LP-06：单一真值`, `##LP-07：先收敛低`, `##LP-08：测试是兼`, `##LP-09：增量基线`, `##LP-10：每批净减`, `##LP-11：禁止减重`, `##LP-12：删除延迟`, `#5.公共兼容冻结契约`, `#6.风险模型`, `#7.用户故事与验收场景`, `##US-01：冻结可执`, `##US-02：冻结现有`, `##US-03：建立增量`, `*独立测试**：路线图中`, `##US-05：用框架自`, `*独立测试**：Lean`, `#11.边界情况`, `#12.冻结决策`。
- removed comment reason: specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md 删除首版重复日期标签 `*日期**：2026-0`，日期仍由 spec 创建日期、Git revision 和 execution log batch 时间提供，不影响任务语义或审计追踪。
- 该批只补删除理由和被删摘要，不修改第六轮 review target 三文件，因此双 PASS 哈希保持不变。

## 12. Batch 2026-07-13-011：最终验证

- `uv run pytest tests/integration/test_repo_program_manifest.py tests/integration/test_cli_handoff.py tests/integration/test_cli_workitem_truth_check.py tests/unit/test_verify_constraints.py -q`：`156 passed in 11.07s`。
- YAML 解析：`program-manifest.yaml`、project state、checkpoint、resume-pack 全部 PASS。
- 文档合同：GAP=11、LP=12、NC=6、CC=8、RC=10、FR=12、SC=8、WP=7，任务目录与追踪矩阵 PASS。
- review target hash：`dcd2231b3a075b7ce0d5afe51e1129a0e4356662a7f61f326cb3c7d7c472e67b`，与第六轮两个 Agent verdict 一致。
- 路径白名单：相对 main 与 working tree 均无 `src/ai_sdlc/`、`tests/`、`rules/`、`providers/`、`.github/workflows/` 变更。
- `git diff --check`：PASS。
- `uv run ai-sdlc verify constraints`：首次因本次 Markdown 结构减重缺删除说明而 BLOCKED；Batch 11 补充逐文件理由和摘要后重跑为 `no BLOCKERs`。
- `program truth sync --execute --yes`：当前 snapshot 无新增 manifest diff；既有 GAP-09～GAP-11 外部债务保持原值，不伪造关闭。

## 13. Batch 2026-07-13-012：PR Codex Review 修订

- PR：`#120`；reviewed commit：`04e9364e286d198e8d2140e0057de7f0570ecf73`。
- Codex finding：`spec.md` 将 program truth 证据硬编码为旧 snapshot hash，和提交内 `program-manifest.yaml` 的最终 truth snapshot 不一致。
- 核验：成立。truth sync 会更新 `generated_at`、`repo_revision` 和 `snapshot_hash`，固定 hash 会让 GAP-09～GAP-11 证据在后续同步后立即陈旧。
- 处置：规范改为引用目标提交内 `truth_snapshot.repo_revision + generated_at + snapshot_hash` 三元组，并要求使用 `uv run ai-sdlc program truth audit` 复核；禁止在规范中硬编码动态 snapshot hash。
- 修订后 review target hash：`624f62bc07955866a592790d49395b8600ee26266c23980838d27399935735d6`。
- 原 `dcd223...` 双 PASS 因 target 变化失效；必须由 Chandrasekhar 与 Mencius 对新哈希重新评审并双 PASS 后推送。

### 13.1 第七轮对抗评审

- `compat_safety_review` / Chandrasekhar：`FAIL`；要求把 audit 绑定到目标 commit，并冻结 `fresh`、可接受非 ready 状态和 fail-closed 条件。
- `lean_efficiency_review` / Mencius：`FAIL`；要求在 T43 提交后实际执行既有 audit，不新增工作包、脚本或 artifact。
- 两个 Agent 独立收敛到同一问题：仅替换动态引用仍不足以形成可执行的提交后门禁。

### 13.2 处置与第八轮目标

- `spec.md` 增加目标 commit/PR checkout 绑定、三元组/output/exit code 记录、`snapshot_state=fresh` 和非预期状态 fail-closed 规则。
- `tasks.md` 在 T43 增加提交后 audit；退出码 1 只有在非 ready 状态精确等于已登记 GAP-09～GAP-11 集合时才是 `PASS_WITH_REGISTERED_DEBT`。
- 本提交允许的 capability blocking refs 精确集合：`frontend_inheritance:generation`、`frontend_inheritance:quality`、`adapter_canonical_consumption:unverified`。
- 本提交允许的 GAP-11 source inventory 精确计数：`total=1041`、`mapped=1008`、`unmapped=33`、`missing=11`；validation error 不在允许集合内。
- 动态 truth 三元组不在版本化 execution log 中硬编码；目标 commit 的三元组、audit 输出和退出码只记录在对应 PR target evidence，目标提交内的 `program-manifest.yaml` 是复核真值源。旧 PR target 的三元组一律视为历史证据，不得用于后续 T43 判定。
- 第八轮 review target hash：`afddacf905876355b8c46725f6d82cf83daa556fc730199f0084ed5800a46cb3`。

### 13.3 第八轮同哈希双 PASS

| agent_id | dimension | findings | disposition | verdict | review_target_hash |
|---|---|---|---|---|---|
| `compat_safety_review` / Chandrasekhar | 兼容、安全、回退、状态与审计可证性 | 未发现可操作问题 | 第七轮 finding 已关闭 | `PASS` | `afddacf905876355b8c46725f6d82cf83daa556fc730199f0084ed5800a46cb3` |
| `lean_efficiency_review` / Mencius | YAGNI、减重力度、直接性、预算、关键路径与治理成本 | 未发现可操作问题 | 第七轮 finding 已关闭 | `PASS` | `afddacf905876355b8c46725f6d82cf83daa556fc730199f0084ed5800a46cb3` |

- 两位 Agent 独立复算的组合哈希一致；原 Codex finding 与第七轮共同 finding 均已闭环。
- 本轮只修改 audit 证据绑定与判定，不新增工作包、脚本、artifact 或运行时代码。

## 14. Batch 2026-07-13-013：PR Codex Review 连续性状态修订

- reviewed commit：`3414a2aaaf27b40067f56f46475c3bfdf5395733`。
- Codex finding：checkpoint 的 `linked_wi_id` 已指向 WI-196，但 `feature.id/spec_dir/branch` 仍指向 WI-189；resume-pack 重建会把已纠正路径覆盖回 WI-189。
- 核验：成立。root resume-pack 虽正确，但 scoped resume-pack 由旧 checkpoint 派生，当前提交状态不能稳定重建。
- 处置：将 checkpoint feature 五字段统一绑定 WI-196 和当前分支，再通过 `uv run ai-sdlc handoff update` 重建 canonical/scoped resume-pack；重建后路径和分支必须保持 WI-196。
- 关联 branch/worktree disposition 计划：merge
- 当前批次 worktree disposition 状态：保留至 PR 合并完成
- 该修订只改变 continuity 状态与执行日志，不修改 `spec.md + plan.md + tasks.md`；第八轮双 PASS 哈希 `afddacf905876355b8c46725f6d82cf83daa556fc730199f0084ed5800a46cb3` 保持有效。

## 15. Batch 2026-07-13-014：GAP-07/T51 mainline 关闭与 GAP-08 启动

- WI-197 PR `#121` 在 Codex review 当前 HEAD 无问题、22 项 GitHub checks 全绿后 squash merge；merge commit 为 `4802596f9ef2fda8c27717c25d6760ed09136811`。
- `origin/main` 与 WI-197 已验收 branch tree hash 均为 `90da33d6ac6b0c911b2bf0ce91c8b04b90a12e04`，证明 squash 合并内容无漂移。
- mainline-equivalent targeted：`tests/integration/test_cli_workitem_init.py + tests/unit/test_cli_hooks.py + tests/unit/test_workitem_scaffold.py` → `26 passed in 11.79s`。
- mainline truth audit：snapshot `fresh`；inventory 保持 `1013/1046 mapped`、`33 unmapped`、`11 missing`，既有三个 frontend/adapter blocker 未扩大，预期 exit 1。
- GAP-07/T51 状态更新为 `closed`；权威实现/评审/回退证据位于 WI-197 execution log §6.3～6.7 与 PR `#121`。
- GAP-08/T52 进入独立 WI-198：`specs/198-linked-wi-resume/`；docs branch `feature/198-linked-wi-resume-docs`，runtime branch 预留 `codex/198-linked-wi-resume`。
- T51/T52 barrier 尚未关闭；只有 WI-198 独立 PR 合并并完成 mainline truth 后才允许进入 WP-01A。

## 16. Batch 2026-07-13-015：GAP-08/T52 mainline 关闭与 GAP-09 启动

- WI-198 PR `#122` 经 Codex review 修订、双 Agent 当前 HEAD 复审和 22 项 required checks 后 squash merge；merge commit 为 `68150d3f5ba128c0e4b44b11b13bc8ad60cc0d63`。
- branch 与 `origin/main` tree hash 均为 `6acaf28f22c6c59c4e751b5900387fd4478e1389`；mainline-equivalent focused tests 为 `94 passed in 34.44s`。
- mainline truth audit snapshot fresh；inventory 为 `1018/1051 mapped`、`33 unmapped`、`11 missing`，只保留 GAP-09～GAP-11 已登记 debt。
- GAP-08/T52 状态更新为 `closed`；权威实现、双 Agent、Codex finding 修订与回退证据位于 WI-198 execution log §3～§8 和 PR `#122`。
- T51/T52 barrier 已关闭。WP-01A 获得进入资格；统一路线当前选择先推进独立 WI-199 GAP-09/T53A，不把该选择解释为所有减重包的全局前置。
- WI-199 工作树：`.worktrees/199-frontend-inheritance-truth`；canonical branch：`feature/199-frontend-inheritance-truth-docs`。CLI 拒绝非 canonical docs branch 后已切换到要求的 branch 并完成 formal init/link。
- GAP-09 before truth：generation/quality handoff 均因 `frontend_solution_snapshot_missing` blocked；release capability 附加 `frontend_inheritance:generation` 与 `frontend_inheritance:quality`。
- 根因初判：`frontend-mainline-delivery` 的 16 个 carrier 全部显式为 `framework_capability`，release gate 却要求框架仓库具备消费项目 solution snapshot。WI-199 将在双 Agent 同哈希设计 PASS 后以 fail-closed 分类修复，不运行 frontend solution execute。

## 17. Batch 2026-07-13-016：GAP-09/T53A branch truth-ready

- WI-199 已完成实现与分层验证：定向/CLI status `399 passed`，全量 `3172 passed, 3 skipped`，Ruff、constraints、diff check PASS。
- 产品净新增 52 LOC，测试 raw additions 160；未新增模块、公共 API、依赖、config 或 schema。
- branch truth exact delta 仅移除 `frontend_inheritance:generation` 与 `frontend_inheritance:quality`；`frontend-mainline-delivery` 为 `audit=ready`，原始 handoff/status 仍保留 missing snapshot 的 blocked 诊断。
- GAP-10 保留 `adapter_canonical_consumption:unverified`；GAP-11 保留 `33 unmapped / 11 missing`。WI-199 五件套使 mapped/source 总数同步增加 5，不属于债务清仓。
- GAP-09 当前标记为 `branch truth-ready / PR-mainline pending`；只有 WI-199 PR 合并并在 `origin/main` 重跑证据后才更新为 closed。

## 18. Batch 2026-07-15-017：GAP-09～GAP-11 mainline 关闭与 sponsor receipt

- GAP-09/T53A：WI-199 经双审、Codex/CI 与 mainline smoke 后由 PR #123 squash merge；commit
  `208a34c82da0474a3cf51f3758934a188758b33d`。Framework capability 与 consumer inheritance
  fail-closed 语义分离，frontend release truth 不再含两个误报 blocker。
- GAP-10/T53B：WI-200 由 PR #124 squash merge；commit
  `c737eda056b2c86a6110ab32db237c417ee19a04`。Repository capability closure 与本机会话 canonical
  consumption admission 分离，后者仍按 runtime 环境独立 fail-closed。
- GAP-11/T54：WI-201 由 PR #125 squash merge；commit
  `d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`。33 个 unmapped 与 11 个 missing source 收敛为 0；
  inventory=`complete`。
- WI-203 / PR #126 / merge `75d3dda5ec8b45d0f9441058da889163d814b717` 冻结一个
  9-handler、预计净删除至少 1,501 LOC 的 WP-07 候选，以及总保护 claim≤353、candidate T61A/B≤180、
  WI-202 T62A≤170、reserve=3 不可借出的 sponsor receipt。该 receipt 只授权受限保护预算，不代表
  candidate 实现或删除已发生。
- 当前 mainline truth 为 source `1071/1071/0/0`、close `203/203`；GAP-07～GAP-11 均已有独立
  mainline evidence。父项仍未满足 RC-08，不得标记整体完成。

## 19. Batch 2026-07-15-018：WI-202 RC-06/RC-09 No-Go 与零残留处置

### 19.1 失败目标与纠偏

WI-202 最初尝试在 cap 170 内同时实现 WP-02 两个 T62A report-only 规则族。Round 1/2/3/5
formal 均双 FAIL；Round 4 在 verdict 前主动撤销；Round 6 target
`06d2764160f4ada12c86f3c8ab958b8fab154aca7203bc49eb751e7677635d2d` 也由 Pascal 与
Confucius 独立复算后双 FAIL。主要纠偏：不得用 fake Git、物理压行、场景名称、未闭合 parser，
也不得把 changed-code 与 contract admission 核心语义推迟到 T62B 来换取预算。

### 19.2 两套父合同完整 proof

两套 proof 都覆盖真实 Git、changed-code added/deleted/budget、changed Python 400/50、fixed
classification、required contract fields、固定 CC/RC、closed waiver、closed deterministic JSON、
无自由文本回显、invalid/non-project、zero-write 和 actual `verify_app`；所有新增函数≤50。

| proof | 设计 | core | CLI | tests | product | candidate | prior 后 | source-set SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| v6 | exact base/candidate 40hex、完整 object/containment edge | 223 | 28 | 178 | 251 | 429 | 431 | `aeb48490db13ea37708d328399381df442a1a6cf6fa23785189460b1ce8325d8` |
| v7 | 显式 base + exact HEAD、复用只读 Git、Git-object-only | 205 | 20 | 157 | 225 | 382 | 384 | `981ef703ea36b7d28140bf7ca3b32b36cbd0073bc5703ad3bb755cd5d9de837b` |

Source SHA：v6 core=`32f15140a22c9c4a938f003aafc9182958968c99bbbd27fa16e411b4524818c9`、
CLI=`d979caee23dbd55b97fdb84ad96baeaffef15b2b155ce110542781d9dd6b24e9`、
test=`846aa8b86b663cdf9661b702dfeade3d4daffd1a48f615d7ada95b662301041f`；v7
core=`16c0bbc2e87f641c1bcdd8366ab91bf73fa07f725380054f3597988618edb70c`、
CLI=`7de0cde5ea86434b4ea7bfa121f9ac7537eb04d38d20683019dee133081b178a`、
test=`1275d4cc5027278e3bf7ecdf40f0d1559cfaefaf9306077250935e0205dcdbe3`。固定环境复验 UTC
`2026-07-15T09:20:32Z`：两套均 `4 passed`，`ruff check` PASS，`ruff format --check` 为
`3 files already formatted`，zero-write PASS。V7 即使完全不计 tests，product 225 + prior 2 =227，
仍超过 cap 57；超限来自父合同职责，不是 formatter 或测试 setup。

### 19.3 RC-09 决策与双 Agent 策略统一

- RC-06：全部 product/test/harness/normalizer additions 必须合计计费，删除不抵扣；当前 sponsor
  为 WI-202 开放的 cap 精确为 170，candidate 的 180 不可自动转移。
- RC-09：继续压缩只能删除父合同语义、安全断言或证据，因此停止该候选；不创建产品代码、
  不激活 sponsor、不消费 unique key，effective claim=0。
- Confucius / 兼容安全 / `2026-07-15T09:17:55Z`：GO 仅限删除 WI-202 全部 source/state/truth，
  在父项留 No-Go 审计；独立 WI 会产生未获 claim 覆盖的 2 行 tests additions，并错误扩张
  `cancelled_no_go` 生命周期。
- Pascal / 精简效率 / `2026-07-15T09:24:46Z`：接受上述反例并撤回保留独立 WI 的建议；确认父日志
  足以防止重复投入，额外 source 只会违反停止投资目的。

最终处置：删除 `specs/202-lean-gate-report-only/**`、scoped handoff、manifest entry、checkpoint/
resume/handoff 引用和 truth tuple delta；不合入 spike/sidecar/sponsor/T61A 副本。GAP-01/T62A 保持
open，T62B/T62C 未开始；WP-02 涉及 CC-05/CC-06，FR-08 的两个独立 reviewer fallback 继续生效。
重启必须同时有足额新/替代 sponsor，以及重新冻结并同 hash 双 PASS 的父合同；不得复活 WI-202。

父文档 PR 的回退为 `git revert --no-edit <parent-no-go-audit-squash-sha>`。由于无 WI-202 runtime/
source/truth/claim，回退不需要清理命令、模块、测试或预算 ledger。

## 20. Batch 2026-07-15-019：父合同 current-truth 与 sponsor lifecycle 对账

首轮父合同正式复核目标为
`9684e07fa29cfeeb39dca1359d7aa40f0ab4c047449af4a5f2b3c4bad22d5e16`。Pascal（精简效率，
`2026-07-15T09:41:16Z`）与 Confucius（证据安全，`2026-07-15T09:41:25Z`）均独立复算一致并
判定 `FAIL`：formal 仍把已关闭的 GAP-07/08 写成待启动；WI-203 scoped continuity 仍要求恢复
WI-202；WI-196 handoff 的 Changed Files 仍是候选删除前的旧工作区快照。

处置：

- `spec.md + plan.md + tasks.md` 把 GAP-07/T51、GAP-08/T52 标为已关闭，绑定 WI-197/198、
  PR #121/#122 与 merge evidence；当前 continuation 改为 WI-196 的 T62A No-Go/restart contract。
- 不修改 WI-203 已冻结的 `spec.md + plan.md + tasks.md`；仅在其 summary、execution log 与 scoped
  handoff 对账 sponsor lifecycle：旧 WI-202 allocation effective claim=0 且不可复活/转移。
- 使用 canonical handoff CLI 刷新 WI-196 continuity，并以最终分支实际路径集合替换旧过程快照。

修订后的 formal review target 为
`923413a09d945cd211832734d7e1f527f21ba2f07f6c1b6e6f47409d078b005a`；旧哈希的两个 FAIL
只保留为审计历史，当前目标必须由两个 Agent 从零重新复核。

第二轮复核仍为双 `FAIL`：Pascal（`2026-07-15T09:50:14Z`）与 Confucius
（`2026-07-15T09:54:03Z`）均独立复算 `923413a0…005a`，共同指出 plan/tasks 仍把已关闭的
T53A/T53B/T54 表达成待推进硬依赖；Confucius 另以只读 truth surface 证明本批文档变化已使
deferred signal 从 6439 变为 6441，旧 handoff 的 fresh 声明失效。

再次处置：formal 将 GAP-09～GAP-11 明确为 WI-199～WI-201 已关闭，impact analysis 只承担
防回归职责；仅当对应 blocker 或 unmapped/missing source 再现时 fail-closed 并重开 GAP，不得
重复执行已关闭 T53A/T53B/T54。新 formal review target 为
`0b8ed80a245e8b87221098c752d88f2adfd6734f2b8bf722e86e164f73af91b7`。随后必须执行 terminal
truth sync/audit 并刷新 handoff；在 fresh 证据产生前不得沿用旧通过结论。

第三轮目标 `0b8ed80a245e8b87221098c752d88f2adfd6734f2b8bf722e86e164f73af91b7`
由 Pascal 在 `2026-07-15T10:04:09Z` 判定 `PASS`；Confucius 随后指出正式门禁仍允许已关闭的
GAP-09～GAP-11 以 `PASS_WITH_REGISTERED_DEBT` 解释 non-ready/exit 1，与“回归必须重开 GAP”
冲突，因此该轮最终为 `FAIL`，Pascal PASS 随目标变化失效。

处置：`spec.md` 与 `tasks.md` 删除 registered-debt 例外；当前交付唯一允许
`snapshot_state=fresh + state=ready + exit 0 + zero blocker`。任意 non-ready/非零/集合变化均
fail-closed；对应 truth 债务再现时返回 T41/T22 并重开 GAP。新 formal review target 为
`096f0feac07596b7aad1c30721a15a46ac29fb54c328ed77251be5473ec72e4b`。

第四轮由两名 Agent 严格从零、只读复核同一 formal hash，当前唯一有效 verdict 如下：

| Agent | 维度 | UTC | Findings | Disposition | Verdict |
|---|---|---|---|---|---|
| Pascal / `wi200_lean_design` | 精简设计、治理语义、任务可执行性 | `2026-07-15T10:16:42Z` | none | 独立 hash 一致；确认 GAP07～11 current truth、No-Go、预算隔离、T62/restart、13-path handoff 与 strict truth gate 全闭合 | `PASS` |
| Confucius / `wi200_proof_safety` | 证据安全、生命周期、零残留 | `2026-07-15T10:17:52Z` | none | 独立 hash 一致；确认 fresh+ready+exit0+zero blocker、WI202 zero residue/claim=0、FR08 fallback 与 manifest 静态证据闭合 | `PASS` |

两者均未运行会写 adapter/ProgramService 的命令，未修改文件。`spec.md + plan.md + tasks.md`
自此冻结；任一 target 文件变化会同时作废上述两个 PASS。

## 21. Batch 2026-07-16-020：WI-205 mainline 关闭与 WI-206 启动

- WI-205 / PR #134 / merge `aa156afe53534a10b1379348c532eb554ccf9ad3` 已完成
  frontend artifact path duplicate family：12 个定义收敛为 1 个 private helper，产品净减少 109 行；
  本地 PowerShell differential/rollback、双 Agent final PASS、Codex review、22 项 CI 与 fresh-main
  `3220 passed, 3 skipped` 均通过。
- 该结果关闭 WI-205 选定的 T63 重复族，但不关闭整个 T63、GAP-05、WI-196 或 RC-08；
  `program_service.py` 与 `program_cmd.py` 仍远高于 400 行。
- 下一原子项选择 WI-206 `206-model-string-dedupe`：Round 1 对抗审计将范围纠正为18个models
  顶层helper（含 `state.py::_dedupe_string_items`），基线216 LOC / 100 calls；预测产品
  新增≤33、删除≥216、净删≥183。
- 选择理由：该 L1 候选的收益/风险和 RC-06 余量优于 L2 Page/UI baseline；Loop Store 当前
  39 LOC 候选为 RC-06 No-Go；WI-203/204 Program Finalization candidate 保持 RC-09 No-Go、claim=0；
  WP-02 仍缺新/替代 sponsor。
- WI-206 formal branch=`feature/206-model-string-dedupe-docs`，worktree=
  `.worktrees/206-model-string-dedupe`，基线=`origin/main@aa156afe`。只有 formal 同哈希双 PASS 并
  合入 main 后，独立 implementation branch 才允许进入 T61A/TDD。

## 22. Batch 2026-07-16-021：WI-206 mainline 关闭与 GAP-12/GAP-13 分流

### 22.1 WI-206 closing evidence

- WI-206 implementation PR #137 在 Codex review 无 actionable finding、21 项 required checks 全绿后
  merge；merge commit=`506e950dee3469248ef7e6b5e1aac664668d18a1`。
- product=`+37/-246/net -209`，test=`+2`；18 个 models string helper 收敛为 1 个 private helper，
  calls=100、bindings=18、complexity 72→4；选定重复族 100% 消除。
- differential/rollback receipt SHA-256=
  `bb654c134fb4460d163f771b7d36da1e58dc898c5631032dcaa206d2e0d7abd8`。
- fresh detached main：19-file `281 passed, 2 skipped`、Ruff PASS、root truth exact node PASS、full
  `3220 passed, 3 skipped in 628.97s`；truth ready/fresh、inventory complete、zero blocker，worktree clean。
- WI-206 以 `completed_reduction` 关闭一个 T63/WP-03 family；不关闭整个 GAP-05、WI-196 或 RC-08。

### 22.2 新问题复现与原子分流

WI-206 acceptance 期间两类无关 tracked state 被治理命令改写。fresh `origin/main@506e950d` 的独立
复现证明它们不是同一根因：

1. GAP-12：`program validate` 业务 PASS 前由 root callback 调用 adapter hook，把 tracked Cursor
   rule SHA 从 `d5f04acf...` 改为 `02d9656d...`；program tests 只 patch nested root 时也可能写真实
   checkout。责任项为 T55 / WI-207。
2. GAP-13：`status` 通过 `load_resume_pack()` 重建两份 pack，把内部路径变为 worktree absolute，
   branch/active/context 变空。责任项为 T56 / WI-208；需要先裁决 canonical reconstruction source，
   不能通过信任旧 pack 绕过 WI-198。

Pascal/精简与 Confucius/兼容继续负责 formal 对抗评审。WI-207 只允许一行 root dispatch 修复和一处
test isolation；WI-208 独立处理 continuity。两个 gap 都不计减重成果，但会污染验证/恢复证据，因此
先于新的 T63/T65/WP-06/WP-07 候选关闭。

### 22.3 当前 next step

- active child=`207-program-adapter-side-effect`
- docs branch=`feature/207-program-adapter-side-effect-docs`
- formal review target=child 与 parent 两组三文件的组合哈希
- WI-207 formal 双 PASS/mainline 后进入独立 dev branch；fresh-main 后启动 WI-208。
- GAP-05、GAP-01/T62A、WP-06、WP-07、WI-196、RC-08 与版本发布仍 open。

## 23. Batch 2026-07-16-022：WI-207 PR #139 兼容 finding 与 formal 重开

- PR #139 的 naive 全族 bypass 已通过本地双审，但 Codex P2 指出 managed delivery 首次宿主验证迁移
  丢失；Pascal/Confucius 独立复核后均 ACCEPT 核心 finding。
- 影响仅限 `managed-delivery-apply` 与 `solution-confirm --execute --continue`；truth sync execute、普通
  solution-confirm execute 和其他 31 个 program handler 不依赖该状态，不恢复 hook。
- PR #139 已转 draft；T55 从 implementation 返回 formal design。修订预算为 main bypass + 一个 import +
  两个局部调用，总产品 additions≤4；不改 adapter/ProgramService，不引入通用命令分类器。
- GAP-13/WI208、减重收益与发布边界不变；T55 fresh-main 前仍阻断新减重候选。

## 24. Batch 2026-07-16-023：WI-207 Round 4 双 FAIL 与合同收敛

- Pascal/Confucius 对同一 `8cc93382...dcdeae` 独立 FAIL：父 CC-05 缺 managed dry-run 唯一例外、
  T55 旧范围残留、pre-import local patch 不可执行，且 solution-confirm hook 时序未冻结到授权门禁。
- 父 CC-05 现只允许 WI-207 `managed-delivery-apply --dry-run` 执行幂等 adapter/config 宿主验证
  exact delta，不普遍放宽 dry-run；T55 范围统一为 root bypass + 两 managed 局部刷新 + test isolation。
- solution-confirm 采用“persist then continue”：yes/preflight/continue/ack 通过且 solution 已持久化后，
  在 managed request 前单行调用；失败路径零调用，避免为四行预算写压缩条件或新增分类器。
- Round 4 verdict 作废；terminal sync 与 Round 5 同哈希双审完成前，PR #139 继续 draft。

## 25. Batch 2026-07-16-024：WI-207 Round 5 安全合同补齐

- Round 5 `0ed22f05...c631f0` 获 Pascal PASS、Confucius FAIL；精简方案成立，但兼容合同遗漏所有
  non-managed execute 路径的批准差分、direct apply 既有 preflight 写入和 hook 软失败语义。
- 父 CC-05 现明确区分 default、既有 truth-derived request materialization 与 WI207 adapter exact delta；
  direct execute missing yes 仍可完成 guard preflight，但禁止 mutate/apply result。
- 子合同增加 truth sync execute/solution no-continue 无 hook 证据，并区分 propagated RuntimeError 停止
  managed phase 与 config-lock warning-and-continue。四行产品预算和两 managed 入口边界不变。
- Round 5 verdict 全部失效；Round 6 双 PASS/mainline 前 PR #139 继续 draft。

## 26. Batch 2026-07-16-025：WI-207 Round 6 对抗评审统一通过

- formal combined=`2eaa2c0fa7aa18f9cd3598a89dbb85db78d0369d4f9342182f027bd0fedf5fcd`；time=
  `2026-07-16T20:24:50Z`。
- Pascal/lean=`PASS`、Confucius/safety=`PASS`；双方独立重算同一六文件 hash，findings 均为 none，
  未修改文件。
- 结论统一：四行 root bypass + import + 两调用是最小实现；non-managed delta、direct preflight、
  propagated/config-lock failure 与测试/回退合同完整。六文件冻结，下一步 formal PR/mainline receipt。

## 27. Batch 2026-07-16-026：PR #140 状态真值修复与 Round 7 双 PASS

- Codex P2 指出 child tasks T22～T25 状态落后于 Round 6 双 PASS 与 PR #140 事实；接受并只机械更新
  四个状态，未修改合同内容。
- Round 7 combined=`4394016e7d7af59090bf0a8ecaea82be0286c1fbbafaf5976467a3bf99ebc8c5`；Pascal/Confucius
  均独立 PASS、无 finding。T24 已完成，T25 正在 review/checks，T35 仍等待 formal mainline。
- PR #140 将保持单一 formal commit，更新后重新请求 Codex review 并继续 heartbeat。

## 28. Batch 2026-07-16-027：WI-207 formal receipt 去自引用

- PR #140 第二轮 Codex P2 指出 child T22～T24 仍绑定已退役的 Round 6 hash，与 Round 7 当前状态
  冲突；finding 接受。
- 根因是动态 combined/verdict 被写回参与 combined 的 `tasks.md`。现将任务状态稳定为引用 child
  execution log 最新终态回执，具体 round/hash 只保留在日志，避免 receipt 写回后再次使 formal 自失效。
- Round 7 退役；新的六文件固定 hash 必须重新取得 Pascal/Confucius 双 PASS、terminal gates 和
  Codex 当前 HEAD 无 actionable finding，之后才能合并 formal PR 并恢复 implementation。

## 29. Batch 2026-07-16-028：WI-207 Round 8 双 FAIL

- Round 8 combined=`484441ac7477f935fd595a8fcafe0c072c4ca38696d600a5c947d34415fbe735`；两位 Agent
  均独立 FAIL，finding 统一为 T22～T24 仍提前声明完成，和正在重审的状态矛盾。
- 仅将三行状态改为由 child execution log 最新 formal 同哈希终态回执决定，不内嵌动态 verdict/hash、
  不预先声明完成；其余 formal、四行产品预算、授权/异常/回退合同均不变。
- Round 8 退役；新 combined 必须重新双 PASS 后才能更新外部 receipt、terminal gates 与 PR。

## 30. Batch 2026-07-16-029：WI-207 Round 9 回执（已作废）

- 当时按 child spec 的重复编码记录 formal combined=
  `6a661de80c947fde2c7f73ee3d29fd21b9e041cd052ed11e2bf584eef46473b4`；该值不是父计划 §9
  canonical recipe 的结果。Pascal/lean 与 Confucius/safety 当时的 PASS 均随错误 target 身份退役。
- T22～T24 不再内嵌动态 verdict/hash 或预先声明完成；child execution log 最新终态节成为唯一
  formal review receipt，追加回执不会改变六文件 combined。
- 四行产品、两 managed 入口、测试预算、授权/异常/回退与 fresh-main 合同无变化；本节只保留历史审计。

## 31. Batch 2026-07-16-030：WI-207 Round 9 terminal gates

- constraints 无 BLOCKER；truth sync ready，动态 truth 三元组以目标提交内 `program-manifest.yaml`
  为准、不在本日志硬编码；inventory=`1091/1091`；validate PASS；truth audit ready/fresh；root exact=
  `1 passed in 77.31s`；diff-check PASS。
- terminal program 命令触发的已知 GAP-12 Cursor 非目标刷新已精确恢复；continuity root/scoped copy
  字节一致，resume-pack 为 repo-relative。该 gate 结果不能修复错误 review-target 身份。

## 32. Batch 2026-07-16-031：WI-207 canonical recipe 单一化

- PR #140 当前 HEAD 的 Codex P1 指出父计划 §9 与 child spec §8 的组合哈希算法互斥；Pascal 与
  Confucius 分别按父 canonical recipe 独立复算，均得到修订前 combined=
  `68829454a346c885b6e5ab731d715e48dee05eaee9a63513e73abdfc2292ceb8` 并一致 `FAIL`。
- 旧 `6a661de8...73b4` 回执和双方 PASS 明确退役；T22～T24 重新打开。最小修订仅让 child spec 引用
  父计划唯一 recipe，不改变四行产品、测试、授权、异常、回退或 fresh-main 合同。
- 下一步重跑终态门禁、冻结新 canonical combined，并让双方从零复审；双 PASS 前不合并、不恢复
  PR #139 implementation。

## 33. Batch 2026-07-16-032：WI-207 canonical Round 10 terminal gates

- constraints 无 BLOCKER；truth sync ready，动态 truth 三元组以目标提交 `program-manifest.yaml` 为准；
  inventory=`1091/1091`，unmapped/missing=`0/0`；validate PASS；truth audit ready/fresh；root exact=
  `1 passed in 76.33s`；diff-check PASS。
- 已知 GAP-12 Cursor 非目标刷新已精确恢复，worktree/HEAD blob 均为
  `ec0ed427a1db1d14370e1518a0c0fd2b8880384b`，无非目标 diff。
- 冻结父计划 §9 canonical combined=
  `2d19a12ce90d85b0838a53f6efdcf8454d36c7e5c242625c78802c2792ac4fa9`；双 reviewer 必须从零
  复审该同一哈希，任一 formal 修改使双方 verdict 同时失效。

## 34. Batch 2026-07-16-033：WI-207 canonical Round 10 同哈希双 PASS

- Pascal/lean 与 Confucius/safety 均独立按父计划 §9 复算 combined=
  `2d19a12ce90d85b0838a53f6efdcf8454d36c7e5c242625c78802c2792ac4fa9` 并 `PASS`，
  findings=`none`；起止 formal 摘要一致，target 无漂移。
- 双方确认 child spec 不再定义第二套编码；四行产品、测试预算、授权/异常、回退/fresh-main 与
  WI207/WI208 边界均无新增问题。旧 `6a661...`/`688294...` verdict 继续退役。
- 动态 receipt 写入后的终态复验已全绿：constraints no BLOCKER；truth ready/fresh、inventory
  `1091/1091`、unmapped/missing=`0/0`；validate PASS；root exact=`PASS`；diff-check PASS；运行耗时只保留
  在原始命令输出，不作为动态回执身份字段；
  已知 GAP-12 Cursor 非目标刷新已精确恢复。下一步更新 PR #140 current HEAD；合并前仍不恢复 PR #139。

## 35. Batch 2026-07-16-034：WI-207 Codex P2 与 Round 10 退役

- PR #140 current HEAD `e14dd07b` 的 Codex review 发现 child T31 提前标记 completed，而验收要求
  implementation worktree 来自 formal merge main，PR #139 仍待 rebase。
- finding 接受；最小修订只把 T31 改为部分完成，并把 completed 绑定到 T25/formal merge/rebase 后。
  四行产品、测试预算、授权/异常、回退/fresh-main 与 WI207/WI208 边界不变。
- child `tasks.md` 变化使 Round 10 `2d19a12c...4fa9` 双 PASS 退役。终态门禁与 Round 11 同哈希
  双审完成前不得更新/合并 PR #140 或恢复 PR #139。

## 36. Batch 2026-07-16-035：WI-207 Round 11 terminal gates 与冻结

- 父计划 §9 canonical combined=
  `46b63b1c923a5d382bd38650157dd04e7ffb4f8720e68b136057a8738fdc2efb`。
- constraints no BLOCKER；truth ready/fresh、inventory `1091/1091`、unmapped/missing=`0/0`；validate
  PASS；root exact=`PASS`；diff-check PASS；已知 GAP-12 Cursor 非目标刷新已精确恢复。
- 下一步 Pascal/Confucius 对该同一哈希从零双审；双 PASS 前不更新/合并 PR #140、不恢复 PR #139。

## 37. Batch 2026-07-16-036：WI-207 Round 11 同哈希双 PASS

- Pascal/lean 与 Confucius/safety 均独立按父计划 §9 复算 combined=
  `46b63b1c923a5d382bd38650157dd04e7ffb4f8720e68b136057a8738fdc2efb` 并 `PASS`，
  findings=`none`；formal target 无漂移。
- 双方确认 T31 lifecycle 修订消除提前完成，四行产品、测试预算、兼容/回退/fresh-main 与
  WI207/WI208 边界未改变。动态 PASS receipt 后 final gates 已全绿：constraints no BLOCKER；truth
  ready/fresh、inventory `1091/1091`、unmapped/missing=`0/0`；validate/root exact/diff-check PASS；Cursor
  非目标刷新已恢复。下一步更新 PR #140 current HEAD。

## 38. Batch 2026-07-16-037：WI-207 formal merge 与 implementation candidate

- PR #140 合并为 `8d325a4d`，fresh-main formal constraints/root exact/validate/truth audit 全绿；随后
  implementation branch rebase 到该 main，过期的 pre-merge docs receipts 未带入。
- Implementation commit `c4e5f07d` 只含批准的两个产品文件与一个测试文件：产品 additions=4，测试
  additions=110；real-host/exactly-once/未授权零调用/RuntimeError 与 config-lock 边界已覆盖。
- focused=`238 passed`、Ruff PASS、full=`3224 passed, 3 skipped`、constraints/truth/validate/diff-check
  全绿；治理命令不再污染 Cursor。精确 revert/reapply rehearsal 的 parent/candidate tree 均完全匹配。
- WI207 仍待 final-tree 双 Agent、PR #139 Codex/required checks、merge/fresh-main；在此之前 GAP-12 仍
  active，GAP-13/WI208 queued，WI196/RC-08 与 release 均不得关闭。

## 39. Batch 2026-07-16-038：WI-207 merge、fresh-main repair 与 GAP-14 分流

- WI207 implementation final HEAD `8bbff9bd` 已取得 Pascal/Confucius 同树双 PASS；PR #139
  current-head Codex 无 finding、22/22 checks success，合并为 `8752aa97`。
- 首轮 fresh detached main 的 real-hook/focused/full/Ruff 业务断言全绿，但 full suite 留下 root
  resume-pack 与 Cursor diff；pristine verify/real-hook/focused 单独运行 clean，根因不是产品 hook 或 verify，
  而是 8 组 CLI tests 继承真实 cwd。T55/GAP-12 因 fresh-main clean 条件未满足继续 active。
- 独立 repair branch 只改 8 个测试文件，产品 diff 为空：共享临时 cwd fixture + session repository-state
  guard。受影响集合 `195 passed, 1 skipped`；安全版 full `3224 passed, 3 skipped` 且外部 tracked/index/
  3 份 scoped resume/project config pre/post 摘要直接相同。Pascal 要求把 guard 从 `+127` 收敛到约 99 行，
  精简后 Pascal/Confucius 均 PASS；final compact affected=`196 passed, 1 skipped`、full=
  `3224 passed, 3 skipped`、Ruff/format/manifest exact 全绿，guard 与外部 pre/post 摘要均直接相同。
  repair exact-tree 双审、PR/Codex/checks/merge 与 fresh-main 尚待完成。
- dirty YAML resume diff 让 `comment_policy._is_comment_line()` 把 quoted scalar 续行 `#139...` 误判为
  removed comment。该问题登记 GAP-14/T57/WI209；不得混入 WI207 或用 execution-log waiver 掩盖。
- 路线顺序更新为 T55/WI207 → T56/WI208 → T57/WI209；三项均为基础可靠性修复，不计 RC-08，
  全部 fresh-main 前不恢复新的 T61/T62/T63～T67 实例，也不发布版本。

## 40. Batch 2026-07-17-039：GAP-12 关闭与 WI208 formal 启动

- WI207 repair exact target 取得 Pascal/Confucius 同目标双 PASS；PR #141 current-head Codex 无 actionable
  issue、13 required checks success，合并为 `8d8b8f96725ba6d2ba3257341f930348d7d9b0ac`。
- fresh detached main 的 real-hook=`4 passed`、focused=`238 passed`、full=`3224 passed, 3 skipped`；
  Ruff/format/constraints/validate/truth/manifest exact 全绿。显式 clean gate 证明 tracked/canonical adapter/
  project config/全部 scoped resume 与 pre-state 相同，无 restore，worktree clean。
- GAP-12/T55 因而 closed。WI208 已在独立 docs branch 初始化，GAP-13/T56=active；GAP-14/T57/WI209
  继续 queued。WI196/GAP-05/RC-08/release 均未关闭。
- WI208 根因收敛到共同 resume builder：filesystem fallback 写 absolute path，optional artifacts 缺失时
  expected pack 没有 branch/active/context。formal 冻结 checkpoint 单一真值、matching handoff 的窄字段
  fallback、portable path、WI-198 迁移与 relocation/detached/Windows/crash-convergent staged-pair/no-op
  matrix；不信任旧 pack。

## 41. WI-208 formal Round 5 admission 与 terminal pre-pass

- child+parent 六文件 canonical combined
  `4edae999905c32ad4d0e5caf6a04c5ad65aba922d9ecdf46d608211e592f68d1`；Pascal/精简直接性与
  Confucius/兼容安全性分别 start/end 复算同值，均 `PASS` 且无 actionable finding、target drift=`NO`。
- 五轮评审已关闭 checkpoint/runtime source、Changed Files、docs baseline、Cursor、crash-convergence、
  handoff tri-state/branch/context/wire grammar、raw-byte convergence 与 approved delta 的全部 findings。
- terminal pre-pass：truth ready/fresh、inventory `1096/1096`、unmapped/missing=`0/0`；constraints no
  BLOCKER、validate PASS、manifest exact `1 passed`。evidence 回写后继续 final sync/gates 与 formal PR。
- 首次 staged check 随后发现 untracked WI208 新文档行尾空格；未提交。修复后的 Round 6 combined
  `aab82d2601bbeb097331865e022b6c2458133bfae62f3afa9c5fc4a1496a18aa` 已重新取得 Pascal/Confucius
  双 PASS、无 finding；最终必须 re-stage exact target、worktree-index zero diff、cached diff-check=0。

## 42. Batch 2026-07-17-040：GAP-13/T56 fresh-main 关闭

- WI208 final HEAD=`a0b6feb1`、tree=`69ebf49f`、formal combined=
  `ce6cd4013af1a2f8e0d37082e330c42dc1d2a9a2cb686d36ad6fe7267c0361e0` 取得
  Pascal/Confucius 同一身份双 PASS；Codex current-head review 无 major issue，PR #143 22/22 checks
  SUCCESS，merge=`f51c176a8c57f7cb9a5bc05f467dc0dfedfaf079`。
- fresh detached main 的 relocation=`1 passed`、focused=`107 passed`、full=`3230 passed, 3 skipped`；Ruff、
  constraints、validate、truth `ready/fresh`、inventory `1096/1096`、unmapped/missing=`0/0`、manifest exact
  全绿。HEAD/tree、保护文件、scoped resume absent 与 clean status 前后无漂移。
- GAP-13/T56 关闭；回退 PR #143 会重开。GAP-14/T57 仍开放/queued，但 T56 依赖已满足；下一步只在新的
  WI209 formal branch 冻结 YAML quoted-scalar parser 边界，不恢复其他减重候选、不关闭 WI196/RC-08、
  不发布版本。

## 43. Batch 2026-07-17-041：WI208 closure 合并与 WI209 formal 初始化

- WI208 closure exact target 取得 Pascal/Confucius 同身份双 PASS；PR #144 的 Codex current-head review
  clean，Compatibility Gate/PR verify 最终 10/10 success，merge=`85bdedaca6a34563ccc2b8626a7e0adb188f1d4e`。
- closure fresh detached main 证明相对第一父提交 `src/tests` 零差异；constraints/validate/truth `ready/fresh`、
  inventory `1096/1096`、unmapped/missing=`0/0`、manifest exact=`1 passed in 76.67s`；root/scoped handoff
  bytes 相同、scoped resume absent、worktree clean。GAP-13/T56 终态不变。
- 从该 merge 创建 WI209 独立 docs branch。只读 spike 在 single/double quoted scalar 上都复现 1 finding，
  PyYAML scanner 同时给出跨行 quoted token span；formal 因而冻结 `--unified=0` hunk old/new 行号、
  HEAD/worktree 两侧 source 与 quoted token span 的对称过滤。
- GAP-14/T57 进入 formal active，仍未关闭；双对抗 PASS、formal PR/merge 前不改产品代码，WI209
  fresh-main 前不启动新的减重候选、不关闭 WI196/RC-08、不发布版本。

## 44. Batch 2026-07-17-042：WI209 formal Round 1 双 FAIL

- 主线程冻结 combined 时未使用本计划 §9 唯一算法；两位 reviewer 复算 canonical=`98d1781d…`，原
  `c4ccd5bc…` 无效。Pascal 同时指出 §9 示例仍硬编码 WI208、child 未明确引用，直接性 verdict=FAIL。
- Confucius 另发现 added YAML 解析失败会继续抵消真实 removed comment、closing token 行的尾部真实
  comment 会被整行豁免、old/new rename 与 Git quoted path 未建模、hunk zero/count/suffix/no-newline
  边界不全、缺少真实 CLI exit/text 五组安全缺口，verdict=FAIL。
- formal 加固为 removed/added 分侧 fail-closed、token end-column 后缀检查、old/new path 与完整 hunk
  状态机、CLI integration；父 §9 切到 WI209，child 唯一引用该 recipe。内容变化使旧 verdict 全部失效，
  新 exact target 必须重新经过两位 Agent 从零评审。

## 45. Batch 2026-07-17-043：WI209 formal Round 2 双 FAIL

- Round 2 exact target：staged tree=`a5deaa82`、canonical combined=`7a7c1dd5`、binary=`e1c1351e`；
  Pascal/Confucius start/end 均复算一致、无 drift，但 verdict 均为 FAIL。
- 共同 finding：两测试预算新增 CLI integration 文件却未冻结其 1799 行基线，Ruff/normalized 命令也漏该
  文件。Confucius 另发现 flow tokens 后真实尾注释仍可能被整行豁免、新工作树读取可能跟随
  symlink/junction 越界、mixed-extension rename 未锁分侧语义。
- formal 已增加三文件 `256/134/1799` 基线与同集 raw/normalized 门禁；尾部识别改为忽略后续 quoted
  token intervals 后查找 YAML comment；读取增加 no-follow/lstat/reparse/containment；路径矩阵增加
  yaml/py 双向 rename 与大小写扩展名。Round 2 verdict 全部失效，Round 3 必须双方从零复审。

## 46. Batch 2026-07-17-044：WI209 formal Round 3 continuity receipt FAIL

- Round 3 exact target：staged tree=`cf3e01b7`、canonical combined=`052d0780`、binary=`91e463e3`、
  name-status=`3d1becec`；双方 start/end 无 drift，unstaged/untracked=0。
- Pascal 对精简性、三文件预算、同集 raw/normalized 和五 helper 边界 verdict=PASS。Confucius 确认全部
  技术 finding 已闭合，但 continuity handoff 的 Changed Files 仍记录旧 `MM/AM`，与纯 staged 真值矛盾，
  verdict=FAIL。
- handoff 已改为稳定变更类型/路径，并声明 staging truth 由实时 `git status --short` 提供；T11 标记
  completed，T12/T57 标记 formal adversarial review active。内容变化使 Round 3 verdict 全部失效，
  Round 4 必须双方对新 exact identity 从零复审。

## 47. Batch 2026-07-17-045：WI209 formal Round 4 post-sync continuity 双 FAIL

- Round 4 exact target：staged tree=`1687eb0e`、canonical combined=`066f1f8b`、binary=`9a1cef04`、
  name-status=`3d1becec`；双方 start/end 无 drift，14 staged、0 unstaged/untracked。
- truth `ready/fresh`、inventory `1101/1101`、layers `209/209`、missing/unmapped=`0/0`；constraints、
  validate、comment-policy 9 tests、manifest exact 均通过；保护 resume/WI208 handoff 与 HEAD blob 相同。
- 两位 reviewer 均确认技术合同与预算无新问题，但一致指出 root handoff 早于最终 truth sync，且 Next
  仍要求重复已完成 gates/freeze；两方 verdict=FAIL。
- 处置顺序改为先完成 receipt、truth/terminal gates，再用 source CLI 刷新 handoff；最终 handoff 只记录
  已完成 pre-pass、稳定 formal combined 与剩余双审/PR，不保留旧 gate/freeze Next 或易过期 XY code。
  内容变化使 Round 4 verdict 全部失效，Round 5 必须双方从零复审。

## 48. Batch 2026-07-17-046：WI209 formal Round 5 同一身份双 PASS

- Round 5 exact target：staged tree=`9541fbe2`、canonical combined=`066f1f8b`、binary=`6d5b06bf`、
  name-status=`3d1becec`；双方 start/end 无 drift，14 staged、0 unstaged/untracked，diff-check PASS。
- Pascal 对精简/直接性 verdict=PASS：一产品文件、两测试文件、零新模块/公共抽象，预算与
  raw/normalized 同集闭合；manifest exact clean rerun 前后 hash/mtime 不变。
- Confucius 对兼容/安全 verdict=PASS：path/rename/hunk/flow/no-follow/fail-closed/CLI/continuity 闭合；
  root handoff 晚于 manifest，Next 真实，保护 resume/WI208 handoff 等于 HEAD blob。
- T12 转为 completed；T13 与 GAP-14/T57 转为 formal ready / PR delivery in progress。lifecycle 变化会
  改变六文件 target，必须冻结最终身份并由双方再审后才可提交 formal PR。

## 49. Batch 2026-07-18-047：WI209 implementation Round 8 双 FAIL

- formal PR #145 已合并为 `46156c24`；独立 implementation branch 已完成 RED/GREEN、focused/full、
  governance 与 replay。Round 8 产品代码仍限 `comment_policy.py`，预算 product raw/normalized
  `+123/+130`、tests `+196/+200`，不计 RC-08 减重收益。
- Pascal 判定 canonical delete+added real-comment 测试被预算压缩稀释，mutant 可存活；Confucius 确认
  历史 source-trust finding 已闭合，但 child/parent lifecycle、T21～T32、execution receipt 与 handoff
  不反映实现事实。两位 verdict 均为 FAIL，Round 8 identity 退役。
- T57/GAP-14 转为 implementation adversarial review，不提前关闭。当前批恢复独立反事实测试并同步
  child/parent canonical truth；重新跑 truth/manifest/回放且同一新身份双 PASS 后才进入 implementation PR。

## 50. Batch 2026-07-18-048：WI209 Round 8 findings fresh verification

- canonical delete+added real-comment case 已恢复，focused `98 passed` 且错误回退 mutant 被杀死；
  产品 raw/normalized `+123/+130`、测试 `+198/+200`，预算与范围不扩张。
- fresh full `3273 passed, 3 skipped`，constraints/validate/Ruff/diff-check PASS；truth sync 重算 `ready`、
  inventory `1101/1101`。child T23/T31 completed，T32 继续等待新身份 replay 与双审。
- 本 receipt 写回后必须再次 terminal sync/audit/manifest；T57/GAP-14 在 Round 9 双 PASS、implementation
  PR 与 fresh-main 前保持 implementation adversarial review，不恢复其他减重候选。

## 51. Batch 2026-07-18-049：WI209 Round 9 真实 Git 空格路径 FAIL

- Round 9 同一身份评审中 Pascal PASS；Confucius 在默认 ASCII 空格路径和 `core.quotePath=false`
  非 ASCII 空格路径上复现 quoted scalar 假 BLOCKER，verdict=FAIL，身份退役。
- 双路径 `diff --git` 继续因空格歧义 fail-closed；修订只允许从 Tab 终止的 `---/+++` 单路径 header
  安全恢复 old/new source trust。两条真实 Git RED 已得到 `2 failed, 10 passed`。
- T57/GAP-14 继续 implementation adversarial review；T23/T31/T32 重开，T41/T42 queued，禁止恢复
  新减重候选或提前关闭。

## 52. Batch 2026-07-18-050：WI209 真实 Git 空格路径 GREEN

- Tab 终止单路径 header 使用允许空格/非 ASCII、仍拒绝控制字符/引号/反斜杠的 grammar；歧义
  `diff --git` grammar 未放宽，其余 path/source fail-closed 链不变。
- 默认 ASCII 空格与 `core.quotePath=false` 非 ASCII 空格真实 Git 回归 GREEN；focused `100 passed`，
  产品 raw/normalized `+123/+130`、tests `+200/+198`，T23 completed。
- T31/T32 仍等待 fresh full、terminal truth/manifest、replay 与 Round 10 双审；T57/GAP-14 保持开放。
