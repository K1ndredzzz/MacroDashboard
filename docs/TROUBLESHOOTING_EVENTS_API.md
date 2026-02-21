# 服务器端 Events API 故障排查指南

## 问题：服务器上显示 "Failed to fetch events"

### 步骤 1: 检查数据库是否有 events 表和数据

```bash
# SSH 到服务器后执行
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT COUNT(*) FROM core.dim_events;"
```

**预期结果**: 应该返回 7 条记录

**如果表不存在或没有数据**，执行：
```bash
docker exec -i macro-postgres psql -U macro_user -d macro_dashboard < backend/scripts/postgres/02_events.sql
```

---

### 步骤 2: 检查 API 镜像版本

```bash
# 检查当前运行的镜像
docker ps --filter "name=macro-api" --format "{{.Image}}"

# 检查镜像创建时间
docker images fuzhouxing/macro-dashboard-api:latest --format "{{.CreatedAt}}"
```

**预期结果**:
- 镜像应该是 `fuzhouxing/macro-dashboard-api:latest` 或 `v2.0.1`
- 创建时间应该是 2026-02-21 或更新

**如果镜像是旧版本**，执行：
```bash
docker pull fuzhouxing/macro-dashboard-api:v2.0.1
docker compose down api
docker compose up -d api
```

---

### 步骤 3: 测试 API 端点

```bash
# 直接测试 API 容器
curl http://localhost:8020/api/v1/events

# 通过前端 nginx 测试
curl http://localhost:8021/api/v1/events
```

**预期结果**: 两个请求都应该返回 JSON 格式的事件列表

**如果返回 404**:
- 检查 API 容器日志: `docker logs macro-api --tail 50`
- 检查路由是否注册: `docker exec macro-api grep -r "events" app/main.py`

**如果返回 500**:
- 查看详细错误: `docker logs macro-api --tail 100`
- 可能是数据库连接问题

---

### 步骤 4: 检查前端 nginx 配置

```bash
# 检查 nginx 配置
docker exec macro-frontend cat /etc/nginx/conf.d/default.conf | grep -A 10 "location /api"
```

**预期结果**: 应该看到 `proxy_pass http://api:8000;`

**如果配置不正确**，需要重新构建前端镜像。

---

### 步骤 5: 检查网络连接

```bash
# 检查容器间网络
docker exec macro-frontend ping -c 2 api

# 检查 API 容器是否可访问
docker exec macro-frontend curl -s http://api:8000/api/v1/health
```

**预期结果**: ping 应该成功，health 检查应该返回 OK

---

### 步骤 6: 查看浏览器控制台错误

在浏览器中打开开发者工具（F12），查看 Console 和 Network 标签：

**Network 标签**:
- 找到 `/api/v1/events` 请求
- 查看状态码（应该是 200）
- 查看响应内容

**Console 标签**:
- 查看是否有 CORS 错误
- 查看是否有网络错误

---

## 常见问题和解决方案

### 问题 1: 数据库表不存在
**症状**: API 返回 500 错误，日志显示 "relation core.dim_events does not exist"

**解决**:
```bash
docker exec -i macro-postgres psql -U macro_user -d macro_dashboard < backend/scripts/postgres/02_events.sql
```

---

### 问题 2: API 镜像是旧版本
**症状**: API 返回 404，路由未注册

**解决**:
```bash
docker pull fuzhouxing/macro-dashboard-api:v2.0.1
docker compose down api
docker compose up -d api
```

---

### 问题 3: CORS 错误
**症状**: 浏览器控制台显示 CORS 错误

**解决**: 检查 API 的 CORS 配置，确保允许前端域名

---

### 问题 4: 网络连接问题
**症状**: 前端无法连接到 API

**解决**:
```bash
# 重启所有容器
docker compose down
docker compose up -d
```

---

## 快速修复脚本

将以下内容保存为 `fix-events-api.sh` 并在服务器上执行：

```bash
#!/bin/bash
echo "修复 Events API..."

# 1. 拉取最新镜像
echo "1. 拉取最新 API 镜像..."
docker pull fuzhouxing/macro-dashboard-api:v2.0.1

# 2. 重启 API 容器
echo "2. 重启 API 容器..."
docker compose down api
docker compose up -d api

# 3. 等待容器启动
echo "3. 等待容器启动..."
sleep 10

# 4. 初始化 events 表（如果不存在）
echo "4. 初始化 events 表..."
docker exec -i macro-postgres psql -U macro_user -d macro_dashboard < backend/scripts/postgres/02_events.sql 2>/dev/null || echo "表已存在"

# 5. 测试 API
echo "5. 测试 API..."
curl -s http://localhost:8020/api/v1/events | python -m json.tool | head -20

echo ""
echo "修复完成！请刷新浏览器测试。"
```

---

## 验证修复

执行以下命令验证修复是否成功：

```bash
# 1. 检查数据库
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT event_name FROM core.dim_events LIMIT 3;"

# 2. 测试 API
curl http://localhost:8020/api/v1/events | python -m json.tool

# 3. 测试前端访问
curl http://localhost:8021/api/v1/events | python -m json.tool

# 4. 查看 API 日志
docker logs macro-api --tail 20
```

所有测试都应该成功返回数据。

---

## 联系支持

如果以上步骤都无法解决问题，请提供以下信息：

1. `docker ps` 的输出
2. `docker logs macro-api --tail 50` 的输出
3. `docker logs macro-postgres --tail 50` 的输出
4. 浏览器控制台的错误截图
5. Network 标签中 `/api/v1/events` 请求的详细信息
