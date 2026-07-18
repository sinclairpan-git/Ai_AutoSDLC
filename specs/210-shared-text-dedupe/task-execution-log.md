# 任务执行日志：共享文本去重重复族减重

**功能编号**：`210-shared-text-dedupe`
**创建日期**：2026-07-18
**当前状态**：Batch 0 formal 编制；产品实现未授权

## Batch 2026-07-18-001：下一原子候选选择

### 基线与扫描

- exact current main：`4b4348646a11cf2e27e488ddad892977958476a9`；worktree clean。
- `program_cmd.py`=`7065` 行，`program_service.py`=`17474` 行；WI-204 candidate 未实现。
- WI-204 的可信保护最低估算为 Pascal 222 / Confucius 356，均超过 hard cap 180；claim=0、revoked，
  不可复活。
- AST exact-body inventory 找到 28 defs / 27 modules / 196 LOC / 730 direct calls；唯一 body digest=
  `08aa3c8fe861c4d69e2fcfcdbc6bc212b7b6d0c52ef6e2e4b382327dd48d962a`。
- repo scan 未找到跨模块 private import consumer；`p1_artifacts` 只有私有 annotation 较窄，运行 body 相同。

### 候选对抗选择

- Pascal 从精简收益侧推荐该 T63，预测产品净删至少 156 行；拒绝当前 T65/WP-06/WP-07。
- Confucius 从兼容安全侧同意该 T63，要求 private aliases、730 calls 零改、clean subprocess import、
  事件/异常 differential 与严格停止条件。
- 两者起初对承载位置有分歧：Pascal 主张复用 `utils/helpers.py`，Confucius 误以为该依赖层不存在而
  倾向新 package-root leaf。
- 主线程回传当前真值：`utils/helpers.py` 已存在、96 raw / 68 non-empty LOC、stdlib-only，repo-wide
  有 55 个 importer（CLI/Core/Generators 中 42 个），10 个目标模块已依赖；Confucius 撤回错误前提。
  双方收敛为复用现有 text helper section，不新增模块。

### 受影响测试基线

- Confucius 独立执行 23 个受影响 unit files：`441 passed in 31.94s`。
- Confucius 独立执行 8 个代表性 CLI integration files：`398 passed in 60.84s`。
- exact main 的最近 fresh acceptance full：`3275 passed, 3 skipped`。
- 初始 839 项受影响集合用于 implementation candidate/revert/restored 对比；隔离 spike 随后扩展为
  Batch 003 记录的 32-file / 1282-test 集合。两者是递进验证，不是互相冲突的验收口径，也不会复制
  WI-204 大型 harness。

### 决策

- WI-210 选择 exact text-dedupe family，风险 L1，父责任 T63/WP-03/GAP-05。
- formal 与 implementation 必须独立 branch/PR；当前只允许 docs/truth/continuity。
- 预算 spike 仅校准 import/Ruff 实际成本，不构成实现授权或 PASS。

## Batch 2026-07-18-002：Canonical formal 编制

### 已完成

- 通过 `uv run ai-sdlc workitem init` 创建 canonical 四件套与 manifest mapping。
- CLI 自举误刷 `.cursor/rules/ai-sdlc.mdc`，已精确恢复为 HEAD；该文件不属于 formal diff。
- placeholder direct-formal 内容已替换为本项唯一 spec/plan/tasks，不修改产品或测试。
- 分支按框架 canonical 约定使用 `feature/210-shared-text-dedupe-docs`。

### 待完成

1. 运行 formal 门禁并冻结 exact identity；
2. Pascal/Confucius 对同一 identity 评审至双 PASS；
3. 为冻结可复算 identity，允许仅在本地形成 formal commit；双 PASS 前不得 push/创建 PR，也不得进入
   产品实现。

### Branch/worktree disposition

- branch：`merge-pending`（仅表示本地 formal 中间态，不声称 PR 已创建）。
- worktree：`retained(formal review and delivery pending)`。

## Batch 2026-07-18-003：隔离实现预算 Spike

- 隔离 worktree：`.worktrees/210-shared-text-dedupe-spike`；exact HEAD=`4b434864...`；未 commit/push。
- 只修改冻结的 28 个产品文件：`utils/helpers.py` 新增唯一实现，27 个目标模块以 import alias 保留
  28 个局部私有名；tests/docs/specs/.ai-sdlc 零 diff。
- 实测产品 raw=`+39/-252/net -213`；non-empty=`+35/-196/net -161`。non-empty additions 精确为
  28 个 alias import + 7 行 helper；空行删除只出现在 raw 账，不计 RC-04/RC-06 收益。
- 730 call expressions 的逐模块 AST 与 hash 完全不变；27 cold imports PASS；28 alias 均与 shared
  object identity 相同，无 cycle/import failure。
- Ruff lint PASS；format-check 的 inherited debt 为 exact baseline/candidate 同一 24-file 集合，
  `24→24`，不得写成 formatter PASS，也不得为本项顺带格式化 730 calls。
- 32 个代表性测试文件：`1282 passed in 165.56s`；`git diff --check` PASS。
- 批准私有 introspection 差异已实测：28 objects→1；`__module__` 统一到 `ai_sdlc.utils.helpers`；
  `__name__/__qualname__` 统一为 `_dedupe_text_items`；`p1_artifacts` annotation 变为 `object`。
- Formal 预算据此拆成 raw/non-empty 双账：产品 hard=`+39/-252` 与 `+35/-196`；RC-06 采用
  non-empty，product35+test≤9+truth≤2 计划≤46、hard cap=49。
