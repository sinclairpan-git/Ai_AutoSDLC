# 功能规格：Workitem 只读命令 Adapter 副作用隔离

**功能编号**：`214-workitem-readonly-adapter-side-effect`
**日期**：2026-07-19
**类型**：WI-196 / T58 / GAP-15 / L2 / 非减重缺陷修复
**状态**：formal authoring；产品实现须等待同一身份双 Agent PASS0 与 formal fresh-main
**输入**：独立修复五个 `workitem` 只读命令的隐式 adapter refresh，保留 `init/link` 全部既有语义。

## 1. 目标与依据

在 `main@d5ad7616f7f39f68365d6d39f8701a86c1f599e7`，`workitem` 子应用回调对除
`None/init` 外的所有子命令调用 `_run_workitem_adapter()`。因此下列已声明 read-only 的命令会在
handler 前刷新 IDE adapter：

- `plan-check`
- `guard`
- `close-check`
- `branch-check`
- `truth-check`

既有 A/B 证据显示，`program validate` 保持 `.cursor/rules/ai-sdlc.mdc` SHA-256
`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`；而
`workitem plan-check --json` 会输出 install receipt，并把文件改为
`02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134`（tracked diff
`+18/-6`）。这违反只读命令的 bytes、输出与 clean-tree 合同，并会污染后续 T66/T61A 基线。

本 WI 只关闭 GAP-15。它不计入 WI-196 的 Reduction Contract 收益，也不授权 T66、GAP-03、
RC-08 或版本发布。

## 2. 范围

### 2.1 包含

1. 仅修改 `src/ai_sdlc/cli/workitem_cmd.py::_workitem_before_command` 的本地分发条件，使 callback 只为
   当前唯一依赖它的写命令 `link` 调用 hook；`init` 继续由自身 handler 管理，其余当前命令均不调用。
2. 对每个只读命令覆盖 normal、`--help` 与一个 invalid-input 路径；证明 hook count=`0`、adapter/config/
   working-tree bytes 不变、无 install receipt，handler 自身 stdout/stderr/exit 与 no-op-hook 基线相同；
   normal 路径还须在临时项目运行 production hook 的 real-byte fixture。
3. 冻结并回归 `init/link` 的 hook 次数、顺序、输出、退出码与写入集合；把 project-config
   `PermissionError` 的 warning+continue 与其他 exception 的 propagate 两类分开验证。
4. 完成 TDD RED→GREEN、双 Agent 对抗审查、targeted/full/Ruff/constraints、跨平台 CI、PR/Codex、
   merge 与 detached fresh-main 验收。
5. 同步 WI-196/GAP-15、program truth、root/scoped handoff 与生命周期事实；implementation fresh-main 后
   使用独立 lifecycle reconciliation branch/PR 承载关闭 receipt。

### 2.2 不包含

- 不修改 adapter 同步算法、模板、生成内容、root CLI hook 或 `program` 命令族。
- 不修改五个 read-only handler 的领域逻辑、参数、帮助文本、结果模型或错误文案。
- 不修改 `workitem init`、`workitem link` handler 的控制流或写入时序。
- 不引入全局 read/write classifier、registry、decorator、配置、环境变量、公共 API、依赖或版本。
- 不修改 `ProgramService`、T66/T61A 证据或任何减重候选代码。
- 不顺手清理其他 CLI family；发现同类问题只登记，不扩大本 PR。

## 3. 冻结行为合同

### 3.1 唯一批准差异

| 路径 | 当前行为 | 目标行为 | 允许差异 |
|---|---|---|---|
| 五个只读命令 normal | handler 前 hook 1 次 | hook 0 次 | 移除 adapter 写入与 install receipt |
| 五个只读命令 `--help` | child callback 可调用 hook | hook 0 次 | 仅移除 adapter 副作用；help bytes/exit 不变 |
| 五个只读命令 invalid | child callback 可调用 hook | hook 0 次 | 仅移除 adapter 副作用；错误 bytes/exit 不变 |
| `init` | handler 内按既有 preflight 时机调用 | 完全不变 | 无 |
| `link` | child callback 在 handler 前调用 | 完全不变 | 无 |
| 未知 subcommand / workitem 根 help | 不调用 hook | 完全不变 | 无 |

“输出不变”以同 revision、同参数、同 fixture 的 no-op-hook 结果为基线；adapter 自身注入的 install
receipt 是本缺陷的一部分，删除它是唯一批准的输出差异。stdout/stderr 不互换，不做 ANSI/空白宽松化。

### 3.2 `init/link` 兼容矩阵

| 命令/场景 | hook 合同 | 顺序与写入合同 |
|---|---:|---|
| `init` valid clean docs branch | 1 | root/ID/branch/clean preflight 后、scaffold 前；既有 docs/state/manifest 写入不变 |
| `init` missing required option | 0 | 参数解析失败；零业务写入 |
| `init` dirty 或 wrong branch | 0 | preflight 阻断；零 adapter/scaffold 写入 |
| `init` no-project | 0 | root 检查阻断；零 adapter/scaffold 写入 |
| `init` duplicate | 0 | ID 预检阻断；零 adapter/scaffold 写入 |
| `init` project-config `PermissionError` | 1 | preflight 后；保留 `apply_adapter` 已发生写入，输出 warning，继续 scaffold |
| `init` 其他 hook exception | 1 | preflight 后原类型/消息传播；scaffold 不开始，不回滚 hook 前缀写入 |
| `init` no-checkpoint | N/A | `init` 不依赖 checkpoint，不新增此条件 |
| `link` valid | 1 | handler 前调用；随后按既有规则保存 checkpoint |
| `link` help / unknown option | 1 | hook 先执行；help exit=0、invalid exit=2，checkpoint 不写 |
| `link` missing all options | 1 | hook 在 handler 自校验前；exit=2，checkpoint 不写 |
| `link` dirty tree | 1 | 不新增 clean preflight；既有 checkpoint 写入保持 |
| `link` no-project | 1 | hook 在 root 检查前；随后 exit=1，零 checkpoint 写入 |
| `link` no-checkpoint | 1 | hook 在 load 前；随后 exit=1，零 checkpoint 写入 |
| `link` project-config `PermissionError` | 1 | 保留 `apply_adapter` 已发生写入，输出 warning，继续后续 handler 路径 |
| `link` 其他 hook exception | 1 | 原类型/消息传播；handler 不开始，不回滚 hook 前缀写入 |

受控异常仅指 `run_ide_adapter_if_initialized()` 识别到目标为
`.ai-sdlc/project/config/project-config.yaml` 的 `PermissionError`。fixture 必须让真实 `apply_adapter` 先写
guarded adapter，再令 `_persist_config` 失败，逐字节冻结 warning、partial-write set、handler continuation 与
最终 exit；其他 `PermissionError` 和 unexpected exception 都属于传播路径。WI214 不新增事务、补偿或回滚
adapter 内部部分写入。

除“只读 hook 1→0”外，任何 stdout、stderr、exit code、call order、exception type/message、文件集合、
文件 bytes 或 git 状态差异均为未批准差异并阻断合并。

## 4. 需求

- **FR-001**：五个冻结只读命令在 normal/help/invalid 三类入口都不得调用 adapter hook。
- **FR-002**：五个只读命令在写入型 sentinel hook 下必须保持 adapter/config/working-tree bytes 不变且不出现
  marker；其 normal 路径还必须以 `@pytest.mark.real_ide_hook` 在 byte-identical 临时项目运行 production hook，
  证明 guarded adapter/config bytes、stdout/stderr/exit 与 git status 相对 no-op-hook 基线 exact。
- **FR-003**：五个只读 handler 的业务输出、错误输出和退出码必须与同 revision no-op-hook 基线逐字节一致。
- **FR-004**：`init/link` 必须满足 §3.2 全矩阵，分别证明受控 config-lock warning+continue 和其他异常传播；
  不得通过改测试、吞异常、事务化既有部分写入或延后断言伪造兼容。
- **FR-005**：实现必须是 `workitem` callback 内的直接 `ctx.invoked_subcommand != "link"` 判断；不得建立
  命令名单、全局 classifier 或新抽象层。未来命令必须显式决定是否需要写副作用，不能默认消费 hook。
- **FR-006**：TDD 必须先在未改产品源码的 identity 上得到能证明 GAP-15 的 RED，再做最小 GREEN。
- **FR-007**：formal 与实现都必须由 Pascal/LEAN 和 Confucius/SAFETY 对同一 committed+clean identity
  独立审查；任一受审文件变化使双方 verdict 同时失效，直到双 PASS 且 actionable findings=0。
- **FR-008**：formal 使用 docs branch/PR；实现从 formal fresh main 建 dev branch/PR；implementation
  fresh-main 后从 main 建独立 lifecycle reconciliation branch/PR。三个阶段都必须完成 final current-identity
  双审、Codex、required checks、merge 与 detached fresh-main。
- **FR-009**：implementation truth/handoff 与本地门禁必须在 final 双审之前完成；其后任一内容变化都使双方
  verdict 失效。Implementation PR 不得提前把 GAP-15/T58 写成 closed/completed。
- **FR-010**：只有 lifecycle reconciliation fresh-main 才关闭 T58/GAP-15 并授权创建 T66 implementation
  WI/T61A；RC-08 前不得发布版本。
- **FR-011**：implementation merge 后、lifecycle merge 前的回退只 revert implementation PR；lifecycle 已
  merge 时必须先 revert/修正 closure receipt 以重开 GAP-15并阻断 T66，再 revert implementation PR。

## 5. 成功标准

- **SC-001**：`5 × 3 = 15` 个只读 CLI 入口全部 hook count=`0`、sentinel bytes/clean-tree 不变；五个 normal
  路径另有 real production hook 的 guarded bytes/hash/status 证明。
- **SC-002**：15 个入口的 stdout/stderr/exit 与 no-op-hook 基线 exact match；唯一删除内容是 adapter receipt。
- **SC-003**：§3.2 的适用场景全部有自动化断言，`init/link` 未批准差异为 0。
- **SC-004**：产品实现只改一个既有函数，不新增产品文件、公共符号、依赖、配置或版本；新增判断直接可读。
- **SC-005**：targeted、full、Ruff、constraints、program validate/truth、manifest exact、scope、handoff parity、
  Cursor base bytes 与 clean-tree 全绿。
- **SC-006**：formal、implementation 与 lifecycle reconciliation 的 final current identity 均取得双 Agent
  PASS0；各 PR 的 Codex/CI/merge/fresh-main 均有可追溯 receipt。
- **SC-007**：parent GAP-15/T58 只在 lifecycle fresh-main 后标记关闭；T66 T61A 仅在该关闭事实后恢复。

## 6. 停止、回退与发布边界

若实现需要修改 adapter 算法、root callback、handler、第二 CLI family，或无法保持 §3.2 零差异，立即停止并
回到 formal，不用扩范围掩盖问题。Formal PR 可独立 revert；implementation 未形成 closure 时直接 revert
实现 PR。Lifecycle 已关闭后，先 revert/修正 lifecycle receipt，明确重开 GAP-15、阻断尚未开始或正在进行的
T66，再 revert 实现 PR，禁止留下“代码已回退但 truth 仍 closed”。WI214 局部完成不触发 tag、GitHub
Release、PyPI 或共享 CLI 更新。
