Vue3 企业级前端开发规范方案（PrimeVue + UnoCSS）
一、方案定位
适用于：
企业中后台系统
Vue3 + TypeScript 技术栈
多人协作开发
中大型项目
长期维护项目
原子化 CSS 开发模式
不使用暗黑模式
不做复杂多主题系统

二、最终技术栈

三、核心设计思想
技术职责划分
组件逻辑 -> PrimeVue
页面布局 -> UnoCSS
视觉统一 -> CSS Variables
业务样式 -> 少量普通 CSS

四、整体开发原则
原则一：优先使用 UnoCSS
优先通过原子类完成布局与样式。
推荐：
<div class="flex items-center gap-3 px-4 py-2">
不推荐：
<div class="user-wrapper">
.user-wrapper {
  display: flex;
  align-items: center;
}

原则二：尽量减少 CSS 文件
避免：
UserTable.css
UserForm.css
OrderDialog.css
大量出现。

原则三：统一设计 Token
禁止直接写颜色值：
color: #409eff;
统一使用：
color: var(--app-primary);

原则四：页面只负责“组装”
页面组件只负责：
数据请求
页面拼装
路由参数
权限控制
复杂逻辑应拆分至：
composables
business components
stores

五、推荐项目目录结构
src/
├── api/
│
├── assets/
│
├── components/
│   ├── base/
│   ├── business/
│   └── layout/
│
├── composables/
│
├── constants/
│
├── directives/
│
├── layouts/
│
├── plugins/
│
├── router/
│   ├── index.ts
│   └── modules/
│
├── stores/
│
├── styles/
│   ├── reset.css
│   ├── variables.css
│   ├── primevue.css
│   └── main.css
│
├── types/
│
├── utils/
│
├── views/
│
├── App.vue
└── main.ts

六、UnoCSS 规范
安装
pnpm add -D unocss

vite.config.ts
import UnoCSS from 'unocss/vite'

export default defineConfig({
  plugins: [
    UnoCSS(),
  ],
})

uno.config.ts
import {
  defineConfig,
  presetUno,
  presetIcons,
  presetTypography,
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetIcons(),
    presetTypography(),
  ],
})

UnoCSS 使用规范
UnoCSS 负责
flex
grid
spacing
typography
responsive
hover
transition
layout

普通 CSS 负责
特殊动画
第三方组件覆盖
极复杂样式场景

七、CSS Variables 规范
styles/variables.css
:root {
  /* colors */
  --app-primary: #3b82f6;
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

八、PrimeVue 使用规范
禁止直接大量使用 PrimeVue 原始组件
不推荐：
<Button />
<DataTable />
<InputText />
直接散落业务代码。

推荐封装 Base 组件
components/base/
├── BaseButton.vue
├── BaseTable.vue
├── BaseDialog.vue
├── BaseForm.vue

Base 组件职责
统一：
loading
size
国际化
权限控制
默认样式
空状态
错误状态

九、组件开发规范
组件分层

Base组件
例如：
BaseButton
BaseTable
BaseCard
特点：
不包含业务逻辑
高复用
高统一性

Business组件
例如：
UserTable
OrderPanel
特点：
包含业务逻辑
服务于特定模块

十、TypeScript 规范
tsconfig 必须开启 strict
{
  "compilerOptions": {
    "strict": true
  }
}

禁止使用 any
允许：
unknown

类型统一管理
types/
禁止：
页面内大量 inline type
到处重复定义类型

API 返回结构统一
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

十一、Pinia 规范
推荐结构
stores/
├── app.ts
├── user.ts
├── permission.ts
└── settings.ts

规范要求
一个领域一个 store
禁止：
global.ts
超级大 store。

十二、路由规范
推荐结构
router/
├── index.ts
└── modules/
    ├── dashboard.ts
    ├── system.ts
    └── user.ts

meta 规范
meta: {
  title: '用户管理',
  auth: true,
  keepAlive: true,
  roles: ['admin'],
}

十三、API 管理规范
推荐目录
api/
├── modules/
├── http.ts
├── interceptors.ts
└── types.ts

接口命名规范
推荐：
getUserList
createUser
updateUser
deleteUser
不推荐：
fetchUserApi
queryUserListApi

十四、ESLint 规范
推荐方案
@antfu/eslint-config

推荐规则
{
  semi: false,
  quotes: ['error', 'single'],
}

必须要求
保存自动格式化
CI 执行 ESLint
禁止提交 lint 错误代码

十五、Git 提交规范
推荐工具
husky
lint-staged
commitlint

commit message 规范
feat:
fix:
refactor:
docs:
style:
test:

十六、国际化规范
推荐
vue-i18n

禁止
<div>用户管理</div>

推荐
<div>{{ t('user.title') }}</div>

十七、推荐安装依赖
运行依赖
pnpm add vue-router pinia axios primevue primeicons

pnpm add vee-validate zod vue-i18n @vueuse/core dayjs

开发依赖
pnpm add -D typescript vite unocss eslint prettier vitest playwright

十八、推荐开发原则
原则一
先组合，不要先封装。

原则二
先原子化，不要先写 CSS。

原则三
先拆组件，不要写巨型页面。

原则四
页面只负责“组装”。

十九、最终推荐方案
Vue3
+ TypeScript
+ Vite
+ PrimeVue
+ Pinia
+ Vue Router
+ UnoCSS
+ CSS Variables
+ Axios
+ vee-validate
+ zod
+ vue-i18n
+ ESLint
+ Prettier
+ Vitest

二十、方案优势
该方案具备以下优势：
学习成本低
开发效率高
TypeScript 友好
AI 辅助开发友好
样式维护成本低
组件化程度高
长期维护成本低
适合多人协作
非常适合现代 Vue3 企业项目

二十一、AI-SDLC 默认落地映射

当前 AI-SDLC 源码版本中，普通前端需求的首个推荐 provider 已对齐本规范：

frontend_stack
vue3

provider_id
public-primevue

style_pack_id
modern-saas

默认生成路径包括：
Vite
PrimeVue
UnoCSS
CSS Variables
Pinia
Vue Router
BaseButton / BaseTable / BaseDialog / BaseForm

企业 Vue2 组件库仍作为显式选择路径保留：

frontend_stack
vue2

provider_id
enterprise-vue2

style_pack_id
enterprise-default

二十二、AI-SDLC Web、视觉和可访问性质量门

Web smoke blocker：
Vite dev server 无法启动
页面无法打开
页面白屏或主要内容缺失
browser console error
browser page error

首版 warning / advisory：
桌面 1440x900 截图证据
移动 390x844 截图证据
视觉结构、主内容、横向溢出
Button / Input / Select / Dialog / Form 覆盖
Dialog close / focus return 风险
表单控件缺少 label 或 aria 等价名称
键盘焦点可见性问题

这些 warning 不阻断普通生成，但必须作为浏览器 gate 证据沉淀，后续可升级为 pixel diff、结构 diff 或更严格的可访问性 blocker。
