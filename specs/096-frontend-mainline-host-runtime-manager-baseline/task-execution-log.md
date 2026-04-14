# 执行记录：Frontend Mainline Host Runtime Manager Baseline

## Batch 2026-04-12-001 | 状态检查与计划续接

### 1. 范围

- 对账当前仓库状态、spec 落点与 work item 序号；
- 判断当前应继续 `095` 还是 `096`；
- 为 `096` 补齐执行骨架：`plan.md`、`tasks.md`、`task-execution-log.md`。

### 2. 事实记录

- `project-state.yaml` 当前 `next_work_item_seq: 97`，说明 `096` 已编号但未进入实现闭环。
- `specs/093-*` 到 `specs/096-*` 目录当前都只有 `spec.md`，尚未补充计划与执行记录。
- `095` 是母规格；`096` 明确声明自己是 `095.Host Readiness` 的第一块 implementable slice。
- `src/ai_sdlc/cli/main.py` 当前只承载 CLI 装配，没有 Host Runtime Manager 对应命令面。
- `packaging/offline/install_offline.sh` 与 `packaging/offline/install_offline.ps1` 仍是人工可读安装入口，尚未进入 `host_runtime_plan` 契约。

### 3. 本批输出

- 新增 [`plan.md`](./plan.md)，固定 `096` 的目标、边界、批次与验证命令；
- 新增 [`tasks.md`](./tasks.md)，把实现拆成可勾选批次；
- 建立本执行记录，保存状态续接依据，便于后续批次直接衔接。

### 4. 决策

- 当前继续目标确定为 `096`，而不是直接把 `095` 展开为完整实现；
- 原因：`096` 的范围清晰、依赖明确，且与仓库现状匹配；`095` 目前仍应作为后续汇总契约存在。

### 5. 验证命令

```bash
git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/tasks.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md
```

### 6. 验证结果

- `git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/tasks.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`：通过。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。

### 7. 当前结论

- `096` 已从“只有规格”推进到“可直接进入实现批次”的状态；
- 下一步应按 `Batch 1` 进入 TDD，先固定 `host_runtime_plan` 的契约与 fail-closed 语义；
- 本批没有引入功能代码，也没有改变运行时行为。

## Batch 2026-04-12-002 | 对抗 review 合同清补

### 1. 范围

- 复核 reviewer 提出的 `.bat` 离线入口缺口是否已真正闭环；
- 清理 `InstallerProfileRef` 段内部仍残留的 profile 命名不一致。

### 2. 事实记录

- `.bat` 入口已经进入 `096` 的模型层说明、FR-096-012 与验收准则，不再是缺失项；
- 但 `InstallerProfileRef` 的 v1 reality 列表仍写成 `offline_bundle_posix`，而同文档的 FR-096-012 与执行计划使用 `offline_bundle_posix_shell`；
- 仓库内没有其他正式 baseline 或实现代码引用 `offline_bundle_posix`，因此这属于 `096` 内部合同命名未完全统一，而不是跨文件兼容约束。

### 3. 本批输出

- 将 `InstallerProfileRef` 段的 POSIX profile 名称统一为 `offline_bundle_posix_shell`；
- 保持 Windows PowerShell / `.bat launcher` 的二层语义不变：`.bat` 是受控 launcher alias，不另造执行语义。

### 4. 验证命令

```bash
git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md
```

### 5. 验证结果

- `git diff --check -- specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md specs/096-frontend-mainline-host-runtime-manager-baseline/plan.md specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`：通过。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。

### 6. 当前结论

- reviewer 指出的 `.bat` profile 合同缺口已收口到同一命名体系；
- `096` 目前不存在“模型层漏掉 `.bat` / FR 层承认 `.bat`”这类自相矛盾。

## Batch 2026-04-13-003 | Batch 1-2 and Batch 3 core baseline

### 1. 范围

- 落地 `host_runtime_plan` 的核心 machine contract 与 JSON 序列化真值；
- 实现最小宿主判定、bootstrap acquisition handoff 与 mainline remediation fragment 的主体；
- 用 TDD 固定 unknown platform / unknown runtime / unbound surface / remediation / ready 五类核心分支。

### 2. 事实记录

- 仓库中此前不存在 `src/ai_sdlc/core/host_runtime_manager.py` 与 `host_runtime_plan` 对应模型；
- `096` 的真实缺口集中在 Batch 1-3：contract、判定器、offline profile 映射与 mainline gap 诊断都还没有代码落点；
- CLI 入口与用户文档仍未开始，因此本批只推进 core truth，不引入 mutate surface。

### 3. 本批输出

- 新增 `src/ai_sdlc/models/host_runtime_plan.py`，定义 `HostRuntimePlan`、`HostRuntimeReadiness`、`BootstrapAcquisitionFacet`、`RemediationFragmentFacet` 与 `InstallerProfileRef`；
- 新增 `src/ai_sdlc/core/host_runtime_manager.py`，实现：
  - OS / arch 归一化与支持矩阵；
  - Python 3.11 门槛、installed runtime readiness、surface binding fail-closed 判定；
  - `offline_bundle_posix_shell`、`offline_bundle_windows_powershell`、`offline_bundle_windows_bat_launcher` profile 映射；
  - Node / package manager / Playwright browsers 缺口到 `mainline_remediable` fragment 的映射；
- 当前仍未覆盖 `permission / disk` 等 host blocker reason code；
- 新增 `tests/unit/test_host_runtime_manager.py`，先红后绿固定 Batch 1-3 contract。

### 4. 验证命令

```bash
uv run pytest tests/unit/test_host_runtime_manager.py -q
uv run ruff check src/ai_sdlc/models/host_runtime_plan.py src/ai_sdlc/core/host_runtime_manager.py tests/unit/test_host_runtime_manager.py
uv run ai-sdlc verify constraints
git diff --check
```

### 5. 验证结果

- 首次红灯：`ModuleNotFoundError: No module named 'ai_sdlc.core.host_runtime_manager'`，确认测试确实命中新缺口；
- 绿灯复跑：`uv run pytest tests/unit/test_host_runtime_manager.py -q` 通过（`5 passed`）。
- `uv run ruff check src/ai_sdlc/models/host_runtime_plan.py src/ai_sdlc/core/host_runtime_manager.py tests/unit/test_host_runtime_manager.py`：通过（`All checks passed!`）。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。
- `git diff --check`：通过。

### 6. 当前结论

- `096` 的 Batch 1、2 已完成，Batch 3 还剩 `permission / disk` 类 blocker reason code；
- 当前仍未完成的是剩余 Batch 3 与 Batch 4：CLI 输出入口、CLI 集成测试、`USER_GUIDE.zh-CN.md` 说明和本轮最终收尾验证；
- 本批仍保持只读语义，没有引入下载、安装、升级或回滚动作。

## Batch 2026-04-13-004 | Batch 3 blocker completion and Batch 4 CLI/docs

### 1. 范围

- 补齐 `offline bundle / permission / disk` 类 blocker reason code；
- 为 `096` 增加只读 `host-runtime plan` CLI 入口与 JSON/退出码集成测试；
- 更新 `USER_GUIDE.zh-CN.md` 与 `096/tasks.md`、补齐本轮验证归档。

### 2. 事实记录

- Batch 2026-04-13-003 已落地 core truth，但 `permission / disk` 类 blocker 仍未进入 machine reason code；
- 仓库此前不存在 `src/ai_sdlc/cli/host_runtime_cmd.py`，`ai-sdlc` 主 CLI 也没有 `host-runtime` 子命令；
- `096` 明确要求这条入口保持只读，不得触发 adapter apply，也不得隐式修改宿主环境。

### 3. 本批输出

- 扩展 `HostRuntimeProbe`，补入 `offline_bundle_available`、`bundle_platform_matches`、`install_target_writable`、`disk_space_sufficient`；
- 在 `src/ai_sdlc/core/host_runtime_manager.py` 中补齐：
  - `offline_bundle_missing`
  - `bundle_platform_mismatch`
  - `permission_denied`
  - `disk_space_insufficient`
  这些 blocker reason code 与对应 handoff / blocked 语义；
- 新增 `src/ai_sdlc/cli/host_runtime_cmd.py`，提供 `python -m ai_sdlc host-runtime plan` 与 `--json`；
- 在 `src/ai_sdlc/cli/main.py` 中挂载 `host-runtime` 子命令，并将其加入 read-only exemption，避免触发 IDE adapter apply；
- 新增 `tests/integration/test_cli_host_runtime.py`，固定 JSON 输出与退出语义；
- 更新 `USER_GUIDE.zh-CN.md` 的 operator surface 读写矩阵，明确 `host-runtime plan` 只读且不会静默修改宿主。

### 4. 验证命令

```bash
uv run pytest tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py -q
uv run ruff check src/ai_sdlc/models/host_runtime_plan.py src/ai_sdlc/core/host_runtime_manager.py src/ai_sdlc/cli/host_runtime_cmd.py src/ai_sdlc/cli/main.py tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py
uv run ai-sdlc verify constraints
uv run ai-sdlc host-runtime plan --json
git diff --check
```

### 5. 验证结果

- 红灯阶段：
  - `HostRuntimeProbe.__init__()` 尚不接受 `offline_bundle_available / install_target_writable / disk_space_sufficient`
  - `ai_sdlc.cli.host_runtime_cmd` 尚不存在
  - `offline_bundle_missing` 初版被错误归到 `bootstrap_required`
- 绿灯复跑：
- `uv run pytest tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py -q`：通过（`10 passed`）
- `uv run ruff check src/ai_sdlc/models/host_runtime_plan.py src/ai_sdlc/core/host_runtime_manager.py src/ai_sdlc/cli/host_runtime_cmd.py src/ai_sdlc/cli/main.py tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py`：通过
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc host-runtime plan --json`：在当前源码仓运行时返回 `bootstrap_required` / `surface_binding_unbound`，并输出只读 `host_runtime_plan` JSON；符合 `source runtime` fail-closed 预期。
- `git diff --check`：通过

### 6. 当前结论

- `096` 的 Batch 1-4 与收尾验证项均已完成；
- 当前 `host_runtime_plan` 已具备：
  - fail-closed core contract
  - bootstrap / remediation 分面
  - `offline bundle / permission / disk` blocker reason code
  - 只读 CLI 输出入口与 JSON/退出语义
- 本轮仍保持“只读规划，不执行 mutate”边界，后续真正的下载/安装/确认仍应由 `095` 下游承接。

### Batch 2026-04-14-005 | close-check normalization

#### 2.1 批次范围

- 覆盖目标：补齐 latest batch close-out 必填字段，保持 `host_runtime_manager` 既有 runtime slice 结论不变。
- **改动范围**：`specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`
- 预读范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 激活的规则：`close-check execution log fields`、`verification profile truthfulness`、`git closure truthfulness`

#### 2.2 统一验证命令

- **验证画像**：`docs-only`
- **改动范围**：`specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`
- `V0`（host runtime regression replay）
  - 命令：`uv run pytest tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py -q`
  - 结果：通过（`10 passed in 1.03s`）
- `V1`（work item truth）
  - 命令：`uv run ai-sdlc workitem truth-check --wi specs/096-frontend-mainline-host-runtime-manager-baseline`
  - 结果：通过（read-only truth-check exit `0`）
- `V2`（governance constraints）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过（`verify constraints: no BLOCKERs.`）

#### 2.3 任务记录

##### Task closeout-normalization | latest batch close-check 收口

- 改动范围：`specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`
- 改动内容：补齐 `验证画像`、`改动范围`、`代码审查`、`任务/计划同步状态` 与 git close-out markers；不改变既有 `host-runtime plan`、CLI 或 runtime 行为。
- 新增/调整的测试：无；本批只增加 close-out 归档字段，并 fresh 回放 host runtime regression 与只读真值/约束校验。
- 执行的命令：见 V0-V2。
- 测试结果：V0-V2 通过。
- 是否符合任务目标：符合。当前批次只修正 latest batch 归档真值，不扩张 `096` 的 runtime 完成口径。

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：本批只承接前序 runtime 实现证据，不把 docs-only 收口伪装成新的下载/安装能力。
- 代码质量：本批未修改 `src/` / `tests/`；既有 `host_runtime_manager`、CLI 与 tests 结论保持不变。
- 测试质量：采用 `docs-only` 画像，但 latest batch 额外回放了 host runtime regression；前序 code-change 证据仍留在 `2026-04-13-003/004`。
- 结论：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已对账`
- `plan.md` 同步状态：`已对账`
- `spec.md` 同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`retained（当前在共享工作区完成 close-out normalization，待 capability closure audit 收敛后统一归档）`

#### 2.6 批次结论

- latest batch 已满足 close-check 必填归档字段；`096` 当前仍按既有 runtime slice 口径闭环，不额外声称 mutate surface。

#### 2.7 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：由当前 close-out commit 统一承载；以当前分支 `HEAD` 为准
- 当前批次 branch disposition 状态：`retained`
- 当前批次 worktree disposition 状态：`retained（允许 .ai-sdlc/state/checkpoint.yml* 生成物脏状态）`
