# AGENTS.md — Daily Food News 项目规范

## 项目定位
中国烘焙食品行业 AI 情报站，每日自动抓取 → AI 打分 → AI 摘要 → 静态站点构建 → GitHub Pages 部署。
参照 rss-ai-ranker 项目架构重建，技术栈从 Python 迁移到 Astro + Node.js + Gemini API。

## 核心原则

### 配置驱动，代码不硬编码
- 所有源、关键词、分类、参数全部从 `config/*.json` 读取
- 增删源 / 改关键词 / 调分类 → 只改 JSON，不改代码
- 代码中禁止出现硬编码的 URL、关键词、分类名

### 模块化
- 每个功能独立文件：抓取、打分、摘要、构建各自分离
- 公共工具函数放 `src/utils/`

### 零静默故障
- 任何抓取失败、API 报错必须 console.error 输出，不静默吞掉
- 单源失败不阻断整体流程，跳过并记录

## 技术栈
- **运行时**: Node.js 20+
- **前端框架**: Astro 5.x（静态生成）
- **AI**: Google Gemini API（打分 + 中文摘要）
- **部署**: GitHub Pages
- **CI/CD**: GitHub Actions

## 目录结构
daily-food-news/
├── .github/workflows/
│   └── daily.yml                # GitHub Actions 每日定时任务
├── config/
│   ├── feeds.json               # 源列表（type: rss | scrape）
│   ├── keywords.json            # 品牌关键词 + 信号关键词
│   ├── categories.json          # 分类定义 + 匹配规则
│   └── settings.json            # 全局参数
├── src/
│   ├── fetch-feeds.ts           # 抓取模块（RSS 解析 + 网页抓取）
│   ├── ai-rank.ts               # Gemini AI 打分
│   ├── ai-summary.ts            # Gemini AI 中文摘要
│   ├── categorize.ts            # 基于 config 的分类匹配
│   ├── main.ts                  # 编排入口
│   └── utils/
│       ├── config-loader.ts     # 统一读取 config/*.json
│       └── dedup.ts             # 去重（URL + 标题相似度）
├── site/                        # Astro 前端
│   ├── astro.config.mjs
│   ├── src/
│   │   ├── layouts/Layout.astro
│   │   ├── pages/
│   │   │   ├── index.astro      # 首页
│   │   │   └── archive.astro    # 归档页
│   │   └── components/
│   │       ├── ArticleCard.astro
│   │       ├── CategorySection.astro
│   │       ├── SearchBar.astro
│   │       ├── TagFilter.astro
│   │       └── StatsPanel.astro
│   └── public/
├── data/
│   ├── articles.json            # 每日产出（抓取→打分→摘要后的结果）
│   └── archive/                 # 历史归档 YYYY-MM-DD.json
├── package.json
├── tsconfig.json
└── AGENTS.md

## 数据流


GitHub Actions cron 触发
→ src/main.ts
→ 1. fetch-feeds.ts: 读 config/feeds.json，按 type 分 RSS/scrape 抓取
→ 2. dedup.ts: URL + 标题去重
→ 3. ai-rank.ts: 调 Gemini API，基于 config/keywords.json 打分（0-100）
→ 4. ai-summary.ts: 调 Gemini API，生成中文摘要（≤150字）
→ 5. categorize.ts: 读 config/categories.json，按信号+关键词匹配分类
→ 6. 写入 data/articles.json + data/archive/YYYY-MM-DD.json
→ Astro build: 读 data/articles.json 生成静态 HTML
→ 部署到 GitHub Pages
→ process.exit(0)

## AI 打分 Prompt 模板


你是一位中国烘焙食品行业分析师。请对以下文章评分（0-100）：
评分维度：

行业相关性（30%）：与烘焙/食品制造的直接相关度
决策价值（25%）：对采购/供应链/合规决策的参考价值
时效性（20%）：信息的紧迫程度
信息深度（15%）：数据/分析的专业程度
独家性（10%）：是否为独家/首发信息

同时输出：

score: 整数 0-100
tags: 从以下标签中选择 1-3 个：[从 config/categories.json 动态读取]
summary: 中文摘要，≤150字

标题：{title}
内容：{content}
以 JSON 格式返回：{"score": N, "tags": [...], "summary": "..."}

## 前端规范

### 设计风格（与 rss-ai-ranker 统一）
- 深色背景 `#0f1117`，白色卡片 `#1a1f2e`
- 主色调：食品行业用暖色 `#f0b90b`（金色）
- 评分圆圈：≥70 绿色，40-69 黄色，<40 灰色
- 响应式：移动端单列，桌面端多列

### 功能
- 搜索框：实时过滤标题/摘要
- 标签筛选：按 categories.json 中的分类筛选
- 统计面板：今日文章数、源分布、分类分布
- 摘要展开/收起：首页默认收起，点击展开
- 评分 ≥ 70 的文章默认展示，低分折叠

### 归档页
- 按日期列出历史数据
- 读取 data/archive/*.json

## GitHub Actions 规范
- cron: `0 0 * * *`（UTC 0:00 = 北京 8:00）
- 需要 secret: `GEMINI_API_KEY`
- workflow 末尾必须 commit + push data/ 和 site 构建产物
- 使用 `process.exit(0)` 确保 Node 进程正常退出

## 代码规范
- TypeScript strict mode
- 所有配置通过 config-loader.ts 读取，禁止 import JSON 硬路径散落各处
- console.log 统一格式：`[HH:MM:SS] Step N: 描述`
- 错误处理：try-catch 包裹每个源的抓取，单源失败不阻断

## 禁止事项
- ❌ 不要在代码中硬编码任何 URL、关键词、分类
- ❌ 不要使用 Python（全部迁移到 Node.js/TypeScript）
- ❌ 不要引入数据库，纯 JSON 文件
- ❌ 不要使用第三方 CSS 框架，手写 CSS
- ❌ 修改任何文件前必须先说明计划和风险