---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：Lean Gate Report-Only 基线

**编号**：`202-lean-gate-report-only`
**基线**：`d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`
**规格**：`specs/202-lean-gate-report-only/spec.md`
**阶段边界**：WP-01A/T61A + WP-02/T62A；不进入 T62B/T62C。

## 1. 实施结论

采用独立兄弟命令 `verify lean-report`，不向 `ConstraintReport`、`verify constraints`、governance bundle 或 telemetry 注入字段。核心使用一个私有、纯读取模块，CLI 只解析参数和渲染。这样可将 report-only 与现有阻断语义、digest 和副作用完全隔离。

## 2. 影响边界

```text
src/ai_sdlc/core/lean_gate_report.py         # 唯一新产品文件；commit blob diff + report
src/ai_sdlc/cli/verify_cmd.py                # 薄命令适配
tests/integration/test_cli_verify_lean_report.py
tests/integration/test_cli_verify_constraints.py  # 仅必要的 characterization 断言
tests/unit/test_command_names.py             # 新命令 discovery
specs/202-lean-gate-report-only/*             # formal、expected delta、证据日志
```

禁止修改：`verify_constraints.py`、telemetry、gate、state machine、reviewer、runner、project config model、workflow、provider 和 frontend runtime。

## 3. 设计

### 3.1 核心报告

`build_lean_gate_report(root, base_ref, candidate_ref, wi_path) -> dict[str, object]` 是模块内唯一由 CLI 调用的入口。模块不引入 DTO/Enum/registry；只使用现有运行时依赖和私有 helper。

处理顺序：

1. 校验 WI 为 repo-relative 路径并归一化 `\\`。
2. 解析 base/candidate；失败时创建 source-unavailable finding，但保持合法调用 exit 0。
3. 使用 `git diff --name-status -z --find-renames` 读取精确变更，不使用换行拆分。
4. 读取 commit blob bytes 和 mode；binary、非 UTF-8、symlink、submodule 转为 unknown。
5. 按冻结优先级分类；仅对 Python 产品/测试文本计算物理行和 AST 函数跨度。
6. 读取 candidate WI frontmatter与父规格 §6.3，独立生成 contract evidence。
7. 对所有 mapping/list 使用固定 key 和排序，返回 `lean-gate-report/v1`。

所有 Git 子进程都有 timeout、`check=False`、bytes 输出和确定错误摘要；不得 fetch 或回退工作树。

### 3.2 CLI

`verify_cmd.py` 增加约 20～35 行：三个必填 option、`--json`、一次 core 调用和中性 plain renderer。命令显式 `raise typer.Exit(0)`；非法 WI path 使用 `typer.BadParameter`。不复用 Rich warning/error 样式。

### 3.3 合同来源

当前 WI 使用 `spec.md` 的 `lean_contract/v1` frontmatter。适用矩阵从 `contract_source` 指向的父规格表读取；产品代码不得硬编码 WP-02 的第二份集合。`expected-delta.json` 是唯一允许变化清单，不是 runtime 配置。

### 3.4 兼容基线

复用现有 `test_cli_verify_constraints.py` 场景冻结 plain/JSON/exit、telemetry 和 adapter 不变；只增加证明新命令未接入这些路径的最少断言。不创建通用 Golden executor。动态 root/时间/ID/digest 派生值只通过当前测试 helper 的明确 normalizer 比较。

## 4. TDD 阶段

### Phase 0：formal admission

- 重写四件套和 expected delta。
- 记录 clean-clone T61A receipt、具体预算赞助候选和 350 LOC 上限。
- 对 `spec.md + plan.md + tasks.md + expected-delta.json` 计算内容 hash。
- 兼容安全与精简效率两个原 agent 独立复核；任一非 PASS 均修订并对新 hash 重跑双方，直到同哈希双 PASS。

### Phase 1：RED

先提交失败测试，覆盖：命令 discovery/help；新/历史/changed 400/50；分类优先级；rename/binary/symlink/Unicode/CRLF；合同缺口与 waiver 无效；两个规则族独立 unavailable；finding exit 0；确定性和零写入；原 constraints 无差异。

RED 证据必须证明失败原因是命令/模块尚不存在，而不是 fixture 或环境错误。

### Phase 2：最小 GREEN

- 先实现纯 report builder，再接薄 CLI。
- 不增加 mode、config、warning、blocking、artifact writer 或泛化扩展点。
- 每批运行 LOC 预算脚本；预测超过 350 时停止并删除非必要测试/helper，不能扩大分母。

### Phase 3：候选提交验收

绑定精确 candidate commit，执行 targeted、全量、Ruff、mypy（若仓库现有命令适用）、constraints、truth audit、diff check、LOC budget、零写入 clone smoke 和 Windows/macOS/Linux CI。

### Phase 4：PR 与 mainline

按仓库协议 push/open PR、请求 `@codex review`、约五分钟 heartbeat。所有 actionable feedback 在同分支最小修复并重跑。Codex 无重大问题且 required checks 全绿后合并；mainline exact tree 重放 targeted、constraints、truth audit 和 lean report。

## 5. 精确验证命令

```text
uv run pytest tests/integration/test_cli_verify_lean_report.py tests/integration/test_cli_verify_constraints.py tests/unit/test_command_names.py -q
uv run pytest
uv run ruff check src tests
uv run mypy src/ai_sdlc/core/lean_gate_report.py src/ai_sdlc/cli/verify_cmd.py
uv run ai-sdlc verify constraints
uv run ai-sdlc program truth audit
uv run ai-sdlc verify lean-report --base-ref d19c8b7df66ca43e4fa55a99a6d05fa2d1219586 --candidate-ref <candidate-sha> --wi specs/202-lean-gate-report-only --json
git diff --check
```

LOC 预算以 base/candidate 的 `git diff --numstat` 统计 `src/ai_sdlc/core/lean_gate_report.py`、`src/ai_sdlc/cli/verify_cmd.py`、两个 verify integration tests 和 command-name test 的新增行；合计必须 `≤350`，产品 `≤210`，test/harness/normalizer `≤140`。

## 6. Expected delta 与不变量

唯一批准变化：

- `verify --help` 和 command discovery 新增 `lean-report`；
- 显式执行新命令时新增 neutral plain/JSON report；
- candidate 自身 formal/测试/产品文件。

以下必须零变化：原 `verify constraints` 的参数/help/输出/JSON/exit、telemetry digest 语义和写集；任何 gate/reviewer/execute 状态；项目配置和 checkpoint；普通用户默认流程；前端确认边界。

## 7. 进入、完成、停止、回退

### 进入

- T51/T52/GAP-09～GAP-11 已关闭并有 mainline 证据。
- T61A clean-clone 基线完成。
- 预算赞助候选和 350 LOC 上限由两个 agent 在同一 formal hash 上通过。

### 完成

- spec 的十项 FR、八个场景、六项 SC 全部有 fresh evidence。
- target/full/lint/type/constraints/truth/zero-write/cross-platform checks 全绿。
- exact candidate report 和 rollback drill 成功。
- PR 经 Codex review、required checks 全绿、合并，并在 mainline 重放。

### 停止

严格采用 spec §9 的停止条件。尤其是：触碰现有 gate/telemetry/state/config、出现非零 finding exit、需要超过 350 LOC 或需新增公共框架时立即 No-Go。

### 回退

合并前删除新模块和薄 CLI；合并后 `git revert <merge-sha>`。回退树必须恢复 command discovery 只含 `constraints`，并重放原 constraints characterization、全量测试和 truth audit。

## 8. Formal hash 协议

在 worktree 根执行，目标顺序不依赖 shell glob：

```text
for p in specs/202-lean-gate-report-only/spec.md specs/202-lean-gate-report-only/plan.md specs/202-lean-gate-report-only/tasks.md specs/202-lean-gate-report-only/expected-delta.json; do printf '%s  %s\n' "$(shasum -a 256 "$p" | cut -d' ' -f1)" "$p"; done | LC_ALL=C sort | shasum -a 256
```

四个目标文件任一字节变化即使旧 verdict 失效；两个 agent 必须分别复算并审阅同一新 hash。
