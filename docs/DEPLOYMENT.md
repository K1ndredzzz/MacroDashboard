# 部署和维护指南

## 快速部署

### 前置要求
- Docker 和 Docker Compose
- FRED API Key（从 https://fred.stlouisfed.org/docs/api/api_key.html 获取）

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

填入以下必填项：
```bash
POSTGRES_PASSWORD=your_secure_password
FRED_API_KEY=your_fred_api_key
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **验证部署**
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问服务
# 前端: http://localhost:8021
# API 文档: http://localhost:8020/api/v1/docs
```

## 端口配置

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| PostgreSQL | 5432 | 5433 | 数据库 |
| Redis | 6379 | 6380 | 缓存 |
| API | 8000 | 8020 | 后端 API |
| Frontend | 80 | 8021 | 前端界面 |

## 日常维护

### 1. 查看服务状态

```bash
# 查看所有容器状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f data-collector
docker-compose logs -f postgres
```

### 2. 数据采集监控

数据采集器每 6 小时自动运行一次（可在 `.env` 中修改 `CRON_SCHEDULE`）。

**查看采集日志：**
```bash
docker-compose logs data-collector --tail 100
```

**手动触发采集：**
```bash
docker exec macro-collector python /app/collect_data.py
```

**查看采集历史：**
```bash
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "
SELECT run_id, source, status, started_at, records_inserted
FROM ops.etl_runs
ORDER BY started_at DESC
LIMIT 10;
"
```

### 3. 数据库维护

**查看数据量：**
```bash
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "
SELECT
    indicator_code,
    COUNT(*) as observation_count,
    MIN(observation_date) as first_date,
    MAX(observation_date) as last_date
FROM core.fact_observations
GROUP BY indicator_code
ORDER BY indicator_code;
"
```

**备份数据库：**
```bash
# 创建备份
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup_$(date +%Y%m%d).sql

# 恢复备份
cat backup_20260221.sql | docker exec -i macro-postgres psql -U macro_user -d macro_dashboard
```

**清理旧数据（可选）：**
```bash
# 删除 1 年前的数据
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "
DELETE FROM core.fact_observations
WHERE observation_date < NOW() - INTERVAL '1 year';
"
```

### 4. 更新服务

**更新到最新版本：**
```bash
# 拉取最新代码
git pull origin main

# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

**仅更新特定服务：**
```bash
# 更新 API
docker-compose pull api
docker-compose up -d api

# 更新前端
docker-compose pull frontend
docker-compose up -d frontend
```

### 5. 性能监控

**查看容器资源使用：**
```bash
docker stats
```

**查看数据库连接：**
```bash
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE datname = 'macro_dashboard';
"
```

**查看 Redis 状态：**
```bash
docker exec macro-redis redis-cli INFO stats
```

### 6. 故障排查

**API 无法访问：**
```bash
# 检查 API 健康状态
curl http://localhost:8020/api/v1/health

# 查看 API 日志
docker-compose logs api --tail 50

# 重启 API
docker-compose restart api
```

**前端加载失败：**
```bash
# 检查前端容器
docker-compose logs frontend --tail 50

# 检查 CORS 配置
curl -I http://localhost:8020/api/v1/dashboard/overview

# 重启前端
docker-compose restart frontend
```

**数据采集失败：**
```bash
# 查看 collector 日志
docker-compose logs data-collector --tail 100

# 检查 FRED API Key
docker exec macro-collector env | grep FRED_API_KEY

# 手动测试采集
docker exec macro-collector python /app/collect_data.py
```

**数据库连接失败：**
```bash
# 检查数据库状态
docker exec macro-postgres pg_isready -U macro_user

# 查看数据库日志
docker-compose logs postgres --tail 50

# 重启数据库
docker-compose restart postgres
```

## 安全建议

### 1. 生产环境配置

**修改默认密码：**
```bash
# 在 .env 中使用强密码
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

**限制访问：**
```yaml
# 在 docker-compose.yml 中，仅暴露必要端口
# 生产环境建议使用反向代理（Nginx/Caddy）
```

**启用 HTTPS：**
```bash
# 使用 Nginx 或 Caddy 作为反向代理
# 配置 SSL 证书（Let's Encrypt）
```

### 2. 备份策略

**自动备份脚本：**
```bash
#!/bin/bash
# backup.sh - 每天自动备份数据库

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
docker exec macro-postgres pg_dump -U macro_user macro_dashboard | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# 保留最近 30 天的备份
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**添加到 crontab：**
```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh >> /var/log/macro-backup.log 2>&1
```

## 扩展功能

### 1. 添加新的数据源

编辑 `backend/functions/collect_data.py`，在 `FRED_SERIES` 列表中添加新的指标代码：

```python
FRED_SERIES = [
    "DGS2",         # US 2Y Treasury
    "DGS10",        # US 10Y Treasury
    # ... 添加更多指标
    "YOUR_SERIES_ID",  # 新指标
]
```

### 2. 修改采集频率

编辑 `.env` 文件：
```bash
# 每 3 小时采集一次
CRON_SCHEDULE="0 */3 * * *"

# 每天凌晨 1 点采集
CRON_SCHEDULE="0 1 * * *"
```

### 3. 自定义前端

前端源码位于 `frontend/src/`，修改后重新构建：

```bash
cd frontend
npm install
npm run build

# 或重新构建 Docker 镜像
docker build -t your-username/macro-dashboard-frontend:latest .
```

## 关于 n8n

**不需要 n8n**。本项目已经使用 Docker 内置的 cron 实现了定时数据采集，功能完整且轻量。

如果你需要更复杂的工作流（如数据采集失败时发送通知、多数据源编排等），可以考虑集成 n8n，但对于当前需求来说不是必需的。

## 监控告警（可选）

如果需要监控和告警，可以集成：

1. **Prometheus + Grafana**：监控容器和应用指标
2. **Uptime Kuma**：监控服务可用性
3. **Webhook 通知**：数据采集失败时发送通知

示例：在 `collect_data.py` 中添加失败通知：
```python
import requests

def send_alert(message):
    # 发送到 Slack/Discord/企业微信等
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})

# 在 main() 函数中
if status == "failed":
    send_alert(f"Data collection failed: {error_message}")
```

## 常见问题

参考 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 获取详细的故障排查指南。

## 技术支持

- GitHub Issues: https://github.com/K1ndredzzz/MacroDashboard/issues
- 文档: https://github.com/K1ndredzzz/MacroDashboard/tree/main/docs
