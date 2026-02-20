# Macro Dashboard Frontend

宏观经济仪表盘前端应用

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **状态管理**: TanStack Query (React Query)
- **HTTP 客户端**: Axios
- **图表库**: ECharts (待集成)
- **日期处理**: Day.js

## 开发

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```
访问 http://localhost:5173

### 构建生产版本
```bash
npm run build
```

## 环境变量

- `.env.local` - 本地开发: `VITE_API_BASE_URL=http://localhost:8000`
- `.env` - 生产环境: `VITE_API_BASE_URL=https://macro-dashboard-api-771720899914.us-central1.run.app`

## 当前功能

✅ 已完成:
- React + TypeScript 项目初始化
- API 客户端和 React Query 集成
- 仪表板页面基础布局
- 实时数据展示（利率、外汇、大宗商品、通胀、就业）

🔄 待开发:
- ECharts 图表集成
- 时间序列图表
- 指标详情页面
- 数据筛选功能
