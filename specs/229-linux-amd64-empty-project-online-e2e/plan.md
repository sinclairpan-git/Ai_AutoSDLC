---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 实施计划：R09 Linux AMD64 空项目在线首次用户闭环

**编号**：`229-linux-amd64-empty-project-online-e2e`  
**日期**：2026-09-05  
**规格**：`specs/229-linux-amd64-empty-project-online-e2e/spec.md`  
**状态**：formal admission 对抗评审中；未授权 implementation

## 概述

在不新增 workflow、脚本或产品代码的前提下，把已有 POSIX user-guide online consumer
从 R06/R10 两行扩为 R06/R09/R10 三行。通过一个 `project_kind` 矩阵字段让同一 replay
分别准备真正空目录或已有项目；资产下载/校验、安装、fresh shell、init、恢复和 receipt
继续共享。PR exact HEAD 只交付 R09 `partial` 证据，下一次自然发布才可能升级为 `proven`。

## 技术背景

**语言/格式**：GitHub Actions YAML、Bash、Python workflow 合同测试  
**主要依赖**：现有 offline bundle、GitHub release/attestation、`jq`、fresh bash  
**存储**：GitHub Actions 临时 evidence 目录与 artifact；不新增仓库运行时状态  
**测试**：`tests/integration/test_github_workflows.py` + 真实 Ubuntu/macOS matrix jobs  
**目标平台**：R09 Linux AMD64；R06 macOS arm64、R10 Linux AMD64 作为回归  
**约束**：单 job/单 replay；无 runtime/schema/producer/依赖/用户指南改动；220 gross additions

## 宪章检查

| 宪章门禁 | 计划响应 |
|---|---|
| MUST-1 MVP 优先 | 只准入 R09，不扩展其余路线或安装器 |
| MUST-2 关键路径可验证 | 直接 RED/GREEN 合同测试 + 真实 Ubuntu R09 receipt |
| MUST-3 范围、验证、回退 | 冻结 allowlist；单 PR；可整体 revert |
| MUST-4 状态外化 | 只写既有 route receipt/artifact，不新增状态 |
| MUST-5 产品/开发隔离 | workflow 与测试不进入 `src/ai_sdlc`，formal 独立归档 |
| 文件/函数预算 | 不新增 Python 产品文件；workflow + 直接测试 gross additions <=220 |

## 文件边界

### Formal PR

- `specs/229-linux-amd64-empty-project-online-e2e/**`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `.ai-sdlc/state/codex-handoff.md`
- `.ai-sdlc/work-items/229-linux-amd64-empty-project-online-e2e/codex-handoff.md`
- `docs/FRAMEWORK_ROADMAP.zh-CN.md`（仅记录 formal admission 终态）
- 必要的 Program Manifest 库存断言机械同步

### Implementation 候选 allowlist（需另行批准）

- `.github/workflows/macos-user-guide-e2e.yml`
- `tests/integration/test_github_workflows.py`
- 本 WI、路线图、Program Truth、continuity 和必要库存断言

以下任一出现即超范围：`src/ai_sdlc/**`、`pyproject.toml`、packaging/release producer、
新 workflow/helper、receipt schema、`USER_GUIDE.zh-CN.md` 正文。

## 阶段计划

### Phase 0：formal admission

**目标**：冻结 R09 用户价值、现状证据、最小切片、预算、allowlist 与停止条件。  
**产物**：spec/plan/tasks/execution log、Program Truth、路线图状态。  
**验证**：constraints、Program validate、plan-check、两位独立专家 exact-head PASS0。  
**回退**：未通过评审即关闭 formal No-Go，不创建 dev 分支。

### Phase 1：合同红测（implementation 获批后）

**目标**：先固定 R06/R09/R10 三行矩阵、empty 语义和动态 receipt/artifact。  
**产物**：仅修改 `tests/integration/test_github_workflows.py`。  
**验证**：定向 pytest 必须因当前 workflow 缺少 R09/empty 而按预期失败。  
**回退**：红灯若暴露必须改 schema/producer，立即 No-Go。

### Phase 2：最小 workflow 参数化

**目标**：加入一行 R09 和 `project_kind`，在同一 replay 中条件准备 empty/existing 项目。  
**产物**：现有 POSIX workflow + 直接合同测试。  
**验证**：定向测试、完整 workflow 集成测试、Ruff、constraints、Program validate、diff budget。  
**回退**：整体 revert；不得抽取新框架续做。

### Phase 3：真实环境与收口

**目标**：在 PR exact HEAD 取得 R06/R09/R10 matrix 成功和 R09 partial receipt。  
**产物**：同一 implementation PR 的 run/artifact/评审证据。  
**验证**：receipt 12 字段、empty precondition、Result/Next、recover、R06/R10 回归。  
**回退**：最多两轮同路径聚焦修复；仍失败则 No-Go 并撤回 implementation。

## 最小实现形态

1. 矩阵增加 `project_kind`；R06/R10 为 `existing`，R09 为 `empty`。
2. 保留 legacy job key，避免无价值地改变现有 required-check 身份。
3. replay 共享资产、attestation、安装和 fresh shell；只在项目准备、`adopt`、文件 hash 与
   receipt 内层字段处按 `project_kind` 分支。
4. artifact 名包含 route 与 project kind，避免 R09/R10 在同一 Ubuntu run 中混淆。
5. 不抽取 helper：当前仅一个消费面，抽象不会减少重复。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|---|---|---|
| R09 矩阵身份 | YAML 直接合同测试 | GitHub job 名/runner 证据 |
| 空目录与 init | Ubuntu replay + pre-init file count | artifact 文件清单 |
| 安装与 fresh shell | `command -v` + `ai-sdlc --help` | 安装日志 |
| Result/Next | 精确用户可见字符串断言 | init 输出 artifact |
| recover | 主动损坏 + `ai-sdlc recover` | bundle Python YAML 解析 |
| receipt | 12 字段 `jq` 断言 | 独立 artifact 核验 |
| R06/R10 回归 | 同 matrix 两行成功 | 现有 workflow 测试 |
| 代码纯洁 | allowlist + gross diff budget | 架构专家评审 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|---|---|---|
| 现有 12 字段 receipt 的内层结构能否直接表达 empty/init | 预计可行，须由 RED 测试与架构评审确认 | implementation |
| legacy job key 是否保留 | 冻结为保留，避免 required-check 身份漂移 | 已决策 |
| R09 proven 何时取得 | 下一次正常 `release.published`，不为本项单独发版 | 非阻塞 |

## 实施顺序与门禁

1. 完成 formal 四件套、Truth/路线图同步与本地验证。
2. 产品价值、架构纯洁两位专家独立评审；只允许一轮 formal 修订。
3. formal PASS0 后创建 formal PR，Codex/CI 全绿再合并。
4. 重新向用户申请 implementation execute；未确认前停止。
5. 获批后从 fresh-main 创建 dev 分支，按 RED -> 最小 GREEN -> 真实 CI -> exact-head review 执行。

---
related_doc:
  - "docs/FRAMEWORK_ROADMAP.zh-CN.md"
  - "specs/222-first-user-twelve-route-e2e-contract/spec.md"
  - "specs/227-linux-amd64-existing-project-online-e2e/spec.md"
---
