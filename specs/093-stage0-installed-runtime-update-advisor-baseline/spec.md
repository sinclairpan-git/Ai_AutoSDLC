# 功能规格：Stage 0 Installed Runtime Update Advisor Baseline

**功能编号**：`093-stage0-installed-runtime-update-advisor-baseline`  
**创建日期**：2026-04-11  
**状态**：formal baseline 已冻结；已完成两轮对抗收敛  
**输入**：[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../src/ai_sdlc/__init__.py`](../../src/ai_sdlc/__init__.py)、[`../../pyproject.toml`](../../pyproject.toml)

> 口径：`093` 是 Stage 0 supporting baseline，不是前端框架闭环本体。它服务于“零文档、低命令、CLI/IDE/AI 一致提醒”的使用体验，但不负责真正执行 CLI 自升级，也不授权项目依赖、provider、组件库的自动升级。

## 问题定义

当前仓库已经具备安装态版本信息读取能力，但没有一条正式冻结的 update advisor contract 来回答下面四个问题：

- 什么时候才算“已安装 CLI 运行态”，而不是 `uv run`、源码态、editable 态或宿主内置 runtime
- 谁可以联网检查 GitHub 最新 release，谁只能消费本地缓存
- CLI、IDE、AI 三个表面如何共享同一份 update truth，而不是各自实现一套提醒逻辑
- 如何避免把“GitHub 上游出了新 release”误报成“你当前安装渠道现在可升级”

如果这一层不先定死，后续想做“只要知道安装命令，后续都能在 CLI 或 AI 会话里得到清晰引导”的体验，会先在 update remind 这件小事上分叉成三套口径：

- 安装态和源码态混淆，导致开发者在 `uv run ai-sdlc ...` 下也被提示升级
- 离线或企业网络受限环境，每次启动都重复联网、重复提示失败
- IDE/AI 表面和 CLI 表面对同一 runtime 给出不同版本判断、不同提示强度、不同去重结果

因此 `093` 的目标是冻结一条最小但严格的 baseline：只解决 installed runtime update advisory 的 truth、refresh authority、shared cache、helper contract、notice contract 和 trigger boundary。

## 范围

- **覆盖**：
  - 已安装 CLI 运行态判定
  - GitHub stable release 检查与用户级缓存
  - `runtime_identity` 命名空间
  - CLI、IDE、AI 的 refresh authority / notify surface 边界
  - helper 的 machine-readable contract
  - light notice 与 actionable notice 的分层
  - freshness、backoff、去重、超时、不阻断规则
- **不覆盖**：
  - 真正执行升级命令、自更新或安装器改造
  - 项目内前端/后端依赖升级
  - provider、style pack、adapter、registry 的 runtime 安装
  - `uv run ai-sdlc ...`、`python -m ai_sdlc ...`、editable/source runtime 的在线检查

## 已锁定决策

- update advisor 只对“本机已安装 CLI 运行态”生效；源码态、editable 态、`uv run` 态全部 fail closed
- update advisor 是 advisory-only 能力；检查失败、超时、缓存损坏都不得阻断命令执行
- GitHub stable release 是 upstream truth，但不等于每个 install channel 的 channel truth
- installed CLI runtime 拥有 refresh authority；IDE/AI 表面不得直接联网，只能绑定本地 installed runtime helper
- 版本相关 notice 只允许基于 `fresh` 或“本次刚成功刷新”的数据发出；`stale` / `expired` 不得输出版本确定性结论
- notice 至少拆成两类：
  - `light_upstream_release_notice`：轻提醒，可跨 CLI/IDE/AI 复用
  - `actionable_cli_update_notice`：强提醒，只能由 CLI interactive surface 输出
- helper 是 machine truth 的唯一 owner；宿主不得自行推断 notice eligibility，也不得直接写缓存

## 运行时模型

### 1. RuntimeIdentity

`runtime_identity` 是 installed runtime 级别的稳定命名空间键，至少必须由以下维度构成：

- `ai-sdlc` executable realpath identity
- distribution/package install location identity
- detected install channel
- installed version source identity

仅靠版本号、PATH 字符串或项目路径都不足以构成合法的 `runtime_identity`。

### 2. FreshnessState

- `fresh`：距 `last_success_checked_at` 小于 24 小时
- `stale_but_usable`：距 `last_success_checked_at` 大于等于 24 小时且小于 7 天
- `expired`：距 `last_success_checked_at` 大于等于 7 天，或从未成功检查

`freshness` 只由最近一次成功检查时间决定；失败检查不会把缓存“刷新成 fresh”。

### 3. NoticeClass

- `light_upstream_release_notice`
  - 表示“GitHub 上游存在更新 release”
  - 不承诺当前安装渠道已经可升级
  - 可在 CLI、IDE、AI 表面展示
- `actionable_cli_update_notice`
  - 表示“当前安装渠道已知可升级，且精确升级指令已验证”
  - 只能在 CLI interactive surface 展示
- `check_failed_notice`
  - 表示“本次无法刷新 GitHub update state”
  - 只能在 CLI interactive surface 展示

## 用户故事与验收

### US-093-1

作为 **安装态 CLI 用户**，我希望只在“当前安装渠道确实可升级”时看到明确升级命令，这样我不会因为上游 release 已发布但当前安装渠道还未就绪而收到误导提示。

**验收**：

1. Given 当前 runtime 是 `github-archive` 安装态且缓存 fresh，When GitHub stable release 高于已装版本，Then CLI 可以输出 actionable update notice 和精确升级命令
2. Given 当前 runtime 是 `pipx`、`pip-user` 或 `unknown` 渠道，When GitHub stable release 高于已装版本，Then 系统只能输出 upstream release 轻提醒，不能宣称“当前已可升级”

### US-093-2

作为 **在 IDE 或 AI 会话里调用 AI-SDLC 约束的用户**，我希望也能知道本机安装态 CLI 是否有上游新版本，但不想在编辑器打开、线程启动、后台心跳时被反复打扰。

**验收**：

1. Given IDE/AI 表面能验证绑定到本地 installed runtime，When 实际发起一次 AI-SDLC 约束执行，Then 它可以消费同一份缓存并按 contract 输出轻提醒
2. Given IDE/AI 表面没有绑定到可验证的 installed runtime，When 发起 AI-SDLC 约束执行，Then 它不得猜测性提示更新
3. Given IDE/AI 表面只是打开会话、加载工具或执行非 SDLC 相关操作，When 未触发真正的 AI-SDLC 约束执行，Then 不得评估或展示 update advisor

### US-093-3

作为 **框架维护者或开发者**，我希望 `uv run`、源码态、editable 态继续保持安静，这样 update advisor 不会污染框架自迭代开发流。

**验收**：

1. Given 当前命令通过 `uv run ai-sdlc ...` 或 `python -m ai_sdlc ...` 运行，When 命令启动，Then 系统不得进行在线版本检查，也不得展示 update notice
2. Given 当前环境处于连续联网失败 backoff 窗口内，When 命令启动，Then 系统不得再次发起 GitHub refresh

## 功能需求

### FR-093-001 已安装运行态判定

只有同时满足以下条件时，`installed_runtime=true`：

- 版本来源来自真实安装分发元数据，而不是 fallback 常量
- 当前入口是本机已安装的 `ai-sdlc` CLI 或其 helper
- 当前运行方式不是 `uv run`、`python -m ai_sdlc`、editable/source runtime、或宿主内置 runtime

`src/ai_sdlc/__init__.py` 中的 fallback 版本字符串不得被视为 installed runtime 证据。

### FR-093-002 Stage 0 入口位置

installed CLI runtime 必须在全局 CLI 入口的 Stage 0 评估 update advisor，一次命令生命周期最多评估一次，且必须发生在具体子命令执行前。

补充约束：

- update advisor 不得改变子命令的退出码、成功状态或阶段推进
- `--help`、`--version`、shell completion、machine mode、非交互表面不得输出人类可见 notice

### FR-093-003 Refresh Authority 与 Notify Surface

- installed CLI runtime 拥有唯一的联网 refresh authority
- IDE/AI 表面只允许作为 notify surface 存在
- IDE/AI 表面不得直接访问 GitHub；如需刷新，只能委托与其绑定的 installed runtime helper
- helper 也必须服从与 CLI 相同的 freshness、backoff、timeout 约束

### FR-093-004 Surface Binding Contract

IDE/AI 表面将 `surface_binding -> runtime_identity` 的解析顺序固定为：

1. 宿主显式提供的 `ai-sdlc` installed executable path
2. 已持久化且仍可验证的 workspace/surface runtime binding
3. 宿主明确声明“其真实调用目标就是当前 PATH 解析到的 installed CLI entry”时，才允许绑定到该 PATH 解析目标
4. 以上均不满足时，绑定失败并禁用 update notice

补充约束：

- PATH 解析结果只能作为“可验证调用目标”的最后回退，不能作为猜测性来源
- 绑定验证必须通过 installed helper 的 `identity` machine output 完成
- 不允许回退到 `python -m ai_sdlc`、editable/source runtime、或任何只凭版本字符串推断的目标

### FR-093-005 Helper Machine Contract

helper 必须提供固定 machine contract，至少包含以下 verb：

- `identity`
- `evaluate`
- `ack-notice`

宿主只能依赖 helper 的 machine output，不得自行用版本比较或缓存文件推断 notice eligibility。

#### `identity` 输出

`identity` 必须返回稳定 JSON，至少包含：

- `protocol_version`
- `installed_runtime`
- `binding_verified`
- `runtime_identity`
- `installed_version`
- `install_channel`
- `executable_path`

#### `evaluate` 输出

`evaluate` 必须返回稳定 JSON，至少包含：

- `protocol_version`
- `runtime_identity`
- `installed_runtime`
- `freshness`
- `refresh_attempted`
- `refresh_result`
- `last_success_checked_at`
- `failure_backoff_until`
- `upstream_latest_version`
- `channel_latest_version`
- `release_url`
- `eligible_notice_classes`
- `reason_code`

其中：

- `refresh_result` 枚举至少包括：`not_needed`、`success`、`backoff`、`network_error`、`parse_error`、`timeout`、`disabled`
- `eligible_notice_classes` 只能由 helper 计算，宿主不得自行补算
- `reason_code` 必须覆盖“绑定失败”“缓存过期”“渠道不可判定”“帮助器不可用”等宿主需要区分的分支

#### `ack-notice` 输出

宿主在真实展示 notice 后，必须调用 `ack-notice`，由 helper 以并发安全方式写回 notice state。其输出至少包含：

- `protocol_version`
- `runtime_identity`
- `notice_class`
- `notice_version`
- `ack_recorded`

`ack-notice` 失败不得阻断主流程，但宿主不得绕过 helper 直接写缓存文件。

### FR-093-006 Upstream Truth 与 Channel Truth

- GitHub stable release 是唯一的 upstream truth
- draft release 与 prerelease 不进入 v1 判定
- 版本比较必须做 semver normalization，并允许剥离 `v` 前缀
- `channel_latest_version` 与 `upstream_latest_version` 是两个不同字段
- v1 中仅 `github-archive` 允许把 `channel_latest_version` 直接视为 GitHub stable release
- `pipx`、`pip-user`、`unknown` 渠道在没有可靠 channel latest source 之前，`channel_latest_version` 必须为 `null`

### FR-093-007 Notice Eligibility 与提示强度

notice eligibility 必须按 notice class 分开判定：

- `light_upstream_release_notice`
  - 只要求 `fresh` 数据且 `upstream_latest_version > installed_version`
  - 文案必须表述为“检测到 GitHub 上游新 release”，不得表述为“当前安装渠道已可升级”
- `actionable_cli_update_notice`
  - 必须满足 `fresh` 数据
  - 必须满足 `channel_latest_version > installed_version`
  - 必须存在已验证的精确升级指令
  - 只能在 CLI interactive surface 输出
- `check_failed_notice`
  - 只在 CLI interactive surface 输出
  - 只说明“本次无法刷新 update state”，不得阻断命令

`light_upstream_release_notice` 与 `actionable_cli_update_notice` 必须独立去重；轻提醒不得压掉后续 CLI 的强提醒。

### FR-093-008 缓存命名空间与 Schema

缓存必须放在用户级目录，但按 `runtime_identity` 分 namespace。单个 namespace 的 schema 至少包含：

- `schema_version`
- `runtime_identity`
- `installed_version`
- `install_channel`
- `upstream_latest_version`
- `channel_latest_version`
- `release_url`
- `last_checked_at`
- `last_success_checked_at`
- `last_check_status`
- `failure_count`
- `failure_backoff_until`
- `notice_state`

其中 `notice_state` 至少要能分别记录：

- `light_upstream_release_notice`
- `actionable_cli_update_notice`
- `check_failed_notice`

每个 notice class 至少应记录最近一次展示时间和关联版本或原因。

### FR-093-009 缓存并发一致性

同一 `runtime_identity` 的缓存更新，除原子写之外，还必须满足并发一致性约束：

- 必须使用文件锁，或等价的 compare-and-swap/read-merge-write 策略
- `last_checked_at`、`last_success_checked_at`、notice timestamps 必须保留时间更晚的值
- `failure_count` 必须单调不减；`failure_backoff_until` 必须单调向后推进，除非发生成功 refresh
- 旧的 notice ack 不得覆盖新的 notice state
- 文件损坏、未知 schema 或不可安全合并时，可以静默丢弃该 namespace 并重建，但不得阻断主流程

### FR-093-010 Freshness 状态机

`freshness` 的判定规则如下：

- `fresh`：`now - last_success_checked_at < 24h`
- `stale_but_usable`：`24h <= now - last_success_checked_at < 7d`
- `expired`：`now - last_success_checked_at >= 7d` 或从未成功刷新

迁移规则如下：

- 成功 refresh 立即进入 `fresh`
- 时间自然流逝可从 `fresh -> stale_but_usable -> expired`
- 失败 refresh 只更新失败字段，不改变 `last_success_checked_at`
- `stale_but_usable` / `expired` 不得直接输出版本确定性结论，除非本次刚刚成功 refresh

### FR-093-011 Failure Backoff

任何 refresh 尝试前，helper 或 CLI runtime 都必须先检查：

- 当前 runtime 是否具备 refresh authority
- 当前缓存是否非 `fresh`
- `now >= failure_backoff_until`

只有三者同时满足时，才允许联网 refresh。否则必须 cache-only。

退避窗口固定为：

- 第一次连续失败后：24 小时
- 第二次连续失败后：72 小时
- 第三次及以上连续失败后：7 天封顶

只有成功 refresh 才能清零 `failure_count` 并移除 backoff。

### FR-093-012 Trigger Boundary

CLI、IDE、AI 三个表面的触发边界必须固定：

- CLI：仅 installed runtime 的真实命令调用入口可以评估 advisor
- IDE/AI：仅在“实际发起一次 AI-SDLC 约束执行”这一事件上评估 advisor
- IDE/AI 不得在编辑器启动、会话打开、后台心跳、工具列表刷新、非约束型普通聊天时评估 advisor
- 源码态、editable 态、`uv run`、`python -m` 不得评估 advisor

### FR-093-013 输出与文案边界

- CLI interactive notice 必须提供清晰下一步，但不得要求用户查外部文档
- CLI interactive notice 的确认提示、阻断原因、下一步命令、恢复建议必须采用“中文主句 + 精简英文辅句”的双语输出
- 若输出升级指令，只能输出与当前 notice class 一致的指令级别
- `light_upstream_release_notice` 只能提供“查看 release / 使用渠道自有升级方式”的轻建议
- `actionable_cli_update_notice` 才能输出精确升级命令
- 文案必须显式区分“上游新 release”与“当前渠道可升级”

### FR-093-014 全局禁用与静默

必须存在全局 `disable_update_check` 类配置，命中后：

- 所有表面都不得刷新
- 所有表面都不得输出 update notice 或 failure notice
- 主流程继续执行

### FR-093-015 延迟预算与不阻断

- installed CLI 的单次 refresh 尝试总预算不得超过 1.5 秒
- IDE/AI 等待 helper 的预算不得超过 800 毫秒
- backoff 命中、helper 不可用、网络失败、解析失败、超时、缓存损坏都必须立即降级为非阻断路径
- update advisor 的任何结果都不得改变主任务退出码或任务状态

## 成功标准

- **SC-093-001**：`github-archive` 安装态用户在 CLI 中只会收到真实可执行的强升级提示，不会把 GitHub 上游更新误解成当前渠道已可升级
- **SC-093-002**：IDE/AI 表面在真正调用 AI-SDLC 约束时，可以基于同一 `runtime_identity` 给出轻提醒，但不会抑制后续 CLI 的强提醒
- **SC-093-003**：`uv run`、源码态、editable 态、`python -m` 均不会触发在线检查或版本提醒
- **SC-093-004**：连续联网失败环境不会在每次启动时重复发起 GitHub refresh
- **SC-093-005**：`stale_but_usable` 或 `expired` 缓存不会输出“当前有新版可升”的确定性结论
- **SC-093-006**：宿主侧实现只需遵循 helper machine contract，不需要各自维护一套版本判断逻辑

## 两轮对抗收敛

第 1 轮对抗补掉了三个实现漂移风险：

- 失败退避不再只管提示，也硬性约束 refresh 尝试资格
- 共享缓存不再只要求原子写，而是明确要求并发一致性合同
- IDE/AI 不再允许靠 PATH 猜测 runtime，必须绑定到可验证的真实调用目标

第 2 轮对抗补掉了四个产品语义风险：

- 把“GitHub 上游有新 release”和“当前安装渠道已可升级”彻底拆开
- helper 从概念接口收紧为 machine contract，避免 CLI/IDE/AI 各自实现一套判定逻辑
- 轻提醒和强提醒拆成不同 notice class，避免弱提示压掉 CLI 的强提示
- IDE/AI 的触发时机被收紧到“真实 AI-SDLC 约束执行”事件，避免宿主噪音分叉

---
related_doc:
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "src/ai_sdlc/cli/main.py"
  - "src/ai_sdlc/__init__.py"
update_advisor_scope: "installed_runtime_only"
update_advisor_status: "formal_baseline"
---
