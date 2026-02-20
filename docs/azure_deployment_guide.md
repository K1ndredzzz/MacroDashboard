# Azure 自托管部署指南

本指南帮助您将宏观经济仪表盘从 GCP 迁移到 Azure 服务器（2核4G）。

## 📋 前置要求

### 服务器要求
- **配置**: 2核4G 或更高
- **操作系统**: Ubuntu 20.04+ / Debian 11+
- **磁盘空间**: 至少 20GB 可用空间
- **网络**: 公网 IP 地址

### 本地要求
- Docker 和 Docker Compose
- Git
- Python 3.11+ (用于数据迁移)
- GCP 凭证 (仅用于数据导出)

## 🚀 快速部署（3 步完成）

### 步骤 1: 服务器准备

SSH 登录到您的 Azure 服务器：

```bash
ssh your-user@your-server-ip
```

安装 Docker 和 Docker Compose：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose -y

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录以应用组权限
exit
```

### 步骤 2: 部署应用

重新登录后，克隆项目：

```bash
# 克隆项目
git clone https://github.com/your-username/MacroDashboard.git
cd MacroDashboard

# 创建环境变量文件
cp .env.example .env
nano .env  # 编辑配置
```

配置 `.env` 文件：

```bash
# 必填项
POSTGRES_PASSWORD=your_secure_password
FRED_API_KEY=your_fred_api_key

# 可选项（使用默认值即可）
CRON_SCHEDULE=0 */6 * * *
FRONTEND_API_URL=http://your-server-ip:8000
```

启动所有服务：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 步骤 3: 数据迁移（可选）

如果您已经在 GCP 上有数据，可以迁移到 PostgreSQL：

```bash
# 在本地机器上执行（需要 GCP 凭证）

# 1. 导出 BigQuery 数据
cd backend/scripts/migration
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/gcp-key.json
python export_from_bigquery.py

# 2. 将数据上传到服务器
scp -r migration_data your-user@your-server-ip:~/MacroDashboard/backend/scripts/migration/

# 3. 在服务器上导入数据
ssh your-user@your-server-ip
cd MacroDashboard/backend/scripts/migration
export POSTGRES_PASSWORD=your_password
python import_to_postgres.py
```

## ✅ 验证部署

访问以下 URL 验证服务：

```bash
# API 健康检查
curl http://your-server-ip:8000/api/v1/health

# 前端界面
http://your-server-ip

# API 文档
http://your-server-ip:8000/api/v1/docs
```

## 📊 服务架构

```
┌─────────────────────────────────────────────────┐
│                  Azure 服务器                    │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Frontend │  │   API    │  │  Redis   │     │
│  │  :80     │  │  :8000   │  │  :6379   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │              │            │
│       └─────────────┴──────────────┘            │
│                     │                           │
│              ┌──────┴──────┐                    │
│              │  PostgreSQL │                    │
│              │    :5432    │                    │
│              └─────────────┘                    │
│                     ▲                           │
│              ┌──────┴──────┐                    │
│              │   Cron Job  │                    │
│              │ (每6小时)    │                    │
│              └─────────────┘                    │
└─────────────────────────────────────────────────┘
```

## 🔧 常用命令

### Docker Compose 管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 查看服务状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache
```

### 数据库管理

```bash
# 连接到 PostgreSQL
docker exec -it macro-postgres psql -U macro_user -d macro_dashboard

# 备份数据库
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql

# 恢复数据库
docker exec -i macro-postgres psql -U macro_user macro_dashboard < backup.sql

# 查看数据库大小
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT pg_size_pretty(pg_database_size('macro_dashboard'));"
```

### 查看数据采集日志

```bash
# 查看 cron 日志
docker exec macro-collector tail -f /var/log/cron/collector.log

# 手动触发数据采集
docker exec macro-collector python -m ingest_fred.main
```

## 🔐 安全建议

1. **修改默认密码**: 确保 `.env` 中的 `POSTGRES_PASSWORD` 使用强密码
2. **防火墙配置**: 只开放必要的端口（80, 443）
3. **定期备份**: 设置自动备份脚本
4. **更新依赖**: 定期更新 Docker 镜像

```bash
# 配置防火墙（UFW）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📈 性能优化

### 资源限制（可选）

编辑 `docker-compose.yml` 添加资源限制：

```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          memory: 512M
```

### PostgreSQL 调优

编辑 PostgreSQL 配置：

```bash
# 创建自定义配置
cat > postgres.conf <<EOF
shared_buffers = 512MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
EOF

# 在 docker-compose.yml 中挂载配置
volumes:
  - ./postgres.conf:/etc/postgresql/postgresql.conf
command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

## 🔄 更新应用

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs -f
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs [service_name]

# 检查端口占用
sudo netstat -tulpn | grep -E ':(80|8000|5432|6379)'

# 重置所有容器
docker-compose down -v
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker-compose ps postgres

# 测试数据库连接
docker exec macro-postgres pg_isready -U macro_user

# 查看 PostgreSQL 日志
docker-compose logs postgres
```

### 前端无法访问 API

1. 检查 `.env` 中的 `FRONTEND_API_URL` 是否正确
2. 确认 API 服务正在运行：`curl http://localhost:8000/api/v1/health`
3. 检查 CORS 配置：`backend/api/app/main.py`

## 💰 成本估算

### Azure 2核4G 服务器
- **月费用**: ¥200-300/月（按量付费）
- **流量**: 通常包含 1TB 免费流量
- **存储**: 40GB SSD 系统盘

### 总成本
- **服务器**: ¥200-300/月
- **域名**: ¥50-100/年（可选）
- **SSL 证书**: 免费（Let's Encrypt）

**对比 GCP**: 从 $20/月 降至 ¥200-300/月（约 $28-42），但拥有完全控制权。

## 📚 相关文档

- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [FRED API 文档](https://fred.stlouisfed.org/docs/api/)
- [Nginx 文档](https://nginx.org/en/docs/)

## 🆘 获取帮助

如遇问题，请检查：
1. Docker 日志：`docker-compose logs -f`
2. 系统资源：`docker stats`
3. 磁盘空间：`df -h`
4. 内存使用：`free -h`

---

**部署完成后，您的宏观经济仪表盘将 24/7 运行在您的 Azure 服务器上！** 🎉
