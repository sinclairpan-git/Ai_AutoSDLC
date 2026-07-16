# 任务执行日志：Program 治理命令 IDE Adapter 副作用隔离

**功能编号**：`207-program-adapter-side-effect`
**创建日期**：2026-07-16
**当前状态**：formal authoring

## 1. 归档规则

- 本文件按批次追加事实，不把未执行计划写成已完成。
- 精确 Program Truth snapshot/hash 只以终态 `program-manifest.yaml` 为准，避免 authoring 自引用。
- 每批记录范围、命令、结果、findings、回退、branch/worktree disposition 和下一步。
- 产品/测试实现与当批 execution log/tasks 状态使用同一逻辑 commit；PR/merge/fresh-main 事实可在后续
  route writeback 批次追加。

## 2. Batch 2026-07-16-001：T11 只读根因分流

### 2.1 基线

- revision：`origin/main@506e950dee3469248ef7e6b5e1aac664668d18a1`
- worktree：`.worktrees/207-side-effect-diagnosis`，detached、初始 clean
- Python：`uv` 解析 CPython 3.11.15

### 2.2 Program adapter 复现

执行 `uv run ai-sdlc program validate`：

- exit=`0`，业务结果=`program validate: PASS`
- 额外输出=`IDE adapter (cursor): installed 1 file(s)`
- `.cursor/rules/ai-sdlc.mdc`：
  - before=`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`
  - after=`02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134`
- `.ai-sdlc/state/resume-pack.yaml` 与 canonical handoff SHA 不变。

随后执行 `uv run ai-sdlc verify constraints`：exit=`0`、`no BLOCKERs`；Cursor、resume-pack、handoff
SHA 均相对 verify 前不变。因此 verify 不是本次 Cursor mutation 来源。

### 2.3 Resume-pack 独立复现

执行 `uv run ai-sdlc status`：exit=`0`，输出 `resume-pack stale; rebuilding from checkpoint`；两份
resume-pack 被同步改写：

- constitution/tech-stack/spec/plan/tasks 从 repo-relative 变为当前 `.worktrees/...` 绝对路径；
- `current_branch: feature/206-model-string-dedupe-dev` 变为 `current_branch: ''`；
- `active_files` 变为空；
- `context_summary` 变为空。

调用链审计确认 program/verify 不调用 `load_resume_pack()`；status/recover/handoff update 才进入
continuity rebuild。因此本症状不属于 WI207。

### 2.4 分流决策

- GAP-12 / WI207：root `program` dispatch implicit adapter side effect + program test isolation，L1。
- GAP-13 / WI208：resume-pack portable/lossless canonical reconstruction source，L2。
- verify telemetry 潜在写入语义：另行登记，不混入 WI207/WI208。

Carver / `wi202_real_spike` 完成独立只读诊断，无文件修改；结论与本地复现一致。

## 3. Batch 2026-07-16-002：T12 canonical formal init

- docs branch：`feature/207-program-adapter-side-effect-docs`
- worktree：`.worktrees/207-program-adapter-side-effect`
- base：`origin/main@506e950d`
- 命令：`uv run ai-sdlc workitem init --wi-id 207-program-adapter-side-effect ...`
- 结果：创建 canonical `spec.md / plan.md / tasks.md / task-execution-log.md`，manifest 增加 WI207，
  `next_work_item_seq` 从 207 更新为 208。
- 已知副作用：workitem init 在当前基线通过既有 hook 刷新 `.cursor/rules/ai-sdlc.mdc`；该 tracked
  文件不属于 formal diff，terminal truth 后使用 `apply_patch` 精确恢复。

## 4. Batch 2026-07-16-003：T13 formal authoring

### 4.1 冻结边界

- 产品：`src/ai_sdlc/cli/main.py` 仅增加一个 `"program"` tuple member。
- 测试：`tests/integration/test_cli_program.py` 增加 autouse isolation 与 real-hook byte-stability。
- 非目标：`ide_adapter.py`、ProgramService/program handlers、resume-pack、verify telemetry。
- 预算：product additions≤1；test additions≤90；新产品/测试文件、函数、公共 API、依赖、config=0。

### 4.2 Formal 路线写回

- child 五件套已改为可执行合同，无 scaffold placeholder。
- 父项新增 GAP-12/GAP-13 和 T55/T56；WI208 在 WI207 fresh-main 后启动。
- WI206 的 PR/merge/fresh-main 关闭证据进入历史 log/summary；只标记其一个 T63 family
  `completed_reduction`，不关闭父路线。

### 4.3 下一步

1. root exact truth test 已按新增五件套把 inventory `1086→1091`、close `206→207`，不新增测试逻辑；
2. 同步 truth/continuity，并精确恢复 Cursor side effect；
3. 计算六文件 combined hash；
4. Pascal/Confucius 对同一 hash 对抗评审，直到双 PASS。

## 5. Batch 2026-07-16-004：T14/T21 truth 与静态门禁

- `program truth sync --execute --yes`：state ready、source inventory complete、unmapped=0、missing=0；
  精确 snapshot/hash/计数只以当前 `program-manifest.yaml` 为准。
- `program validate`：PASS；`program truth audit`：state ready、snapshot fresh、exit 0。
- `verify constraints`：no BLOCKERs。
- root exact truth node：`1 passed in 78.35s`；新增 WI207 五件套对应 inventory/close 计数已机械对齐。
- `git diff --check`：PASS；formal branch `src/**` product diff 为空；测试 diff 只含 root exact truth 两个
  值替换，无新增测试逻辑或行数。
- 已知 root hook 再次 materialize Cursor managed rule；已用 `apply_patch` 精确恢复 HEAD，
  `.cursor/rules/ai-sdlc.mdc` 不在工作树 diff。
- root/scoped resume-pack 已人工恢复 repo-relative path、active files 与当前 docs branch；这是 GAP-13
  修复前的已知 workaround，不冒充 WI208 产品修复。

T13、T14、T21 完成。下一步冻结 formal combined hash 并执行 T22/T23 对抗评审。

## 6. Batch 2026-07-16-005：T22/T23 Round 1 双 FAIL

- formal combined=`f74a06abb535785e114cadd6f0aca7582729029a677a1e4cc4d9e5753914de75`
- baseline HEAD=`506e950dee3469248ef7e6b5e1aac664668d18a1`；tree=
  `35fa6f37ad4334ed142dc8e8bad4b1d1c71ed06c`
- cached binary diff=`cf90cda7b7f97d342e608330d756c246fb17d926377693feeededa86809f748a`
- cached name-status=`a157355b9951d59a10480ce38cabfaacc0aa3f99ae01c516bd2fa2fc1d8a45cc`
- Pascal / 精简直接性=`FAIL`：父 FR-12/SC-04/tasks 与 root exact truth test 例外冲突；父 NC 矩阵
  漏 T55/T56；子 CC-01/02 映射错误且漏 CC-03；T56 对后续减重未形成任务硬依赖。
- Confucius / 兼容安全=`FAIL`：同意测试例外与 NC 矩阵 finding；另指出 handoff/resume Exact Next
  仍要求重复 truth sync，与“已完成、等待评审”状态矛盾。
- 双方均确认一行产品方案、autouse/real-hook 测试必要性、execute/显式 adapter 兼容与 WI207/WI208
  实现边界本身合理；评审期间未修改文件，起止 hashes/status 一致。

### 6.1 处置

1. 父 FR-12、SC-04、tasks 加入唯一 root exact truth 两值机械例外；
2. 父 §6.1/§6.3/追踪矩阵把 T55/T56 纳入 NC-01～NC-06 + impact CC、RC N/A；
3. 子合同拆正 CC-01 surface、CC-02 exit、CC-03 artifact/schema，并同步追踪；
4. 父 tasks 增加全局恢复门禁：T56 fresh-main 前不得启动任何新 T61/T62/T63～T67 实例；
5. continuity 记录 Round 1 FAIL；下一步改为修订、重跑门禁、恢复 Cursor、冻结新 hash、从零复审。

Round 1 verdict 已失效。T22/T23 评审动作完成但未通过；T24 进入修订中。

### 6.2 Round 1 findings 闭环与 Round 2 前置

- 父 FR-12/SC-04/tasks 已加入唯一 root exact truth 两值机械例外；
- 父 NC 非减重范围、§6.3 适用矩阵和追踪矩阵均已覆盖 T55/T56，RC 明确 N/A；
- 子合同已按父定义拆分 CC-01 surface、CC-02 exit、CC-03 artifact/schema；
- 父 tasks 已增加 T56 fresh-main 的全局恢复硬门禁；
- root/scoped handoff 与 resume-pack 已记录 Round 1 FAIL，不再要求恢复者重复旧 terminal sync。

修订后门禁：truth sync/validate/audit ready/fresh；constraints 无 BLOCKER；root exact truth node重新通过；
working/cached diff-check通过；Cursor rule精确恢复HEAD。下一步只冻结Round 2新hash并从零双审；若双PASS，
不再修改formal target，进入formal PR。

## 7. Batch 2026-07-16-006：T24 Round 2 双 FAIL 与顶层范围闭环

- Round 2 combined=`262d2613990f9b92e57e7777e95d97cef244f07e2ad22bd84029d672e089682d`
- cached binary=`aa59134598b473211d94ccc4cfb8f6c1146477ae696d9ab8cb4377a58116a599`
- Pascal=`FAIL`：父 tasks 顶层仍写“四件套”，与合法 staged 的 child/parent 五件套及 WI196/WI206/WI207
  development summary 冲突。
- Confucius=`FAIL`：父 spec 顶层仍说测试只能由后续 WI 修改，与 FR-12/SC-04 的 root exact truth 唯一
  例外冲突。
- 双方确认 Round 1 的 NC/CC、测试例外主体、T56 全局门禁和 continuity findings 已闭环；产品方案、
  测试设计、execute/adapter 兼容和 WI207/WI208 边界无其他 finding。

处置：父 spec 顶层明确引用 FR-12 唯一测试例外；父 tasks 顶层精确允许 current child/parent 五件套、
被关闭前项 execution/summary 与 truth/continuity。Round 2 verdict 作废；terminal sync/restore 后冻结
Round 3，新目标只做从零双审。
