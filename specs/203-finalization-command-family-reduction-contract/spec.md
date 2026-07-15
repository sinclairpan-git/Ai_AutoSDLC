# 功能规格：Program Finalization Command Family Reduction Contract

**功能编号**：`203-finalization-command-family-reduction-contract`
**创建日期**：2026-07-14
**状态**：设计准入候选；未授权实现
**类型**：WP-07 / GAP-04 / L3 减重合同与 WI-202 保护预算 sponsor receipt
**基线 revision**：`d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`
**治理来源**：`specs/196-ai-sdlc-lean-code-self-reduction-governance/`

## 1. 结论与授权边界

本工作项冻结一个可实施、可量化、可回滚的 WP-07 候选：仅收敛 9 个同构
`program` handler 的 orchestration body。候选预测把目标 family 从 2,020 行降到不超过
519 行，净删除不少于 1,501 行，镜像实现下降约 83%。

本工作项当前只交付设计准入合同。只有以下条件全部成立，才允许后续独立 candidate
实现工作项进入 T61A；本 PR 本身不得修改 `src/`、runtime rules 或发布配置。`tests/` 默认
禁止修改，唯一例外是 `tests/integration/test_repo_program_manifest.py` 中既有仓库真值断言的
两个精确 tuple 可随 WI-203 已登记 source inventory 从 `1066/1066/0/0`、close `202/202`
同步为 `1071/1071/0/1`、close `203/202`。该例外不得新增测试逻辑、放宽断言或触及其他
测试文件，并必须由 full compatibility matrix 证明：

1. 两个本地独立只读 Agent 分别从兼容安全与精简效率维度对同一 review target hash
   明确 `PASS`；
2. formal PR 合入 `main`，提交哈希成为不可变 sponsor receipt；
3. candidate 实现项重新绑定该 mainline receipt、基线 revision 和 T61A 运行时基线；
4. candidate 实现项在编码前通过适用的 CC-01～CC-08、RC-01～RC-10 准入。

Formal 合入只允许下游引用保护预算，不授权运行时实现、删除 legacy、发布版本或改变安全
边界。Sponsor 使用 §6 RC-06 的状态机；候选取消、停滞、blocked、废弃、被替代、RC-09
No-Go、baseline/scope 变化或 receipt 被 revert 时，WI-202 必须移除该 claim、缩小到其他已合并
sponsor 的可用预算，或 revert 尚未获其他 sponsor 覆盖的保护代码。

## 2. 问题、目标与范围

### 2.1 问题

`src/ai_sdlc/cli/program_cmd.py` 在基线 revision 为 7,062 行。目标 9 个 handler 复制了
相同控制骨架：解析 root/manifest、校验、构造 request、渲染 preview、`--yes` 授权、
execute、写 canonical artifact、渲染结果、可选 report、设置退出码。差异主要是显式
service callable、字段 adapter 和文本，不需要 9 份完整控制流。

### 2.2 目标切片（RC-01）

文件：`src/ai_sdlc/cli/program_cmd.py`；精确符号与基线行号：

| CLI command | Python handler | 行号 |
|---|---|---:|
| `cross-spec-writeback` | `program_cross_spec_writeback` | 2745–2966 |
| `guarded-registry` | `program_guarded_registry` | 2969–3184 |
| `broader-governance` | `program_broader_governance` | 3187–3410 |
| `final-governance` | `program_final_governance` | 3413–3655 |
| `writeback-persistence` | `program_writeback_persistence` | 3658–3884 |
| `persisted-write-proof` | `program_persisted_write_proof` | 3887–4105 |
| `final-proof-publication` | `program_final_proof_publication` | 4108–4340 |
| `final-proof-closure` | `program_final_proof_closure` | 4343–4560 |
| `final-proof-archive` | `program_final_proof_archive` | 4563–4780 |

选定重复族只指这 9 个 handler 的 orchestration body。9 个 public command、Python symbol、
Typer 注册、decorator、签名和 docstring 必须保留；每个 handler 最终只能成为薄 adapter。

### 2.3 受保护但不迁移

以下内容必须由 T61A/B 保护，但不计入本候选减重成果，也不得在 candidate 中修改：

- 9 个 `_render_frontend_*_result`（基线符号 LOC 共 220）；
- `ProgramService` 的 9 组 Step/Request/Result、builder、executor、artifact writer 和 payload
  builder；
- 9 种 canonical YAML、step Markdown、optional report 结构与字段顺序；
- `program_app` 其余 24 个命令及 `program truth` group。

Renderer 源码片段哈希必须与基线相同；调用次数按阶段冻结：所有 dry-run、load/validation
失败、execute 无 `--yes`、executor/writer 抛异常均为 0；`--execute --yes` 且 writer 成功后
为 1（包括业务 incomplete）；report 写失败发生在 renderer 之后，因此仍为 1。它们的重复
债务保留给未来独立候选，不能在本项宣称关闭。

### 2.4 明确排除

- `program_final_proof_archive_thread_archive` 及其 renderer；该命令无本 stage artifact
  writer、report 指向上游 artifact，并有 `materialize_steps` 双模式；
- `program_final_proof_archive_project_cleanup`；
- ProgramService、DTO、artifact schema、状态或业务规则重构；
- 公共命令删除/改名、新增 option/JSON envelope、修复 report 外部路径行为；
- 通用 DSL、公共 executor、字符串反射式 service method 查找、按 command name 的
  `if/elif`；
- WI-202 Lean Gate 代码；本 formal 仅提供受限 sponsor receipt。

## 3. 用户故事与验收场景

### US-1：以最小改动面删除重复控制流（P0）

作为框架维护者，我希望 9 个公共命令继续表现完全一致，但只保留一份私有 orchestration
实现，以减少维护成本而不损失功能。

**独立测试**：在隔离 baseline/candidate clone 中运行 T61B，比较 9 命令 surface、退出码、
stdout/stderr、调用顺序、文件树、raw artifact/report bytes 和外部副作用，结果零未批准差异。

1. **Given** 任一基线 truth 场景，**When** 分别运行 legacy 与 candidate，**Then** 除
   allowlist 中的 clone root 和 `generated_at` 外逐项相同。
2. **Given** candidate runner 需要 stage-name 分支或 optional writer，**When** 执行准入，
   **Then** RC-09 No-Go，保留 legacy。

### US-2：用硬预算阻止“为减重而增重”（P0）

作为框架负责人，我希望每个 commit 都有 LOC ledger，确保 shadow 和终态均在预算内。

**独立测试**：对 baseline、每个 migration commit 和 deletion commit 运行同一 LOC/AST 脚本。

1. **Given** private module 尚与全部 legacy body 共存，**When** 聚合新增手写产品 LOC 大于
   303，**Then** 立即停止并回退。
2. **Given** 最终 family 大于 519 行或净删除小于 1,501 行，**When** 评估 RC-04，
   **Then** 不得合并或关闭。

### US-3：为保护门禁提供不重复计算的 sponsor（P0）

作为路线图治理者，我希望 formal 合入后可为 WI-202 提供有限保护预算，同时避免候选、
WI-202 和后续工作项重复消费同一删除量。

**独立测试**：sponsor ledger 的 claimed LOC 总和不超过 353，且每笔 claim 指向已合并
receipt 和独立 formal hash。

### US-4：删除后仍能真实回退（P0）

作为发布负责人，我希望 legacy deletion 之后仍能通过 revert deletion PR 与回滚稳定版恢复
9 个命令，而不是只证明 Git 理论可回退。

**独立测试**：删除后 rollback rehearsal 恢复 route、9 个 transcript、artifact 和
side-effect tree。

## 4. 公共兼容合同（CC）

| CC | 影响 | 冻结内容与证据 |
|---|---|---|
| CC-01 | 是 | 全部 33 个 `program` command discovery；目标 9 命令名称、option 顺序/类型/default/help、docstring、表格、plain/report 文本与 stdout/stderr 顺序。目标命令无 `--json`。 |
| CC-02 | 是 | not-project=1、load error=2、invalid manifest=1、dry-run=0、execute 无 yes=2、passed=0、incomplete=1，以及未捕获 I/O 异常行为。 |
| CC-03 | 是 | 9 个 canonical path、YAML key/list 顺序、字段缺失、step Markdown、report Markdown、错误文本；normalizer 只能处理明确允许项。 |
| CC-04 | 否 | 不触碰 checkpoint/workitem/loop/review 状态机；只保护现有业务 artifact state。触碰即 scope expansion / No-Go。 |
| CC-05 | 高风险 | 默认 dry-run 不写 stage/canonical artifact；显式 `--report` 允许写 report；execute/yes、step/artifact/report 写序、`.git`、外部 sentinel、subprocess/network、outer adapter/update hook 分别观测。 |
| CC-06 | 是 | root/manifest 解析、幂等、覆盖、partial write、writer/report failure、重试与中断后的文件集合。 |
| CC-07 | 是 | Windows/macOS/Linux、PowerShell、Unicode/非 ASCII 路径、POSIX surrogate-escaped 路径、UTF-8/非 UTF-8 locale/console encoding、固定 console width、离线 release smoke。 |
| CC-08 | 是 | 稳定发布后用全局安装的 bare `ai-sdlc` 在有选择理由的代表性 sibling project 做 help、dry-run 和隔离 execute-chain smoke。 |

9 个命令公共 option 形状保持：

```text
--manifest TEXT                    default=program-manifest.yaml
--dry-run / --execute              default=--dry-run
--report TEXT                      default=""
--yes                              default=false
```

每个命令专属 `--dry-run/--execute` help、`--yes` help 和所有提示从基线逐字冻结。

## 5. 已冻结的差异与边界行为

1. `cross-spec-writeback` 使用 `orchestration_result/orchestration_summaries`，并写业务 spec
   目录；其余 stage 使用各自 state/result/summaries 字段和 memory step 目录。
2. `final_governance` report summaries 当前不执行统一 dedupe；candidate 不得顺手更改。
3. publication/closure/archive renderer 使用 `soft_wrap=True`；前 6 个不使用。Renderer 不改。
4. execute 即使业务 blocked，也会把 confirmed blocked result 写入 canonical YAML 后 exit 1。
5. `root / report` 当前允许 absolute 和 `../` 解析到 project 外。本减重项为保证零差异明确
   保留这一既有行为，但测试只能写入隔离 temp parent sentinel。收紧路径属于独立安全迁移项，
   不能混入减重 PR；candidate 不得静默拒绝、normalize 或重定向。
6. 完整 CLI 在 handler 前仍可能运行 adapter 和 update notice。T61A 固定
   `AI_SDLC_DISABLE_UPDATE_CHECK=1` 捕获 handler differential，并另设 full-entrypoint 场景
   观测 outer hook；candidate 不得把 outer hook 差异归因于 handler normalizer。
7. normalizer 不得排序 YAML key/list、全局 dedupe、折叠 whitespace、全局替换 path separator、
   删除 warning/blocker 或模糊化所有时间样式文本。
8. `--manifest` 的 default、project-relative、nested relative、absolute、`../`、missing、malformed
   和 invalid 解析/错误行为全部由 T61A 逐命令冻结；candidate 不得借 common runner 收紧、
   normalize 或重定向。

## 6. Reduction Contract（RC-01～RC-10）

### RC-02 基线

机器可读值见 `candidate-baseline.json`。核心冻结值：

| 指标 | 值 |
|---|---:|
| 目标 handler decorator-inclusive LOC | 2,020 |
| decorator + signature | 207 |
| retained decorator + signature + docstring | 216 |
| executable orchestration body（不含 docstring） | 1,804 |
| AST branch-point proxy | 432 |
| 现有相关 integration tests | 59（其中连续主聚类 58） |
| 现有相关 service tests | 106（主聚类 104 + archive 补充 2） |
| generated / fixture / vendored 产品 LOC | 0 / 0 / 0 |

LOC/docstring/branch proxy 的 AST 公式完整写入 `candidate-baseline.json.measurement_method`。
Line/token/AST similarity 因 normalization 口径不唯一，不作为准入指标，也不进入删除预测；重复
证据使用精确符号范围、共同执行序列、branch proxy 与 T61 行为 differential。

运行时 p50/p95 必须由 T61A 在固定环境、同一 baseline hash 上补齐；在数值和采样命令写入
runtime baseline 前不得编码。运行时缺失是 candidate execute blocker，不是本 design-only formal 的
占位许可。

### RC-03 预算

- 新增私有模块最多 1 个，计划/硬上限为 230 行；
- 9 个 candidate route adapter 与 internal selector 合计不超过 70 行，import/glue 合计不超过
  3 行；三者都是同一 303 行总预算的组成部分，不能分别放大；
- candidate route 与完整 legacy body 共存时及删除后，新/替代手写产品 LOC 合计均不超过
  `230+70+3=303`，最终 family 总 LOC 不超过 `216+303=519`；
- 不新增公共抽象、依赖、配置、公开开关或 schema；所有新函数不超过 50 行；
- 稳定发布后的独立 deletion PR 删除 legacy handler body 不少于 1,804 行，最终净删除不少于
  `2020-519=1,501` 行；
- 新测试/harness/normalizer 不计产品 LOC，但必须计入 RC-06。

### RC-04 结果阈值

- mirror before=`2020-207=1813`；mirror after 最大=`519-207=312`；下降至少 82.7%；
- 原 `program_cmd.py` 的 migrated executable responsibility 从 1,804 行降到不超过 83 行，
  full-responsibility handler 从 9 降到 0；
- 选定 9 个 handler body 的重复控制分支 100% 消除；renderer 明确不属于选定族；
- 产品 LOC 净下降至少 1,501；纯移动或只加 facade 均 No-Go。完整 legacy 与 candidate 只可
  在 RC-05 限额内共存至稳定发布，不得在 deletion 后残留两套实现。

### RC-05 临时膨胀

上限为 `min(2020×15%,1000)=303` 行。该上限按每个 candidate commit 相对 baseline 的
“仍与 legacy 并存的新增手写产品 LOC”聚合计算，而不是分别计算 component maxima。

| 相位 | 允许状态 | 峰值规则 |
|---|---|---|
| S0 | 私有 runner/descriptor 仅由测试调用，legacy route 不变 | module≤230、import/glue≤3、聚合共存新增≤233 |
| S1 | 加入 9 个私有 route adapters/selector，默认仍可指向 legacy | adapters/selector≤70；module+adapters+glue 聚合≤303；legacy body 不删除 |
| S2 | internal route 切到 candidate，完整 legacy body/route 继续保留；做 T61B、回退演练和稳定发布 | 任一 commit 相对 baseline 的共存新增≤303；回退只切内部 route，不依赖 public flag |
| S3 | 稳定发布后独立 legacy-deletion PR 删除 9 个 legacy bodies 和失活 selector 分支 | 删除前不得关闭；deletion 后 candidate 新/替代 LOC 仍≤303，family≤519 |

每个相位在 execution log 记录 commit hash、new/deleted/net/peak LOC；任一峰值超过 303 即
RC-09 No-Go。

### RC-06 保护成本与 sponsor ledger

硬删除下限 1,501 对应理论保护上限 `floor(1501×25%)=375`。为保留 22 行风险缓冲，
本 sponsor receipt 主动将可 claim 总额收紧为 353 行，并受路线图累计 1,500 行绝对上限约束：

| Claim | 上限 | 生效条件 |
|---|---:|---|
| 本 candidate 的 T61A/B 新 test/harness/normalizer | 180 | candidate formal 独立通过；优先复用 59+106 个现有测试 |
| WI-202 T62A report-only | 170 | WI-202 引用已合并 sponsor receipt 并对自己的同 hash formal 双 PASS |
| 未分配缓冲 | 3 | 不可自动转给其他工作项 |

Claim 按合并顺序登记，不能重复消费；fixture/snapshot 每个冻结 CC 场景最多 2 个，规范化
snapshot 累计不超过 2 MiB。任一 claim 超预算必须缩小范围或停止，不能扩大删除预测。

Sponsor receipt 状态机：

| 状态 | 进入条件 | Claim 效力 |
|---|---|---|
| `provisional` | formal 双 PASS、尚未 mainline merge | 不可 claim |
| `active` | formal merge；owner/handoff/候选 baseline 已登记 | 可按上表 claim；30 日内必须进入 T61A |
| `verified` | T61A 已开始，最近 14 日内有同 baseline evidence/ledger 更新 | 既有 claim 有效，可继续但不可超额 |
| `stale` | 14 日无 evidence、连续 3 个 checkpoint blocked、WI/branch 被 archive 或 owner 明确暂停 | 不得新增 claim；既有 claim 7 日内重新获 sponsor 或开始缩减/revert |
| `revoked` | 30 日未进入 T61A、candidate 取消/废弃/被替代、RC-09 No-Go、baseline/scope 改变、receipt revert | Claim 立即失效；WI-202 在下一个 mainline PR 或 7 日内（取先到者）完成替代、缩减或 revert |
| `settled` | deletion release 已发布；实际净删除与实际 protection LOC 结算满足 25%/1,500 上限；T52 rollback receipt 通过 | 实际登记的下游 claim 永久由已实现删除量覆盖；停止 freshness timeout，不得再新增或扩大 claim |

状态变化必须写入 mainline 可审计 handoff/ledger；仅在聊天中声明继续不恢复 sponsor。新的
baseline/scope 必须产生新的 formal hash 和 mainline receipt，不能沿用旧预测删除量。
只有 `verified→settled` 是成功终态；`stale/revoked` 不能直接 settled。若实际删除量不足以覆盖
实际 protection LOC，先替换/缩减/revert 超额 claim，结算后才可进入 `settled`。

### RC-07 文件与抽象

- 新私有模块不超过 230 行，低于宪章 400 行；修改后的 9 个 handler 均不超过 50 行；
- 所有新 helper 不超过 50 行；私有 runner 有 9 个当前调用者；
- 无公共抽象、工厂、DSL 或未来扩展点；
- 历史 `program_cmd.py` 总文件超限继续由 WP-07 后续 family 处理，本项不能借机修改无关区域。

### RC-08 路线图贡献

本项只贡献至少 1,501 行净删除和 9 个 full-responsibility handler 清零，不关闭 RC-08。
路线图最终仍必须使 `program_cmd.py` 与 `program_service.py` 均不超过 400 行，并完成其他
重复族；本项不得把 renderer 未关闭债务计为成果。

### RC-09 停止投资

任一条件成立立即停止、保留或恢复 legacy：

- final family >519、净删除 <1,501、mirror 下降 <70%；
- 任一 shadow commit 聚合新增 >303，或保护 claim 合计 >353；
- runner 按 command name/family 分支、需要 optional writer、字符串反射或公共 DSL；
- 需要修改 ProgramService/DTO/renderer/thread-archive/project-cleanup；
- renderer source hash 改变，或 output/artifact/exit/side-effect 出现未批准差异；
- report path/outer hook 行为未按 §5 冻结；
- runtime p95 相对 baseline 退化超过 10%且复测仍成立；
- targeted/full、平台、offline release、installed artifact 或 sibling smoke 失败；
- 无法完成删除前 route 回退或删除后真实 rollback rehearsal。

### RC-10 证据

Candidate 与 deletion PR 必须给出 baseline/candidate/deletion commit、before/after LOC 与
complexity、逐 commit RC-05 ledger、RC-06 ledger、T61A/B differential、side-effect tree、
runtime p50/p95、pre-deletion rollback、稳定版本及 installed-artifact smoke、legacy deletion
receipt、post-deletion rollback、剩余风险。缺一项不得 merge/close。

## 7. T61A / T61B 强制基线

### T61A：旧行为

绑定 baseline revision、Python/Typer/Rich/PyYAML 版本、OS、locale、encoding、console width、
color mode、`AI_SDLC_DISABLE_UPDATE_CHECK=1`、9 个 include 和 3 个 exclude。

每个命令至少覆盖 help、not-project、manifest missing/malformed/invalid、upstream missing/
malformed/non-completed、completed+blockers、no-required-work、one-valid-step、valid+invalid-step、
outside/missing spec path、stable-empty visual/a11y、issue-review；主要 truth 分别运行默认 dry-run、
dry-run+report、execute 无 yes、execute+yes、execute+yes+report、dry-run+yes。

捕获 exit、分离 stdout/stderr、service call 顺序、before/after tree+hash、`.git`、外部 sentinel、
report/canonical YAML/step raw bytes、subprocess/network、runtime p50/p95，并跑完整 9-stage chain。

中断恢复矩阵在每个写入边界注入 `KeyboardInterrupt`/`SystemExit`，并在隔离 subprocess 对可
观测边界执行进程终止：first step 前、每个 step 写后、canonical artifact 写前/后、renderer 后、
report mkdir/write 期间。每次捕获残留 tree/mode/raw bytes，再以同一命令重跑，冻结覆盖、幂等、
错误传播和最终文件集合；legacy/candidate 的中断点、残留和恢复结果必须逐项相同。

路径/编码矩阵至少覆盖 project root=`项目-é-測試`、manifest=`配置/程序清单.yaml`、
report=`报告/结果-é.md`、spec path=`specs/001-课程-é`；POSIX 另测 surrogate-escaped byte
component，Windows 另测非 UTF-8 console code page。每项冻结 legacy 的成功/失败、输出字节、
文件路径和退出码，不假设所有平台必须成功，也不得用全局 path/encoding normalizer 掩盖差异。

Renderer 额外冻结 source segment hash；使用隔离 `StringIO + Rich Console`、color off、width
40/80/120 逐字符比较 empty/重复/Unicode/Rich markup/超长 summary/path/blocker/warning、顺序、
newline、fallback 和 soft-wrap。Renderer 层 normalizer 为空。调用矩阵必须分别断言：dry-run/
load/validation/execute-no-yes/executor-failure/writer-failure=0；writer-success=1（包括 incomplete）；
report-failure=1，且顺序为 `executor→writer→renderer→report`。

Full-entrypoint outer-hook 基线至少覆盖：update disabled、uninitialized adapter no-op、initialized
adapter no-op、stale adapter managed write、adapter permission warning、`--help` bypass，以及
`update→adapter→handler` 顺序；每项记录 handler 是否进入、stdout/stderr、文件/缓存/网络变化。

### T61B：候选 differential

- 固定 candidate commit/tree hash；代码变化使旧结果失效；
- report/execute 在两份 byte-identical 隔离 clone 分别运行，不在同一 root 连续双写；
- 比较 exit、stdout、stderr、调用顺序、tree、mode、raw bytes、YAML key/list 顺序与外部副作用；
- normalizer 只允许 temp clone absolute root、明确 key=`generated_at` 的时间和实际存在且登记的
  随机 ID；
- candidate full chain 可消费前一 stage artifact；所有差异必须为零或精确列入已批准 allowlist；
- renderer hash 必须不变，调用次数和位置与上述成功/失败矩阵一致。

## 8. 依赖、影响与治理债务

- GAP-07/WI-197、GAP-08/WI-198、GAP-09/WI-199、GAP-10/WI-200、GAP-11/WI-201 已在
  本 baseline 前合入；candidate 必须以 mainline truth audit 重新证明无回归。
- 当前切片不依赖 frontend provider runtime、adapter canonical consumption 或 source inventory
  未决项；若 truth audit 集合变化则 fail-closed。
- 既有 report 外部路径行为和 renderer 重复均未在本项修复；它们是明确非目标，不得在
  completion 中误报关闭。

## 9. 完成、发布与回退

### 设计准入完成

- 四件套与 `candidate-baseline.json` 无占位、矛盾或未决决策；
- 两个 Agent 对同一 review target hash PASS；
- constraints、truth audit、diff/path 白名单和 formal PR checks 通过；
- formal PR 合入 main，receipt 记录 merge commit；无运行时代码变化。

### Candidate 完成

1. T61A 同 hash baseline 完成；
2. TDD 实现且所有 RC 预算合格；
3. T61B 零未批准差异，删除前 route rollback 通过；
4. candidate PR 经 Codex review、required checks 和 L3 本地双 Agent PASS 后合入；
5. 发布 candidate stable `Vn`（candidate route 启用、legacy 保留），完成 §9 稳定准入；
6. 独立 legacy-deletion PR 删除失活 body/route，并发布 deletion stable `Vn+1`；
7. 从已安装 `Vn+1` 回滚到 `Vn` 恢复 legacy code 可用性，再应用精确标识的 selector-only
   `Rlegacy` artifact 实际运行 legacy route；最后重装 `Vn+1` 恢复当前。完整回归和 rollback
   receipt 通过后进入 sponsor `settled`，才以 `completed_reduction` 关闭。

### Stable/deletion release chain

| 节点 | 内容 | 准入/证据 |
|---|---|---|
| Candidate `Vn` | candidate internal route 生效，完整 legacy body/route 保留 | required CI；每 OS 两个 clean-root 9-stage chain（54 stage executions）；至少 2 个代表性 sibling；零未批准差异/新 violation；p95 退化≤10%；truth fresh |
| Deletion gate | `Vn` 安装产物完成上述矩阵，且 3 次独立 release-smoke job 全绿 | 无最低日历等待；用可复算执行次数/环境/健康阈值替代主观“观察一段时间” |
| Deletion `Vn+1` | deletion PR 已合入，legacy body/route 删除 | 重新 required CI、三平台/离线/installed/sibling smoke；final≤519、net delete≥1,501 |
| Deletion rollback | 源=`Vn+1`，目标=`Vn` candidate stable tag/commit | 安装 `Vn` 只证明 legacy body/route code 可用性恢复，不宣称 selector 已切到 legacy |
| Legacy-active rehearsal | 精确 `Vn` tag + 已记录 selector-only commit=`Rlegacy` | 构建非发布 artifact，记录 source commit、filename、SHA256；安装后证明 selector=legacy 并恢复 9 transcript/artifact/side-effect tree |
| Restore current | 源=`Rlegacy` rehearsal / `Vn`，目标=`Vn+1` | 重装并复验 `Vn+1`，确认当前 deletion release 恢复；临时 artifact 不成为新 stable release |

### 回退

- 删除前：内部 route 恢复 legacy；不得新增 public CLI/env 开关；
- 删除后：revert legacy-deletion PR/安装 `Vn` 恢复 legacy code 可用性；应用记录唯一 commit/hash
  的 `Rlegacy` selector-only rollback artifact 实际切到 legacy 并验证；随后重装 `Vn+1` 恢复
  current deletion release。仅回到 `Vn` 不得声称 legacy route 已运行；
- rollback receipt 必须证明 9 个 transcript、artifact、side-effect tree 和全局安装 CLI 恢复。

## 10. 成功标准

- **SC-01**：formal 同 hash 双 PASS 并合入 main，形成不可变 sponsor receipt。
- **SC-02**：候选终态 family ≤519 LOC、净删除 ≥1,501 LOC、mirror 下降 ≥70%。
- **SC-03**：任一 shadow commit 新增聚合 ≤303；私有模块≤230、route adapters/selector≤70、
  import/glue≤3；函数≤50；公共抽象=0。
- **SC-04**：CC-01～CC-08 零未批准差异；renderer source hash 和字符输出不变。
- **SC-05**：T61A/B、targeted/full/platform/offline/installed/sibling evidence 全部通过。
- **SC-06**：稳定发布与独立 legacy deletion 完成，删除后 rollback rehearsal 通过。
- **SC-07**：RC-06 claimed LOC ≤353；WI-202 claim ≤170 且不可重复计算；sponsor 状态不是
  `active/verified/settled` 时按期限完成替代、缩减或 revert；`settled` 只覆盖按 actual LOC
  结算的既有 claim，并停止 freshness timeout。
- **SC-08**：本项只关闭选定 handler orchestration 重复族，不误报 renderer、report path 或
  RC-08 路线图完成。
