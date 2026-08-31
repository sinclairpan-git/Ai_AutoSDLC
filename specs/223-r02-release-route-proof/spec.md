# 功能规格：R02 正式发布路线证明载体

**功能编号**：`223-r02-release-route-proof`  
**创建日期**：2026-08-30  
**状态**：P3-B formal；实现已获用户批准，须在 formal review 通过后进入 dev 分支  
**远端主线基线**：`origin/main@49d43c459cdabe5d3664dafd4600192c01333500`  
**发布基线**：GitHub Release `v0.9.8` / tag commit `4f3e55c300dab20fb4fea93818d79394a927f77e`  
**输入**：`specs/222-first-user-twelve-route-e2e-contract/spec.md` 与 `docs/FRAMEWORK_ROADMAP.zh-CN.md`

## 1. 目标与边界

本工作项只为 R02（Windows AMD64 / 已有项目 / 在线正式发布包）建立一条可复用的证明载体：同一次 Windows 执行必须绑定正式 release asset、验证 GitHub 发布 digest、完成安装和已有项目接入、验证 `Result / Next` 与业务文件保持、主动破坏并恢复 continuity 文件，最后生成包含 WI222 冻结 12 字段的临时 `route-receipt.json`。

### 1.1 本次覆盖

- 把现有 Windows 已有项目 E2E 的长内联步骤抽成一个 CI 专用共享执行器，由 `windows-user-guide-e2e.yml` 与 `release-artifact-smoke.yml` 复用。
- 对 GitHub Release 返回的资产 `digest` 与下载文件 SHA256 做精确比较；不以 `AGENTS.md` 或业务文件 hash 代替 archive 完整性。
- 主动损坏 `.ai-sdlc/state/resume-pack.yaml`，调用已发布 CLI 的 `recover` 恢复，并保存故障前后与恢复输出。
- 生成 CI 临时 receipt；receipt 不是产品运行时状态、Program Truth、ledger 或长期数据库。
- PR 本地产物、`workflow_dispatch` 正式包重放与 `release` event 使用同一执行器，但保持不同证明等级。

### 1.2 本次不覆盖

- 不修改 `src/ai_sdlc/`、CLI/runtime、installer、`USER_GUIDE.zh-CN.md` 正文、版本号、release asset 或发布状态。
- 不启动 v0.9.9、D2、P4、R01/R03–R12、macOS/Linux 路线或新的在线安装器。
- 不新增状态机、持久化 receipt ledger、certificate、waiver、retry engine 或 Program Truth blocker。
- 不使用产品站、比赛材料、本地材料分支、未合并 worktree 或参赛版代码作为实现真值。
- 不为获得 `release` event 证据单独发布新版本，也不把 `workflow_dispatch` 或 PR run 冒充正式发布事件。
- 不新增 `development-summary.md`，不修改历史 work item execution log，不删除现有 16 个 Program Truth blocker。
- formal 新增 WI223 后只允许同步 `tests/integration/test_repo_program_manifest.py` 的固定库存期望；不得改变测试逻辑。

## 2. 已验证现状与 Go/No-Go

半天特征化闸门基于 exact main 与 GitHub 远端事实：

1. `gh release view v0.9.8 --json assets` 返回 Windows asset digest `sha256:0ed406cc9280a285478fdff5e52b322cce6331c7ed6769a8b50099a4ef4bdc72`，可与下载文件直接比较。
2. `Release Artifact Smoke` run `33084560424` 是 `release` event、head `4f3e55c...` 且 Windows job 成功，但旧 workflow 没有 R02 生命周期、主动恢复和逐路 receipt，不能追认 R02 为 `proven`。
3. `.github/workflows/windows-user-guide-e2e.yml` 已有 `init/adopt`、双语 `Result / Next` 和业务文件 hash 保持；`.github/workflows/release-artifact-smoke.yml` 已有正式 Windows asset 下载与安装。抽出一份共享执行器可以删除重复内联步骤，不需要第二套实现。
4. 当前 CLI 已支持损坏或缺失 resume pack 后执行 `recover` 重建；本工作项只使用该既有公开恢复入口，不新增恢复语义。
5. 隔离 worktree 在任何改动前全量基线为 `3407 passed, 3 skipped`。

**闸门结论**：`Go`。若实现中出现第 4 节退出条件，则自动转为 `No-Go / needs_user`，不得用追加支撑层强行完成。

## 3. 用户场景与验收

### US-223-1：维护者获得自包含的 R02 候选回执（P0）

作为发布维护者，我希望一个 Windows clean runner 能从正式发布包完成已有项目接入和恢复，并输出单个自包含 receipt，以便我不再拼接多个 workflow 的间接证据。

**独立测试**：PR 路径使用本地产物执行同一核心步骤并生成 `partial` receipt；静态契约测试验证两个 workflow 只调用同一个执行器。

1. **Given** 一个含 `package.json`、源码、README 和 TODO 的已有项目，**When** 执行安装、`init` 和 `adopt`，**Then** 业务文件 SHA256 不变，输出包含 `Result / Next`，receipt 的生命周期字段可复核。
2. **Given** init 后的 resume pack 被主动写坏，**When** 执行已发布 CLI 的 `recover`，**Then** 命令成功、resume pack 恢复为可解析文件、业务文件仍未改变，故障与恢复日志被 receipt 引用。

### US-223-2：评审者不能把候选重放误报为正式证明（P0）

作为评审者，我希望 receipt 的结论由事件类型和完整证据共同决定，以便 PR 或手工重放不能被标记为正式路线证明。

**独立测试**：契约测试分别构造 `pull_request`、`workflow_dispatch`、`release` 事件条件；只有 `release` event 加 digest 匹配和其余字段成功时，状态才允许为 `proven`。

1. **Given** PR 本地构建包通过全部生命周期步骤，**When** 生成 receipt，**Then** 状态仍为 `partial`，资产字段明确标注非正式 release digest。
2. **Given** `workflow_dispatch` 下载 v0.9.8 正式包并校验 digest，**When** 生成 receipt，**Then** 它是候选重放证据，不能替代 `release` event。
3. **Given** 下一次自然 `release` event 在同一 job 中满足 12 字段，**When** receipt 完成，**Then** 才可输出 `proven`；WI223 合并本身不得提前更改 WI222 的 `0/12 proven` 基线。

## 4. 功能需求与退出条件

- **FR-223-001**：receipt 必须包含且只使用 WI222 定义的 12 个必需顶层证据字段：`route_id`、`environment`、`project_mode`、`acquisition_mode`、`source_binding`、`asset_integrity`、`installation`、`lifecycle`、`result_next`、`success_receipt`、`fault_recovery`、`evidence_links`；允许另有 `schema_version` 和 `status` 元数据。
- **FR-223-002**：R02 固定为 Windows AMD64、已有项目、在线正式 release 获取；执行器不得接受任意 route ID 或扩展为未授权矩阵框架。
- **FR-223-003**：正式资产模式必须从 GitHub Release API 取得资产名、tag/target commit 与 digest，比较本地 SHA256；缺字段或不一致必须 fail closed。
- **FR-223-004**：共享执行器必须被两个既有 workflow 调用；不得在 workflow 中保留第二份完整安装/init/adopt/recover 实现。
- **FR-223-005**：故障恢复必须真实损坏 resume pack 后调用 `ai-sdlc recover`；不得用字符串断言或预制成功 JSON 代替执行。
- **FR-223-006**：PR、本地候选或手工 dispatch 的 receipt 状态必须为 `partial`；仅 `GITHUB_EVENT_NAME=release` 且所有必需检查通过时允许 `proven`。
- **FR-223-007**：receipt 只作为 Actions artifact 上传，不写入产品 `.ai-sdlc/` 状态或仓库历史真值。
- **FR-223-008**：实现必须保留现有 Windows guide replay 的直接 shim、Git Bash stale PATH、双语输出和业务文件保护合同，以及 release smoke 的离线包验证入口。

以下任一条件触发停止并回到用户决策：

- 需要修改产品 runtime、installer、版本或发布资产；
- 需要第二套状态机、持久化 ledger 或平行 truth；
- 为完成 R02 复制第三份近似 workflow，或无法删除现有重复核心步骤；
- 实际总投入预计超过 3 人日；
- 需要削弱“真实 release event 才能 proven”的合同；
- 两轮独立评审后仍有可操作问题。

不设置机械 LOC 上限；文件大小和支撑比例只触发 Lean 复核。只要实现直接映射 12 字段、复用两条既有路径且无持久化治理扩张，可保留必要的 Windows/恢复支撑代码。

## 5. ROI 决策

1. **价值**：`9.5/10`。它把正式资产存在升级为首次用户可复核的已有项目接入与恢复路径。
2. **投入**：特征化已完成；实现、测试、CI、评审与收口目标 `1.5–2.5` 人日，硬上限 `3` 人日。
3. **最小方案**：一个 R02 执行器、两个薄 workflow 调用、一个临时 receipt；不实现通用路线平台。
4. **备选方案**：复制现有 PowerShell 到 release smoke 投入更小但会形成双轨；一次实现 12 路需 6–10 人日且未证明复用；两者均拒绝。
5. **决策**：`implement`。用户已批准“半天闸门通过后继续最小实现”；formal review 通过后进入 dev 分支。

## 6. 成功标准

- **SC-223-001**：focused 契约测试先 RED 后 GREEN，证明共享执行器存在、两个 workflow 复用它、旧的重复核心块被移除。
- **SC-223-002**：PR Windows E2E 在真实 Windows runner 上执行安装/init/adopt/故障恢复并上传 `route-receipt.json`；PR receipt 保持 `partial`。
- **SC-223-003**：正式资产模式对本地 archive SHA256 与 GitHub asset digest 做精确比较，任何缺失或不一致均失败。
- **SC-223-004**：receipt 的 12 个必需字段完整，且非 `release` 事件不能产生 `proven`。
- **SC-223-005**：实现 PR 不触达禁止范围；全量测试、Ruff、constraints 与 diff-check 通过。
- **SC-223-006**：实现后完成半天 Lean/ROI 复核；在下一次自然 release event 产生真实 `proven` receipt 前，Program Truth 与 WI222 的路线结论保持真实 blocked/partial。
