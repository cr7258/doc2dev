# Doc2Dev 多语言支持实施计划

## 🎯 项目目标

为 Doc2Dev 前端界面添加中英文双语支持，提供用户友好的语言切换功能。

### 核心需求
- ✅ 支持中文（默认）和英文两种语言
- ✅ 右上角语言切换器
- ✅ 保持现有 URL 结构不变
- ✅ 用户语言偏好本地存储
- ✅ 即时语言切换，无需刷新页面

## 🏗️ 技术方案

### 技术选型
**方案：** `react-i18next` - React 生态最成熟的 i18n 解决方案

**选择理由：**
- ✅ React 生态最流行的 i18n 库（40k+ GitHub stars）
- ✅ 完美支持 TypeScript 类型安全
- ✅ 内置 localStorage 持久化支持
- ✅ 丰富的功能：插值、复数、命名空间等
- ✅ 优秀的性能和懒加载支持
- ✅ 不需要路由级别的国际化（适合我们的需求）

**核心特性：**
- 自动语言检测和持久化
- 类型安全的翻译 keys
- 支持嵌套翻译结构
- 插值和动态内容支持

### 架构设计

```
frontend/
├── lib/
│   └── i18n/
│       ├── index.ts           # i18next 配置和初始化
│       ├── resources.ts       # 翻译资源定义
│       └── types.ts          # TypeScript 类型定义
├── locales/
│   ├── zh/
│   │   ├── common.json       # 通用翻译
│   │   ├── pages.json        # 页面翻译
│   │   └── components.json   # 组件翻译
│   └── en/
│       ├── common.json       # 通用翻译
│       ├── pages.json        # 页面翻译
│       └── components.json   # 组件翻译
├── components/
│   ├── language-switcher.tsx  # 语言切换器组件
│   └── ui/
│       └── ...               # 现有 UI 组件
└── app/
    ├── layout.tsx            # 根布局（包装 I18nextProvider）
    ├── page.tsx             # 首页
    ├── query/               # 查询页面
    ├── download/            # 下载页面
    ├── settings/            # 设置页面
    └── ...                  # 其他页面
```

## 📋 详细实施步骤

### 第一步：安装和配置 react-i18next

**目标：** 建立基于 react-i18next 的多语言基础设施

**安装依赖：**
```bash
npm install react-i18next i18next i18next-browser-languagedetector
npm install --save-dev @types/react-i18next
```

**实施内容：**
1. 创建 `lib/i18n/index.ts` - i18next 配置和初始化
2. 创建 `lib/i18n/resources.ts` - 翻译资源管理
3. 创建 `lib/i18n/types.ts` - TypeScript 类型定义
4. 修改 `app/layout.tsx` - 集成 I18nextProvider

**核心配置结构：**
```typescript
// lib/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'zh',
    lng: 'zh', // 默认中文
    detection: {
      order: ['localStorage'], // 只从 localStorage 检测
      caches: ['localStorage']
    },
    resources: {
      zh: { translation: zhTranslations },
      en: { translation: enTranslations }
    }
  });
```

### 第二步：创建翻译文件结构

**目标：** 建立完整的中英文翻译内容

**实施内容：**
1. 创建 `locales/zh/` 和 `locales/en/` 目录结构
2. 分析现有页面，提取所有需要翻译的文本
3. 建立翻译 key 的命名规范
4. 创建分模块的翻译文件（common.json, pages.json, components.json）

**翻译内容分类：**
- 导航栏和菜单
- 页面标题和描述
- 按钮和链接文本
- 表单标签和占位符
- 提示信息和状态文本
- 表格标题和数据展示

**文件结构示例：**
```json
// locales/zh/common.json
{
  "nav": {
    "home": "首页",
    "query": "查询",
    "settings": "设置"
  },
  "buttons": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除"
  },
  "messages": {
    "success": "操作成功",
    "error": "操作失败",
    "loading": "加载中..."
  }
}

// locales/zh/pages.json
{
  "home": {
    "title": "为 AI 编程助手提供最新文档",
    "description": "索引和查询 GitHub 仓库，与 Cursor、Windsurf 等工具集成"
  },
  "query": {
    "title": "文档查询",
    "placeholder": "输入您的问题..."
  }
}
```

### 第三步：实现语言切换组件

**目标：** 创建用户友好的语言选择器

**实施内容：**
1. 创建 `components/language-switcher.tsx`
2. 使用 react-i18next 的 `useTranslation` hook
3. 使用 shadcn/ui 的 Select 组件
4. 添加国旗图标和语言名称
5. 集成到导航栏中

**核心代码：**
```typescript
import { useTranslation } from 'react-i18next';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const handleLanguageChange = (language: string) => {
    i18n.changeLanguage(language);
  };

  return (
    <Select value={i18n.language} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-32">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="zh">🇨🇳 中文</SelectItem>
        <SelectItem value="en">🇺🇸 English</SelectItem>
      </SelectContent>
    </Select>
  );
}
```

**组件特性：**
- 显示当前选中语言
- 下拉菜单展示可选语言
- 国旗图标 + 语言名称
- 响应式设计，适配移动端
- 即时切换效果

**位置：** 导航栏右上角，GitHub 登录按钮左侧

### 第四步：翻译前端UI文本

**目标：** 将所有硬编码文本替换为翻译函数调用

**实施内容：**
1. 修改 `app/layout.tsx` - 包装语言提供者
2. 修改 `app/page.tsx` - 首页翻译
3. 修改 `app/query/page.tsx` - 查询页面翻译
4. 修改 `app/download/page.tsx` - 下载页面翻译
5. 修改 `app/settings/page.tsx` - 设置页面翻译
6. 修改 `components/navbar.tsx` - 导航栏翻译
7. 修改其他组件的文本内容

**替换示例：**
```typescript
// 替换前
<h1>Up-to-date docs for AI code assistants</h1>

// 替换后
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();
<h1>{t('pages.home.title')}</h1>

// 支持命名空间
const { t } = useTranslation('pages');
<h1>{t('home.title')}</h1>
```

### 第五步：用户语言偏好功能

**目标：** 配置 react-i18next 的语言持久化

**实施内容：**
1. 配置 i18next-browser-languagedetector
2. 设置语言检测顺序（仅 localStorage）
3. 禁用浏览器自动检测
4. 设置默认语言为中文

**配置示例：**
```typescript
// lib/i18n/index.ts
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'zh',
    lng: 'zh', // 强制默认中文
    detection: {
      order: ['localStorage'], // 只从 localStorage 检测
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
      excludeCacheFor: ['cimode'] // 开发模式排除
    },
    // 其他配置...
  });
```

**特点：**
- ✅ 自动保存用户语言选择到 localStorage
- ✅ 页面刷新后保持用户选择
- ✅ 首次访问默认显示中文
- ✅ 不依赖浏览器语言设置

### 第六步：测试和调试

**目标：** 确保多语言功能的完整性和用户体验

**测试内容：**
1. **功能测试**
   - 语言切换是否正常工作
   - 所有页面文本是否正确翻译
   - 用户偏好是否正确保存和恢复

2. **界面测试**
   - 不同语言下的界面布局
   - 文本长度变化对布局的影响
   - 移动端适配情况

3. **边界情况测试**
   - 首次访问的默认语言
   - localStorage 不可用的情况
   - 翻译缺失的处理

4. **性能测试**
   - 语言切换的响应速度
   - 翻译系统的内存占用

## 🎨 用户体验设计

### 语言切换器设计
- **位置：** 导航栏右上角
- **样式：** 下拉选择器，与现有 UI 风格一致
- **内容：** 🇨🇳 中文 / 🇺🇸 English
- **交互：** 点击即时切换，无需刷新页面

### 默认行为
- **默认语言：** 中文
- **首次访问：** 显示中文界面
- **语言记忆：** 用户选择后永久记住偏好

## 📊 翻译内容统计

### 预估翻译量
- **导航栏：** ~10 个文本项
- **首页：** ~20 个文本项
- **查询页面：** ~25 个文本项
- **下载页面：** ~30 个文本项
- **设置页面：** ~35 个文本项
- **通用组件：** ~40 个文本项

**总计：** 约 160 个翻译项

### 翻译优先级
1. **高优先级：** 导航栏、页面标题、主要按钮
2. **中优先级：** 表单标签、提示信息
3. **低优先级：** 帮助文本、详细说明

## 🚀 实施时间线

- **第1步：** 1-2 小时（基础设施）
- **第2步：** 2-3 小时（翻译内容准备）
- **第3步：** 1-2 小时（语言切换器）
- **第4步：** 3-4 小时（UI文本替换）
- **第5步：** 1 小时（用户偏好）
- **第6步：** 1-2 小时（测试调试）

**总计：** 9-14 小时

## 📝 注意事项

1. **类型安全：** 确保所有翻译 key 都有 TypeScript 类型检查
2. **性能优化：** 翻译内容在构建时静态化，避免运行时开销
3. **可扩展性：** 预留接口，便于未来添加更多语言
4. **一致性：** 建立翻译规范，确保术语使用一致
5. **测试覆盖：** 重点测试语言切换的边界情况

## 🔄 后续优化

实施完成后可考虑的优化方向：
- 添加更多语言支持
- 实现翻译内容的懒加载
- 添加翻译管理后台
- 集成专业翻译服务
