# 功能规格：ProgramService artifact loader 精确重复族减重

**功能编号**：`217-programservice-artifact-loader-dedupe`
**创建日期**：2026-07-21
**状态**：formal authoring
**类型**：WI-196 / WP-03 / T63 / GAP-05 / L1
**父项**：`196-ai-sdlc-lean-code-self-reduction-governance`
**基线**：fresh-main `b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`

## 1. 目标与边界

把 `ProgramService` 中 13 个同形 frontend artifact YAML loader 收敛成一个私有 helper：12 个普通、
单调用者 wrapper 由内部 caller 直接传入冻结 label；只有额外规范化 persisted warnings 的 project-cleanup
wrapper 保留。所有公共 callable、DTO、CLI、artifact 路径、YAML 读取、错误文本、异常文本和 cleanup
warning 语义必须逐字保持。

本工作项的 implementation 若 GO，则修复一个 T63 精确重复族并登记真实产品净删除；implementation
merge 本身不关闭 GAP-03/T66、GAP-05、WI-196、RC-08 或 release，唯一 closure 按 §4.1 在 GO/NO-GO
两条路径统一关闭路线。它不继承 WI-213/WI-215 的结构、预算、GO、hash 或 reviewer receipt。

formal 与 implementation 必须使用独立分支和 PR。formal PR 禁止修改 `src/**` 或产品测试逻辑；只有 formal
fresh-main 验收通过后，才能从新的 fresh-main 创建 implementation 分支。

## 2. Current-main 基线（RC-01 / RC-02）

- `src/ai_sdlc/core/program_service.py`：17,474 physical LOC。
- 目标重复族：13 个 `_load_frontend_*payload` 私有方法，403 physical LOC / branch proxy 39。
- 12 个普通 loader 各有一个 service 内调用者；project-cleanup loader 有六个 service 内调用者。
- 除上述18个 `ProgramService` 内部 callsite 外，没有其他产品代码或测试消费者；历史 specs 只作记录，
  不是运行时 seam。
- `tests/unit/test_program_service.py` 基线为 18,311 physical LOC；fresh-main 实跑
  `406 passed in 35.83s`。
- 目标文件不属于 generated、fixture 或 vendored 源码。

冻结的 12 个 caller→label 绑定如下；表外不得新增 label registry 或动态派发：

| Caller | Exact label |
|---|---|
| `build_frontend_provider_handoff` | `remediation writeback` |
| `build_frontend_provider_patch_handoff` | `provider runtime` |
| `build_frontend_cross_spec_writeback_request` | `provider patch apply` |
| `build_frontend_guarded_registry_request` | `cross-spec writeback` |
| `build_frontend_broader_governance_request` | `guarded registry` |
| `build_frontend_final_governance_request` | `broader governance` |
| `build_frontend_writeback_persistence_request` | `final governance` |
| `build_frontend_persisted_write_proof_request` | `writeback persistence` |
| `build_frontend_final_proof_publication_request` | `persisted write proof` |
| `build_frontend_final_proof_closure_request` | `final proof publication` |
| `build_frontend_final_proof_archive_request` | `final proof closure` |
| `build_frontend_final_proof_archive_thread_archive_request` | `final proof archive` |

project-cleanup 的 exact label 固定为 `final proof archive project cleanup`，其六个 caller 不变。

## 3. 唯一允许设计

新增一个 class-private helper：

```python
def _load_frontend_artifact_payload(
    self,
    artifact_path: Path,
    *,
    artifact_label: str,
) -> tuple[dict[str, object] | None, list[str]]:
    ...
```

helper 必须按旧顺序执行：`exists` → UTF-8 `read_text` + `yaml.safe_load` → mapping 类型检查 →
返回 payload。missing、YAML/read exception、non-mapping 的 exact 输出分别保持：

```text
missing <label> artifact: <root-relative-or-absolute-path>
invalid <label> artifact: <root-relative-or-absolute-path> (<exception>)
invalid <label> artifact: <root-relative-or-absolute-path>
```

12 个普通 wrapper 删除，调用者显式传入上表 label。project-cleanup wrapper 调用 common helper；只有当
payload 是 mapping 时返回 `_normalize_string_list(payload.get("warnings", []))`，错误路径原样返回 helper
warnings。

禁止产品/runtime新增模块、public symbol、依赖、配置、环境变量、registry、reflection、DSL、`getattr`、stage-name
分支、dynamic dispatch、type erasure、fallback 或兼容 alias。禁止合并 payload builder、修改第二个重复族、
顺手格式化整个 17K 文件或改变注释语义。T61A 允许 test-only `inspect.getsource(getattr(...))` 读取冻结
caller source；该 inspection 不进入产品/runtime，也不得被复用为生产派发。

## 4. Reduction Contract

| 合同 | 冻结值 |
|---|---|
| RC-01 | 13 个 loader + 12 个 ordinary caller label binding；仅保留 cleanup wrapper |
| RC-02 | legacy=403 physical / branch39；unit baseline=406 passed；clean spike product=`+48/-406`，proof=`+48` |
| RC-03 | product additions≤48；proof/test additions≤48；mechanical truth additions≤2；新增产品/测试文件=0；新 private helper≤1；public abstraction=0 |
| RC-04 | 同形 loader body `13→1`；terminal loader family≤44 LOC / branch≤4；产品净删≥358，切片下降≥88%；重复分支减少≥35 |
| RC-05 | product additions≤48≤`min(floor(403×15%),1000)=60`，buffer≥12；没有 shadow/selector 共存 |
| RC-06 | product48 + proof48 + truth≤2 = combined≤98≤`floor(406×25%)=101`，buffer≥3；路线历史保守 subtotal184 后累计≤282≤1,500 |
| RC-07 | 新文件=0；新 helper=33 LOC≤50；无公共抽象 |
| RC-09 | 任一行为差异、预算超限、无关格式化、动态机制、第二重复族或回退失败立即 NO-GO，保留 legacy |
| RC-10 | formal、RED、implementation、rollback/reapply、review、PR、fresh-main 各绑定 exact commit/tree、命令和 ledger |

删除不能抵扣 RC-06 additions。实现 diff 必须保持 product=`+≤48/-≥406`；proof/test=`+≤48`；允许的
机械 truth 标量最多两行。若 Ruff 或修复要求突破任一上限，不放宽预算，直接缩小或 NO-GO。

### 4.1 减重路线终局约束

WI217 是 WI196 减重专项最后一个 work item。当前 formal PR 完成后，最多只允许一个 implementation PR
和一个 closure PR；implementation 的修复与重审必须留在同一分支/PR，不得以第二个 PR 重启候选。若在
开 PR 前已确定 NO-GO，可以不创建 implementation PR；若 PR 已创建但未合并时确定 NO-GO，关闭该 PR 且
不合入产品，并直接进入唯一 closure PR。Closure 通常 records-only；唯一例外是 implementation 已合并后
detached fresh-main 验收失败，此时同一 closure PR 必须先把 reviewed product/proof blob 精确恢复为
pre-implementation baseline，再登记最终零产品净变化的 NO-GO，不得另开 rollback 或第二 implementation PR。

终止依据为路线级投入产出失衡：专项已接近7天且结束时间不可预测，持续消耗token、评审和CI资源并
阻塞正常特性开发；已合入产品raw净删653行约占初始产品基线0.61%，WI217即使GO累计1,011行也仅约
0.94%。减重必须与新特性均衡，不能以追逐RC-08取代AI-SDLC的产品演进。

Closure 不以 RC-08 达成为前提：GO 路径登记实际净删；NO-GO 路径登记最终产品净变化为零，并区分
pre-merge零产品合入或post-merge临时合入后exact rollback。两条路径都必须关闭
WI217 与 WI196 减重路线，把 RC-08 记为 `retired_unrealistic_composite_target`，并把 GAP-01/GAP-03～06
及 T62～T67 的剩余结构债转为非阻塞 backlog。Closure 后禁止创建新的减重 work item；正常特性开发
恢复，是否发布仍由独立正常发布流程决定，本路线不得顺带创建 tag、Release、PyPI 上传或全局 CLI 更新。

## 5. 兼容影响与 T61A/T61B

| 合同 | 影响与证明 |
|---|---|
| CC-01 | public Python/CLI surface 零变化；repository consumer scan 证明被删私有名称无运行时/测试消费者 |
| CC-02 | missing、read/YAML exception、non-mapping 的类型、顺序、exact path/error/exception text 零差异 |
| CC-03 | valid mapping identity、YAML key/list 顺序与 cleanup normalized warnings 零差异 |
| CC-04 | 不改 checkpoint/workitem/review/state machine；现有 ProgramService 全文件测试覆盖 |
| CC-05 | loader 仍只读；无 subprocess/network/额外写入；静态 diff 与既有测试证明 |
| CC-06 | relative/absolute path、UTF-8、invalid content 和 cleanup warnings 由参数化测试及既有测试冻结 |
| CC-07 | required Windows/macOS/Linux CI、wheel/sdist、clean-install/offline smoke 通过 |
| CC-08 | 无 public/interface/package-layout 变化，不新增 sibling 专用逻辑；安装产物 CLI smoke 代替重复 sibling harness |

T61A 必须先加入 48 raw LOC 以内的 proof，并在 legacy 上观察预期 RED：12 个 caller 尚未绑定 common
helper，common helper 尚不存在。proof 由两部分组成：

1. 一个 source-binding test 逐项断言12个 `ProgramService` caller 的 exact `artifact_label`；
2. 一个 persistent representative test 在legacy上调用provider-runtime loader，在candidate上调用common
   helper，并复用同一断言覆盖root外绝对路径下的missing、invalid YAML（含exact exception）、non-mapping、
   valid mapping与directory read failure五态。

cleanup 的 invalid exact path/error 与 warning normalization 复用现有六组测试，不新增平行 harness。Legacy
T61A 必须得到5个behavior GREEN +1个binding RED；candidate必须得到6/6 GREEN，完整ProgramService unit
应为412/412 GREEN。T61B还必须运行CLI integration、full suite、跨平台/安装包 smoke与disposable clone
rollback/reapply。

## 6. 允许与禁止文件

### Formal PR

允许：WI217 的 `spec.md/plan.md/tasks.md/task-execution-log.md` 四个已物化文档、WI196 五件套的最小状态
追加、`program-manifest.yaml`、project-state、root/scoped handoff，以及 manifest exact 两个机械计数。
WI217 `development-summary.md` 只注册 mapping、保持 `exists=false`，直至独立 closure；禁止预建空 summary
伪造完成。禁止 `src/**`、产品测试逻辑、workflow、依赖、版本、release。

### Implementation PR

产品/测试只允许：

- `src/ai_sdlc/core/program_service.py`
- `tests/unit/test_program_service.py`

另允许 WI196/WI217 非 summary records、manifest/truth、root/scoped handoff 和最多两行机械 inventory
expectation。implementation pre-close 继续保持唯一 WI217 summary missing；只有 closure PR 才创建 summary。
禁止其他产品/测试文件。整个路线最多创建一个 implementation PR；同一 PR 内可最小修复和重审，但不得
创建替代或补充 implementation PR。Closure 正常路径产品/行为测试零 diff；仅 §4.1 的 post-merge
fresh-main NO-GO 允许在同一 closure PR 对上述两个 product/proof 文件做 implementation diff 的精确逆变更，
不得夹带其他产品修改。

## 7. 功能需求

- **FR-217-001**：13 个 legacy 同形 loader body 必须收敛为一个私有 helper。
- **FR-217-002**：12 个普通 caller 必须显式绑定冻结 label；cleanup wrapper 与六个 caller 保留。
- **FR-217-003**：missing/invalid YAML/read failure/non-mapping/valid/outside-root path/cleanup warnings 的
  observable结果必须零未批准差异。
- **FR-217-004**：实现必须满足 RC-03～RC-07 的全部硬预算；不得以 formatter churn 或证明代码换取假净删。
- **FR-217-005**：formal 与 implementation 分离；每阶段 LEAN/SAFETY 必须审查同一 committed+clean identity。
- **FR-217-006**：implementation 必须完成 RED→GREEN、rollback/reapply、full/cross-platform/package/offline 验证。
- **FR-217-007**：WI217 是最后一个减重 work item；formal 后最多一个 implementation PR 和一个 closure PR，
  不得创建新的减重 work item。
- **FR-217-008**：任一差异或预算失败时回退整个 implementation commit，不保留 helper、测试或 claim 残留。
- **FR-217-009**：GO 或 NO-GO 都必须经唯一 closure PR 关闭 WI217/WI196，RC-08 以不现实组合终态退役，
  剩余结构债转为非阻塞 backlog，并恢复正常特性开发。

## 8. 成功标准

SC-217-001～005 是 implementation GO 门；任一未满足时 implementation 必须 NO-GO，但不阻断
SC-217-006 的唯一路线 closure。NO-GO 必须保留失败门的 exact evidence，不能把未运行写成通过。

- **SC-217-001**：product diff `+≤48/-≥406`、净删≥358；terminal loader family≤44 LOC/4 branch。
- **SC-217-002**：proof≤48、truth≤2、RC-06 combined≤98/101；无新模块、依赖、public abstraction。
- **SC-217-003**：6个新增pytest cases（其中binding case内部断言12对）、412个ProgramService unit、CLI
  integration、full suite、Ruff、治理、
  required CI、package/offline smoke 全绿。
- **SC-217-004**：独立 proof-red worktree 在 legacy + proof-only overlay 上取得5 behavior GREEN/1 binding
  RED；disposable clone revert只恢复exact baseline code/test blobs并取得406 baseline unit GREEN；reapply恢复
  candidate blobs并取得6 proof/412 unit GREEN。
- **SC-217-005**：LEAN/SAFETY 对 final exact HEAD/tree/formal-six 均 PASS0/findings=0；PR checks 全绿并完成
  detached fresh-main 验收。
- **SC-217-006**：GO 时只登记实际产品净删；NO-GO 时明确最终产品净变化为零并如实记录是否临时合入，
  不得伪造收益。两条路径的 closure
  均关闭 WI196、退役而非宣称达成 RC-08、把剩余结构债转为非阻塞 backlog，且不创建新减重 work item；
  post-merge fresh-main NO-GO 必须在该 closure 内先恢复 exact baseline product/proof blobs。

## 9. 回退

实现产品与 proof 作为一个原子 candidate commit；回退该 commit 同时恢复 13 个 legacy loader、12 个旧
callsite 和 406-test baseline。formal receipt 不强制 implementation GO；若 implementation 合并前 NO-GO，
只追加失败 receipt、关闭已开的单个 implementation PR且不合入产品，然后进入唯一 closure PR。若已合并
后 detached fresh-main NO-GO，唯一 closure PR 承担 exact product/proof rollback 与终局记录；两种情况都
不得保持路线 open、不得创建第二个 implementation/rollback PR或新的减重 work item，也不删除或改写历史 formal。
