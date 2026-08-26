# 任务执行日志：主线真值复位与轻量 ROI 合同

**功能编号**：`219-mainline-truth-roi-contract`
**创建日期**：2026-08-25
**状态**：execute authorized

## Batch 2026-08-25-001 | T11-T13

### 变更范围

- 从当前远端 `origin/main@762527466119dde127d7488b73d5592e44afaaa6` 创建独立 worktree；
- 通过 `workitem init` 生成 canonical formal docs，并同步 Program Truth 映射；
- 只改写 WI219 formal 文档与 root Program Manifest inventory 的两行机械断言，未修改产品 runtime 或特性
  测试实现。

### 基线命令与结果

- `uv run ai-sdlc handoff show`：成功，复现仍要求合并 PR 173 的陈旧 handoff；
- `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_handoff.py tests/unit/test_checkpoint_fr088.py tests/unit/test_handoff.py -q`：`63 passed in 38.46s`；
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`；
- `uv run ai-sdlc program truth sync --execute --yes`：完成 WI219 manifest 映射；
- `uv run ai-sdlc status --json`：复现 active WI204=`branch_only_implemented`、
  `BLOCK_CODE_PREPARE_TASKS`；Program Truth=`fresh`，release targets=`ready`。

### 决策

- 采用现有真值入口、定向 active binding 消费修正与模板提示方案；
- link WI219 后通过现场解析确认：checkpoint feature=WI204、linked=WI219、canonical active=WI219，但
  readiness binding/dir 与 execute active 均为 WI204；
- WI198 已冻结 linked-first 语义并明确拒绝 link 时改写历史 feature，因此根因是 readiness 与 execute
  authorization 各自直接读取 `checkpoint.feature`，不是 link 写入或 checkpoint schema 失效；
- 首轮候选允许一个无 I/O/持久化的共享 spec-dir helper，使 resume、readiness 与 execute 三个消费方复用
  active binding；该调用面和预算已由 Batch 002 的完整审计结果取代；
- 首轮候选以产品 30 LOC、测试 150 LOC 作为 re-review 信号；Batch 002 已按新增的 truth/status 证据重新估算，
  两组数字均不作脱离风险的机械门禁；
- 用户批准 formal 规格前不进入实现。

### Formal inventory RED

- `tests/integration/test_repo_program_manifest.py` 在旧主线 tuple `1142/1142/0/0` 上稳定 RED；实际 WI219
  formal inventory 为 `1147/1147/0/1`，close layer 为 `218/217`；其余 78 项通过。
- 历史 WI217 formal 提交采用相同 missing close 语义；因此只更新两个精确 tuple，不改完整性、unmapped、
  capability 或 release 断言。

## Batch 2026-08-25-002 | T14-T16 formal adversarial remediation

### 首轮合议与事实裁决

- 三席固定审阅 `76252746..b3665d7e`；自主性席经 WI198 证据纠偏后撤回 optional-link Critical 并
  `APPROVE`，硬边界席为 `APPROVE_WITH_CONDITIONS`，可落地性席为 `REJECT`；有效阻断不能由票数覆盖，
  主席裁决 `REJECT`。
- 真实 `workitem truth-check --wi specs/219-mainline-truth-roi-contract --rev HEAD` 复现
  `branch_only_implemented`、`Execute started=yes`、`Ahead/behind main=221/0` 与 close/merge action；本地
  `main@c0f333c8` 比 `origin/main@76252746` 落后 220 个提交。
- status 调用面审计确认 backlog breach guard 仍读取历史 feature；committed handoff 仍记录 `??` 与“提交已
  提交 identity”；adapter allowlist 无具体路径；双模板验收仅检查六项存在，均纳入 formal 整改。

### 整改决策

- 不通过移动本地 main、fetch、手写 status 或新增状态掩盖缺陷；truth baseline 仅在本地 default 落后已有
  origin ref 时只读使用 remote ref，其他场景保留本地 default。
- formal-only classification 使用精确 control-file allowlist，不解析 Markdown、不忽略任意 tests/config；
  任何范围外路径仍是 execution evidence。
- active binding 覆盖全部 status/execute/resume 子面，并以 valid/no-link/missing/partial/branch-stage/strict
  矩阵验收；Track B 比较 canonical semantic set，不新增 parser 或 runtime gate。
- 预计总投入调整为 2.5–4.5 人日；40–80/180–300 LOC 仅作 cost signal，越过冻结架构边界或缺少必要性
  证据才暂停。

### 下一步

- Formal required/forbidden 自审：0 missing、0 forbidden；`git diff --check` PASS；
- `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_handoff.py tests/unit/test_checkpoint_fr088.py tests/unit/test_handoff.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_repo_program_manifest.py -q`：
  `79 passed in 155.35s`；
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`；Ruff：`All checks passed`；
- 完成 formal 自审、Program Truth 同步、constraints/manifest 回归与 continuity refresh；
- 提交新 formal identity；
- 原三席对同一新 SHA 做 round 2，整改通过前不进入实现。

## Batch 2026-08-25-003 | T16-T20 approval and implementation planning

### Round 2 合议与用户授权

- 三席只读复审同一冻结区间
  `762527466119dde127d7488b73d5592e44afaaa6..a5fe086ebad132db096a2c159b37cf7f65d2a63f`；
  自主性/ROI、平衡 Lean、硬边界三席最终均为 `APPROVE`，无可操作 Critical/Important。
- 硬边界席最初提出 formal allowlist 的文件内内容风险；同 SHA 交叉质询确认 `formal_freeze_only` 仅是
  只读 truth 信号，不参与 execute/close/release 授权，且现有 audit/test/diff review 仍独立生效；该项降为
  advisory，不引入 YAML/hunk policy engine。
- 用户于 2026-08-25 明确回复“批准”，T17 完成，允许按 A0→A1→B 顺序进入产品/测试实现。

### 执行计划与基线

- 使用独立 linked worktree
  `/Users/sinclairpan/project/Ai_AutoSDLC/.worktrees/219-mainline-truth-roi-contract`；
  branch=`feature/219-mainline-truth-roi-contract-docs`，批准时 HEAD=`a5fe086e`，相对 origin/main ahead 3。
- 将批准后的实施拆为 A0 truth baseline/classification、A1 linked-first active binding、B 双模板 semantic set；
  每批先 RED、后最小 GREEN、独立 Go/No-Go 和提交。
- 批前基线：
  `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_handoff.py tests/unit/test_checkpoint_fr088.py tests/unit/test_handoff.py tests/unit/test_telemetry_readiness.py tests/unit/test_execute_authorization.py tests/integration/test_repo_program_manifest.py -q`
  得到 `79 passed in 173.39s`。
- 当前只完成 planning/approval 记录；尚未修改任何 Track A/B 产品或特性测试文件。下一步为 T20 A0 RED。

### 计划文档替换说明

- removed comment: `specs/219-mainline-truth-roi-contract/plan.md` `## 已冻结推荐方案`；用户批准后由 Task 1–3
  的逐步 RED/GREEN、接口和 Go/No-Go 合同完整替代。
- removed comment: `specs/219-mainline-truth-roi-contract/plan.md` `## 计划生成条件`；批准条件已满足，由当前
  plan 四个可执行 Task 及 `tasks.md` T20–T52 取代。
- 文件：`specs/219-mainline-truth-roi-contract/plan.md`。
- 删除的原说明标题：`## 已冻结推荐方案`，其摘要为“批准前只描述方案 B 的 behind-only、共享 helper 与
  双模板方向”；删除原因是用户批准后已由 Task 1–3 的逐步 RED/GREEN、接口和 Go/No-Go 合同完整替代。
- 删除的原说明标题：`## 计划生成条件`，其摘要为“用户批准后再生成 A0/A1/B 详细计划”；删除原因是该条件
  已于 2026-08-25 满足，并由当前 plan 的四个可执行 Task 及 `tasks.md` T20–T52 取代。
- 上述删除不移除行为边界；behind-only、单一纯 helper、双模板 semantic set、禁止新状态/parser/公共面和
  三批独立回退均在新计划中保留并细化。

## Batch 2026-08-25-004 | T20-T22 A0 truth baseline/classification

### RED

- 只修改 `tests/integration/test_cli_workitem_truth_check.py`，新增真实 Git fixtures：本地 main 落后已有
  origin/main、remote 缺失、本地领先、双方分叉、精确 formal control 集及四类范围外路径。
- 首次运行 `uv run pytest tests/integration/test_cli_workitem_truth_check.py -q` 得到
  `4 failed, 10 passed in 5.23s`；四个失败均为当前把 formal control 集判为
  `branch_only_implemented`，无 fixture/语法错误。

### GREEN 与 refactor

- `src/ai_sdlc/core/workitem_truth.py` 仅在本地 default 严格落后已有 origin/default 时选择 remote ref；
  remote 缺失、本地领先、分叉保持 local；只调用既有只读 GitClient 方法。
- 新增一个私有 exact-path helper；精确 formal control 集可判 `formal_freeze_only`，任一范围外源码、测试、
  配置或产品文档仍是 execution evidence；未新增状态、schema、参数或内容 parser。
- GREEN：`14 passed in 5.44s`；提取 test-only helper 去除重复后仍为 `14 passed in 5.66s`；Ruff PASS，
  `git diff --check` PASS。
- 真实 `workitem truth-check --wi specs/219-mainline-truth-roi-contract --rev HEAD --json` 在批准计划提交
  `e6567e63` 上返回 `formal_freeze_only`、`execution_started=false`、无远端主线历史 code paths、无 close/merge
  action。

### ROI / Go-No-Go

- 产品 diff：38 additions / 3 deletions；测试 diff 经去重后 161 additions；测试高于单批直觉值但覆盖四类
  Git 拓扑、ref 不变、精确 allowlist 和四类范围外证据，未出现 mock-only 或重复矩阵，保留为必要证明。
- 未修改 GitClient、writer、Runner、ProgramService、status schema/格式或 checkpoint schema；A0=`Go`。
- 独立提交：`3dbdd8a2 fix: align work item truth with remote main`。

## Batch 2026-08-25-005 | T30-T32 A1 linked-first active binding

### RED

- 在 `tests/unit/test_context_state.py`、`tests/unit/test_telemetry_readiness.py` 与
  `tests/unit/test_execute_authorization.py` 增加 valid/no-link/missing、branch-stage、main+close 和
  strict-load 消费矩阵；未修改 `tests/integration/test_cli_status.py`。
- 首次定向运行得到 `7 failed, 44 passed`；补入 missing-linked backlog fail-closed 用例后，失败面覆盖八个
  历史 feature 泄漏路径。失败均由 readiness/execute 仍直接读取 `checkpoint.feature` 导致。

### GREEN 与真实 CLI

- `src/ai_sdlc/context/state.py` 新增一个无 I/O 的 `active_work_item_spec_dir`；resume、readiness 与 execute
  统一复用 `active_work_item_id` / `active_work_item_spec_dir`，link 存在时不再静默回退历史 feature。
- 没有修改 checkpoint writer/schema、status 输出格式或 backlog guard 本体；missing linked directory 通过
  readiness 既有 `unavailable` 结果 fail-closed，legacy 无 link 行为保持不变。
- 三组 unit GREEN：`52 passed in 0.79s`；status CLI：`55 passed in 34.17s`；合并回归：
  `107 passed in 34.68s`；目标文件 Ruff 与 `git diff --check` 均 PASS。
- 真实 `uv run ai-sdlc status --json` 返回
  `branch_lifecycle.active_work_item=219-mainline-truth-roi-contract`、
  `workitem_diagnostics.active_work_item=219-mainline-truth-roi-contract`、
  `execute_authorization.active_work_item=219-mainline-truth-roi-contract` 与
  `execute_authorization.wi_path=specs/219-mainline-truth-roi-contract`；Program Truth 为 ready，
  `1147/1147` mapped、0 unmapped。

### ROI / Go-No-Go

- 产品 diff 为 53 additions / 13 deletions，净增 40；测试为 216 additions / 1 deletion。测试证明量高于原
  180–300 总体信号的剩余空间，但来自跨 resume/readiness/backlog/execute 与 branch-stage/main-close 的
  必要消费矩阵，没有新增运行时层、第二 resolver 或 mock-only 结论；因此不为追逐数字删减关键回归证据。
- 真实 status 暴露 `tasks.md` 原 checklist 不符合 executable-task parser 格式；补入 T31X/T40B 两个既有
  parser 合同任务后，`workitem guard` 返回 `ALLOW_CODE_WITH_TASK` 并绑定 T31X。该修复仅调整 WI219 治理
  文档，不扩展产品 parser。
- A1=`Go`；独立提交：`6d969546 fix: unify linked work item consumers`。Track B 必须保持仅双模板与两条真实
  生成路径的最小实现，避免继续放大测试/运行时表面。

## Batch 2026-08-25-006 | T40-T42 B 双模板 ROI semantic set

### RED

- 只在 `tests/unit/test_workitem_scaffold.py` 与 `tests/unit/test_doc_gen.py` 增加语义断言；分别走
  `WorkitemScaffolder.scaffold()` direct-formal 路径和 `DocScaffolder().render("spec.md.j2", context)`
  stage/native 路径，不读取模板源码作字符串代替。
- 首次定向运行得到 `2 failed, 30 passed in 0.59s`；两个失败都精确指向生成结果缺少六项提示、四个 decision、
  `not-applicable` 例外、risk-only 数值解释与 blocker 类别。

### GREEN 与 ROI

- 只修改 `templates/spec-template.md` 与 `src/ai_sdlc/templates/spec.md.j2`，加入同一份“ROI 与实现边界”提示；
  没有修改 `workitem_scaffold.py`、生成器、parser、constraint、model、Enum、持久化字段或公共 API。
- 文本明确允许微小事项用一行 `not-applicable`；`400/50`、辅助/核心比例与少调用方公共抽象仅是风险信号，
  不单独阻断；只有未经授权的范围扩展、缺失可执行证据或可复现安全/隐私/数据/兼容/回归问题可成为
  blocker。
- GREEN：`uv run pytest tests/unit/test_workitem_scaffold.py tests/unit/test_doc_gen.py
  tests/integration/test_cli_workitem_init.py -q` 得到 `51 passed in 8.11s`；两测试文件 Ruff 与
  `git diff --check` 均 PASS。
- 模板净增 30 行，测试净增 64 行；测试重复的是两条独立入口的同一 canonical semantic set，未增加运行时
  支撑层。B=`Go`；独立提交：`ffad821f docs: add lightweight ROI prompts to specs`。

## Batch 2026-08-25-007 | T50 unified verification and ROI review

### 当前 HEAD 新鲜验证

- focused：`172 passed in 47.30s`；覆盖 truth-check、context、readiness、execute authorization、status、
  direct-formal scaffold、stage/native render 与 workitem-init。
- full：`3349 passed, 3 skipped in 744.89s`；exit code 0。
- `uv run ruff check .`：`All checks passed`；`uv run ai-sdlc verify constraints`：`no BLOCKERs`；
  `git diff --check 762527466119dde127d7488b73d5592e44afaaa6..HEAD`：PASS。
- `uv run ai-sdlc program truth audit`：`ready/fresh`，`1147/1147` mapped、0 unmapped、1 missing；两个 release
  target ready。`program truth sync` 默认 dry-run 计算 snapshot hash `03bbc350...`，未产生文件变更；
  `tests/integration/test_repo_program_manifest.py` 为 `1 passed in 101.56s`，随后 audit 仍为 fresh。

### ROI / 瘦身裁决

- 相对批准计划提交 `e6567e63`，Track A 运行时代码净增 75 行：A0 truth baseline/classification 35 行，A1
  linked-first binding 40 行；Track B 两模板净增 30 行。产品/模板合计净增 105 行，高于 40–80 初始
  cost signal 25 行，但超出部分全部是两份用户可见模板提示，不是新的运行时支撑层。
- 定向测试净增 440 行，高于 180–300 signal；构成是 4 类 Git 拓扑、ref 不变、4 类 formal allowlist 越界、
  resume/readiness/backlog/execute 的 linked valid/missing/terminal 矩阵，以及 direct/stage 两条真实生成路径。
  审计未发现 mock-only 结论、第二 resolver 或可删除而不损失独立风险证明的重复矩阵。
- 冻结允许文件以外 0 项产品/测试修改；没有新增命令、依赖、writer、schema、status 格式、parser、constraint、
  Enum、持久化字段或治理生命周期。仅为追逐数字合并/删除 Git 拓扑、fail-closed 或双入口证明会降低回归
  防护，因此裁决为 `implement/retain`，并把测试规模作为后续变更不得继续扩面的风险基线。

## Batch 2026-08-25-008 | T52 exact-head read-only review

- 独立 reviewer 固定检查
  `762527466119dde127d7488b73d5592e44afaaa6..d02dbcc3fc8dd966a1dc91debf4a8976e3f56c95`；
  工作树 clean、远端 `main` 与冻结 base 仍为同一 SHA。
- verdict=`With fixes`，Critical=0，Important=3：rename-aware `git diff --name-only` 只暴露 allowlist 目标；
  未校验 linked ID 和 resolved containment 可读取仓库外目录；formal-only 在 execution log 已存在时仍声称其缺失。
- Minor=1：两测试文件复制同一 26 行 ROI assertion helper。复核确认前三项均有当前代码或真实 Git probe
  证据；进入 T53 定向整改，不 push、不创建 PR。
- 冻结整改边界：复用既有 GitClient 双向 changed-path 读取，不修改 GitClient；在 canonical active ID 与三个
  I/O 消费面 fail-closed，不修改 link writer/schema；修正文案不解析 execution log；Minor 只压缩重复断言，
  不新增共享运行时或越界 test helper 文件。

## Batch 2026-08-25-009 | T53 review remediation

### Important 1：rename 来源路径

- 真实 Git fixture 把 `src/feature.py` rename 到 allowlisted root manifest test；RED 为
  `1 failed, 14 deselected`，当前分类错误为 `formal_freeze_only`。
- GREEN 在 truth-check 内对既有 `GitClient.changed_paths(base,target)` 与反向结果去重并集；不修改 GitClient、
  不解析 name-status、不写 ref。truth-check 全文件 `15 passed in 6.89s`，rename 的旧/新路径均进入 inventory，
  分类为 `branch_only_implemented`。

### Important 2：linked path fail-closed

- RED 为 `3 failed, 3 passed`：POSIX traversal 未校验；readiness 对仓库外 symlink 抛 `ValueError`；execute
  把外部目录误判为 ready。resume 的同类用例因既有 portable-path 防护已通过。
- canonical `active_work_item_id` 现在拒绝 POSIX/Windows path segment 和 drive-relative 字符串；spec-dir helper
  对非法非空 link 返回空，不回退历史 feature。resume/readiness/execute 在 linked 场景下还独立要求 resolved
  path 同时位于仓库和仓库 `specs/` 下，防止 symlink escape。
- 三组 consumer unit GREEN：`55 passed in 0.82s`；无 link writer/schema/status format 修改。

### Important 3 与 Lean Minor

- 已有 execution-log formal fixture 的文案断言先 RED；detail 改为“changed paths limited to formal controls”，
  next action 只要求记录 implementation evidence，不再谎称 log 缺失。随 truth suite 一并 `15 passed`。
- 两真实模板入口保留独立 semantic assertions，但把每份 26 行重复 helper 压缩为 13 行精确语义锚点；未新增
  第三个 test helper 文件或运行时常量。模板/workitem-init 回归 `51 passed in 8.56s`，测试净删 16 行。

### ROI / 提交

- 本批运行时代码 51 additions / 21 deletions，净增 30；测试 110 additions / 35 deletions，净增 75。新增量
  对应两个已复现的 truth/fail-closed Important 和一项错误提示修复，没有新命令、依赖、parser、schema、
  state 或治理层；安全/兼容证明属于 ROI 合同允许超过一般支撑比例的必要例外。
- 目标 Ruff 与 `git diff --check` PASS；独立提交：`33fd1e50 fix: close WI219 review gaps`。

## Batch 2026-08-25-010 | T54 remediation re-review

- 同 reviewer 复核 `d02dbcc3..5447a153`：原 3 个 Important 均 closed，Lean Minor 的 in-place 压缩可接受；
  新发现 1 个 Important：resume containment 无条件要求 `root/specs`，破坏 no-link 非标准
  `feature.spec_dir`；另有 status 在 linked symlink unavailable 时丢失 active identity 的 Minor。
- 将既有 legacy 用例改为真实 `formal/nonstandard/{spec,plan,tasks}.md` 后稳定 RED；full status symlink
  assertion 也稳定复现 `active_work_item=None` 与错误原因。
- GREEN 只让 `root/specs` containment 适用于非空 link；no-link 继续接受仓库内历史非标准路径。readiness
  unavailable surface 保留 canonical linked ID，并统一 detail=`active work item directory is unavailable`；linked
  traversal/symlink 的 fail-closed 不回退。
- 定向 `3 passed`；context/readiness/execute unit `55 passed in 0.83s`；status CLI
  `55 passed in 38.20s`；目标 Ruff 与 diff-check PASS。
- 本批运行时代码净增 10 行，测试净增 25 行；不增加新 resolver、状态或格式字段。独立提交：
  `2b23c8c1 fix: preserve legacy resume paths`。下一步为新 exact HEAD focused/full 与最终复审。

## Batch 2026-08-25-011 | final exact-head verification

- 候选产品/测试/证据 HEAD=`a121b672a3cbbbe672dbcab05301100a65fa58c8`；GitHub
  `refs/heads/main` 仍为冻结 base `762527466119dde127d7488b73d5592e44afaaa6`，工作树 clean。
- focused：`176 passed in 49.79s`；full：`3353 passed, 3 skipped in 830.41s`；均 exit 0。
- `uv run ruff check .`：PASS；`uv run ai-sdlc verify constraints`：`no BLOCKERs`；full-range
  `git diff --check`：PASS。
- `uv run ai-sdlc program truth audit`：`ready/fresh`，`1147/1147` mapped、0 unmapped、1 missing，两个 release
  target ready；root manifest：`1 passed in 122.06s`。
- 以上为 second-review regression 后的新鲜证据；无需再重复 full verification，除非后续改动产品/测试内容或
  required check 报告新的可复现失败。下一步仅为 exact-head 最终 reviewer 与仓库 PR 协议。

## Batch 2026-08-26-012 | PR #175 Codex P2 remediation

- GitHub Codex 在 `66f60da976287058f1bcbba6b0f65793b45cf80d` 提出 2 个 P2：linked 目录可通过指向
  `specs/` 内另一 work item 的 symlink 保持 containment 却丢失 canonical identity；`main/master + close`
  下 linked 目录缺失会先进入 terminal-inactive 判定，从而隐藏损坏指针的 ID。
- 4 个最小回归先稳定 RED：execute 会对错误 work item 执行 truth-check，resume 会加载历史 formal docs，
  readiness 会返回错误 spec-dir，missing main-close 会返回 `(None, None)`；合计 `4 failed`。
- GREEN 只增加一个共享 canonical-identity 谓词，要求 resolved linked 目录精确等于
  `repo/specs/<linked-id>`；readiness 在 terminal-inactive 前先识别 linked target 缺失并保留 linked ID。
  execute/readiness/resume 共用同一身份约束；不新增 resolver、状态字段、schema、命令或依赖。
- 新回归 `4 passed in 0.58s`；扩大 checkpoint/resume/status/handoff/execute/manifest 回归
  `123 passed in 158.43s`；exact-tree full `3357 passed, 3 skipped in 880.47s`；全库 Ruff PASS；
  constraints=`no BLOCKERs`。

## Batch 2026-08-26-013 | PR #175 execution-history P2 remediation

- Codex 在 `4876ffc171fe2435162865ad41b8cd207f3f2193` 发现新的 P2：mainline/base 已有 scaffold
  `task-execution-log.md` 时，旧条件会以“日志存在且不在当前 diff”替代实施证据，把纯 formal revision 误判
  `mainline_merged`，并令 close-stage linked binding 错误 terminal-inactive。
- 两种真实 Git topology 先稳定 RED：已 merge 的纯 formal revision 与 base 已有日志、branch 只改 formal control
  均返回 `execution_started=True`；合计 `2 failed`。
- GREEN 新增两个窄的只读 Git 原语：沿 first-parent 枚举触及该 execution log 的提交，并读取单提交变更路径；
  普通/merge commit 复用双向 parent diff，root commit 使用 `diff-tree --root`。只有同一证据提交包含非 formal
  路径时才承认历史实施，不读取日志内容、不 fetch、不写 ref、不新增 parser/schema/state。
- 首轮扩大回归暴露 2 个 status fixture 仍把“仅日志”当实施，已改为 baseline 后在证据提交携带真实实现路径；
  随后的 full 暴露 root/fast-forward history 被跳过，补齐 root commit path inventory 后相关 `7 passed`。
- truth/status/readiness/GitClient/ProgramService 扩大回归 `532 passed in 80.59s`；final exact-tree full
  `3359 passed, 3 skipped in 861.35s`；全库 Ruff PASS；constraints=`no BLOCKERs`。
- 本批运行时代码净增 40 行、测试净增 48 行；投入对应 mainline、base-branch、merge、root、fast-forward 五类
  已复现 topology，未增加第二 truth classifier 或持久化面，ROI 裁决为保留。

## Batch 2026-08-26-014 | PR #175 root-bootstrap P2 remediation

- Codex 在 `1da23c513eb30344d43605ab74cb808a0244fec1` 发现 root-commit P2：scaffold work item
  若与 `README.md`、`pyproject.toml` 等普通 bootstrap 文件同处初始提交，root inventory 会把这些无关文件
  当成实施路径，再次误判 `mainline_merged`。
- 新增 root-bootstrap 真实 Git topology 后稳定 RED：`1 failed`，`execution_started=True`。
- root commit 现只接受明确实现载体前缀 `src/tests/governance/providers/kernel/scripts/templates`，并排除 formal
  allowlist；普通/merge commit 仍沿用既有非 formal 规则。GitClient 只增加 first-parent 查询，root diff 仍为只读；
  不解析日志、不增加持久化或第二 classifier。
- root formal/bootstrap、root implementation、merge、fast-forward 关键矩阵 `8 passed`；ProgramService/truth/status
  扩大回归 `533 passed in 73.66s`；final exact-tree full `3360 passed, 3 skipped in 728.74s`；全库 Ruff PASS；
  constraints=`no BLOCKERs`。
- 本批运行时代码净增 28 行、测试净增 12 行；以一个强证据 predicate 关闭误报，不扩展到文件内容、commit
  message 或语言后缀启发式，ROI 裁决为保留。

## Batch 2026-08-26-015 | PR #175 project-layout flexibility remediation

- Codex 在 `842b9befabb062d2d9f7ad4ef6cf6a9fdbc419ab` 指出新的 P2：root commit 的固定实现目录
  白名单会拒绝 `app/`、`lib/`、根级产品配置等合法项目布局，把框架的默认习惯错误升级为项目结构硬规则；
  这与 WI219 保留模型自主性、避免僵化治理的目标冲突。
- 新增 root arbitrary-layout topology：根提交只携带 `product-config.yaml` 与已填写的 execution log；旧实现稳定
  RED，四 topology 合计 `1 failed, 3 passed`。这证明问题来自固定目录假设，而非既有 merge/fast-forward
  规则。
- GREEN 删除全部实现目录白名单。root commit 现要求“至少一个非 formal changed path”与“同一提交中的
  execution log 已具备真实执行证据”同时成立；证据谓词与 close-check 共用既有三项语义 marker，并拒绝
  `YYYY-MM-DD-X`、`T0XX`、`待补充` 等未填写 scaffold token。目录、文件名、语言与后缀保持开放，也没有
  新增第二 parser、schema、状态或持久化面。
- target topology `5 passed in 3.58s`；close-check `71 passed in 14.73s`；truth/status/readiness/execute/
  GitClient/ProgramService 扩大回归 `639 passed in 91.81s`；final exact-tree full
  `3361 passed, 3 skipped in 730.42s`；全库 Ruff PASS；constraints=`no BLOCKERs`。
- Program Truth execute 写入 snapshot `84db6bf8...`；随后独立 audit=`ready/fresh`、`1147/1147` mapped、
  0 unmapped、两个 release target ready；root manifest test=`1 passed in 117.97s`。
- 相对上一候选，本批运行时代码 36 additions / 21 deletions，净增 15；测试 25 additions / 9 deletions，
  净增 16。新增投入只用于共享证据判定和四类 root truth 对抗矩阵；删除过度刚性的路径规则后，误报与漏报
  同时受约束，ROI 裁决为保留。

## Batch 2026-08-26-016 | PR #175 separate implementation/log P2 remediation

- Codex 在 `7a4869a5b1ecfcdb2f4ee91ca890a41d193bd6c0` 提出 P2：实现提交与 execution-log 更新分离并经
  rebase/fast-forward 进入 main 时，旧历史扫描只查看触及日志的提交，会漏掉两次日志更新之间的真实实现提交。
- 真实 Git topology 先稳定 RED：formal scaffold、根级 `product-config.yaml` 实现、已填写日志分别提交后，
  truth-check 返回 `execution_started=False/formal_freeze_only`；`1 failed, 19 deselected`。
- GREEN 保持窄窗口：先沿 first-parent 读取触及 execution log 的提交；同提交证据规则不变，仅在相邻两次日志
  更新之间读取双向 diff，并要求较新的日志通过共享 evidence predicate。未扫描从 WI 创建到当前的全部历史，
  未读取 commit message，也未新增路径/后缀白名单、GitClient API、parser、schema、状态或持久化面。
- truth-check 全文件 `20 passed in 8.09s`；truth/status/readiness/execute/GitClient/close/ProgramService 扩大
  回归 `640 passed in 89.02s`；final exact-tree full `3362 passed, 3 skipped in 703.17s`；全库 Ruff PASS；
  constraints=`no BLOCKERs`。
- Program Truth execute 写入 snapshot `1ab636ef...`；独立 audit=`ready/fresh`、`1147/1147` mapped、
  0 unmapped、两个 release target ready；root manifest test=`1 passed in 114.16s`。
- 本批运行时代码 22 additions / 1 deletion，净增 21；测试净增 13。投入只覆盖一个已复现且会错误保持已实施
  WI active 的 P2，并用“相邻日志区间”限制误归因半径；不把一次边界修复扩成通用历史推断引擎，ROI 裁决为保留。
