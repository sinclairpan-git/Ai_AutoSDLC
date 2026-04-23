# 设计稿：Frontend Visual Regression Drift First Slice

**日期**：2026-04-23  
**状态**：draft  
**目标**：把当前已存在的 browser gate 截图变成可执行、可阻断、可追踪的视觉回归证据，并且在缺少新依赖时自动完成 workspace bootstrap，保证自动化测试可以在干净环境中继续跑下去。

**备注**：本文件仅作为 design reference；正式 work item 已迁移到 [`specs/178-frontend-visual-regression-drift-baseline/spec.md`](../../../specs/178-frontend-visual-regression-drift-baseline/spec.md)。

## 背景

当前仓库已经具备三类相关能力：

- `browser-gate-probe` 可以稳定产出 `navigation-screenshot.png`
- `frontend-visual-a11y-evidence.json` 已经在做结构、对比度、焦点、运行错误等启发式检查
- `governance/frontend/quality-platform/evidence-platform.yaml` 已经预留了 `visual-regression-evidence` 合同，要求的 payload 字段就是 `screenshot_ref` 和 `diff_ratio`

现在缺的是把“截图存在”升级成“截图和基线比较后才算证据完整”。没有这一步，现有 browser gate 还是偏向启发式检查，不能真正证明 UI 没有发生肉眼可见的回归。

## 设计结论

我建议把这件事做成一个独立的 `visual-regression` 证据 lane，而不是继续往 `frontend-visual-a11y-evidence.json` 里堆更多启发式规则。

原因很直接：

- 截图 diff 是客观的，最适合做第一层自动视觉回归
- 当前仓库已经有 `visual-regression-evidence` 的质量平台合同，可以直接接
- keyboard traversal 和审美启发式都更容易误报，不适合先做成阻断门禁

## 范围

### 这次要做

- 新增一个视觉回归证据文件，和现有 a11y 证据分开
- 在 browser gate runtime 中比较当前截图和 repo-pinned baseline
- 产出 diff 图、diff ratio、baseline ref、阈值和 verdict
- 当缺少 diff 依赖时自动安装，不把问题留给用户手工处理
- 让 `visual_verdict` 由视觉回归结果驱动

### 这次不做

- 不做 keyboard tab 顺序的完整验证
- 不做主观审美评分
- 不做多浏览器矩阵
- 不做完整 WCAG 平台
- 不把 baseline 自动覆盖成“最新截图”

## 推荐架构

### 1. 新证据文件

新增一个 spec-scoped 证据文件：

- `specs/<spec>/frontend-visual-regression-evidence.json`

它和当前的 `frontend-visual-a11y-evidence.json` 并列，但用途不同：

- a11y 文件继续放结构、labels、contrast、focus、runtime error 这类启发式信号
- visual-regression 文件只负责 screenshot diff 的真值

建议的 artifact 结构保持和现有证据文件一致：

- `schema_version`
- `provenance`
- `freshness`
- `evaluations`

新增的核心 evaluation 至少要有：

- `auto-visual-regression-drift`

其中 `quality_hint` 里写清楚：

- `baseline_ref`
- `current_screenshot_ref`
- `diff_image_ref`
- `diff_ratio`
- `threshold`

对应的运行时比较逻辑使用的 node 依赖要显式进入 `managed/frontend/package.json` 和 `managed/frontend/package-lock.json`，这样 `npm ci` 才能在干净环境里自动装起来。

### 2. Baseline 存放

baseline 不放在临时目录，不放在 `.ai-sdlc/artifacts`，而是放进 repo 的治理区，作为显式、可 review 的基线资产。

建议路径：

- `governance/frontend/quality-platform/evidence/visual-regression/<profile>/baseline.png`
- `governance/frontend/quality-platform/evidence/visual-regression/<profile>/baseline.yaml`

`baseline.yaml` 的最小字段建议包括：

- `profile_id`
- `delivery_entry_id`
- `browser_id`
- `viewport_id`
- `threshold`
- `blessed_at`
- `source_screenshot_ref`
- `source_digest`

其中 `<profile>` 初版先固定为单一 profile，键值建议由以下信息组成：

- `delivery_entry_id`
- `browser_id`
- `viewport_id`

第一阶段只支持一个 profile 没问题，先把闭环打通再扩矩阵。

### 3. Diff 产物

运行时产物放在 `.ai-sdlc` 下，避免污染仓库：

- `.ai-sdlc/artifacts/frontend-browser-gate/<gate_run_id>/visual-regression/diff.png`
- `.ai-sdlc/evidence/frontend-browser-gate/<gate_run_id>/visual-regression.yaml`

其中：

- `diff.png` 用于人工 review
- `visual-regression.yaml` 用于机器消费和追踪

### 4. Browser gate 接口

`BrowserQualityBundleMaterializationInput` 现有的 `visual_verdict` 字段继续保留，但它的来源改成视觉回归结果，而不是只看启发式截图观察。

`basic_a11y` 继续消费现有的 a11y 证据文件，不和视觉回归混在一起。

这样做的好处是：

- bundle 里仍然只有一个视觉 verdict 槽
- a11y 和 visual regression 的责任边界清晰
- 未来如果要加更多视觉层级，只需要再扩 contract，不会污染当前检查面

## Runtime Flow

### Step 1. 运行前预检

browser gate 启动时先检查 `managed/frontend` 的运行时依赖是否齐全。

如果缺少视觉回归所需的 node 模块，自动执行 workspace bootstrap：

- 在 `managed/frontend` 目录里安装缺失依赖
- 优先使用 lockfile 驱动的确定性安装
- 安装后重新解析模块，再继续 probe

这一层的原则是：

- 缺依赖时自动装
- 安装成功后继续跑
- 安装失败才终止

这条是硬要求，因为没有依赖就无法完成自动测试，不能把失败责任甩给用户。

### Step 2. 固定执行视口

为了让 diff 稳定，runner 必须使用固定的浏览器 profile：

- 单一浏览器：`chromium`
- 单一视口：先固定一个 desktop profile
- 不依赖随机窗口大小
- 不依赖动画完成时机以外的人工操作

如果后面要扩矩阵，再按 `browser_id + viewport_id` 扩 profile，不在第一刀里搞多维矩阵。

### Step 3. 取基线并比较

runner 在当前 gate run 下抓取 live screenshot，然后：

- 读取对应 profile 的 baseline
- 用轻量 PNG diff 库计算差异
- 产出 `diff_ratio`
- 产出 `diff.png`

比较规则建议如下：

- baseline 缺失 -> `evidence_missing`
- diff 依赖安装失败 -> `transient_run_failure`
- diff ratio 超过阈值 -> `actual_quality_blocker`
- diff ratio 在可接受噪声内 -> `pass`

第一版不建议做“主观审美 advisory”分层，先把回归信号做实。

### Step 4. 写回证据

browser gate runtime 把结果写回两个地方：

- spec-scoped regression evidence 文件
- `.ai-sdlc` 下的运行时 diff 产物

最终 `program status` 和 bundle 只消费结构化 verdict，不直接依赖人眼去看截图。

## 依赖自动安装

这部分是用户明确要求的，不留人工操作口子。

### 需要自动安装的东西

第一阶段只安装视觉回归 diff 所需的最小 node 依赖，建议是：

- `pixelmatch`
- `pngjs`

它们和 Playwright 一样从 `managed/frontend` 这个 workspace 解析，不从 repo root 解析。

### 安装策略

建议的策略是：

1. 先尝试 `managed/frontend/node_modules` 的模块解析
2. 如果模块不存在，自动执行 `npm ci` 或等价的 lockfile 驱动安装
3. 安装后重新解析并继续运行
4. 如果安装仍失败，才把结果分类为 `transient_run_failure`

### 为什么要这样做

因为视觉自动化不是单纯的“写个脚本就结束”，它需要：

- runner 可执行
- diff 库可解析
- baseline 可比较

只要缺一项，自动化测试就跑不通。这个失败必须由框架自己补齐，而不是让用户去猜 npm 装什么。

## 阈值与失败语义

建议采用单一硬阈值，先别搞复杂评分：

- `diff_ratio <= threshold` -> `pass`
- `diff_ratio > threshold` -> `actual_quality_blocker`

`threshold` 建议从 baseline metadata 里读取，初版保持保守，不要把噪声误判成回归。

### 失败分类

- `evidence_missing`
  - baseline 不存在
  - 当前 screenshot 缺失
  - 关键 profile 无法解析
- `transient_run_failure`
  - diff 依赖安装失败
  - 浏览器或 runner 在比较前崩溃
- `actual_quality_blocker`
  - diff ratio 超阈值
  - 视觉差异是确定性的、可复现的

## 基线刷新方式

baseline 不能自动覆盖，必须由 trusted maintainer 显式 blessing。

建议流程：

1. 先跑一轮 browser gate，确认当前截图是可接受的
2. 人工 review 截图和 diff 结果
3. 用一个明确的 bless 动作把当前截图提升为 baseline
4. 后续运行只比较，不自动改 baseline

这样可以避免“测试系统自己把自己改成通过”。

## 测试策略

### 单测

要补的测试至少包括：

- baseline 路径解析正确
- baseline 缺失时返回 `evidence_missing`
- diff ratio 超阈值时返回 `actual_quality_blocker`
- diff 依赖缺失时触发自动安装逻辑
- 安装失败时返回 `transient_run_failure`

### 集成测

要补一条真实链路测：

- `python -m ai_sdlc run --dry-run`
- `python -m ai_sdlc program browser-gate-probe --execute`

通过后应能看到：

- 视觉回归证据文件已 materialize
- diff 产物可追踪
- `visual_verdict` 进入 bundle

### 回归测

要再加一条“坏截图”场景：

- 改一个明显布局或文本
- 断言 diff ratio 上升
- 断言 verdict 变成 blocker

## 为什么不先做另外两条

- keyboard traversal 太容易被 composite widget、roving tabindex、overlay 打爆
- aesthetic heuristics 太主观，短期只会放大噪声
- screenshot diff 是当前最客观、最可复现、最容易 review 的第一步

## 成功标准

这件事做到位以后，应该满足下面几条：

- 用户不需要手工装新的 diff 依赖
- 浏览器 gate 可以自动完成比较
- baseline 缺失、安装失败、真实回归三类问题能被清楚区分
- 当前截图不再只是“留痕”，而是能直接阻断不合格的视觉变更
- 这条能力和现有 a11y heuristic 互不抢职责
