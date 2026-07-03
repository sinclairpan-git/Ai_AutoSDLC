# Vue3企业级前端开发规范方案 v1.6.1（AI执行版）

## 1. 目标

本规范用于约束 AI 直接输出可落地的 Vue3 前端代码与工程化配置。

`v1.6.1` 的目标是在 `v1.6` 基础上补齐仍然缺失的强约束：

- `TypeScript`、路由 `meta`、公共响应结构
- `Base` 层中的统一权限控制职责
- Git 提交粒度与可读性要求
- 深色信息块使用边界

同时明确：

- 接口命名以后台实际契约、生成代码或既有服务层约定为主，不做前端命名风格强限制

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
- `Playwright`
- `ESLint + Prettier + husky + lint-staged + commitlint`

## 3. 工程化边界

当用户说“这是前端项目的约束”时，默认按前端子项目边界落地，不自动扩大为整个宿主仓库约束。

SDLC 不硬编码唯一前端子项目名。AI 必须优先读取当前项目已经确认的前端子项目路径；若项目没有明确路径，必须先在方案确认或初始化阶段收口。以下路径只作为已确认项目的示例：

```txt
apps/prompt-template-center
```

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
- 深色信息块只允许用于正文、输出、代码、预览结果等高对比阅读区

### 明确禁止

- 左侧深色导航 + 右侧浅色品牌内容区
- 导航和内容区像两个不同产品
- 黑色 `contrast` 标签和浅色品牌标签大面积同屏混用
- 主题未收口时继续靠业务 CSS 给 PrimeVue 组件打补丁
- 用 `!important` 批量压制 PrimeVue 默认样式

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

壳层样式默认方向：

```css
.shell__sidebar {
    background: linear-gradient(180deg, #f6faff 0%, #edf4fb 100%);
    border: 1px solid #d9e5f2;
    border-radius: 28px;
    box-shadow: 0 18px 40px rgba(23, 112, 230, 0.08);
}

.shell__nav-link.is-active {
    background: #e8f1ff;
    color: #1770e6;
    border-color: #c8dcff;
}

.shell__topbar {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(16, 35, 62, 0.08);
    box-shadow: 0 12px 30px rgba(23, 112, 230, 0.06);
    backdrop-filter: blur(16px);
}
```

## 5. 样式职责边界

### `UnoCSS`

- 负责布局、间距、排版、响应式、过渡
- 优先用原子类完成页面结构

### `CSS Variables`

- 负责品牌变量、布局变量、壳层变量
- 不负责替代 `PrimeVue Theme` 去承接大面积基础组件视觉

### `PrimeVue Theme`

- 负责基础组件 token
- 负责 `primary / surface / highlight`
- 负责按钮、输入框、标签、面板等基础控件统一视觉基线

### 不要做

- 不要在页面里散落大量颜色值
- 不要用页面 CSS 大面积覆盖 `.p-button`、`.p-inputtext`、`.p-select`、`.p-tag`
- 不要让同一页面出现两套圆角、边框、阴影体系

## 6. 组件、目录与拆分规则

### 目录与职责

- `components/base`：基础组件
- `components/business`：业务语义组件
- `views`：页面组装
- `stores`：领域状态
- `router/modules`：路由模块
- `api/modules`：接口模块
- `types`：公共类型

页面只负责：

- 数据请求
- 页面拼装
- 路由参数
- 权限控制

### `Base / Business / View`

- `Base`：高复用、无业务语义、统一交互与统一外观
- `Business`：业务语义、状态映射、领域逻辑
- `View`：页面级组装与调度

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

### 拆分要求

- 一个领域一个 store
- store 按领域拆分，例如 `app`、`user`、`permission`、`settings`
- 路由按 `router/modules` 拆分
- API 按 `api/modules` 拆分
- 公共类型统一收口到 `types/`

### 路由 `meta` 规范

推荐 `meta` 字段统一管理：

- `title`
- `auth`
- `keepAlive`
- `roles`

### API 与类型补充

- 接口命名以后台实际契约、生成代码或既有服务层约定为主
- 优先使用 `unknown`，避免直接使用 `any`
- 公共请求/响应类型统一收口到 `types/` 或 `api/types.ts`
- 若项目存在统一响应包装，应抽象为公共泛型结构，例如：

```ts
interface ApiResponse<T> {
    code: number;
    message: string;
    data: T;
}
```

### 不要做

- 不要把明显业务语义组件塞进 `Base` 层
- 不要在页面里长期散落 `primevue/*` 高频控件用法
- 不要让 `store / router / api / types` 长期堆在单文件
- 不要继续使用 `global.ts` 这类无限膨胀的总 store

## 7. 标签体系与表单家族规则

### 标签必须拆分

- 状态标签
- 范围标签
- 风险标签

### 推荐业务组件

- `TemplateStatusTag`
- `TemplateVisibilityTag`
- `TemplateRiskTag`

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

## 8. 国际化规则

### 核心规则

所有用户可见中文文案，开发阶段统一写成：

```vue
$i('中文')
```

不要直接写裸中文。

不要一上来就手写英文 key。

### 必须包 `$i(...)` 的内容

- 页面标题
- 路由 `meta.title`
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

### 不要包 `$i(...)` 的内容

- 变量名
- 路由 `name`
- 枚举值
- 接口字段
- 权限码
- 埋点字段
- 调试日志

### 允许的例外

仅在以下场景允许直接使用稳定 key：

- 项目已经存在统一词典中心
- 当前改动只是延续既有 key 体系
- 同一领域术语必须复用既有命名

## 9. ESLint 执行规则

项目真实配置文件必须以当前前端子项目为准。以下路径是已确认前端子项目的示例，不得作为所有项目的全局硬编码：

```txt
apps/prompt-template-center/eslint.config.js
```

### 必须输出的基线

- 基于 `@eslint/js`
- 基于 `eslint-plugin-vue` 的 `flat/recommended`
- 使用 `vue-eslint-parser`
- `script` 部分交给 `@typescript-eslint/parser`
- 仅校验：

```txt
src/**/*.{ts,vue}
```

- 忽略：

```txt
dist/**
coverage/**
```

### 当前规则口径

#### `error`

- `no-var`
- `prefer-const`
- `object-shorthand`
- `@typescript-eslint/no-unused-vars`
- `@typescript-eslint/consistent-type-imports`
- `vue/no-mutating-props`

#### `warn`

- `no-console`，但允许 `warn` 和 `error`
- `no-debugger`
- `@typescript-eslint/no-explicit-any`

#### `off`

- `no-unused-vars`
- `vue/html-self-closing`
- `vue/multi-word-component-names`

### AI 输出要求

- 不允许把 `.vue` 文件直接交给 TS parser
- 不允许省略浏览器全局变量声明后再让前端代码被 `no-undef` 卡死
- 不允许把当前 `warn` 规则擅自升级成 `error`
- 不允许把当前已放宽规则重新收紧后却不说明兼容成本

## 10. Prettier 执行规则

项目真实配置文件必须以当前前端子项目为准。以下路径是已确认前端子项目的示例，不得作为所有项目的全局硬编码：

```txt
apps/prompt-template-center/.prettierrc.cjs
```

### 当前实值

- `printWidth: 120`
- `tabWidth: 4`
- `useTabs: false`
- `semi: true`
- `singleQuote: true`
- `quoteProps: 'as-needed'`
- `jsxSingleQuote: false`
- `trailingComma: 'all'`
- `bracketSpacing: true`
- `arrowParens: 'avoid'`
- `rangeStart: 0`
- `rangeEnd: Infinity`
- `requirePragma: false`
- `insertPragma: false`
- `proseWrap: 'preserve'`
- `htmlWhitespaceSensitivity: 'css'`
- `vueIndentScriptAndStyle: false`
- `endOfLine: 'lf'`
- `embeddedLanguageFormatting: 'auto'`

### AI 输出要求

- 不允许把 JSON 版 Prettier 配置和带注释 / `Infinity` 的 JS 配置混用
- 不允许在未说明的情况下擅自改回 `2` 空格或 `80/100` 行宽
- 不允许忽略 `LF` 与 `4` 空格这两个已明确收口的格式约束

## 11. Commitlint 执行规则

项目真实配置文件必须以当前前端子项目为准。以下路径是已确认前端子项目的示例，不得作为所有项目的全局硬编码：

```txt
apps/prompt-template-center/commitlint.config.cjs
```

### 当前规则来源

- 继承 `@commitlint/config-conventional`

### 当前显式覆盖值

- `type-enum`
  - 允许：`feat / fix / docs / style / refactor / perf / test / build / ci / chore / revert`
- `subject-empty: [2, 'never']`
- `subject-full-stop: [2, 'never', '.']`
- `header-max-length: [2, 'always', 100]`

### 当前继承后仍然生效的限制

- `type-empty: [2, 'never']`
- `type-case: [2, 'always', 'lower-case']`
- `header-trim: [2, 'always']`
- `subject-case: [2, 'never', ['sentence-case', 'start-case', 'pascal-case', 'upper-case']]`
- `body-leading-blank: [1, 'always']`
- `footer-leading-blank: [1, 'always']`
- `body-max-line-length: [2, 'always', 100]`
- `footer-max-line-length: [2, 'always', 100]`

### AI 输出要求

- 不允许把“未显式配置”误写成“不生效”
- 如果继承了 `config-conventional`，必须说明继承规则仍然有效
- 不允许遗漏当前仍在生效的 inherited rules，尤其是正文/页脚 `100` 字符限制
- 不允许生成当前项目不存在的额外本地规则项
- 不允许在示例里给出标题末尾带 `.` 的提交信息

## 12. 提交链路与验证规则

项目真实提交链路必须以当前前端子项目为准。以下路径是已确认前端子项目的示例，不得作为所有项目的全局硬编码：

```txt
apps/prompt-template-center/.husky/pre-commit
apps/prompt-template-center/.husky/commit-msg
apps/prompt-template-center/lint-staged.config.cjs
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

### `lint-staged` 当前作用域

```js
module.exports = {
    'src/**/*.{ts,vue}': ['pnpm exec eslint --fix', 'pnpm exec prettier --write'],
    '**/*.{js,cjs,mjs,json,md,yml,yaml}': ['pnpm exec prettier --write'],
};
```

AI 必须理解：

- 这是“前端子项目独立提交链路”
- 不是整个宿主工作区默认全部受控
- 代码文件先 `eslint --fix` 再 `prettier`
- 其余配置和文档只做 `prettier`

### 提交粒度与可读性

- 不要把格式化噪音和业务改动混成一次不可读提交
- 不要把无关的大范围格式化改动塞进一次功能提交
- `commit message` 不仅要合规，还要可快速追溯本次真实意图

### 测试与验证

- `Playwright` 用于关键页面与关键交互回归
- 若项目存在单测体系，则行为变更时补齐对应测试
- 不要把“页面能打开”当成完成

至少验证：

- 主题是否生效
- 表单控件是否同族
- 标签映射是否统一
- 国际化作者态是否一致
- 深色信息块是否被错误用在普通卡片、筛选容器或常规信息分组

## 13. AI 禁令

- 不要只改导航，不同步页头、badge、标签、筛选器
- 不要一边统一按钮风格，一边放任标签和输入框继续使用旧风格
- 不要为了省事回退到原生表单控件
- 不要把主题问题继续下放给页面 CSS 兜底
- 不要把深色信息块滥用到普通卡片、筛选容器和常规信息分组
- 不要一部分写裸中文，一部分写 `$i('中文')`
- 不要把所有标签继续散落在页面局部写 `severity`
- 不要让 `store / router / api / types` 长期堆在单文件
- 不要继续生成 `global.ts` 这类无限膨胀的总 store
- 不要只写“建议接入 ESLint / Prettier / Commitlint”，必须写出当前实值
- 不要把宿主仓库约束与前端子项目约束混为一谈
- 不要把继承值写成显式配置值
- 不要在 JSON 文件中添加注释
- 不要为了补文档而虚构当前项目不存在的规则项
- 不要把格式化噪音和业务改动混成一次不可读提交说明

## 14. 输出口径

如果用户让你更新规范文档：

- 先以当前真实配置为准
- 再把规则提炼成文档条目
- 明确写出作用域、工具文件路径、规则级别、限制值

如果用户让你实现前端项目：

- 先按本规范输出工程化基线
- 主题先收口到 `theme.ts`
- 国际化先用 `$i('中文')`
- 高频基础控件优先进入 `Base` 层
- 高频标签优先进入业务标签组件
- 再输出页面实现
- 不允许先写业务代码、后补工程约束
