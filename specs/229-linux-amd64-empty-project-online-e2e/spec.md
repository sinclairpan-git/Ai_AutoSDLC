# 功能规格：R09 Linux AMD64 空项目在线首次用户闭环

**功能编号**：`229-linux-amd64-empty-project-online-e2e`
**创建日期**：2026-09-05
**状态**：formal 本地双专家 PASS0，等待 formal PR；未授权实现
**主仓基线**：`origin/main@1111552d87ab6e09ec6c5f6989722af22319f7eb`
**关联路线**：`docs/FRAMEWORK_ROADMAP.zh-CN.md` P3 / R09

## 1. 问题与决策目标

P3 的十二条首次用户路线当前为 `1/12 proven、11/12 partial、0/12 missing`。R09
代表 Linux AMD64、空项目、在线获取。现有 release smoke 只间接证明 Linux 资产可安装，
现有 POSIX user-guide consumer 已直接覆盖 R06/macOS 已有项目和 R10/Linux 已有项目，
但没有在真实 Ubuntu runner 上证明以下同一条链路：正式/候选资产获取与完整性、fresh shell
中的 CLI、空目录 `init`、用户可见 Result/Next、主动故障恢复和逐路 receipt。

本 work item 只决定是否准入一个 R09 最小薄片。formal 合并不等于 implementation
授权；实现必须在 formal 合并后另行取得用户确认。

## 2. 范围

### 2.1 包含

- 复用 `.github/workflows/macos-user-guide-e2e.yml` 中现有的唯一 POSIX 在线 consumer，
  为 R09 增加一行 Linux AMD64 / empty / online 矩阵身份。
- PR 事件使用当前候选构建的 Linux bundle，生成 `status=partial` 的 12 字段 R09 receipt；
  `release.published` 才允许生成 `status=proven`。
- 从真正空目录开始，安装后在 fresh bash 中运行 `ai-sdlc --help` 与
  `ai-sdlc init . --agent-target codex --shell bash`。
- 验证 `.ai-sdlc/`、`AGENTS.md`、双语 Result/Next 和返回 AI 对话的下一步。
- 主动破坏 `resume-pack.yaml`，执行 `ai-sdlc recover` 并验证恢复后的 YAML 可解析。
- 保留 R06/R10 行为与 receipt 回归；实现前先写直接 workflow 合同红测。

### 2.2 不包含

- R01–R08、R10–R12 的新增能力，或一次性执行完整 12 路矩阵。
- 单独发布新版本、修改 release producer、安装器、bundle 格式、attestation 协议或
  receipt 顶层 schema。
- 新增 workflow、helper/script、产品 Python 源码、运行时依赖、状态机、ledger 或公共 API。
- 修改用户指南正文；若真实回放证明指南命令错误，当前候选立即 `needs_user`，不得顺手扩围。
- 重开 WI228/P4、Lean Code 或任何独立减重工作。
- 把 PR 本地产物回放写成正式 release 证明，或把 `partial` 越权升级为 `proven`。

## 3. 用户场景与测试

### 用户故事 1：Linux 新用户从空目录完成初始化（P0）

作为 Linux AMD64 首次用户，我希望从可核验的在线发布/候选资产完成安装并在空目录
执行 `init`，从而无需手工安装 Python、创建 venv 或猜测 PATH 就能回到 AI 对话继续开发。

**优先级说明**：这是路线图在 P2 完成、P4 No-Go 后明确排在首位的正常产品候选，
且直接补齐空项目用户路径，不是结构优化。

**独立测试**：真实 `ubuntu-latest` AMD64 job 从空目录执行完整 replay；PR exact HEAD
上传合法的 R09 `partial` receipt。

**验收场景**：

1. **Given** 项目目录创建后不含任何文件，**When** 用户通过安装后的 fresh bash 运行
   `ai-sdlc init . --agent-target codex --shell bash`，**Then** 命令成功，生成
   `.ai-sdlc/` 与 `AGENTS.md`，并显示“当前结果 / Result”“下一步 / Next”和返回 AI 对话。
2. **Given** 用户没有手工创建 Python 环境，**When** 安装脚本完成并启动 fresh bash，
   **Then** `command -v ai-sdlc` 和 `ai-sdlc --help` 成功，replay 不依赖手工 `pip`、venv
   或 PATH 猜测步骤。

### 用户故事 2：失败后可以就地恢复（P0）

作为首次用户，我希望初始化状态损坏时得到已有恢复入口，而不是删除项目或重装环境。

**独立测试**：初始化成功后写入无效 `resume-pack.yaml`，从 fresh bash 执行
`ai-sdlc recover`，再由 bundle Python 解析恢复后的 YAML。

**验收场景**：

1. **Given** R09 已完成初始化且 resume pack 被主动破坏，**When** 执行
   `ai-sdlc recover`，**Then** 命令成功，恢复后的文件可解析，证据写入同一 R09 artifact。

### 用户故事 3：维护者获得不夸大的逐路证据（P0）

作为发布维护者，我希望 R09 复用现有 12 字段 receipt 和事件语义，以便区分候选可执行性
与正式版本证明，同时不复制第二套 POSIX workflow。

**独立测试**：直接 YAML 合同测试固定 R06/R09/R10 三行矩阵、项目模式、动态 artifact
身份、12 字段 receipt、`partial/proven` 事件边界和 R06/R10 回归。

**验收场景**：

1. **Given** PR 事件使用本地构建 bundle，**When** R09 replay 成功，**Then** receipt 为
   `route_id=R09`、Linux/AMD64、empty、`status=partial`。
2. **Given** 非 `release.published` 事件，**When** 生成 receipt，**Then** 即使全部步骤成功
   也不得标记 `proven`。

## 4. 边界情况

- “空项目”定义为 replay 创建后、`init` 前 `find` 结果为零的独立目录；不能先放占位文件。
- PR runner 上用于构建候选 bundle 的 Python 不得被当作用户安装前置；用户 replay 必须从
  bundle installer 与 fresh shell 开始。
- release/tag、asset、SHA256 或 attestation 任一绑定失败时必须在安装前失败。
- R09 不执行 `adopt`，也不伪造 `business_files_preserved=true`；receipt 使用 empty-project
  语义记录初始化结果。
- R06/R10 仍执行已有项目文件保护与 `adopt`，R09 分支不得改变其回执含义。
- GitHub API、网络或 runner 临时不可用只导致证据未取得，不得写成产品失败或成功。

## 5. 功能需求

- **FR-229-001**：现有 POSIX 在线 consumer 必须复用一个 job 与一个 replay block 承载
  R06、R09、R10；不得复制第二份 workflow 或完整 shell replay。
- **FR-229-002**：矩阵必须显式绑定 `route_id`、runner、OS、architecture、asset suffix、
  fresh shell、shell name 和 project kind；R09 必须为 Linux/AMD64/empty/online。
- **FR-229-003**：R09 的 `project_root` 在 `init` 前必须存在且文件数为零，初始化后必须
  包含 `.ai-sdlc/` 和 `AGENTS.md`。
- **FR-229-004**：所有路线必须继续在 fresh shell 中验证安装后的 `ai-sdlc`；R09 必须
  捕获并验证双语 Result/Next、返回 AI 对话提示及内部诊断术语不泄露。
- **FR-229-005**：R09 必须主动损坏 resume pack、调用现有 `recover` 并验证恢复结果；
  不新增恢复机制。
- **FR-229-006**：receipt 必须保留现有 12 个顶层字段，并严格使用 5.1 的 mode-specific
  projection；R09 不能沿用已有项目的保护文件断言，也不能由实现者临时发明字段。
- **FR-229-007**：PR/manual 证据只能为 `partial`；只有 `release.published`、正式 asset
  与强 attestation 同时成立时才允许 `proven`。
- **FR-229-008**：R06/R10 的现有矩阵身份、init/adopt、业务文件 hash、恢复和 receipt
  语义必须保持。
- **FR-229-009**：实现 diff 只允许现有 POSIX workflow、其直接合同测试、R09 formal/
  路线图/Program Truth/continuity 文件；任何产品源码、依赖、producer、schema、新 workflow
  或用户指南正文改动均触发 No-Go。
- **FR-229-010**：workflow 与直接合同测试合计 gross added lines 不得超过 220；超过预算
  或需要第二个 implementation PR 时，WI229 terminal No-Go，不创建 replacement formal、
  第二 WI 或续作。未来只有 Sponsor 基于全新用户证据明确授权的独立产品需求才可重新评估，
  且不得视为 WI229 的延续。

### 5.1 R09 receipt 精确投影

R09 继续使用既有 12 个顶层字段，不新增第 13 个字段、不修改 runtime validator、producer
或持久化 schema。只有以下三个顶层对象使用冻结的 empty-project 内层投影；其余九个字段
沿用当前 consumer：

```json
{
  "project_mode": {"kind": "empty", "initial_file_count": 0},
  "lifecycle": {"init": "passed", "adopt": "not_applicable"},
  "success_receipt": {
    "status": "partial|proven",
    "version": "<release_version>",
    "initialized": true
  }
}
```

- `initial_file_count=0` 必须来自 `init` 前真实目录扫描，并保存
  `empty-project-before.txt`；不能用常量直接写入 receipt。
- `initialized=true` 必须同时由 `.ai-sdlc/`、`AGENTS.md` 和已验证的 Result/Next 支撑，
  并保存 `empty-project-after.txt` 与 init 输出。
- `adopt=not_applicable` 是空项目的显式不适用值；R09 不执行 `adopt`。
- R06/R10 继续使用现有 existing projection：`protected_files=4`、`adopt=passed`、
  `business_files_preserved=true`，不得随 R09 改动。

## 6. ROI 与实现边界

1. **用户可观察收益**：首次为 Linux AMD64 空项目提供从资产到初始化、Result/Next、恢复
   和 receipt 的真实闭环，使 P3 新增一条直接逐路证据，而非增加内部治理功能。
2. **现状证据**：R09 当前只有 release smoke/指南的间接证据；R10 已证明同一 Ubuntu
   runner、Linux bundle、fresh bash 和 receipt consumer 可执行，主要剩余差异是项目模式。
3. **最小方案**：向现有 POSIX matrix 增加 R09，并以 `project_kind` 做最小条件分支。
   复制 workflow、抽取通用框架或修改 installer 均比现有承载方式更大。
4. **总投入**：formal 约 0.25 人日；实现、红测、本地验证、真实 CI 和复审合计上限
   1.5 人日；不为本项单独发布。长期维护只增加一个矩阵行和同一 replay 的空项目分支。
5. **范围与退出条件**：无 public API、依赖或持久化状态；一个 implementation PR，最多
   两轮确定性同路径修复。需修改冻结 allowlist、超过 220 gross additions、R06/R10 回归、
   receipt 无法表达 empty 语义或真实 Ubuntu 路径需要新平台机制时立即 No-Go。
6. **决策**：`needs_user`。formal 本地对抗评审已通过；formal PR 合并后仍需用户单独批准
   implementation。

## 7. 成功标准

- **SC-229-001**：直接 workflow 合同测试先对缺失 R09/empty 语义呈 RED，再在最小实现后 GREEN。
- **SC-229-002**：PR exact HEAD 的 R06、R09、R10 三个真实 matrix job 均成功；R09 artifact
  包含合法 12 字段 `partial` receipt。
- **SC-229-003**：R09 证据证明 `init` 前目录零文件，初始化后 `.ai-sdlc/`、`AGENTS.md`、
  Result/Next 和 AI 对话下一步均成立。
- **SC-229-004**：R09 的主动损坏与 `recover` 成功，恢复后的 resume pack 可解析。
- **SC-229-005**：R06/R10 直接合同测试及完整 workflow 测试通过，已有项目文件保护语义不变。
- **SC-229-006**：实现 allowlist 外零 diff，workflow + 直接测试 gross additions `<=220`，
  Ruff、constraints、Program validate、相关 pytest 与 diff-check 通过。
- **SC-229-007**：产品价值与架构纯洁两位独立评审对 exact formal HEAD 均为 PASS0；任何
  Important/Critical 未收敛则 formal No-Go，不进入实现。

## 8. 固定终止与回退

- formal 只允许当前这一轮对抗意见修订；修订后任一专家仍有 Important/Critical 即 No-Go。
- implementation 最多一个 PR、两轮确定性同路径修复；API/网络/runner 排队不计修复轮次。
- 无法用现有 consumer 表达 R09 时整体回退，不以新 helper、workflow 或 runtime 扩围续命。
- WI229 No-Go 后不得创建 replacement formal、第二 WI 或第二 implementation PR 续命；只有
  Sponsor 基于全新用户证据另行明确授权的独立产品需求可在未来重新评估。
- PR 候选可整体 `git revert`；自然发布证明不作为本实现 PR 的合并前置，也不得伪造。

---
related_doc:
  - "docs/FRAMEWORK_ROADMAP.zh-CN.md"
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
  - "specs/227-linux-amd64-existing-project-online-e2e/spec.md"
---
