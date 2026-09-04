# v0.9.9 Canonical Release Implementation Plan

> **执行约束：** T21、T22、T23、T31、T32 已完成。用户已批准在同一 WI、同一分支和原 PR 上执行一次 `F-TRUTH-SCOPE-01` 同根稳定化；本增补取代下方旧的“两轮后终止”表述，但不重新开启其他任务或范围。

**Goal:** 用 WI226 的显式依赖闭包驱动现有逐规格 Program Truth readiness，并把它接入 v0.9.9 的 PR 与 tag 发布门禁。

**Architecture:** `program-manifest.yaml` 是唯一范围来源。现有 `ProgramService.build_spec_truth_readiness()` 保持单规格判定权威；新增一个很薄的 release-candidate 聚合方法，只解析根 WI、遍历 `depends_on` 并汇总已有结果。现有 `program truth audit` 增加可选 `--wi`；无参数路径完全兼容。PR Checks 与 Release Build 调用同一命令，不引入新 ledger、schema、命令或 range inference。

**Tech Stack:** Python 3.11、Typer、Pydantic、PyYAML、pytest、GitHub Actions、uv。

## 不变量与预算

- 全局 Program Truth 继续 `blocked`，16 项历史 blocker 原样保留。
- PR #200 仅属于 WI226 的 R06 partial release composition；不改 WI222/WI224 历史记录。
- 一个 canonical WI、一个实施/发布 PR；仅允许一次 `F-TRUTH-SCOPE-01` 稳定化和一次新的 exact-HEAD 认证。
- 生产代码净新增不超过 150 行；实现与测试不超过 1 人日。
- 本次稳定化主动工程投入硬上限为 4 小时；CI、GitHub API 和评审排队等待不计入。
- API/网络 `unknown` 只重试观察，不消耗代码修复轮次。
- 超预算或需要 schema/ledger/waiver/第二套设计时直接 No-Go，不做边缘修补。

---

### Task 1：冻结 canonical formal baseline

**Files:**

- Modify: `program-manifest.yaml`
- Modify: `.ai-sdlc/project/config/project-state.yaml`
- Create: `specs/226-v0-9-9-canonical-release/spec.md`
- Create: `specs/226-v0-9-9-canonical-release/plan.md`
- Create: `specs/226-v0-9-9-canonical-release/tasks.md`
- Create: `specs/226-v0-9-9-canonical-release/task-execution-log.md`
- Modify: `tests/integration/test_repo_program_manifest.py`（仅同步新增 WI 的 inventory 期望）

**Steps:**

1. 声明 WI226 的 `release_candidate` role 与六个显式依赖。
2. 记录 `v0.9.8@4f3e55c3`、初始远端主线锚点 `8f9df406`、18 个 first-parent carrier 和 PR #200 的 partial 边界。
3. 运行 `uv run ai-sdlc program validate`；预期 manifest 无 error。
4. 运行 `uv run ai-sdlc program truth sync --execute --yes`，只刷新既有 snapshot，不删除 blocker。
5. 运行 `uv run ai-sdlc verify constraints`；预期无 blocker。
6. 运行 `uv run pytest tests/integration/test_repo_program_manifest.py -q`；只允许把既有 inventory 期望同步到实际新增五层后的数值。
7. 完成计划评审与用户批准后，只将 T12 标记 done，并激活 T21；不得预先启动后续任务。

### Task 2：TDD 实现显式依赖闭包 readiness

**Files:**

- Modify: `src/ai_sdlc/core/program_service.py`
- Test: `tests/unit/test_program_service.py`

**Step 1: 写失败测试**

增加以下五类测试：

- 全局 truth blocked、闭包内均 ready 时聚合成功。
- 闭包内任一 spec 命中 release blocker 时失败并只报告相关动作。
- snapshot stale 时失败。
- 根 spec 未声明 `release_candidate` 时失败。
- 重复/传递依赖只评估一次，闭包顺序稳定。

先运行：

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'
```

预期：新增测试因方法不存在而失败。

**Step 2: 最小实现**

复用现有 `ProgramSpecTruthReadinessResult`，不新增结果类型。在 `ProgramService` 只增加：

```python
def build_release_candidate_truth_readiness(
    self,
    manifest: ProgramManifest,
    *,
    spec_path: str | Path,
    validation_result: ProgramValidationResult | None = None,
) -> ProgramSpecTruthReadinessResult:
```

实现顺序固定为：校验 manifest → 唯一路径匹配 → 校验 `release_candidate` role → DFS 收集根与传递依赖 → 对每个成员调用现有 `build_spec_truth_readiness()` → 用现有 `matched_spec_ids`、`detail` 与 `next_required_actions` 去重汇总。不得读取 git range、commit message 或 execution log。

**Step 3: 绿灯与回归**

```powershell
uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'
```

预期：新增测试和既有单规格 readiness 测试全部通过。

### Task 3：TDD 扩展现有 audit CLI

**Files:**

- Modify: `src/ai_sdlc/cli/program_cmd.py:1011`
- Test: `tests/integration/test_cli_program.py`

**Step 1: 写失败测试**

覆盖：`--wi` 成功、相关依赖失败、非 candidate 失败，以及不带 `--wi` 的原输出与退出码不变。

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'
```

预期：Typer 尚不识别 `--wi`，测试失败。

**Step 2: 最小实现**

在 `program_truth_audit()` 增加：

```python
wi: str | None = typer.Option(
    None,
    "--wi",
    help="Audit one release-candidate work item and its declared dependency closure.",
)
```

`wi is None` 时保留现有代码路径；有值时调用 Task 2 的聚合方法，输出根 WI、闭包 spec ids、state、detail 和去重后的 next actions，并以 `ready` 决定 0/1。载入或参数错误继续使用退出码 2。

**Step 3: 验证兼容性**

```powershell
uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit'
```

预期：既有与新增 audit 测试全部通过。

### Task 4：把同一门禁接入 PR 与 tag 构建

**Files:**

- Modify: `.github/workflows/pr-checks.yml`
- Modify: `.github/workflows/release-build.yml`
- Test: `tests/integration/test_github_workflows.py`

**Step 1: 写失败的工作流合同测试**

断言两个工作流均包含：

```powershell
uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release
```

并断言 Release Build 的该步骤在 `Build offline bundle`、attestation 与 `gh release upload` 之前。

```powershell
uv run pytest tests/integration/test_github_workflows.py -q -k 'release_candidate_truth or release_build'
```

**Step 2: 最小工作流改动**

- PR Checks：在 `Verify constraints` 后增加独立 release-candidate truth step。
- Release Build：在 exact-tag checkout、Python/uv setup 后、平台构建前增加相同步骤。
- 不增加 continue-on-error、fallback、waiver 或条件跳过。

**Step 3: 验证 YAML 与顺序**

```powershell
uv run pytest tests/integration/test_github_workflows.py -q
```

预期：全部通过。

### Task 5：同步 v0.9.9 版本与发布入口

**Files:**

- Modify: `pyproject.toml`, `uv.lock`, `src/ai_sdlc/__init__.py`
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `README.md`, `USER_GUIDE.zh-CN.md`
- Modify: `packaging/offline/README.md`, `packaging/offline/RELEASE_CHECKLIST.md`
- Modify: `docs/pull-request-checklist.zh.md`, `docs/框架自迭代开发与发布约定.md`
- Create: `docs/releases/v0.9.9.md`
- Modify: `.github/workflows/release-build.yml`, `.github/workflows/release-artifact-smoke.yml`
- Modify: `.github/workflows/windows-user-guide-e2e.yml`, `.github/workflows/macos-user-guide-e2e.yml`
- Modify: `.github/workflows/windows-update-prompt-e2e.yml`, `.github/workflows/windows-offline-smoke.yml`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_github_workflows.py`
- Test: `tests/integration/test_offline_bundle_scripts.py`
- Modify: `program-manifest.yaml`（仅在 `docs/releases/v0.9.9.md` 已创建的同批次登记 `release_doc/release` source_registry）
- Modify: `tests/integration/test_repo_program_manifest.py`（同批更新 `range(0, 10)` 与 inventory 期望）

**Steps:**

1. 先把一致性测试预期改为 `0.9.9` 并运行，确认红灯来自尚未同步的产品文件。
2. 只替换“当前发布版”和默认 release tag；保留明确的历史 `v0.9.8` 比较叙述。
3. 发布说明按 18 个主线载体归并用户可见价值，不把治理流水账当作产品特性。
4. 创建 `docs/releases/v0.9.9.md` 后，在同一变更批次登记其 `release_doc/release` source_registry，并同步 manifest inventory 测试的 `range(0, 10)`；不得提前登记不存在的 release note。预期登记完成后为 `1180/1180 mapped`、`unmapped 0`、`missing 6`、release layer `45`。
5. 运行 `uv lock` 同步 lockfile。
6. 运行：

```powershell
uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q
uv run ai-sdlc verify constraints
```

预期：全部通过且无 constraint blocker。

### Task 6：终局验证、精确 HEAD 评审与发布

**Files:**

- Modify: `specs/226-v0-9-9-canonical-release/tasks.md`
- Append: `specs/226-v0-9-9-canonical-release/task-execution-log.md`
- Refresh: `program-manifest.yaml` truth snapshot
- Refresh: `.ai-sdlc/state/codex-handoff.md` 与 scoped handoff（若已链接）

**Steps:**

1. 运行 focused suite、`uv run ruff check src tests`、`uv run pytest -q`、`uv run ai-sdlc verify constraints`。
2. 运行 `uv run ai-sdlc program truth sync --execute --yes`，再运行全局 audit 与按 WI226 audit；前者必须保留 16 blocker，后者必须 ready。
3. 更新任务日志，确保只有真实执行结果，不预写 merge/release 成功。
4. 推送唯一实施/发布分支并打开一个 PR；请求一次精确 HEAD Codex review，并启动约五分钟 heartbeat。
5. 认证只接受冻结范围内的 finding；外部 API `unknown` 在同一 HEAD 重试，不记作候选失败或代码修复轮次。
6. required checks 与 review 均通过后合并；确认 `origin/main` 精确等于 merge SHA。
7. 在该 main SHA 创建 `v0.9.9` draft release，运行 Release Build；三平台资产、attestation 和 checksum/smoke 成功后发布。
8. 验证 Windows/macOS 12-route 自然发布回执和 release artifact smoke；失败时只按本规格边界处理直接因果问题。

### Task 7：`F-TRUTH-SCOPE-01` 同根稳定化

**Files:**

- Modify: `src/ai_sdlc/core/program_service.py`
- Test: `tests/unit/test_program_service.py`
- Modify: `specs/226-v0-9-9-canonical-release/tasks.md`
- Append: `specs/226-v0-9-9-canonical-release/task-execution-log.md`

**Steps:**

1. 先增加 persisted ready/blocked 的七成员失败测试，证明共享上下文只能构建一次，且闭包外 blocker 不改变成员 readiness。
2. 让传入的共享 truth surface 成为成员投影的权威输入；共享上下文存在时禁止进入 persisted fast path 或重建 snapshot。
3. 只根据当前成员命中的 capability rows 判定 ready/blocked；缺少预期 row 时继续 fail closed。
4. 运行 focused、全量、Ruff、constraints、program validate、diff-check 和真实规模 scoped audit；全部绑定同一候选 HEAD 后再请求一次冻结范围评审。
5. 若同一 finding family 仍复现、出现第二个 family、超出 150 行/4 小时/文件范围，或最终认证仍有 load-bearing finding，则终止本 WI，不再申请例外。

## 计划自检

- 每个行为都由现有 manifest、readiness 或 workflow 承载；没有第二状态源，也没有新增结果模型。
- 唯一新增 CLI 表面是现有命令的可选 `--wi`，无参数行为有回归测试。
- 计划没有把全局 `blocked` 改成 `ready`，也没有把 PR #200 倒灌为历史 WI 完成。
- 任何超预算情形都结束本 WI，不触发重新设计链。
