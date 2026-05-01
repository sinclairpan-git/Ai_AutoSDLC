# Feature 184 任务执行归档

## 1. 归档规则

- 本文件是 `184-release-0-7-1-offline-smoke-and-artifact-verification` 的固定执行归档文件。
- 每批任务结束后追加记录验证命令、结果与剩余发布后动作。

## 2. 批次记录

### Batch 2026-05-01-1 | T184-001-T184-006

#### 2.1 批次范围

- 覆盖任务：T184-001、T184-002、T184-003、T184-004、T184-005、T184-006
- 覆盖阶段：release workflow hardening、version/docs truth、本地验证
- 预读范围：`AGENTS.md`、`.ai-sdlc/memory/constitution.md`、`README.md`、`packaging/offline/README.md`、`docs/releases/v0.7.0.md`、`tests/integration/test_github_workflows.py`
- 激活的规则：先执行 `ai-sdlc run --dry-run`；release docs consistency；offline bundle 平台 smoke 不可替代正式发布资产 smoke

#### 2.2 统一验证命令

- **验证画像**：`code-change`
- `V0`（入口预演）
  - 命令：`uv run ai-sdlc run --dry-run`
  - 结果：PASS（Stage close: PASS）
- `V1`（定向 pytest）
  - 命令：`uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`
  - 结果：PASS（release build workflow / asset suffix 更新后为 128 passed）
- `V1b`（module invocation regression）
  - 命令：`uv run pytest tests/integration/test_cli_module_invocation.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`
  - 结果：PASS（133 passed）
- `V2`（ruff）
  - 命令：`uv run ruff check src tests`
  - 结果：PASS（All checks passed）
- `V2b`（全量 pytest）
  - 命令：`uv run pytest -q`
  - 结果：PASS（2421 passed；在新增 release-build workflow 前完成，新增 workflow 后已补定向 pytest）
- `V3`（约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：PASS（verify constraints: no BLOCKERs）
- `V4`（truth sync dry-run）
  - 命令：`python -m ai_sdlc program truth sync --dry-run`
  - 结果：PASS（source inventory complete, 919/919 mapped）
- `V5`（truth sync execute）
  - 命令：`python -m ai_sdlc program truth sync --execute --yes`
  - 结果：PASS（source inventory complete，written path: `program-manifest.yaml`）
- `V6`（184 plan-check）
  - 命令：`uv run ai-sdlc workitem plan-check --wi specs/184-release-0-7-1-offline-smoke-and-artifact-verification`
  - 结果：非阻断（无 `related_plan`，命令按当前实现返回 exit 1 并提示 skipped）
- `V7`（184 close-check pre-commit）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/184-release-0-7-1-offline-smoke-and-artifact-verification`
  - 结果：预提交阻断；当前仅剩 `git_closure` BLOCKER（latest batch is not marked as git committed）。任务完成、verification profile、program truth、docs consistency 均 PASS；最终 git close-out 需在提交后复跑。

#### 2.3 任务记录

##### T184-001 | Offline smoke action runtime 收口

- 改动范围：`.github/workflows/windows-offline-smoke.yml`
- 改动内容：将 evidence upload 从 `actions/upload-artifact@v4` 升级到 `actions/upload-artifact@v7`
- 新增/调整的测试：`tests/integration/test_github_workflows.py`
- 执行的命令：`uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`
- 测试结果：PASS
- 是否符合任务目标：符合

##### T184-002 | Release artifact smoke workflow

- 改动范围：`.github/workflows/release-artifact-smoke.yml`
- 改动内容：新增 workflow，支持从 GitHub Release 下载 `.zip` / `.tar.gz` 资产并安装验证；追加 `release-build.yml`，支持云端 Windows / macOS / Linux matrix 构建、smoke、上传 release assets
- 新增/调整的测试：`tests/integration/test_github_workflows.py`
- 执行的命令：`uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`
- 测试结果：PASS
- 是否符合任务目标：符合；发布后仍需真实 GitHub Release assets 触发 smoke，release build workflow 也需在云端对 tag `v0.7.1` 运行

##### T184-003-T184-005 | 0.7.1 版本与入口真值

- 改动范围：`pyproject.toml`、`uv.lock`、`src/ai_sdlc/__init__.py`、`src/ai_sdlc/core/verify_constraints.py`、`README.md`、`USER_GUIDE.zh-CN.md`、`packaging/offline/README.md`、`packaging/offline/RELEASE_CHECKLIST.md`、`docs/releases/v0.7.1.md`、`docs/pull-request-checklist.zh.md`
- 改动内容：将当前 staged release 入口推进到 `v0.7.1`
- 新增/调整的测试：`tests/unit/test_packaging_backend.py`、`tests/unit/test_verify_constraints.py`
- 执行的命令：`uv run pytest tests/integration/test_cli_module_invocation.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_packaging_backend.py tests/unit/test_verify_constraints.py -q`；`uv run ai-sdlc verify constraints`；`python -m ai_sdlc program truth sync --execute --yes`
- 测试结果：PASS
- 是否符合任务目标：符合

##### T184-006/T184-008 | 本地验证归档与云端发布构建 handoff

- **改动范围**：`.github/workflows/windows-offline-smoke.yml`、`.github/workflows/release-artifact-smoke.yml`、`.github/workflows/release-build.yml`、`pyproject.toml`、`uv.lock`、`src/ai_sdlc/__init__.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/integration/test_github_workflows.py`、`tests/integration/test_offline_bundle_scripts.py`、`tests/integration/test_cli_module_invocation.py`、`tests/unit/test_packaging_backend.py`、`tests/unit/test_verify_constraints.py`、`README.md`、`USER_GUIDE.zh-CN.md`、`packaging/offline/README.md`、`packaging/offline/RELEASE_CHECKLIST.md`、`packaging/install_online.sh`、`packaging/offline/build_offline_bundle.sh`、`docs/releases/v0.7.1.md`、`docs/pull-request-checklist.zh.md`、`docs/框架自迭代开发与发布约定.md`、`program-manifest.yaml`、`specs/184-release-0-7-1-offline-smoke-and-artifact-verification/*`
- 改动内容：记录本批 code-change 验证画像、验证命令、truth sync execute、全量回归结果、云端 release build workflow 与发布后 handoff 边界
- 新增/调整的测试：修复/同步全量测试暴露的 7 个失败点：`npx` 测试替身接管、git commit timestamp UTC 归一、status linked WI reviewer decision 展示、managed delivery 自动继承 generation/quality 后的 status 期望
- 执行的命令：见 2.2
- 测试结果：PASS（2421 passed；ruff / verify / dry-run 通过）；`close-check` 仍需提交后复跑消除 git closure blocker
- 是否符合任务目标：符合当前 PR 收口目标

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：符合。已先执行 dry-run；release docs、workflow、tests 与 program truth 同步。
- 代码质量：符合。workflow 保持 evidence artifact 合同，新增 release smoke 只消费 GitHub Release assets，不构建/替代正式资产。
- 测试质量：符合。workflow 合同、版本 dist-info、release docs consistency 与 module invocation regression 均有 pytest 覆盖；ruff 通过。
- 结论：`无 Critical 阻塞项`；最终发布仍需 PR 合并后 tag / release assets / release-artifact-smoke 证据。

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：已同步
- `related_plan`（如存在）同步状态：无
- 关联 branch/worktree disposition 计划：待最终收口
- 说明：`workitem init` 因当前分支不是该 WI 的 docs branch 而拒绝自动 materialize；本批在当前用户指定续作上下文中手动创建 canonical docs，并保留该约束事实。发布后 `release-artifact-smoke.yml` 是 post-release handoff，不在当前 PR close-check checklist 中伪装完成。

#### 2.6 自动决策记录（如有）

- AD-184-001：采用 `actions/upload-artifact@v7`，依据官方 action README 和 release page 当前示例 / 最新版本线。
- AD-184-002：release artifact smoke 不负责构建或上传 release assets，只消费 GitHub Release 已发布资产，避免把源码树临时构建误当正式发布资产。

#### 2.7 批次结论

- 本地 `0.7.1` release-path hardening 已完成：offline smoke action 升级到 `v7`，新增 release artifact smoke workflow，版本/docs/constraints 同步到 `v0.7.1`，program truth snapshot 已刷新。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`5a1c3c7`
- 当前批次 branch disposition 状态：待最终收口
- 当前批次 worktree disposition 状态：retained（当前分支已有用户/历史改动，未切换分支）
- 是否继续下一批：是
