# 任务执行日志：Linked Work Item Resume Working Set

**功能编号**：`198-linked-wi-resume`
**创建日期**：2026-07-13
**状态**：GREEN 与完整回归通过，待 final branch 双 Agent 评审

## 1. 固定合同

- 父项：WI-196 `GAP-08 / T52`。
- 基线：`origin/main@4802596f9ef2fda8c27717c25d6760ed09136811`。
- docs branch/worktree：`feature/198-linked-wi-resume-docs` / `.worktrees/198-linked-wi-resume`。
- runtime branch：`codex/198-linked-wi-resume`，只在双 PASS 后进入。
- 允许产品文件：`src/ai_sdlc/context/state.py`。
- 允许修改测试：`tests/unit/test_context_state.py`、`tests/integration/test_cli_handoff.py`、`tests/integration/test_cli_recover.py`。
- 只回归测试：`tests/unit/test_handoff.py`、`tests/integration/test_cli_status.py`。
- 预算：产品净新增 ≤20 LOC，测试新增 ≤140 LOC；0 新文件/公共抽象/依赖/配置/schema。
- 回退 owner：framework maintainer；mainline/发布回退整个 PR/版本，分支源码按 GREEN+RED 成对回退。

## 2. Batch 2026-07-13-001：mainline 与 child WI admission

### 2.1 WI-197 mainline 关闭证据

- PR `#121` 在 Codex 当前 HEAD 无问题、22 项 checks 全绿后 squash merge。
- merge commit：`4802596f9ef2fda8c27717c25d6760ed09136811`。
- merged `origin/main` 与已验收 branch tree hash 均为 `90da33d6ac6b0c911b2bf0ce91c8b04b90a12e04`，无内容漂移。
- mainline-equivalent targeted：`26 passed in 11.79s`。
- mainline truth audit：snapshot `fresh`；`1013/1046 mapped`、`33 unmapped`、`11 missing` 与既有三个 frontend/adapter blockers 均未漂移，返回预期 exit 1。

### 2.2 WI-198 初始化

- `uv run ai-sdlc workitem init --title "Linked Work Item Resume Working Set" --wi-id "198-linked-wi-resume" ...` 成功创建 canonical 四件套并登记 program manifest；project next sequence 更新到 199。
- init adapter 改写 `.cursor/rules/ai-sdlc.mdc`；该文件不属于 WI-198，已用 `apply_patch` 精确恢复，未混入设计范围。
- 新隔离 worktree targeted baseline：`26 passed`。
- WI-198 直接受影响 focused baseline：
  - `uv run pytest tests/unit/test_context_state.py tests/unit/test_handoff.py tests/integration/test_cli_handoff.py tests/integration/test_cli_recover.py -q`
  - 结果：`33 passed in 1.34s`。
- focused Ruff：`All checks passed!`；`git diff --check`：PASS。

### 2.3 WI-198 program truth

- `uv run ai-sdlc program truth sync --execute --yes`：成功写入 WI-198 mapping 与快照；snapshot hash `e1fb49e6cb81c81abc75af23d88cc9634f1ad3c1ddfcd49662f12b16a665f58b`。
- `uv run ai-sdlc program truth audit`：snapshot `fresh`；`1018/1051 mapped`、`33 unmapped`、`12 missing`，spec/plan/tasks/execution 为 `199/199`，close 为 `187/199`；既有三个 frontend/adapter blockers 未扩大，返回预期 exit 1。
- truth 命令再次改写 `.cursor/rules/ai-sdlc.mdc`；已用 `apply_patch` 精确恢复并确认该文件相对 HEAD 无差异。

## 3. 事实审计与方案裁决

### 3.1 根因链

1. `active_work_item_id()` 正确让 stripped `linked_wi_id` 优先。
2. `_build_resume_pack_from_checkpoint()` 用该 active id 读取 runtime/summary/working-set artifact。
3. `_build_resume_working_set()` 在 artifact 缺失/不完整前先调用 filesystem fallback。
4. `_build_resume_working_set_from_filesystem()` 只读取 `checkpoint.feature.spec_dir`，导致 active id 与三件套路径分裂。
5. handoff update 与 recover rebuild 都复用 build/load resume-pack，因此传播同一错误路径。

### 3.2 方案

- A（采用）：把已解析 active id 传给现有私有 fallback；linked 非空使用 `specs/<linked>`，否则沿用 feature.spec_dir。
- B（拒绝）：link 时改写 feature；会改变历史 checkpoint/branch/stage 语义。
- C（拒绝）：manifest/glob lookup；引入第二真值源、额外 I/O 与不确定 fallback。

### 3.3 当前风险

- linked target 缺失时若错误回退历史 docs，会继续造成静默错恢复；因此冻结 fail-closed 空字段。
- persisted working-set artifact 可能掩盖 filesystem bug；RED fixture 必须明确不创建该 artifact，并另有 overlay 回归。
- 全量/CLI 可能改写 adapter 或 resume state；每次验证后必须核对并只恢复可证明副作用。

### 3.4 修复前 continuity artifact

- `uv run ai-sdlc workitem link --wi-id 198-linked-wi-resume --plan-uri specs/198-linked-wi-resume/plan.md` 后，checkpoint active link 已切为 WI-198。
- 随后的真实 `uv run ai-sdlc handoff update ...` 正确写出 canonical 与 WI-198 scoped handoff，二者 `Work Item` 为 `198-linked-wi-resume`。
- 同次 refresh 生成的 root 与 WI-198 scoped `resume-pack.yaml` 却仍把 `spec_path / plan_path / tasks_path` 全部指向 `specs/197-adapter-preflight-order/`；这份 before artifact 直接证明 GAP-08，不是测试构造推断。
- 命令触发的 `.cursor/rules/ai-sdlc.mdc` 副作用已精确恢复；GREEN 后必须用同一 continuity 路径生成只指向 `specs/198-linked-wi-resume/` 的 after artifact。

## 4. 设计评审记录

### 4.1 Round 1：hash `eb23ca472127266e596c462822daae9e8f23666b4254a47ef7f567b43ef85b6c`

- 精简效率 Agent：PASS，确认原方案是最短私有调用链修复、无重复 resolver/overlay、预算可执行。
- 兼容安全 Agent：FAIL，提出三项可操作 finding：
  1. 升级前生成但 fingerprint/root/scoped equality 仍 fresh 的错误 pack 不会被只改 builder 的方案自动纠正；
  2. 父项 T52 明确包含 current branch 派生，而原子项错误冻结 branch 不变；
  3. artifact “其他字段无 diff” 未排除必变 timestamp 与命令显式 summary。
- 根因复核：三项均成立。旧 `load_resume_pack()` 只按 checkpoint freshness/root-scoped equality 返回，handoff 随后原样保存；linked 无 runtime 时 branch 回退 feature；rebuild 会更新时间戳。
- 处置：原 PASS 随目标变化失效。合同增加 legacy semantic-stale 自动重建、linked branch fail-closed 与 artifact normalizer；仍只修改 `state.py`，预算调整为产品净新增 ≤20 LOC、测试新增 ≤140 LOC。

### 4.2 Round 2 candidate

- review target：`spec.md + plan.md + tasks.md` bytes 拼接 SHA-256 `6908c6a1da675c83ab70b2d1be07369d4f8662403119cd519fcfbfa210c1e3d5`。
- root 与两个 Agent 独立发现同一剩余 P1：完整 persisted overlay 可让 docs 已正确，但旧 fresh pack 的 branch 仍历史；只比较三件套无法迁移。
- 兼容安全 Agent 另发现：semantic builder 读取损坏 optional artifact 会让旧 fresh 成功路径新增 `YamlStoreError`；接口边界也漏列 load/build-pack 两个函数。Round 2 结论为 FAIL，精简 Agent 已暂停旧候选。
- 处置：semantic comparison 改为同源 expected pack 的 spec/plan/tasks/current_branch；expected pack 至多构建一次并在 stale rebuild 复用；semantic-only optional artifact 解析失败跳过迁移，保持旧成功/error 合同；接口边界明确列出四个实际函数。

### 4.3 Round 3 candidate

- review target：`spec.md + plan.md + tasks.md` bytes 拼接 SHA-256 `a2c882515543a7b474aa61d8b4cca5e9e44751b57303ce3f3764cb98aef79bfe`。
- 两个 Agent 独立给出同一 FAIL：完整 expected pack 还会读取 `latest-summary.md`，无效 UTF-8/不可读会抛 `UnicodeError`/`OSError`，原设计只处理 `YamlStoreError`，会扩大旧 fresh 成功路径异常面。
- 安全 Agent 另指出 tasks 仍写成“两函数私有调用链”，未与 plan/NC-02 的四函数边界对齐。
- 处置：semantic-only expected build 的兼容跳过范围精确扩为 `YamlStoreError`、`UnicodeError`、`OSError`；增加 invalid UTF-8 latest-summary 回归；tasks 改为冻结四函数边界。真正 stale 的既有 error 路径不变。

### 4.4 Round 4 candidate

- review target：`spec.md + plan.md + tasks.md` bytes 拼接 SHA-256 `8ac337e615eb0f1f6bc626515a9be72fec1acb379ab01994611be4cbe0cd5118`。
- 兼容安全 Agent：PASS；哈希一致；`未发现可操作问题`。确认历轮 legacy docs/branch、optional artifact error、linked/no-linked、artifact normalizer 与四函数边界 findings 全部闭合。
- 精简效率 Agent：PASS；哈希一致；`未发现可操作问题`。确认 expected pack 至多构建一次且 mismatch 直接复用，20/140 LOC 预算现实，unit/handoff/recover 分层无过度测试。
- 一致结论：Round 4 同哈希双 PASS，设计 admission gate 关闭；允许提交 docs baseline 并进入 runtime branch 的严格 RED→GREEN。
- 任一 finding 成立即修订并重算；两个 Agent 对同一哈希 PASS 前不进入 runtime branch。

## 5. Batch 2026-07-13-002：T21 RED characterization

- docs baseline commit：`30bcbf89`；已 fast-forward 到 runtime branch `codex/198-linked-wi-resume`。
- RED test commit：`a0196fd2`；只修改三个获准测试文件，`+140/-1`，无产品代码。
- 最终 RED：
  - `uv run pytest tests/unit/test_context_state.py tests/integration/test_cli_handoff.py tests/integration/test_cli_recover.py -q`
  - 结果：`4 failed, 34 passed in 1.44s`。
  - 四个失败分别证明 linked build 仍读取历史 docs、完整 overlay 下历史 branch 未自愈、handoff pack 历史路径泄漏、recover legacy-fresh pack 未进入 semantic-stale rebuild；均非 fixture/解析错误。
- 兼容 GREEN 已覆盖：corrupt working-set/runtime、invalid UTF-8 latest-summary、patched `OSError` 仍返回正确 fresh pack；无 linked 非标准 `feature.spec_dir`、linked runtime branch、linked missing/partial 和既有 31 项相关回归均通过。
- 跨平台断言使用解析后的 `Path` 三元组精确比较 spec/plan/tasks；不搜索 raw YAML 分隔符。
- `uv run ruff check` 三文件：PASS；`git diff --check`：PASS；Cursor adapter 测试副作用已用 `apply_patch` 精确恢复。
- 独立 RED reviewer 首轮/二轮 findings 全部修订；最终 verdict：`PASS / Spec compliant: Yes / RED quality: Approved / 未发现测试内容的可操作问题`。

## 6. Batch 2026-07-13-003：T22～T31 GREEN 与 fresh verification

- fixture 校正 commit：`bb4e3366`；旧版 fresh pack fixture 显式写入历史 docs/branch，防止产品修复后 fixture 自愈，测试总预算仍为 `+140/-1`。
- 最小 GREEN commit：`6a46fc65`；产品仅修改 `src/ai_sdlc/context/state.py`，`+19/-3`、净新增 16 LOC，未新增文件、公共抽象、依赖、配置或 schema。
- 实现结果：filesystem fallback 在 linked WI 下使用 `specs/<linked>`，无 linked 保留 `feature.spec_dir`；linked 无 runtime branch 返回空值；fresh legacy pack 比较 docs/branch 后复用同一 expected pack 进入既有 stale rebuild；semantic-only expected build 对 `YamlStoreError`、`UnicodeError`、`OSError` 保持旧成功合同。
- 三个 RED 文件：`38 passed`；五个 focused 文件：`94 passed`。
- 独立 GREEN reviewer verdict：`PASS / Spec compliant: Yes / Code quality: Approved / 未发现可操作问题`。
- fresh 完整验证：
  - `uv run pytest -q`：`3156 passed, 3 skipped in 427.01s`；
  - `uv run ruff check src tests`：PASS；
  - `uv run ai-sdlc verify constraints`：PASS；
  - `git diff --check`：PASS。
- 预算复核：产品 `+19/-3`（净 +16，≤20）；三个获准测试文件合计 `+140/-1`（新增 140，≤140）；其余产品/测试文件无 diff。
- CC-03/04/06/07 after artifact 的 approved delta 仅为三件套从 `specs/197-adapter-preflight-order/` 切到 `specs/198-linked-wi-resume/`，以及 linked WI 无 runtime branch 时从历史 feature branch 切为空；`timestamp` 由完整测试的 rebuild 更新，显式 context summary 由最终 handoff 刷新，二者不纳入语义漂移。
- 完整测试按预期刷新 root resume pack，并改写非本工作项的 Cursor adapter；adapter 已用 `apply_patch` 精确恢复，resume pack 由最终 continuity handoff 补齐 summary 后作为 after evidence 保存。
