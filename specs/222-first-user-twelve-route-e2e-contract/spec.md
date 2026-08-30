# 功能规格：跨平台首次用户十二路线证据合同

**功能编号**：`222-first-user-twelve-route-e2e-contract`
**创建日期**：2026-08-30
**状态**：P3-A formal/admission；runtime 未授权
**真值基线**：`origin/main@2e507df62c65cdd6d3137764bb492dc445a82074`
**发布证据基线**：GitHub Release `v0.9.8` / tag commit `4f3e55c300dab20fb4fea93818d79394a927f77e`（证据快照：2026-08-30）
**关联路线图**：`docs/FRAMEWORK_ROADMAP.zh-CN.md`

## 1. 目标与边界

本工作项把 P3 的“Windows AMD64、macOS arm64、Linux AMD64 × 空项目/已有项目 × 在线/离线”冻结为 12 条可逐路验收的首次用户合同，并对每条路线现有证据做 `proven / partial / missing` 分类。交付物是 formal 真值、缺口去重结果和后续最小实现薄片建议，不是 P3 runtime 实现。

### 1.1 本次覆盖

- 固定 12 条路线的 ID、平台、项目模式、资产获取模式和证据字段。
- 只以远端主线基线中的用户指南、安装器、GitHub workflow、release/tag 和可复核运行记录作为证据。
- 区分 PR 本地构建产物重放与正式 release asset 证明，禁止互相替代。
- 形成共性缺口、平台特有缺口、ROI、止损条件和一个最小后续实现薄片。
- 同步 Program Truth 清单、路线图状态和由新增 formal work item 引起的固定库存期望。

### 1.2 本次不覆盖

- 不修改 `src/`、安装器、GitHub workflow、用户指南正文、测试行为、release asset、版本号或发布状态。
- 不启动 D2 多能力补缺、v0.9.9、P4、全仓瘦身、ProgramService 重写或历史执行日志回填。
- 不使用产品站、比赛材料、本地材料分支、未合并 worktree 或参赛版实现作为主线真值。
- 不创建 `development-summary.md` 来人为提高 close materialized 计数。
- 唯一允许触达测试的情况，是新增 WI222 后同步 `tests/integration/test_repo_program_manifest.py` 的固定库存期望；该调整不得改变测试逻辑或 runtime 行为。

### 1.3 可重放的发布证据基线

本次 `0/12 proven、12/12 partial、0/12 missing` 结论固定评估以下正式发布事实，后续发布不得悄然替换本批基线：

- Release/tag：`v0.9.8`，GitHub release 发布于 `2026-08-27T14:51:19Z`，tag/target commit 为 `4f3e55c300dab20fb4fea93818d79394a927f77e`。
- Windows AMD64 asset：`ai-sdlc-offline-0.9.8-windows-amd64.zip`，GitHub asset digest `sha256:0ed406cc9280a285478fdff5e52b322cce6331c7ed6769a8b50099a4ef4bdc72`。
- macOS arm64 asset：`ai-sdlc-offline-0.9.8-macos-arm64.tar.gz`，GitHub asset digest `sha256:b203961720e8f3b70f876b421cb663310c840cd715b5692d602a388d7b5fe897`。
- Linux AMD64 asset：`ai-sdlc-offline-0.9.8-linux-amd64.tar.gz`，GitHub asset digest `sha256:b5ea4627f6ff82f4beb459b355946de44b425abf218ba9bc98d08491abc57247`。
- Build run：`Release Build` run `33084090992`，`workflow_dispatch`，同一 head SHA，结论 `success`。
- Released-asset run：`Release Artifact Smoke` run `33084560424`，`release` event，同一 head SHA，结论 `success`。
- 直接入口：`https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/v0.9.8`、`https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/33084090992`、`https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/33084560424`。

这些事实补齐的是“被评估对象可定位”，不自动补齐任一路线的生命周期、`Result / Next`、成功回执和主动恢复字段，因此不改变严格路线结论。

## 2. 用户场景与测试

### 用户故事 US-222-1：首次用户获得可复核的成功路线（优先级：P0）

作为第一次使用 AI-SDLC 的用户，我希望我所处的平台、项目状态和资产获取方式对应一条自包含路线，以便我能安装、初始化或接入项目、看到 `Result / Next`、验证成功，并在故障后按本路线恢复。

**优先级说明**：P3 的用户价值来自“新用户真的能走通”，而不是仅证明资产存在；没有逐路合同，就无法判断后续实现是否真正补齐用户闭环。

**独立测试**：任选一条路线，仅依赖该路线证据记录，即可回答资产来源与完整性、安装命令、`init/adopt`、`Result / Next`、成功回执、故障恢复及版本绑定；任一字段缺失时不得标记为 `proven`。

**验收场景**：

1. **Given** 一条路线拥有用户指南和安装 smoke，但缺少正式资产 SHA256 或主动恢复证据，**When** 评审其状态，**Then** 状态必须为 `partial`，不能因共享 smoke 通过而升级为 `proven`。
2. **Given** 一条路线完整记录了正式 tag、资产完整性、安装、项目生命周期、`Result / Next`、成功回执和恢复证据，**When** 在干净环境复核，**Then** 才能标记为 `proven`。

### 用户故事 US-222-2：维护者以共享合同控制投入和膨胀（优先级：P0）

作为框架维护者和评审者，我希望 12 条路线复用一个证据模型与少量平台适配，以便后续优先补共性高价值缺口，而不是复制 12 套流程或围绕细枝末节不断扩张。

**优先级说明**：参赛版历史已证明，对抗实现若缺少 ROI 与退出条件，支撑代码会超过核心特性。本工作项必须先冻结最小合同和停止条件，再决定 runtime 投入。

**独立测试**：证据表必须覆盖 12/12 路线、共性缺口只能登记一次并映射受影响路线、后续建议最多一个薄片，且任何建议都不得绕过新的 execute 授权。

**验收场景**：

1. **Given** 多条路线缺少同一种 release asset 完整性验证，**When** 制定后续方案，**Then** 必须优先设计共享验证步骤，不得复制成 12 套独立实现。
2. **Given** 新增方案开始引入第二套状态机、证据 ledger 或大量平台重复 workflow，**When** 进行 ROI 复核，**Then** 触发 No-Go 或重新定界，而不是为追求形式完备继续扩张。

### 2.1 边界情况

- GitHub runner 或目标架构暂时不可用、且无法取得可复核证据时，该路线状态保持 `missing`；交付过程可以因需要用户权限而暂停，但不得把 `needs_user` 写入路线三态，也不得用模拟结果冒充干净环境证明。
- PR 内构建并安装成功，只证明候选产物，不证明已发布 asset 与 tag/SHA256 绑定。
- 只校验 `AGENTS.md`、业务文件或安装后文件 hash，不能替代下载 archive 的发布完整性校验。
- 指南写明恢复命令但 workflow 未主动制造故障并执行恢复时，恢复字段只能算文档证据，路线仍为 `partial`。
- “在线”表示从正式 release/tag 获取资产；“离线”表示从预先传入且有完整性信息的离线包安装，不能在执行过程中隐式依赖网络获取产品资产。
- 已有项目路线必须证明 `adopt` 或等价接入行为不会破坏既有业务文件；空项目路线必须证明 `init` 创建可用项目入口。

## 3. 十二路线合同

### 3.1 路线 ID

| 路线 | 平台/架构 | 项目模式 | 获取模式 |
|---|---|---|---|
| R01 | Windows AMD64 | 空项目 | 在线 |
| R02 | Windows AMD64 | 已有项目 | 在线 |
| R03 | Windows AMD64 | 空项目 | 离线 |
| R04 | Windows AMD64 | 已有项目 | 离线 |
| R05 | macOS arm64 | 空项目 | 在线 |
| R06 | macOS arm64 | 已有项目 | 在线 |
| R07 | macOS arm64 | 空项目 | 离线 |
| R08 | macOS arm64 | 已有项目 | 离线 |
| R09 | Linux AMD64 | 空项目 | 在线 |
| R10 | Linux AMD64 | 已有项目 | 在线 |
| R11 | Linux AMD64 | 空项目 | 离线 |
| R12 | Linux AMD64 | 已有项目 | 离线 |

### 3.2 每条路线的最小证据字段

1. `route_id`：R01–R12 中唯一 ID。
2. `environment`：真实 OS、架构、runner/镜像与干净环境边界。
3. `project_mode`：空项目或已有项目，以及前置文件状态。
4. `acquisition_mode`：在线 release 获取或离线包输入，禁止模糊混用。
5. `source_binding`：仓库、正式 tag、commit 与 workflow event/run 绑定。
6. `asset_integrity`：资产名、版本和发布 SHA256 或等价完整性证明。
7. `installation`：用户可复制的安装或升级步骤及退出码。
8. `lifecycle`：空项目执行 `init`；已有项目执行 `adopt` 或等价受保护接入。
9. `result_next`：捕获用户可见的 `Result / Next`，并验证下一步与路线一致。
10. `success_receipt`：版本、状态、关键产物或业务文件保留的可复核回执。
11. `fault_recovery`：主动制造至少一个路线相关故障并验证本地恢复入口。
12. `evidence_links`：指南、workflow、run、release/tag、checksum 的直接证据位置。

### 3.3 状态语义

- `proven`：12 个字段均有同一正式版本或可解释连续版本链的真实、可复核证据。
- `partial`：存在指南或自动化证据，但至少一个必需字段缺失、仅为共享/间接证明，或证据绑定不完整。
- `missing`：没有足以执行或复核路线的有效证据，或目标真实环境不可获得。

## 4. 基线证据普查

严格按上述合同，当前结论是 **0/12 fully proven，12/12 partial，0/12 missing**。这不表示 12 条路线要从零实现：用户指南已覆盖全部组合，且三平台安装/发布 smoke 提供了大量共享证据；缺口集中在自包含绑定、完整性、项目模式矩阵和主动恢复。

| 路线 | 当前状态 | 已有主线证据 | 仍缺的自包含字段 |
|---|---|---|---|
| R01 | partial | `USER_GUIDE.zh-CN.md` 空项目/Windows/在线说明；Windows 与 release smoke 的共享安装证据 | 正式 archive SHA256、完整空项目在线链、主动恢复、同版本绑定 |
| R02 | partial | `windows-user-guide-e2e.yml` 已有项目在线安装、`init/adopt`、`Result / Next`、业务文件保留 | 正式 release event/asset SHA256、主动恢复、发布版本自包含绑定 |
| R03 | partial | `USER_GUIDE.zh-CN.md` 空项目/Windows/离线说明；`windows-offline-smoke.yml` 离线安装与 init 片段 | 完整空项目链、离线包完整性绑定、主动恢复 |
| R04 | partial | Windows 离线安装共享 smoke；指南已有项目接入说明 | 完整已有项目 adopt/保留证据、离线包完整性、主动恢复 |
| R05 | partial | macOS 在线指南；`release-artifact-smoke.yml` 的 macOS asset 安装 smoke | 空项目 init、`Result / Next`、archive SHA256、主动恢复、同版本链 |
| R06 | partial | macOS 在线指南；release asset 安装共享证据 | 已有项目 adopt/保留、`Result / Next`、archive SHA256、主动恢复 |
| R07 | partial | macOS 离线指南；`posix-offline-smoke.yml` 的 macOS arm64 离线安装 smoke | 空项目 init、离线包完整性、`Result / Next`、主动恢复 |
| R08 | partial | macOS 离线指南；POSIX 离线安装共享证据 | 已有项目 adopt/保留、离线包完整性、`Result / Next`、主动恢复 |
| R09 | partial | Linux 在线指南；`release-artifact-smoke.yml` 的 Linux asset 安装 smoke | 空项目 init、`Result / Next`、archive SHA256、主动恢复、同版本链 |
| R10 | partial | Linux 在线指南；release asset 安装共享证据 | 已有项目 adopt/保留、`Result / Next`、archive SHA256、主动恢复 |
| R11 | partial | Linux 离线指南；`posix-offline-smoke.yml` 的 Linux AMD64 离线安装 smoke | 空项目 init、离线包完整性、`Result / Next`、主动恢复 |
| R12 | partial | Linux 离线指南；POSIX 离线安装共享证据 | 已有项目 adopt/保留、离线包完整性、`Result / Next`、主动恢复 |

### 4.1 去重后的共性缺口

1. 没有统一 route ID、证据 schema 和逐路 owner，现有证明分散在指南与不同 smoke 中。
2. 路线 workflow 没有以正式发布的 checksum 证明下载 archive 完整性；安装后文件 hash 不能替代它。
3. macOS/Linux 缺少空项目与已有项目的完整 `init/adopt` 生命周期矩阵；Windows 也不是四路完整矩阵。
4. 恢复路径主要停留在指南说明，没有主动 fault injection 和成功回执。
5. PR 本地 bundle 重放与正式 released asset 证明没有形成统一、不可混淆的状态合同。
6. 在线/离线资产边界、触发事件、tag/commit/run 绑定没有被一份机器可复核的路线合同统一冻结。

## 5. 功能需求

- **FR-222-001**：formal 文档必须绑定精确远端主线基线和当前正式发布证据，不得使用用户排除的本地材料。
- **FR-222-002**：必须以 R01–R12 唯一标识完整覆盖三平台、两种项目模式和两种获取模式。
- **FR-222-003**：每条路线必须按 12 个最小证据字段评估，并使用 `proven / partial / missing` 三态语义。
- **FR-222-004**：证据记录必须区分指南、PR 候选 bundle、正式 release asset、checksum、workflow run 和真实环境，不得用间接证据替代缺失字段。
- **FR-222-005**：只有资产完整性、安装、生命周期、`Result / Next`、成功回执、恢复和版本绑定全部可复核时，路线才可标记为 `proven`。
- **FR-222-006**：共性缺口必须去重并优先通过共享矩阵或复用步骤解决；平台适配仅承载不可共享的差异。
- **FR-222-007**：本工作项不得进入 runtime、workflow、release 或 D2/P4 实现；任何实现都需要新的范围和 execute 批准。
- **FR-222-008**：后续建议最多给出一个可独立验收的最小薄片，并同时定义 Go/No-Go 与膨胀止损条件。
- **FR-222-009**：Program Truth 同步不得删除或掩盖既有 16 个 D2 blocker，也不得伪造 close materialization。

### 5.1 关键实体

- **RouteContract**：一条 R01–R12 路线的环境、项目模式、获取模式和 12 个证据字段定义。
- **RouteEvidence**：绑定 source/tag/asset/checksum/workflow run 的可复核证据集合及其 `proven / partial / missing` 状态。
- **CommonGap**：跨路线重复出现、应由共享步骤解决的缺口；保留受影响 route ID 集合，避免重复实现。

## 6. ROI 与实现边界

1. **用户收益**：价值维持路线图评估的 `9.5/10`；它直接验证首次用户能否在真实环境完成安装、接入、恢复，而不是增加内部治理展示。
2. **现状证据**：三平台已有指南和安装 smoke，但严格合同为 `0/12 proven、12/12 partial`；核心缺口高度重复，先做 admission 可避免盲目构建 12 套流程。
3. **最小方案**：本批只花不超过 1 人日冻结合同与差距表。后续首选薄片是“一份共享 route receipt schema + 在一个既有 workflow 中证明 1 条正式 release 路线”，再决定是否扩展矩阵；不一次性复制 12 套 workflow。
4. **总投入**：P3-A formal/admission 不超过 1 人日；完整 P3 仍维持 6–10 人日粗估，必须在薄片后用实际复用率重新估算。
5. **退出条件**：若薄片需要第二套状态机/ledger/持久化工件、复制超过 2 套近似 workflow、修改无关 runtime，或预计总投入超过 10 人日而不能增加 proven 路线，则 No-Go/重新定界。
6. **决策**：`implement` 仅指 formal/admission 文档与真值同步；runtime 实现为 `defer`，等待本工作项评审通过及用户另行 execute 批准。

`400/50`、辅助代码比例和调用方数量只作为风险信号，不是机械 blocker。安全、恢复和跨平台证据允许有必要支撑，但必须能映射到上述路线字段、复用路径和退出条件。

## 7. 成功标准

- **SC-222-001**：R01–R12 共 12/12 路线均有唯一 ID、平台、项目模式、获取模式和状态，未分类路线为 0。
- **SC-222-002**：所有 `proven` 判定均满足 12 个证据字段；当前基线不得产生假 `proven`，目标为 `0/12 proven、12/12 partial、0/12 missing`。
- **SC-222-003**：重复缺口收敛为不超过 6 个共性缺口，并明确受影响路线，而不是产生 12 份重复待办。
- **SC-222-004**：formal 批次不修改 runtime、workflow、用户指南、release/version 或既有 16 个 Program Truth blocker。
- **SC-222-005**：只给出 1 个后续最小薄片，包含独立验收、ROI 复核和 No-Go 条件；未获新批准前不执行。
- **SC-222-006**：constraints、program validate、Program Truth dry-run/同步和固定库存回归全部通过，且 close materialized 不因补写 `development-summary.md` 而虚增。
