# Vue3 企业级前端开发规范方案 v1.3（AI 执行版）

## 1. 目标

本规范用于约束 AI 直接产出可落地、可维护、可机械化收口的 Vue3 前端代码。

默认目标不是“先做出来”，而是“按统一技术方案、统一视觉语言、统一工程边界做出来”，并让后续 SDLC 的生成、验证、修复和交付闭环可以稳定复用。

## 2. 默认技术方案

除非用户明确指定其他方案，否则默认采用：

- `Vue3 + TypeScript + Vite`
- `PrimeVue + @primeuix/themes + primeicons`
- `definePreset(Aura) + darkModeSelector=false`
- 主色固定为 `#1770e6`
- `UnoCSS + CSS Variables`
- `Pinia + Vue Router + Axios`
- `vee-validate + zod`
- `vue-i18n`
- `Vitest + Playwright + ESLint + Prettier + husky + lint-staged + commitlint`

## 3. 页面视觉规则

### 3.1 必须遵守

- 导航容器属于页面内容体系的一部分。
- 左侧导航和顶部导航都允许使用，但不同导航形态不得出现风格强割裂。
- 页面内导航、页头、卡片、标签、按钮、筛选器必须属于同一视觉家族。
- 导航激活态、页头胶囊、badge、按钮、标签必须共享 `#1770e6` 的语义高亮。
- 同一筛选区内输入框、下拉框、按钮必须统一高度、圆角、边框和 focus 态。

### 3.2 明确禁止

- 左侧深色导航 + 右侧浅色品牌内容区。
- 顶部导航一套中性色，内容区另一套蓝色体系。
- 黑色 `contrast` 标签和浅色品牌标签大面积同屏混用。
- 原生 `select` 与 PrimeVue 输入框并排使用导致明显割裂。
- 深色块滥用于普通卡片、筛选区、导航区。

## 4. 主题与组件规则

默认优先级为：

1. `PrimeVue Theme Token`
2. 基础组件封装
3. `UnoCSS` 布局与间距
4. 页面局部样式补充

不要直接在页面里散落大量颜色值，不要用零散业务 CSS 全局覆盖 PrimeVue 基础外观，也不要让同一页面出现两套圆角、边框、阴影体系。

### 4.1 基础组件封装规则

统一使用组件库后，仍然需要对高频基础控件进行 `Base` 层收口，但不要机械地把所有组件都封一层。

优先封装：

- 高频复用组件
- 有统一视觉规则的组件
- 有统一交互规则的组件
- 未来可能需要全局调整的组件

典型高优先级组件：

- `Button`
- `InputText`
- `Select`
- `Tag`
- `Dialog`
- 表单项外壳

不要做：

- 不要只是透传组件库原参数而没有新增统一价值。
- 不要把明显属于业务语义的组件错误塞进 `Base` 层。
- 不要因为已经统一了组件库，就放弃统一组件用法。

### 4.2 按钮与标签统一规则

- 主操作按钮默认走品牌蓝主按钮或品牌蓝强调按钮。
- 不要在同一产品内长期混用蓝色主操作和绿色主操作。
- 可见性、风险、状态标签应拆分类处理，不要全部压成一个 `warn`。
- 标签映射应优先进入统一业务组件，而不是页面局部直接写 `severity`。

## 5. 国际化规则

所有新增用户可见中文文案，开发阶段统一写成：

```vue
$i('中文')
```

不要直接写裸中文，也不要一上来就手写英文 key。

必须包 `$i(...)` 的内容：

- 页面标题
- 按钮文案
- `label`
- `placeholder`
- 空状态
- 错误提示
- 成功提示
- tooltip
- 标签文案
- 表格列标题
- 弹窗标题
- tabs 文案

不要包 `$i(...)` 的内容：

- 变量名
- 枚举值
- 接口字段
- 路由 name
- 权限码
- 埋点字段
- 调试日志

允许的开发期最终态：

```vue
$i('新建模板')
```

若当前文件已经是稳定 key 体系，只延续既有 key，不回退成裸中文。不要擅自把 `$i('中文')` 改成其他运行时 API，除非用户明确要求。

## 6. AI 输出禁令

- 不要直接翻译成英文文案。
- 不要直接发明大量 `user.title`、`page.header.name` 之类的 key。
- 不要把视觉优化只做在左侧导航，遗漏顶部导航、badge、胶囊、筛选器。
- 不要一边统一按钮风格，一边放任标签和输入框继续使用旧风格。
- 不要引入未经确认的第二套组件库。
- 不要为了省事回退到原生表单控件。

## 7. 推荐目录结构

```text
src/
├── api/
│   ├── http.ts
│   ├── interceptors.ts
│   ├── types.ts
│   └── modules/
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
│   └── main.css
├── types/
├── utils/
├── views/
├── theme.ts
├── App.vue
└── main.ts
```

## 8. 实现约束

### 8.1 目录与职责

- 页面只负责组装，不承载大段基础交互封装。
- 高频基础控件优先进入 `Base` 层。
- 业务语义组件进入 `Business` 层。
- 不要在页面文件里重复声明大量公共类型和公共状态逻辑。

### 8.2 样式与主题

- `UnoCSS` 负责布局与间距。
- `CSS Variables` 负责品牌与壳层变量。
- `PrimeVue Theme` 负责基础组件视觉 token。
- 不要用页面 CSS 大面积覆盖 `.p-button`、`.p-inputtext`、`.p-select`、`.p-tag`。

`src/styles/variables.css` 至少保留以下 token 组：

```css
:root {
  /* colors */
  --app-primary: #1770e6;
  --app-success: #22c55e;
  --app-warning: #f59e0b;
  --app-danger: #ef4444;

  /* text */
  --app-text-primary: #111827;
  --app-text-secondary: #6b7280;

  /* border */
  --app-border-color: #e5e7eb;

  /* radius */
  --app-radius-sm: 4px;
  --app-radius-md: 8px;
  --app-radius-lg: 12px;

  /* shadow */
  --app-shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);

  /* layout */
  --app-header-height: 56px;
  --app-sidebar-width: 220px;
}
```

### 8.3 TypeScript、Pinia、路由、API

- 默认开启 `TypeScript strict`。
- 不用 `any` 兜底业务类型；不确定输入优先用 `unknown` 并在边界处收窄。
- store 按领域拆分，不要生成超级大 store。
- 路由按 `router/modules` 拆分。
- API 按 `api/modules` 拆分。
- 接口命名优先使用 `get/create/update/delete`。

### 8.4 表单控件与筛选区

- 同一筛选区内统一高度、圆角、边框、focus 态。
- 能用 PrimeVue 同家族控件时，优先不用原生控件混搭。
- 不要让输入框、按钮、下拉框分别维持三套不同外观。

## 9. 提交前检查

提交前至少确认：

- 所有新增可见中文是否已包 `$i(...)`。
- 是否存在导航与内容区风格割裂。
- 是否存在标签、按钮、输入框三套不同视觉语言。
- 是否仍残留黑色 `contrast` 标签滥用。
- 是否仍残留原生 `select`。
- 是否仍存在页面私有大面积基础组件样式覆盖。
- 是否已形成 `Base / Business / View` 基本分层。
- store、router、api 是否仍然集中堆在单文件内。

## 10. 工程化与提交规则

多人协作项目默认应补齐以下工具链：

- `husky`
- `lint-staged`
- `commitlint`
- `ESLint`
- `Prettier`

AI 在生成项目规范、初始化方案或工程化建议时，不要遗漏这部分基础约束。

默认要求：

- 提交前运行 `lint-staged`。
- 禁止提交存在 lint 错误的代码。
- `commit message` 至少遵循 `feat:`、`fix:`、`docs:`、`refactor:`、`style:`、`test:`。
- 不要把格式化噪音和业务改动混成一次不可读提交。

推荐安装依赖时，不要遗漏：

- `vue-router`
- `pinia`
- `axios`
- `primevue`
- `primeicons`
- `@primeuix/themes`
- `vee-validate`
- `zod`
- `vue-i18n`
- `@vueuse/core`
- `dayjs`
- `typescript`
- `vite`
- `unocss`
- `eslint`
- `prettier`
- `husky`
- `lint-staged`
- `@commitlint/cli`
- `@commitlint/config-conventional`
- `playwright`

## 11. 输出口径

如果用户让你实现页面：

- 先按本规范产出代码。
- 国际化先用 `$i('中文')`。
- 技术栈、组件库和 style pack 仍必须先经过前端方案确认。

如果用户让你写规范或约束：

- 优先保证规则明确、动作可执行、边界清晰。
- 不要把规范写成泛泛而谈的设计描述。

## 12. 与旧版规范差异评估

| 维度 | 旧版仓库规范 | v1.3 优化后要求 | SDLC 升级动作 |
| --- | --- | --- | --- |
| 默认技术栈 | 已确认 `vue3/public-primevue/modern-saas` | 保持不变，明确 `PrimeVue + @primeuix/themes + primeicons` 和 `#1770e6` | 不改变默认 provider，只强化规范 |
| 视觉一致性 | 强调 token 与 UnoCSS，但禁止项不够具体 | 明确导航、页头、badge、按钮、标签、筛选器属于同一视觉家族 | 进入生成 hard rules 与 PRD 验收 |
| Base / Business 分层 | 已有 Base 组件边界 | 补充优先封装对象和“不机械全封装”边界 | 进入规范与生成规则 |
| 国际化 | 旧版偏向 vue-i18n / key 管理 | 开发期新增可见中文先写 `$i('中文')`，稳定 key 体系继续沿用 | PRD 从泛化 i18n 改成开发期执行规则 |
| 表单控件 | 已建议 PrimeVue | 明确禁止原生 `select` 与 PrimeVue 输入框混搭 | 进入生成 hard rules |
| 工程化 | ESLint/Prettier/Vitest/Playwright 已是默认基线，husky 等是增强项 | 多人协作默认补齐 `husky + lint-staged + commitlint` | 升级模板 dev dependencies；验证等级仍为 advisory |
