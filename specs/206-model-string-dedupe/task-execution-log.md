# 任务执行日志：Model String Dedupe Reduction

**功能编号**：`206-model-string-dedupe`
**创建日期**：2026-07-16
**当前状态**：formal review candidate；未进入 execute

## 1. 归档与安全规则

- 每个批次记录 revision/tree、范围、命令、结果、RC/CC/GAP、回退和评审结论。
- formal 内容变化使两个 Agent 的旧 verdict 同时失效；final source 另算 tree/diff hash。
- mutation 与 rollback 只在可恢复 patch/disposable clone 中执行，不使用 destructive reset/checkout。
- 产品、测试和日志按逻辑批次提交；日志不预写未知 commit hash。
- continuity 在方向变化、代码批次、测试/调试后和交接前更新。

## 2. Batch 2026-07-16-001：范围审计与候选选择

### 2.1 父路线状态

- WI-205 / PR #134 / merge `aa156afe53534a10b1379348c532eb554ccf9ad3` 已完成 artifact path
  helper 减重和 fresh-main 验收，但 WI-196 的 WP-02～WP-07 与 RC-08 总体终态仍未关闭。
- WI-203 的 9-command WP-07 formal 删除收益高；WI-204 已证明其安全保护最低 222/356 LOC，超过
  cap 180，按 RC-09 No-Go，claim=0、legacy 保留，当前不得复活。
- WI-202 T62A 仍缺新/替代 sponsor 与重新双审父合同；WP-02 暂不可启动。

### 2.2 候选排序

只读审计建议顺序：

1. 17-module `_dedupe_strings` T63/WP-03：204→29 replacement slice、净删 175、L1；
2. Page/UI baseline T65：此前条件 Go，但 L2、净删预测 72～82、保护 cap 18～20；
3. Loop Store：完全一致切片仅 39 LOC，新增 helper 超 RC-06，当前 No-Go；
4. ProgramService L3；
5. Program Stage L3；WI-203 candidate 受 WI-204 No-Go 约束。

因此本项只选择第 1 项，不混入 T65/WP-04/WP-06/WP-07。

### 2.3 fresh-main 事实

- 基线：`origin/main@aa156afe53534a10b1379348c532eb554ccf9ad3`。
- 17 个 definition 的 AST body digest 全部为
  `3a0faf9ac553d0701610620b2b17ee0dda2fa014442a3eebf0a0c6c11067042d`。
- defs=17、calls=92、algorithm non-empty LOC=204、complexity proxy=68。
- 17 产品文件=8,181 raw / 7,162 non-empty LOC。
- 17 targeted test files=9,766 raw / 8,955 non-empty LOC。
- PowerShell 7.5.8 执行 targeted：`236 passed, 2 skipped in 5.64s`。
- fresh-main full acceptance 已记录：`3220 passed, 3 skipped`。

## 3. Batch 2026-07-16-002：创建 WI-206 formal

### 3.1 canonical scaffold

- branch：`feature/206-model-string-dedupe-docs`
- worktree：`.worktrees/206-model-string-dedupe`
- 命令：`uv run ai-sdlc workitem init --wi-id 206-model-string-dedupe ...`
- 结果：五件套、manifest mapping 与 project-state sequence 创建；未修改产品代码。

### 3.2 冻结设计

- 新增唯一 `src/ai_sdlc/models/_string_lists.py`，原样 12 LOC helper，不 public export。
- 17 个模块各加一条 import、删除 12 LOC local body；92 个调用和 validator 不变。
- 预测产品 +29/-204/net -175；算法 204→12，含 imports 204→29；complexity 68→4。
- RC-06 cap=51；共享身份 test≤4 + root truth additions=2 后全部 source additions≤35，余量≥16。
- 现有 program order test 承担 reverse mutation；不新增重复行为测试或 harness。

### 3.3 下一步

1. 完成五件套、root truth tuple、parent route index 与 continuity。
2. 计算 `spec.md + plan.md + tasks.md` exact hashes。
3. Pascal/Confucius 独立 review 同一 tuple；处置 findings 直至共同 PASS。
4. 运行 formal gates，提交/PR/merge 后再建立 implementation branch。

## 4. Batch 2026-07-16-003：root truth RED/GREEN 与 formal Round 1

### 4.1 root inventory 精确红绿

- RED：新增 WI-206 五件套后运行 root manifest 精确 nodeid，旧 expectation
  `1081/1081/0/0` 在实际 `1086/1086/0/0` 上失败；`1 failed in 69.41s`。
- 修订：只把两个既有 tuple 更新为 inventory `1086/1086/0/0`、close `206/206`。
- GREEN：同一 nodeid `1 passed in 68.97s`；未新增 test function/file 或放宽其他断言。

### 4.2 Program Truth 与 formal gates

- `program truth sync --execute --yes`：snapshot hash
  `eb9b25da65542b9f7d58611606ca103f9b8bb378fe5ce24c9e21650046cddccd`；state ready；
  inventory 1086/1086、unmapped=0、missing=0，各 formal/close layer=206/206。
- `program truth audit`：fresh + ready；两个 release capability closure=closed/audit=ready。
- `program validate`：PASS；`verify constraints`：no BLOCKERs；`git diff --check`：PASS。
- checkpoint 已绑定 `206-model-string-dedupe`；canonical/scoped handoff 已刷新。

### 4.3 Round 1 formal review target

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `b733bfdba5bd49607fa8a5646bba568d7989b8e9ba28390d1786af04e2e996de` |
| `plan.md` | `05b2553d329e278d52e34fb5b76e16cf2b0f85c14ffeadbab7fb8af97d15ef63` |
| `tasks.md` | `ac3139e00986e561c192a13a6e43f886a9b7f8f17522c7d5895ed9f2472e8ed3` |

固定顺序 path + NUL + 8-byte length + bytes combined SHA-256：
`90c0895c92b33b15766a869fb9a3d88022888395eb1a6a29d79a0e272689c366`。

Pascal 与 Confucius 已分别从精简效率、兼容安全维度启动只读评审；任何 target 内容变化使本轮
verdict 失效。

## 5. Batch 2026-07-16-004：Round 1 双 FAIL 与统一修订

### 5.1 Pascal / 精简效率

- `state.py::_dedupe_string_items` 与目标 body digest 完全一致且有8个调用；原17-module边界漏项，
  正确基线为18 defs、100 calls、216 LOC、complexity72。
- 定向测试漏 `test_frontend_contract_models.py` 和 state 直接覆盖；正确19-file fresh baseline为
  `281 passed, 2 skipped in 1.65s`，10,537 raw / 9,646 non-empty LOC。
- 每模块重复保存同一 corpus 属于证据臃肿；应按 distinct body digest 保存一份，再用 binding matrix关联。
- verdict=`FAIL`；起止 formal hashes 一致，无文件修改。

### 5.2 Confucius / 兼容安全

- 原定向清单未覆盖 `frontend_contracts` 的 ValidationError/dedupe tests。
- 9-case corpus漏 bare string、iter/next部分失败、str/hash/equality可达异常与事件顺序。
- body-only digest不能证明参数名、annotation、defaults、decorators与runtime signature。
- rollback承诺与计划不一致，且没有 exact tree identity。
- verdict=`FAIL`；Program Truth fresh/ready、root nodeid PASS、起止formal hashes一致，无文件修改。

### 5.3 Round 2 统一处置

- 纳入 `state.py`，但显式排除带decorator/classmethod/`cls`参数的dispatcher class validator；后者需要
  wrapper或decorator rebinding，不属于本顶层helper原子项。
- 新helper保留future annotations；产品预算修订为 +≤33/-≥216/net≤-183，RC-06 source≤39/54。
- 19-file module→test mapping显式落plan，fresh baseline `281 passed, 2 skipped`。
- corpus改为每distinct digest一份，增加bare string与iter/next/str/hash/eq event trace；18-module binding表
  证明适用范围。
- 结构gate增加full FunctionDef、signature contract、inspect/annotations/default/doc/private consumer。
- rollback收窄为exact baseline/candidate tree OID + targeted/corpus；full只在baseline/candidate各跑一次。

Round 1 hashes自内容修订后全部失效；必须计算Round 2新target并由双方从零复审。

### 5.4 Round 2 formal review target

修订后 Program Truth sync/audit：snapshot
`45c6947bcaf9054923a1f20d158901f55d4b7d07fb2fb9cd42f77930e3299834`，fresh/ready，
inventory 1086/1086、unmapped=0、missing=0；validate PASS、constraints no BLOCKER、diff check PASS。

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `0733bd67ad3d0c140056e77a56bc9307dd9dc1173e21882a7d9d64a7a83a4365` |
| `plan.md` | `b65484542d489eadae8d8424d772c745473cd72313c3d0a03b764da83c0f0e42` |
| `tasks.md` | `e1e5e1ed0bb06284ea7888d7d6412409d4ee1c8442a82806707d333ef90b703d` |

固定顺序 combined SHA-256：
`77d3234839a9776b1f274272fffbb87258b6b715c264648d0cee2b0806efa88a`。
Round 2 只接受双方在结束前重新复算并确认上述 target 未漂移后的 verdict。

## 6. Batch 2026-07-16-005：Round 2 分歧与 Round 3 收敛

### 6.1 Round 2 verdict

- Pascal / 精简效率：`PASS`，未发现可操作问题；起止 hashes 一致，未修改文件。
- Confucius / 兼容安全：`FAIL`，剩余两项次要但可操作问题：
  1. introspection allowlist 未显式批准共享函数必然改变的 `__globals__`、`__code__` identity、
     `co_filename`、`co_firstlineno`、source file 与 traceback frame；
  2. `tasks.md` 的“四件套”与实际五个 formal 文件不一致。
- Round 2 target 因处置上述 findings 后失效，不沿用 Pascal 的旧 `PASS`。

### 6.2 Round 3 统一处置

- introspection contract 改为有限枚举 allowlist：显式记录允许变化的 `__module__`、`__globals__`、
  `__code__` identity/source location 与 traceback frame；保留 signature、annotations、defaults、
  kwdefaults、doc、argcount、kwonlyargcount、调用结果和 public behavior。
- 保留 `state.py` 本地 alias 名 `_dedupe_string_items`；共享 callable 的 `__name__` / `__qualname__`
  统一为 `_dedupe_strings`，并明确 formal 不承诺未枚举的所有 Python introspection observable。
- formal 文件数量统一为五件套；T12/T14 的 verdict 与完成状态只写 execution log，避免任务正文自证。

### 6.3 Round 3 formal review target

Program Truth sync/audit：snapshot
`991bdf0c718b657912cc83044aa7c7a3f970a85e90f5c2470275f403d0572a2c`，fresh/ready，
inventory 1086/1086、unmapped=0、missing=0；validate PASS、constraints no BLOCKER、diff check PASS。

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `523fbe634a0dfbfedb38352d8157ab8b3921b8d24d8fad1850204231804d15d5` |
| `plan.md` | `363b1b2c137634f537baf39481df745866597f57ff00c6cd315d40d3d17fae3e` |
| `tasks.md` | `e07d0b59aeda795b41393a6e58a1e0e354409b4600e9f079d1cbe692b3111401` |

固定顺序 combined SHA-256：
`3d6defd4f39b50c378d40ec6118f42109076f2fb1a45221f060a4ff74666c959`。
Round 3 必须由双方从零复审同一 target，且只在结束前 hashes 仍一致时接受 verdict。

## 7. Batch 2026-07-16-006：Round 3 双 FAIL 与轮次解耦

### 7.1 Round 3 verdict

- Pascal / 精简效率：`FAIL`。`plan.md` 实施顺序仍写已作废的“Round 2 formal 同哈希双 PASS”，
  可能使执行者错误接受旧 verdict；其余范围、预算、证据和回退未发现可操作问题。
- Confucius / 兼容安全：旧 target 已被通知作废，仍独立确认同一轮次引用问题；另发现
  `spec.md` 把 100 个调用表达式误称为 100 个 validator 调用。AST 实际为 99 个
  `field_validator` 内调用，加 `state.py::_dedupe_dict_string_lists` 中 1 个普通 helper 调用。
- 双方均保持只读；Round 3 target 内容修订后全部 verdict 失效。

### 7.2 Round 4 统一处置

- 实施门禁改为“当前 formal target 同哈希双 PASS”，不再把执行语义绑定到可能继续增长的评审轮次。
- US-1 改为“100 个现有调用表达式”，与 AST、其他 formal 位置和 binding ledger 一致。
- 重新计算 Round 4 exact hashes 后，双方必须再次从零复审。

### 7.3 Round 4 formal review target

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `d3a72359b3913e5c28964c021646b1be5e9e56b3c6faf2f6537088d2a90963eb` |
| `plan.md` | `85d8a38a02bbf9d12e92ce6553ddf9fe75f8cb9c9e365e97320be1f4c14370f0` |
| `tasks.md` | `e07d0b59aeda795b41393a6e58a1e0e354409b4600e9f079d1cbe692b3111401` |

固定顺序 repo-relative path + NUL + 8-byte big-endian length + bytes combined SHA-256：
`fb0fbb4d9d5ef4ae3c7beeb299136884fe41327752dd01f9ae368ce655a94bbd`。

### 7.4 Round 4 双 PASS

- Pascal / 精简效率：`PASS`；无 Critical、Important 或其他可操作 finding。
- Confucius / 兼容安全：`PASS`；无可操作 finding。
- 双方均在开始与结束独立复算并确认 spec/plan/tasks/combined 等于 §7.3 target，且均未修改文件。
- 共同确认：18 defs / 100 调用表达式（99 validator + 1 ordinary helper）/ 216 LOC / complexity72；
  product `+≤33/-≥216/net≤-183`；source additions `39≤54`；19-file `281 passed, 2 skipped`；
  state alias、dispatcher 排除、event corpus、introspection allowlist、mutation、rollback/full/fresh-main
  顺序均闭合。
- `program-manifest.yaml` 的 WI-206 `depends_on` 已与 formal 父项声明对齐到
  `196-ai-sdlc-lean-code-self-reduction-governance`；未改变 formal target。

T14 完成；下一步进入 T15 formal 最终验证、提交、PR 和 mainline receipt。

## 8. Batch 2026-07-16-007：T15 formal 最终本地门禁

- Round 4 target 结束复算仍为 §7.3 的三个单文件 hashes 与 combined `fb0fbb4d...94bbd`。
- 19-file targeted：`281 passed, 2 skipped in 1.85s`。
- root Program Truth exact nodeid：`1 passed in 72.33s`。
- `program truth sync --execute --yes`、`program truth audit`：ready/fresh，inventory 1086/1086，
  unmapped=0、missing=0、close 206/206；canonical snapshot 以最终 `program-manifest.yaml` 为准。
- `program validate`：PASS；`verify constraints`：no BLOCKERs；`git diff --check`：PASS。
- formal worktree 无 `src/` 产品代码变化；仅 WI-206 formal/continuity、父路线记录、truth manifest 与
  root inventory 精确 expectation 在提交范围内。

本地 T15 门禁通过；待 commit/push/PR、Codex review、required checks、merge 与 fresh-main receipt。

## 9. Batch 2026-07-16-008：暂存门禁揭示格式漂移与 Round 5

- 首次 `git diff --cached --check` 揭示新 formal Markdown 沿用脚手架行尾双空格，命中
  `trailing whitespace`；此前未暂存检查未能证明最终 index，§8 的 diff-check 结论因此撤回。
- 该问题不改变需求语义，但违反 T15 的可提交性门禁；Round 4 target 不能作为最终 receipt。
- 机械删除 WI-206 五件套所有行尾空白，不修改词句、结构、预算、命令或验收语义。
- Round 5 target：

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `ac0a7137ff6da59ed3a98ba7668f3152e1c49fd3e3cec92887e71811d31d16b3` |
| `plan.md` | `788626860e3ac811c9a8b0344892d8adca463cbe60e297c493d6e310dab7f766` |
| `tasks.md` | `55feaf160227b60cdbbddcebc4d07ae7af233667a10e5cd995e63dab81acb345` |

固定顺序 combined：`85ccdca44eccec5faca7baedb98233401059188f6b4bf7b5460a5e21da18c45f`。
双方必须针对 Round 5 从零复审，旧 PASS 不沿用；最终门禁必须同时检查 working tree 与 staged index。

## 10. Batch 2026-07-16-009：Round 5 双 PASS 与 formal admission

- Pascal / 精简效率：`PASS`；Critical、Important、Other actionable 均无。
- Confucius / 兼容安全：`PASS`；无可操作 finding。
- 双方开始/结束均复算并确认 §9 三个单文件 hashes 与 combined 完全一致，评审全程只读。
- 双方逐行确认 Round 4→Round 5 仅删除行尾空白，未改变合同文字、数字、范围、顺序或验收条件；
  `git diff --check` 与 `git diff --cached --check` 均 exit 0。
- 共同复核仍为：18 defs、100 calls（99 validator + 1 ordinary helper）、216 LOC、complexity72，
  product `+≤33/-≥216/net≤-183`，source additions `39≤54`，19-file `281 passed, 2 skipped`，
  root truth `1 passed`，Program Truth fresh/ready 1086/1086，constraints 无 BLOCKER，无 `src/` 变化。

Round 5 是当前唯一有效 formal receipt；T14 完成。T15 只剩 commit/push/PR、Codex review、required
checks、merge 与 fresh-main acceptance。

## 11. Batch 2026-07-16-010：implementation 探针触发预算 amendment

- Formal PR #135 已合并 main=`1a37e684d82370f0961275840616c109b7a07f87`；fresh-main targeted
  `281 passed, 2 skipped`、root truth `1 passed`、Program Truth fresh/ready。
- implementation T61A 基线：Python 3.11.15、Pydantic 2.12.5、macOS arm64；full
  `3220 passed, 3 skipped in 594.40s`；18 defs、100 calls、216 LOC、complexity72、digest/corpus均复现。
- identity 断言在 legacy 上稳定 RED，最小 shared helper/import 实验后 GREEN。
- Ruff `I001` 证明 4 个没有既有 first-party import block 的模块必须各增加 1 条分隔空行；真实最小
  product raw additions 是 `15 helper + 18 imports + 4 separators = 37`，旧上限33不可满足。
- 该差异不增加行为、依赖、抽象或测试；保守预算修订为 product +≤37/-≥216/net≤-179，
  source≤43≤54、余量≥11。当前实现暂停，旧 formal hashes/verdict 对预算内容作废。

预算 amendment 必须在独立 formal branch 由 Pascal/Confucius 对同一新 hashes 从零 PASS、PR 合入 main
后，implementation branch 才允许合并最新 main 并继续。

### 11.1 Budget amendment formal target

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `a614e9a0d76beea69a5a3039aaeb3952831104dc3ee01cabd7b20fd76487dc45` |
| `plan.md` | `8b16dcf7f3e692f580eadfc1d5b45a3d163079fe77f2530761de9e12ad19ea4e` |
| `tasks.md` | `d9444b7f66e84bc2d7de842743eb6bd2e40f7dc3616dd2d7a031af6593233b6a` |

固定顺序 repo-relative path + NUL + 8-byte big-endian length + bytes combined：
`3f036e0ed6f3bdc1eb0cf5496c172f8926103832a91ae6b95768ae66747f04de`。

### 11.2 Budget amendment Round 1 adversarial verdict

- Pascal：`FAIL`。旧文本没有禁止 late import 与 lint suppression；在 helper 原位置使用
  `# noqa: E402` 可把四个模块压回单条 addition，因此“37 是整洁实现最小值”尚未被合同锁定。
- Confucius：`FAIL`。独立复现标准顶层、无 suppression candidate 为 product `+37/-246/net -209`、
  defs=1/imports=18/calls=100、targeted `281 passed, 2 skipped`；除同一合同缺口外未发现安全 blocker。
- 处置：Round 1 target 作废；spec/plan/tasks 同步要求标准顶层 first-party import block，并禁止
  late/mid-file import、分号/多语句压行、noqa/isort/Ruff 配置修改及等价 suppression。四个模块的
  分隔空行由此成为可复验的最小整洁成本，其余 14 个模块复用删除首个 helper 后释放的既有空行。

### 11.3 Budget amendment Round 2 formal target

| 文件 | SHA-256 |
|---|---|
| `spec.md` | `b3b4c05b3f957ef5f6cce362d902502a05943240ff072134005b7e3c61352972` |
| `plan.md` | `2429e3f8d6e9ee276d704cf11ca61566c60e9046fe12f04ee0d57fdbca7c5ab5` |
| `tasks.md` | `c8c910cb99ac9470fb153f4095b62be85e6112dcebd97c6969b444430c6e1744` |

固定顺序 repo-relative path + NUL + 8-byte big-endian length + bytes combined：
`d0e29ec47fbf3582c275e6a0ca6f7ee94acb2ac3efc5669291d70ac619930566`。

### 11.4 Round 2 pre-review gates

- `program truth sync --execute --yes`：snapshot
  `464fa08a63c5bcbd3cab5940c8e39a4dc8272d40e223c234c8b2bd6d5a10cb7b`；audit
  ready/fresh，inventory 1086/1086、unmapped=0、missing=0、close 206/206。
- `program validate`：PASS；`verify constraints`：no BLOCKERs；治理命令产生的 Cursor adapter
  自动刷新已精确恢复，不进入 amendment diff。
- 19-file targeted：`281 passed, 2 skipped in 2.06s`。
- root Program Truth exact nodeid：`1 passed in 78.97s`。
- Round 2 三个 formal hashes 复算稳定；working diff-check PASS；工作树无 `src/` 产品代码变化。

### 11.5 Round 2 双 PASS

- Pascal / 精简直接性：`PASS`；无 Critical、Important 或其他可操作 finding。确认标准顶层、无
  suppression 的最小成本严格为 `15 helper + 18 imports + 4 separators = 37`；`+37` 上限已被
  必要成本占满，不存在 padding、wrapper、预算放水或更直接且同等安全的替代方案。
- Confucius / 兼容证明：`PASS`；无可操作 finding。独立确认 candidate product
  `+37/-246/net -209`、source `43≤54`、defs 18→1/imports18/calls100、14类事件差分一致、
  targeted `281 passed, 2 skipped`、Ruff 全绿，rollback/full CI/schema/error 保护完整。
- 双方开始与结束均复算并确认 §11.3 的 spec/plan/tasks/combined hashes 完全一致，只读且未修改
  文件；working/cached diff-check 均通过，amendment 无 `src/` 或 `tests/` 变化。

Round 2 是本预算 amendment 唯一有效 adversarial receipt；旧 Round 1 target/verdict 不再有效。

### 11.6 PR #136 Codex P2：resume-pack 可移植性

- Codex review 指出根与 scoped `resume-pack.yaml` 被 handoff 命令写成当前 macOS worktree 绝对路径；
  换 checkout 后 `load_resume_pack()` 会判 stale，并可能在重建时丢失当前 `context_summary`。
- 处置：两份 pack 恢复 repo-relative constitution/tech-stack/spec/plan/tasks path，补回本 amendment
  active files，并记录实际 branch；formal spec/plan/tasks 三文件及 combined hashes 不变。
- `uv run ai-sdlc handoff show` 前后两份 pack SHA-256 稳定，未触发 stale rebuild；
  `tests/unit/test_context_state.py tests/integration/test_cli_handoff.py` 为 `27 passed in 0.74s`。
- 该修复只影响连续性元数据，不改变预算、产品代码、测试代码或 formal 双 PASS receipt。

### 11.7 PR #136 Codex Round 2 P2：summary 预算一致性

- Codex re-review 指出 `development-summary.md` 首段仍把初始 `+≤33/net≤-183` 表述为“当前计划”，
  与后文已生效的 amendment `+≤37/net≤-179` 冲突，恢复执行者可能误用旧硬门禁。
- 处置：首段明确把 `+33/-183` 标为 amendment 前历史预算，并指向当前唯一有效的
  `+37/-≥216/net≤-179、source≤43≤54`；formal spec/plan/tasks hashes 与双 PASS receipt 不变。

## 12. Batch 2026-07-16-011：T61A/T61B implementation、mutation 与 rollback

- Budget amendment PR #136 在处理两个 Codex P2 后，以 merge commit
  `22f4d32f4e1c4c658a12be66aa128190b0a132fe` 合入 main；fresh-main formal hashes、19-file
  `281 passed, 2 skipped`、root truth `1 passed`、truth ready/fresh 1086/1086，acceptance worktree clean。
- implementation branch fast-forward 到该 main；identity legacy RED、candidate GREEN。product-only commit
  `6c52f03f94f3415d03914e3e03424c1c41de8621` 精确包含 19 个产品文件与既有 test 的 2 行断言。
- Git raw ledger：product `+37/-246/net -209`，test `+2/0`；累计 WI source additions
  `37+2+2=41≤43≤54`，RC-06 余量 13；无 suppression、wrapper、public export 或新依赖。
- candidate probe：defs18→1、calls100、complexity72→4、binding identity18→1，所有模块绑定
  `ai_sdlc.models._string_lists._dedupe_strings`；body/full/signature digest 满足合同，14类 result/exception/
  event trace 与 baseline 零差异；raw product LOC 8556→8347，净减209。
- Ruff：PASS；19-file targeted：`281 passed, 2 skipped in 1.40s`。
- reverse-order mutation：既有 order assertion 稳定 `1 failed in 0.18s`；apply_patch 恢复后
  `1 passed in 0.17s`，mutation 未提交。
- exact rollback disposable worktree：candidate tree
  `0762c1b3653fd476c75fc515d503c5a26a54d717`；revert commit `fb4d1d32...` 后 tree
  `c50937d345a4e93dde931b0ed2c1d98d6813081c` 精确等于 amended-main baseline；reapply commit
  `9be6cbac...` 后精确回到 candidate tree。revert/reapply 两侧 targeted 均 `281 passed, 2 skipped`，
  corpus/aggregate/top-level helpers 分别与 baseline/candidate 完全一致，不重复 full。
- candidate full：`3220 passed, 3 skipped in 564.24s`；与 baseline `3220 passed, 3 skipped` 计数一致。
- 唯一 receipt：`.ai-sdlc/work-items/206-model-string-dedupe/t61-differential-rollback-receipt.json`，
  SHA-256 `bb654c134fb4460d163f771b7d36da1e58dc898c5631032dcaa206d2e0d7abd8`。
- full suite 期间连续性 pack 被运行路径再次自动刷新为绝对 worktree path/空 working set；已在证据批次
  后恢复 repo-relative。该副作用与 `program` 自动 Cursor 刷新一起登记为后续独立原子 gap，不混入产品 commit。

T31、T32、T33、T34、T41、T42 已完成；T43 只剩 root truth 与 final governance，之后进入 T51 双审。

## 13. Batch 2026-07-16-012：T43 final governance

- root Program Truth exact nodeid：`1 passed in 77.14s`；Ruff：PASS；working diff-check：PASS。
- `program truth sync --execute --yes` 后 audit 为 ready/fresh，inventory `1086/1086`、unmapped=0、
  missing=0；精确 snapshot/hash 与可变 signal counts 只以最终 `program-manifest.yaml` 为准，避免在
  truth authoring 输入中自引用当前值。
- `program validate`：PASS；`verify constraints`：no BLOCKERs；GAP-09～11 未见回归。
- 治理命令再次自动刷新 `.cursor/rules/ai-sdlc.mdc`；已用 `apply_patch` 精确恢复 HEAD，工作树不含该
  文件。两份 resume-pack 保持 repo-relative，未出现当前机器绝对路径或 `.worktrees/` 路径。
- formal spec/plan/tasks hashes 与 combined `d0e29ec47fbf3582c275e6a0ca6f7ee94acb2ac3efc5669291d70ac619930566`
  稳定；receipt SHA-256 仍为 `bb654c134fb4460d163f771b7d36da1e58dc898c5631032dcaa206d2e0d7abd8`。

T43 完成；下一步冻结同一 HEAD/tree/binary diff/name-status/receipt/formal hashes，执行 T51 双 Agent
final tree 对抗评审。评审结论回写后将再次冻结并复审最终内容，避免“记录评审结果”改变被评审目标。

## 14. Batch 2026-07-16-013：T51 Round 1 双 FAIL 与证据自引用修复

- Round 1 历史目标：HEAD `d793f6a7ecc61e1c5aea86ed0f837ffe1f4d6828`、tree
  `2839802c73a9df538c472958d91c9968174dc764`、binary diff
  `f89b27fe69d791e12530b20726249c6587743d69f5f288c4d23df5ddc0e62437`、name-status
  `507865a5290883b4c35f3b2b17370faaf68c680454483e56d40704e2fcc16319`；receipt 与 formal hashes 稳定。
- Pascal / 精简直接性：`FAIL`；Confucius / 兼容证明：`FAIL`。双方独立发现同一 Important：T43
  authoring 文档与 handoff 把 pre-final sync 的 snapshot/hash 与 signal count 写成当前最终真值；这些
  文件本身进入 truth inventory，回写后再 sync 会产生新值，造成自引用漂移。
- 产品实现、ledger `+37/-246/net -209`、source `41≤43≤54`、18→1/calls100、targeted
  `281 passed, 2 skipped`、Ruff、corpus、mutation、rollback/reapply 均未发现问题。
- 处置：从 execution summary 与 handoff 删除当前精确 snapshot/hash 和可自增 signal count；只保留
  ready/fresh、inventory complete、zero blocker 等稳定结论，并规定当前精确 truth 仅以最终
  `program-manifest.yaml` 为准。终态 sync/audit 后重新冻结 Round 2；Round 1 目标与 verdict 作废。

## 15. Batch 2026-07-16-014：T51 Round 2 continuity 修复

- Round 2 历史目标：HEAD `c9b849a90771a8cf1522a14f004e941904a1e0d2`、tree
  `e07167f3a9884ec25904e891b7c4ed47195eda9a`、binary diff
  `33daeb06361eb49a948138fd0441a236294f103e499e0fccaaa9c3c31f845f04`、name-status
  `507865a5290883b4c35f3b2b17370faaf68c680454483e56d40704e2fcc16319`；receipt 与 formal hashes 稳定。
- Confucius / 兼容证明：`PASS`，确认 Round 1 自引用 finding 已闭环，产品、corpus、rollback、
  resume-pack path 与跨平台保护无 finding。
- Pascal / 精简直接性：`FAIL`，发现 root/scoped handoff 与两份 resume-pack 的 exact next step 仍要求
  “终态 sync/audit 后冻结 Round 2”，但该动作已经完成；恢复者会重复 sync，改变 generated_at、
  snapshot 与冻结 diff。
- 处置：连续性状态统一为稳定终态——terminal sync/audit 完成后，当前冻结目标只执行同哈希双审；
  双 PASS 不再改树并直接 push/PR，FAIL 才修订、sync 与 refreeze。Round 2 目标作废，重新冻结 Round 3。
- 产品实现、receipt、formal hashes、预算与测试证据均未变化；当前精确 truth 继续只以 manifest 为准。
