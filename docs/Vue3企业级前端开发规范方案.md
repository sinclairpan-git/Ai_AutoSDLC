# Vue3企业级前端开发规范方案 v1.8（AI执行版）

## 1. 目标

本规范用于约束 AI 直接输出可落地的 Vue3 前端代码与工程化配置。

`v1.8` 用于在完整继承 `v1.7.1` 的前提下，新增页面信息载体一致性约束。

AI 必须把“规范正文”“可选建议”“已经落地”三者严格区分。

## 2. 默认技术方案

除非用户明确指定其他方案，否则默认采用：

- `frontend_stack=vue3`
- `provider_id=public-primevue`
- `style_pack_id=modern-saas`

并同时具备以下技术栈：

- `Vue3 + TypeScript + Vite`
- `PrimeVue + @primeuix/themes + primeicons`
- `definePreset(Aura) + darkModeSelector=false`
- 主色固定为 `#1770e6`
- `UnoCSS + CSS Variables`
- `Pinia + Vue Router + Axios`
- `vee-validate + zod`
- `vue-i18n`（仅在项目启用国际化时接入）
- `Playwright`
- `ESLint + Prettier + husky + lint-staged + commitlint`

## 3. 工程化边界

当用户说“这是前端项目的约束”时，默认按前端子项目边界落地，不自动扩大为整个宿主仓库约束。

AI 必须区分：

- 哪些能力是 Git 宿主级能力
- 哪些文件约束可以收敛到前端子项目
- 哪些配置值是当前项目真实落地值

## 4. 主题、壳层与视觉规则

### 必须遵守

- 主题必须通过 `definePreset` 统一收口
- 主题必须同时定义 `primary`、`surface`、`highlight`
- 页面壳层、导航容器、页头胶囊必须与内容区属于同一视觉家族
- 导航激活态、badge、按钮、标签必须共享 `#1770e6` 的语义高亮
- 左侧导航和顶部导航都允许使用，但都必须采用浅色品牌承载逻辑
- 浅色页面中的普通信息载体必须与页面主体保持同一视觉体系

### 明确禁止

- 左侧深色导航 + 右侧浅色品牌内容区
- 导航和内容区像两个不同产品
- 黑色 `contrast` 标签和浅色品牌标签大面积同屏混用
- 主题未收口时继续靠业务 CSS 给 PrimeVue 组件打补丁
- 用 `!important` 批量压制 PrimeVue 默认样式
- 破坏“浅色页面中的普通信息载体必须与页面主体保持同一视觉体系”这一约束

### 默认主题基线

生成或调整主题时，默认对齐以下结构：

```ts
import Aura from '@primeuix/themes/aura';
import { definePreset } from '@primeuix/themes';

export const AppPreset = definePreset(Aura, {
    semantic: {
        primary: {
            50: '#eef6ff',
            100: '#d9ebff',
            200: '#bddcff',
            300: '#90c6ff',
            400: '#5ca6ff',
            500: '#1770e6',
            600: '#1159b8',
            700: '#0f468d',
            800: '#123d73',
            900: '#17345f',
            950: '#10213f',
        },
        colorScheme: {
            light: {
                surface: {
                    0: '#ffffff',
                    50: '#f6faff',
                    100: '#edf4fb',
                    200: '#d9e5f2',
                    300: '#c1d3e6',
                    400: '#99abc4',
                    500: '#72829a',
                    600: '#5d6c84',
                    700: '#44536b',
                    800: '#2e3d54',
                    900: '#1c2a41',
                    950: '#10213f',
                },
                primary: {
                    color: '{primary.500}',
                    contrastColor: '#ffffff',
                    hoverColor: '{primary.600}',
                    activeColor: '{primary.700}',
                },
                highlight: {
                    background: '#e8f1ff',
                    focusBackground: '#d9ebff',
                    color: '#1770e6',
                    focusColor: '#1159b8',
                },
            },
        },
    },
});
```

### 样式职责边界

`UnoCSS`：

- 负责 `flex / grid / layout / spacing / responsive / typography / hover / transition`
- 优先用原子类完成页面结构

`CSS Variables`：

- 负责品牌变量、布局变量、壳层变量
- 不负责替代 `PrimeVue Theme` 去承接大面积基础组件视觉

普通 CSS：

- 只负责特殊动画、极复杂结构样式、少量页面壳层补充、第三方组件例外覆盖

`PrimeVue Theme`：

- 负责基础组件 token
- 负责 `primary / surface / highlight`
- 负责按钮、输入框、标签、面板等基础控件统一视觉基线

AI 不要做：

- 不要在页面里散落大量颜色值
- 不要用页面 CSS 大面积覆盖 `.p-button`、`.p-inputtext`、`.p-select`、`.p-tag`
- 不要让同一页面出现两套圆角、边框、阴影体系
- 不要对 `.p-inputtextarea`、`.p-card`、`.p-dialog` 做大面积基础视觉重写
- 不要破坏“浅色页面中的普通信息载体必须与页面主体保持同一视觉体系”这一约束

## 5. 组件、目录与拆分规则

### 目录与职责

AI 默认按以下路径级结构生成，不得只写抽象职责、不落具体目录：

```txt
src/
  api/
    client.ts
    interceptors.ts
    types.ts
    modules/
  assets/
  components/
    base/
    business/
    layout/
  composables/
  constants/
  directives/
  i18n/
  layouts/
  pages/ 或 views/
  plugins/
  router/
    index.ts
    modules/
  stores/
  styles/
    reset.css
    variables.css
    main.css
  theme.ts
  transform/
  types/
  utils/
  App.vue
  main.ts
```

AI 必须同时遵守以下硬约束：

- 新项目默认生成 `pages/`，不要同时新建 `pages/` 和 `views/`；历史项目若已经使用 `views/`，则沿用原命名，不再额外引入 `pages/`
- `components/base` 只放高复用、无业务语义组件；`components/business` 只放业务语义组件；`components/layout` 只放布局骨架与容器
- `api/client.ts` 是推荐的唯一 Axios 入口；若历史项目已存在 `api/http.ts`，则只保留一个真实入口，不要双入口并存
- `api/interceptors.ts` 单独承载拦截器；不要在页面、store 或零散模块里重复写鉴权与错误处理
- `api/modules/*` 必须按领域拆分；不要在页面里直接拼 URL 或直接散写正式请求实现
- `router/index.ts` 负责装配；`router/modules/*` 负责分域声明；除极小项目外，不要把全部路由塞进单文件
- `theme.ts` 是主题预设唯一入口；不要在 `main.ts`、页面样式或业务组件中重复创建主题配置
- `styles/` 只放 `reset.css`、`variables.css`、`main.css` 与少量全局壳层样式；不要把业务页面样式和大量 PrimeVue 基础重写放到全局样式
- `types/` 统一收口共享类型；跨模块复用类型不得长期散落在页面、store 或接口文件内部
- `transform/` 必须承接 DTO 到前端模型的映射；不要把字段转换逻辑散在页面模板和组件渲染层

页面只负责：

- 数据请求
- 页面拼装
- 路由参数
- 权限控制

复杂逻辑必须继续下沉拆分到：

- `stores`
- `composables`
- `business components`
- `domain / rules`

### `Base / Business / View`

- `Base`：高复用、无业务语义、统一交互与统一外观
- `Business`：业务语义、状态映射、领域逻辑
- `View/Page`：页面级组装与调度

### 高频控件收口

优先进入 `Base` 层的控件：

- `Button`
- `InputText`
- `Select`
- `Tag`
- `Dialog`
- 表单项外壳

`Base` 层还应承担：

- 默认 loading / disabled 规则
- 默认国际化接入方式
- 统一权限控制

## 6. 状态、表单、接口与国际化

### 状态管理

- 必须使用 `Pinia`
- 一个领域一个 store
- store 按领域拆分
- 不要继续生成无限膨胀的总 store
- 异步动作必须显式处理加载态、错误态和空态

### 路由 `meta`

推荐统一管理：

- `title`
- `auth`
- `keepAlive`
- `roles`

### 表单校验

- 必须使用 `vee-validate + zod`
- 不要只靠手写 `if/else` 零散校验
- schema 必须集中定义
- 错误信息必须接入 i18n 或统一文案层

### 接口分层

- `Axios` 是唯一正式 HTTP 客户端
- 必须有 `api/client`
- 必须有 `api/modules/*`
- 必须有 `types/*`
- 必须有 DTO 到前端模型的映射层
- 公共请求/响应类型统一收口到 `types/` 或 `api/types.ts`
- 若项目存在统一响应包装，应抽象为公共泛型结构，例如：

```ts
interface ApiResponse<T> {
    code: number;
    message: string;
    data: T;
}
```

AI 不要做：

- 不要在页面里直接拼 URL
- 不要正式实现里继续散写 `fetch`
- 不要把后端原始响应结构直接灌给所有页面组件
- 不要只安装 `axios` 却不建立服务层
- 不要把明显业务语义组件塞进 `Base` 层

### 标签体系与表单家族

### 标签必须拆分

- 状态标签
- 范围标签
- 风险标签

### 推荐业务组件

- `TemplateStatusTag`
- `TemplateVisibilityTag`
- `TemplateRiskTag`

### 推荐映射

- `private` -> 中性浅灰胶囊
- `team` -> 浅蓝灰胶囊
- `department` -> 浅橙或浅金胶囊
- `official` -> 品牌蓝浅底胶囊
- `low` -> `secondary`
- `medium` -> `info`
- `high` -> `warn`
- `critical` -> `danger`
- `draft` -> `secondary`
- `review_pending` -> `warn`
- `published` -> `success`
- `rejected` -> `danger`

### 明确禁止

- 直接把原始枚举值裸输出给用户
- 同一类型标签在不同页面重复手写不同映射
- 把所有标签长期压成 `success / warn / danger`
- 黑色 `contrast` 作为默认高频可见状态标签

### 表单控件必须同家族

- 同一筛选区、同一表单区、同一预览区内的控件必须同家族
- 优先使用 PrimeVue 同家族控件或统一 `Base` 表单控件
- 统一控件高度、圆角、边框、focus、placeholder、helper 层级

### 明确禁止

- 原生 `select` 与 PrimeVue 输入框并排混用
- 原生 `input` 与 PrimeVue `InputText` 在同一区域混用
- 同一表单区中输入框、下拉框、按钮分别维持三套外观

### 国际化

- 默认兼容 `vue-i18n`，但不是所有项目都必须首版立即启用多语言
- 已启用国际化时，不要一部分写裸中文，一部分写 `$i('中文')`
- 已启用国际化时，用户可见文案应进入 i18n 资源
- 未启用国际化时，允许先使用稳定中文文案，但要保留后续接入 i18n 的扩展结构

### 作者态规则

已启用国际化的项目，用户可见中文文案开发阶段统一写成：

```vue
$i('中文')
```

### 已启用国际化时必须包 `$i(...)` 的内容

- 页面标题
- 路由 `meta.title`
- 按钮文案
- `label`
- `placeholder`
- 空状态
- 错误提示
- 成功提示
- `tooltip`
- 标签文案
- 表格列标题
- 弹窗标题
- `tabs` 文案

### 不要包 `$i(...)` 的内容

- 变量名
- 路由 `name`
- 枚举值
- 接口字段
- 权限码
- 埋点字段
- 调试日志

### 允许的例外

- 项目已经存在统一词典中心
- 当前改动只是延续既有 key 体系
- 同一领域术语必须复用既有命名

## 7. Git 初始化与提交链路规则

### Git 前置条件

`husky`、`lint-staged`、`commitlint` 是否“已落地”，不能靠依赖列表判断，必须靠 Git 真实状态判断。

AI 必须遵守：

- 在接入 Git Hook 前，先确认当前目录是否是可用 Git 仓库
- 若不是，先执行 `git init` 或要求用户提供已初始化仓库
- 仅存在 `.git` 目录不算通过
- 必须以 `git rev-parse --is-inside-work-tree` 成功返回为准
- 若该命令失败，不得宣称 `husky`、`lint-staged`、`commitlint` 已生效

### 推荐脚本

```json
{
    "scripts": {
        "dev": "vite",
        "build": "vue-tsc --noEmit && vite build",
        "lint": "eslint . --ext .ts,.vue",
        "format": "prettier --write .",
        "test:e2e": "playwright test",
        "prepare": "husky"
    }
}
```

### ESLint 最低实值

- 若这是某个已存在项目的落地规范，优先写该项目真实配置文件路径和当前实值，不要长期只写通用推荐值

- 基于 `@eslint/js`
- 基于 `eslint-plugin-vue` 的 `flat/recommended`
- 使用 `vue-eslint-parser`
- `script` 部分交给 `@typescript-eslint/parser`
- 仅校验 `src/**/*.{ts,vue}`
- 忽略 `dist/**`、`coverage/**`

### 关键规则口径

- `error`
  - `no-var`
  - `prefer-const`
  - `object-shorthand`
  - `@typescript-eslint/no-unused-vars`
  - `@typescript-eslint/consistent-type-imports`
  - `vue/no-mutating-props`
- `warn`
  - `no-console`，但允许 `warn` 和 `error`
  - `no-debugger`
  - `@typescript-eslint/no-explicit-any`

- `off`
  - `no-unused-vars`
  - `vue/html-self-closing`
  - `vue/multi-word-component-names`

### ESLint AI 输出要求

- 不允许把 `.vue` 文件直接交给 TS parser
- 不允许省略浏览器全局变量声明后再让前端代码被 `no-undef` 卡死
- 不允许把当前 `warn` 规则擅自升级成 `error`
- 不允许把当前已放宽规则重新收紧后却不说明兼容成本

### TypeScript 补充约束

- `tsconfig` 应开启 `strict`
- 优先使用 `unknown`，避免直接使用 `any`
- 公共类型统一收口到 `types/`
- 避免在页面内重复声明大量 inline type

### Prettier 最低实值

- `printWidth: 120`
- `tabWidth: 4`
- `useTabs: false`
- `semi: true`
- `singleQuote: true`
- `trailingComma: 'all'`
- `vueIndentScriptAndStyle: false`
- `endOfLine: 'lf'`

- `quoteProps: 'as-needed'`
- `jsxSingleQuote: false`
- `bracketSpacing: true`
- `arrowParens: 'avoid'`
- `rangeStart: 0`
- `rangeEnd: Infinity`
- `requirePragma: false`
- `insertPragma: false`
- `proseWrap: 'preserve'`
- `htmlWhitespaceSensitivity: 'css'`
- `embeddedLanguageFormatting: 'auto'`

### Prettier AI 输出要求

- 不允许把 JSON 版 Prettier 配置和带注释 / `Infinity` 的 JS 配置混用
- 不允许在未说明的情况下擅自改回 `2` 空格或 `80/100` 行宽
- 不允许忽略 `LF` 与 `4` 空格这两个已明确收口的格式约束

### Commitlint 最低实值

- 继承 `@commitlint/config-conventional`
- `type-enum`
  - `feat / fix / docs / style / refactor / perf / test / build / ci / chore / revert`
- `subject-empty: [2, 'never']`
- `subject-full-stop: [2, 'never', '.']`
- `header-max-length: [2, 'always', 100]`
- 仍需承认 inherited rules 生效：
  - `type-empty`
  - `type-case`
  - `header-trim`
  - `subject-case`
  - `body-leading-blank`
  - `footer-leading-blank`
  - `body-max-line-length`
  - `footer-max-line-length`

### Commitlint AI 输出要求

- 不允许把“未显式配置”误写成“不生效”
- 如果继承了 `config-conventional`，必须说明继承规则仍然有效
- 不允许遗漏当前仍在生效的 inherited rules，尤其是正文/页脚 `100` 字符限制
- 不允许生成当前项目不存在的额外本地规则项
- 不允许在示例里给出标题末尾带 `.` 的提交信息

### 推荐链路

```txt
.husky/pre-commit
.husky/commit-msg
lint-staged.config.cjs
commitlint.config.cjs
```

### `pre-commit`

执行：

```txt
pnpm exec lint-staged
```

### `commit-msg`

执行：

```txt
pnpm exec commitlint --edit "$1"
```

### `lint-staged` 建议作用域

```js
module.exports = {
    'src/**/*.{ts,vue}': ['pnpm exec eslint --fix', 'pnpm exec prettier --write'],
    '**/*.{js,cjs,mjs,json,md,yml,yaml}': ['pnpm exec prettier --write'],
};
```

AI 必须理解：

- 代码文件先 `eslint --fix` 再 `prettier`
- 其余配置和文档只做 `prettier`
- 这是提交链路，不等于项目全部质量保证

### 最低门禁

提交前至少满足：

- `git rev-parse --is-inside-work-tree` 通过
- `pnpm lint` 通过
- `pnpm build` 通过
- 关键 E2E 用例可执行
- Git 提交信息符合 `commitlint` 规则

### 推荐安装依赖

运行依赖：

```bash
pnpm add vue-router pinia axios primevue primeicons @primeuix/themes
pnpm add vee-validate zod vue-i18n @vueuse/core dayjs
```

开发依赖：

```bash
pnpm add -D typescript vite unocss eslint prettier playwright
pnpm add -D husky lint-staged @commitlint/cli @commitlint/config-conventional
```

### 推荐开发原则

- 先组合，不要先封装
- 先原子化，不要先写大量 CSS
- 先拆组件，不要写巨型页面
- 页面只负责“组装”
- 先统一视觉家族，再做局部点缀
- 先收口主题，再谈页面补丁

## 8. 测试与验证

- `Playwright` 用于关键页面与关键交互回归
- 若项目存在单测体系，则行为变更时补齐对应测试
- 不要把“页面能打开”当成完成

至少验证：

- 主题是否生效
- 表单控件是否同族
- 标签映射是否统一
- 浅色页面中的普通信息载体是否仍与页面主体保持同一视觉体系
- 若项目已启用国际化，国际化作者态是否一致
- `pre-commit` 和 `commit-msg` 是否真实生效

## 9. AI 禁令

- 不要把“企业后台 / 中后台 / 管理台 / 表单 / 表格 / 审批流 / 工作台”误判为 Vue2 信号
- 不要只改导航，不同步页头、badge、标签、筛选器
- 不要一边统一按钮风格，一边放任标签和输入框继续使用旧风格
- 不要为了省事回退到原生表单控件
- 不要把主题问题继续下放给页面 CSS 兜底
- 不要破坏“浅色页面中的普通信息载体必须与页面主体保持同一视觉体系”这一约束
- 已启用国际化时，不要一部分写裸中文，一部分写 `$i('中文')`
- 不要把所有标签继续散落在页面局部写 `severity`
- 不要让 `store / router / api / types` 长期堆在单文件
- 不要继续生成 `global.ts` 这类无限膨胀的总 store
- 不要只写“建议接入 ESLint / Prettier / Commitlint”，必须写出当前实值
- 不要把“装了依赖”写成“已经落地”
- 不要在 `git rev-parse --is-inside-work-tree` 失败时宣称 hook 生效
- 不要把宿主仓库约束与前端子项目约束混为一谈
- 不要在 JSON 文件中添加注释
- 不要为了补文档而虚构当前项目不存在的规则项

## 10. 输出口径

如果用户让你更新规范文档：

- 先以当前真实配置与真实前置条件为准
- 再把规则提炼成文档条目
- 明确写出作用域、工具文件路径、规则级别、限制值

如果用户让你实现前端项目：

- 先按本规范输出工程化基线
- 先确认默认方案选择
- 先确认 Git 是否已初始化可用
- 主题先收口到 `theme.ts`
- 若项目已启用国际化，国际化实现先统一接入
- 高频基础控件优先进入 `Base` 层
- 再输出页面实现
- 不允许先写业务代码、后补工程约束
