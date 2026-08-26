# 实施计划：主线真值复位与轻量 ROI 合同

> **执行要求**：逐任务使用 `superpowers:test-driven-development`；当前会话使用
> `superpowers:executing-plans` 内联执行。每个产品批次必须先看到预期 RED，再做最小 GREEN，并独立提交。

**编号**：`219-mainline-truth-roi-contract`
**状态**：用户已批准实施（2026-08-25）
**规格**：`specs/219-mainline-truth-roi-contract/spec.md`

## 目标与架构

**目标**：让 truth-check、status/execute/resume 与两条 spec 生成路径在远端主线事实、linked-first 活动工作项
和轻量 ROI 语义上保持一致，同时不新增状态机、parser、公共 API 或运行时治理面。

**架构**：Track A0 在既有 `workitem_truth.py` 内完成 behind-only 基线选择和精确 formal-control 路径分类；
Track A1 在 `context/state.py` 增加一个无 I/O 的 spec-dir 纯解析 helper，现有消费者只复用该结果；Track B
只修改两份现有模板，并通过两条真实渲染路径验证同一 canonical semantic set。

**技术栈**：Python 3.11+、Typer CLI、Pydantic checkpoint model、pytest、Jinja2、Git CLI（只读比较）。

## 全局约束

- 固定比较基线为 `origin/main@762527466119dde127d7488b73d5592e44afaaa6`；忽略产品站及本地材料分支。
- 不复制参赛版本代码，只实现已批准的行为合同。
- 不修改 GitClient、workitem link writer、Runner、ProgramService、status 输出 schema/格式或 checkpoint schema。
- 不新增命令、状态、ledger、certificate、receipt、waiver、parser 或 close 权限。
- 40–80 产品 LOC、180–300 测试 LOC 仅是 cost/risk 信号；只有越过冻结边界或缺少行为证据才暂停。
- 任一批次需要新增公共面、持久化状态或泛化策略引擎时立即 No-Go，不由后续批次掩盖。

## 文件职责

| 文件 | 职责 |
|---|---|
| `src/ai_sdlc/core/workitem_truth.py` | A0：只读基线选择和三态 truth classification |
| `tests/integration/test_cli_workitem_truth_check.py` | A0：真实 Git fixtures 与 CLI classification 回归 |
| `src/ai_sdlc/context/state.py` | A1：唯一 active id/spec-dir 纯解析语义与 resume fallback |
| `src/ai_sdlc/telemetry/readiness.py` | A1：status 的 Program Truth、frontend、branch、diagnostics、backlog 消费 |
| `src/ai_sdlc/core/execute_authorization.py` | A1：execute authorization 复用 active binding |
| `tests/unit/test_context_state.py` | A1：valid/no-link/missing/partial resume 与 helper 单测 |
| `tests/unit/test_telemetry_readiness.py` | A1：linked-first 和 main/close terminal 矩阵 |
| `tests/unit/test_execute_authorization.py` | A1：linked target 可用/缺失/fail-closed |
| `tests/integration/test_cli_status.py` | A1：真实 link→status 跨消费面闭环（仅在 unit 无法证明时修改） |
| `templates/spec-template.md` | B：direct-formal spec 的 ROI 语义提示 |
| `src/ai_sdlc/templates/spec.md.j2` | B：stage/native spec 的 ROI 语义提示 |
| `tests/unit/test_workitem_scaffold.py` | B：direct-formal 真实 scaffold 语义回归 |
| `tests/unit/test_doc_gen.py` | B：stage/native 真实 render 语义回归 |

---

### Task 1：A0 stale-main 基线与 formal-only 分类

**接口**：

- 消费：既有 `GitClient.branch_exists`、`resolve_revision`、`is_ancestor`、`changed_paths`。
- 产出：`_detect_base_ref(git: GitClient) -> str | None` 仍保持私有签名；新增私有
  `_is_formal_freeze_only_change_set(paths: tuple[str, ...], wi_rel: str) -> bool`，不产生公共 API。

- [x] **Step 1：写 behind-only 与 formal-control RED**

  在 `tests/integration/test_cli_workitem_truth_check.py` 增加真实 Git fixtures，至少覆盖：
  `origin/main` 严格领先本地 main、remote 缺失、本地领先、双方分叉；记录 `show-ref` 前后完全一致。
  再增加 WI219 精确 control-file 集合为 `formal_freeze_only`，以及额外 `src/`、普通 test、配置或产品文档
  后转为 `branch_only_implemented` 的参数化用例。期望值必须使用字面量，不从生产 allowlist 反推。

- [x] **Step 2：运行 RED 并确认失败原因**

  ```powershell
  uv run pytest tests/integration/test_cli_workitem_truth_check.py -q
  ```

  预期：stale-local-main fixture 暴露远端主线历史产品路径；精确 formal control fixture 仍被当前
  `execution_log/test/other_paths` 逻辑判为 `branch_only_implemented`。不得接受 fixture 或语法错误型 RED。

- [x] **Step 3：做最小 GREEN**

  在 `workitem_truth.py` 内保持 local `main/master` 为默认，仅当已有 `origin/<default>`、两端 SHA 不同且
  `git.is_ancestor(local, remote)` 为真时返回 remote ref；不得 fetch 或写 ref。

  formal-control helper 只构造以下字面路径集合：当前 WI 四份 formal 文档、project-state、checkpoint、两份
  handoff、resume-pack、program-manifest 和 root manifest test。只有 changed paths 非空且全部属于该集合时
  才忽略 execution-log/path 证据；任一范围外路径都令 `execution_started=True`。

- [x] **Step 4：运行 GREEN 与 A0 回归**

  ```powershell
  uv run pytest tests/integration/test_cli_workitem_truth_check.py -q
  uv run ruff check src/ai_sdlc/core/workitem_truth.py tests/integration/test_cli_workitem_truth_check.py
  ```

- [x] **Step 5：A0 Go/No-Go 与提交**

  若需要修改 GitClient、读取网络、解析 Markdown/YAML 内容或新增 classification 状态则 No-Go；否则提交：

  ```powershell
  git add src/ai_sdlc/core/workitem_truth.py tests/integration/test_cli_workitem_truth_check.py
  git commit -m "fix: align work item truth with remote main"
  ```

### Task 2：A1 linked-first active binding 全消费面统一

**接口**：

- 产出：`active_work_item_spec_dir(checkpoint: Checkpoint | None) -> str`；linked 非空时返回
  `specs/<linked_wi_id>`，否则原样返回 historical `feature.spec_dir`，不可用时返回空字符串。
- 消费：resume filesystem fallback、readiness 的三个 binding loader、Program Truth、frontend evidence、
  branch lifecycle、workitem diagnostics、backlog breach guard 和 execute authorization。

- [x] **Step 1：写纯 helper 与 consumer matrix RED**

  在三个 unit test 文件中使用 historical feature=WI204、linked=WI219 的真实 Checkpoint，覆盖：valid link、
  no/blank link、linked directory missing、formal docs partial、non-main/non-close、main+close 未 merged、
  main+close 已 merged、strict checkpoint load。断言所有 consumer 的 id/path 都是 WI219，且 missing/partial
  fail-closed，绝不读取 WI204。

  只有 unit 无法证明 status 聚合闭环时，才在 `tests/integration/test_cli_status.py` 增加一条真实 CLI JSON 用例，
  断言 Program Truth、frontend、branch lifecycle、diagnostics、backlog 与 execute 均绑定 linked target。

- [x] **Step 2：运行 RED 并确认失败原因**

  ```powershell
  uv run pytest tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py -q
  ```

  预期：resume 已有局部 linked-first 行为通过，但 readiness/backlog/execute 仍返回历史 feature id/spec-dir。

- [x] **Step 3：实现单一纯解析 helper 并复用**

  在 `context/state.py` 增加：

  ```python
  def active_work_item_spec_dir(checkpoint: Checkpoint | None) -> str:
      if checkpoint is None:
          return ""
      linked = (checkpoint.linked_wi_id or "").strip()
      if linked:
          return f"specs/{linked}"
      if checkpoint.feature is None:
          return ""
      return (checkpoint.feature.spec_dir or "").strip()
  ```

  resume、readiness 与 execute 只调用 `active_work_item_id` / `active_work_item_spec_dir`；保留现有文件 I/O、
  branch/stage 判断、错误文本和 strict checkpoint 校验。不得修改 backlog guard 本体或 status 展示。

- [x] **Step 4：运行 GREEN 与真实 CLI 闭环**

  ```powershell
  uv run pytest tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q
  uv run ruff check src/ai_sdlc/context/state.py src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/core/execute_authorization.py tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py
  ```

- [x] **Step 5：A1 Go/No-Go 与提交**

  若需要新 writer/schema/status 格式、第二个 resolver 或 silent historical fallback 则 No-Go；否则提交：

  ```powershell
  git add src/ai_sdlc/context/state.py src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/core/execute_authorization.py tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py
  git commit -m "fix: unify linked work item consumers"
  ```

  若 `tests/integration/test_cli_status.py` 未修改，提交时不得为凑清单触碰该文件。

### Task 3：B 双模板轻量 ROI semantic set

**接口**：仅生成 Markdown 提示；不新增 parser、model、Enum、持久化字段或 blocker。

- [x] **Step 1：写两个真实路径的 semantic RED**

  在 `tests/unit/test_workitem_scaffold.py` 对 `WorkitemScaffolder.scaffold()` 生成的 spec 断言六项提示、
  `implement/defer/needs_user/not-applicable`、一行轻量例外、400/50 仅为风险信号，以及允许成为 blocker 的
  范围扩展/缺证据/安全/隐私/数据/兼容/回归类别。

  在 `tests/unit/test_doc_gen.py` 对 `DocScaffolder().render("spec.md.j2", context)` 的真实输出执行同一组
  test-only semantic assertions；测试比较语义集合，不要求两模板逐字一致。

- [x] **Step 2：运行 RED 并确认缺少 ROI 段落**

  ```powershell
  uv run pytest tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py -q
  ```

- [x] **Step 3：只修改两份模板完成 GREEN**

  两份模板均新增“ROI 与实现边界”段，包含规格 §4.2 的六项、四个 canonical decision、轻量例外、risk-only
  数值解释和 blocker 边界。自然语言可以不同，但不得把 advisory 写成自动 blocker。

- [x] **Step 4：运行 GREEN 与模板回归**

  ```powershell
  uv run pytest tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py tests/integration/test_cli_workitem_init.py -q
  uv run ruff check tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py
  ```

- [x] **Step 5：B Go/No-Go 与提交**

  若模板无法在不改生产 Python 的情况下生成语义段，先暂停复核；不得直接扩展 scaffold API。否则提交：

  ```powershell
  git add templates/spec-template.md src/ai_sdlc/templates/spec.md.j2 tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py
  git commit -m "docs: add lightweight ROI prompts to specs"
  ```

### Task 4：统一验证、证据刷新与交付

- [x] **Step 1：运行 focused 与 full verification**

  ```powershell
  uv run pytest tests/integration/test_cli_workitem_truth_check.py tests/unit/test_context_state.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py tests/integration/test_cli_workitem_init.py -q
  uv run pytest -q
  uv run ruff check .
  uv run ai-sdlc verify constraints
  uv run ai-sdlc program truth audit
  git diff --check 762527466119dde127d7488b73d5592e44afaaa6..HEAD
  ```

- [x] **Step 2：核对 ROI 与冻结边界**

  记录产品/测试净新增、修改文件、调用方覆盖和任何例外；数字超预期只触发证据复核，不自动删测试或停工。
  若修改了冻结范围外文件或引入新 public/persistent/runtime surface，则回退对应 batch 并 No-Go。

- [x] **Step 3：刷新 task log、Program Truth 与 continuity**

  通过 `uv run ai-sdlc handoff update` 记录准确命令、结果、风险和下一步；同步 manifest 后重跑 root manifest test。

- [x] **Step 4：完成本地只读 PR review 后交付主线流程**

  冻结 exact HEAD/diff，执行本地独立只读 review；无可操作问题后 push、开 PR、请求 Codex review，并按仓库
  Local Repository PR Protocol 持续监控 required checks，直到合并或出现用户输入 blocker。
