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
| GAP-07 | planned-first | T51 | `cli/main.py`、`cli/cli_hooks.py`、首批执行记录 | red/green CLI test、clean-tree snapshot |
| GAP-08 | planned-second | T52 | `context/state.py`、当前 resume-pack 风险 | red/green continuity tests、artifact diff |
| GAP-09 | planned-independent | T53A | `program-manifest.yaml` truth snapshot | blocker closure snapshot |
| GAP-10 | planned-independent | T53B | `program-manifest.yaml` truth snapshot | consumption evidence、closure snapshot |
| GAP-11 | planned-independent | T54 | source inventory 1008/1041 | per-source resolution/exception ledger |

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
