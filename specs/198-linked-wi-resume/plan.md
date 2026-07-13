---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# Linked Work Item Resume Working Set Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox syntax in `tasks.md`; final reviewer verdicts live only in the execution log/handoff to avoid a self-referential hash.

**Goal:** 修复 WI-196 GAP-08，使 resume-pack、handoff 与 recover 的 working set/branch 始终遵守 active linked WI，并自动迁移升级前仍被判 fresh 的历史错误 pack。

**Architecture:** 保留 `active_work_item_id()` 为唯一 active-WI resolver，把已解析 `work_item_id` 传入现有私有 filesystem fallback。非空 linked id 使用 canonical `specs/<linked>`；否则严格沿用 `feature.spec_dir`。linked fresh pack load 时至多构建一次同源 expected pack并窄比较 spec/plan/tasks/current_branch，让 legacy mismatch 复用既有 stale rebuild和该 expected pack；仅 semantic 校验读取损坏 optional artifact 时跳过迁移以保持旧成功合同。branch 优先 linked runtime，无 linked runtime 时 fail-closed。模型、状态与 CLI 均不变。

**Tech Stack:** Python 3.11、Pydantic、Typer/Click、pytest、`pathlib.Path`、uv、Ruff。

## Global Constraints

- 基线：`origin/main@4802596f9ef2fda8c27717c25d6760ed09136811`。
- 只实现 WI-196 GAP-08/T52；不修改 checkpoint schema、历史 feature/stage 或其他 gap。
- 产品净新增 ≤20 LOC；测试新增 ≤140 LOC；不新增产品/测试文件、公共抽象、依赖、配置或 schema。
- 受影响契约仅 CC-03、CC-04、CC-06、CC-07。
- linked target 缺失必须 fail-closed，禁止回退历史 feature docs。
- linked runtime 缺失/branch 为空时 branch 必须 fail-closed；legacy fresh 错误 pack 必须自愈。
- 每个生产改动前必须有对应 RED；修复后先 focused GREEN，再跑 full verification。
- docs branch 只冻结合同；runtime 变更在独立 dev branch 完成。

---

## 1. 文件与接口边界

允许修改的产品文件：

```text
src/ai_sdlc/context/state.py
  load_resume_pack(...)
  _build_resume_pack_from_checkpoint(...)
  _build_resume_working_set(...)
  _build_resume_working_set_from_filesystem(...)
```

允许修改的测试文件：

```text
tests/unit/test_context_state.py
tests/integration/test_cli_handoff.py
tests/integration/test_cli_recover.py
```

只回归、不修改：

```text
tests/unit/test_handoff.py
tests/integration/test_cli_status.py
```

若需要第二个产品文件、第四个测试修改文件或任何新文件，立即停止并重做 NC-02/NC-03。

## 2. Task 1：合同、基线与双 Agent admission

1. 用 canonical CLI 创建 WI-198 四件套并登记 program manifest/next sequence。
2. 冻结 observed/expected、三种方案、受影响 CC、预算、文件边界、停止与回退。
3. 记录 mainline tree equality、targeted `26 passed` 与 WI-198 focused baseline `33 passed`。
4. 计算 `spec.md + plan.md + tasks.md` bytes 拼接 SHA-256。
5. 兼容安全 Agent 与精简效率 Agent 独立审查同一哈希；任一 finding 成立即修订并重跑，双 PASS 前不进入 execute。

验证：

```bash
uv run ai-sdlc verify constraints
git diff --check
```

## 3. Task 2：RED characterization

### 3.1 Unit：build/load fallback

在 `tests/unit/test_context_state.py` 新增 `test_build_resume_pack_prefers_linked_work_item_docs` 与 `test_load_resume_pack_rebuilds_fresh_legacy_linked_working_set`：

1. 创建历史 feature 与新 linked WI 的完整三件套。
2. checkpoint.feature 指向历史目录，linked_wi_id 指向新目录，不创建 linked working-set artifact。
3. 调用 `build_resume_pack()`；断言 spec/plan/tasks 都来自 linked WI，且没有历史路径。
4. 断言 linked runtime 非空 branch 优先；无 linked runtime 时 branch 为空；无 linked WI 时保留 feature branch。
5. 先用旧语义构造 checkpoint fingerprint、root/scoped equality 均 fresh，但三件套或 branch 仍指向历史 feature 的 pack；覆盖“完整 persisted overlay 已修正 docs、仅 branch 错误”，调用 `load_resume_pack()` 后断言 stale/rebuilt event 并原子纠正两份 pack。
6. 增加 linked 目录缺失/partial docs、persisted overlay、正确 fresh pack、损坏 optional working-set/runtime、无效 UTF-8 latest-summary 与无 linked 非标准 feature.spec_dir 边界，防止错误 fallback、semantic-stale 误判或新增异常。

### 3.2 Integration：handoff

在 `tests/integration/test_cli_handoff.py` 新增 `test_handoff_update_prefers_linked_work_item_working_set`：

1. fixture 同时创建历史 feature 与 linked docs。
2. 执行真实 `handoff update`。
3. 断言 canonical/scoped handoff 的 Work Item 为 linked WI；root 与 linked scoped resume-pack 的三件套均来自 linked WI，legacy fresh pack 也能在 summary refresh 前重建。

### 3.3 Integration：recover rebuild

在 `tests/integration/test_cli_recover.py` 新增 `test_recover_rebuilds_resume_pack_for_linked_work_item`：

1. checkpoint 保留历史 feature 并关联 linked WI。
2. 让 root/scoped pack 缺失、checkpoint-stale 或 legacy-semantic-stale，执行真实 `recover`。
3. 断言 rebuild notice、exit 0、root/scoped pack 同步且三件套来自 linked WI。

RED 命令：

```bash
uv run pytest tests/unit/test_context_state.py -k "linked_work_item_docs or fresh_legacy_linked" -q
uv run pytest tests/integration/test_cli_handoff.py -k "linked_work_item_working_set" -q
uv run pytest tests/integration/test_cli_recover.py -k "linked_work_item" -q
```

期望：至少 unit 与 handoff/recover 中一个因实际路径仍为历史 feature 而失败；fixture/解析错误不算 RED。

## 4. Task 3：最小 GREEN

只在 `src/ai_sdlc/context/state.py`：

1. `_build_resume_working_set()` 调用 filesystem fallback 时传入已解析的 `work_item_id`。
2. `_build_resume_working_set_from_filesystem(root, checkpoint, work_item_id)` 判断 stripped `checkpoint.linked_wi_id`：非空时使用 `root / "specs" / work_item_id`，否则沿用 `root / checkpoint.feature.spec_dir`。
3. `load_resume_pack()` 仅在 linked root pack 结构上 fresh 时至多构建一次 expected pack，窄比较 spec/plan/tasks/current_branch；任一不一致复用现有 `stale` rebuild并直接写该 expected pack，不比较 summary/active_files。
4. 若上述 semantic-only expected build 因 optional working-set/runtime/latest-summary 损坏、无效编码或不可读而抛出 `YamlStoreError`、`UnicodeError` 或 `OSError`，跳过 semantic 迁移并返回既有 fresh pack；若 root/scoped/checkpoint 本来已 stale，仍保持既有 rebuild/error 路径。
5. `_build_resume_pack_from_checkpoint()` 保留 runtime branch 优先；linked id 非空但 runtime branch 缺失时返回空 branch；无 linked id 时继续使用 feature branch。
6. 保留逐文件 exists 检查与 persisted artifact overlay；不得新增 manifest/glob lookup、公共 helper、schema 分支或第二真值源。
7. 运行所有 RED 和五个 focused 回归文件，确认 GREEN。

GREEN 命令：

```bash
uv run pytest tests/unit/test_context_state.py tests/unit/test_handoff.py tests/integration/test_cli_handoff.py tests/integration/test_cli_recover.py tests/integration/test_cli_status.py -q
uv run ruff check src/ai_sdlc/context/state.py tests/unit/test_context_state.py tests/integration/test_cli_handoff.py tests/integration/test_cli_recover.py
git diff --check
```

## 5. Task 4：验证、证据与交付

1. 统计 product/test numstat；超出预算立即停止。
2. 记录 build/handoff/recover 的 artifact before/after。比较前规范化 `timestamp` 与本次命令显式提供的 `context_summary`；approved delta 只允许 linked spec/plan/tasks 与 linked 无 runtime 时的 branch，逐字段证明 stage/batch/task/docs baseline/fingerprint/schema/error 合同无 diff。
3. 运行：

```bash
uv run pytest tests/unit/test_context_state.py tests/unit/test_handoff.py tests/integration/test_cli_handoff.py tests/integration/test_cli_recover.py tests/integration/test_cli_status.py -q
uv run pytest -q
uv run ruff check src tests
uv run ai-sdlc verify constraints
git diff --check
```

4. 生产/测试 task reviewer 分别做 spec-compliance 与 code-quality review；完整 branch 再由兼容安全、精简效率两个 Agent 对抗复审，所有可操作 finding 关闭。
5. 推送 PR，回复 Codex finding（如有），请求当前 HEAD review，并维持约五分钟 heartbeat 至 review/checks 全绿后合并。
6. mainline targeted/truth 复核后更新 WI-196 Gap Evidence Index，将 GAP-08/T52 标为 closed。

## 6. 回退与完成判定

- mainline/发布回退整个 PR merge/squash commit 或包含版本。
- 未合并源码分支按 GREEN 与对应 RED test 成对撤销；不得只撤 runtime 留下必失败测试。
- 只有 PR 合并、mainline targeted/truth fresh、父项 GAP Evidence Index 关闭，T52 才完成。
