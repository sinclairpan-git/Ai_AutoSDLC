# 功能规格：Release 0.7.1 Offline Smoke And Artifact Verification

**功能编号**：`184-release-0-7-1-offline-smoke-and-artifact-verification`  
**创建日期**：2026-05-01  
**状态**：草案（执行中）  
**输入**：用户要求在 `0.7.1` 中修复 offline smoke workflow 的 `actions/upload-artifact@v4` Node 20 warning，并在其他修复完成后发布 `0.7.1` 新版本。

**范围**：本工作项覆盖 `0.7.1` 版本真值、offline smoke workflow action runtime、发布资产安装冒烟 workflow、release 入口文档与约束测试。不覆盖 GitHub Release 的最终发布操作；该动作需在 PR 合并、tag 与资产上传完成后执行。

## 用户场景与测试（必填）

### 用户故事 1 - Offline smoke action runtime 收口（优先级：P1）

维护者希望 Windows offline smoke workflow 不再因旧版 artifact action 输出 Node 20 warning，以便 `0.7.1` CI 证据保持干净。

**独立测试**：`uv run pytest tests/integration/test_github_workflows.py -q`

**验收场景**：

1. **Given** `.github/workflows/windows-offline-smoke.yml`，**When** 检查 artifact 上传步骤，**Then** 使用 `actions/upload-artifact@v7`。
2. **Given** workflow 成功运行，**When** 上传 smoke evidence，**Then** artifact 名称和路径保持 `windows-offline-smoke-evidence` 合同不变。

### 用户故事 2 - 发布资产真实安装冒烟（优先级：P1）

维护者希望在 `v0.7.1` GitHub Release 发布资产上传后，从 release 下载正式 `.zip` / `.tar.gz` 再安装验证，以便证明发布资产而非源码树临时构建产物可用。

**独立测试**：`uv run pytest tests/integration/test_github_workflows.py -q`

**验收场景**：

1. **Given** `v0.7.1` Release 已含离线包资产，**When** 运行 `release-artifact-smoke.yml`，**Then** workflow 下载 `ai-sdlc-offline-*.zip` 和 `ai-sdlc-offline-*.tar.gz`。
2. **Given** workflow 下载到资产，**When** 安装离线包，**Then** 执行 `ai-sdlc --help`、`adapter status` 与 `run --dry-run`。

### 用户故事 3 - 0.7.1 入口真值一致（优先级：P1）

使用者希望 README、用户手册、offline README、release notes 与约束检查都指向同一个 `v0.7.1` 发布入口，以便安装和验证路径不会漂移。

**独立测试**：`uv run pytest tests/unit/test_verify_constraints.py tests/unit/test_packaging_backend.py -q`

**验收场景**：

1. **Given** 当前 release docs consistency gate，**When** 检查入口文档，**Then** 必须出现 `v0.7.1`、`docs/releases/v0.7.1.md`、`ai-sdlc-offline-0.7.1.zip` 与 `ai-sdlc-offline-0.7.1.tar.gz`。
2. **Given** 构建 wheel，**When** 读取 dist-info，**Then** 使用 `ai_sdlc-0.7.1.dist-info`。

## 需求（必填）

### 功能需求

- **FR-184-001**：Windows offline smoke workflow 必须使用 `actions/upload-artifact@v7` 上传证据。
- **FR-184-002**：必须新增 release artifact smoke workflow，从 GitHub Release 下载正式资产后安装验证，而不是只验证当前源码构建产物。
- **FR-184-003**：`0.7.1` 必须同步 `pyproject.toml`、源码 fallback version、`uv.lock`、release docs consistency gate 与相关测试。
- **FR-184-004**：入口文档必须同步 `v0.7.1` release notes 与 offline asset 名称。
- **FR-184-005**：本工作项不得声称 GitHub Release 已发布；最终发布动作必须等 PR 合并、tag 与资产上传完成后再执行并记录证据。

### 关键实体

- **Offline smoke workflow**：当前源码构建出的 Windows offline bundle 安装验证。
- **Release artifact smoke workflow**：GitHub Release 已发布资产的下载、安装和 CLI smoke 证据。
- **Release docs consistency gate**：保证 release 入口文档、资产名和版本号一致的约束检查。

## 成功标准（必填）

### 可度量结果

- **SC-184-001**：`tests/integration/test_github_workflows.py` 覆盖 `actions/upload-artifact@v7` 与 `release-artifact-smoke.yml`。
- **SC-184-002**：`tests/unit/test_verify_constraints.py` 的 release docs consistency 测试通过 `v0.7.1` 入口。
- **SC-184-003**：`uv run ai-sdlc verify constraints` 对 `0.7.1` release 文档入口无 BLOCKER。
- **SC-184-004**：发布后 `release-artifact-smoke.yml` 能对 tag `v0.7.1` 产出 zip/tar smoke evidence artifact。
