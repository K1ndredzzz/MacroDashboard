# Macro Dashboard

宏观经济实时仪表盘 - 全栈数据可视化平台

## 项目概述

自动采集、存储和可视化宏观经济数据的完整解决方案。支持 GCP 云端部署或自托管服务器部署。

### 核心功能
- 自动采集宏观经济数据（FRED API）
- PostgreSQL 数据仓库存储历史数据
- FastAPI 后端 API 服务
- React + TypeScript 可视化仪表盘
- Docker Compose 一键部署
- 支持 GCP 或自托管服务器

### 核心指标
- **利率**: 美债利率曲线（2Y/10Y）、联邦基金利率
- **外汇**: EURUSD、USDCNY、USDJPY
- **大宗商品**: WTI 原油、黄金
- **通胀**: CPI、核心 CPI
- **就业**: 失业率、非农就业、劳动参与率

## 🚀 快速部署

### 方式 1: 一键部署脚本（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/MacroDashboard.git
cd MacroDashboard

# 2. 配置环境变量
cp .env.example .env
nano .env  # 填入 POSTGRES_PASSWORD 和 FRED_API_KEY

# 3. 运行部署脚本
./deploy.sh
```

### 方式 2: 手动部署

```bash
# 配置环境变量
cp .env.example .env
nano .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 访问应用

- **前端界面**: http://localhost
- **API 文档**: http://localhost:8000/api/v1/docs
- **健康检查**: http://localhost:8000/api/v1/health

## 技术架构

### 完整技术栈
- **前端**: React 18 + TypeScript + Vite + TanStack Query
- **后端**: FastAPI + Python 3.11 + Uvicorn
- **数据库**: PostgreSQL 16
- **缓存**: Redis 7
- **容器化**: Docker + Docker Compose
- **数据源**: FRED API

### 系统架构

```
┌─────────────┐
│   Frontend  │  React + Nginx
│    :80      │
└──────┬──────┘
       │
┌──────▼──────┐
│     API     │  FastAPI
│   :8000     │
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────┐
│ PostgreSQL  │◄────┤ Cron Job │  数据采集
│   :5432     │     └──────────┘
└──────┬──────┘
       │
┌──────▼──────┐
│    Redis    │  缓存
│   :6379     │
└─────────────┘
```

## 项目结构

```
MacroDashboard/
├── backend/
│   ├── api/                    # FastAPI 应用
│   │   ├── app/
│   │   │   ├── api/v1/        # API 端点
│   │   │   ├── core/          # 配置
│   │   │   ├── repositories/  # 数据访问层
│   │   │   ├── schemas/       # Pydantic 模型
│   │   │   └── services/      # 业务服务
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── functions/              # 数据采集
│   │   ├── ingest_fred/       # FRED 数据采集
│   │   ├── common/            # 共享代码
│   │   └── Dockerfile.collector
│   └── scripts/
│       ├── postgres/          # PostgreSQL 初始化
│       └── migration/         # BigQuery 迁移工具
├── frontend/                   # React 应用
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── hooks/            # React Hooks
│   │   ├── services/         # API 服务
│   │   └── types/            # TypeScript 类型
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                       # 文档
│   ├── azure_deployment_guide.md
│   └── implementation_plan.md
├── docker-compose.yml          # Docker Compose 配置
├── .env.example               # 环境变量模板
├── deploy.sh                  # 一键部署脚本
├── DEPLOYMENT.md              # 部署说明
└── README.md
```

## 环境变量配置

必填项：

```bash
POSTGRES_PASSWORD=your_secure_password
FRED_API_KEY=your_fred_api_key  # 从 https://fred.stlouisfed.org 获取
```

可选项：

```bash
CRON_SCHEDULE=0 */6 * * *  # 数据采集频率（默认每6小时）
FRONTEND_API_URL=http://your-server-ip:8000  # 前端 API 地址
```

## 数据迁移

如果您已在 GCP BigQuery 上有数据，可以迁移到 PostgreSQL：

```bash
# 1. 导出 BigQuery 数据（本地执行）
cd backend/scripts/migration
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
python export_from_bigquery.py

# 2. 上传到服务器
scp -r migration_data user@server:/path/to/MacroDashboard/backend/scripts/migration/

# 3. 导入到 PostgreSQL（服务器执行）
cd backend/scripts/migration
export POSTGRES_PASSWORD=your_password
python import_to_postgres.py
```

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 备份数据库
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql

# 恢复数据库
docker exec -i macro-postgres psql -U macro_user macro_dashboard < backup.sql

# 手动触发数据采集
docker exec macro-collector python -m ingest_fred.main
```

## 部署选项

### 选项 1: 自托管服务器（推荐）
- **成本**: ¥200-300/月（Azure 2核4G）
- **优势**: 完全控制、无供应商锁定
- **文档**: [Azure 部署指南](docs/azure_deployment_guide.md)

### 选项 2: GCP Cloud Run
- **成本**: ~$20/月
- **优势**: 自动扩展、托管服务
- **文档**: [GCP 部署指南](docs/deployment_summary.md)

## 性能指标

- **API 响应时间**: < 500ms (P95)
- **缓存命中率**: > 80%
- **数据更新频率**: 每 6 小时
- **支持并发**: 100+ 用户

## 开发计划

详见 [实施计划](docs/implementation_plan.md)

## 相关文档

- [完整部署指南](DEPLOYMENT.md)
- [Azure 部署指南](docs/azure_deployment_guide.md)
- [API 文档](backend/api/README.md)
- [前端文档](frontend/README.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
