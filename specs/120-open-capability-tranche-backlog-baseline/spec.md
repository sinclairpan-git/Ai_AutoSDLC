# 功能规格：Open Capability Tranche Backlog Baseline

**功能编号**：`120-open-capability-tranche-backlog-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：`program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`、`specs/005-*`、`specs/009-*`、`specs/010-*`、`specs/012-*`、`specs/014-*`、`specs/020-*`、`specs/022-*`、`specs/025-*`、`specs/047-*`、`specs/050-*`、`specs/067-*`、`specs/070-*`、`specs/071-*`、`specs/083-*`、`specs/085-*`、`specs/091-*`、`specs/094-*`、`specs/095-*`、`specs/096-*`、`specs/100-*`、`specs/101-*`、`specs/103-*`、`specs/105-*`、`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`

> 口径：`120` 不是新的 capability audit，也不是第二套 program DAG。它只把 `program-manifest.yaml > capability_closure_audit` 中已经确认仍为 open 的能力，展开成可执行的 delivery streams 与 tranche backlog，供后续实现按批次连续落地。若 `120` 的表述与 root manifest 冲突，以 root manifest 为准。

## 问题定义

`119` 已经把“work item local truth”和“capability closure truth”正式拆层，根级机器真值现在能明确回答哪些能力簇仍是 `formal_only / partial / capability_open`。但当前仓库仍缺最后一层落地准备：

- root truth 只能说明“哪些能力未闭环”，还不能直接说明“下一批先实现什么”
- 历史 spec 大量采用 child baseline、prospective-only runtime cut、implementation slice、sync carrier 交织推进；只看编号顺序无法稳定排出实现优先级
- 若继续按单条 spec 口头解释，很容易再次回到“工单关了，但父能力没交付”的假收口
- 若不先形成 tranche backlog，后续每次开工都还要重复做一轮 capability audit，项目会继续卡在“知道没闭环，但没有可连续执行的 implementation queue”
- 当前 CLI 安装链路把 Claude/Codex/VS Code 等宿主写到非官方默认读取入口，并把 `ai-sdlc adapter activate` 的人工确认当成继续 `run` 的门禁；这证明“adapter 文件已生成”与“宿主真实接入成功”仍不是同一件事。`121` 已把该问题升级为 root truth，但 runtime tranche 仍未落地

因此，`120` 的目标不是重审 root truth，而是把已确认 open 的能力拆成一份可执行 backlog，满足三件事：

1. 从 root cluster 出发，而不是从单个 spec 头部状态出发
2. 每个 tranche 都明确缺的 carrier、依赖关系、收口条件和建议验证面
3. 明确哪些工单只是 sync/formal carrier，不能继续被误当成交付证明

同时，`120` 必须诚实处理评审过程中发现的 **root truth 外阻塞项**：若新问题属于当前 root open clusters 之外的关键跨层能力缺口，`120` 不能把它伪装成既有 stream 已覆盖；只能先标为 `pending_root_truth_update`，待 root truth 回写后再进入正式 tranche queue。

## 范围

- **覆盖**：
  - 将 root `capability_closure_audit` 的 7 个 open clusters 展开成 delivery streams
  - 把仍未闭环的能力进一步细化成 tranche backlog
  - 为每个 tranche 回填：来源范围、当前 closure class、缺失 carrier、依赖、退出条件、建议验证面
  - 明确 sync/formal carrier 与 implementation carrier 的区别
  - 给出推荐的 value-first 落地顺序
  - 记录评审中新发现但尚未进入 root capability truth 的关键阻塞，并明确其不得直接伪装成既有 stream 已覆盖
- **不覆盖**：
  - 修改 `program-manifest.yaml` 的 open cluster 机器真值
  - 宣称任何 open cluster 已闭环
  - 在本工单中直接实现 runtime / installer / writer / browser gate
  - retroactively 重写所有历史 `spec.md` 顶部状态
  - 新增第二套 frontend rollout DAG 或替换既有 `specs:` 依赖真值

## 已锁定决策

- root capability closure 的唯一机器真值仍然是 `program-manifest.yaml > capability_closure_audit`
- `120` 是派生执行 backlog，不是第二套 closure truth
- root 的 7 个 open clusters 在执行层细化为 9 条 delivery streams：
  - `S9` Agent adapter verified host ingress：`010`、`094`、`121`
  - `S1` 平台元能力基础链：`005-008`
  - `S2` Frontend contract / observation / gate 基础链：`009-018`、`065`、`077-078`
  - `S3` Program execute / remediation / provider / writeback / governance 主线：`019-040`
  - `S4` Final proof / publication / archive / cleanup 主线：`041-064`
  - `S5` P1 experience stability 运行时缺口：`066-071`
  - `S6` P2 solution + Stage 0 / frontend mainline delivery：`073`、`093-101`
  - `S7` Browser quality gate：`102-106`
  - `S8` Framework-only closure / frontend evidence class 生命周期：`079-092`、`107-113`
- `072`、`074`、`075`、`076`、`116`、`117`、`118`、`119`、`120` 都属于 root sync / formal carrier；它们可以修正文案与真值同步，但不是 capability delivery 证明
- 单个 work item 只有同时补齐 runtime surface、用户可见行为、测试/验证面，才可以作为 capability closure 证据；`formal baseline`、`prospective-only runtime cut`、`首批 implementation slice` 都不能直接等同父能力闭环
- 推荐排序采用 **user-visible mainline closure 优先**，不是单纯按编号顺序执行
- 若评审发现当前 root truth 未覆盖的关键阻塞，`120` 只能先把它登记为 `pending_root_truth_update`；在 root truth 回写后，再升级成正式 delivery stream

## Root Clusters 与 Delivery Streams

| Stream | 对应 root cluster | 范围 | 当前判断 |
|---|---|---|---|
| `S1` | `project-meta-foundations` | `005-008` | 仍是 formal baseline，未形成可交付 runtime surface |
| `S2` | `frontend-contract-foundation` | `009-018`, `065`, `077-078` | 有 sample self-check 与局部消费，但 scanner / attachment / gate 主链未闭环 |
| `S3` | `frontend-program-automation-chain` | `019-040` | execute/remediation/provider/writeback/governance 仍是 formal chain，缺 end-to-end runtime |
| `S4` | `frontend-program-automation-chain` | `041-064` | publication/archive/cleanup 有局部 consumption，但父能力仍未关 |
| `S5` | `frontend-p1-experience-stability` | `066-071` | `067-069` 有局部实现，`070-071` 仍 docs-only |
| `S6` | `frontend-mainline-delivery` | `073`, `093-101` | solution 已冻结，Stage 0 / host readiness 已有切片，但 apply executor / installer / file writer 未落地 |
| `S7` | `frontend-mainline-delivery` | `102-106` | browser quality gate 只有部分 runtime carrier，整链未闭环 |
| `S8` | `frontend-evidence-class-lifecycle` | `079-092`, `107-113` | validator / status / mirror / close-check 只有部分 runtime/backfill，父能力仍 open |
| `S9` | `agent-adapter-verified-host-ingress` | `010`, `094`, `121` | root truth 已冻结，但官方默认入口落位、自动 verify runtime、诚实 degraded/unsupported gate 仍未闭环 |

## 评审新增阻塞（已由 `121` 升格为 Root Truth）

本轮对抗审阅额外发现一个 **已实质阻断用户主线接入** 的 P0 缺口：

- 当前 `ide_adapter` 会把 Claude/Codex/VS Code 写入 `.claude/AI-SDLC.md`、`.codex/AI-SDLC.md`、`.vscode/AI-SDLC.md` 等非官方默认读取入口
- `run` 的当前门禁只要求 `adapter activate` 形成 `acknowledged`，并不能证明宿主已经真实读取或采纳框架约束
- `generic` 只能投放提示文件；像 `TRAE` 这类当前缺少厂商公开文档来明确默认读取入口与验证协议的目标，只能先归入 `generic`，不能单列为明确适配

这说明“真实适配成功”仍缺一个独立的 cross-cutting capability：**official/default ingestion surface materialization + host/plugin verification + honest degraded truth**。该缺口现已由 `121` 正式升级为 root open cluster，因此 `120` 必须把它放进正式 tranche queue，而不能继续伪装成现有 `S6` 的普通安装子任务。

## 关键未闭环证据

- `005`、`006`、`007`、`008` 的顶部状态仍是 baseline，而不是已交付能力
- `012` 只冻结 verify integration，不负责 scanner 实现；`014` 只为后续 `core / cli / runner / tests` 提供 baseline
- `020` 明确不是 auto-fix engine，也不做隐式 writeback；`022` 只定义 bounded materialization；`025` 只定义 handoff payload
- `047` 不默认 archive artifact persistence；`050` 明确只承诺 bounded cleanup，且不承诺真实删除工作区内容
- `067` 只有唯一首批 implementation slice；`070`、`071` 都明确停留在 docs-only formal freeze
- `095` 承诺确认后受控交付总线，但 `096` 只做到 host runtime plan；`100`、`101` 都明确不在本轮实现 executor / installer / file writer
- `103` 只冻结 browser probe runtime baseline，不声称 Playwright runner 已在本批实现；`105` 也只是首批 runtime slice
- `083` 明确“本轮不要求任何命令已经实现该 contract”；`085` 是 prospective-only first runtime cut；`091` 仍是“首批 implementation slice 进行中”
- `010` 明确当前 file-based adapter 的上限只是 `acknowledged`/soft prompt，不覆盖 host-verifiable activation；但当前实现仍把 `.claude/AI-SDLC.md`、`.codex/AI-SDLC.md`、`.vscode/AI-SDLC.md` 这类非官方默认入口统一视为 `installed`
- `run` 现在要求的仍是人工 `adapter activate`，不是 IDE/插件已读取官方入口的机器证据；这意味着 Stage 0 / mainline install 还缺真正的“安装成功定义”

## 用户故事与验收

### US-120-1 — Maintainer 需要从 capability truth 直接得到可执行 backlog

作为 **maintainer**，我希望在 root capability truth 已经对齐后，能直接得到“先做哪条能力、每条能力拆成哪些 tranche”的 backlog，而不是继续靠口头审计决定下一批工单。

**验收**：

1. Given 我查看 `120`，When 我从 root open clusters 往下读，Then 可以看到对应的 delivery streams 与 tranche backlog  
2. Given 某条 spec 顶部写着“已完成”或“已冻结”，When 其父能力仍在 open cluster 中，Then `120` 仍会把它视为未闭环流的一部分

### US-120-2 — Implementer 需要每个 tranche 都有缺口与退出条件

作为 **implementer**，我希望每个 tranche 都明确缺的 carrier、依赖、退出条件与建议验证面，这样后续派生工单时就不需要再次重新审计全仓。

**验收**：

1. Given 我选中任一 tranche，When 我查看其描述，Then 可以看到来源范围、缺失 carrier、依赖与 exit criteria  
2. Given 我准备新开 implementation work item，When 我从 `120/tasks.md` 派生，Then 不需要再回头判断该 tranche 是否只是 sync/formal carrier

### US-120-3 — Reviewer 需要 sync carrier 与 implementation carrier 分离

作为 **reviewer**，我希望 `072/074/075/076/116/117/118/119/120` 这类 sync/formal carrier 被明确标成“非 capability delivery 证明”，这样以后不会再出现“同步真值的工单被误读成能力已交付”。

**验收**：

1. Given 我审阅 `120`，When 我查看非 implementation carrier 规则，Then 可以明确读到 sync/formal carrier 不等于 capability closure  
2. Given 后续又出现 root sync / wording sync 工单，When 对照 `120`，Then 不会再把它们放进 delivery backlog

### US-120-4 — Operator 需要“一次安装就能用”的真实适配闭环

作为 **operator / 小白用户**，我希望安装命令自动识别宿主/插件、写到官方默认读取入口并自动验证是否真的生效，而不是再让我执行 `adapter activate` 之类人工确认，这样“已安装”才真正等于“可进入下一步”。

**验收**：

1. Given 当前仓库只完成了 adapter 文件投放和人工确认，When 我审阅 `120`，Then 可以明确看到这仍被视为未闭环能力缺口，而不是已完成安装体验  
2. Given `generic` 目标缺少官方自动加载/验证协议，When 我查看 `120`，Then 只能看到 `S9` 下的 `degraded / unverified / unsupported` 等诚实状态，而不是“已适配成功”；这也包括当前未获厂商公开文档明确支持的 `TRAE`

## 功能需求

| ID | 需求 |
|----|------|
| FR-120-001 | `120` 必须明确声明 root `capability_closure_audit` 是唯一机器真值，`120` 只作为派生 backlog |
| FR-120-002 | `120` 必须把 root 的 7 个 open clusters 展开成 9 条 delivery streams |
| FR-120-003 | `120/tasks.md` 必须为每个 tranche 记录来源范围、当前 closure class、缺失 carrier、依赖、退出条件与建议验证面 |
| FR-120-004 | `120` 必须明确 sync/formal carrier 不得被当作 capability delivery 证明 |
| FR-120-005 | `120` 必须给出 value-first 的实现顺序，优先打通 frontend mainline delivery 与 browser gate |
| FR-120-006 | `120` 不得擅自把任何 open cluster 改写为 closed / implemented |
| FR-120-007 | `120/task-execution-log.md` 必须明确本工单只回填 backlog，不执行后续 tranche |
| FR-120-008 | 若评审发现未被 root `capability_closure_audit` 覆盖的关键阻塞，`120` 必须把它记录为 `pending_root_truth_update`，不得私自伪装成既有 stream 已覆盖 |
| FR-120-009 | `120/tasks.md` 对 `pending_root_truth_update` 阻塞必须单独建档，明确其来源证据、预期 root truth 回写方向与禁止绕过的下游门禁 |

## 成功标准

- **SC-120-001**：root open clusters 都被映射到可执行的 delivery streams
- **SC-120-002**：后续实现者可以直接从 `120/tasks.md` 派生 implementation work item，而不需要再重新做全仓 capability audit
- **SC-120-003**：sync carrier 与 implementation carrier 的边界被正式写回仓库
- **SC-120-004**：frontend mainline delivery、browser gate、contract foundation 等高价值缺口拥有明确的优先级与 tranche 入口
- **SC-120-005**：若未来再次发现未进入当前 root truth 的关键阻塞，仓库会先诚实暴露为 `pending_root_truth_update`；一旦 root truth 回写完成，则可升级为正式 stream/tranche

---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
  - "specs/025-frontend-program-provider-handoff-baseline/spec.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
