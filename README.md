# MacroDashboard V2 📊

MacroDashboard 是一款专为**量化金融**设计的宏观经济数据仪表板。
V2 版本带来了极致的**“控制室 (Control Room)”**拟态玻璃风 (Glassmorphism) UI，提供直观、高对比度、实时动态的全球宏观经济指标监控体系。

数据完全基于 **FRED API** 自动采集，应用采用现代化容器架构 (Docker Compose) 进行一键私有化部署。

---

## 🌟 核心功能特性

MacroDashboard 不仅仅是一个静态的数据展示面板，它内置了多项深度的量化宏观分析工具：

1. 📈 **美债收益率曲线 (Yield Curve)**：
   自动构建并展示各期限的美国国债收益率曲线形态（正常、倒挂、平坦），并实时计算 10Y-2Y 利差，助您监控衰退信号。
2. 🔄 **跨资产相关性分析 (Correlation Heatmap)**：
   基于指定时间窗口，动态计算并生成各种宏观资产（如美债、外汇、原油等）之间的相关性矩阵系数，高亮深度的正负相关对。
3. 💥 **情景冲击模拟器 (Shock Simulator)**：
   允许您定义宏观冲击（如：加息/降息 N 个基点、大宗商品暴涨暴跌），基于历史统计模型，模拟并预测该冲击对其他关联资产的连带影响与置信区间。
4. 🕰️ **历史事件回测 (Event Backtest)**：
   选取历史重大黑天鹅/宏观事件（如：疫情爆发、金融危机等），回测并展现事件发生前后关键经济指标的波动范围及变化率。
5. 📊 **实时宏观基本盘监控**：
   内置对全球核心宏观数据（如 CPI 通胀、非农就业、大宗商品等）的高密度 Grid 面板展示，支持自定义查询日期区间。

---

## 🚀 技术架构与部署

MacroDashboard 采用完全本地化的架构，支持离线或局域网私有化全量运行。数据源直接对接 **[FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)**。

| 类别 (Category)     | 指标 (Indicators)                                                                 |
| ------------------- | --------------------------------------------------------------------------------- |
| **利率 Rates**      | 美债 10 年期收益率 (US10Y), 美债 2 年期收益率 (US2Y), 联邦基金利率 (FEDFUNDS)      |
| **外汇 FX**         | 欧元兑美元 (EURUSD), 美元兑日圆 (USDJPY), 美元兑人民币 (USDCNY)                   |
| **大宗商品 Commodity**| WTI 原油 (WTI), 黄金 (GOLD)                                                       |
| **通胀 Inflation**  | 全项目 CPI (CPI_US), 核心 CPI (CPI_CORE_US)                                       |
| **劳动力市场 Labor**  | 失业率 (UNRATE_US), 非农就业 (PAYEMS_US), 劳动力参与率 (CIVPART_US)                |

---

## 🛠️ 技术栈架构

**前端 (Frontend) - Port 8021**
- `React 18` + `TypeScript` + `Vite`
- 视觉渲染: `Recharts`, 深度定制化全局 CSS (Grid & Glassmorphism)

**后端引擎 (Backend) - Port 8020**
- API 服务层: `FastAPI` (Python 3.11)
- 缓存层缓冲: `Redis 7`
- 关系型持久化: `PostgreSQL 16`
- 数据采集器: 轻量化 Python 脚本配合定时任务 `Cron`

---

## 🚀 极速部署 (Docker)

在运行部署之前，请确保您已经免费申请了 [FRED API Key](https://fred.stlouisfed.org/docs/api/api_key.html)。

1. **克隆项目并配置环境**
   ```bash
   git clone https://github.com/K1ndredzzz/MacroDashboard.git
   cd MacroDashboard
   cp .env.example .env
   ```
2. **填入您的安全凭证**
   编辑 `.env` 文件，补充您的 `POSTGRES_PASSWORD` 和 `FRED_API_KEY`。

3. **一键拉起容器矩阵**
   ```bash
   docker-compose up -d
   ```

4. **即可访问**
   - 绝美终端演示：`http://localhost:8021`
   - FastAPI 接口文档：`http://localhost:8020/api/v1/docs`

对于深度的运维管理与数据备份指南，请查阅 [部署指南 DEPLOYMENT.md](./docs/DEPLOYMENT.md)。

---

## 🤝 贡献与许可
本项目采用 **MIT License** 许可协议。
遇到任何 BUG 或有绝妙的功能改进想法，欢迎提交 [Issues](https://github.com/K1ndredzzz/MacroDashboard/issues) 与 PR。

> **免责声明**：本项目仅供学习研究和技术演示使用。它**不**构成任何形式的投资、财务、或交易建议。请您在进行实际决策前独立审查宏观市场各项情况。
