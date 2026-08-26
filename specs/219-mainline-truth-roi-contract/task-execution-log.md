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
