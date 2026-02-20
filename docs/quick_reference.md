# 快速参考

## 🚀 一键部署

```bash
git clone https://github.com/your-username/MacroDashboard.git
cd MacroDashboard
cp .env.example .env
nano .env  # 填入 POSTGRES_PASSWORD 和 FRED_API_KEY
./deploy.sh
```

## 🔗 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost | 主界面 |
| API 文档 | http://localhost:8000/api/v1/docs | Swagger UI |
| 健康检查 | http://localhost:8000/api/v1/health | 服务状态 |

## 📝 常用命令

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart [service_name]

# 查看日志
docker-compose logs -f [service_name]

# 查看服务状态
docker-compose ps

# 重新构建
docker-compose build --no-cache
```

### 数据库操作

```bash
# 连接到 PostgreSQL
docker exec -it macro-postgres psql -U macro_user -d macro_dashboard

# 备份数据库
docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i macro-postgres psql -U macro_user macro_dashboard < backup.sql

# 查看数据库大小
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT pg_size_pretty(pg_database_size('macro_dashboard'));"
```

### 数据采集

```bash
# 查看采集日志
docker exec macro-collector tail -f /var/log/cron/collector.log

# 手动触发采集
docker exec macro-collector python -m ingest_fred.main

# 查看采集任务状态
docker exec macro-collector crontab -l
```

### 监控和调试

```bash
# 查看容器资源使用
docker stats

# 查看磁盘空间
df -h

# 查看内存使用
free -h

# 查看系统负载
top

# 查看网络连接
netstat -tulpn | grep -E ':(80|8000|5432|6379)'
```

## 🔧 故障排查

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
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 测试数据库连接
docker exec macro-postgres pg_isready -U macro_user

# 查看 PostgreSQL 日志
docker-compose logs postgres
```

### API 无响应

```bash
# 检查 API 容器状态
docker-compose ps api

# 查看 API 日志
docker-compose logs api

# 测试 API 连接
curl http://localhost:8000/api/v1/health
```

### 前端无法访问 API

```bash
# 检查 CORS 配置
curl -H "Origin: http://localhost" -I http://localhost:8000/api/v1/health

# 检查环境变量
docker exec macro-frontend env | grep API

# 重新构建前端
docker-compose build frontend
docker-compose up -d frontend
```

## 📊 SQL 查询示例

```sql
-- 查看所有指标
SELECT * FROM core.dim_series WHERE is_active = true;

-- 查看最新数据
SELECT * FROM mart.v_latest_snapshot ORDER BY category, indicator_code;

-- 查看特定指标的历史数据
SELECT * FROM core.fact_observations
WHERE indicator_code = 'US10Y'
ORDER BY observation_date DESC
LIMIT 100;

-- 查看数据采集日志
SELECT * FROM ops.etl_runs
ORDER BY started_at DESC
LIMIT 10;

-- 统计各类别指标数量
SELECT category, COUNT(*) as count
FROM core.dim_series
WHERE is_active = true
GROUP BY category;
```

## 🔐 安全检查

```bash
# 检查防火墙状态
sudo ufw status

# 检查开放端口
sudo netstat -tulpn

# 检查 .env 文件权限
ls -la .env

# 确保敏感文件不在 git 中
git status --ignored
```

## 📈 性能优化

```bash
# 清理 Docker 缓存
docker system prune -a

# 清理 Redis 缓存
docker exec macro-redis redis-cli FLUSHALL

# 优化 PostgreSQL
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "VACUUM ANALYZE;"

# 查看 PostgreSQL 慢查询
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 📦 备份和恢复

```bash
# 完整备份
./scripts/backup.sh

# 仅备份数据库
docker exec macro-postgres pg_dump -U macro_user macro_dashboard | gzip > backup_$(date +%Y%m%d).sql.gz

# 恢复数据库
gunzip < backup.sql.gz | docker exec -i macro-postgres psql -U macro_user macro_dashboard

# 备份 Docker volumes
docker run --rm -v macro_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data
```

## 🔄 更新应用

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 查看日志确认
docker-compose logs -f
```

## 📞 获取帮助

- **文档**: [Azure 部署指南](docs/azure_deployment_guide.md)
- **检查清单**: [部署检查清单](docs/deployment_checklist.md)
- **API 文档**: http://localhost:8000/api/v1/docs
- **GitHub Issues**: https://github.com/your-username/MacroDashboard/issues
