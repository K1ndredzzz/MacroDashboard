# 自托管部署方案（Azure 2核4G）

## 背景
- GCP Free Trial $300 即将到期
- 目标：将服务迁移到 Azure 2核4G 云服务器
- 保持核心功能：数据采集 + API 后端 + 前端仪表板

---

## 架构调整

### 当前 GCP 架构
```
Cloud Scheduler → Cloud Functions → BigQuery
                                   ↓
                          Cloud Run (FastAPI)
```

### 自托管架构
```
Cron Job → Python Script → PostgreSQL/SQLite
                          ↓
                    FastAPI (Docker)
                          ↓
                    React Frontend (Nginx)
```

---

## 资源需求评估

### Azure 2核4G 服务器配置
- **CPU**: 2 核心
- **内存**: 4GB RAM
- **存储**: 建议至少 40GB SSD
- **操作系统**: Ubuntu 22.04 LTS

### 服务资源分配
```
PostgreSQL:     ~512MB RAM
FastAPI:        ~256MB RAM
Nginx:          ~64MB RAM
Cron Jobs:      ~128MB RAM (运行时)
系统开销:       ~1GB RAM
剩余:           ~2GB RAM (缓冲)
```

---

## 迁移方案

### Phase 1: 数据存储迁移（BigQuery → PostgreSQL）

#### 1.1 导出 BigQuery 数据
```bash
# 导出 dim_series
bq extract --destination_format=CSV \
  gen-lang-client-0815236933:macro_core.dim_series \
  gs://macro-dashboard-export/dim_series.csv

# 导出 fact_observation
bq extract --destination_format=CSV \
  gen-lang-client-0815236933:macro_core.fact_observation \
  gs://macro-dashboard-export/fact_observation.csv

# 下载到本地
gsutil cp gs://macro-dashboard-export/*.csv ./data/
```

#### 1.2 PostgreSQL 设置
```bash
# 安装 PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres psql
CREATE DATABASE macro_dashboard;
CREATE USER macro_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE macro_dashboard TO macro_user;
```

#### 1.3 导入数据
```sql
-- 创建表结构（使用 backend/bigquery/ddl/ 中的 SQL，调整为 PostgreSQL 语法）
-- 导入 CSV 数据
COPY dim_series FROM '/path/to/dim_series.csv' CSV HEADER;
COPY fact_observation FROM '/path/to/fact_observation.csv' CSV HEADER;
```

### Phase 2: 数据采集迁移（Cloud Functions → Cron + Python）

#### 2.1 复用现有代码
```bash
# 将 backend/functions/ 代码复制到服务器
scp -r backend/functions/ user@azure-server:/opt/macro-dashboard/
```

#### 2.2 配置 Cron Job
```bash
# 编辑 crontab
crontab -e

# 每日 8:00 AM UTC 执行 FRED 数据采集
0 8 * * * cd /opt/macro-dashboard/functions && python -m fred.main >> /var/log/macro-fred.log 2>&1
```

#### 2.3 环境变量配置
```bash
# /opt/macro-dashboard/.env
FRED_API_KEY=your_fred_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=macro_dashboard
DB_USER=macro_user
DB_PASSWORD=your_secure_password
```

### Phase 3: API 后端迁移（Cloud Run → Docker）

#### 3.1 Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: macro_dashboard
      POSTGRES_USER: macro_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  api:
    build: ./backend/api
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: macro_dashboard
      DB_USER: macro_user
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_ENABLED: "False"
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3.2 部署命令
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Phase 4: 前端部署（待 React 开发完成）

#### 4.1 Nginx 配置
```nginx
# /etc/nginx/sites-available/macro-dashboard
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/macro-dashboard;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 成本对比

### GCP 成本（Free Trial 后）
- Cloud Functions: ~$5/月
- Cloud Run: ~$10/月
- BigQuery: ~$5/月
- Cloud Scheduler: $0.10/月
- **总计**: ~$20/月

### Azure 自托管成本
- Azure VM (2核4G): 已有
- 域名（可选）: ~$10/年
- **总计**: $0/月（仅 VM 成本）

---

## 性能优化建议

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_observation_date ON fact_observation(observation_date);
CREATE INDEX idx_indicator_code ON fact_observation(indicator_code);
CREATE INDEX idx_series_uid ON fact_observation(series_uid);

-- 定期 VACUUM
VACUUM ANALYZE fact_observation;
```

### 2. API 缓存
```python
# 使用内存缓存替代 Redis
from functools import lru_cache

@lru_cache(maxsize=128)
def get_indicators():
    # 缓存指标列表
    pass
```

### 3. 数据库连接池
```python
# 使用 SQLAlchemy 连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

---

## 迁移步骤清单

### 准备阶段
- [ ] 导出 BigQuery 数据到 CSV
- [ ] 在 Azure 服务器上安装 Docker 和 Docker Compose
- [ ] 安装 PostgreSQL
- [ ] 配置防火墙规则（开放 80, 443, 8000 端口）

### 迁移阶段
- [ ] 导入数据到 PostgreSQL
- [ ] 修改 FastAPI 代码以使用 PostgreSQL
- [ ] 测试数据采集脚本
- [ ] 配置 Cron Job
- [ ] 部署 Docker Compose
- [ ] 配置 Nginx（前端完成后）

### 验证阶段
- [ ] 测试 API 端点
- [ ] 验证数据采集正常
- [ ] 性能测试
- [ ] 监控设置

---

## 监控和维护

### 日志管理
```bash
# 查看 API 日志
docker-compose logs -f api

# 查看数据采集日志
tail -f /var/log/macro-fred.log

# 查看 PostgreSQL 日志
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### 备份策略
```bash
# 每日备份数据库
0 2 * * * pg_dump -U macro_user macro_dashboard | gzip > /backup/macro_$(date +\%Y\%m\%d).sql.gz

# 保留最近 7 天的备份
find /backup -name "macro_*.sql.gz" -mtime +7 -delete
```

### 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop

# 监控磁盘空间
df -h

# 监控内存使用
free -h

# 监控 Docker 容器
docker stats
```

---

## 代码修改清单

### 1. 数据库适配器
创建 `backend/api/app/repositories/postgres_repo.py`，替换 `bigquery_repo.py`

### 2. 数据采集脚本
修改 `backend/functions/common/loaders.py`，支持 PostgreSQL

### 3. 配置文件
更新 `backend/api/app/core/config.py`，添加 PostgreSQL 配置

### 4. Docker Compose
创建完整的 `docker-compose.yml`

---

## 时间估算

- **数据导出和导入**: 2-3 小时
- **代码修改和测试**: 4-6 小时
- **部署和配置**: 2-3 小时
- **验证和优化**: 2-3 小时
- **总计**: 1-2 天

---

## 注意事项

1. **数据一致性**: 迁移前确保 BigQuery 数据完整
2. **API 兼容性**: 保持 API 接口不变，前端无需修改
3. **性能监控**: 迁移后密切监控服务器资源使用
4. **备份策略**: 定期备份数据库和配置文件
5. **安全性**:
   - 使用强密码
   - 配置防火墙
   - 定期更新系统
   - 使用 HTTPS（Let's Encrypt）

---

## 下一步行动

1. **立即**: 继续使用 GCP 完成前端开发
2. **Free Trial 剩余 $50 时**: 开始准备迁移
3. **Free Trial 到期前**: 完成迁移并验证
4. **迁移后**: 关闭 GCP 资源，避免产生费用
