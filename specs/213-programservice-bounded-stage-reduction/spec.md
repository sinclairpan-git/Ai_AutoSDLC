# 功能规格：ProgramService 九阶段精益减重正式合同

**功能编号**：`213-programservice-bounded-stage-reduction`
**创建日期**：2026-07-19
**状态**：formal-only 准入；禁止产品 execute
**类型**：WI-196 / WP-06 / T66 / GAP-03 / L3
**基线**：`main@e184c8e27818aa7950fcc64dbb10fa7a65888f8c`

## 1. 结论与授权边界

本工作项把 WI212 选中的九阶段 `ProgramService` 切片冻结为可实现、可量化、可回退的正式合同。
目标是以一个私有领域引擎替代 45 个方法中的镜像职责，同时保留全部公共 Python callable、CLI、DTO、
artifact、授权和错误语义。

WI213 **只交付 formal receipt**。本分支不得修改 `src/**`、产品测试逻辑、workflow、provider、runtime
rule、依赖、版本或发布配置。只有 WI213 的正式 PR 已合入 `main`、detached fresh-main 验收通过，且
GAP-15 已由独立 T58 work item/PR 关闭并通过 fresh-main 验收，才允许创建唯一 T66 implementation WI；
该 WI 还必须在写产品代码前完成 T61A，并取得 LEAN 与 SAFETY 两位 reviewer 的 readiness `GO`，才允许
进入 candidate 实现。

后续 candidate 与 legacy deletion 属于同一个 T66 工作包，但必须使用两个独立 PR。Candidate 合入时
legacy 必须完整保留；主线预发布稳定周期通过后才允许删除。Legacy 删除和删除后回退证明完成前，
不得关闭 T66、GAP-03、WI-196 或发布新版本。

## 2. 问题、目标与范围

### 2.1 当前问题

`src/ai_sdlc/core/program_service.py` 为 17,474 行。九个连续 frontend bounded stage 对同一控制骨架
重复实现 request、execute、artifact write、payload build 和 payload load；差异集中在显式类型、路径、
状态字段、文本和少数 step strategy。重复代码扩大了维护、评审与回归面，也阻碍 `ProgramService`
最终降到 400 行以内。

### 2.2 精确目标切片（RC-01）

Stage id 固定为：

1. `cross_spec_writeback`
2. `guarded_registry`
3. `broader_governance`
4. `final_governance`
5. `writeback_persistence`
6. `persisted_write_proof`
7. `final_proof_publication`
8. `final_proof_closure`
9. `final_proof_archive`

每个 stage 只包含五个方法族，共 45 个方法：

- `build_frontend_<stage>_request`
- `execute_frontend_<stage>`
- `write_frontend_<stage>_artifact`
- `_build_frontend_<stage>_artifact_payload`
- `_load_frontend_<stage>_artifact_payload`

### 2.3 明确保留

- 27 个既有 public request/execute/write callable 的名称、签名、annotation、docstring 和返回类型；
- 九组 RequestStep/Request/Result dataclass 及其构造、字段、默认值、`__post_init__` 和 module identity；
- 九个 CLI handler、renderer、Typer surface、退出码和 stdout/stderr；
- canonical artifact 路径、YAML key/list 顺序、raw bytes、step Markdown、report、错误/告警文本；
- dry-run、`--execute --yes`、确认、写入顺序、幂等、重试、中断和异常传播语义。

### 2.4 明确排除

- `program_final_proof_archive_thread_archive`、project cleanup 及其 service/CLI/renderer；
- 其他 `ProgramService` 领域、`program_cmd.py` 减重、DTO 合并或搬迁；
- 公共命令/option/schema/status/安全边界变更；
- 公共 executor、DSL、插件、registry framework、配置开关、环境变量或新增依赖；
- 字符串 method name + `getattr`、按 stage name 的 `if/elif/match`、循环 import、运行时 monkeypatch；
- 借本切片修复历史行为或清理无关代码。
- 在本 formal 分支修复 `workitem` 只读命令的隐式 adapter refresh；该 GAP-15 由独立 T58 承担。

出现上述需求即为 scope expansion，按 RC-09 停止并另立功能/迁移工作项；不得把它算作减重。

## 3. Current-main 实测基线（RC-02）

计量使用 Python 3.11 AST。Physical=`end_lineno-lineno+1`；executable 从函数体第一个非 docstring
statement 到 `end_lineno`，保留中间空行；branch proxy 以每函数 1 为基数并累计 branch/comprehension、
bool-op、try handler/else/finally 和 match case。

| 方法族 | 数量 | physical | executable | header | branch proxy |
|---|---:|---:|---:|---:|---:|
| request builder | 9 | 961 | 898 | 63 | 112 |
| executor | 9 | 1,589 | 1,517 | 72 | 148 |
| artifact writer | 9 | 378 | 288 | 90 | 72 |
| payload builder | 9 | 431 | 359 | 72 | 18 |
| payload loader | 9 | 279 | 243 | 36 | 36 |
| **合计** | **45** | **3,638** | **3,305** | **333** | **386** |

其中 27 个 public callable=`2,928 physical = 225 header + 2,703 executable`；18 个 private payload
method=`710 physical = 108 header + 602 executable`。18 个 private method 各有一个 service 内调用，
在 `src/**` 外部调用数为 0。生产调用总数：request=`18 service-internal + 9 CLI`、execute=
`9 service-internal + 9 CLI`、writer=`9 CLI`、private build/load 各=`9 service-internal`。

现有相关测试为 165 个：`tests/unit/test_program_service.py` 106 个/3,835 physical LOC，
`tests/integration/test_cli_program.py` 59 个/2,482 physical LOC；current-main 实跑为
`165 passed, 474 deselected in 2.77s`。该库存只能复用，不能代替 T61A differential。目标切片没有
generated、fixture 或 vendored 产品 LOC。仓库产品基线仍为 217 个 Python 文件/107,321 行，
`program_cmd.py` 为 7,057 行。

## 4. 最小设计合同

### 4.1 唯一允许的结构

后续 implementation WI 最多新增一个私有模块：

```text
src/ai_sdlc/core/
├── program_service.py                  # 27 个 public thin facade；九组本地 typed binding
└── _program_bounded_stage.py           # private definitions + engine，≤360 行
```

私有模块不得 import `program_service.py` 或 CLI。它只定义：

- frozen/slots 的私有 stage definition；
- 九个当前 stage 的静态 definition；
- 一个 cross-spec strategy 与一个其余 bounded-stage strategy，以显式 callable 绑定，不按 stage name 分支；
- request/execute/write/payload/load 的小函数；每个函数≤50行。

`program_service.py` 必须在 DTO 已定义后建立九个显式 typed/path binding；每组绑定 stage definition、
Request/RequestStep/Result factory、source/output path 以及 step-dir 或 cross filename。Ruff 88 列格式下九组
机械下限约 83～85 行，因此 binding/import/selector glue hard cap 为90行，不能把它藏入 private module、
反射或循环 import。Terminal facade body 合计≤45行；candidate 共存时 selector+route 增量≤72行。

Engine 通过 binding 中的显式 constructor/callback 和结构化 value 运行，不使用字符串方法反射或第二份
YAML/schema。Stage definition 只承载当前已存在的状态 key 和文本差异，不预留未来扩展字段。不得增加
public CLI/env/config 开关。该 Ruff 反证使 WI212 的预备 glue≤5、terminal691、净删2947 和本 formal
早期草案的 glue≤15/terminal701 同时退役；所有预算以下表重新闭合。

### 4.2 切换语义

1. T61A 后，candidate 模块和测试 seam 先存在但生产 selector 默认 `legacy`。
2. 每个 stage 在隔离双根完成 old/new differential；未轮到的 stage 继续 legacy。
3. 九阶段全部通过 T61B 后，以单一私有 binding/constant 切到 candidate；立即演练切回 legacy、重跑、再切回 candidate。
4. Candidate PR 合入 `main` 时默认 candidate、legacy 完整保留。
5. 主线预发布稳定周期通过后，独立 deletion PR 删除旧 body、18 个失活 private method 和 legacy selector 分支。
6. 删除后回退必须先实际 revert deletion PR 恢复 legacy，再验证 selector rollback/reapply；不能只写 Git 理论说明。

## 5. Reduction Contract

| 合同 | WI213 冻结值 |
|---|---|
| RC-01 | 仅 §2.2 的 45 methods + §4.1 一个 private module；27 public callable 保留 |
| RC-02 | `3,638 physical / 3,305 executable / branch proxy 386`；测试 `165 / 6,317 LOC / 2.77s` 单次基线；T61A 补 p50/p95 |
| RC-03 | private module≤360；candidate facade addition≤72；terminal facade body≤45；typed/path binding+import+selector glue≤90；新依赖=0；公共抽象=0；预计删除≥2,918 |
| RC-04 | 原文件 full-responsibility methods `45→0`、executable responsibility `3,305→≤45`；终态切片≤720；branch proxy≤90；stage-specific 镜像分支100%消除；纯移动 No-Go |
| RC-05 | legacy 共存新增产品≤`360+72+90=522`，低于 `min(floor(3638×15%),1000)=545`，buffer≥23 |
| RC-06 | 新增 product≤522，新增 test/harness/normalizer≤190，合计≤712≤`floor(2918×25%)=729`，buffer≥17；既有保守 subtotal184，路线累计≤896≤1,500 |
| RC-07 | 新文件≤360<400；新/修改函数≤50；公共抽象=0；只允许一个私有模块 |
| RC-09 | 任一数值超限、T61A readiness 非双 GO、语义差异、第二领域、反射/DSL/循环 import、平台/安装/离线/兄弟项目或回退失败即停止并保留 legacy |
| RC-10 | formal、T61A、candidate、stability、deletion、rollback 每阶段绑定 commit/tree、LOC ledger、命令和 raw evidence |

终态数学：`225 public header + 45 facade body + 90 binding/glue + 360 private module = 720`；全产品净删至少
`3,638-720=2,918`。`program_service.py` 自身最多保留 `225+45+90=360` 行目标职责，因此至少减少
`3,278` 行，从 17,474 降到不高于 14,196。该结果只关闭一个领域切片，不关闭 `program_service.py`
400 行终态或 RC-08。

所有新增手写 product、test、harness、normalizer 都计费；facade、selector、门禁不是减重成果。
现有测试和既有 fixture 不重复计费；任何新 snapshot 每个冻结 CC 场景≤2，版本库累计≤2 MiB。

## 6. 兼容与防回归影响分析

| 合同 | 影响 | 必须证明 |
|---|---|---|
| CC-01 | 是 | 33 个 program command discovery；目标九命令 help/参数/default/docstring/stdout/stderr 零差异 |
| CC-02 | 是 | success、blocked、invalid、I/O exception 的退出码和异常类型/文本零差异 |
| CC-03 | 是 | request/result 字段、YAML/Markdown/report 路径、顺序和 raw bytes 零差异 |
| CC-04 | 间接 | 不修改 checkpoint/workitem/loop/review；九阶段链的既有合法状态和 source linkage 不变 |
| CC-05 | 高 | dry-run 无写；execute/confirm、step→artifact→report 顺序；workspace/.git/外部 sentinel/subprocess/network 观测 |
| CC-06 | 高 | path、覆盖、幂等、重试、partial write、KeyboardInterrupt/SystemExit/isolated termination 后恢复 |
| CC-07 | 是 | Windows/macOS/Linux、PowerShell、Unicode/路径/encoding、wheel/sdist clean install 与 offline smoke |
| CC-08 | 是 | 至少两个有选择理由的代表性 sibling project 使用安装产物跑 help/dry-run/隔离 execute chain |

Normalizer 只允许双临时根绝对前缀，以及经 clock spy 证明由默认 `utc_now_z()` 生成的
`generated_at` 值；caller-supplied truthy 时间必须逐字节比较，不能仅按 key 删除。`None`/空串等 falsey
输入沿用 legacy `value or fallback` 并调用时钟，是否调用、次数与顺序必须单独零差异。实际出现随机 ID 时
必须逐字段登记。禁止排序 key/list、全局空白/换行/path-separator/time regex、dedupe 或删除 warning/blocker。

GAP-09/10/11 防回归结论：本项不改 frontend capability/inheritance、不改 provider/adapter consumption；
formal 只新增 canonical source，implementation 新增的 source/proof 仍必须全部映射。任一 inheritance/consumption
blocker、unmapped source 或除 active work item 唯一 summary 外的 missing source 出现时，立即重开对应 GAP。

GAP-15 当前实测：`main@e184c8e2` 上 `program validate` 前后 `.cursor/rules/ai-sdlc.mdc` SHA-256 均为
`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`；随后运行标称只读的
`workitem plan-check --wi specs/213-programservice-bounded-stage-reduction --json`，CLI 输出
`IDE adapter (cursor): installed 1 file(s)`，SHA 变为
`02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134`，产生 `+18/-6` tracked diff。
根因边界是 `workitem` subapp callback 对除 `init` 外的子命令统一调用 adapter hook。Formal 已恢复 base
bytes，只登记 GAP-15；T58 必须用独立 RED/GREEN 命令矩阵关闭后，T66 才可进入 T61A。

## 7. T61A / T61B 最小充分证据

### T61A：编码前 legacy 基线

- 固定 formal merge commit/tree、Python/OS/dependency、九阶段 45-symbol map 和 LOC/branch recipe；
- 重跑 165 个现有测试，并建立双临时根的 direct-service + full-CLI baseline；
- 覆盖 missing/malformed/non-mapping/upstream state、empty/valid/invalid steps、confirmation、write/report failure、
  path outside root、raw bytes、异常、调用顺序、重试与中断恢复；
- 记录 file tree/mode/hash、stdout/stderr、dataclass equality、external sentinel、subprocess/network；
- warm-up 后至少 20 次样本记录 p50/p95；candidate p95 允许最多 10% 回归，超限复测仍成立即停止；
- 生成版本化 Python-surface manifest：27 个 public callable 的 `inspect.signature`、parameter kind/default/
  annotation、return annotation、`__annotations__`、`__doc__`；九组 DTO 的 module/qualname、
  `dataclasses.fields` name/type/default/default_factory/order 及 `__post_init__` 可移植 fingerprint。Canonical
  schema 分三类：public facade 只比较 API surface + 代表性行为 digest，不比较必然变化的 body/source；合同
  禁止修改的 DTO `__post_init__` 比较 presence/module/qualname/signature/source SHA-256 + 行为 digest，
  当前源码不可读取即 fail-closed，不实现 bytecode/code-object fallback；default/default_factory 使用
  MISSING、typed literal、source-backed callable fingerprint，或仅
  对当前 `builtins.list/dict` 使用 `builtin + module + qualname + behavior` tag。未知/不可 canonicalize 的
  callable kind 才 fail-closed；禁止 `id()`、对象 identity 或含内存地址的 `repr()`；
- 用 subclass/spy/`patch.object` 冻结九个 execute 对 `self.build_*`、九个 writer 对 `self.build_*` 与
  `self.execute_*` 的 late-bound dispatch。矩阵覆盖 `None`、正常 truthy、falsey request/result stub，以及
  `generated_at=None/""/固定 truthy 时间`；保持 legacy `value or fallback`、调用次数/顺序和异常传播；
- 预测 architecture 与 proof LOC；product>522、proof>190 或需要非 §4.1 结构即 readiness `NO-GO`；
- Pascal/LEAN 与 Confucius/SAFETY 对同一 T61A identity 均明确 `GO` 后才可写产品代码。

### T61B：candidate pre-merge differential

- baseline/candidate 使用两份 byte-identical fixture root，禁止在同一工作区顺序覆盖后比较；
- 九阶段逐方法与完整链比较 request/result、exception、transcript、raw artifact/report、tree/mode、调用顺序和副作用；
- 对 T61A Python-surface manifest 逐字段零差异，并重放 late-bound subclass/spy 矩阵；candidate engine 必须
  接收从 `self` 解析的 public callbacks，不得旁路 override/monkeypatch；
- 绑定 candidate commit/tree、normalizer version、LOC/branch/runtime ledger；零未批准差异；
- selector legacy→candidate→legacy→candidate 四个 receipt 均实际运行；
- targeted、full、Ruff、constraints、truth 与两个本地 reviewer current-identity PASS 后才允许 candidate PR。

## 8. 主线预发布稳定周期与 deletion

Candidate merge 后不创建版本/tag/GitHub Release/PyPI，不更新全局 CLI。对精确 merge tree：

1. required cross-platform checks 全绿；
2. wheel/sdist 构建并核对 private module 被正确打包，构建依赖与运行依赖预置到受控本地 wheelhouse；
3. 网络关闭后，两个 clean env 使用 `--no-index --find-links <wheelhouse>` 分别安装 wheel/sdist；证明
   build isolation 和运行依赖均未联网、未回读源码 checkout，再运行 Python-surface manifest、目标 help、
   dry-run 和九阶段链；
4. 至少两个 sibling project 使用安装产物 smoke；
5. selector rollback/reapply 与 T61B raw evidence 一致。

全部通过后才创建独立 deletion branch/PR。Deletion current-head 先完成本地双审、Codex 和 required checks，
合入后再从精确 deletion merge commit 建立一次性隔离 rollback worktree/branch，实际 revert 该 merge commit，
重跑 legacy route、Python-surface 与 selector rollback/reapply；销毁临时回退工作区后，再在 deletion
fresh-main 重复 targeted/full/platform/build/no-index offline install/sibling。两种状态均通过前，implementation
WI 保持 active；WI213 formal receipt 不得被冒充为产品完成证据。

## 9. 功能需求

- **FR-001**：formal 必须绑定 current-main 45-symbol/LOC/complexity/call/test 基线和唯一计量 recipe。
- **FR-002**：设计必须满足 §4 的无反射、无循环 import、无 stage-name 分支、无第二真值边界。
- **FR-003**：27 个 public callable、九组 DTO 的反射 surface 与 late-bound `self` dispatch，以及 CLI、
  artifact/授权/错误行为必须零未批准差异。
- **FR-004**：T61A 和双 readiness GO 必须发生在任何产品代码之前；旧 WI203/WI204 proof/hash 不得复用。
- **FR-005**：candidate 默认 legacy，T61B 后才切 candidate；candidate merge 时 legacy 完整保留。
- **FR-006**：candidate/stability/deletion 属同一 T66 工作包；deletion 使用独立 PR，删除前不得关闭。
- **FR-007**：RC-03～RC-07 任一超限立即 RC-09 No-Go，禁止扩大分母、scope 或 normalizer。
- **FR-008**：formal 内容由 LEAN/YAGNI 与 SAFETY/COMPAT 两位独立 Agent 对同一 formal-six identity 评审到 PASS0。
- **FR-009**：每个 mainline PR 遵守 Codex review、required-check heartbeat、merge 与 detached fresh-main 验收。
- **FR-010**：RC-08 前禁止版本/tag/Release/PyPI/全局 CLI；本项不关闭 GAP-03、WI-196 或总体发布门禁。
- **FR-011**：formal source inventory、root/scoped handoff 与 program truth 必须一致；隐式 IDE adapter refresh 不得混入。
- **FR-012**：GAP-15 必须由独立 T58/WI/branch/PR 在 T61A 前关闭；formal 仅登记 A/B 证据并恢复
  `.cursor/rules/ai-sdlc.mdc`，不得实施或把修复计入 T66 减重收益。

## 10. 成功标准

- **SC-001**：WI213 formal PR 相对 base 的 `src/tests逻辑/workflow/provider/rules/dependency/version` diff 为零；
  manifest exact test 仅机械替换 inventory/close 精确值且不增减测试逻辑/LOC。
- **SC-002**：45 methods=`3,638/3,305/386`、165 tests=`106+59` 可复算，预算 `522/712/720/2,918`
  数学闭合，无旧 claim 或过期 hash。
- **SC-003**：formal spec/plan/tasks 无占位或未决用户选择；parent+child formal-six 同 identity 双 PASS、findings=0。
- **SC-004**：constraints、program validate/truth、manifest exact、scope、handoff parity、diff-check 全绿；formal PR/Codex/checks/merge/fresh-main 有 receipt。
- **SC-005**：formal 关闭 receipt 经 lifecycle reconciliation 双审/mainline/fresh-main 收口后，只授权
  创建一个 T58/GAP-15 WI；T58 fresh-main 后才授权唯一 T66
  implementation WI，没有产品、selector、legacy deletion 或发布声明。
- **SC-006**：最终 T66 只有在 candidate + pre-release stability + independent deletion + post-deletion rollback
  全部证明后才能 `completed_reduction`；rollback 必须针对精确 deletion merge commit，终态满足切片≤720、
  净删≥2,918、原文件职责减少≥3,278。
- **SC-007**：WI213 formal 的 lifecycle reconciliation fresh-main 后，唯一下一执行项是
  T58/GAP-15；其五个只读命令 bytes/clean-tree
  与 help/invalid-input 不变，且 `init/link` valid/负路径 hook 时序零未批准差异的 fresh-main receipt 完成前，
  不创建 T66 implementation WI。

## 11. 冻结决策

1. 不要求用户逐条评审；两个对抗 Agent 代行 formal 内容审查，但不替代 L4 用户授权。
2. WI213 formal 与后续 implementation WI 分离；implementation 内 candidate/deletion 仍是同一 T66 工作包。
3. 采用“静态定义 + 显式 callable/type binding + 私有 engine”，拒绝反射、DSL、循环 import和未来扩展点。
4. Ruff 88 列反证确认九组显式 binding 不能藏入 5/15 行；冻结 binding/glue≤90，并以 module≤360、
   facade terminal≤45/candidate addition≤72 重新闭合预算；旧 691/2,947 与早期 701/2,937 均退役。
5. 公开版本只在 WI196 所有 spec/RC-08 完成后发布，不能用 WI213/T66 的局部成功提前发布。
6. WI213 新发现的 GAP-15 与 T66 产品切片分属不同根因和回退面；先独立关闭 T58，再进入 T61A，禁止
   为赶路线把 adapter 分发修复混进 formal、candidate 或 deletion PR。
