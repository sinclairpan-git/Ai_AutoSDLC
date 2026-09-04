# 功能规格：R10 Linux AMD64 已有项目在线 E2E

**功能编号**：`227-linux-amd64-existing-project-online-e2e`  
**创建日期**：2026-09-04  
**状态**：已批准，进入 bounded execute  
**基线**：`origin/main@8a3973a555c4fe463cc31cdec1021a1c76b7f3a8`  
**决策来源**：用户批准的双专家对抗合议，2/2 `APPROVE`

## 1. 目标与范围

在不复制第二份大型 POSIX workflow 的前提下，把现有 macOS R06 已有项目在线 consumer 参数化为两行矩阵，并在真实 `ubuntu-latest` AMD64 runner 上增加 R10：Linux 正式资产获取、安装、`init/adopt`、Result/Next、业务文件保护、故障恢复和 12 字段 receipt。

**范围内**：

- `.github/workflows/macos-user-guide-e2e.yml` 的现有单 job POSIX consumer 参数化。
- `tests/integration/test_github_workflows.py` 的直接 workflow 合同测试。
- 本 WI、Program manifest、项目序号与路线图的最小状态记录。
- PR exact HEAD 上真实 Ubuntu R10 job 的运行证据。

**范围外**：

- Python runtime、CLI、receipt schema、release producer、installer 行为或依赖。
- R02、R01/R03–R09/R11/R12，以及 v0.9.9 tag/release 状态。
- `USER_GUIDE.zh-CN.md` 正文；主线已包含 Linux 资产安装和已有项目 `init/adopt` 路径。
- 为取得 `proven` 单独发布版本，或复制第二份约 350 行的 POSIX workflow。
- 新治理状态、waiver、第二工作项、第二分支或第二 PR。

## 2. 用户故事与验收

### US-1：Linux 已有项目在线闭环（P0）

作为 Linux AMD64 上的已有项目用户，我希望使用正式 Linux 资产完成安装和项目接入，并在失败后按本地恢复入口恢复，以便不破坏已有业务文件地继续开发。

**独立验收**：GitHub `ubuntu-latest` 从本 PR 本地产物执行完整路径，生成 `route_id=R10`、`environment.os=linux`、`architecture=amd64` 且含 12 个顶层字段的 `partial` receipt；四个业务文件哈希前后一致。

### US-2：保留 R06（P0）

作为发布维护者，我希望参数化不降低现有 macOS R06 证据，以便 Linux 覆盖不是通过复制或牺牲既有路线获得。

**独立验收**：同一个 matrix job 同时保留 R06/macOS arm64 与 R10/Linux AMD64；平台资产、shell、runner、receipt 和 evidence artifact 均由矩阵值绑定。

## 3. 功能需求

- **FR-001**：现有 `existing-project-online-install` 必须使用恰好两行显式矩阵：R06/macOS arm64 与 R10/Linux AMD64。
- **FR-002**：两行必须共享同一 replay 实现；禁止复制完整 job、完整 run block 或新建第二份 POSIX workflow。
- **FR-003**：runner、route ID、OS、architecture、资产后缀和 fresh shell 必须由矩阵显式提供；真实 runner 架构与预期不一致时 fail closed。
- **FR-004**：PR 事件分别构建匹配平台的本地 bundle；manual/release 事件下载匹配正式资产；自然发布 attestation 仍绑定 tag/ref/commit 与既有 signer workflow。
- **FR-005**：R10 必须执行安装、fresh-shell `ai-sdlc --help`、已有项目 `init/adopt`、Result/Next 检查、损坏 resume-pack 的 `recover` 和业务文件哈希保护。
- **FR-006**：receipt 保持既有 12 字段合同；PR/manual 为 `partial`，只有真实 `release.published` 可为 `proven`。
- **FR-007**：R06 的 macOS arm64、zsh、资产名和 receipt 语义必须保持；R10 使用 Linux AMD64、bash 和 Linux 资产。
- **FR-008**：工作流合同测试必须先以缺少 R10 矩阵行为失败，再由最小 workflow 修改转绿。
- **FR-009**：API/网络/runner 排队属于观察态，不消耗修复轮次；确定性 R10 路径失败才进入同一 PR 内的聚焦修复。

## 4. ROI 与实现边界

- **用户价值**：P3 路线完整性价值 `9.5/10`；R10 覆盖 Linux 已有项目这一高频普通用户路径。
- **现状证据**：Linux release smoke 已证明资产可安装，但 WI222 仍缺生命周期、Result/Next、主动恢复和逐路 receipt；R06 已提供可复用 consumer。
- **最小方案**：参数化现有 R06 job，而不是复制 workflow 或抽象新的 runtime/helper。
- **投入**：一个工作项、一个实施分支、一个 PR；最多两轮同路径聚焦修复。
- **停止条件**：真实 Ubuntu 路径需要修改 runtime/schema/release producer、复制完整 workflow，或第二轮后仍有确定性同路径失败时，立即 No-Go，不扩大范围。
- **决策**：`implement`。

## 5. 成功标准

- **SC-001**：直接 workflow 合同测试经历 RED→GREEN，完整文件测试通过。
- **SC-002**：PR exact HEAD 的 R06 与 R10 matrix jobs 均成功；R10 artifact 内 receipt 为合法 `partial`。
- **SC-003**：R06 路径、release/manual 语义及现有 required checks 无回归。
- **SC-004**：R02 保持 `partial`；R10 在下一次正常发布前保持 `partial`，不伪称 `proven`。
- **SC-005**：Ruff、constraints、Program validate、diff-check 与相关 pytest 通过；tracked diff 不含 runtime、schema、release producer 或 USER_GUIDE 正文。
