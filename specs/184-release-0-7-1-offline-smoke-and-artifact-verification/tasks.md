# 任务清单：Release 0.7.1 Offline Smoke And Artifact Verification

**输入**：`specs/184-release-0-7-1-offline-smoke-and-artifact-verification/spec.md`  
**前置条件**：`uv run ai-sdlc run --dry-run` 已通过；当前分支允许在已有 dirty worktree 上追加本工作项文件。  
**测试要求**：涉及 workflow、src、tests 与 release docs，按 `code-change` 验证画像执行。

## Phase 1：Release workflow hardening

- [x] T184-001 [US1] 将 `.github/workflows/windows-offline-smoke.yml` 的 evidence upload action 升级到 `actions/upload-artifact@v7`
  - **验收标准（AC）**：workflow 中不再出现 `actions/upload-artifact@v4`；artifact 名称仍为 `windows-offline-smoke-evidence`。
  - **验证**：`uv run pytest tests/integration/test_github_workflows.py -q`

- [x] T184-002 [US2] 新增 `.github/workflows/release-artifact-smoke.yml` 下载 GitHub Release `.zip` / `.tar.gz` 并执行 CLI smoke
  - **验收标准（AC）**：workflow 支持 `workflow_dispatch` tag 输入；下载 release assets；执行 install、`--help`、`adapter status`、`run --dry-run`；上传 release smoke evidence。
  - **验证**：`uv run pytest tests/integration/test_github_workflows.py -q`

## Phase 2：Version and docs truth

- [x] T184-003 [US3] 将 `pyproject.toml`、`src/ai_sdlc/__init__.py`、`uv.lock` 与 packaging tests 更新到 `0.7.1`
  - **验收标准（AC）**：wheel dist-info 测试读取 `ai_sdlc-0.7.1.dist-info`。
  - **验证**：`uv run pytest tests/unit/test_packaging_backend.py -q`

- [x] T184-004 [US3] 新增 `docs/releases/v0.7.1.md` 并同步 README、USER_GUIDE、offline README、release checklist、PR checklist 与发布约定
  - **验收标准（AC）**：入口文档统一指向 `docs/releases/v0.7.1.md` 与 `ai-sdlc-offline-0.7.1.*`。
  - **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`

- [x] T184-005 [US3] 更新 `src/ai_sdlc/core/verify_constraints.py` 的 release docs consistency gate 到 `v0.7.1`
  - **验收标准（AC）**：约束 gate 要求 `v0.7.1` release notes 和 release artifact smoke 标记。
  - **验证**：`uv run ai-sdlc verify constraints`

## Phase 3：Verification and release handoff

- [x] T184-006 [US1][US2][US3] 执行本地验证并在 `task-execution-log.md` 记录结果
  - **验收标准（AC）**：pytest、ruff、verify constraints、truth sync dry-run 结果明确记录。
  - **验证**：`uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`; `uv run ruff check src tests`; `uv run ai-sdlc verify constraints`; `python -m ai_sdlc program truth sync --dry-run`

## Post-release handoff（不计入当前 PR close-check checklist）

- T184-007 [US2] PR 合并、tag 与 release 资产上传后运行 `release-artifact-smoke.yml`
  - **验收标准（AC）**：GitHub Actions 对 tag `v0.7.1` 产出 `release-zip-smoke-evidence` 与 `release-tar-smoke-evidence`。
  - **验证**：GitHub Actions run URL 与 artifact 名称记录到本执行日志或 release 记录。

- T184-008 [US2] 运行 `release-build.yml` 在云端按平台构建、smoke 并上传 release assets
  - **验收标准（AC）**：Windows / macOS / Linux matrix 各自产出平台后缀资产，并仅在安装 smoke 通过后执行 `gh release upload`。
  - **验证**：GitHub Actions run URL、上传资产名与 smoke evidence artifact 记录到 release 记录。

## 依赖与执行顺序

- T184-001 → T184-002 → T184-003/T184-004/T184-005 → T184-006 → T184-007

## 可并行机会

- release docs 文案与 workflow 测试可并行审查，但最终以 `verify constraints` 为合流点。
