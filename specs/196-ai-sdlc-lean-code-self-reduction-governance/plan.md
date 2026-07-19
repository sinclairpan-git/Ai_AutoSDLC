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
  ├─ T51 GAP-07 adapter/preflight 缺陷（WI-197 / PR #121，已关闭）
  ├─ T52 GAP-08 linked-WI resume 缺陷（WI-198 / PR #122，已关闭）
  └─ Barrier：T51 与 T52 已关闭
            └─ WP-01A 目标切片旧行为基线
                 ├─ WP-02 Lean Gate：report → warning → blocking（首个 T62A 候选 RC-09 No-Go；仍 open）
                 ├─ WP-03 helper/DTO/test 重复族
                 ├─ WP-04 Loop Store 重复族
                 ├─ WP-05 baseline 候选 go/no-go
                 ├─ WP-06 ProgramService 单领域切片
                 └─ WP-07 Program Stage 单 family 切片

已关闭的关联治理债务（当前仅保留防回归检查）
  ├─ T53A frontend inheritance truth（WI-199 / PR #123，已关闭）
  ├─ T53B adapter consumption truth（WI-200 / PR #124，已关闭）
  └─ T54 source inventory（WI-201 / PR #125，已关闭）

WI-206 fresh-main 新暴露的验证/连续性缺口（先于下一减重候选）
  └─ T55 GAP-12 program implicit adapter side effect（WI-207，已关闭）
       └─ T56 GAP-13 portable/lossless resume reconstruction（WI-208 / PR #143，已关闭）
            └─ T57 GAP-14 YAML quoted-scalar comment-policy false positive（WI-209 / PR #146，已关闭）
                 └─ T63 exact text-dedupe family（WI-210 / PR #149，completed_reduction）
                      └─ T63 exact mapping-dedupe family（WI-211 / PR #153，completed_reduction）

WI-213 formal 新暴露的独立只读入口副作用（先于 T66 T61A）
  └─ T58 GAP-15 workitem read-only adapter side-effect isolation（open）
       └─ WI-213 formal receipt 后的 T66 implementation WI / T61A
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

- **当前状态**：已由 WI-197 / PR #121 / merge `4802596f` 关闭；以下条款保留为已执行合同与回退依据。
- **风险/范围**：L1/L2；只处理 adapter hook 与 mutation preflight 的执行顺序。
- **非目标**：不重写 adapter，不改变普通用户自动适配语义。
- **进入**：先用 canonical CLI fixture 复现 `.cursor` 写入导致 clean-tree 阻断。
- **验证/完成**：红测能复现；修复后 `workitem init` 不因无关 adapter 写入自阻断，正常 adapter 路径保持绿色。
- **停止**：需要关闭自动适配或改变用户入口时升级为功能项。
- **回退**：revert 独立提交；旧 hook 行为恢复。
- **证据**：characterization test、clean-tree 前后快照、targeted CLI tests。

### T52：GAP-08 linked work item continuity

- **当前状态**：已由 WI-198 / PR #122 / merge `68150d3f` 关闭；以下条款保留为已执行合同与回退依据。
- **风险/范围**：L2；只修复 resume working set 与 current branch/spec/plan/tasks 派生。
- **非目标**：不改历史 checkpoint 阶段语义，不迁移 schema。
- **进入**：fixture 同时设置历史 `feature` 与新的 `linked_wi_id`，红测证明工作集仍指向历史 spec。
- **验证/完成**：linked WI 优先；canonical/scoped handoff、resume-pack 重建和 recover 使用同一工作集。
- **停止**：需要改变 checkpoint schema 时转 L4 迁移项。
- **回退**：revert 独立提交；保留现有手工恢复路径。
- **证据**：unit + CLI recover/handoff 回归、重建前后 artifact diff。

T51 与 T52 分属两个 WI/branch/PR，不以“基础包”合并交付。

### T55：GAP-12 program implicit adapter side effect

- **当前状态**：已关闭。PR #139 合并为 `8752aa97`；独立 test-isolation repair PR #141 合并为
  `8d8b8f96`；fresh-main real-hook/focused/full/Ruff/format/constraints/validate/truth 全绿且 checkout clean。
- **风险/范围**：L2 / CC-05；root `program` bypass + 两个 managed-delivery handler 局部既有 hook +
  `test_cli_program.py` root/local 隔离与双轴 fixture。
- **非目标**：不修改 adapter 同步算法、ProgramService、第三个 handler、resume-pack 或 verify telemetry。
- **进入**：real-hook Cursor fixture 证明只读 program 会改 adapter bytes；real-host fixture 证明 naive
  bypass 会让 managed delivery 保持 materialized 并出现假 blocker。
- **验证/完成**：三个只读命令受保护 bytes 稳定；managed 两入口保留 verified_loaded 迁移；其他
  truth/execute 与显式 adapter 路径保持；fresh-main clean。
- **停止/回退**：若需修改 `ide_adapter.py`、ProgramService、第三个 handler、引入分类器或超过 4 行产品
  additions 则停止；revert WI-207 独立实现提交。
- **证据**：WI-207 formal、原始/naive/candidate 双轴证据、focused/full、PR/CI/fresh-main。

### T56：GAP-13 portable/lossless resume reconstruction

- **当前状态**：completed；WI-208 / PR #143 已合入 `f51c176a`，fresh-main relocation、focused、full、
  Ruff、constraints、validate、truth 与 manifest exact 全绿，保护文件与 clean state 不变。
- **风险/范围**：L2；只处理 status/recover/handoff 的 resume-pack reconstruction 与 root/scoped 同步。
- **非目标**：不信任可能陈旧的旧 pack 字段，不修改 root adapter dispatch；checkpoint 继续锚定 active
  WI/fingerprint/docs baseline/execute fallback，active-WI runtime 继续优先提供 stage/batch/task。WI-198 的窄
  迁移裁决允许 matching canonical handoff 为所有 active WI 补 context、只以 eligible Branch 补 linked
  branch；active files 只从 working-set 或既有 `STAGE_FILES` 构造，no-linked 始终使用 checkpoint feature
  branch，仍禁止 `HEAD`/GitError fallback/历史 feature branch/docs 泄漏。
- **进入**：在不同 absolute worktree/detached HEAD 下复现绝对路径、空 branch/active/context，并完成
  WI-198 合同 impact analysis。
- **验证/完成**：repo 内部路径 portable；canonical sources 可无损重建；fresh status/handoff 幂等；
  stale/missing/corrupt、model-equal/raw-bytes-different、handoff tri-state/sentinel/summary、linked branch
  eligibility 与 Windows 路径矩阵回归通过。
- **批准差分**：除 portable/context/eligible branch/active-set/semantic 修复外，byte-only mismatch 只允许
  首次 canonical serialization、既有 stale/rebuilt event 序列与 rebuild timestamp；模型语义、checkpoint、
  event 文本不变，第二次 load 无写入/无 event。
- **停止/回退**：若只能通过信任旧 resume-pack 或推翻 WI-198 fail-closed 语义实现，则回到 design；
  revert WI-208 独立提交。
- **证据**：unit + status/recover/handoff integration + relocation/detached/crash-convergence receipt。

### T57：GAP-14 YAML quoted-scalar comment-policy false positive

- **当前状态**：completed；WI-209 formal PR #145/merge `46156c24` 与 implementation PR #146/merge
  `31aad572` 已完成。Round 15 candidate/replay tree 精确一致，Pascal/Confucius 对同一身份双 PASS；Codex
  审到 current head `c5c6e94adc` 且 22/22 checks success。fresh detached main focused `100 passed`、full
  `3275 passed, 3 skipped`，Ruff、constraints、validate、truth `ready/fresh 1101/1101 209/209`、manifest
  与 clean guard 全绿；GAP-14 已关闭，回退 PR #146 会重开。
- **风险/范围**：L2；只处理 unified diff 中 YAML quoted scalar 内容被 `_is_comment_line()` 误判为注释。
- **非目标**：不豁免真实 YAML comments，不修改 adapter、resume reconstruction 或 verify telemetry。
- **进入**：用 single/double quoted multiline scalar、plain/literal/folded、真实 comment 和非 YAML source
  建立 RED characterization；同时冻结 added quoted 内容不得抵消真实 removed comment。
- **验证/完成**：path/syntax-aware 最小实现；现有 Python/Markdown/YAML comment detection 保持；focused/full/
  constraints/fresh-main clean。
- **停止/回退**：若方案需要全局关闭 YAML comment detection、引入完整 YAML diff 重写器或 waiver，则回到
  design；revert WI-209 独立提交。
- **证据**：WI-209 child formal、comment-policy unit/Git matrix、verify constraints integration、双 Agent、
  PR/CI/fresh-main。

T55、T56、T57 必须顺序使用三个 WI/branch/PR；它们均是基础缺陷，不计 Reduction Contract 收益。

### T58：GAP-15 workitem read-only adapter side-effect isolation

- **当前状态**：open；由 WI-213 formal 的 `workitem plan-check --json` 验证发现，当前 formal 只登记和隔离。
- **风险/范围**：L2 / CC-05；只调整 `workitem` subapp adapter hook 的只读/写命令分发。
- **非目标**：不修改 adapter 同步算法、生成内容、`program` 分发、workitem handler 领域逻辑或 T66 产品代码。
- **进入**：在 clean fixture 先 RED 证明 `plan-check/guard/close-check/branch-check/truth-check` 至少当前
  `plan-check` 会改变 adapter bytes/working tree；同时冻结 `init/link` 的 valid、missing option、dirty/preflight、
  no project、no checkpoint、hook exception 矩阵，以及 hook 次数/时序、退出码、输出与写入。`init` 仅在
  branch/clean/duplicate preflight 成功后调用 hook；`link` 当前在 handler guard 前调用，改变任一负路径必须
  先登记 explicit expected delta。
- **验证/完成**：五个只读命令及其 help/invalid-input 前后 adapter/config/working tree bytes 不变且不输出
  install receipt；`init/link` 的冻结矩阵零未批准差异；targeted/full/Ruff/constraints、跨平台与 detached
  fresh-main clean 全绿。
- **停止/回退**：若修复要求关闭全部 workitem adapter、修改 adapter 算法或扩大到其他 CLI family，则回到
  design；revert T58 独立实现 PR。
- **证据**：command matrix RED/GREEN、real-hook byte hash、输出/退出码、dirty-state、双 Agent、PR/CI/fresh-main。

T58 不计 Reduction Contract 收益；其 fresh-main receipt 是 WI-213 后续 T66 T61A 的硬前置。

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

- **当前状态**：WI-205、WI-206、WI-210、WI-211 已各关闭一个 family。WI-211 / PR #153 / merge
  `cd64d8aa` 将 10 个 exact mapping-dedupe defs / 10 modules / 120 LOC 收敛为 1 个共享 body 与 10 个
  局部 alias，23 calls 不变；产品 raw 净删 122、non-empty 净删 104，fresh-main direct/impact/full/
  治理/clean-state 全绿。GAP-05 仍 active，下一 family 尚未选择。
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

- **当前状态**：WI-212 已唯一选择九个 bounded frontend stage；WI-213 formal-only 已在 PR #158 /
  merge `450d4988` 完成双审、mainline 与 detached fresh-main，冻结 45 methods=`3,638/3,305`、
  terminal≤720、产品净删≥2,918。当前先由独立 T58 关闭 GAP-15，才可创建唯一 implementation WI。
  该 WI 必须先 T61A 和双 readiness GO，随后 candidate PR 保留 legacy、完成主线预发布稳定周期，再以
  独立 PR 删除 legacy。
- **范围**：每个子 WI 只迁移一个领域；`ProgramService` 暂作薄 facade。
- **非目标**：不同时迁移第二领域，不改变公共调用方、CLI 或 artifact 合同。
- **进入**：WP-01A 完成；只依赖与该领域真实重叠的 WP-03～WP-05 子项，不等待无关低风险任务。
- **切换**：旧/新 shadow → 单入口切换 → 受影响 smoke → 一个主线预发布稳定周期 → 独立删旧 PR。该周期要求 candidate 已合入且 legacy 仍保留，并通过 required cross-platform CI、wheel/sdist、clean install、offline smoke、代表性 sibling project smoke 与 selector rollback/reapply；不创建版本、tag、GitHub Release、PyPI 发布或全局 CLI 更新。
- **完成**：迁移职责在原文件的 LOC/方法数下降至少 90%，并达到 RC-04 至少一项结构改善阈值；新文件/函数符合 RC-07，纯移动 No-Go。
- **停止/回退**：跨两个领域、差异不为零或临时膨胀超 RC-05 时缩小切片；删旧前 facade 指回旧实现，删旧后先 revert legacy-deletion PR，再回退 candidate PR。deletion 后必须重复同等安装包、offline/sibling smoke 与 rollback/reapply；rollback receipt 覆盖最终删除状态。
- **终态**：逐切片推进，直到 `program_service.py` 符合 400 行约束。
- **证据**：domain map、dependency diff、shadow result、release smoke、legacy deletion receipt。

### WP-07：Program Stage 单 family 切片（L3）

- **范围**：每个子 WI 只处理一个同语义 stage family；33 个公共命令全部保留。
- **非目标**：不删除/改名公共命令，不用 family 特判堆出新的通用 executor。
- **进入**：WP-01A 完成；stage family 的输入、失败和 artifact 语义已证明一致。
- **切换**：dry-run 双跑 → artifact 双跑 → 单 family 切换 → 主线预发布稳定周期 → 独立删旧 PR。该周期要求 candidate 已合入且 legacy 仍保留，并通过 required cross-platform CI、wheel/sdist、clean install、offline smoke、代表性 sibling project smoke 与 selector rollback/reapply；不创建版本、tag、GitHub Release、PyPI 发布或全局 CLI 更新。
- **完成**：目标 family 镜像实现 LOC 至少下降 70%，产品 LOC 净下降，CLI surface/退出码/提示零未批准差异。
- **停止/回退**：executor 出现 family 特判、语义差异或超 RC-05 时停止；删旧前命令路由切回旧 handler，删旧后先 revert legacy-deletion PR，再回退 candidate PR。deletion 后必须重复同等安装包、offline/sibling smoke 与 rollback/reapply；rollback receipt 覆盖最终删除状态。
- **终态**：逐 family 推进，直到 `program_cmd.py` 符合 400 行约束。
- **证据**：family matrix、33 命令 surface、shadow diff、release smoke、legacy deletion receipt。

## 7. 已关闭的关联治理债务与防回归

T53A、T53B、T54 已分别使用独立 WI/branch/PR 关闭，不再是待执行任务或当前总前置：

- T53A：WI-199 / PR #123 / merge `208a34c8`，frontend inheritance truth 已关闭。
- T53B：WI-200 / PR #124 / merge `c737eda0`，adapter canonical consumption truth 已关闭。
- T54：WI-201 / PR #125 / merge `d19c8b7d`，source inventory 已收敛为 unmapped=0、missing=0。

每个后续目标切片仍须落盘对应 impact analysis，作用是防止上述 truth 回归，而不是重复执行已关闭任务。
active child 在 closure 前只允许一个已映射但尚不存在的 `development-summary.md`，close 层必须精确为
`N/(N-1)`；closure 必须归零为 `N/N`，不得预建空 summary 伪造完成。分析缺失或不确定，或当前 truth
再次出现对应 blocker、unmapped、第二个 missing 或其他类型/path/layer 的 missing source 时，必须
fail-closed 并重开相应 GAP；关闭条件持续满足时不得把 T53A/T53B/T54 重新当作硬依赖。涉及 adapter
入口的切片仍须明确验证 GAP-10 的 consumption 边界未回归。

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

- Parent-only review target 为父 `spec.md + plan.md + tasks.md`。当前 child authoring 修改父 formal 时，
  target 唯一扩展为 child 与父各三文件。canonical combined 算法唯一：repo-relative path 按 ordinal
  升序；每行是 `<lowercase file sha256><two spaces><repo-relative path>\n`；对全部 UTF-8 行再次做 SHA-256。
  当前 WI213 在 worktree 根使用；后续 active child 必须机械替换 `$child`，不得发明第二套算法：

  ```powershell
  $parent = 'specs/196-ai-sdlc-lean-code-self-reduction-governance'
  $child = 'specs/213-programservice-bounded-stage-reduction'
  $files = @("$parent/spec.md", "$parent/plan.md", "$parent/tasks.md", "$child/spec.md", "$child/plan.md", "$child/tasks.md") | Sort-Object
  $rows = foreach ($file in $files) { "$((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant())  $file" }
  $payload = [Text.Encoding]::UTF8.GetBytes(($rows -join "`n") + "`n")
  [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($payload)).ToLowerInvariant()
  ```
- review record 包含 agent、维度、review target hash、时间、findings、处置、verdict；任一目标文件变化使两个 PASS 同时失效。
- 所有运行时工作包与 WI-196 mainline PR 均遵守 `AGENTS.md` 的 push、PR、Codex review、checks、heartbeat 和 merge 协议；L3 额外要求本地只读 reviewer。
- 当前子项 authoring 修改父 formal 时，review target 必须按上述唯一算法包含六文件；双 Agent 对同一
  combined hash PASS 后才可合并。handoff 应指向当前 active child，不得退回已关闭的
  GAP-07/08、旧 WI-202 或已完成 WI-206/WI-210。
