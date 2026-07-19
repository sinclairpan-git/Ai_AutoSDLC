# 实施计划：AI-SDLC 精益减重候选选择

**编号**：`212-reduction-candidate-selection`  
**日期**：2026-07-19  
**规格**：`specs/212-reduction-candidate-selection/spec.md`  
**交付类型**：docs-only formal；不进入 execute

## 1. 目标与策略

本计划用一次 fresh-main 只读扫描选择下一原子减重项，并修正 L3 路线的发布/删除死锁。选择依据按以下顺序 fail-closed：

1. 是否有真实可删除职责，而不是纯移动或第二真值。
2. 是否能在 RC-05/RC-06/RC-07 内完成实现和保护。
3. 是否直接推进 RC-08 的 10,588 行缺口或两个超大文件。
4. 是否能限定为一个领域、一个回退单元和一个独立 work item。
5. 是否不依赖 revoked sponsor、旧 claim 或过期 candidate hash。

最终选择 T66 bounded-stage ProgramService domain。WI212 只冻结选择和预备预算，产品实现必须进入下一独立 formal/dev 生命周期。

## 2. 技术背景

- **运行时**：Python 3.11.15；`uv`；仓库 source CLI。
- **输入**：main `32742a25...`、WI-196 LP/CC/RC、当前 AST/LOC、调用者、历史 WI-203/WI-204 receipts。
- **输出**：WI212 formal 四件套、父路线窄修、program/project truth、root/scoped handoff。
- **测试**：只读 AST/LOC recipe、constraints、program validate/truth、manifest exact、路径白名单。
- **硬约束**：本分支 `src/workflows/providers/runtime rules` 零 diff；test 仅允许父 FR-12 的 manifest
  inventory/close 两值 `+2/-2` 等量替换；不发布；不创建 product claim。

## 3. 宪章与父合同检查

| 门禁 | 响应 |
|---|---|
| MUST-1 范围严控 | 只做候选选择和阻断 L3 的合同矛盾；不实现候选 |
| MUST-2 可验证 | 每个数值绑定 revision、symbol 和可执行 recipe |
| MUST-3 范围/验证/回退 | docs-only 独立 commit/PR；revert 不影响运行时 |
| MUST-4 状态外化 | WI212 execution log、manifest 与双 handoff 同步 |
| MUST-5 产品隔离 | 产品、测试、runtime rule 和 workflow 零差异 |
| LP-01/10 | 不以 LOC 替代兼容；Conditional Go 有净删和停止阈值 |
| LP-02/03 | 只服务九个当前 stage；不造 future extension point |
| LP-05/12 | ProgramService 保留 thin facade；下一 WI 完成 candidate+stability+deletion 后才关闭 |
| RC-09 | 预算、保护或语义任一不可达即停止，不继续“结构准备” |

## 4. 变更范围

### 4.1 允许修改

```text
specs/212-reduction-candidate-selection/
specs/196-ai-sdlc-lean-code-self-reduction-governance/{spec.md,plan.md,tasks.md,task-execution-log.md,development-summary.md}
program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
.ai-sdlc/state/codex-handoff.md
.ai-sdlc/work-items/212-reduction-candidate-selection/codex-handoff.md
tests/integration/test_repo_program_manifest.py（仅 inventory/close 两个精确值等量替换）
```

truth sync 的机械派生字段允许变化。`development-summary.md` 只在 WI212 完成选择、双审和交付验收后创建。

### 4.2 禁止修改

```text
src/**
tests/**（上述单文件两值替换除外）
.github/workflows/**
.ai-sdlc/providers/**
.ai-sdlc/rules/**
AGENTS.md
pyproject.toml
uv.lock
发布/tag/全局 CLI
```

CLI 初始化产生的无关 IDE adapter refresh 不纳入本 PR，必须恢复到 main 字节。

## 5. 阶段计划

### Phase 0：fresh-main 身份与路线缺口冻结

1. 固定 main commit/tree、Python、产品 LOC 和两个超大文件 LOC。
2. 验证 WI211/PR #155 已合并且 reviewed tree 等于 merge tree。
3. 确认 GAP-05/06/03/04、WI-196、RC-08、release 仍 open。
4. 排除 T62A 和所有 revoked claim。

**退出条件**：truth `ready/fresh`、1111/1111、missing/unmapped=0/0；工作树从 fresh main 创建。

### Phase 1：候选扫描与排序

1. 用 AST exact-body 扫描 T63，单列定义数、物理 LOC 和重复副本 LOC。
2. 对 T64 复核既有 39-LOC No-Go，没有基线变化则不重开。
3. 对 T65 六 builder 统计定义、LOC、真实消费者和第二真值；无第二真值直接预测 No-Go，不写 loader。
4. 对 T67 比较 current 九 handler 与 WI-203 baseline；旧 claim/receipt 只作历史证据。
5. 对 T66 统计九 stage 的 request/execute/write/payload build/load 45 个方法、调用者与测试库存。
6. 用净删除、保护余量、风险、RC-08 贡献排序，只保留一个 Conditional Go。

**退出条件**：矩阵无未处置项；任何数字均可复算；没有把 wrappers/签名误算为可删除实现。

### Phase 2：L3 合同死锁修正

1. 将 WP-06/WP-07 的“稳定发布”明确为主线预发布稳定周期。
2. 保留 candidate merge 后 legacy 共存、独立 deletion PR 和真实 rollback receipt。
3. 明确该周期不创建 tag/Release/PyPI/全局 CLI，RC-08 发布禁令不变。
4. 把父 RC-06 的文字范围同步为“适用矩阵声明 RC-06 的全部候选”，不改变 25%/1,500/fixture 上限。
5. 同步父 spec、plan、tasks、execution log 和 development summary，禁止只改一个表面。

**退出条件**：L3 可在不公开发布版本的前提下完成稳定期和删旧，且不能绕过跨平台/安装包/离线/兄弟项目验证。

### Phase 3：双 Agent 对抗评审

1. 按父 plan §9 唯一算法计算 child/parent `spec.md + plan.md + tasks.md` 六文件逐一 SHA-256 与 canonical combined identity。
2. Pascal 从 LEAN/YAGNI、收益、直接性和避免过度实现维度独立审查。
3. Confucius 从安全、兼容、证据、回退、发布边界维度独立审查。
4. 任一 finding 经仓库证据确认后做最小修正；formal 变化使双方结论全部失效。
5. 重复直到相同 identity 上两方均 `PASS`、findings=0。

### Phase 4：truth、PR 与 fresh-main 交付

1. 更新 root/scoped handoff，保持 byte-identical。
2. 完成 WI212 tasks、execution log 和 development summary，并把 manifest exact test 机械更新为
   terminal inventory/close；pre-close `missing=1` 不得伪装为终态 PASS。
3. 执行一次 program truth sync，提交唯一 clean identity。
4. 跑 constraints、validate、truth、manifest exact、diff/path/parity 门禁。
5. 双 review current identity 后 push/PR、`@codex review`、required checks heartbeat。
6. Codex current-head clean 且全部 required checks 成功后 merge。
7. detached fresh-main 验收 tree、truth、manifest、scope 和 clean state。

**完成后唯一动作**：创建新的 T66 bounded-stage formal WI；仍不得在 WI212 分支实现产品代码或发布版本。

## 6. 下一 T66 formal 的强制执行顺序

WI212 不执行下列步骤，只冻结其顺序以防下一 WI 漂移：

1. current-main 复算 45-symbol baseline、165-test inventory、影响 CC 和 RC-06 累计余额。
2. 先捕获 legacy T61A；candidate private engine 与 legacy 共存时默认路由仍指向 legacy。
3. 在双临时根/双安装环境对 old/new 做九 stage request/result/artifact/tree/exception differential，避免重复写同一工作区。
4. candidate PR 切单一内部 selector，完整 legacy 保留并完成 pre-release stability cycle。
5. 独立 deletion PR 删除 legacy，重新跑 differential、rollback/reapply、cross-platform/install/offline/sibling smoke。
6. deletion 前不得写 `completed_reduction`；任一预算或差异失败按 RC-09 保留 legacy。

## 7. 验证矩阵

| 关键路径 | 主验证 | 补充验证 |
|---|---|---|
| 候选测量 | Python AST recipe | `rg` 调用者与 Git baseline exact compare |
| T65 第二真值 | 定义/消费者图 | loader/schema 预测成本审计 |
| T67 历史边界 | current/baseline 九函数 exact compare | WI-204 revoked receipt/claim=0 |
| T66 测量 | AST `end-lineno+1` physical / first non-docstring statement→end executable，45 methods=3,638/3,305 | 18 private helper outside-service refs=0 |
| formal identity | child/parent 六文件逐一 SHA-256 + 父 plan §9 canonical combined | 双 Agent 独立复算 |
| scope | `git diff --quiet` 禁止路径 | `git diff --check` |
| truth | constraints/validate/truth audit | manifest exact integration test |
| PR | Codex reviewed current head | required checks 100% success |

## 8. 回退

- WI212：revert 单一 docs/truth PR，运行时和发布物不受影响。
- 父合同窄修：revert 后 L3 回到发布/删除死锁，因此不得单独摘除而保留 Conditional Go。
- 下一 T66：candidate 删除前切 selector 回 legacy；删除后 revert deletion PR，再回滚 candidate PR；不得靠配置永久保留双实现。

## 9. 开放问题

无用户决策项。两个对抗 Agent 可提出 finding，但只能在当前范围内通过仓库证据处置；任何 L4 需求仍需用户另行批准。
