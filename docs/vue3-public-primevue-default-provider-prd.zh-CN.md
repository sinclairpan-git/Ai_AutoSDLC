# PRD：Vue3 Public PrimeVue 默认前端 Provider 与企业级开发规范

**文档状态**：已归档，三轮对抗评审通过  
**创建日期**：2026-06-22  
**适用仓库**：Ai_AutoSDLC  
**输入文档**：`docs/Vue3企业级前端开发规范方案.md`  
**目标版本**：下一轮前端治理版本  

## 1. 背景

当前 AI-SDLC 前端方案确认逻辑默认优先推荐 `enterprise-vue2`，当企业组件库不可用时回退到 `public-primevue`。这导致框架的默认推荐路径仍停留在 Vue2 企业私有组件库，而新的前端开发规范已经明确以 Vue3、TypeScript、PrimeVue、UnoCSS 和 CSS Variables 为核心技术栈。

本 PRD 要求将框架默认前端推荐调整为 Vue3 公共 provider 路径，并把新的企业级开发规范沉淀为 AI-SDLC 可执行、可校验、可生成的产品能力。

## 2. 产品目标

1. 将默认推荐前端 provider 从 `enterprise-vue2` 调整为 `public-primevue`。
2. 将默认前端技术栈调整为 `Vue3 + TypeScript + Vite + PrimeVue + @primeuix/themes + UnoCSS + CSS Variables`。
3. 保留 `enterprise-vue2` 作为企业私有组件库兼容路径，但不再作为普通默认首推路径。
4. 让 `program solution-confirm`、managed delivery、provider profile、生成模板和验证面使用同一套 Vue3 默认口径。
5. 将样式职责边界固化为：组件逻辑由 PrimeVue 承担，页面布局由 UnoCSS 承担，视觉统一由 CSS Variables 承担，复杂业务样式由少量普通 CSS 承担。

## 3. 非目标

1. 不在本轮引入暗黑模式。
2. 不在本轮实现复杂多主题系统。
3. 不移除 `enterprise-vue2`，也不破坏已有企业私有组件库用户的显式选择路径。
4. 不把所有推荐工具一次性升级为硬阻断，例如 husky、commitlint、Playwright 可作为增强能力逐步落地。
5. 不在 PRD 阶段生成前端实现代码。

## 4. 用户与场景

### 4.1 普通 Vue3 项目用户

用户希望初始化或确认前端方案时，框架默认给出符合现代 Vue3 企业中后台实践的组件库和样式方案，而不是先推荐 Vue2 企业私有组件库。

### 4.2 企业内网项目用户

用户仍可能需要使用 `enterprise-vue2` 私有组件库。框架必须允许用户显式选择企业 Vue2 路径，并继续执行企业 provider 的可用性检查、私有 registry 前置条件和降级说明。

### 4.3 框架维护者

维护者需要一套稳定的 provider/profile/template/verification 合同，避免“推荐口径是 Vue3、生成口径仍是 Vue2”或“文档说 UnoCSS、生成模板没有 UnoCSS”的漂移。

## 5. 产品决策

### 5.1 默认 provider 决策

默认推荐必须调整为：

| 字段 | 新默认值 |
| --- | --- |
| `frontend_stack` | `vue3` |
| `provider_id` | `public-primevue` |
| 组件库 | `PrimeVue` |
| 主题基础 | `@primeuix/themes` |
| 样式方案 | `UnoCSS + CSS Variables` |
| 默认 style pack | `modern-saas` |

本轮不新增新的默认 style pack。`public-primevue` 默认 style pack 固定为 `modern-saas`，以避免同时修改 provider 默认选择、style-support 和主题语义带来的范围膨胀。更偏企业中后台的 `enterprise-console` 可作为后续版本新增，但不得阻塞本轮默认 provider 切换。

### 5.2 企业 Vue2 兼容决策

`enterprise-vue2` 必须保留为显式选择项：

1. 当用户明确要求“框架自带 Vue2 企业级组件库”或企业私有 provider 时，推荐必须包含 `enterprise-vue2` / `vue2`。
2. 当用户选择 `enterprise-vue2` 且前置条件不满足时，框架继续给出 registry/network 等可用性诊断。
3. 从 `enterprise-vue2` 回退到 `public-primevue` 必须仍需要清晰的用户确认，避免私有组件库需求被静默替换。

## 6. 功能需求

### FR-001 默认方案确认

`program solution-confirm --dry-run` 在未显式指定前端栈和 provider 时，必须推荐：

- `frontend_stack=vue3`
- `provider_id=public-primevue`
- 组件库来源为 PrimeVue
- 样式方案为 UnoCSS + CSS Variables
- `style_pack_id=modern-saas`

该规则必须覆盖当前 `enterprise_provider_eligible=True` 的默认分支。`enterprise_provider_eligible` 不再决定普通默认推荐是否优先 `enterprise-vue2`；它只影响用户显式选择 `enterprise-vue2` 时的 availability、preflight 和诊断输出。

### FR-002 显式企业 Vue2 选择

当用户显式请求企业 Vue2 路径时，方案确认必须继续支持：

- `frontend_stack=vue2`
- `provider_id=enterprise-vue2`
- 企业私有组件库安装策略
- 企业 provider availability/preflight 诊断

### FR-002A 高级用户多方案选择

Vue3 默认推荐不得被实现成唯一方案。技术方案确认必须保留“小白默认最优 + 高级用户可选”的双层体验：

1. 普通用户默认看到 `vue3/public-primevue/modern-saas` 最优推荐。
2. 高级用户可以进入候选矩阵，查看 `public-primevue` 支持的 `enterprise-default`、`data-console`、`high-clarity`、`modern-saas`、`macos-glass` 等 style pack。
3. 显式 `vue2/enterprise-vue2/enterprise-default` 继续作为兼容路径展示，但不得因“企业后台”等场景词自动变成默认推荐。
4. CLI 和 adapter 指引必须提供 `--frontend-stack`、`--provider-id`、`--style-pack-id` 覆盖入口，避免需求确认后的技术栈推荐与自定义选择环节丢失。

### FR-003 public-primevue 依赖分层

依赖必须拆分为 provider 核心包、模板运行依赖和模板开发依赖，避免把项目模板依赖误写入 provider 核心安装契约。

#### Provider core packages

`public-primevue` 的 provider 核心安装策略必须保持聚焦，至少包含：

- `primevue`
- `@primeuix/themes`

#### Template runtime dependencies

Vue3 默认模板运行依赖必须覆盖：

- `vue-router`
- `pinia`
- `axios`
- `vue-i18n`
- `@vueuse/core`
- `dayjs`

`primeicons` 本轮不作为默认必选依赖；图标能力默认由 UnoCSS `presetIcons` 承担。若后续具体 PrimeVue 组件或主题适配需要 `primeicons`，必须在对应 spec 中作为显式依赖加入。

#### Template dev dependencies

Vue3 默认模板开发依赖必须覆盖：

- `typescript`
- `vite`
- `unocss`
- `vitest`

Playwright、ESLint、Prettier、`@antfu/eslint-config`、husky、lint-staged、commitlint 可作为增强项进入后续分阶段任务。

### FR-004 UnoCSS 默认集成

Vue3 默认 provider 的生成模板必须包含：

1. `uno.config.ts`
2. Vite 插件注册 `UnoCSS()`
3. 主入口导入 UnoCSS 生成样式
4. 基础 preset：`presetUno`、`presetIcons`、`presetTypography`

### FR-005 CSS Variables 设计 token

生成模板必须包含 `src/styles/variables.css`，并提供至少以下 token 类别：

- brand / status colors
- text colors
- border color
- radius
- shadow
- layout dimensions

框架生成的业务代码不得直接散落硬编码品牌色；可通过 token、style pack 或 provider theme adapter 映射生成。

### FR-006 PrimeVue 使用边界

框架生成的页面和业务组件不得直接散落 PrimeVue 原始组件 import。默认生成策略必须优先使用 AI-SDLC 语义组件或 Base 组件层，例如：

- `UiButton` / `BaseButton`
- `UiTable` / `BaseTable`
- `UiDialog` / `BaseDialog`
- `UiForm` / `BaseForm`

PrimeVue 原始组件只允许出现在以下位置：

1. provider adapter / runtime adapter / theme bridge。
2. `src/components/base/` 下的 Base 组件。
3. 明确标记为 provider 封装层的测试 fixture。

生成的 `src/views/` 和 `src/components/business/` 不得直接 `import ... from 'primevue/*'`。该边界必须可通过 import scan 或 AST scan 验收。

### FR-007 推荐目录结构

Vue3 默认模板必须生成或预留以下目录结构：

```text
src/
├── api/
├── assets/
├── components/
│   ├── base/
│   ├── business/
│   └── layout/
├── composables/
├── constants/
├── directives/
├── layouts/
├── plugins/
├── router/
│   ├── index.ts
│   └── modules/
├── stores/
├── styles/
│   ├── reset.css
│   ├── variables.css
│   ├── primevue.css
│   └── main.css
├── types/
├── utils/
├── views/
├── App.vue
└── main.ts
```

### FR-008 页面职责边界

生成代码和模板说明必须遵守：

1. 页面组件只负责数据请求、页面拼装、路由参数、权限控制。
2. 复杂逻辑应拆分至 composables、business components 或 stores。
3. 不生成巨型页面组件。
4. 不生成“一个 global store 承载所有业务”的状态结构。

### FR-009 TypeScript 基线

Vue3 默认模板必须启用 TypeScript strict。默认生成代码不得使用 `any` 作为业务类型兜底；确需不确定输入时应优先使用 `unknown` 并在边界处收窄。

### FR-010 API 管理规范

默认模板必须提供 API 分层约定：

- `api/http.ts`
- `api/interceptors.ts`
- `api/types.ts`
- `api/modules/`

接口命名应使用业务动词，例如 `getUserList`、`createUser`、`updateUser`、`deleteUser`，避免生成 `fetchUserApi`、`queryUserListApi` 这类重复后缀。

### FR-011 国际化基线

Vue3 默认模板必须支持 vue-i18n。框架生成的用户可见业务文案应支持通过 i18n key 管理；不应在模板中大量直接硬编码业务中文。

### FR-012 质量与验证

本轮实现必须提供测试或验证证明：

1. 默认 solution confirmation 在 `enterprise_provider_eligible=True` 和 `False` 时均推荐 `public-primevue`，除非用户显式请求企业 Vue2。
2. 显式 `enterprise-vue2` 仍可选择。
3. `public-primevue` provider core packages 仍聚焦 `primevue` 和 `@primeuix/themes`。
4. managed delivery 生成模板包含 UnoCSS 配置、CSS Variables、PrimeVue 初始化和目录结构。
5. verify constraints 或等价验证面能发现默认口径与生成口径漂移。
6. 业务 `views/` 和 `components/business/` 中的 `primevue/*` 直接 import 可被 scan 发现。

### FR-013 验证等级

本轮验证必须区分 blocker、warning 和 advisory：

| 验证项 | 等级 | 说明 |
| --- | --- | --- |
| 默认 recommendation 不是 `vue3/public-primevue` | blocker | 直接违反新默认 provider 决策 |
| 显式企业 Vue2 请求被静默切到 Vue3 | blocker | 破坏企业兼容路径 |
| confirmed/default provider 与 managed delivery 输出不一致 | blocker | 生成口径漂移 |
| Vue3 模板缺失 Vite 可运行入口、PrimeVue 初始化、UnoCSS 配置或 CSS Variables | blocker | 默认模板不可用 |
| Web smoke 出现白屏、Vite 启动失败、fatal console error 或根页面无法渲染 | blocker | 默认前端必须可运行可访问 |
| PrimeVue、UnoCSS 或 CSS Variables 在 smoke 页面未生效 | blocker | 默认技术栈未真实接入 |
| 桌面/移动关键视口截图为空、主内容不可见或明显重叠 | warning，稳定后升级为 blocker | 首版先建立视觉证据和 baseline |
| 基础键盘焦点、Dialog 开关、表单 label / aria 存在缺口 | warning | 首版纳入可访问性证据，不阻断普通生成 |
| `src/views/` 或 `src/components/business/` 直接 import `primevue/*` | warning，后续可升级为 targeted blocker | 本轮先作为可观测治理边界，避免首版过度拦截 |
| ESLint、Prettier、Playwright、husky、lint-staged、commitlint 未配置 | advisory | 本轮仅作为增强建议，不阻断普通生成 |

### FR-014 Web 与视觉测试规划

Vue3 默认 provider 的交付闭环必须包含 Web smoke、组件渲染、视觉证据和基础可访问性规划。Playwright 工具链本身可作为增强项逐步落地，但“生成后的 Vue3 前端能启动、能渲染、关键样式生效”必须作为 blocker 级验收。

#### Web smoke

默认生成前端在 managed delivery 后必须支持自动或半自动 smoke：

1. 启动 Vite dev server。
2. 打开根页面或默认路由。
3. 页面不得白屏。
4. 浏览器控制台不得出现 fatal runtime error。
5. PrimeVue plugin / theme 初始化必须成功。
6. UnoCSS 原子类必须在页面上生效。
7. `src/styles/variables.css` 中的核心 CSS Variables 必须可被页面样式引用。

#### Provider 组件渲染

Web smoke 页面或专用验证页必须至少覆盖以下组件层：

1. `UiButton` / `BaseButton`
2. `UiTable` / `BaseTable`
3. `UiDialog` / `BaseDialog`
4. `UiForm` / `BaseForm`

该验证的目的不是替代完整 E2E，而是证明 `public-primevue` provider adapter、Base 组件封装和 PrimeVue 运行时依赖能共同工作。

#### 视觉证据

首版视觉验证必须产出结构化证据，至少包含：

1. 桌面视口截图，例如 `1440x900`。
2. 移动视口截图，例如 `390x844`。
3. 截图元数据，包括 provider、style pack、viewport、时间戳和生成入口。
4. 空白页面、主内容不可见、明显遮挡或布局重叠的检查结果。

首版不要求严格 pixel diff 作为 blocker。稳定 baseline 建立后，后续版本可将关键页面 pixel diff 或视觉结构 diff 升级为 blocker。

#### 基础可访问性与交互

首版必须规划以下 warning 级检查：

1. 主要交互元素存在可见焦点态。
2. 表单控件具备 label 或等价 aria 描述。
3. Dialog 可打开、关闭，且关闭后焦点回到合理位置。
4. Button、Input、Select 等基础控件可通过键盘访问。

这些检查首版不阻断普通生成，但必须进入证据报告，为后续升级为 targeted blocker 留出路径。

## 7. 验收标准

### AC-001 默认推荐

Given 用户未显式指定前端 provider，When 运行方案确认 dry-run，Then 无论企业 provider eligibility 为 true 还是 false，输出默认推荐均为 `vue3/public-primevue`，默认 style pack 为 `modern-saas`，且样式方案包含 `UnoCSS + CSS Variables`。

### AC-002 企业 Vue2 保留

Given 用户明确要求 Vue2 企业组件库，When 运行方案确认 dry-run，Then 输出必须保留 `vue2/enterprise-vue2`，不得擅自切换到 Vue3。

### AC-003 默认生成可运行

Given 用户确认 `public-primevue` 默认方案，When 执行 managed delivery apply，Then 生成的 Vue3 前端必须具备 Vite 可运行入口、PrimeVue 初始化、UnoCSS 配置和基础样式文件。

### AC-004 样式职责清晰

Given 生成一个业务页面，When 查看代码，Then 布局优先使用 UnoCSS 原子类，品牌色和关键视觉参数通过 CSS Variables 或 style token 引用。

### AC-005 组件封装边界

Given 生成业务页面，When 扫描 `src/views/` 和 `src/components/business/`，Then 不应存在 `from 'primevue/*'` 的直接 import；页面应优先依赖语义组件、Base 组件或受控业务组件。

### AC-006 验证等级清晰

Given 默认 provider 变更进入实现，When 运行验证，Then blocker、warning、advisory 的输出必须能区分默认口径漂移、模板缺失和增强项未配置，不得把 Playwright、husky、commitlint 等增强项作为本轮普通生成 blocker。

### AC-007 文档一致性

Given 用户阅读 CLI 输出、用户指南和 provider 文档，When 比对默认推荐，Then 不应出现“文档推荐 Vue3，但 CLI 默认 Vue2”的冲突。

### AC-008 Web smoke 阻断

Given 用户确认 `public-primevue` 默认方案并生成 Vue3 前端，When 执行 Web smoke，Then Vite dev server 必须可启动，根页面必须非白屏，控制台不得出现 fatal runtime error，PrimeVue、UnoCSS 和 CSS Variables 必须真实生效。

### AC-009 视觉证据可归档

Given Web smoke 通过，When 执行视觉证据采集，Then 必须产出桌面和移动视口截图及结构化元数据；空白页面、主内容不可见和明显布局重叠必须至少以 warning 形式报告。

### AC-010 基础交互与可访问性证据

Given 生成的默认验证页包含按钮、表格、弹窗和表单，When 执行基础交互检查，Then Dialog 开关、表单 label / aria、键盘焦点和基础控件可访问性问题必须进入 warning 级证据报告。

## 8. 迁移与兼容

1. 现有 `enterprise-vue2` 用户不应被破坏。
2. 旧项目中已持久化的 solution confirmation 不应被自动改写。
3. 新默认只影响未显式选择 provider 的新确认流程。
4. 发布说明必须明确默认 provider 变更属于用户可见行为变化。
5. 如果存在历史测试假设默认推荐为 `enterprise-vue2`，需要更新为“显式企业 Vue2 场景”测试。

## 9. 风险

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 默认从企业 Vue2 切到公共 Vue3 后，企业用户感知变化过大 | 高 | 保留显式 `enterprise-vue2` 路径，并在 CLI 输出中说明如何选择 |
| UnoCSS 被纳入默认后增加依赖和学习成本 | 中 | 将 UnoCSS 作为 Vue3 默认样式引擎，但保持普通 CSS 逃逸口 |
| PrimeVue 原始组件封装不足 | 高 | 先落 Base/Ui 组件边界，再扩大业务模板生成 |
| style pack 与 CSS Variables 双轨漂移 | 高 | 要求 provider theme adapter、style pack、variables.css 使用同一 token 映射 |
| 默认前端只生成文件但无法真实启动或渲染 | 高 | 将 Web smoke 白屏、fatal console error 和关键样式未生效设为 blocker |
| 视觉测试过早采用严格 pixel diff 导致误报过多 | 中 | 首版以截图证据和结构化 warning 为主，baseline 稳定后再升级 blocker |
| i18n、lint、Playwright 一次性全硬阻断导致落地成本过高 | 中 | 使用 blocker/warning/advisory 分级；工程增强项本轮不阻断普通生成 |

## 10. 分阶段建议

### Phase 1：默认口径与确认面

- 调整默认 recommendation 为 `vue3/public-primevue`。
- 保留显式 `enterprise-vue2`。
- 更新 solution-confirm 输出、测试和文档。

### Phase 2：生成模板

- 增加 UnoCSS 配置。
- 增加 CSS Variables。
- 增加 PrimeVue 初始化。
- 增加推荐目录结构和基础 Base 组件层。

### Phase 3：验证面

- 增加默认 provider 与 managed delivery 输出一致性验证。
- 增加 token/style pack 漂移检查。
- 增加业务页面中 PrimeVue 原始组件直接 import 风险检查，首版按 warning 输出。

### Phase 4：Web 与视觉验证

- 建立 Web smoke 运行入口。
- 采集桌面和移动视口截图证据。
- 输出视觉结构 warning 和基础可访问性 warning。
- 为后续 pixel diff baseline 预留证据格式。

### Phase 5：增强工程规范

- 引入 ESLint/Prettier 推荐配置。
- 引入 Vitest 基线。
- 视项目成熟度引入 Playwright、husky、lint-staged、commitlint。

## 11. 对抗评审记录

### Round 1

**评审人设**：全球顶尖前端开发专家，对 Vue3 企业中后台、组件库治理、设计系统、样式工程和大型团队协作有严格要求。  
**结论**：不通过。  
**必须修订项**：

1. 默认 provider 切换条件必须覆盖 `enterprise_provider_eligible=True` 的当前分支。
2. 默认 style pack 不能写成 `modern-saas` 或新 style pack 二选一。
3. provider install strategy 与模板依赖必须分层。
4. Base/Ui 组件边界必须可通过 import scan 或 AST scan 验收。
5. 验证面必须区分 blocker、warning 和 advisory，避免一次性过度硬阻断。

**处理结果**：已在 Round 2 修订中落实上述 5 项。

### Round 2

**结论**：通过。  
**复评结果**：

1. `enterprise_provider_eligible=True` 已覆盖；普通默认推荐不再受企业 provider eligibility 影响。
2. 默认 style pack 已唯一固定为 `modern-saas`。
3. 依赖已拆分为 provider core packages、template runtime dependencies 和 template dev dependencies。
4. PrimeVue 原始组件 import 边界已可通过 import scan 或 AST scan 验收。
5. 验证等级已拆分为 blocker、warning 和 advisory，工程增强项不会阻断普通生成。

### Round 3

**结论**：通过。  
**复评结果**：

1. Web smoke 的 blocker 范围合理，覆盖 Vite 启动、根页面非白屏、fatal console error、PrimeVue / UnoCSS / CSS Variables 生效。
2. 技术栈生效验证已在 FR-014 与 AC-008 中闭环。
3. 视觉证据策略合理，首版要求桌面/移动截图和结构化元数据，但不把 pixel diff 过早设为 blocker。
4. 基础交互和可访问性作为 warning 合理，能沉淀证据且不会阻断普通生成。
5. FR-014、AC-008、AC-009、AC-010 与 Phase 4 保持一致。

## 12. 最终结论

本 PRD 通过三轮对抗评审，已达到进入后续正式 spec / plan / tasks 拆解的质量门槛。后续实现应以本 PRD 中的默认 provider 决策、依赖分层、组件封装边界、验证等级以及 Web/视觉测试规划为准。

## 13. 落地状态

截至本工作项执行记录，默认 provider 口径、Vue3 public-primevue 生成模板、import boundary warning、Web smoke blocker、桌面/移动视觉 evidence、基础交互和可访问性 warning evidence 均已进入实现与验证范围。

当前首版质量等级保持如下：

- blocker：默认 provider 漂移、显式企业 Vue2 被静默切换、生成模板关键文件缺失、Web smoke 白屏、browser console error、browser page error。
- warning / advisory：PrimeVue 原始组件业务层直接 import、桌面/移动视觉结构风险、横向溢出、Button/Input/Select/Dialog/Form 覆盖不足、Dialog close/focus return 风险、表单 label/aria 缺失、键盘焦点可见性问题。
- advisory：ESLint、Prettier、Playwright 完整用例、husky、lint-staged、commitlint 等工程增强项在本工作项中不作为普通生成 blocker。
