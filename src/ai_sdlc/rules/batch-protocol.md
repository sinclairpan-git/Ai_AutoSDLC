# 批次执行协议

> 本规则在 EXECUTE 阶段的每个批次中激活，定义预读、执行、归档、提交的固定步骤。
> 当检测到 Parallel Groups（`[PA]` 标记）且多 Agent 支持时，切换为并行执行模式（详见 `rules/multi-agent.md`）。

## 批次划分规则

1. 按 tasks.md 中的 Phase 分批：每个 Phase = 一个批次
2. 如果单个 Phase 任务数 > 12，拆分为子批次（每个子批次 6-12 个任务）
3. 如果 Phase 中有"测试任务 + 实现任务"的 TDD 结构，先执行测试子批次再执行实现子批次

## 每批次固定流程

### Step 1：预读（Mandatory）

每个批次开始前必须阅读以下文件：

```
必读：
  - PRD（原始需求文档）
  - .ai-sdlc/memory/constitution.md（项目宪章）
  - 当前批次所属 Phase 对应的 spec 文档章节
  
条件读：
  - 如果本批次涉及外部集成 → 读取对接文档
  - 如果本批次涉及数据库 → 读取 data-model.md
  - 如果本批次涉及 API → 读取 contracts/
```

预读完成后在 execution-log 中记录预读范围。

### Step 2：任务执行

按 tasks.md 中的任务顺序逐个执行：

- 标记为 `[P]` 的任务可以并行（修改不同文件、无共享依赖）
- 未标记 `[P]` 的任务严格按顺序执行
- 每个任务完成后，在 tasks.md 中将 `- [ ]` 改为 `- [x]`

### Step 3：验证

```
1. 运行当前批次相关的定向测试 → 记录命令和结果
2. 运行全量回归测试 → 记录命令和结果
3. 运行构建（如适用）→ 记录命令和结果
4. 运行 Smoke Test（见 rules/verification.md）→ 记录结果
5. 全部通过 → 进入 Step 3.5
6. 有失败 → 进入调试循环（遵循 rules/debugging.md 四阶段流程）
```

调试循环协议（引用 `rules/debugging.md`）：

```
Round 1：
  - 阶段一：根因调查（读错误 → 复现 → 查变更 → 追溯数据流）
  - 阶段二：模式分析（找有效代码 → 对比差异）
  - 阶段三：假设验证（形成假设 → 最小变更 → 验证）
  - 阶段四：实现修复（写测试 → 修复 → 验证 → 防御纵深）
  - 重跑测试

Round 2（如仍失败）：
  - 回到阶段一，扩大调查范围（多组件证据收集）
  - 新假设 + 新修复
  - 重跑测试

Round 3（如仍失败）：
  - 评估是否为架构问题（3 次修复失败 → 质疑架构）
  - 如果是架构问题 → 阻断流水线
  - 如果不是 → 最后一轮修复
  - 重跑测试

Round 3 后仍失败 → 触发熔断器，阻断流水线
```

### Step 3.5：代码审查（Mandatory）

在验证通过后、归档之前，执行代码自审（遵循 `rules/code-review.md`）：

```
审查六维度：
  1. 宪章对齐 — 是否偏离核心原则？是否违反硬约束？
  2. 需求规格对齐 — 验收标准是否完整覆盖？术语是否一致？
  3. 技术规范一致性 — 编码规范、API 契约、数据模型是否对齐？
  4. 代码质量 — 安全漏洞、性能隐患、错误处理？
  5. 测试质量 — TDD 规则、边界覆盖、反模式？
  6. Spec 偏移 — 实现与设计有偏移？偏移是否已记录？

判定：
  - 全 PASS 或仅 WARNING → 进入 Step 4
  - 有 Critical 需修复项 → 修复后重审（仅审改动相关维度）
  - 修复次数 > 2 → 评估任务拆分问题
```

### Step 4：归档

**提交与哈希（FR-097 / SC-022）**：默认 **单次提交**。本批验证通过后，先在 `task-execution-log.md` 追加批次记录，再将 **本批实现、测试、归档段落与 `tasks.md` 勾选** 一并 `git commit`。**「提交哈希」** 仅在本次 commit **成功之后** 写入归档（或等价地由该提交的 SHA 追溯），**禁止**为填满哈希栏而额外制造与实现无关的第二次「仅改归档」提交。

在 `task-execution-log.md` 末尾追加批次记录，使用以下固定格式：

```markdown
### Batch YYYY-MM-DD-X | T0XX-T0YY

#### 批次范围
- 覆盖任务：T0XX-T0YY
- 覆盖阶段：Phase N / [阶段描述]
- 预读范围：[列出实际阅读的文件]

#### 统一验证命令
- **验证画像**：`docs-only` / `rules-only` / `code-change`
- `R1`（如有 TDD）
  - 命令：
  - 结果：
- `V1`
  - 命令：
  - 结果：
- `V2`
  - 命令：
  - 结果：

#### 任务记录

##### T0XX | 任务名称
- 改动范围：
- 改动内容：
- 新增/调整的测试：
- 执行的命令：
- 测试结果：
- 是否符合任务目标：`符合` / `不符合`

#### 自动决策记录（如有）
- AD-001：[问题] → [决策] → [来源] → [理由]

#### 批次结论
- [总结当前批次完成情况和下一步]

#### 归档后动作
- 已完成 git 提交：`是`（与 **本批唯一一次** commit 对应）
- 提交哈希：`xxxxxxx`（**commit 成功后** 填一次；不预占位后二次修订）
- 是否继续下一批：`是` / `阻断`
```

### Step 4.5：完成前验证（Mandatory）

在提交之前，执行 `rules/verification.md` 的门函数：

```
确认以下证据已就绪（当前步骤新鲜运行的，不引用之前的结果）：
  □ latest batch 已声明 `验证画像`
  □ R1 红灯验证完成
  □ V1 绿灯验证完成
  □ V2 全量回归通过
  □ 构建通过（如适用）
  □ Smoke Test 通过（如适用）
  □ 代码审查通过（Step 3.5）
  □ tasks.md 对应任务已勾选
  □ execution-log 已记录

任何一项缺失 → 补充后再进入 Step 5
```

### Step 5：提交

```bash
git add [本批次改动的所有文件]
git add specs/NNN/task-execution-log.md
git add specs/NNN/tasks.md
git status --short
git diff --cached --stat
git commit -m "[type]: [描述]"
git push origin <branch>
```

**与 Step 4 的衔接**：优先 **一次**串行 `git add` → `git status/diff` → `git commit` 覆盖实现、测试、归档与任务勾选；如需推送远端，再在 commit 成功后单独执行 `git push`。**禁止**把这些 Git 写步骤交给并行工具或与其他仓库写命令重叠调度。若须在获知 SHA 后才填写「提交哈希」，可在更新 `task-execution-log.md` 对应行后执行 **`git commit --amend --no-edit`**，仍视为 **单条语义提交**，避免多出「仅改归档」的第二次 commit。**每批哈希只回填一次**。

commit message 规范：
- 准备/基础阶段：`feat: scaffold [feature name] implementation`
- 用户故事实现：`feat: implement [US 描述]`
- 测试：`test: add [测试范围] coverage`
- 文档：`docs: [描述]`

### Git 操作异常处理

当 git add / git commit 失败时：

```
情况 1：未初始化 git 仓库
  → 执行 git init && git add . && git commit -m "initial commit"
  → 然后重试原始提交

情况 2：存在未解决的合并冲突
  → 阻断流水线，输出冲突文件列表
  → 提示用户手动解决冲突后重新运行

情况 3：出现 `.git/index.lock`
  → 先判定是否仍有活跃 Git 进程持锁
  → 若有活跃进程：等待其结束，禁止默认删锁
  → 若确认无活跃进程：仅允许走显式 stale-lock 清理分支
  → 禁止把“先 rm 锁文件再继续”当成默认恢复动作

情况 4：pre-commit hook 失败
  → 读取 hook 输出，分析失败原因
  → 如果是 lint/format 问题 → 自动修复后重试（最多 2 次）
  → 如果是其他原因 → 阻断并输出诊断

情况 5：磁盘权限或空间不足
  → 阻断流水线，输出系统错误信息

情况 6：detached HEAD 状态
  → 尝试 git checkout -b feature/NNN-recovery
  → 然后重试提交
```

git 操作失败不算作"任务失败"（不触发调试循环），而是直接走上述专项处理。

### Step 6：进入下一批次

门禁通过 + 归档完成 + 提交完成后，检查执行模式：

```
1. 读取 pipeline.yml → stage_overrides.execute
   - 如果没有覆盖 → 使用全局 execution_mode
2. 如果 = auto → 直接开始下一批次 Step 1
3. 如果 = confirm:
   a. 读取 batch_confirm 配置（默认 per_batch）
   b. per_batch → 每个批次完成后输出确认卡，暂停等待
   c. per_phase → 仅当当前 Phase 所有批次完成后输出确认卡
   d. 用户输入「继续」→ 执行下一批次
   e. 用户输入「自动」→ 切换为 auto，后续批次不再暂停
   f. 用户输入「终止」→ 保存断点并停止
```

**状态面板**：无论执行模式如何，每批次完成后都输出阶段级状态面板（含批次进度更新）。

## 多 Agent 并行模式

当当前 Phase 包含 Parallel Groups（`[PA]` 标记）且 `multi_agent.supported = true` 时，批次执行流程切换为并行模式：

```
并行模式下的批次流程：

Step 1（Main 预读 + 准备上下文包）
  → Main 为每个 Parallel Group 准备隔离的上下文和文件边界
  → Step P1: 分发任务到各 Agent

Step P2（各 Agent 并行执行）
  → 每个 Agent 独立执行 Step 2（任务执行）+ 定向测试
  → Agent 不执行 git commit，不修改 tasks.md

Step P3（Main 合并验证）
  → 文件冲突检测
  → 编译/构建验证
  → 接口一致性检查
  → 全量回归测试
  → 逻辑一致性 + 防重复 + 防溢出检查

Step 3.5（Main 代码审查 — 覆盖所有 Agent 的产出）

Step 4（Main 归档 — 合并各 Agent 的 execution-log）

Step 4.5（Main 完成前验证）

Step 5（Main 提交 — 统一 git commit）

Step 6（模式检查 — 同串行模式）
```

并行失败时自动降级为串行（详见 `rules/multi-agent.md` 降级策略）。

## 调试循环协议

当测试失败时，遵循 `rules/debugging.md` 的四阶段系统化调试流程（已在 Step 3 中详细描述）。

**核心要求：**
- 禁止不经根因调查就尝试修复
- 每次只改一个变量，不同时修多个东西
- 修复后必须添加防御纵深（在调用链各层添加校验）
- 3 次修复失败 → 质疑架构，不再盲目尝试第 4 次
- 调试过程记录到 execution-log（格式见 `rules/debugging.md`）
