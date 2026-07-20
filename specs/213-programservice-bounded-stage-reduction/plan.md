---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/212-reduction-candidate-selection/development-summary.md"
---
# 实施计划：ProgramService 九阶段精益减重正式合同

**编号**：`213-programservice-bounded-stage-reduction`
**日期**：2026-07-19
**规格**：`specs/213-programservice-bounded-stage-reduction/spec.md`
**当前交付**：formal-only；不执行产品代码
**风险**：L3

## 1. 策略

WI213 先把 current-main 事实、最小设计、兼容矩阵、预算、T61A/B 和两 PR 删除路线冻结并经双 Agent
对抗评审，再由 mainline receipt 授权后续唯一 implementation WI。顺序不可压缩为一个大 PR：

```text
WI213 formal
  -> fresh-main receipt
  -> T58/GAP-15 standalone fix delivery + closure receipt fresh-main
  -> implementation WI / T61A / dual readiness GO
  -> candidate PR（默认 candidate，legacy 保留）
  -> mainline pre-release stability（不发版本）
  -> independent legacy-deletion PR
  -> post-deletion rollback/fresh-main acceptance
  -> T66 completed_reduction
```

该拆分把三类风险隔离：formal 回退不影响运行时；candidate 可用内部 selector 即时切回；删除后可先
revert deletion PR 恢复 legacy。它不拆散 T66 工作包，也不允许删除前关闭。

## 2. 技术背景

- **语言/版本**：Python 3.11.15；`uv`；repo-source `ai-sdlc`。
- **产品基线**：217 files / 107,321 LOC；`program_service.py`=17,474；`program_cmd.py`=7,057。
- **目标**：九 stage / 五 family / 45 methods=`3,638 physical / 3,305 executable / branch proxy 386`。
- **测试库存**：106 unit + 59 integration=`165`，物理 6,317 LOC；current-main 2.77s。
- **运行依赖**：现有 stdlib/dataclass/Path/PyYAML；禁止新增依赖。
- **持久化面**：九类 YAML/Markdown/report 和 workspace file tree；schema/path/bytes 不变。
- **平台**：Windows/macOS/Linux；PowerShell、wheel/sdist、clean install、offline、sibling projects。
- **本地主机例外**：PowerShell 的既知 .NET regex assembly 问题只允许本地 Python3.11/zsh fallback；
  Windows/PowerShell 仍由 CI/安装 smoke 强制覆盖。

## 3. 治理响应

| 门禁 | 计划响应 |
|---|---|
| LP-01 行为优先 | 零未批准 differential 是 merge 前硬门禁，LOC 不能抵消差异 |
| LP-02/03/04 | 只服务九个当前调用者；静态 definition 只编码现有差异；不造公共/future abstraction |
| LP-05 | 27 个 public method 留在 ProgramService 作 thin facade |
| LP-06 | DTO、path/schema/status 常量继续使用现有 canonical source，不复制 YAML/schema |
| LP-08 | 复用 165 tests；参数化可减测试实现，场景/断言/平台不得减少 |
| LP-10/12 | 预算和 terminal deletion 都是硬条件；无无限期 shadow |
| FR-07 | candidate merge 后走主线预发布稳定周期，不发布版本，再独立删旧 |
| RC-01～10 | spec §5 逐项冻结；T61A/B 为 pre-merge gate |
| GAP-09～11 | 每阶段 truth/source/adapter/inheritance 影响分析；漂移即 fail-closed 重开 |
| GAP-15 | formal 只登记/恢复；T58 独立 RED/GREEN delivery + closure receipt fresh-main 后才进入 T61A |
| PR protocol | 每个 PR push、Codex current-head review、check heartbeat、merge、fresh-main |

## 4. WI213 formal 变更边界

### 4.1 允许修改

```text
specs/213-programservice-bounded-stage-reduction/{spec.md,plan.md,tasks.md,task-execution-log.md}
specs/213-programservice-bounded-stage-reduction/development-summary.md（terminal formal closure 才创建）
specs/196-ai-sdlc-lean-code-self-reduction-governance/{spec.md,plan.md,tasks.md}
specs/196-ai-sdlc-lean-code-self-reduction-governance/{task-execution-log.md,development-summary.md}
program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
.ai-sdlc/state/codex-handoff.md
.ai-sdlc/work-items/213-programservice-bounded-stage-reduction/codex-handoff.md
tests/integration/test_repo_program_manifest.py（只机械替换 inventory/close 精确值）
```

Formal terminal 允许 truth sync 的机械派生字段变化。`program-manifest.yaml` 中 WI213 必须显式
`depends_on: [196-ai-sdlc-lean-code-self-reduction-governance]`。Root/scoped handoff 必须 byte-identical。

### 4.2 禁止修改

```text
src/**
tests/**（上述 manifest 两值例外以外）
.github/workflows/**
.ai-sdlc/providers/**
.ai-sdlc/rules/**
AGENTS.md
pyproject.toml
uv.lock
版本/tag/Release/PyPI/全局 CLI
```

`workitem init` 与当前 `workitem plan-check` 触发的 `.cursor/rules/ai-sdlc.mdc` refresh 不属于 formal，
必须恢复到 base 字节并在 execution log 留痕。后者登记为 GAP-15；本分支不得修改 callback/source 修复它。

## 5. 下游唯一允许的源码结构

```text
src/ai_sdlc/core/
├── program_service.py
│   ├── 原九组 DTO（不移动）
│   ├── 9 个 typed/path binding（binding/import/selector glue≤90）
│   └── 27 个 public thin facade（candidate addition≤72；terminal body≤45）
└── _program_bounded_stage.py
    ├── frozen private definition
    ├── 9 个 current-stage definition
    ├── cross-spec strategy + bounded-stage strategy
    └── request/execute/write/payload/load engine（总计≤360；每函数≤50）
```

### 5.1 依赖方向

`program_service.py -> _program_bounded_stage.py` 单向依赖。私有模块不 import ProgramService、DTO、CLI；
typed constructor/callback 由 ProgramService 显式传入。禁止底部/延迟循环 import、字符串 method dispatch、
`getattr`、stage-name branching、运行时 registration 或 YAML-driven DSL。

现有 public-to-public 调用保持 late-bound：execute 默认 request 必须经 `self.build_*`，writer 默认
request/result 必须经 `self.build_*`/`self.execute_*` 解析后再作为 callback 注入 private engine。是否 fallback
严格保留 legacy `provided_value or callback()` truthiness：`None` 与 falsey 显式对象仍 fallback，truthy 值才
绕过；`generated_at` 同样保留 `provided_value or utc_now_z()`。不得从 module-level binding 直接调用并旁路
subclass override、`patch.object`、clock spy、调用次数/顺序或异常传播。

### 5.2 差异表达

静态 definition 只含当前九 stage 的：artifact/step path、state/result/summary key、upstream key、固定文本和
strategy callable。Cross-spec 的 manifest path validation 与直接 spec write 使用专职 strategy；其余八阶段
复用现有 bounded-step strategy。Strategy 由 definition 绑定，因此 engine 不判断 stage name。

DTO 构造仍由原类完成，字段 adapter 产出显式 dict 后立刻传给 typed constructor；不得以通用 object、
动态 attribute 或未校验 mapping 向 CLI 泄漏。Payload key 顺序由 definition 的固定 tuple/构造顺序决定，
不得依赖排序 normalizer。

## 6. 阶段计划

### Phase 0：WI213 formal admission（本工作项执行）

1. 从 `main@e184c8e2` 冻结 Git/Python/source/truth/release 身份。
2. AST 复算 45 methods、fan-in/out、branch proxy、测试函数/LOC；运行 165 tests。
3. 写 spec/plan/tasks/log，最小更新 WI196 parent formal。
4. A/B 证明 `program validate` bytes 稳定而 `workitem plan-check` 仍改写 adapter；登记 GAP-15/T58并恢复 bytes。
5. 对 parent+child formal-six 计算唯一 identity；Pascal 审 LEAN/YAGNI，Confucius 审 SAFETY/COMPAT。
6. 任一 finding 成立则最小修正；任一 formal-six 字节变化使双方 verdict 同时失效，重审至同 identity PASS0。
7. 创建 terminal formal summary，机械同步 manifest exact/truth/handoff；再对 final current identity 双审。
8. Push/PR、`@codex review`、heartbeat required checks；merge 后 detached fresh-main 验收。

**完成**：只产生 mainline formal receipt，并授权创建独立 T58/GAP-15 WI；不授权创建 T66 implementation
WI 或直接写产品。
**回退**：revert formal PR，产品行为不变，下游 authorization 立即失效。

### Phase 1：T58 / GAP-15 独立修复（下游执行）

1. 从 formal fresh main 创建独立 branch/worktree/canonical WI。
2. 用 real-hook fixture 对 `plan-check/guard/close-check/branch-check/truth-check` 及 help/invalid-input 建立
   adapter/config/working-tree bytes 与输出 RED；固定 `init/link` valid、missing option、dirty/preflight、
   no project、no checkpoint、hook exception 的 hook 次数/时序、退出码、输出与写入。
3. 只修正 workitem subapp 的 read/write dispatch；不改 adapter 算法、ProgramService 或 T66 测试。
4. 双 Agent、targeted/full/Ruff/constraints、平台、PR/Codex/checks/merge/detached fresh-main 全绿后关闭。

**停止**：需要关闭全部 workitem adapter、改变生成内容或扩大到另一 CLI family。
**回退**：revert T58 独立 PR；T66 继续阻断在 T61A 前。
**当前执行状态**：WI214 implementation PR #162 / merge `2845fedc`、delivery PR #163 / merge
`60fe6d90` 与 closure receipt PR #164 / merge `7922956d` 均已 detached fresh-main 验收；GAP-15/T58
已关闭，Phase 2 的唯一 implementation WI215 已创建并正在执行 T61A，双 readiness GO 前产品代码零改动。

### Phase 2：Implementation WI / T61A readiness（下游执行）

1. 从 T58 fresh main 创建独立 branch/worktree和 canonical WI，不复制第二套 contract。
2. 在任何产品代码前，冻结exact165 ordered nodes、目标test/fixture/config blob、两个独立basetemp PASS和
   selector warm-up+20原始duration。
3. 冻结toolchain、architecture ledger与public callable/DTO结构manifest；唯一recorder≤200，只生成
   JSON-primitive五section原子receipt/verify，不在T61A重复实现动态差分矩阵。
4. 证明candidate product shadow≤522、proof≤290，且
   `shadow + actual current proof + frozen future proof reserve≤729`；当前implementation WI以既有测试文件
   中的唯一test-only runner承载三方replay并逐文件/symbol冻结future reserve=90；
   个别上限不得相加使用；两 reviewer 对同一 proof identity 双 `GO`。

**停止**：任一 reviewer NO-GO、proof/architecture 超预算、legacy 不稳定或隔离写边界不可靠。
**回退**：NO-GO 先持久化不可变 receipt、commit/tree、raw-evidence hash、review verdict 和关闭状态，再放弃
产品路线；不得删除唯一证据载体，运行时保持未修改。

### Phase 3：TDD candidate shadow

1. 先写 candidate seam/differential RED；不得修改 assertion 迎合 candidate。
2. 新增唯一 private module，逐函数≤50；先接 `cross_spec_writeback` 证明特殊 strategy。
3. 按 guarded→broader→final governance→persistence→persisted proof→publication→closure→archive 接入。
4. 每个 public method 的内部 selector 初始默认 legacy；未迁移 stage 一律 legacy。
5. 每stage以既有测试文件中的唯一test-only runner和三套isolated project环境执行原始legacy、current
   legacy、candidate完整dynamic matrix；leaf覆盖`pythonpath=<leg-root>/src`并用importlib mode，先验真
   checkout/import/route provenance；从T61A receipt展开九组disjoint exact node IDs，分组前拒绝任何
   thread_archive/project_cleanup node，三腿worker直接选择
   candidate测试定义中的累计节点并逐项对账JUnit，T61B union精确106+59；两个测试文件各九个seed helper
   逐symbol source SHA验真，仅为未输出ledger/性能增加capture，再以同一behavior root证明零差异；
   同时记录commit、module/route/glue/total LOC、branch proxy、tests；product peak≤522。

**停止**：需要第二 module/领域、DTO 移动、反射/DSL/stage branch、公共开关或任何差异。
**回退**：selector 指回 legacy，删除 candidate module/guard；legacy body 始终在。

### Phase 4：T61B、candidate PR 与 fresh-main

1. 固定candidate commit/tree，以byte-identical seed三方运行原始legacy/current legacy/candidate。
2. 三方比较Python-surface manifest、loader/builder、late-bound dispatch、dataclass、fault/termination/retry、
   exception、transcript、raw bytes、tree/mode/write order、transient sentinel、副作用与p50/p95。
3. 执行 legacy→candidate→legacy→candidate；每次重跑目标矩阵。
4. Run 165、full、Ruff、constraints、validate、truth、manifest；双 reviewer current identity PASS0。
5. Candidate 默认 candidate、legacy 完整保留；`actual peak product + actual total proof≤729`后走
   PR/Codex/check/merge/fresh-main。

**完成**：candidate mainline 可用但 T66 仍 active。
**回退**：selector-only commit 指回 legacy；不删除任何 legacy。

### Phase 5：主线预发布稳定周期

对 candidate merge tree 运行 required cross-platform、wheel/sdist、两个 clean install、offline smoke、
两个有选择理由的 sibling project 和 selector rollback/reapply。安装产物必须包含 private module；构建/运行
依赖先进入受控 wheelhouse，断网 clean env 以 `--no-index --find-links` 分别安装 wheel/sdist，且 build
isolation、Python-surface smoke 与离线运行均不能联网或回读源码 checkout。该阶段无 tag/Release/PyPI/global CLI。

**停止**：任一平台、包、offline、sibling、性能或 rollback 失败；修复仍在 candidate work package，
不得开始 deletion。

### Phase 6：独立 legacy deletion

1. 从通过稳定周期的 candidate merge commit 创建独立 deletion branch/PR。
2. 删除 45 个 legacy full body、18 个失活 private method、legacy selector branch 和仅 legacy 使用的 glue；
   保留 27 public facade。
3. 复算 terminal≤720、net delete≥2,918、ProgramService responsibility reduction≥3,278、branch proxy≤90。
4. 以T61A原始legacy、冻结pre-deletion candidate-merge current legacy、deletion-head candidate三腿重跑
   完整dynamic matrix，并运行Python surface、165/full/Ruff/governance、平台/build/no-index offline install/sibling。
5. 双 reviewer、Codex/checks 对 deletion current head 全绿后 merge；此时 T66 仍 active。
6. 从精确 deletion merge commit 建立一次性隔离 rollback worktree/branch，实际 revert merge commit，证明
   legacy route 与 selector rollback/reapply；销毁临时回退工作区后回到 deletion fresh-main，重复关键
   surface/differential/install/clean 验证。
7. 回到deletion fresh-main后，仍以T61A原始legacy、冻结pre-deletion current legacy、fresh-main candidate
   三腿重跑完整dynamic matrix；post-merge rollback receipt与deletion fresh-main全绿后才关闭implementation WI/T66。

**回退顺序**：先 revert deletion PR 恢复 legacy，再 selector 指回 legacy；必要时再 revert candidate PR。

### Phase 7：WI196 路线继续与版本发布

T66 完成只更新 GAP-03/RC ledger；GAP-04～06、其他 ProgramService domain、`program_cmd.py≤400`、全产品
10% 等剩余 spec 继续执行。只有 WI196 全部任务和 RC-08 终态证明完成，才启动新版本 release skill/
发布流程；T66 不单独发布。

## 7. 关键验证矩阵

| 路径 | 主验证 | 阻断 |
|---|---|---|
| 45-symbol baseline | Python AST physical/executable/header/branch | 任一集合/数字漂移未解释 |
| call graph | AST Call + outside-service scan | private 外部消费者或公共 surface 漏项 |
| legacy tests | 精确 `-k` selector 165 | 数量不是 106+59 或任一失败 |
| Python surface | versioned inspect/dataclasses manifest + late-bound subclass/spy | signature/DTO/dispatch 任一差异 |
| service differential | 三方 dataclass/exception/call/tree/raw bytes | 任一未批准差异 |
| CLI differential | 9 help/mode/failure/full chain stdout/stderr/exit | 任一未批准差异 |
| authorization | dry-run/confirm/execute/write order/external sentinel | 新写入或越权 |
| recovery | write boundaries + KeyboardInterrupt/SystemExit/process termination | retry/final tree 不一致 |
| performance | warm-up + ≥20 samples p50/p95 | p95 > baseline 110% 且复测成立 |
| budget | per-commit AST/LOC/branch ledger | product>522、proof>290、product+proof>729、terminal>720 |
| package/platform | three OS + wheel/sdist + wheelhouse no-index offline install | 联网/checkout/import/resource/encoding/PowerShell failure |
| sibling | ≥2 chosen projects, installed artifact | 使用 checkout 或任一 smoke 失败 |
| rollback | selector round-trip；exact deletion merge post-merge actual revert | 只反转未合并分支或恢复失败 |
| governance | constraints/validate/truth/manifest/parity/scope | non-ready、unmapped、unexpected missing/diff |

## 8. Formal identity 与对抗评审

Review target 固定为 parent 与 child 各自 `spec.md + plan.md + tasks.md` 六文件。按 repo-relative path
ordinal 升序；每行：

```text
<lowercase file sha256><two spaces><repo-relative path>\n
```

对含最后 LF 的 UTF-8 payload 再做 SHA-256。任何六文件变化使两方 PASS 同时失效。Review receipt 必须
含 agent、dimension、HEAD/tree、combined hash、reviewed_at、findings、dispositions、verdict。

- Pascal：范围、YAGNI、直达性、预算、是否移动/过度实现、删除闭环。
- Confucius：功能/DTO/CLI/artifact/授权/异常/平台/安装/offline/sibling/rollback、truth/release 边界。

双方必须对相同 committed+clean identity 明确 `PASS` 且 actionable findings=0；不得拼接不同轮次 verdict。

## 9. 分支、PR 与提交边界

| 阶段 | 分支/PR | 必要事实 |
|---|---|---|
| formal | `feature/213-programservice-bounded-stage-reduction-docs` | docs/truth only；mainline receipt |
| GAP-15 | WI213 后续独立 T58 implementation/delivery/receipt PR | read-only bytes stable；`init/link` unchanged；closure receipt fresh-main |
| T61A/candidate | T58 后续 WI 的独立 candidate branch/PR | legacy retained；candidate default；T61A/B |
| deletion | 同 implementation WI 的独立 deletion branch/PR | candidate baseline exact；legacy delete/rollback |
| release | 仅 RC-08 全局终态后的 release branch | tag/Release/PyPI/global CLI 同版本 |

每个阶段提交必须保持逻辑单一；review/check 后文件变化必须重审。不得把 future merge hash 写进受审 formal，
也不得用 lifecycle reconciliation 文案冒充尚未发生的证据。

## 10. 开放问题与停止判定

没有用户决策项。Formal 对抗 reviewer 可以提出范围内 finding；如果实际代码证明 360/522/290/729/720 任一
预算不可达，结论不是自动扩预算，而是 RC-09 No-Go 或回到新的 formal review。任何公共行为、L4 迁移或
发布提前请求必须另行取得用户授权。
