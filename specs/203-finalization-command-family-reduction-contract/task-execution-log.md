# 任务执行日志：Program Finalization Command Family Reduction Contract

**功能编号**：`203-finalization-command-family-reduction-contract`
**创建日期**：2026-07-14
**当前状态**：Round 7 同 hash 双 PASS；T04 formal mainline delivery 进行中

## 1. 归档与哈希规则

- 本文件只追加执行、review 和 mainline receipt；不进入 review target hash。
- Review target 是 `spec.md + plan.md + tasks.md + candidate-baseline.json`；任一文件变化使两个
  PASS 同时失效。
- 后续实现、release、deletion 使用独立 WI/PR；本 formal 不预填未来完成结果。
- 每个 candidate commit 必须记录 RC-05 added/deleted/net/coexisting peak；保护代码记录 RC-06
  actual claim。
- 每批结束先验证，再把代码/测试与本批日志在同一逻辑提交中归档；不得伪造未来 commit。

## 2. Batch 2026-07-14-001｜T01-T02｜基线审计与 formal 重写

### 2.1 范围与预读

- 目标：从 10-command 草案识别最小可行 WP-07 family，冻结完整 RC/CC/T61/rollback。
- 基线：`d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`。
- 预读：项目宪章、WI-196 `spec.md/plan.md/tasks.md`、目标 handler/renderer/service/tests。
- 当前改动：仅 WI-203 formal、合法 manifest/project-state；无产品代码/测试/runtime rule。

### 2.2 宿主 shell 处置

项目 preferred shell 为 PowerShell。当前 macOS 宿主的 `pwsh` 在执行任何命令前退出 134：

```text
System.IO.FileLoadException: The given assembly name was invalid.
System.Text.RegularExpressions, Version=10.0.0.0
```

因此本批仓库只读/验证命令使用 zsh fallback；没有把宿主故障当作产品失败，也没有修改项目
shell 配置。后续 candidate 仍必须执行 Windows/PowerShell smoke。

### 2.3 只读基线证据

- 9 handler decorator-inclusive LOC：2,020；decorator/signature：207；retained+docstring：216；
  executable orchestration：1,804；AST branch proxy：432。
- 预审曾给出 line/AST similarity，但 normalization 口径不唯一；正式合同删除该分数，不以
  不可复算的相似度做准入。重复证据改为精确 symbol/LOC/branch 与行为 differential。
- 主 integration 聚类 58 tests；另有 1 个相关 report-dedupe test，总计 59。
- service 主聚类 104 tests；另有 2 个 archive 补充 test，总计 106。
- 已运行连续 CLI 聚类选择：`58 passed in 2.13s`。
- 已运行 9-stage integration+service 精确过滤：`165 passed, 469 deselected in 3.29s`。
- 9 renderer 共 220 LOC，但完全排除迁移；source hash 和逐字符行为纳入保护。

一次早期 pytest 选择命令把多行 node id 作为单一 zsh 参数，得到 no-tests-collected；根因是
shell 参数拆分，不是产品失败。改用 zsh 行数组拆分后获得上述 58 passed。

### 2.4 第一轮独立对抗预审

| Agent | 维度 | 初始关键发现 | 处置 |
|---|---|---|---|
| Pascal / `wi200_lean_design` | 精简效率 | 原 10-command 不同形；thread-archive 必须排除；指出 9 handler 的高重复和 RC-05 风险。最初建议 renderer co-migration。 | 接受排除 thread-archive；要求与安全侧交叉反证 renderer 边界。 |
| Confucius / `wi200_proof_safety` | 兼容安全 | placeholder formal 越权；CC-05 必须区分 default dry-run、explicit report、outer hook；路径行为、失败矩阵、T61A/B 不完整。最初建议 handler-only。 | 全部补入 formal；要求与效率侧交叉反证 renderer 边界。 |

### 2.5 交叉对抗与统一结论

双方在第一次交叉审阅中交换立场，说明“能否再删 220 行”本身不足以裁决。主 Agent 固定裁决
准则：在满足 WP-07 ≥70% 硬减重后，优先选择改动面最小、最利于真实回退的方案；renderer
必须明确为未关闭债务，不能冒充成果。

第二次交叉复核先统一 handler-only 边界；以下是正式终审前的初始预算，已被 §2.10 的 L3
相位修正取代，不作为当前合同：

```text
最终候选 = 前 9 个 public handler orchestration bodies
renderer = 不修改、不迁移、不计减重，以 source hash + 字符级 differential 保护
baseline = 2,020 LOC
final <= 606 LOC
net delete >= 1,414 LOC
mirror drop ~= 78%
shadow coexisting added LOC <= 303 per commit
```

安全侧当时判断：`PASS` 该候选边界，前提是 RC-05 不能把 module≤300、adapters≤81、glue≤9
误解为 shadow 同时新增 390。效率侧当时判断：
`PASS with hard budgets`，handler-only 已满足 WP-07，扩大到 renderer 不值得增加 Rich 输出风险。

这些 verdict 是对边界选择的预审，不是 T03 对最终 formal target hash 的正式 PASS。Formal 内容
生成后仍须双方重新复算同一 hash 并独立终审。

### 2.6 冻结决策

1. RC-01 只选 9 handlers；排除 thread-archive/project-cleanup/renderer/service/DTO。
2. 既有 external report absolute/`../` 行为在减重项中原样保留；安全收紧另立迁移项。
3. Outer adapter/update hook 与 handler differential 分层观测。
4. RC-05 每个 commit 聚合 shadow peak≤303；candidate 与完整 legacy 只在此上限内共存至
   stable release，随后由独立 deletion PR 删除 legacy。
5. 修正后的硬删除下限为 1,501；理论保护上限 375，但 receipt 主动只开放 353：
   candidate≤180、WI-202≤170、reserve=3。
6. Formal mainline merge只形成 sponsor receipt，不授权实现。

### 2.7 本批变更

- 重写 `spec.md`：目标切片、CC/RC、T61、stop/release/rollback、sponsor。
- 重写 `plan.md`：formal→T61A→TDD→migration→T61B→stable→deletion 全链路。
- 重写 `tasks.md`：T01～T53，可执行依赖、验收、追踪矩阵。
- 新增 `candidate-baseline.json`：机器可读指标、symbol、测试与预算真值。
- 重写本 execution log；恢复 `workitem init` 意外改写的 Cursor adapter 到 HEAD 内容。

### 2.8 验证状态

| 验证 | 结果 |
|---|---|
| JSON parse / 数字公式 | PASS；JSON parse 0，230+70+3=303，2020-519=1501，25%=375，claim=353 |
| targeted existing tests | final rerun `165 passed, 469 deselected in 2.66s`；覆盖 59 integration + 106 service |
| `uv run ai-sdlc verify constraints --json` | exit 0；blockers=0、advisories=0、decision=allow |
| truth audit | exit 1 `stale`；current recompute=`ready`，CLI 明确要求 formal commit 后 terminal truth sync 再 audit |
| review target hash | `9f835a8fe8bdd87acaab072e7df9d7abf66b2298df5e1bdb90a961a9042054d8` |
| 两个 Agent 同 hash终审 | Round 4 双 PASS；见 §2.13 |

### 2.9 批次结论

T01/T02 内容已形成；在 JSON/constraints/targeted 验证和 T03 双 PASS 之前，不进入 T04，
不创建 candidate 产品代码。

### 2.10 T03 Round 1｜正式同 hash 审核 FAIL 与处置

Round 1 的主 Agent zsh pipeline 给出 `31b820659650...`，但命令末尾包含 LF；plan 当时的
PowerShell `-NoNewline` 和两个 reviewer 独立 Python 复算均为 `00c65836fb3e...`。双方拒绝
在不同 hash 上签发 PASS，处置为新增唯一 canonical Python 算法：正斜杠相对路径、两个空格、
byte-order 排序、UTF-8、行间单 LF、末尾无 LF；PowerShell 显式 UTF-8 no-BOM。

双方共同发现 Phase 3“adapter 与 body 同 commit 删除”使 pre-deletion rollback 和 stable 后
独立 deletion 不可执行。已修正为：private module≤230、route adapters+selector≤70、glue≤3，
共存新增≤303；完整 legacy body/route 保留至 candidate merge 与 stable release；T51 独立删除。
修正后 final≤519、net delete≥1,501、mirror drop≥82.7%。

安全 reviewer 另发现并已处置：

- renderer 调用次数按 precondition/executor/writer/report failure 明确为 0/1；
- `--manifest` default/relative/absolute/`../` 解析加入 T61A；
- outer hook 增加 update/adapter/help/order 七场景；
- sponsor 增加 provisional/active/verified/stale/revoked、30/14/7 日与 blocked/替代失效规则。

效率 reviewer 另发现 similarity 分数无唯一 normalization。Formal 已删除该准入分数，并在
baseline 写入 LOC/docstring/branch proxy 的精确 AST 算法。Round 1 verdict 均为 `FAIL`，且 target
随后变化；旧 verdict 永久失效。新 hash 必须重新双审。

### 2.11 T03 Round 2｜同 hash FAIL 与处置

Review target：`f7accaf46908836932043391330ca0f4b3683823aedfdbf78b4d9144daa053f5`。
两个 reviewer 均独立复算一致；target 冻结期间未修改。

| Agent | UTC | Finding | 处置 |
|---|---|---|---|
| Pascal / 精简效率 | 2026-07-15T02:20:56Z | T01 仍要求已废弃 similarity 可复算 | 删除该要求；明确 similarity 不参与准入/删除预测，保留可复算 AST/LOC/branch/test 指标 |
| Confucius / 兼容安全 | 2026-07-15T02:23:06Z | sponsor 无成功终态；中断恢复/路径编码矩阵不具体；deletion 后 release/rollback 对象不闭合 | 新增 `settled`；写入中断点和路径样本；冻结 `Vn→Vn+1→Vn→Vn+1` 安装/代码回退链与量化 deletion gate |

Round 2 verdict 均为 `FAIL`。处置后 formal 进一步冻结：

- Sponsor 只有 `verified→settled` 为成功；按 actual deletion/protection 结算后停止 freshness
  timeout，不得新增 claim。
- 中断覆盖 step/artifact/renderer/report 边界的 KeyboardInterrupt/SystemExit/process termination，
  比较残留 raw tree 与同命令恢复。
- 路径覆盖中文/重音 root、manifest/report/spec path、POSIX surrogateescape 和 Windows non-UTF8
  console code page，冻结 legacy outcome。
- Candidate stable `Vn` 保留 legacy；三平台每个 2 条 9-stage clean chain（54 stage executions）、
  3 release-smoke jobs、2 sibling、零差异/新 violation、truth fresh、p95≤10% 后进入 deletion；
  deletion stable `Vn+1` 发布后回滚安装/代码到 `Vn`，再恢复 `Vn+1`。

Target 已变化，Round 2 不能复用；必须生成 Round 3 canonical hash 并重新双审。

### 2.12 T03 Round 3｜同 hash FAIL 与处置

Review target：`18838d559a3e2630e7e4d7c0f5604b246847a22895345e20e82f5310d03388ea`。
两个 reviewer 均独立复算一致，UTC 分别为 `2026-07-15T02:29:16Z`、
`2026-07-15T02:29:58Z`，全程只读。

双方共同指出：T53 将 `completed_reduction` 与 sponsor `settled 或 revoked` 并列；正式状态机只
允许 `verified→settled` 成功。已改为 T53 必须 settled；revoked 只进入取消/No-Go 路径。

安全 reviewer 另指出：candidate stable `Vn` 的 selector 指向 candidate，安装 `Vn` 只能恢复
legacy code 可用性，不能证明 legacy route 已运行。已把删除后 rollback 拆为：

1. `Vn+1→Vn`：恢复 legacy code/route 可用性，不宣称 legacy-active；
2. 在精确 `Vn` tag 上应用 selector-only commit `Rlegacy`，构建记录 source commit、filename、
   SHA256 的非发布 artifact，安装后实际运行 legacy route；
3. 重装 `Vn+1`，恢复并复验 current deletion release。

Round 3 verdict 均为 `FAIL`；target 变化后必须 Round 4 重新双审。

### 2.13 T03 Round 4｜同 hash 双 PASS

Review target：`9f835a8fe8bdd87acaab072e7df9d7abf66b2298df5e1bdb90a961a9042054d8`。

| Agent | 维度 | UTC | Findings | Disposition | Verdict |
|---|---|---|---|---|---|
| Confucius / `wi200_proof_safety` | 兼容安全 | 2026-07-15T02:33:09Z | 无可操作问题 | CC-01～08、T61A/B、renderer 0/1、manifest/outer hook、中断/Unicode、Vn/Vn+1/Rlegacy、sponsor actual-LOC 全闭合 | `PASS` |
| Pascal / `wi200_lean_design` | 精简效率 | 2026-07-15T02:36:22.999771Z | 无可操作问题 | 2020/207/216/1804/432、303/519/1501/353/22/54 全部独立复算；Rlegacy 不引入常驻层或第三 stable | `PASS` |

两者均独立复算 canonical hash 与主 Agent 一致，全程只读、target 未变化。T03 完成；后续仅可
向不在 target 的 execution log/handoff 追加 receipt。任一 target 文件变化会使本双 PASS 失效。

### 2.14 T03 Round 5｜空白修复后的最终同 hash 双 PASS

Staged `git diff --cached --check` 在首次提交前识别到 Markdown 行尾双空格。虽只影响排版，
仍按 hash 规则使 Round 4 PASS 失效。去除全部行尾空格后，final review target 为：

`15022819f0d526c5a3ec12e1a745a244c805ee341778e2253eaeae59a219f41c`

| Agent | 维度 | UTC | Findings | Disposition | Verdict |
|---|---|---|---|---|---|
| Confucius / `wi200_proof_safety` | 兼容安全 | 2026-07-15T02:45:11Z | 无可操作问题 | 独立 hash 一致；CC/T61、sponsor settled、Vn/Rlegacy/Vn+1 未因空白修复变化；cached diff/JSON PASS | `PASS` |
| Pascal / `wi200_lean_design` | 精简效率 | 2026-07-15T02:45:35.792276Z | 无可操作问题 | 独立 hash 一致；预算/AST/54 executions 复算通过；cached diff/165 tests PASS | `PASS` |

Round 5 在当时是有效双 PASS；后续 Codex whitelist finding 触发 target 修订，故该 verdict 已失效。

### 2.15 T03 Round 6｜测试真值白名单修正后的同 hash 双 PASS

Codex 指出 formal 白名单禁止所有 `tests/` 变更，但 PR 为已登记的 5 个 WI-203 truth source
机械同步了仓库级 inventory regression tuple，receipt 因而自相矛盾。Formal 已收窄为唯一允许
`tests/integration/test_repo_program_manifest.py` 的两个既有 tuple 精确更新；禁止新增/删除逻辑、
放宽断言或修改其他测试文件。新的 canonical review target 为：

`45dfaa4a986c3fa4ffbfef6c977ee5a0fb07501ad3978bb1b64c549c0aee66cf`

| Agent | 维度 | UTC | Findings | Disposition | Verdict |
|---|---|---|---|---|---|
| Confucius / `wi200_proof_safety` | 兼容安全 | 2026-07-15T03:37:01Z | 无可操作问题 | 独立 hash 一致；例外与 2 additions/2 deletions 严格对应；无 runtime/release/gate 放宽；CC/T61、Vn/Rlegacy/Vn+1、sponsor settlement 均未受破坏 | `PASS` |
| Pascal / `wi200_lean_design` | 精简效率 | 2026-07-15T03:37:42.275511Z | 无可操作问题 | 独立 hash 一致；机械同步净增 LOC=0，无新增/删除逻辑或其他 tests；303/519/1501/353/22/54 预算未受侵蚀 | `PASS` |

两者均只读独立复算并审查当前完整 diff。Round 6 当时是唯一有效双 PASS；后续 Codex
missing-source finding 触发 target 修订，故该 verdict 已失效。

### 2.16 T03 Round 7｜恢复 missing-source guard 后重新双审

Codex 指出将 WI-203 缺失的 `development-summary.md` 白名单化会削弱 WI-201 建立的仓库级
missing-source guard。意见成立：formal 改为物化如实标注“仅设计准入、candidate 未授权、工作项
未关闭”的 summary，并把两个既有 truth tuple 收紧为 `1071/1071/0/0`、close `203/203`。
Round 6 hash 与 verdict 作废；新 canonical review target 与双 Agent verdict 待本节追加。

新 canonical review target：

`cfcd63d7662175e8e9d413b831e582ee81d00958cb8d9c3c8c717de0987dc57f`

修复后的仓库真相回归：`1 passed in 59.48s`。

| Agent | 维度 | UTC | Findings | Disposition | Verdict |
|---|---|---|---|---|---|
| Confucius / `wi200_proof_safety` | 兼容、安全、回退、证据 | 2026-07-15T04:04:00Z | 无可操作问题 | summary 未虚报 closure；truth tuple 保持严格；CC/T61、renderer、outer hooks、平台/offline/sibling、Vn/Rlegacy/Vn+1 与 sponsor 边界无退化；terminal truth sync 仍为合并前强制条件 | `PASS` |
| Pascal / `wi200_lean_design` | 精简效率、预算、最小改动 | 2026-07-15T04:03:51.263836Z | 无可操作问题 | summary 是消除 missing-source 的最小 truthful artifact；测试仅 2 additions/2 deletions；预算与 AST 口径闭合；最终非 target 状态修正复核通过 | `PASS` |

两者均独立复算 canonical hash、只读审查当前完整 diff，并在最终非 target evidence 修正后确认
同一 hash `PASS`。Round 7 是当前唯一有效双 PASS；四个 target 文件从此冻结。

## 3. T03 正式评审记录

最终有效记录为 §2.16 Round 7。固定字段 agent/dimension/hash/UTC/findings/disposition/verdict
均完整；Round 1～3 的 FAIL，以及被 target 变化失效的 Round 4～6 PASS 均保留为审计历史，
不得用于当前 sponsor receipt。

## 4. T04 Mainline receipt

待 formal PR 合入后追加 branch、commit、PR、Codex review、checks、merge commit、truth 三元组、
handoff 和 sponsor activation。未合入前 receipt 不生效。

### 4.1 PR #126 首轮兼容门禁处置

首轮 Compatibility Gate 在 4 个 POSIX matrix job 中均只失败于
`test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence`：仓库真值断言仍固定为
WI201 的 `1066/1066/0/0` 与 close `202/202`，而 WI203 正式登记后的实际值为
`1071/1071/0/1` 与 close `203/202`；唯一 missing 是开放工作项尚未生成的
`development-summary.md`。首个失败 job 的完整结果为 `3185 passed, 1 failed, 3 skipped`。

处置仅更新该仓库级测试基线，不创建虚假的 completion artifact，也不修改四个 review target。
修复后相关回归为 `406 passed in 87.31s`，`verify constraints --json` 为 allow、0 blocker、
0 advisory；canonical review target 仍为
`15022819f0d526c5a3ec12e1a745a244c805ee341778e2253eaeae59a219f41c`。最终 receipt 仍以修复提交
上的 Codex Review 与全部 required checks 为准。

### 4.2 Codex old-head finding 处置

Codex 对 `ee9c45cb` 指出 canonical/scoped handoff 仍引用已被空白修复失效的 Round 4 hash。
该意见成立。handoff 与 resume pack 已明确写入唯一有效 Round 5 hash
`15022819f0d526c5a3ec12e1a745a244c805ee341778e2253eaeae59a219f41c`，并显式标记 Round 4 hash
`9f835a8fe8bdd87acaab072e7df9d7abf66b2298df5e1bdb90a961a9042054d8` 已失效。四个 review target
未变化；新 head 必须重新取得 Codex 无可操作意见和 required checks 全绿。

### 4.3 Codex whitelist finding 处置

Codex 对 `5d8a3634` 指出：实际 inventory regression test 机械更新不在 formal 白名单内。该意见
成立，触发 §2.15 的 target 修订和 Round 6 双 Agent 重审。当前唯一例外与实际 2 additions / 2
deletions 一致，未新增逻辑或放宽断言；旧 Round 5 receipt 已失效。

### 4.4 Codex missing-source guard finding 处置

Codex 对 `1b1e3955` 指出：把 missing source 固定为 1、close materialized 固定为 202 会重新打开
WI-201 已关闭的缺失来源回归。意见成立，触发 §2.16 的 target 修订和 Round 7 双 Agent 重审。
修复新增如实的 `development-summary.md`，恢复 `missing_sources == 0` 与 close `203/203`；不再用
测试白名单容忍缺失文件。

### 4.5 Codex summary review-state finding 处置

Codex 对 `61866429` 指出：新 summary 已物化 close source，但仍把 Round 7 双 Agent PASS 列为
待完成，与 execution log 的有效 receipt 冲突。意见成立。Summary 已改为“formal 双审通过、
mainline delivery 进行中”，把 Round 7 移入当前结论，并只保留 Codex/check/merge、WI-202 与
后续 candidate 工作为待完成。四个 review target 未变化，canonical hash 仍为
`cfcd63d7662175e8e9d413b831e582ee81d00958cb8d9c3c8c717de0987dc57f`。

最终非 target evidence 修正经双方只读复核：

| Agent | 维度 | UTC | Findings | Verdict |
|---|---|---|---|---|
| Confucius / `wi200_proof_safety` | 兼容、安全、回退、证据 | 2026-07-15T04:25:31Z | 无可操作问题 | `PASS` |
| Pascal / `wi200_lean_design` | 精简效率、预算、最小改动 | 2026-07-15T04:25:21.318782Z | 无可操作问题 | `PASS` |

双方均确认 target/runtime/tests 未变化，summary 未虚报 sponsor 激活、candidate、release 或 closure；
同一 canonical hash 继续有效。
