# 新服务器部署指南

## 标准部署流程（无需修复脚本）

### 前提条件
- Docker 和 Docker Compose 已安装
- 已配置环境变量（`.env` 文件）

---

## 部署步骤

### 1. 克隆或上传项目代码
```bash
git clone <your-repo-url>
cd MacroDashboard
```

### 2. 配置环境变量
```bash
cp .env.example .env
nano .env
```

必需的环境变量：
```env
POSTGRES_PASSWORD=your_secure_password
FRED_API_KEY=your_fred_api_key
```

### 3. 启动服务
```bash
docker compose up -d
```

**重要**：首次启动时，PostgreSQL 会自动执行初始化脚本：
- `backend/scripts/postgres/01_init_schema.sql` - 创建 schema 和基础表
- `backend/scripts/postgres/02_events.sql` - 创建 events 表并插入数据

这些脚本会在容器首次启动时自动运行（通过 Docker 的 `/docker-entrypoint-initdb.d/` 机制）。

### 4. 验证部署
```bash
# 检查所有容器状态
docker compose ps

# 测试 API
curl http://localhost:8020/api/v1/health
curl http://localhost:8020/api/v1/events

# 访问前端
# 浏览器打开 http://localhost:8021
```

---

## 为什么不需要修复脚本？

### ✅ 自动初始化机制

Docker Compose 配置中，PostgreSQL 容器会自动执行初始化：

```yaml
# docker-compose.yml
postgres:
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./backend/scripts/postgres:/docker-entrypoint-initdb.d  # 自动执行 SQL 脚本
```

**工作原理**：
1. PostgreSQL 容器首次启动时
2. 检查 `/docker-entrypoint-initdb.d/` 目录
3. 按字母顺序执行所有 `.sql` 文件：
   - `01_init_schema.sql` → 创建 schema 和表
   - `02_events.sql` → 创建 events 表和数据

### ✅ 使用最新镜像

新服务器直接拉取最新镜像，包含所有最新代码：

```bash
# docker-compose.yml 中指定
api:
  image: fuzhouxing/macro-dashboard-api:latest  # 或 v2.0.1
```

---

## 什么情况下需要修复脚本？

### 场景 1: 升级现有服务器
如果服务器上已经运行了旧版本，需要：
- 更新代码（新增 Events API）
- 更新数据库（添加 events 表）

**此时需要**：`fix-events-api.sh`

### 场景 2: 数据库已存在但缺少 events 表
如果 PostgreSQL 数据卷已存在，不会重新执行初始化脚本。

**此时需要**：手动执行 `02_events.sql`

### 场景 3: 全新部署
数据库是空的，会自动执行所有初始化脚本。

**此时不需要**：任何修复脚本 ✅

---

## 部署检查清单

### 首次部署新服务器

- [ ] 1. 上传项目代码
- [ ] 2. 配置 `.env` 文件
- [ ] 3. 确认 `backend/scripts/postgres/` 目录包含：
  - [ ] `01_init_schema.sql`
  - [ ] `02_events.sql`
- [ ] 4. 运行 `docker compose up -d`
- [ ] 5. 等待容器启动（约 30 秒）
- [ ] 6. 验证：
  ```bash
  # 检查数据库
  docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT COUNT(*) FROM core.dim_events;"
  # 应该返回 7

  # 测试 API
  curl http://localhost:8020/api/v1/events
  # 应该返回 JSON 数组
  ```

### 升级现有服务器

- [ ] 1. 备份数据库
  ```bash
  docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql
  ```
- [ ] 2. 拉取最新代码
  ```bash
  git pull
  ```
- [ ] 3. 拉取最新镜像
  ```bash
  docker compose pull
  ```
- [ ] 4. 运行修复脚本（如果需要）
  ```bash
  bash fix-events-api.sh
  ```
- [ ] 5. 重启服务
  ```bash
  docker compose up -d
  ```

---

## 常见问题

### Q1: 如何确认数据库初始化脚本已执行？

```bash
# 检查 events 表
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "\dt core.*"

# 检查 events 数据
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT COUNT(*) FROM core.dim_events;"
```

### Q2: 如果初始化脚本没有自动执行怎么办？

可能原因：
1. 数据卷已存在（PostgreSQL 只在首次初始化时执行脚本）
2. 脚本路径不正确

**解决方案**：
```bash
# 手动执行初始化脚本
docker exec -i macro-postgres psql -U macro_user -d macro_dashboard < backend/scripts/postgres/01_init_schema.sql
docker exec -i macro-postgres psql -U macro_user -d macro_dashboard < backend/scripts/postgres/02_events.sql
```

### Q3: 如何完全重置数据库？

```bash
# 停止服务
docker compose down

# 删除数据卷
docker volume rm macro-network_postgres_data

# 重新启动（会重新初始化）
docker compose up -d
```

---

## 推荐的部署脚本

创建一个 `deploy.sh` 用于新服务器部署：

```bash
#!/bin/bash
set -e

echo "开始部署 MacroDashboard..."

# 1. 检查环境
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在"
    echo "请复制 .env.example 并配置环境变量"
    exit 1
fi

# 2. 拉取镜像
echo "拉取 Docker 镜像..."
docker compose pull

# 3. 启动服务
echo "启动服务..."
docker compose up -d

# 4. 等待服务启动
echo "等待服务启动..."
sleep 30

# 5. 验证部署
echo "验证部署..."

# 检查容器状态
docker compose ps

# 检查数据库
EVENT_COUNT=$(docker exec macro-postgres psql -U macro_user -d macro_dashboard -t -c "SELECT COUNT(*) FROM core.dim_events;" 2>/dev/null | tr -d ' ')
if [ "$EVENT_COUNT" -eq 7 ]; then
    echo "✓ 数据库初始化成功 ($EVENT_COUNT 个事件)"
else
    echo "✗ 数据库初始化失败"
    exit 1
fi

# 测试 API
if curl -s http://localhost:8020/api/v1/events > /dev/null; then
    echo "✓ API 运行正常"
else
    echo "✗ API 无法访问"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ 部署完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  前端: http://localhost:8021"
echo "  API:  http://localhost:8020"
echo "  文档: http://localhost:8020/api/v1/docs"
echo ""
```

---

## 总结

### 新服务器部署：
```bash
# 只需要这三步
docker compose pull
docker compose up -d
# 完成！
```

### 现有服务器升级：
```bash
# 需要额外的修复步骤
git pull
docker compose pull
bash fix-events-api.sh  # 如果数据库缺少 events 表
docker compose up -d
```

**关键区别**：新服务器的数据库是空的，会自动执行所有初始化脚本，无需手动干预。
