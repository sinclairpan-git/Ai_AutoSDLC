# 任务执行日志：Adapter Mutation 与 Workitem Preflight 顺序修复

**功能编号**：`197-adapter-preflight-order`
**创建日期**：2026-07-13
**状态**：runtime implemented and task reviews approved；PR pending

## 1. 固定合同

- 父项：WI-196 `GAP-07 / T51`。
- 基线：`origin/main@4dd0f1c9cdcc26a359dd0d724f365a3168d66fe8`。
- 分支/worktree：`feature/197-adapter-preflight-order-docs` / `.worktrees/197-adapter-preflight-order`。
- 实现前置：`spec.md + plan.md + tasks.md` 同哈希双 Agent PASS。
- 允许产品文件：`src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/workitem_cmd.py`。
- 允许测试文件：`tests/integration/test_cli_workitem_init.py`、`tests/unit/test_cli_hooks.py`。
- 回退 owner：framework maintainer；实现提交必须可独立 revert。

## 2. Batch 2026-07-13-001：现状审计与未改代码基线

### 2.1 仓库状态

- 根 `main` 有用户 continuity 与文档改动，未切换、未清理、未修改。
- 新 worktree 从 `origin/main` 创建；初始 HEAD 为 `4dd0f1c9`。
- `.worktrees/` 由 `.gitignore` 明确忽略。
- 仓库首选 PowerShell，但本机此前已确认 PowerShell runtime 不可用；本批沿用已诊断的 zsh fallback。

### 2.2 事实审计

- `src/ai_sdlc/cli/main.py:94-97` 在非 bypass 顶层命令前运行 adapter。
- `src/ai_sdlc/cli/workitem_cmd.py:75-118,163-169` 在子命令内部后运行 clean-tree preflight。
- `tests/integration/test_cli_workitem_init.py:34-37` 对整个文件 patch 根 hook，真实冲突未覆盖。
- GAP-10 proof carrier、校验与 blocker 已存在；本项不修改它们。

### 2.3 基线验证

- `uv run pytest tests/unit/test_cli_hooks.py tests/unit/test_workitem_scaffold.py -q`
  - 结果：`9 passed in 0.89s`。
- `uv run pytest -q`
  - 结果：`3145 passed, 3 skipped in 408.98s`。
  - 观察：测试更新了隔离 worktree 内的 `resume-pack.yaml` 与受管 Cursor rule；两处均已用补丁恢复到 HEAD，未带入用户工作或 WI-197 变更。
- `workitem init` 首次尝试被上述测试副作用触发的 clean-tree gate 正确阻断；恢复后通过 patched canonical CLI 成功生成 WI-197。

### 2.4 兼容安全独立审计

- reviewer 结论：WI-196 原子路线 `PASS`，当前没有必然 L4。
- T51 特别约束：保持自动 adapter；execute 前落 GAP-10 impact analysis；不得用关闭 hook 或放宽 proof 解决。
- disposition：全部纳入本项 spec/plan/tasks。

## 3. 下一步

### 3.1 第一轮同哈希评审

- review target hash：`ec47124aeb0bf79ac2b62370a010cca7f262762dba0588a565f264b0d537a928`。
- 兼容安全 Agent：`FAIL`；根 callback 无法可靠识别二级 `init`，GAP-10 proof 持久化时序和参数解析失败路径未冻结。
- 精简效率 Agent：`FAIL`；缺少非 `init` workitem 子命令的可执行回归，错误跳过整个组也可能通过。
- disposition：findings 全部成立。改为 root → workitem group callback 委托；冻结 clean/dirty、缺失参数、非 `init` 与 proof 重试场景。
- 三目标文件已变化，第一轮两个 verdict 全部失效。

### 3.2 下一门禁

第二轮 review target hash：`37db361715fd8de7accdd80084c0a50a351dfcda09908c25467757711e0ba6b6`。

- 兼容安全 Agent：独立复算一致，未发现可操作问题，`VERDICT: PASS`。
- 精简效率 Agent：独立复算一致，未发现可操作问题，`VERDICT: PASS`。
- 结论：T12 admission 通过，三目标文件冻结；后续目标变化会让双方 PASS 同时失效。

下一步：提交 docs batch，切 dev branch，按 T21 开始 RED。

## 4. Batch 2026-07-13-002：设计准入与 truth 基线

### 4.1 双 Agent 设计准入

- 同一 review target hash：`37db361715fd8de7accdd80084c0a50a351dfcda09908c25467757711e0ba6b6`。
- 兼容安全 Agent：独立复算一致，`PASS`，无可操作问题。
- 精简效率 Agent：独立复算一致，`PASS`，无可操作问题。
- 结论：`spec.md`、`plan.md`、`tasks.md` 冻结，允许进入实现。

### 4.2 Program Truth 同步

- snapshot state：`migration_pending`。
- snapshot hash：`65d36f71a1bc2818c20ad8982f5181f689723230ed00c23d93b6f48ff5e16918`。
- frontend blockers：`frontend_inheritance:generation`、`frontend_inheritance:quality`。
- adapter blocker：`adapter_canonical_consumption:unverified`。
- source inventory：`total=1046`、`mapped=1013`、`unmapped=33`、`missing=11`。
- 相对 WI-196 已登记基线，新增 5 个 WI-197 文档使 total/mapped 同增 5；unmapped/missing 债务集合未扩大。

### 4.3 Continuity 临时对齐

- `workitem link` 已把 `linked_wi_id` 和 `linked_plan_uri` 指向 WI-197，但 checkpoint `feature` 仍停留在 WI-196；这与父项 GAP-08 的已知缺口一致。
- 在 GAP-08 尚未修复前，本项用显式补丁把 checkpoint `feature` 对齐到 WI-197 与当前 docs branch；没有修改运行时代码或放宽门禁。
- 后续以 `uv run ai-sdlc handoff update` 生成 canonical/scoped handoff 与 resume pack，并在执行日志中保留该 workaround。
- 当前批次 branch disposition 状态：PR merge carrier。

### 4.4 提交卫生与同哈希复核

- `git diff --cached --check` 发现冻结设计文件含 5 处 Markdown 行尾空格；未绕过门禁，仅移除行尾空格。
- 格式修复后的 review target hash：`0c97361ef27901ef3d207cc1c21980e2cc9cb64c633d4c03caa1e43db74a9236`。
- 兼容安全 Agent：独立复算一致，`PASS`，无可操作问题。
- 精简效率 Agent：独立复算一致，`PASS`，无可操作问题。
- 结论：格式修复未改变设计语义；以新哈希重新冻结三目标文件并进入提交门禁。

## 5. Batch 2026-07-13-003：RED/GREEN 实现证据与任务评审

### 5.1 RED characterization

- RED commit：`b89203c4`（`test(workitem): characterize adapter preflight order`）。
- focused 命令：`uv run pytest tests/integration/test_cli_workitem_init.py -k "adapter_before_clean_tree_preflight or missing_title or non_init" -q`。
- focused 结果：预期 RED，`3 failed, 1 passed, 13 deselected`：
  - clean 合法 `init` 被 adapter 自身的 Git-visible 写入变成 self-dirty；
  - 用户脏树在 clean-tree preflight 拒绝前已先执行 adapter 写入；
  - 缺失 `--title` 在 Typer 返回 exit 2 前已先执行 adapter 写入；
  - 合法非 `init` 的 `workitem plan-check` 通过，证明没有误跳过整个 workitem group。
- 既有非 RED 命令：`uv run pytest tests/integration/test_cli_workitem_init.py -k "not adapter_before_clean_tree_preflight and not missing_title and not non_init" -q`；结果 `13 passed, 4 deselected`。
- 独立 RED task reviewer：`Spec compliant + Task quality: Approved`，无可操作问题。

### 5.2 首版 GREEN 诊断与对抗裁决

- 首版 direct child import 使 focused 用例转绿，但 full suite 为 `13 failed, 3136 passed, 3 skipped`；独立 `test_cli_workitem_close_check.py` 为 `13 failed, 25 passed`。
- 根因：child-bound hook 绕过既有 root composition/patch seam，真实 adapter 输出污染 JSON，并生成 Git-visible tree 写入。
- 兼容安全与精简效率两个对抗 Agent 对 strict Click `ctx.meta` 修订方案统一 `PASS`：使用唯一 private dotted key；root 注入调用当下的 hook 后立即 return；child 只做 strict key index；不增加 fallback、不把写操作冒充 read-only，并删除失效 child patch。

### 5.3 最小 GREEN 与独立复核

- GREEN commit：`c644884e`（`fix(workitem): defer adapter until clean preflight`）。
- 实现 Agent 验证：focused `4 passed, 13 deselected`；init/hooks 两文件 `20 passed`；close-check `38 passed`；full suite `3149 passed, 3 skipped`；`ruff check src tests`、`verify constraints`、`git diff --check` 均 PASS。
- 主 Agent 独立复核：focused 4、init/hooks 两文件 20、close-check 38、focused ruff 均 PASS。
- 独立 GREEN task reviewer：`Spec compliant + Task quality: Approved`，无 Critical、Important 或 Minor 问题。

### 5.4 预算、范围、非影响与回退

- 产品代码 numstat 为 `main.py 5 additions / 1 deletion`、`workitem_cmd.py 17 additions / 0 deletions`，即 `22 insertions - 1 deletion = net +21 LOC`；WI-197 测试累计 72 additions / 0 deletions。
- 新增产品文件、公共抽象、依赖、配置均为 0；最终 runtime diff 仅 `src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/workitem_cmd.py`、`tests/integration/test_cli_workitem_init.py` 三个授权文件。
- GAP-10 proof carrier/schema/校验/blocker 未修改；其他顶层命令继续沿用既有 root hook 路径。
- 既有 preflight 将 `GitError` 包装为 `WorkitemScaffoldError`，既有 CLI handler 再将 `WorkitemScaffoldError` 映射为 exit 1；adapter 非 special-case 异常与 strict-meta composition 异常继续传播；本变更未新增异常吞没或映射。
- rollback：revert `c644884e`；如需继续保留缺陷 characterization，可保留 RED 测试提交 `b89203c4`。

### 5.5 Branch disposition 与未完成项

- 当前 `feature/197-adapter-preflight-order` 是 PR merge carrier。
- 当前仅能确认 runtime implemented 且 RED/GREEN task reviews approved。
- final whole-branch review 已发现两项 Minor evidence-precision findings，本批已修正文档；final re-review、PR、Codex review/required checks、merge、main program truth 同步与 GAP-07 close 均尚未完成；不得提前声明 mainline 已交付。

### 5.6 Continuity、program truth 与交付准备验证

- `uv run ai-sdlc handoff update` 已把 canonical/scoped handoff 对齐到两个逻辑提交、task reviews approved 与 PR pending；next step 固定为 final verification、whole-branch review 与 PR。
- patched canonical `program truth sync --execute --yes` 成功；snapshot state 保持 `migration_pending`。
- source inventory 保持 `1013/1046 mapped`、`33 unmapped`、`11 missing`；既有 blocker 仍且仅为 `frontend_inheritance:generation`、`frontend_inheritance:quality`、`adapter_canonical_consumption:unverified`。
- patched `program truth audit`：snapshot `fresh`；仅因上述已登记 migration/blockers 返回预期 exit 1。
- fresh focused verification：`uv run pytest tests/integration/test_cli_workitem_init.py tests/unit/test_cli_hooks.py tests/integration/test_cli_workitem_close_check.py -q` → `58 passed`。
- `uv run ruff check src tests` → `All checks passed!`；`uv run ai-sdlc verify constraints` → `no BLOCKERs`；`git diff --check` → PASS。
- 验证未生成额外 tracked/untracked 文件；continuity 文件在 focused tests 前后 hash 不变。
- 环境 concern：本机 `pwsh` 在仓库命令执行前因 `System.Text.RegularExpressions, Version=10.0.0.0` assembly `FileLoadException` 退出，因此沿用已记录的 zsh fallback；项目命令结果不受影响。

## 6. PR Codex review remediation

### 6.1 Finding 与根因

- PR `#121` 的 Codex inline comment `3572707130` 指出：重复执行已存在 canonical docs 的 `workitem init` 时，CLI 在 `scaffold()` 拒绝前先运行 adapter，使 exit 1 路径仍可写 proof。
- 根因确认：`workitem_init` 的顺序为 `preview_work_item_id` → Git preflight → adapter → `scaffold`，而 duplicate validation 只存在于 `scaffold` 内。
- 旧 HEAD 的 final review 与验证结论因此失效，WI-197 重新进入设计门禁与 RED→GREEN。

### 6.2 对抗方案评审与重新冻结

- 兼容安全 Agent 与精简效率 Agent 均拒绝在 CLI 复制 canonical 文件清单；两者一致选择把既有 duplicate validation 前移到 `WorkitemScaffolder.preview_work_item_id`，并以 module-private canonical 名称清单供 preview/scaffold 复用。
- 该方案不新增公共抽象、依赖或产品文件，预计 `workitem_scaffold.py` 净减少约 3 LOC，使全部产品净增从 21 降至约 18；唯一必要边界扩展是允许修改第三个既有产品文件。
- 第一版修订哈希 `6f194ae700229aad207e4956584df18ad55b71b142e83f7b06e1462edca5c506` 被精简 Agent 判定 FAIL：测试文件“运行范围”与“修改范围”文字歧义。
- 消除歧义后，冻结 `spec.md + plan.md + tasks.md` bytes 拼接 SHA-256 为 `7627839c93ba3c227790a9df57b288baaef32a5368790e7d3746c2c2ad356633`；兼容安全与精简效率 Agent 均独立复算并给出 PASS，无可操作 finding。
- 最终边界只允许修改 3 个既有产品文件和 `tests/integration/test_cli_workitem_init.py`；两个 unit 文件只回归运行。第五个产品或测试修改文件触发 stop gate。

### 6.3 remediation RED/GREEN 与独立 task reviews

- RED commit `4c7b35a3` 只增强既有 duplicate integration test：首次 init 后删除 proof 并清空调用记录，第二次同 ID 调用要求 adapter 零次且 proof 不重建。
- 当前生产代码下精确测试稳定 RED：`1 failed`，失败点为期望 `calls == []`、实际 `['adapter']`；首次 init 与 fixture 正常，失败原因精确指向第二次 adapter 副作用。
- RED task reviewer 独立复跑后给出 `Spec compliant: Yes / Task quality: Approved`；累计测试 numstat 为 `+80/-5`，gross additions 恰好满足 80 行上限。
- GREEN commit `3940723e` 只修改 `workitem_scaffold.py`：增加 module-private `_CANONICAL_DOC_NAMES`，scaffold 由该清单生成 paths，preview 在返回 id 前使用同一清单拒绝重复目标；原错误文本保持。
- GREEN 精确测试 `1 passed`；三个 focused 文件 `26 passed`；core ruff 与 diff-check PASS。
- GREEN task reviewer 独立复跑并给出 `Spec compliant: Yes / Task quality: Approved`，无 Critical、Important 或 Minor finding。
- 最终产品 numstat 为 `main.py +5/-1`、`workitem_cmd.py +17/-0`、`workitem_scaffold.py +10/-12`，合计 `+32/-13 = net +19`；无新产品文件、公共抽象、依赖、配置或相邻重构。

### 6.4 remediation fresh full verification

- `uv run pytest -q` → `3149 passed, 3 skipped in 383.10s`。
- `uv run ruff check src tests` → `All checks passed!`。
- `uv run ai-sdlc verify constraints` → `no BLOCKERs`；`git diff --check` → PASS。
- `uv run ai-sdlc program truth audit`：snapshot `fresh`；source inventory 仍为 `1013/1046 mapped`、`33 unmapped`、`11 missing`；blocker 仍且仅为 `frontend_inheritance:generation`、`frontend_inheritance:quality`、`adapter_canonical_consumption:unverified`，因此返回预期 exit 1。
- full suite 与 truth audit 均触发现有 Cursor adapter 安装副作用；`.cursor/rules/ai-sdlc.mdc` 已用 `apply_patch` 恢复到测试前 SHA-256 `d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`，无测试副作用进入提交。
