# 功能规格：Resume-pack 可迁移、无损的 canonical reconstruction

**功能编号**：`208-resume-pack-portable-lossless-reconstruction`
**父项**：WI-196 `GAP-13 / T56`
**创建日期**：2026-07-17
**状态**：formal review pending
**风险**：L2；影响 CC-03、CC-06、CC-07；Reduction Contract 不适用

## 1. 背景与问题

`resume-pack.yaml` 是 checkpoint 的派生快照，不是第二恢复真值。当前实现虽能按 checkpoint fingerprint
识别 missing/corrupted/stale pack，但 `_build_resume_working_set_from_filesystem()` 把 spec、plan、tasks、
constitution、tech-stack 写成当前 worktree 的绝对路径；当 active linked WI 没有 optional
`runtime.yaml / working-set.yaml / latest-summary.md` 时，重建还会把 `current_branch`、`active_files`、
`context_summary` 清空。

在 fresh detached/relocated worktree 中，只要 work-item scoped pack 未被版本化，`status`、`recover` 或
`handoff update` 就会触发上述重建；root/scoped pack 虽重新相等，却不再 portable，也不再包含已经由
canonical continuity artifact 记录的上下文。这是 WI-196 GAP-13，不属于 WI-207 adapter dispatch 或
WI-209 comment-policy。

## 2. 范围

### 2.1 必须交付

- 让 `build_resume_pack()` 产生的所有仓库内部路径统一为 `/` 分隔的 repo-relative path。
- 为 `current_branch`、工作集路径、`active_files` 与 `context_summary` 冻结字段级 canonical source
  优先级；missing/corrupted/stale/mismatched pack 只能从这些来源重建。
- 让 `load_resume_pack()`、`status`、`recover` 与 `handoff update` 复用同一 builder；root/scoped pack
  始终同一内容、可恢复且第二次读取无写入。
- 兼容 attached branch、detached HEAD、复制/relocate 到不同 absolute root、POSIX/Windows path、旧的
  absolute optional artifact、root/scoped 缺失或不一致。
- 先以真实 RED characterization 固定当前缺陷，再实施最小修复并完成 focused/full/fresh-main 验收。

### 2.2 明确非目标

- 不改变 checkpoint schema、resume-pack schema、working-set/runtime schema、fingerprint 或 stage/batch
  语义。
- 不把 resume-pack 的旧字段提升为真值；stale/corrupted/mismatched pack 不得作为 overlay 或迁移来源。
- 不回退到历史 `checkpoint.feature` 的 docs/branch 来补 linked WI。
- 不修改 root adapter dispatch、IDE adapter、Program Truth、comment policy 或 verify telemetry。
- 不修改 public CLI 名称、参数、成功/失败退出码；不引入全仓 path abstraction、完整 Markdown parser 或
  新状态数据库。
- 本项是缺陷修复，不计 WI-196 RC-08 减重收益，也不宣称 WI-196、GAP-05 或 release 完成。

## 3. Canonical source 合同

checkpoint 继续是 active WI、checkpoint fingerprint、docs baseline 与 execute fallback 的权威锚点；
active-WI runtime 保留既有 stage/batch/task 优先级。resume-pack 始终可删除、可重建。其他 artifact 只为
各自字段提供 canonical context，不得反向覆盖 checkpoint 锚点。

| 字段 | 优先级（从高到低） | Fail-closed 规则 |
|---|---|---|
| stage/batch/last task | active WI `runtime.yaml` 的非空/已定义值；checkpoint/execute progress | 不读取旧 pack；保持既有 runtime 优先语义 |
| branch | linked WI：active runtime 非空 branch、eligible matching handoff Branch、否则空；无 linked WI：checkpoint feature branch | handoff 不得覆盖 no-linked feature branch；linked handoff Branch 必须通过下述资格检查，不得回退历史 feature branch |
| spec/plan/tasks | active WI `working-set.yaml` 中合法 portable 的非空值；active WI filesystem canonical docs | 不存在则对应字段为空；不得回退历史 WI |
| PRD/constitution/tech stack | 合法 portable working-set 值；当前 repo filesystem | repo 内部值必须 repo-relative；不可迁移 absolute 值不得原样传播 |
| active files | working-set 的非空 portable 列表；否则按当前 stage 的既有 `STAGE_FILES` 从真实存在的 canonical path fields 构造最小集合 | 只保留 repo-relative、去重、稳定顺序；不得把 Git dirty/Changed Files 当工作集 |
| context summary | active WI（linked 或 no-linked）匹配的 canonical handoff Goal/State/首个 Next；非空 latest-summary；working-set context | 按下述 wire grammar 重建；无来源时为空；不得复用 stale pack summary |

handoff 是 WI-182 已定义的 canonical continuity artifact。本项只把其中已经存在的 Work Item、Branch、
Goal、State、Exact Next Steps 用作字段级 fallback：context 对所有 active WI 可用，Branch 只对 linked WI
可用：

- canonical root handoff 的 Work Item 必须与 checkpoint active WI 完全一致；
- scoped handoff 存在时必须与 canonical root 内容一致；不一致时 handoff fallback 整体失效；
- handoff fallback 不改变 checkpoint freshness，也不成为 active files、stage/batch/docs baseline 的来源；
- linked handoff Branch 必须非空且不区分大小写地拒绝 `HEAD`/`none`；active linked WI 与 checkpoint
  feature id 不同时，还必须拒绝等于 `checkpoint.feature.current_branch` 的历史值。Branch 不合格只使
  branch fallback 失效，不阻止同一份合法 handoff 提供 context；
- 这是一项显式 WI-198 兼容迁移裁决：WI-198 的“linked 无 runtime branch 为空”收窄为“linked 无
  runtime 且无 eligible matching canonical handoff branch 时为空”，仍禁止历史 feature branch 泄漏。
- no-linked checkpoint 无论 handoff 是否匹配，都继续使用 feature branch；matching handoff 的 context
  必须保留，mismatching handoff 不得注入 context；
- wire grammar 固定为 WI-182 当前编码：字段值 `none` 与章节项 `- none` 都表示 absent；summary 只按
  `Goal: <goal>`、`State: <state>`、`Next: <首个非空 Exact Next Steps>` 的顺序取非空部分并以 ` | ` 连接；
  三项全空时精确为 `Continuity handoff updated`。literal `none` 不作为可编码业务值；
- handoff reader 必须区分 `available`、clean absent/not-applicable（文件不存在或 Work Item 不匹配）与
  `unreadable-or-invalid` 三态；root/scoped 的 `OSError`、无效 UTF-8、内容不一致、malformed/重复 Work
  Item/Branch/Goal/State/Exact Next Steps 字段或章节均属于第三态，而不是 clean absent；
- root/scoped pack 本来 fresh、只做 semantic 校验时遇到第三态，必须继承 WI-198 合同：直接返回原 pack，
  不写文件、不发 rebuild event；pack 本来 missing/corrupt/checkpoint-stale/root-scoped mismatch 时，忽略
  第三态 handoff，从 checkpoint、runtime、working-set、latest-summary 与 filesystem 安全重建。clean
  absent/not-applicable 则正常使用低优先级来源构造 expected pack；所有路径都不得新增 CLI 异常。

## 4. 路径与重建合同

- 新写入的 repo-internal path 必须是非空时无 drive、无 UNC、无前导 `/`、无 `..` escape 的 POSIX
  repo-relative 字符串。
- 当前 root 下的旧 absolute artifact 可确定性转为 relative；来自其他 root/drive、无法证明属于当前 repo
  的 absolute artifact 必须丢弃并从 filesystem/handoff 重建，不得截取可疑后缀猜测。
- 反斜杠 repo-relative 输入统一为 `/`；Windows drive/UNC absolute 输入不得在 POSIX relocation 中伪装为
  relative。
- root/scoped pack 任一 missing/corrupted/stale、两者模型或原始 bytes 不一致，或 semantic fields 与
  canonical builder 不一致时，均使用同一个 expected pack 覆盖两份；旧 pack 不提供字段。合法且
  model-equal 但 YAML key 顺序、引号或空白导致 raw bytes 不同时也必须收敛，不能只比较 `model_dump()`。
- semantic fields 至少比较 stage/batch/task、branch、`docs_baseline_ref/at`、六个 path 字段、active files
  与 context summary；timestamp 与 checkpoint metadata 按既有规则处理。
- optional artifact 只在 semantic-only freshness 检查中不可读时，保留 WI-198 的兼容合同：不把原本
  fresh 的 pack 新增为失败；若 checkpoint/root/scoped 本来已 invalid，继续既有 rebuild/error 路径。
- 两文件继续使用既有 staged replace，合同是 crash-convergent pair、不是跨文件原子 transaction：若
  scoped replace 成功而 root replace 失败，保留原异常并清理 staged 文件；下次 load 必须检测 mismatch、
  收敛两份，第三次 load 无写入。第二次正常 `status/recover` 不得再次写 pack 或改变 checkpoint。

## 5. 用户故事与验收

### US-01：relocated/detached status 保持上下文（P0）

作为在新 worktree/新机器继续任务的维护者，我希望 `status` 重建出的 pack 不含旧机器绝对路径，并保留
canonical branch、active files 与 context，以免恢复到空白现场。

**独立验收**：在源 root 写 checkpoint + matching handoff/optional artifact，迁移到不同 absolute root 并
detached checkout，删除/损坏 scoped pack 后执行 `status`；两份 pack 字节相等、路径全部 relative，四类
字段与 canonical sources 一致，checkpoint bytes 不变；第二次 status 无写入。

### US-02：recover 对 stale/corrupt/mismatch 一致自愈（P0）

作为恢复中断任务的用户，我希望所有损坏形态都进入同一个确定性重建器，而不是从任一旧 pack 拼字段。

**独立验收**：覆盖 root/scoped 的 missing、corrupted、checkpoint-stale、semantic-stale、模型不一致及
model-equal/raw-bytes-different；
`recover` 发出既有 rebuild 可观测事件，结果只等于 canonical expected pack，stage/batch/task/docs baseline 与
错误合同无未批准差异。

### US-03：handoff update 成为下一次重建的完整来源（P0）

作为长任务 agent，我希望更新 canonical/scoped handoff 后 pack 同步得到最新 context，以及 eligible linked
branch，并从 working-set 或 stage-required docs 得到 active files，之后 relocation/rebuild 仍能恢复这些字段。

**独立验收**：真实 Git fixture 在 attached branch 写 handoff，随后 detached/relocated 并强制 pack
rebuild；handoff 两份相等，pack 两份相等，context 与 eligible linked branch 不丢失；active files 来自
working-set 或 stage-required docs；active WI runtime 非空 branch 时仍优先于 handoff branch。no-linked
handoff update 后重建必须保持 feature branch/context，第二次 load 无写入。

### US-04：历史兼容与跨平台（P1）

作为现有使用者，我希望无 linked WI、linked optional artifact、Windows 路径和 unreadable optional
artifact 的既有成功/失败边界保持稳定。

**独立验收**：WI-198 全部 regression 继续通过；Windows drive/UNC/backslash fixture、partial docs、
external/escaping path、no-linked handoff、handoff missing/unreadable/malformed/duplicate、optional artifact
unreadable、linked attached/detached/GitError/historical-feature Branch、zero-option/partial handoff summary
均符合 §3～§4；handoff 第三态分别覆盖 fresh pack byte/no-event 与 invalid pack rebuild 两条路径。

## 6. 功能需求

- **FR-208-01**：checkpoint 必须继续是 active WI、fingerprint、docs baseline 与 execute fallback 的权威
  锚点；stage/batch/task 保持 active-WI runtime 优先，resume-pack 不得被读取为重建 overlay。
- **FR-208-02**：builder 必须实现 §3 单一字段优先级，四个入口不得各自补逻辑。
- **FR-208-03**：所有新写入 repo-internal path 必须满足 §4 portable contract。
- **FR-208-04**：matching canonical handoff 可补所有 active WI 的 context；只有 eligible Branch 可补 linked
  branch。handoff 不得决定 active files、stage、active WI 或 docs baseline；no-linked branch 不读取 handoff。
- **FR-208-05**：root/scoped missing/corrupt/stale/model mismatch/raw-byte mismatch 必须以 crash-convergent pair
  收敛到同一 expected pack。
- **FR-208-06**：fresh semantic mismatch 必须自愈；semantic-only optional-source 的
  `unreadable-or-invalid` 必须原 pack byte/no-event 返回，pack 本已 invalid 时 handoff 第三态不得阻止重建。
- **FR-208-07**：linked runtime branch 保持最高优先级；handoff Branch 不合格只禁用 branch、不丢
  context；无匹配 runtime/eligible handoff Branch 时 linked branch 继续 fail-closed 为空。
- **FR-208-08**：status/recover/handoff 的 CLI surface、退出码、event text 与 checkpoint mutation 合同不变。
- **FR-208-09**：实现只允许修改 `context/state.py` 与四个冻结测试文件；`core/handoff.py` 只回归。任何新
  public helper/module/schema 或第二个产品文件都必须停止并重新评审。
- **FR-208-10**：formal 与 final implementation 必须分别取得 Pascal/Confucius 对同一精确目标的双 PASS。
- **FR-208-11**：WI-207/PR #141 的 GAP-12 关闭证据必须先落盘；WI-209/GAP-14 继续独立 queued。
- **FR-208-12**：PR 合并后必须在 fresh detached main 复跑 relocation、focused、full、Ruff、constraints、
  truth 与 clean-state guard，才可关闭 GAP-13。

## 7. 非功能与精简合同

- **NC-01**：先红后绿；RED 必须失败于绝对路径或字段丢失，而非 fixture/解析错误。
- **NC-02**：一个 builder、一个 path normalizer、一个窄 handoff fallback reader；不得在 CLI handler 复制。
- **NC-03**：产品修改最多 1 个既有文件，净新增不超过 120 行；测试最多 4 个既有文件，净新增不超过
  240 行。超过任一预算先回到 design，不用压缩可读性硬凑。
- **NC-04**：不减少现有测试、断言、平台或错误分支；新增注释只解释 source priority、迁移和 fail-closed。
- **NC-05**：兼容差异只允许：repo-internal absolute→relative、matching handoff 补齐 context、linked
  eligible handoff 补齐 branch、缺 working-set active 时按 `STAGE_FILES` 构造最小 active set、stale semantic
  fields 被 expected 替换，以及 model-equal/raw-bytes-different root/scoped pack 首次收敛为同一 canonical
  expected serialization。byte-only repair 只可复用既有 stale/rebuilt event 文本并允许既有首次 rebuild
  timestamp 变化；不得改变其他模型字段、checkpoint 或 CLI/event 文本，第二次 load 不写入、不发 event。
- **NC-06**：实现 commit 可单独 revert；revert 后 tree 等于 formal baseline，reapply 后等于 candidate。

## 8. 成功标准

- **SC-208-01**：至少一个 relocation/detached test 在修复前稳定 RED，修复后 GREEN。
- **SC-208-02**：所有新生成 pack 的 repo-internal paths 均 relative 且 `/` 分隔；无旧 root/drive 泄漏。
- **SC-208-03**：所有 active WI 的 matching handoff context 与 eligible linked branch 重建前后相同；
  active files 来自 working-set 或 stage-required docs；无来源时 fail-closed，不从旧 pack/Git dirty set 补值。
- **SC-208-04**：root/scoped pack 的 raw bytes 一致；model-equal/bytes-different 也会首次 repair，第二次
  status/recover pack/checkpoint bytes 不变。
- **SC-208-05**：WI-198 unit/handoff/recover/status regression 与全量测试全部通过。
- **SC-208-06**：产品/测试 diff 满足 NC-03，Ruff、format、constraints、program validate/truth、diff-check 全绿。
- **SC-208-07**：Pascal/Confucius 对同一 formal hash 和同一 final tree 分别明确 PASS，无 actionable finding。
- **SC-208-08**：implementation PR 的 current-head Codex、required checks、merge 与 fresh-main acceptance 全绿。
- **SC-208-09**：父台账仅把 GAP-13/T56 标为关闭；GAP-14/T57 仍 queued，WI-196/RC-08/release 仍开放。

## 9. 停止与回退

出现以下任一情况立即停止：需要改 schema/fingerprint、信任 stale pack、回退历史 feature branch/docs、
新增 CLI 分支实现、修改第二个产品文件、无法区分 repo-internal/external absolute path、破坏 WI-198
unreadable optional artifact 合同或超出 NC-03。

formal PR 可整体 revert 文档提交；implementation 用单一逻辑 commit `git revert --no-edit <sha>` 回退。
回退后 GAP-13 重新打开，旧手工 `handoff update`/pack 恢复路径继续可用，不影响 WI-207 与 WI-209。
