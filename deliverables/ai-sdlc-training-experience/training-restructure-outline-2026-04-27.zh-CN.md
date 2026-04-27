# AI-SDLC 培训重构大纲（第二版）

## 1. 重构结论

这套培训不应再以“门禁很多、治理很严”为主线，而应从一个业务事故切入：

- 同一需求跨两周，AI 和人来回改了三轮
- 中途换了一个同事接手，第一件事是重新读项目
- 页面看起来差不多了，但验收的人不敢签完成
- 最后发现旧证据不能代表这轮结果，团队又返工了一遍

这四句应该成为第一页，而不是任何框架定义。只有在讲完“它如何避免这种损失”之后，才回收到一句结论：

> **AI-SDLC 不是更会写代码的聊天流程，而是一个有状态、可续跑、可扩展的 AI 交付操作系统。**

真正要解决的问题不是“AI 会不会写”，而是：

- 长任务会不会在多轮执行中失真
- 中断后能不能快速续跑，而不是重新通读项目
- 完成声明能不能被最新证据支撑
- 失败能不能被系统吸收，变成下一次默认约束
- AI 生成的前端能不能被团队稳定接管，而不是只生成一次性页面

这次培训重构要把以下三块缺口升成主线，而不是补充页：

- 长上下文场景下，系统如何替团队记住任务并支持快速续跑
- AI-SDLC 除了门禁之外，还有哪些系统性能力
- 前端为什么必须先有前端控制栈，再允许 AI 生成

## 2. 培训目标

### 2.1 总目标

让听众在培训结束后形成一个稳定判断：

> AI-SDLC 不是“更会写代码的聊天流程”，而是把需求、状态、执行、证据、收口和失败回写提升成系统对象的交付框架。

### 2.2 面向两类听众的结果

#### 面向业务方 / 轻技术 AI 使用者

- 能理解为什么长任务会漂
- 能理解 AI-SDLC 为什么能支撑中断后继续
- 能理解“完成”为什么不能只听口头表述
- 能理解前端为什么不能直接从空白页面自由生成

#### 面向专业工程人士

- 能看清 AI-SDLC 的状态对象、控制面、执行面、证据面
- 能理解 fresh evidence、close-check、truth sync、branch-check 的工程意义
- 能理解前端控制栈如何把无限生成空间压缩成可治理空间
- 能把失败回写成 rule / workflow / tool / eval 的系统升级输入

### 2.3 业务账

每个模块都必须能回答“对谁，少掉什么动作，避免什么损失”：

| 对谁 | 少掉什么动作 | 避免什么损失 |
| --- | --- | --- |
| 产品负责人 | 少一次换人后的重新对齐会 | 避免需求上下文断片 |
| 交付负责人 | 少一次“做到哪了”人工盘点 | 避免进度表述和真实状态分叉 |
| 验收人 | 少一次“看起来完成”的争议回合 | 避免假完成后的返工 |
| 前端负责人 | 少一次一次性页面的整体重做 | 避免 AI 成品无法接管 |

## 3. 讲述原则

### 3.1 总体顺序

采用由浅入深的单线叙事：

1. 先讲真实失控问题
2. 再讲系统如何记住状态
3. 再讲如何中断后快速续跑
4. 再讲控制面 / 执行面 / 证据面分离
5. 再讲 fresh evidence 与完成判定
6. 再讲失败如何回写成新约束
7. 再讲前端为什么必须先有前端控制栈
8. 最后用前端案例证明整套结构真的在工作

### 3.2 每个模块的讲法

每个模块都固定采用两层表达：

- 先用业务层问题定义和结果表达，把非专业听众带进来
- 再用仓库里的 formal docs、代码、测试和 defects 证明这不是概念话术

### 3.3 系统性能力清单

培训里要显式讲出 AI-SDLC 不只是 gate，还至少包括这些系统能力：

- 状态对象化：把任务推进中的关键事实提升成可恢复对象
- 只读 handoff：允许局部恢复，不必每次重读全项目
- 窄执行面：把真正会落盘的动作收进受控 surface
- 最新证据链：只允许 fresh evidence 支撑完成声明
- 收口核验：用 close-check、branch-check、truth sync 判断当前真值
- 失败回写：把真实踩坑沉淀成 rule / workflow / tool / eval
- 前端受控生成：把自由生成压缩成受控控制栈

### 3.4 明确删弱的旧讲法

- 不要太早讲命令
- 不要太早讲 effective truth、close-check grammar 这类内部术语
- 不要把培训中心放在“门禁很多”
- 不要把前端案例讲成“前端治理案例展示”
- 不要默认听众已经接受前端控制栈的必要性

## 4. 最小架构脊柱

在模块 1 之后，应立即给出一张最小架构脊柱图，把“有状态、可续跑、可扩展”拆成可验证结构，而不是继续停留在口号。

### 最小脊柱

`state object -> read-only truth surface -> narrow execute surface -> fresh evidence -> close-check / truth-sync verdict -> defect writeback`

### 讲法要求

- 先用人话解释：系统先记住，再允许只读查看，再允许窄执行，再要求最新证据，再给出“当前能不能宣称完成”的 verdict，最后把失败写回系统
- 再用同一条前端链路证明：`solution-confirm -> page-ui-schema-handoff -> managed-delivery-apply -> browser-gate-probe -> close-check/truth-sync`

### 仓库证据

- `USER_GUIDE.zh-CN.md:1171-1185`
- `USER_GUIDE.zh-CN.md:1232-1267`
- `USER_GUIDE.zh-CN.md:1393-1436`

## 5. 八个模块的大纲

## 模块 1：长任务为什么天然失控

### 要回答的问题

为什么模型明明会写，团队还是会在长任务里失控。

### 核心结论

长任务的核心风险不是单次生成质量，而是多轮执行中的状态漂移、上下文断裂、假完成和历史证据失认。

### 业务方讲法

先讲团队真实痛点：

- 昨天做到哪，今天说不清
- 换人就要重新读项目
- AI 前后说法不一致
- 旧产物还在，但新流程不认

### 专业人士讲法

强调“聊天记忆”不是正式状态链，系统如果没有把阶段、产物和恢复点对象化，就会在中断后退回靠人工恢复。

### 仓库证据

- `docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md`
- `docs/framework-defect-backlog.zh-CN.md` 中 `FD-2026-03-26-002`
- `docs/framework-defect-backlog.zh-CN.md` 中 `FD-2026-03-28-001`

## 模块 2：AI-SDLC 把什么提升成状态对象

### 要回答的问题

AI-SDLC 至少记住了哪四件事，为什么它能支撑中断继续。

### 核心结论

AI-SDLC 的本体不是提示词模板，而是把任务推进中的关键事实提升成可恢复对象和可读真值面。

### 业务方讲法

先只讲四个问题，不先上内部术语：

- 现在做到哪
- 哪些改动真的已经落盘
- 哪些信息只是只读查看，不代表已经执行
- 凭什么说这轮已经完成

把“对话里说过什么”变成“系统里有对象可查”，这才是团队可续跑的前提。

### 专业人士讲法

在业务问题讲清之后，再回填术语对照，而不是反过来先堆术语：

- work item
- stage state
- solution snapshot
- managed delivery apply artifact
- browser gate latest evidence
- close-check verdict
- branch / worktree disposition

### 仓库证据

- 运行态 / 只读面：
  - `USER_GUIDE.zh-CN.md:1171-1185`
  - `USER_GUIDE.zh-CN.md:1232-1267`
- 收口 / 恢复面：
  - `USER_GUIDE.zh-CN.md:1393-1436`

## 模块 3：如何中断后快速继续，而不是重新通读项目

### 要回答的问题

长上下文优化为什么不是“更长 token”，而是“状态可恢复”。

### 核心结论

真正节省上下文的不是模型一次吃更多，而是关键状态和 handoff 面已经落盘，恢复时只需要读局部真值。

### 业务方讲法

系统替团队回答：

- 当前做到哪
- 哪一步已经落盘
- 哪一步只是只读查看
- 哪一步还缺执行或缺证据

### 专业人士讲法

强调恢复链路由 artifact 和 truth surfaces 支撑，而不是靠操作者重新拼接历史：

- `solution-confirm` 落 `solution snapshot`
- `managed-delivery-apply` 落 apply artifact
- `browser-gate-probe` 落 latest evidence
- handoff surface 用于局部恢复
- `truth sync / close-check / branch-check / reconcile` 作为技术深潜和附录内容出现，不在业务主线里抢前排

### 仓库证据

- 正向恢复链：
  - `USER_GUIDE.zh-CN.md:1230-1267`
  - `USER_GUIDE.zh-CN.md:1298-1304`
- 反向阻断链：
  - `USER_GUIDE.zh-CN.md:1304`
  - `USER_GUIDE.zh-CN.md:1321`
- 历史缺陷：
  - `docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md`

## 模块 4：控制面 / 执行面 / 证据面的分离

### 要回答的问题

为什么不能一边看、一边改、一边说已经做完。

### 核心结论

聊天框负责意图，终端负责流程；只读 handoff 负责暴露真值，execute surface 才允许真正落盘；证据面负责回答“完成能不能被证明”。

### 业务方讲法

这不是形式主义，而是为了防止“边诊断边偷执行”和“边解释边冒充完成”。

### 专业人士讲法

把不同 surface 的职责说清楚：

- `page-ui-schema-handoff` 是只读真值面
- `managed-delivery-apply --execute` 是窄执行面
- `browser-gate-probe --execute` 是证据生产面
- `close-check` 是收口核验面

### 仓库证据

- 只读与执行边界：
  - `USER_GUIDE.zh-CN.md:1171-1185`
  - `USER_GUIDE.zh-CN.md:1298-1304`
- execute surface formal truth：
  - `specs/020-frontend-program-execute-runtime-baseline/spec.md`
  - `specs/133-frontend-program-registry-governance-persistence-runtime-closure-baseline/spec.md`

## 模块 5：为什么完成必须看 fresh evidence

### 要回答的问题

为什么“我跑过了”“我看起来没问题”不算完成。

### 核心结论

完成声明必须由当前声明范围内的最新证据支撑；系统宁可返回 incomplete，也不允许把缺证据误报成 passed。

### 业务方讲法

这里再讲门禁才合理。重点不是“多一道测试”，而是系统拒绝用旧截图、旧结论、旧感觉冒充当前完成。

### 专业人士讲法

讲清 fresh evidence 的 fail-closed 语义：

- evidence missing
- recheck required
- transient run failure
- only latest evidence can support close-out

### 仓库证据

- 正例：
  - `tests/unit/test_frontend_browser_gate_runtime.py:576-610`
- 反例：
  - `tests/unit/test_frontend_browser_gate_runtime.py:527-575`
  - `tests/unit/test_frontend_browser_gate_runtime.py:695-786`
- 收口语义：
  - `docs/framework-defect-backlog.zh-CN.md:740-762`
  - `docs/framework-defect-backlog.zh-CN.md:1394-1468`

## 模块 6：失败不是备注，而是新约束的来源

### 要回答的问题

为什么 AI-SDLC 会越跑越硬，而不是每次都重新犯同类错误。

### 核心结论

真实失败必须进入缺陷池，再沉淀成 rule / policy / middleware / workflow / tool / eval。框架能力来自被记录、被产品化的失败，而不是预想中的完美设计。

### 业务方讲法

强调“这不是出错后记个 note”，而是把踩过的坑变成以后默认不会再踩的系统能力。

### 专业人士讲法

用具体 defect 讲“失败如何变约束”：

- formal spec 误写到辅助目录，后来加 canonical target guard
- 识别违约后没同轮记账，后来加 breach guard
- plan freeze 被误当成 execute 授权，后来加 execute authorization preflight

### 仓库证据

- `docs/framework-defect-backlog.zh-CN.md:157-190`
- `docs/framework-defect-backlog.zh-CN.md:192-223`
- `specs/117-formal-artifact-target-guard-baseline/spec.md`
- `specs/118-release-docs-and-execute-handoff-guard-baseline/spec.md`

## 模块 7：为什么 AI 生成页面最后总像重做

### 要回答的问题

为什么前端不能让 AI 直接从空白页面自由生成，为什么它最后经常像“做出来了但接不住”。

### 核心结论

前端不是“自由生成页面”，而是“语义到实现的受控控制栈”。对业务方先讲结果：如果没有控制栈，同一页面做三次就可能出现三套结构、三套交互、三套维护方式，后面每改一次都像重做。

对专业人士再讲完整结构：Kernel 和 Provider 很重要，但还不够；真正起作用的是：

`Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions -> Gate`

这条栈把无限实现空间压缩成可治理、可比较、可接管的有限空间。

### 业务方讲法

先给反例，而不是先讲术语：同一页面让 AI 连做三次，如果没有控制栈，组件风格、交互约束、页面结构和可维护性都可能不一样，后面每改一次都像重做。

然后再用中文解释成三层：

- 先定页面和组件的通用语言
- 再定接哪套组件库和怎么映射
- 再定哪些组合允许生成、哪些必须被拦

### 专业人士讲法

要讲透三个优势：

- 可比较：`Ui*` 语义不变，Provider 可替换
- 可治理：Whitelist / Hard Rules / Token Rules 可以约束生成空间
- 可接管：结果能进入 quality / consistency / browser gate，而不是一段一次性页面代码

### 仓库证据

- 控制栈 formal truth：
  - `specs/017-frontend-generation-governance-baseline/spec.md`
  - `specs/015-frontend-ui-kernel-standard-baseline/spec.md`
  - `specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`
- 运行态 handoff / downstream 边界：
  - `USER_GUIDE.zh-CN.md:1180-1185`
  - `USER_GUIDE.zh-CN.md:1332-1367`
- 辅助说明：
  - `docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`
  - `src/frontend-governance/runtime/kernel/KernelWrapper.tsx`

## 模块 8：用前端案例证明整套结构真的在工作

### 要回答的问题

前面讲的状态对象、执行面、证据面和前端受控生成，能不能在同一条真实链路里连起来。

### 核心结论

前端案例不是单页展示，而是整套结构的缩微证明：Contract instantiation 和 generation governance 先收紧生成边界，solution snapshot 定义有效方案，只读 handoff 暴露局部真值，apply 真正落盘，browser gate 生成最新证据，close-check / truth-sync 再回答当前能不能继续声称完成。

### 业务方讲法

把这条链路讲成“约束先收紧 -> 方案确认 -> 交接可查 -> 执行留痕 -> 验收有新证据 -> 才能宣称完成”，而不是一堆命令截图。

### 专业人士讲法

必须用同一条链讲清 recommendation、effective truth、latest evidence 和 close-out 之间的关系，避免把 presentation rendering 讲成原始终端证据。

### 仓库证据

- `specs/017-frontend-generation-governance-baseline/spec.md`
- `USER_GUIDE.zh-CN.md:1180-1185`
- `USER_GUIDE.zh-CN.md:1230-1304`
- `USER_GUIDE.zh-CN.md:1393-1436`
- `tests/unit/test_frontend_browser_gate_runtime.py:527-786`

## 6. 建议的新页序

建议下一版正式 deck 不再沿“前半价值、后半治理”硬切，而按这 8 个模块重新组织。推荐页序如下：

1. 开场失败场景：需求跨周、换人、重跑、谁都不敢签完成
2. 长任务为什么天然失控
3. 最小架构脊柱：记住 -> 只读查看 -> 受控执行 -> 最新证据 -> verdict -> 失败回写
4. 系统至少记住哪 4 件事
5. 中断后如何快速继续
6. 控制面 / 执行面 / 证据面为什么必须分离
7. 为什么完成必须看 fresh evidence
8. fresh evidence 的反例：缺证据、要复检、短暂失败都不算通过
9. 失败如何回写成新约束
10. 为什么 AI 生成页面最后总像重做
11. 前端控制栈如何压缩实现空间
12. 最小前端控制链：Contract instantiation -> generation governance -> apply -> gate / recheck
13. 方案确认 -> 交接可查 -> 执行留痕 -> 验收有新证据 -> 才能宣称完成
14. 命令名和具体 surface 统一放讲者备注或附录
15. 业务方只记住这 1 句话
16. 结尾定义：AI-SDLC 才是有状态、可续跑、可扩展的 AI 交付操作系统

## 7. 旧 19 页处置建议

以下按当前 `deliverables/ai-sdlc-training-experience/app.js` 的 19 页 slide 顺序给出处置建议。

| 旧页 | 处理 | 原因 | 去向 |
| --- | --- | --- | --- |
| 1. AI-SDLC：把 AI 编码，升级成可证明的交付系统 | 重写 | 开场不应先喊定义，应先落到真实失败场景，再在结尾回收定义 | 新第 1 页与第 16 页 |
| 2. 没有框架时，AI 交付最常见的 4 种失控 | 保留并强化 | 这是新主线的最好入口，但要加入中断续跑和旧证据失认 | 新第 2 页 |
| 3. 三条路径的差异，不在“谁更聪明”，而在“谁更能闭环” | 重写 | 比较维度可以保留，但中心要从“谁更强”改成“谁更能承受长任务” | 新第 3-5 页背景层 |
| 4. 第一次进入这套系统，只需要分清两个入口 | 降级为补充 | 入口不是主线起点，命令不应出现太早 | 附录或上手页 |
| 5. 第一次上手路径：先看真值，再做安全预演，再提交需求 | 降级为补充 | 作为操作页保留，但不应前置到主叙事前半段 | 附录或 workshop 页 |
| 6. 系统会接住你什么：不是多一个命令，而是多一层交付保障 | 重写 | 可以保留收益表达，但要改成“系统记住什么、替团队接住什么”，并明确业务账 | 新第 4-5 页 |
| 7. 为什么这些体验背后，必须是一套控制系统 | 保留并强化 | 这页适合作为前后半段桥，但现在还不够有力 | 新第 3 页 |
| 8. 系统骨架：谁负责触发，谁负责判定，谁负责阻断，谁负责回写 | 重写 | 要从静态骨架改成最小架构脊柱和动态关系 | 新第 3-6 页 |
| 9. 阶段契约：阶段不是步骤表，而是输入、产物、结论的契约 | 重写 | 保留契约感，但弱化术语密度，前置“为什么能续跑” | 新第 4-6 页 |
| 10. 组件地图与调度方式：哪些可以并行，哪些必须先被约束住 | 降级为补充 | 对非专业听众过早过深，可放技术附录 | 附录 |
| 11. 硬约束：真正不能绕过的，是正式产物、执行授权和最新验证证据 | 重写 | 内容重要，但语气仍像“门禁很多”，要改成“完成定义”和“为什么不能误报完成” | 新第 6-8 页 |
| 12. 观测面：不是多打日志，而是把证据边界诚实暴露给操作者 | 保留并强化 | 这是控制面 / 证据面的关键桥梁 | 新第 6-8 页 |
| 13. 自迭代优化：失败不是一次性的修补，而是框架能力的输入 | 保留并扩写 | 需要升级成完整模块，不再只是单页结论 | 新第 9 页 |
| 14. 前端治理案例：先看同一条受控链路，再逐张看证据渲染 | 重写 | 不应从“治理案例展示”起手，要先回答前端为什么必须受控生成，并补最小前端控制链 | 新第 10-13 页 |
| 15. 证据一：物化 effective truth | 保留但降术语密度 | 保留链路价值，但要讲成“方案确认”，命令名统一退到第 14 页或附录 | 新第 13 页与第 14 页附录 |
| 16. 证据二：只读 handoff 真值面 | 保留但降术语密度 | 保留 read-only 价值，但讲成“交接可查”，命令名统一退到第 14 页或附录 | 新第 13 页与第 14 页附录 |
| 17. 证据三：execute apply 真正落盘 | 保留但降术语密度 | 保留 execute 价值，但讲成“执行留痕”，命令名统一退到第 14 页或附录 | 新第 13 页与第 14 页附录 |
| 18. 证据四：gate receipts passed | 保留但拆成正反两例 | 不只展示 passed，要加 evidence_missing / recheck_required / transient_run_failure，命令名统一退到第 14 页或附录 | 新第 8 页与第 14 页附录 |
| 19. 最后只记住 4 件事：入口、真值、证据、回写 | 重写 | 结尾前应先给一页“业务方只记住这 1 句话”，最终定义单独收口 | 新第 15-16 页 |

## 8. 旧 deck 中应删除的中心偏差

- 不要让听众以为 AI-SDLC 的主要卖点是“门禁多”
- 不要让听众以为长上下文优化等于“大模型能吃更多”
- 不要让听众以为前端 Kernel 只是“统一组件命名”
- 不要让听众以为 Provider 只是“换个组件库皮肤”
- 不要让听众以为浏览器 gate 只是补截图
- 不要让听众以为 failure backlog 只是项目管理留痕

## 9. 下一步交付建议

下一轮不先改实现代码，先按本大纲继续产出三份东西：

1. 一份正式讲稿结构稿
2. 一份新 deck 的逐页 outline
3. 一份“旧页内容迁移表”，标明哪些旧文案可复用、哪些必须重写

完成上述三份后，再进入视觉和前端实现层。
