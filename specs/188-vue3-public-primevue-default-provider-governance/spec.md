# 功能规格：Vue3 public-primevue default provider governance

**功能编号**：`188-vue3-public-primevue-default-provider-governance`  
**创建日期**：2026-06-22  
**状态**：草稿  
**输入**：`docs/vue3-public-primevue-default-provider-prd.zh-CN.md`、`docs/Vue3企业级前端开发规范方案.md`

## 范围

本工作项承接已归档 PRD，将 AI-SDLC 默认前端 provider 从 `enterprise-vue2` 调整为 `vue3/public-primevue`，并把 Vue3 企业级前端开发规范落成可生成、可验证、可追责的框架能力。

覆盖范围：

1. 默认方案确认：未显式选择 provider 时推荐 `frontend_stack=vue3`、`provider_id=public-primevue`、`style_pack_id=modern-saas`。
2. 企业 Vue2 兼容：用户显式要求 Vue2 企业组件库时继续支持 `enterprise-vue2`，并保留 availability/preflight 诊断与显式 fallback 确认。
3. 依赖分层：区分 provider core packages、template runtime dependencies、template dev dependencies。
4. Vue3 默认模板：落地 PrimeVue、`@primeuix/themes`、UnoCSS、CSS Variables、推荐目录结构、Base/Ui 组件封装边界。
5. 组件治理：业务 `views/` 与 `components/business/` 不直接 import `primevue/*`，PrimeVue 原始组件集中在 provider adapter、theme bridge 或 `components/base/`。
6. 验证分级：输出 blocker、warning、advisory，避免把增强工程项过早作为普通生成阻断。
7. Web/视觉测试规划：Web smoke 作为 blocker；桌面/移动截图、基础交互和可访问性作为首版 warning 证据。
8. 文档一致性：CLI、用户指南、provider 文档、测试断言与 PRD 口径一致。

明确不覆盖：

1. 不删除 `enterprise-vue2`。
2. 不在本工作项中新增 `enterprise-console` 默认 style pack；`public-primevue` 默认 style pack 固定为 `modern-saas`。
3. 不把严格 pixel diff 在首版作为 blocker。
4. 不把 Playwright、husky、lint-staged、commitlint、完整 ESLint/Prettier 体系作为首版普通生成 blocker。
5. 不在 spec 阶段直接修改实现代码；实现必须由 `tasks.md` 中 executable task 驱动。

## 用户场景与验收

### 用户故事 1 - 普通项目默认进入 Vue3 public-primevue（优先级：P0）

作为普通 AI-SDLC 用户，我希望未显式指定前端 provider 时，框架默认推荐 Vue3 公共组件库路径，以便生成结果符合新的 Vue3 企业级前端规范。

**独立测试**：构造默认 solution confirmation dry-run，分别覆盖 `enterprise_provider_eligible=True` 与 `False`，断言默认推荐均为 `vue3/public-primevue/modern-saas`，除非用户显式请求企业 Vue2。

**验收场景**：

1. **Given** 用户没有显式指定 frontend stack/provider/style pack，**When** 执行方案确认 dry-run，**Then** recommendation、requested 和 effective 默认值均指向 `vue3/public-primevue/modern-saas`。
2. **Given** `enterprise_provider_eligible=True`，**When** 用户未显式请求企业 Vue2，**Then** eligibility 不得把默认推荐切回 `enterprise-vue2`。
3. **Given** 用户显式请求 `enterprise-vue2`，**When** 运行 dry-run，**Then** 框架必须保留企业 Vue2 路径和可用性诊断，不得静默切到 Vue3。

### 用户故事 2 - Vue3 模板遵守 PrimeVue + UnoCSS + CSS Variables 规范（优先级：P0）

作为前端开发者，我希望 managed delivery 生成的 Vue3 项目具备稳定目录结构、样式职责分层和组件封装边界，以便后续业务开发不会从第一步就违背规范。

**独立测试**：managed delivery 生成快照或文件系统 fixture 验证 `uno.config.ts`、Vite UnoCSS 插件、PrimeVue 初始化、`src/styles/variables.css`、目录结构和 Base/Ui 组件层。

**验收场景**：

1. **Given** 用户确认默认 `public-primevue`，**When** 执行 managed delivery apply，**Then** 生成模板必须包含 Vite 可运行入口、PrimeVue 初始化、UnoCSS 配置、CSS Variables 和推荐目录结构。
2. **Given** 生成业务页面，**When** 扫描 `src/views/` 与 `src/components/business/`，**Then** 不得存在直接 `primevue/*` import；PrimeVue 原始组件只能出现在受控封装层。
3. **Given** 生成样式代码，**When** 检查品牌色和关键视觉参数，**Then** 必须通过 CSS Variables、style token 或 provider theme adapter 引用。

### 用户故事 3 - Web smoke 证明生成前端真实可运行（优先级：P0）

作为框架维护者，我希望 Vue3 默认前端不仅生成文件，还能启动、渲染并加载关键样式，以便默认 provider 切换不会产生“看似成功但白屏”的交付风险。

**独立测试**：在生成后的 managed frontend 上启动 Vite dev server，打开根页面或默认路由，检查非白屏、无 fatal console error、PrimeVue/UnoCSS/CSS Variables 生效。

**验收场景**：

1. **Given** 生成 Vue3 默认前端，**When** 运行 Web smoke，**Then** Vite dev server 必须可启动且根页面可访问。
2. **Given** 浏览器打开默认页面，**When** 收集控制台日志，**Then** 不得出现 fatal runtime error。
3. **Given** smoke 页面渲染，**When** 检查 DOM 与 computed style，**Then** PrimeVue、UnoCSS 原子类和核心 CSS Variables 必须真实生效。

### 用户故事 4 - 视觉证据和基础交互/a11y 可追踪（优先级：P1）

作为质量负责人，我希望首版生成桌面/移动截图和基础交互证据，但不因不稳定 pixel diff 过早阻断普通生成，以便先建立视觉 baseline 再逐步提高门槛。

**独立测试**：采集 `1440x900` 与 `390x844` 截图，输出 provider/style pack/viewport/时间戳/生成入口元数据，并报告空白、主内容不可见、明显重叠、焦点态、Dialog 开关、表单 label/aria 等 warning。

**验收场景**：

1. **Given** Web smoke 通过，**When** 执行视觉证据采集，**Then** 必须产出桌面与移动视口截图及结构化元数据。
2. **Given** 截图为空、主内容不可见或明显重叠，**When** 生成报告，**Then** 必须以 warning 输出，后续 baseline 稳定后可升级为 blocker。
3. **Given** 默认验证页包含按钮、表格、弹窗和表单，**When** 执行基础交互检查，**Then** Dialog 开关、键盘焦点、表单 label/aria 问题必须进入 warning 证据报告。

## 需求

- **FR-188-001**：默认 solution confirmation 必须推荐 `frontend_stack=vue3`、`provider_id=public-primevue`、`style_pack_id=modern-saas`。
- **FR-188-002**：`enterprise_provider_eligible` 不得决定普通默认推荐是否优先 `enterprise-vue2`；它只影响显式企业 Vue2 路径的诊断。
- **FR-188-003**：用户显式请求 `enterprise-vue2` 时，框架必须保留 `vue2/enterprise-vue2` 路径、企业安装策略和 preflight 诊断。
- **FR-188-004**：`public-primevue` provider core packages 必须聚焦 `primevue` 与 `@primeuix/themes`。
- **FR-188-005**：Vue3 template runtime dependencies 必须覆盖 `vue-router`、`pinia`、`axios`、`vue-i18n`、`@vueuse/core`、`dayjs`。
- **FR-188-006**：Vue3 template dev dependencies 必须覆盖 `typescript`、`vite`、`unocss`、`vitest`。
- **FR-188-007**：`primeicons` 本轮不得作为默认必选依赖；图标能力默认由 UnoCSS `presetIcons` 承担，后续需要时通过独立 spec 显式加入。
- **FR-188-008**：Vue3 模板必须生成 `uno.config.ts`，并在 Vite 插件中注册 `UnoCSS()`。
- **FR-188-009**：Vue3 模板必须包含 `src/styles/variables.css`，覆盖 brand/status colors、text colors、border、radius、shadow、layout dimensions。
- **FR-188-010**：Vue3 模板必须包含推荐目录结构：`api/`、`components/base/`、`components/business/`、`components/layout/`、`composables/`、`router/modules/`、`stores/`、`styles/`、`types/`、`utils/`、`views/`。
- **FR-188-011**：生成的业务 `views/` 和 `components/business/` 不得直接 import `primevue/*`；允许位置限定为 provider adapter/runtime adapter/theme bridge、`components/base/`、明确标记的 provider fixture。
- **FR-188-012**：验证输出必须区分 blocker、warning、advisory。
- **FR-188-013**：默认 recommendation 漂移、显式企业 Vue2 被静默切换、confirmed/default provider 与 managed delivery 输出不一致、Vue3 模板关键文件缺失必须作为 blocker。
- **FR-188-014**：Web smoke 中 Vite 启动失败、根页面白屏、fatal console error、PrimeVue/UnoCSS/CSS Variables 未生效必须作为 blocker。
- **FR-188-015**：桌面/移动截图为空、主内容不可见、明显遮挡或布局重叠首版作为 warning，并保留升级 blocker 的证据格式。
- **FR-188-016**：基础键盘焦点、Dialog 开关、表单 label/aria 问题首版作为 warning，并进入结构化证据报告。
- **FR-188-017**：ESLint、Prettier、Playwright、husky、lint-staged、commitlint 未配置在本轮为 advisory，不阻断普通生成。
- **FR-188-018**：CLI 输出、用户指南、provider 文档、测试断言必须与默认 `vue3/public-primevue/modern-saas` 口径一致。
- **FR-188-019**：旧项目中已持久化的 solution confirmation 不得被自动改写；新默认只影响未显式选择 provider 的新确认流程。
- **FR-188-020**：发布说明必须明确默认 provider 变更属于用户可见行为变化，并说明如何显式选择 `enterprise-vue2`。

## 成功标准

- **SC-188-001**：默认 solution confirmation 在 enterprise eligibility true/false 下均推荐 `vue3/public-primevue/modern-saas`。
- **SC-188-002**：显式 `enterprise-vue2` 场景仍保留企业路径和诊断。
- **SC-188-003**：managed delivery 生成 Vue3 模板包含 PrimeVue 初始化、UnoCSS 配置、CSS Variables、推荐目录结构和 Base/Ui 封装层。
- **SC-188-004**：业务 `views/` 与 `components/business/` 的 `primevue/*` 直接 import 可被 scan 检出并按 warning 报告。
- **SC-188-005**：Web smoke 能启动 Vite、打开根页面、证明非白屏、无 fatal console error、PrimeVue/UnoCSS/CSS Variables 生效。
- **SC-188-006**：视觉证据包含桌面/移动截图、元数据和 warning 结构。
- **SC-188-007**：基础交互/a11y warning 证据覆盖 Dialog、表单 label/aria、键盘焦点和基础控件。
- **SC-188-008**：verify constraints 或等价 gate 可发现默认口径、生成模板、Web smoke 与文档口径漂移。
- **SC-188-009**：PRD、spec、plan、tasks、用户文档和 release note 口径一致。
