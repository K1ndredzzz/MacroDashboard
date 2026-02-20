# 🚀 一键部署到 Azure

本项目支持快速部署到任何 Linux 服务器（推荐 2核4G 或更高配置）。

## 快速开始

### 1. 服务器准备

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose -y
```

### 2. 部署应用

```bash
# 克隆项目
git clone https://github.com/your-username/MacroDashboard.git
cd MacroDashboard

# 配置环境变量
cp .env.example .env
nano .env  # 填入 POSTGRES_PASSWORD 和 FRED_API_KEY

# 启动服务
docker-compose up -d
```

### 3. 访问应用

- **前端**: http://your-server-ip
- **API 文档**: http://your-server-ip:8000/api/v1/docs
- **健康检查**: http://your-server-ip:8000/api/v1/health

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

## 数据迁移（可选）

如果您已在 GCP 上有数据：

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
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 备份数据库
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql
```

## 架构说明

```
Frontend (Nginx) :80
    ↓
API (FastAPI) :8000
    ↓
PostgreSQL :5432 ← Cron Job (每6小时采集数据)
    ↓
Redis :6379 (缓存)
```

## 技术栈

- **前端**: React 18 + TypeScript + Vite
- **后端**: FastAPI + Python 3.11
- **数据库**: PostgreSQL 16
- **缓存**: Redis 7
- **容器化**: Docker + Docker Compose

## 详细文档

- [完整部署指南](docs/azure_deployment_guide.md)
- [API 文档](backend/api/README.md)
- [前端文档](frontend/README.md)

## 成本估算

- **Azure 2核4G**: ¥200-300/月
- **流量**: 1TB 免费
- **总成本**: 约 ¥200-300/月

## 许可证

MIT License

---

**问题反馈**: [GitHub Issues](https://github.com/your-username/MacroDashboard/issues)
