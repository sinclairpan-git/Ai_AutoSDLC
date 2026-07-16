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
