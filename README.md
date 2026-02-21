# Macro Economic Dashboard

一个基于 FRED API 的宏观经济数据仪表板，提供实时经济指标监控和可视化。

## 特性

- 📊 **实时数据**：自动从 FRED API 采集最新经济数据
- 🔄 **自动更新**：每 6 小时自动更新数据（可配置）
- 💾 **本地存储**：使用 PostgreSQL 本地存储，无需依赖云服务
- 🚀 **容器化部署**：Docker Compose 一键部署
- 📈 **数据可视化**：直观的图表展示经济指标趋势
- ⚡ **高性能**：Redis 缓存加速数据访问

## 监控指标

### 利率 (Rates)
- US 10-Year Treasury Yield (US10Y)
- US 2-Year Treasury Yield (US2Y)
- Federal Funds Rate (FEDFUNDS)

### 外汇 (FX)
- EUR/USD Exchange Rate (EURUSD)
- USD/CNY Exchange Rate (USDCNY)
- USD/JPY Exchange Rate (USDJPY)

### 大宗商品 (Commodity)
- WTI Crude Oil Price (WTI)
- Gold Price (GOLD)

### 通胀 (Inflation)
- US CPI All Items (CPI_US)
- US Core CPI (CPI_CORE_US)

### 劳动力市场 (Labor)
- US Unemployment Rate (UNRATE_US)
- US Nonfarm Payrolls (PAYEMS_US)
- US Labor Force Participation Rate (CIVPART_US)
- US Average Hourly Earnings (AHETPI_US)

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- FRED API Key（免费申请：https://fred.stlouisfed.org/docs/api/api_key.html）

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/K1ndredzzz/MacroDashboard.git
cd MacroDashboard
```

2. **配置环境变量**
```bash
cp .env.example .env
nano .env
```

填入必填项：
```bash
POSTGRES_PASSWORD=your_secure_password
FRED_API_KEY=your_fred_api_key
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端界面：http://localhost:8021
- API 文档：http://localhost:8020/api/v1/docs
- 健康检查：http://localhost:8020/api/v1/health

## 架构

```
┌─────────────────┐
│   Frontend      │  React + TypeScript + Vite
│   (Port 8021)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Server    │  FastAPI + Python 3.11
│   (Port 8020)   │
└────┬───────┬────┘
     │       │
     ▼       ▼
┌─────────┐ ┌──────────┐
│ Redis   │ │PostgreSQL│
│(Port    │ │(Port     │
│ 6380)   │ │ 5433)    │
└─────────┘ └──────────┘
     ▲           ▲
     │           │
┌────┴───────────┴────┐
│  Data Collector     │  Cron Job (每 6 小时)
│  FRED API → DB      │
└─────────────────────┘
```

## 技术栈

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **PostgreSQL 16**: 关系型数据库
- **Redis 7**: 缓存层
- **psycopg2**: PostgreSQL 驱动
- **FRED API**: 经济数据源

### 前端
- **React 18**: UI 框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Recharts**: 数据可视化
- **Axios**: HTTP 客户端

### 基础设施
- **Docker**: 容器化
- **Docker Compose**: 服务编排
- **Nginx**: 前端服务器
- **Cron**: 定时任务

## 项目结构

```
MacroDashboard/
├── backend/
│   ├── api/                    # FastAPI 应用
│   │   ├── app/
│   │   │   ├── api/v1/        # API 路由
│   │   │   ├── core/          # 核心配置
│   │   │   ├── repositories/  # 数据访问层
│   │   │   └── main.py        # 应用入口
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── functions/              # 数据采集
│   │   ├── fred/              # FRED 数据提取和转换
│   │   ├── common/            # 共享代码
│   │   ├── collect_data.py    # 采集脚本
│   │   └── Dockerfile.collector
│   └── scripts/
│       └── postgres/          # 数据库初始化脚本
│           └── 01_init_schema.sql
├── frontend/
│   ├── src/
│   │   ├── components/        # React 组件
│   │   ├── services/          # API 服务
│   │   ├── types/             # TypeScript 类型
│   │   └── App.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/
│   ├── DEPLOYMENT.md          # 部署和维护指南
│   └── TROUBLESHOOTING.md     # 故障排查指南
├── docker-compose.yml         # 服务编排配置
├── .env.example               # 环境变量模板
└── README.md
```

## 维护指南

### 查看服务状态
```bash
docker-compose ps
docker-compose logs -f
```

### 查看数据采集日志
```bash
docker-compose logs data-collector --tail 100
```

### 手动触发数据采集
```bash
docker exec macro-collector python /app/collect_data.py
```

### 备份数据库
```bash
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql
```

### 更新服务
```bash
git pull origin main
docker-compose pull
docker-compose up -d
```

详细维护指南请参考 [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

## 故障排查

遇到问题？查看 [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) 获取详细的故障排查指南。

常见问题：
- 端口冲突
- 数据库未初始化
- CORS 错误
- 数据采集失败

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `POSTGRES_PASSWORD` | PostgreSQL 密码 | - | ✓ |
| `FRED_API_KEY` | FRED API 密钥 | - | ✓ |
| `CRON_SCHEDULE` | 数据采集频率 | `"0 */6 * * *"` | ✗ |

### 端口配置

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| PostgreSQL | 5432 | 5433 | 避免与本地 PostgreSQL 冲突 |
| Redis | 6379 | 6380 | 避免与本地 Redis 冲突 |
| API | 8000 | 8020 | 后端 API 服务 |
| Frontend | 80 | 8021 | 前端界面 |

## 性能优化

- **Redis 缓存**：API 响应缓存，减少数据库查询
- **连接池**：PostgreSQL 连接池，提高并发性能
- **索引优化**：数据库索引优化查询速度
- **Gzip 压缩**：Nginx 启用 Gzip 压缩静态资源

## 安全建议

1. **修改默认密码**：使用强密码
2. **限制访问**：使用防火墙限制端口访问
3. **启用 HTTPS**：生产环境使用 SSL 证书
4. **定期备份**：设置自动备份策略
5. **更新依赖**：定期更新 Docker 镜像

## 扩展功能

### 添加新指标

编辑 `backend/functions/collect_data.py`：
```python
FRED_SERIES = [
    "DGS2",
    "DGS10",
    # 添加新的 FRED 系列 ID
    "YOUR_SERIES_ID",
]
```

### 修改采集频率

编辑 `.env` 文件：
```bash
# 每 3 小时采集一次
CRON_SCHEDULE="0 */3 * * *"
```

### 自定义前端

修改 `frontend/src/` 中的组件，然后重新构建：
```bash
cd frontend
npm run build
```

## 关于 n8n

**不需要 n8n**。本项目已经使用 Docker 内置的 cron 实现了定时数据采集，功能完整且轻量。

如果你需要更复杂的工作流（如数据采集失败时发送通知、多数据源编排等），可以考虑集成 n8n，但对于当前需求来说不是必需的。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- 数据来源：[FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/)
- 图标：[Lucide Icons](https://lucide.dev/)

## 联系方式

- GitHub: https://github.com/K1ndredzzz/MacroDashboard
- Issues: https://github.com/K1ndredzzz/MacroDashboard/issues

---

**注意**：本项目仅供学习和研究使用，不构成任何投资建议。
