# ProgramService artifact loader 精确重复族减重 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用一个私有 YAML artifact loader 替代 13 个同形 body，真实净删至少 358 行且保持 observable
行为零差异。
**Architecture:** 12 个 ordinary caller 显式传 exact label；保留 cleanup wrapper 承担唯一额外的 warning
normalization。无新模块、registry、reflection、DSL、selector 或依赖。
**Tech Stack:** Python 3.11+、`pathlib.Path`、PyYAML、pytest、Ruff、Git、PowerShell、`uv run ai-sdlc`。

## Global Constraints

- Formal base=`b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`；formal 与 implementation 使用独立 PR。
- 产品只改 `src/ai_sdlc/core/program_service.py`；proof 只改 `tests/unit/test_program_service.py`。
- Product=`+≤48/-≥406`；proof=`+≤48`；mechanical truth=`+≤2`；RC-06 combined≤98/101。
- Terminal loader family≤44 LOC / branch≤4；product net deletion≥358。
- 12 个 caller→label 与 cleanup label 必须逐字使用 spec §2 冻结值。
- 公共 Python/CLI/DTO/artifact/error/path/YAML/warning 行为零未批准差异。
- 不在 17K legacy 文件上运行 write-mode `ruff format`；只运行 Ruff check，并以 diff scope 防 formatter churn。
- 新增注释使用简体中文；本候选不需要解释命名的新增注释。
- 一个 atomic candidate commit 同时包含 product 与 proof；回退该 commit 恢复完整 baseline。
- 任一预算、行为、scope、review 或 required-check 失败均 fail-closed，不扩大合同。
- Active-child pre-close 必须保持 WI217 `development-summary.md` 唯一 mapped/`exists=false`；closure前
  inventory=`complete 1136/1136`、missing/unmapped=`1/0`、close=`216/215`。
- WI217 是减重专项最后一个 work item；formal 后最多一个 implementation PR 和一个 closure PR。
- GO/NO-GO 都由唯一 closure PR 关闭 WI217/WI196、退役 RC-08、把剩余结构债转为非阻塞 backlog；
  closure 后禁止新建减重 work item并恢复正常特性开发。

---

## File Map

| 文件 | 职责 |
|---|---|
| `src/ai_sdlc/core/program_service.py` | common loader、12 个 direct label binding、cleanup wrapper |
| `tests/unit/test_program_service.py` | 12-pair caller-label 与五态 legacy/candidate persistent characterization |
| `specs/217-programservice-artifact-loader-dedupe/{spec.md,plan.md,tasks.md,task-execution-log.md}` | candidate 合同、任务与账本；summary 到 closure 才创建 |
| `specs/196-ai-sdlc-lean-code-self-reduction-governance/*` | parent T63/RC-08 ledger；pre-closure 保持当前事实，唯一 closure 写入路线关闭/退役/backlog 终态 |
| `program-manifest.yaml` | canonical source mapping 与机械 truth snapshot |
| `.ai-sdlc/state/codex-handoff.md` + scoped copy | byte-identical continuity |

## Task 1: Formal-only 准入

**Files:**

- Create: `specs/217-programservice-artifact-loader-dedupe/{spec.md,plan.md,tasks.md,task-execution-log.md}`；
  register but do not create `development-summary.md`
- Modify: `specs/196-ai-sdlc-lean-code-self-reduction-governance/{spec.md,plan.md,tasks.md,task-execution-log.md,development-summary.md}`
- Modify: `.ai-sdlc/project/config/project-state.yaml`, `program-manifest.yaml`
- Modify: `tests/integration/test_repo_program_manifest.py`（只允许两个 exact count）
- Modify/Create: root/scoped `codex-handoff.md`

**Interfaces:**

- Consumes: clean spike ledger `product +48/-406`、proof `+48`、AST `44/4`、R4 双 reviewer PASS0。
- Produces: formal-six=`WI196+WI217` 的 spec/plan/tasks exact identity，以及 implementation admission。

- [ ] **Step 1: 写完四个 pre-close canonical 文档并同步 parent 最小状态**

  不复制 WI216/T66 大型设计，只冻结本 spec 的 13-loader family、预算、impact、stop gate 和回退。

- [ ] **Step 2: 注册 manifest 与 sequence**

  `program-manifest.yaml` 增加 WI217，`depends_on` 只含 WI196；`next_work_item_seq` 为218。正式 source
  commit 后执行：

  ```powershell
  uv run ai-sdlc program truth sync --execute --yes
  ```

  Expected: inventory state=`complete`、mapped=`1136/1136`、close layer=`216/215`、
  missing/unmapped=`1/0`；唯一 missing 是 WI217 `development-summary.md`，overall truth仍ready/fresh。

- [ ] **Step 3: formal gates**

  ```powershell
  uv run pytest -q tests/integration/test_repo_program_manifest.py
  uv run ai-sdlc verify constraints
  uv run ai-sdlc program validate
  uv run ai-sdlc program truth audit
  git diff --check
  ```

  Expected: manifest test `1 passed`；constraints 无 BLOCKER；validate PASS；truth ready/fresh并只含上述
  pre-close missing；diff-check exit0；formal diff 不含 `src/**` 或产品测试逻辑。

- [ ] **Step 4: 同 identity 对抗评审**

  Pascal/LEAN 检查净删、RC-04/05/06、YAGNI 与 claim；Confucius/SAFETY 检查完整语义矩阵、scope、回退和
  continuity。任一 finding 修复后，双方必须对新的 committed+clean HEAD/tree/formal-six 重新审查。

- [ ] **Step 5: formal PR 与 detached fresh-main**

  required checks 全绿且本地双审 PASS0 后 squash merge；detached fresh-main 重跑 Step 3。通过前不得创建
  implementation 分支。

## Task 2: T61A proof 先行并观察 RED

**Files:**

- Modify: `tests/unit/test_program_service.py`
- No product change in this step.

**Interfaces:**

- Consumes: `ProgramService` 12个caller名称、legacy provider-runtime loader、PyYAML、`tmp_path`。
- Produces: 1个内部断言12对的binding case +5个legacy/candidate persistent loader cases，raw additions≤48。

- [ ] **Step 1: 增加 exact proof**

  在标准库 import 中加入 `inspect`，并加入下列测试；总 raw additions 必须≤48：

  ```python
  def test_frontend_artifact_loader_callsite_labels() -> None:
      bindings = {
          "build_frontend_provider_handoff": "remediation writeback",
          "build_frontend_provider_patch_handoff": "provider runtime",
          "build_frontend_cross_spec_writeback_request": "provider patch apply",
          "build_frontend_guarded_registry_request": "cross-spec writeback",
          "build_frontend_broader_governance_request": "guarded registry",
          "build_frontend_final_governance_request": "broader governance",
          "build_frontend_writeback_persistence_request": "final governance",
          "build_frontend_persisted_write_proof_request": "writeback persistence",
          "build_frontend_final_proof_publication_request": "persisted write proof",
          "build_frontend_final_proof_closure_request": "final proof publication",
          "build_frontend_final_proof_archive_request": "final proof closure",
          "build_frontend_final_proof_archive_thread_archive_request": "final proof archive",
      }
      for method_name, artifact_label in bindings.items():
          source = inspect.getsource(getattr(ProgramService, method_name))
          assert f'artifact_label="{artifact_label}"' in source

  @pytest.mark.parametrize("content", [None, "[", "[]", "key: value\n", "<directory>"])
  def test_frontend_artifact_loader_preserves_payload_and_error_contract(tmp_path: Path, content: str | None) -> None:
      root = tmp_path / "root"
      artifact_path = tmp_path / "artifact.yaml"
      if content == "<directory>":
          artifact_path.mkdir()
      elif content is not None:
          artifact_path.write_text(content, encoding="utf-8")
      service = ProgramService(root)
      loader = getattr(service, "_load_frontend_artifact_payload", None)
      if loader:
          payload, warnings = loader(artifact_path, artifact_label="provider runtime")
      else:
          payload, warnings = service._load_frontend_provider_runtime_artifact_payload(artifact_path)
      if content == "key: value\n":
          assert (payload, warnings) == ({"key": "value"}, [])
          return
      suffix = ""
      if content in {"[", "<directory>"}:
          with pytest.raises(Exception) as error:
              yaml.safe_load(content) if content == "[" else artifact_path.read_text()
          suffix = f" ({error.value})"
      prefix = "missing" if content is None else "invalid"
      assert (payload, warnings) == (None, [f"{prefix} provider runtime artifact: {artifact_path}{suffix}"])
  ```

- [ ] **Step 2: 运行 RED**

  ```powershell
  uv run pytest -q tests/unit/test_program_service.py -k 'frontend_artifact_loader_callsite_labels or frontend_artifact_loader_preserves_payload_and_error_contract'
  ```

  Expected: legacy representative五态全GREEN，binding case因caller尚未含`artifact_label`而RED，即
  `1 failed, 5 passed, 406 deselected`。若behavior case失败或binding提前通过，停止实现并复核。

## Task 3: 最小实现并取得 GREEN

**Files:**

- Modify: `src/ai_sdlc/core/program_service.py`
- Test: `tests/unit/test_program_service.py`

**Interfaces:**

- Produces: `_load_frontend_artifact_payload(Path, *, artifact_label) -> tuple[dict | None, list[str]]`。
- Preserves: project-cleanup private wrapper 与六个 caller。

- [ ] **Step 1: 将 12 个 ordinary caller 改为显式 binding**

  每个 caller 使用其现有 path 变量和 exact label：

  ```python
  # build_frontend_provider_handoff
  self._load_frontend_artifact_payload(artifact_path, artifact_label="remediation writeback")
  # build_frontend_provider_patch_handoff
  self._load_frontend_artifact_payload(artifact_path, artifact_label="provider runtime")
  # build_frontend_cross_spec_writeback_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="provider patch apply")
  # build_frontend_guarded_registry_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="cross-spec writeback")
  # build_frontend_broader_governance_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="guarded registry")
  # build_frontend_final_governance_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="broader governance")
  # build_frontend_writeback_persistence_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="final governance")
  # build_frontend_persisted_write_proof_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="writeback persistence")
  # build_frontend_final_proof_publication_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="persisted write proof")
  # build_frontend_final_proof_closure_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="final proof publication")
  # build_frontend_final_proof_archive_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="final proof closure")
  # build_frontend_final_proof_archive_thread_archive_request
  self._load_frontend_artifact_payload(effective_artifact_path, artifact_label="final proof archive")
  ```

  实际文件保留原有多行 call 格式；上面是 exact 参数/变量合同，不允许 mapping/loop/getattr 生成调用。

- [ ] **Step 2: 用一个 helper 替换 13 个 body**

  ```python
  def _load_frontend_artifact_payload(
      self,
      artifact_path: Path,
      *,
      artifact_label: str,
  ) -> tuple[dict[str, object] | None, list[str]]:
      if not artifact_path.exists():
          return None, [
              f"missing {artifact_label} artifact: "
              + _relative_to_root_or_str(self.root, artifact_path)
          ]
      try:
          payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
      except Exception as exc:
          return None, [
              f"invalid {artifact_label} artifact: "
              + f"{_relative_to_root_or_str(self.root, artifact_path)} ({exc})"
          ]
      if not isinstance(payload, dict):
          return None, [
              f"invalid {artifact_label} artifact: "
              + _relative_to_root_or_str(self.root, artifact_path)
          ]
      return payload, []
  ```

  保留 cleanup wrapper：

  ```python
  def _load_frontend_final_proof_archive_project_cleanup_artifact_payload(
      self,
      artifact_path: Path,
  ) -> tuple[dict[str, object] | None, list[str]]:
      payload, warnings = self._load_frontend_artifact_payload(
          artifact_path,
          artifact_label="final proof archive project cleanup",
      )
      if payload is None:
          return None, warnings
      return payload, _normalize_string_list(payload.get("warnings", []))
  ```

- [ ] **Step 3: GREEN 与结构账本**

  ```powershell
  uv run pytest -q tests/unit/test_program_service.py -k 'frontend_artifact_loader_callsite_labels or frontend_artifact_loader_preserves_payload_and_error_contract'
  uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
  git diff --check
  git diff --numstat -- src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
  ```

  Expected: 6 passed、406 deselected；Ruff/diff-check exit0；product additions≤48/deletions≥406，test
  additions≤48。AST 必须为 helper≤33/branch3 + cleanup≤11/branch1。

- [ ] **Step 4: 原子提交**

  ```powershell
  git add src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
  git commit -m "refactor(program): dedupe frontend artifact loaders"
  ```

  Expected: commit 仅含两个允许文件，worktree clean。

## Task 4: T61B、回退与完整验证

**Files:** evidence-only updates to WI196/WI217 non-summary records, manifest/truth and handoff after product
identity is frozen.

- [ ] **Step 1: 运行受影响测试**

  ```powershell
  uv run pytest -q tests/unit/test_program_service.py
  uv run pytest -q tests/integration/test_cli_program.py
  uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py
  ```

  Expected: ProgramService unit=`412 passed`；CLI integration 全部通过；Ruff exit0。

- [ ] **Step 2: 运行全量与治理**

  ```powershell
  uv run pytest -q
  uv run ai-sdlc verify constraints
  uv run ai-sdlc program validate
  uv run ai-sdlc program truth audit
  ```

  Expected: pytest exit0；无 BLOCKER；validate PASS；truth ready/fresh，唯一pre-close summary missing，
  missing/unmapped=`1/0`、close=`216/215`。

- [ ] **Step 3: disposable clone rollback/reapply**

  在隔离临时 clone 定位 atomic candidate commit。revert 后两个 code/test blob 必须等于 fresh-main，
  并运行406项baseline unit；legacy的5 behavior GREEN/1 binding RED已由Task 2独立proof-red worktree回执
  证明，atomic revert后新增proof不存在，不重复要求该结果。reapply后blob等于candidate，6 proof与412 unit全绿。
  所有命令、commit/tree/blob 写入 WI217 execution log；临时 clone 不推送。

- [ ] **Step 4: package/offline/cross-platform**

  本地运行 build 与安装产物 CLI smoke；GitHub required checks 必须包含 Windows/macOS/Linux compatibility、
  POSIX/Windows offline smoke。不得创建 tag、Release、PyPI 上传或全局 CLI 更新。

## Task 5: Final review、PR 与 fresh-main

- [ ] **Step 1: committed+clean same-identity 双审**

  GO时LEAN与SAFETY同时审查candidate commit/tree、final HEAD/tree、formal-six、`+96/-406` code/test diff、
  truth与rollback receipt；NO-GO时双方审查exact失败门、零产品合入与回退状态。任何tracked内容变化使
  两者同时失效。

- [ ] **Step 2: implementation PR**

  只有本地T25 GO才推送最多一个implementation branch并创建一个PR；若此前NO-GO则不创建PR并直接进入
  closure。PR内所有修复/重审留在同一PR，请求Codex review并保持约五分钟heartbeat；若Codex服务不可用，
  仅在用户已经授权的本地 SDLC 双审替代范围内继续，required CI 不得 waiver。

- [ ] **Step 3: merge 与 detached fresh-main acceptance**

  GO路径在current-head无actionable finding、required checks全绿且LEAN/SAFETYPASS0后squash merge，
  不删除本地branch。detached fresh-main重跑Task3 Step3与Task4全部验证，并证明merge tree包含exact
  reviewed product/test blobs。PR阶段若转NO-GO，则关闭该唯一PR、不合入产品并直接进入closure。

- [ ] **Step 4: closure receipt**

  唯一独立 records-only PR 创建 WI217 `development-summary.md`，把missing归零、close恢复`216/216`。
  GO 路径登记实际 product net -358；NO-GO 路径登记零产品合入并关闭未合入的单一 implementation PR。
  两条路径都关闭 WI217/WI196，把 RC-08 记为 `retired_unrealistic_composite_target`，并将 GAP-01/GAP-03～06、
  T62～T67 剩余结构债转为非阻塞 backlog。Closure fresh-main 后恢复正常特性开发，禁止再选择或创建
  gap/reduction work item；本路线不执行版本发布。
