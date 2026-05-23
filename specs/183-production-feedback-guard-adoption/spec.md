# 功能规格：生产反馈驱动的任务守卫、注释规范与半途接入优化

**功能编号**：`183-production-feedback-guard-adoption`
**创建日期**：2026-05-23
**状态**：草稿
**输入**：基于 `docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md` 中已通过两个对抗 agent 二轮评审的生产反馈归档，拆分并落地：废弃 `verified_loaded` 主路径用户口径、next executable task 守卫、tasks executable schema、注释与原注释保护、简体中文 UTF-8 防乱码、brownfield adopt 半途接入。

**范围**：本功能覆盖 AI-SDLC 对生产反馈的治理闭环：写代码前的可执行任务守卫、任务格式可解析化、注释与中文编码质量底线、已有项目半途接入。本文不要求外部 IDE / AI 宿主提供无法返回的加载证明，不实现对第三方 IDE 的宿主协议改造，不迁移或覆盖用户已有任务系统。

## 用户场景与测试

### 用户故事 1 - 写代码前自动绑定可执行任务（优先级：P0）

作为使用 AI-SDLC 的开发者，我希望 AI 在修改产品代码前自动确认当前可执行任务，以便避免只根据 `spec.md` 或聊天上下文直接脑补实现。

**优先级说明**：这是用户反馈中最直接的生产风险；如果不先解决，`spec / plan / tasks` 约束仍会在 AI coding 入口被绕过。

**独立测试**：构造只有 `spec.md`、模板 `tasks.md`、缺 active work item、有可执行任务、diff 超出 scope 等夹具，验证 guard 输出、自动补任务行为和 postflight 结果。

**验收场景**：

1. **Given** 项目只有 `spec.md` 且用户要求实现，**When** AI-SDLC 执行代码前检查，**Then** 不得修改产品代码，必须先自动补最小 `plan.md / tasks.md` 或创建最小 work item。
2. **Given** `tasks.md` 只有模板或占位字段，**When** 用户要求写代码，**Then** 该任务不得被判定为 executable task。
3. **Given** 存在可执行任务 Txx，**When** AI 修改代码，**Then** 修改范围必须匹配 Txx 的 `scope / acceptance / verify`，并在 postflight 写入执行日志。
4. **Given** 用户要求紧急小修，**When** 缺少任务上下文，**Then** AI-SDLC 自动创建包含文件范围、验收标准和验证方式的极简 task，而不是直接改代码。

### 用户故事 2 - 生成代码时保护注释、语言和编码质量（优先级：P0）

作为维护者，我希望 AI 生成或修改代码时保留原有有价值注释、补充必要注释，并避免中文乱码或繁体混入，以便降低 AI 代码对长期维护性的破坏。

**优先级说明**：注释缺失、误删和中文乱码是高频反馈，且会直接降低用户对 AI-SDLC 的信任。

**独立测试**：构造 Java、Go、Python、Vue2、JavaScript、TypeScript 代码样例，覆盖必要注释、噪音注释、原注释保护、中文/英文沟通语言、UTF-8/BOM/mojibake/简繁检查。

**验收场景**：

1. **Given** 文件中已有业务规则注释，**When** AI 修改附近逻辑，**Then** 默认保留并同步更新该注释，不得无理由删除。
2. **Given** 新增复杂业务规则、边界条件、安全或并发逻辑，**When** AI 生成代码，**Then** 必须补充必要注释，且不得写复述代码的噪音注释。
3. **Given** 用户主要使用中文沟通，**When** AI 新增注释，**Then** 注释必须为简体中文且无乱码。
4. **Given** 用户主要使用英文沟通，**When** AI 新增注释，**Then** 注释必须为英文。
5. **Given** 新增或修改中文文本，**When** 执行质量检查，**Then** 检查应覆盖 UTF-8 解码、BOM、替换字符、常见 mojibake pattern 和新增中文片段的简繁风险。

### 用户故事 3 - 已有项目半途接入并从当前进度继续（优先级：P0）

作为已有项目用户，我希望 AI-SDLC 能读取我已有的 JSON 任务进度、README、TODO、commit 和 diff，并自动生成接入映射与继续点，以便不用学习 checkpoint、stage、reconcile 等内部概念。

**优先级说明**：半途接入是生产用户真实使用路径。如果只能从 0、1 步重新开始，AI-SDLC 会被绕开。

**独立测试**：构造 `progress.json`、markdown TODO、issue export、多个 in-progress task、无法识别 JSON、低置信任务、超大目录等夹具，验证 adopt 扫描、置信度、映射、不覆盖原文件和继续点推荐。

**验收场景**：

1. **Given** 项目存在 `progress.json`，**When** 用户要求接入已有项目，**Then** AI-SDLC 生成 adoption map、桥接 work item、任务状态映射和建议继续点，且不修改原 JSON。
2. **Given** 多个任务处于进行中，**When** 生成继续点，**Then** 优先选择与当前 diff、最近 commit、最近更新时间和依赖状态最相关的任务。
3. **Given** JSON 无法稳定识别，**When** 执行 adopt，**Then** 低置信任务进入 `needs-review`，系统仍应基于 README、commit、diff 或用户当前需求生成临时继续点。
4. **Given** 用户不确认接入摘要，**When** adopt 继续处理，**Then** 高置信映射保留为候选，中低置信不作为 active task，流程不应直接失败。

## 边界情况

- 外部 AI 宿主无法提供 `AGENTS.md` 已加载证明时，不应阻塞用户；只调整用户口径和 workflow guard。
- `tasks.md` 文件存在但字段缺失、重复 task id、状态无效或仍含占位文本时，不可执行。
- Postflight diff 可包含测试、文档、快照、迁移和配置等伴随文件，但必须被任务规则允许或记录为范围变更。
- 项目原本使用繁体中文、GBK 或特殊编码时，检查应尊重项目配置并提示风险，不做全仓库强制清洗。
- Adopt 扫描必须忽略 `node_modules/`、`dist/`、`build/`、`vendor/`、`.git/` 等目录，避免性能灾难。
- 用户原始任务系统只能引用和映射，不得覆盖或迁移。

## 需求

### 功能需求

- **FR-001**：系统必须将 Codex / Cursor / VS Code / Claude Code 等无法回传宿主加载证明的 adapter 从用户主路径的 `verified_loaded` 要求中移除。
- **FR-002**：系统必须保留内部诊断能力，但普通用户文案不得把“无法验证宿主加载”呈现为失败或待处理阻塞。
- **FR-003**：系统必须提供 next executable task guard，在修改产品代码前执行 preflight。
- **FR-004**：系统必须定义机器可解析的 executable task schema，覆盖 task id、状态、目标、scope、acceptance、verify 和 notes。
- **FR-005**：系统必须识别模板任务、占位任务、字段缺失任务和 `needs-review` 任务，并禁止其作为 active executable task。
- **FR-006**：系统必须支持 guard during 阶段约束改动范围，并在发现超出 scope 时要求更新任务或取得最小确认。
- **FR-007**：系统必须支持 guard postflight，检查 git diff 与任务 scope / acceptance 的映射，并同步 execution log。
- **FR-008**：系统必须在缺 active work item、缺 `plan.md / tasks.md`、紧急小修等场景自动准备最小任务，而不是只停止。
- **FR-009**：系统必须在注释规范中区分内部规则与用户可见承诺，避免把完整企业规范原样暴露给普通用户。
- **FR-010**：系统必须保护已有有价值注释，默认不得无理由删除；删除或改写时必须记录原因。
- **FR-011**：系统必须要求复杂逻辑、业务规则、边界条件、安全、并发、缓存、事务、外部协议和临时方案补充必要注释。
- **FR-012**：系统必须禁止复述代码、机械逐行解释、过期矛盾注释和无原因 TODO。
- **FR-013**：系统必须按用户当前或近期主要沟通语言生成新增注释；无法判断时默认简体中文。
- **FR-014**：系统必须按 Java、Go、Python、Vue2、JavaScript、TypeScript 的不同特点落地注释规则，并避免对内部普通方法或类型已清晰的 TypeScript 字段制造噪音注释。
- **FR-015**：系统必须提供中文与编码检查，覆盖 UTF-8 解码、BOM、替换字符、常见 mojibake pattern 和新增中文片段的简繁风险。
- **FR-016**：系统必须支持白名单和项目级语言/编码例外，避免误伤历史文件、专有名词或繁体项目。
- **FR-017**：系统必须提供“接入已有项目”能力，扫描 JSON 任务进度、README、TODO、issue export、branch、diff、最近 commit、测试和项目结构。
- **FR-018**：系统必须生成 adoption map，将外部任务 id、状态、来源文件、置信度映射到 AI-SDLC task。
- **FR-019**：系统必须按高 / 中 / 低置信度处理 adopt 结果：高置信自动导入，中置信摘要确认，低置信进入 `needs-review` 且不可作为 active task。
- **FR-020**：系统必须在多个进行中任务存在时，根据 diff、commit、更新时间和依赖状态推荐继续点。
- **FR-021**：系统必须保证 adopt 不覆盖用户原 JSON 或原任务系统，只生成映射和桥接产物。
- **FR-022**：系统必须在 JSON 无法识别时降级从 README、commit、diff 或当前需求生成临时继续点，而不是直接失败。

### 关键实体

- **ExecutableTask**：从 `tasks.md` 解析出的可执行任务，包含 id、状态、目标、scope、acceptance、verify、notes。
- **TaskGuardResult**：代码修改前、中、后的守卫结果，包含 allow/block、原因、推荐自动动作和用户可见文案。
- **CommentPolicy**：按语言和技术栈组合出的注释要求，区分必要注释、禁止注释和原注释保护。
- **TextEncodingFinding**：中文与编码检查结果，包含类型、文件、片段、是否可自动修复。
- **AdoptionSource**：已有项目事实源，例如 JSON、README、TODO、issue export、git diff、commit。
- **AdoptionMap**：外部任务到 AI-SDLC task 的映射，包含外部 id、AI-SDLC task id、状态、来源、置信度。

## 成功标准

### 可度量结果

- **SC-001**：给定无法提供宿主加载证明的 Codex adapter，用户主路径不再展示失败或待验证阻塞。
- **SC-002**：给定只有 `spec.md` 的项目，代码修改前 guard 自动准备最小任务，不直接改产品代码。
- **SC-003**：给定模板 `tasks.md` 或缺字段任务，guard 判定为不可执行。
- **SC-004**：给定可执行任务，guard preflight / during / postflight 均能输出稳定结果。
- **SC-005**：给定 diff 超出任务 scope，postflight 能阻断或要求更新任务。
- **SC-006**：给定已有注释的代码修改，系统默认保留有价值注释，并在删除时要求记录原因。
- **SC-007**：给定复杂逻辑新增，review 或检查能发现缺少必要注释。
- **SC-008**：给定简单显然逻辑，规则不会要求机械噪音注释。
- **SC-009**：给定中文用户沟通场景，新增注释为简体中文。
- **SC-010**：给定英文用户沟通场景，新增注释为英文。
- **SC-011**：给定中文乱码、BOM、替换字符、常见 mojibake 样例，检查能稳定识别。
- **SC-012**：给定繁体项目或白名单专有名词，中文检查不误报阻塞。
- **SC-013**：给定 `progress.json`，adopt 能生成 adoption map、bridge docs 和继续点，且不修改原 JSON。
- **SC-014**：给定多个进行中任务，adopt 能按 diff / commit / 更新时间 / 依赖状态推荐继续点。
- **SC-015**：给定无法识别 JSON，adopt 能降级生成临时继续点。
- **SC-016**：两个对抗 agent 对 spec / plan / tasks 评审无必须修订项后，才允许进入实现。
