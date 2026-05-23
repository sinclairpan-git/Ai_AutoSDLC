# 生产反馈优化归档：任务守卫、注释规范与半途接入

> 状态：待拆分需求
>
> 目的：归档近期生产反馈、根因分析与解决方案，为后续细粒度拆分 `spec / plan / tasks` 提供输入。本文只记录方案，不代表已经实现。

## 1. 背景与问题

近期用户反馈集中在三类问题：

1. 安装 AI-SDLC 后，AI 可能只根据 `spec.md` 直接写代码，没有先生成或遵循 `tasks.md`。
2. 生成代码时注释习惯不稳定：缺少必要注释、偶尔删除原有注释、注释语言不符合用户沟通语言。
3. 已有项目中途接入 AI-SDLC 不顺畅：项目已有 JSON 或其他任务进度，但框架无法无缝继承当前开发状态，容易表现为只完成 0、1 步，后续流程接不上。

补充反馈：

- 中文输出和文件内容偶发乱码。
- 中文注释必须是简体中文，不能混入繁体或乱码。
- 解决方案必须简洁、直达要害，不能每发现一个问题就堆新规则，导致流程卡死或用户学习成本上升。

## 2. 总体结论

AI-SDLC 不应继续把治理主路径建立在“证明 AI 宿主已加载规则”上。

当前 Codex、Cursor、VS Code 插件、Claude Code 等 IDE / AI 工具无法向 AI-SDLC CLI 返回可信的“我已加载并遵守 `AGENTS.md` / adapter 指令”的机器可验证证据。因此，不应强行要求 `verified_loaded` 作为主路径，也不应把 `host_unverifiable` 暴露为普通用户需要理解的状态。

治理重心应从：

```text
证明 AI 是否读了规则
```

转为：

```text
证明每次代码修改是否绑定了可执行任务
```

这条路径更可验证，也更符合 AI coding 的实际控制点。

## 3. 设计原则

1. 不把学习压力转嫁给用户：用户不需要理解 `checkpoint / stage / reconcile / verified_loaded` 等内部概念。
2. 不再追求不可证明的宿主加载证据：adapter 只负责安装项目规则，代码修改由任务守卫约束。
3. 写代码前只检查关键事实：是否存在 `next executable task`。
4. 文件存在不等于流程完成：`tasks.md` 存在不代表任务可执行。
5. 必要注释强制，噪音注释禁止。
6. 保留原有有价值注释，默认不得无理由删除。
7. 注释语言跟随用户当前或近期主要沟通语言，无法判断时默认简体中文。
8. 中文内容必须 UTF-8、简体中文、无乱码。
9. 半途接入采用 adoption 模式：导入事实、映射进度、找到继续点，而不是让用户重新开始。

## 4. Adapter 与治理状态调整

### 4.1 废弃 `verified_loaded` 主路径

不再要求 Codex 类 adapter 达到 `verified_loaded` 才算可用。相关状态可保留为内部诊断，但不作为用户主路径，也不作为进入开发的必要条件。

用户侧应展示更简单的结果：

```text
AI-SDLC 已安装项目规则。
写代码前会检查当前任务拆解；没有可执行任务时，会先补任务，不会直接改代码。
```

### 4.2 新的核心状态

建议将内部实现收敛为两个事实：

- `instructions_installed`：项目规则文件已经写入 canonical path，例如 `AGENTS.md`。
- `workflow_guarded`：本次代码修改是否绑定了可执行任务。

这些是内部状态名，不应直接出现在普通用户主路径中。用户侧只应看到类似文案：

```text
项目规则已安装。
写代码前会先确认当前任务；如果任务缺失，我会先补一条最小任务再继续。
```

内部仍可记录宿主诊断，但普通用户不需要看到“待验证”“无法验证宿主”等容易误解的表述。

## 5. Next Executable Task 守卫

### 5.1 核心规则

如果本次请求会修改产品代码，AI 必须先找到当前 active work item 中的下一个可执行任务。

守卫内部只输出两类结论：

```text
ALLOW_CODE_WITH_TASK: Txx
BLOCK_CODE_PREPARE_TASKS: 先准备可执行任务，禁止修改产品代码
```

这些内部结论不应作为普通用户界面文案。用户侧应表达为：

```text
已找到当前任务，将按 Txx 实现。
```

或：

```text
还缺少可执行任务，我会先补一条最小任务再继续。
```

守卫失败时不能只停止。AI 必须自动执行其中一个动作：

1. 补齐最小 `plan.md / tasks.md`。
2. 创建最小 work item。
3. 启动已有项目接入流程。
4. 仅在范围高歧义或高风险时向用户提出一个最小确认问题。

### 5.2 判定条件

允许写代码必须同时满足：

1. 存在 active work item。
2. 存在 `spec.md / plan.md / tasks.md`。
3. `tasks.md` 中存在至少一个未完成、可执行任务。
4. 任务具备最小字段：
   - task id
   - 目标
   - 涉及文件或范围
   - 验收标准
   - 验证方式
   - 状态：todo / doing / done / blocked
5. 本次请求属于代码修改请求。

代码修改后还必须通过 postflight 检查：本次代码 diff 能映射到任务的文件范围和验收标准，并写入 execution log。

### 5.3 三段式闭环

`next executable task` 守卫必须覆盖三段闭环，而不是只在写代码前做一次判断：

1. Preflight：在修改产品代码前选出一个可执行任务。若没有任务，自动补最小任务或启动 adopt。
2. During：实现过程中只能修改任务声明的文件范围。若发现必须超出范围，应先更新任务或询问用户确认。
3. Postflight：实现后检查 git diff 是否映射到任务文件范围和验收标准；同步 `tasks.md` 状态与 `task-execution-log.md`。

### 5.4 文件存在不等于可执行

`workitem init` 生成的 `tasks.md` 可能只是脚手架或模板任务，不一定是基于用户需求拆出的业务任务。因此必须区分：

- `tasks_present`：文件存在。
- `tasks_executable`：存在可用于编码的任务。

只有 `tasks_executable=true` 才允许修改产品代码。

模板任务或占位任务不得被判定为可执行。以下信号应视为不可执行：

- 标题、目标、文件范围或验收标准仍含“待补充”“TODO”“placeholder”等占位文本。
- 任务文件范围指向框架模板或示例路径，而不是当前用户需求对应的业务文件。
- 任务没有验证方式。
- 任务状态缺失或不是允许枚举。

### 5.5 最小可解析任务格式

为避免继续依赖 LLM 猜测，`tasks.md` 应提供机器可解析的最小任务块。推荐格式如下：

```markdown
### Task T12: 补齐订单状态回写

- status: todo
- goal: 当支付回调成功时，将订单状态从 pending 更新为 paid。
- scope:
  - src/order/service/OrderService.java
  - src/order/repository/OrderRepository.java
- acceptance:
  - 支付成功回调只更新对应订单。
  - 重复回调保持幂等。
- verify:
  - mvn test -Dtest=OrderServiceTest
- notes:
  - 需要保留现有订单状态注释；如修改注释，必须同步业务含义。
```

状态枚举：

- `todo`
- `doing`
- `done`
- `blocked`
- `needs-review`

字段处理：

- 缺 `status / goal / scope / acceptance / verify` 任一字段时，该任务不可执行。
- `needs-review` 不可作为 active task。
- `blocked` 不可执行，除非本次请求明确是解除 blocker。
- `done` 不可执行，除非本次请求是回归修复并创建新的 follow-up task。

### 5.6 不应卡住的场景

以下场景不应要求用户手动执行一堆命令：

- 只有 `spec.md`：AI 应先补最小 `plan.md / tasks.md`，再继续。
- 用户要求紧急小修：AI 应先生成一个极简 task，再实现。极简 task 仍必须包含文件范围、验收标准和验证方式。
- 用户只是分析、解释、排查：不触发代码修改守卫。
- 找不到 active work item：AI 默认创建最小 work item，而不是让用户理解 checkpoint。

极简 task 示例：

```markdown
### Task T-fix-ci: 修复 Windows 安装脚本编码错误

- status: todo
- goal: 修复 PowerShell 安装脚本输出中文乱码。
- scope:
  - packaging/offline/install_offline.ps1
- acceptance:
  - 中文输出在 PowerShell 中显示为简体中文且无乱码。
  - 不改变安装脚本的参数兼容性。
- verify:
  - pwsh -File packaging/offline/install_offline.ps1 -Help
```

## 6. 注释规范

### 6.0 分层表达

本章是内部规则和 code-review 标准，不应原样塞进普通用户提示。普通用户侧只需要看到一句话：

```text
我会保留原有有价值注释，并在复杂逻辑处补充必要注释；中文场景使用简体中文。
```

### 6.1 通用原则

必须写注释的情况：

- 业务规则：折扣、权限、状态流转、审批、计费、风控、库存、订单等。
- 非显然逻辑：算法、复杂条件、特殊分支、兼容逻辑。
- 边界条件：空值、时区、精度、分页、重试、幂等。
- 副作用：写库、发消息、调外部 API、缓存、锁、事务。
- 并发和异步：goroutine、线程池、队列、debounce、race 防护。
- 安全相关：鉴权、脱敏、签名、权限降级、防重放。
- 临时方案：TODO / FIXME 必须说明原因、负责人或触发条件、移除条件。
- 公共 API：对外可调用的类、函数、接口、组件 props / events。

禁止写注释的情况：

- 复述代码，例如“设置 userId”。
- 给每一行机械解释。
- 保留和代码事实冲突的历史注释。
- 用注释掩盖糟糕命名。
- 无原因、无移除条件的 TODO。

### 6.2 注释语言

新增或修改注释的语言由当前用户与 AI 的主要沟通语言决定：

- 用户主要用中文沟通：新增注释必须使用简体中文。
- 用户主要用英文沟通：新增注释必须使用英文。
- 无法判断：默认使用简体中文。
- 不主动重写历史注释；只约束本次新增或修改的注释。
- 如果项目已有明确团队规范，可作为兜底配置，但不应覆盖当前对话中清晰的语言信号。

### 6.3 保留原有注释

生成或修改代码时，已有注释默认视为代码语义的一部分，不得无理由删除。

允许删除或改写原有注释的条件：

- 注释已经明显与代码事实冲突。
- 注释描述的是被删除的旧逻辑。
- 注释是无意义噪音，只复述代码。
- 用户明确要求清理注释。
- 本次重构导致注释必须同步更新。

默认优先动作是更新过期注释，而不是直接删除。

如果本次变更删除了原有注释，必须在 execution log 中记录：

- 删除了什么类型的注释。
- 删除原因。
- 是否有替代说明。

### 6.4 Java / Spring

必须写 Javadoc：

- `public` / `protected` class、interface、enum、record。
- Controller API、Service public method、SDK / API method。
- 跨模块调用点、框架入口、扩展点、回调入口。
- DTO 中业务含义不明显的字段。
- 会返回 `null`、抛业务异常、有事务边界的方法。
- 普通内部 `public` / `protected` method 只有在行为非显然、跨模块复用、涉及业务规则或高风险副作用时才要求 Javadoc。

Javadoc 应说明：

- 做什么，不写实现细节。
- 参数业务含义，特别是单位、范围、是否可空。
- 返回值含义，特别是空集合、null、分页结果。
- 异常和错误码。
- 事务、副作用、权限要求。
- 幂等性和并发约束。

例外：

- 简单 getter / setter 可不写。
- override 方法行为未变化时可不重复写。
- private 方法只有复杂逻辑才写。

### 6.5 Go

必须写注释：

- 每个 package 的 package comment。
- 每个 exported type / func / const / var。
- exported struct field 如果业务含义不明显，必须字段注释。
- goroutine、channel、mutex、context cancellation 的所有权和生命周期。
- sentinel error、错误包装语义。
- 外部协议、重试、超时、幂等规则。

Go 注释风格：

- exported name 注释以名称开头。
- 使用完整句子。
- 不给简单 unexported helper 强行写注释。
- `//go:` directive 不当普通注释处理。

### 6.6 Python

必须写 docstring：

- 对外模块、框架入口模块、CLI 模块。
- public class。
- public function / method 中的跨模块调用点、框架入口、业务规则入口。
- 非平凡 private helper。
- FastAPI / Flask route handler。
- Celery task、定时任务、CLI command。
- 普通内部函数如果命名和类型已经足够清楚，且没有复杂逻辑或副作用，不强制 docstring。

Docstring 内容：

- Summary 一句话。
- `Args`：只写业务含义，不重复 type hint。
- `Returns`：说明语义，不重复类型。
- `Raises`：业务异常、外部错误、重试边界。
- Side effects：写库、发请求、写文件、发消息。
- Security / permission：有鉴权时必须说明。

Inline comment 只用于：

- 复杂算法。
- 不直观的兼容分支。
- 性能取舍。
- 外部系统怪异行为。
- 数据修复逻辑。

### 6.7 Vue2

Vue SFC 必须注释：

- 可复用业务组件的组件级说明。
- props 的业务含义，尤其是枚举、单位、权限、默认行为。
- emitted events 的触发时机和 payload。
- slot 的用途。
- watcher 中的非显然副作用。
- computed 中复杂业务规则。
- mixin / directive / filter 的适用边界。
- 与后端协议、i18n key、权限控制相关的逻辑。
- 为兼容 Vue2 限制写的特殊实现。

### 6.8 JavaScript

JavaScript 必须 JSDoc：

- exported function。
- exported class。
- composable / util / API client。
- 复杂 callback、事件 payload。
- 非显然 boolean 参数，优先改名；不能改名时用参数名注释。

### 6.9 TypeScript

TypeScript 必须 JSDoc：

- exported function / class 中行为非显然、跨模块复用或涉及业务规则的成员。
- exported interface / type 中业务含义复杂、单位不明显、取值范围不明显或与后端协议绑定的字段。
- API client、composable、复杂 callback、事件 payload。

TypeScript 不应对类型已经清楚的字段重复写类型说明。类型系统已经表达清楚的内容，不需要再用 JSDoc 复述。

### 6.10 前端禁止项

前端禁止：

- 在 template 里大量 HTML 注释。
- 对简单 click handler 写废话注释。
- 对类型已经清晰的 TS 字段重复写类型说明。
- 注释里写交互说明但不和实际行为同步。

### 6.11 参考规范

- Google Java Style Guide: https://google.github.io/styleguide/javaguide.html
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
- Google C++ Style Guide: https://google.github.io/styleguide/cppguide.html
- Go Doc Comments: https://go.dev/doc/comment
- Effective Go: https://go.dev/doc/effective_go
- Airbnb JavaScript Style Guide: https://github.com/airbnb/javascript
- Google JavaScript Style Guide: https://google.github.io/styleguide/jsguide.html
- Microsoft TypeScript / C# documentation conventions: https://learn.microsoft.com/
- Alibaba Java Coding Guidelines: https://github.com/alibaba/p3c
- Vue Style Guide: https://vuejs.org/style-guide/

## 7. 中文与编码约束

### 7.1 中文内容要求

- 所有新增中文必须是简体中文。
- 不允许繁体中文混入，除非项目本身就是繁体或用户明确要求。
- 不允许出现乱码、mojibake 或替换字符。

常见乱码特征包括：

- `�`
- `����`
- `Ã`
- `â€™`
- `涓`
- `乱码`

### 7.2 编码要求

- 新建或修改文本文件默认使用 UTF-8，无 BOM，除非项目已有明确编码约定。
- 修改已有文件时尊重原文件编码，不应导致整文件编码漂移。
- Windows / PowerShell 场景下，CLI 输出和文件写入必须明确 UTF-8。
- 涉及中文内容的模板、adapter、生成器、测试夹具必须覆盖 UTF-8 读写。

### 7.3 建议检查

后续可加入轻量检查：

- `encoding check`：扫描新增或修改文本文件是否可用 UTF-8 解码。
- `bom check`：检查新增 UTF-8 文本是否带 BOM；除非项目已有约定，否则不允许新增 BOM。
- `mojibake check`：检查替换字符 `�`、常见 mojibake pattern 和明显异常片段。
- `zh text check`：只扫描新增或修改的中文片段，检查繁体高频字和乱码特征。

检查失败时应给出可操作修复建议，不应让用户理解编码细节。

简繁检查必须有白名单和误报处理：

- 项目本身使用繁体中文时可关闭简体强制。
- 专有名词、品牌名、引用文本允许白名单。
- 默认只检查本次新增或修改的中文片段，不对历史全仓库强制清洗。
- 发现乱码时应优先建议或尝试自动修复，不把 UTF-8 / BOM / mojibake 知识压力交给用户。

## 8. 半途接入：Brownfield Adopt

### 8.1 核心目标

已有项目中途接入 AI-SDLC 时，框架应承担理解现状的责任，不能要求用户学习 AI-SDLC 的内部阶段模型。

用户入口应简单到：

```powershell
ai-sdlc adopt .
```

或在 AI 对话中输入：

```text
这个项目已经做到一半了，进度在 progress.json，帮我接入 AI-SDLC 继续。
```

### 8.2 扫描事实源

adopt 应自动扫描：

- JSON 任务进度文件。
- README / TODO / markdown 计划。
- issue export。
- 当前 git branch。
- uncommitted diff。
- 最近 commits。
- 测试文件。
- 已有接口、页面、模块结构。
- 项目技术栈。

扫描必须有性能边界：

- 默认忽略 `node_modules/`、`dist/`、`build/`、`vendor/`、`.git/`、缓存目录和大体积二进制目录。
- 默认只读取最近 N 次 commit，N 的初始建议值为 30。
- 对大文件只读取头尾和结构摘要，避免一次性读入完整日志或构建产物。
- 若用户显式指定任务文件，例如 `progress.json`，优先读取该文件。

### 8.3 自动识别任务字段

从 JSON 或其他任务源中自动识别：

- `id`
- `title`
- `description`
- `status`
- `progress`
- `children`
- `dependencies`
- `files`
- `owner`
- `createdAt`
- `doneAt`
- `blockedReason`

不要求用户提供 schema。识别不了时生成低置信度映射，交给用户确认摘要。

### 8.4 置信度与确认策略

adopt 不应因为局部识别不确定而卡住整个接入。

建议策略：

- 高置信：字段完整、状态清晰、来源文件明确，自动导入。
- 中置信：字段基本完整但状态或范围存在歧义，输出摘要让用户确认。
- 低置信：字段缺失严重或语义不稳定，标记为 `needs-review`，不作为 active task。

多个进行中任务同时存在时，按以下顺序推荐继续点：

1. 与当前 uncommitted diff 相关的任务。
2. 与最近 commit 修改文件相关的任务。
3. 最近更新时间最新的任务。
4. 依赖已完成且 blocker 最少的任务。

如果用户不确认摘要：

- 已高置信导入的任务保留为候选映射。
- 中低置信任务保持 `needs-review`。
- 框架仍应基于 README、commit、diff 生成一个临时继续点，而不是直接失败退出。

### 8.5 Adoption Map

保留用户原有任务系统，不覆盖原 JSON。

生成：

```text
.ai-sdlc/adoption/adoption-map.yaml
```

表达：

```text
external_task_id -> ai_sdlc_task_id
external_status -> ai_sdlc_status
source_file -> 原任务文件路径
confidence -> high / medium / low
```

adopt 摘要必须明确告诉用户：

```text
原进度文件不会被改动；AI-SDLC 只会生成映射文件和桥接产物。
```

### 8.6 桥接产物

adopt 应自动生成或补齐：

- `specs/<WI>/spec.md`
- `specs/<WI>/plan.md`
- `specs/<WI>/tasks.md`
- `specs/<WI>/task-execution-log.md`
- `.ai-sdlc/state/checkpoint.yml`
- `.ai-sdlc/adoption/adoption-map.yaml`

这些产物应基于已有项目事实合成，而不是从 0 开始。

### 8.7 状态映射

建议状态映射：

- `done` / `completed` / `closed` -> task done，并写入 execution log。
- `doing` / `in_progress` -> 当前 active task。
- `blocked` -> task blocker。
- `todo` / `open` -> pending task。
- 无法判断 -> `needs-review`，但不阻断整个接入。

### 8.8 用户体验

adopt 完成扫描后，只向用户输出摘要：

```text
已识别 18 个历史任务：11 个已完成，2 个进行中，5 个未开始。
当前建议从 T12“补齐订单状态回写”继续。
```

用户只需要确认或指出不对，不需要选择 stage。

用户可见产品名建议使用“接入已有项目”。`adopt` 可作为命令名，但中文文案不应要求用户理解英文术语。

### 8.9 失败降级

如果 JSON 完全无法识别，框架仍应降级继续：

1. 从 README / TODO / 计划文档推断候选任务。
2. 从最近 commit 与当前 diff 推断当前继续点。
3. 从测试失败或用户当前需求生成临时最小 task。
4. 明确说明“没有改动原任务文件，只生成临时接入建议”。

只有在无法读项目、权限不足或存在会破坏用户文件的风险时，才停止并要求用户确认。

## 9. 端到端用户旅程

### 9.1 新项目需求

用户输入：

```text
我要做用户登录功能。
```

系统行为：

1. 自动创建最小 work item。
2. 生成 `spec.md / plan.md / tasks.md`。
3. 选出第一个可执行 task。
4. 再开始写代码。

用户看到：

```text
我会先完成任务拆解，再从第一条可执行任务开始实现。
```

### 9.2 已有 spec 但无 tasks

用户输入：

```text
按这个 spec 继续实现。
```

系统行为：

1. 发现缺少可执行任务。
2. 自动补最小 `plan.md / tasks.md`。
3. 选出可执行 task。
4. 再开始写代码。

用户看到：

```text
当前还缺少任务拆解，我会先补一条可执行任务再继续。
```

### 9.3 已有项目带 progress.json

用户输入：

```text
这个项目已经做到一半了，进度在 progress.json，帮我接入 AI-SDLC 继续。
```

系统行为：

1. 扫描 `progress.json`、README、commit、diff。
2. 生成 adoption map 和桥接产物。
3. 高置信任务自动导入，低置信任务标记 `needs-review`。
4. 推荐继续点。

用户看到：

```text
已识别 18 个历史任务：11 个已完成，2 个进行中，5 个未开始。
原 progress.json 不会被改动。
当前建议从 T12“补齐订单状态回写”继续。
```

## 10. 后续待拆分能力

建议后续拆分为以下 work items：

1. Adapter 口径简化：废弃 `verified_loaded` 主路径，调整用户可见文案。
2. Next executable task 守卫：代码修改前必须绑定可执行任务。
3. Tasks executable schema：定义轻量可执行任务字段与判定。
4. 注释规范落地：按 Java / Go / Python / Vue2 / JS / TS 补模板、规则和 review checklist。
5. 原有注释保护：防止 AI 无理由删除已有注释。
6. 中文与编码检查：简体中文、UTF-8、乱码检测。
7. Brownfield adopt 扫描：识别 JSON / TODO / issue / git 事实源。
8. Adoption map 与桥接产物：映射外部任务到 AI-SDLC work item。
9. Adopt 用户体验：一键接入、摘要确认、自动定位继续点。
10. Guard postflight：diff 映射、execution log、任务状态同步。

## 11. 验收方向

后续实现应至少覆盖以下场景：

1. Codex adapter 无法提供宿主加载证明时，用户不会看到失败或待验证阻塞。
2. 只有 `spec.md` 时，AI 不得直接修改产品代码，而应先补 `plan.md / tasks.md`。
3. `tasks.md` 只是模板任务时，不得被判定为可执行任务。
4. 存在可执行任务时，代码 diff 必须能映射到任务文件范围和验收标准。
5. 生成代码不会无理由删除已有注释。
6. 新增复杂逻辑、业务规则、边界条件时必须补必要注释。
7. 中文用户场景下新增中文注释必须是简体中文。
8. 英文用户场景下新增注释必须是英文。
9. 修改中文文件不引入乱码或编码漂移。
10. 已有项目含 JSON 任务进度时，adopt 能生成映射、桥接产物和继续点。
11. adopt 不覆盖用户原始 JSON。
12. 用户不需要理解 checkpoint / stage / reconcile 即可继续。
13. 守卫失败时不会只停止，而会自动补任务、创建最小 work item、启动 adopt 或提出最小确认问题。
14. 缺 `status / goal / scope / acceptance / verify` 的 task 不可执行。
15. `needs-review` 任务不可作为 active task。
16. 紧急小修 task 必须包含文件范围、验收标准和验证方式。
17. Postflight 能识别 diff 超出任务范围并阻断或要求更新任务。
18. 乱码检查覆盖 BOM、替换字符、常见 mojibake pattern 和新增中文片段简繁检查。
19. adopt 对高 / 中 / 低置信任务有不同处理，并能在 JSON 识别失败时降级生成临时继续点。

## 12. 风险与边界

- 不应把不可证明的宿主加载状态包装成强保证。
- 不应强制所有代码都写注释，否则会污染代码。
- 不应只检查四件套文件存在，否则会制造假安全。
- 不应要求用户手动执行多条诊断命令才能继续。
- 不应覆盖用户已有任务系统，应做映射和引用。
- 不应因为少量低置信度任务阻断整个 brownfield 接入。
