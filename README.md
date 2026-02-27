# MacroDashboard V2 📊

MacroDashboard 是一款专为**量化金融**设计的宏观经济数据仪表板。
V2 版本带来了极致的**“控制室 (Control Room)”**拟态玻璃风 (Glassmorphism) UI，提供直观、高对比度、实时动态的全球宏观经济指标监控体系。

数据完全基于 **FRED API** 自动采集，应用采用现代化容器架构 (Docker Compose) 进行一键私有化部署。

![MacroDashboard V2 Preview](https://github.com/K1ndredzzz/MacroDashboard/assets/preview.png)

---

## 🌟 核心特性

- 🎨 **极致界面 (V2)**：引人注目的网格化布局，磨砂半透明深色卡片 (`Glassmorphism`)，辅以随波动呼吸的各类高对比财务指示器与荧光动效。
- 📊 **实时数据**：后台自动从 FRED API 拉取前沿的美国名义利率、通胀、就业及大宗商品数据。
- 🔄 **离线稳定**：使用本地 **PostgreSQL** 直接存盘并处理历史数据分析，不再强依赖任何第三方云服务。
- ⚡ **毫秒级响应**：引入 **Redis 7** 数据缓存层，配合 FastAPI 的高并发处理，数据面板即开即用。
- 🕒 **自动化 Cron**：脱离复杂的编排工具，采用极为轻量的内置 Cron 脚本，默认每 6 小时自动寻源并入库。

---

## 📈 核心监控矩阵

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
