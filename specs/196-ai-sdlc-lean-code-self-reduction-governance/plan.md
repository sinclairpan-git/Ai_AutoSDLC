# 实施计划：AI-SDLC 框架缺口修复与自身减重

**编号**：`196-ai-sdlc-lean-code-self-reduction-governance`
**规格**：`specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md`
**性质**：治理总项路线图；运行时改动在独立子 work item 执行。

## 1. 执行策略

采用“原子基础缺陷 → 切片级行为基线 → 低风险去重与高价值分域并行 → 单切片双跑 → 稳定后删除”的路径。

不采用：

- 单分支大重写；
- 先建设全仓通用 Golden 平台再开始减重；
- 为满足 LOC 指标删除测试、安全和审计证据；
- 把无关历史 truth 债务串到减重关键路径；
- 只移动文件、不删除重复或降低复杂度的“伪减重”。

## 2. 依赖图

```text
双 Agent 同内容哈希 PASS
  ├─ T51 GAP-07 adapter/preflight 缺陷（独立 WI）
  ├─ T52 GAP-08 linked-WI resume 缺陷（独立 WI）
  └─ Barrier：T51 与 T52 都关闭
            └─ WP-01A 目标切片旧行为基线
                 ├─ WP-02 Lean Gate：report → warning → blocking（首个 T62A 候选 RC-09 No-Go；仍 open）
                 ├─ WP-03 helper/DTO/test 重复族
                 ├─ WP-04 Loop Store 重复族
                 ├─ WP-05 baseline 候选 go/no-go
                 ├─ WP-06 ProgramService 单领域切片
                 └─ WP-07 Program Stage 单 family 切片

关联治理债务（独立推进，不是总前置）
  ├─ T53A frontend inheritance truth
  ├─ T53B adapter consumption truth
  └─ T54 source inventory
```

WP-03～WP-07 不互相强制串行。只有代码重叠、契约重叠或同一重复族才形成真实依赖；依赖必须在子项 spec 中用文件/符号和测试证明。

## 3. 统一子项合同

每个子 work item 的 spec/plan/tasks 必须包含以下通用字段，并按 `spec.md` §6.3 选择 NC/CC/RC：

1. gap/WP 编号、目标切片、风险等级和明确非目标；
2. 代码/契约影响边界及依赖依据；
3. 适用的 NC/CC/RC 基线、预算和阈值；
4. 进入条件、验证命令、完成条件和 evidence URI；
5. 停止条件、回退命令/适配路径和 owner；
6. mainline PR 证据；L3 再增加本地独立 reviewer 证据。

缺少任一字段时，子项只能处于 design，不得进入 execute。合同 admission gate 只有在 `active + verified` 时替代人工评审；其他状态自动恢复风险分层 reviewer：L1/L2 普通项一个独立合同 reviewer，L3 或影响 CC-05/CC-06 的高风险项两个 Agent。

所有子项的最低验证命令为 `uv run pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 和 `git diff --check`；子 WI 必须在其 `tasks.md` 再冻结具体 targeted test 命令。证据统一写入 `specs/{child-wi}/task-execution-log.md`，结构化 differential/rollback receipt 写入 `.ai-sdlc/work-items/{child-wi}/`。

## 4. 基础缺陷子项

### T51：GAP-07 adapter mutation / clean-tree preflight

- **风险/范围**：L1/L2；只处理 adapter hook 与 mutation preflight 的执行顺序。
- **非目标**：不重写 adapter，不改变普通用户自动适配语义。
- **进入**：先用 canonical CLI fixture 复现 `.cursor` 写入导致 clean-tree 阻断。
- **验证/完成**：红测能复现；修复后 `workitem init` 不因无关 adapter 写入自阻断，正常 adapter 路径保持绿色。
- **停止**：需要关闭自动适配或改变用户入口时升级为功能项。
- **回退**：revert 独立提交；旧 hook 行为恢复。
- **证据**：characterization test、clean-tree 前后快照、targeted CLI tests。

### T52：GAP-08 linked work item continuity

- **风险/范围**：L2；只修复 resume working set 与 current branch/spec/plan/tasks 派生。
- **非目标**：不改历史 checkpoint 阶段语义，不迁移 schema。
- **进入**：fixture 同时设置历史 `feature` 与新的 `linked_wi_id`，红测证明工作集仍指向历史 spec。
- **验证/完成**：linked WI 优先；canonical/scoped handoff、resume-pack 重建和 recover 使用同一工作集。
- **停止**：需要改变 checkpoint schema 时转 L4 迁移项。
- **回退**：revert 独立提交；保留现有手工恢复路径。
- **证据**：unit + CLI recover/handoff 回归、重建前后 artifact diff。

T51 与 T52 分属两个 WI/branch/PR，不以“基础包”合并交付。

## 5. WP-01：最小充分 Characterization / Golden / Differential

- **范围**：只覆盖下一目标切片实际影响的 CC；优先复用现有测试、release smoke 和 fixture。
- **非目标**：不创建全仓通用 executor、数据库或新的测试 DSL。
- **Phase A 进入**：T51、T52 关闭；目标切片和 CC 影响矩阵已冻结。
- **Phase A 完成**：固定基线 revision、Python/OS/toolchain、fixture 选择理由和 normalizer allowlist；旧实现重复采样确定。
- **Phase B 验证**：作为每个候选 WI/PR 内的强制 pre-merge gate，绑定精确 candidate commit/tree hash；旧/新并行比较 CLI transcript、退出码、artifact、状态和授权副作用，零未批准语义差异。Phase B 与 rollback receipt 未通过，候选 PR 不得合并、WI 不得关闭。
- **完成**：回退演练通过，受影响平台/兄弟项目 smoke 通过；保护代码满足 RC-06。
- **停止**：harness 预计超过 RC-06 或需要覆盖无关表面时，缩小切片。
- **回退**：删除该切片新增 fixture/adapter，不接入产品入口。
- **证据**：版本化 surface manifest、normalizer、GoldenSnapshot、DifferentialResult 和 rollback receipt。

## 6. 减重工作包

### WP-02：Lean Gate 生命周期（L1/L2）

- **范围**：两个独立规则族：代码分类/changed-code 预算/waiver，以及 NC/CC/RC 适用矩阵/合同字段/admission。
- **非目标**：不追补或一次性阻断历史债务，不引入与 changed-code 无关的全仓重写。
- **进入**：WP-01A 完成；分类器在当前仓库零误分类样本通过。
- **阶段**：T62A 两个规则族 report-only → T62B 两个规则族 warning → T62C 两个规则族 blocking；每阶段独立 PR，两个规则族使用独立状态和开关，可单独降级。
- **当前状态**：WI-202 候选在 formatter/真实 Git/closed safety proof 下仍至少为 product 225、
  candidate 382，超过 170；已按 RC-09 停止，未合入 source 或消费 sponsor。T62A 仍 open。
- **兼容**：强制 CC-01/02/03/05/06/07；新增报告、warning/blocker 与退出行为必须写入版本化 expected-delta artifact，未列入差异为 BLOCKER。
- **完成**：历史未改代码不阻断；新增超限和缺合同字段 fixture 分别经历 report/warning/blocker；所有 waiver 有 owner、理由、路径和到期日；合同 admission 健康检查、状态转换和 execute BLOCKER 通过。
- **停止/回退**：任一规则族误判时只降级该规则族；合同 admission 不处于 `active + verified` 时自动恢复 FR-08 风险分层 reviewer，不追补历史债务。
- **重启**：必须同时有足额的新/替代 sponsor 与重新冻结、同 hash 双 PASS 的父合同；只满足一项
  不得复活 WI-202。重启前影响 CC-05/CC-06 的子项继续使用两个独立 reviewer。
- **预算/证据**：计入 RC-06；结构化报告、blocking fixture、降级演练。

### WP-03：稳定 helper / DTO / 镜像测试重复族（L1）

- **范围**：一次只选一个经语义审查的重复族。
- **非目标**：不跨不同错误语义合并，不建设通用 utility framework。
- **进入**：WP-01A 完成；至少三处当前调用者、失败模式一致、RC 预测达标。
- **完成**：选定重复族 100% 消除，目标切片净 LOC 至少下降 10%，场景/断言/平台不减少。
- **停止/回退**：错误语义不同或抽象需要分支特判时停止；按重复族提交 revert。
- **证据**：候选清单、call-site 比较、before/after、Golden diff、全量测试。

### WP-04：Loop Store 稳定公共逻辑（L2）

- **范围**：一次一个 store family 的 ID、路径、pointer、JSON/Pydantic 读取等稳定逻辑。
- **非目标**：不合并各 loop 的 close/error 规则，不创建依赖 loop 类型分支的公共基类。
- **进入**：WP-01A 完成；至少三个 store 的成功与失败语义一致。
- **完成**：重复族消除、目标切片净 LOC 至少下降 10%，各 loop close/error 规则仍独立。
- **停止/回退**：需要公共基类特判 loop 类型或改变恢复语义时停止；原 store adapter 可逐个切回。
- **证据**：store differential、损坏输入、恢复、幂等和全量测试。

### WP-05：静态 baseline 候选 go/no-go（L2，条件性）

- **范围**：一次审计一个 `build_p*_baseline` 及真实消费者；候选全集固定为 `spec.md` GAP-06 列出的 6 个 builder。
- **非目标**：不预设 YAML/JSON，不为单一消费者新增 schema/loader。
- **进入**：WP-01A 完成；至少两个真实消费者，重复真值可定位。
- **Go**：数据化后预测满足 RC，且 schema/loader/fixture 总成本低于删除量；格式由审计决定，不预设 YAML/JSON。
- **No-Go**：预测不达标即停止候选，不写 loader/schema，状态记为 `cancelled_no_go`。
- **完成**：Go 路径保持字段、顺序、默认值和 provider 行为并以 `completed_reduction` 关闭。单项 No-Go receipt 只关闭本次评估；六项均为 No-Go 时以 `closed_no_viable_reduction` 关闭 GAP-06，不计减重成果，除非基线或消费者实质变化不得重开。
- **停止/回退**：loader 分支比 builder 更复杂时停止；Go 路径保留旧 builder 适配直到差异通过。
- **证据**：consumer graph、成本测算、schema/serialization diff 或 No-Go receipt。

### WP-06：ProgramService 单领域切片（L3）

- **范围**：每个子 WI 只迁移一个领域；`ProgramService` 暂作薄 facade。
- **非目标**：不同时迁移第二领域，不改变公共调用方、CLI 或 artifact 合同。
- **进入**：WP-01A 完成；只依赖与该领域真实重叠的 WP-03～WP-05 子项，不等待无关低风险任务。
- **切换**：旧/新 shadow → 单入口切换 → 受影响 smoke → 一个稳定发布周期 → 独立删旧 PR。
- **完成**：迁移职责在原文件的 LOC/方法数下降至少 90%，并达到 RC-04 至少一项结构改善阈值；新文件/函数符合 RC-07，纯移动 No-Go。
- **停止/回退**：跨两个领域、差异不为零或临时膨胀超 RC-05 时缩小切片；删旧前 facade 指回旧实现，删旧后 revert legacy-deletion PR 并回滚对应发布。rollback receipt 必须覆盖最终删除状态。
- **终态**：逐切片推进，直到 `program_service.py` 符合 400 行约束。
- **证据**：domain map、dependency diff、shadow result、release smoke、legacy deletion receipt。

### WP-07：Program Stage 单 family 切片（L3）

- **范围**：每个子 WI 只处理一个同语义 stage family；33 个公共命令全部保留。
- **非目标**：不删除/改名公共命令，不用 family 特判堆出新的通用 executor。
- **进入**：WP-01A 完成；stage family 的输入、失败和 artifact 语义已证明一致。
- **切换**：dry-run 双跑 → artifact 双跑 → 单 family 切换 → 稳定发布 → 独立删旧 PR。
- **完成**：目标 family 镜像实现 LOC 至少下降 70%，产品 LOC 净下降，CLI surface/退出码/提示零未批准差异。
- **停止/回退**：executor 出现 family 特判、语义差异或超 RC-05 时停止；删旧前命令路由切回旧 handler，删旧后 revert legacy-deletion PR 并回滚对应发布。rollback receipt 必须覆盖最终删除状态。
- **终态**：逐 family 推进，直到 `program_cmd.py` 符合 400 行约束。
- **证据**：family matrix、33 命令 surface、shadow diff、release smoke、legacy deletion receipt。

## 7. 关联治理债务

T53A、T53B、T54 分别使用独立 WI/branch/PR。它们必须修复并产出 truth snapshot，但不自动阻断所有减重包。每个目标切片必须先落盘 impact analysis；分析缺失或结论不确定时 fail-closed，只有肯定的非影响证据才允许排除对应依赖。T51 涉及 adapter 入口，必须在 execute 前明确评估 GAP-10/T53B。

- T53A 关闭 frontend inheritance blockers。
- T53B 关闭 adapter canonical consumption blocker。
- T54 将 33 unmapped/11 missing source 逐项修复；无法修复者必须有 owner、原因和到期日。

## 8. 停止与回退总则

任一条件成立即停止当前切片：

1. 未批准的 CLI、artifact、状态、配置优先级或授权副作用差异；
2. Reduction Contract 预测或实测不达标；
3. 需要同时修改两个独立领域；
4. 测试场景、关键断言、平台覆盖下降；
5. 无法通过 facade、route 或 revert 恢复旧实现；
6. targeted/full tests、受影响 release smoke 或兄弟项目 smoke 失败；
7. 为减少 LOC 引入更深继承、更多特判或少于三个调用者的公共抽象。

兼容/安全差异不能 waiver。L4 变更停止减重并请求用户批准独立迁移项。

## 9. 评审、提交与完成

- 当前治理文档的 review target 为 `spec.md + plan.md + tasks.md`。在 worktree 根运行：`base=specs/196-ai-sdlc-lean-code-self-reduction-governance; for f in "$base/spec.md" "$base/plan.md" "$base/tasks.md"; do shasum -a 256 "$f"; done | LC_ALL=C sort | shasum -a 256`；相对路径文本属于哈希输入。
- review record 包含 agent、维度、review target hash、时间、findings、处置、verdict；任一目标文件变化使两个 PASS 同时失效。
- 所有运行时工作包与 WI-196 mainline PR 均遵守 `AGENTS.md` 的 push、PR、Codex review、checks、heartbeat 和 merge 协议；L3 额外要求本地只读 reviewer。
- 本治理项完成条件：双 Agent 对同一目标哈希 PASS、文档/constraints/diff/path 验证通过、handoff 指向 GAP-07 首个子项。
