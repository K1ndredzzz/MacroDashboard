# 部署问题快速修复

## 问题 0: Docker 构建失败 - ingest_fred 目录不存在

### 错误信息
```
ERROR: failed to compute cache key: "/ingest_fred": not found
```

### 原因
项目目录结构中实际是 `fred` 而不是 `ingest_fred`。

### 解决方案
已修复！最新代码使用正确的目录结构：
- `backend/functions/fred/` - FRED 数据提取和转换
- `backend/functions/collect_data.py` - PostgreSQL 数据采集脚本
- `backend/functions/common/` - 共享代码

如果遇到此问题，请拉取最新代码：
```bash
git pull origin main
```

## 问题 1: .env 文件 cron 表达式错误

### 错误信息
```
.env: line 39: */6: No such file or directory
```

### 原因
Cron 表达式中的 `*` 被 bash 解析为通配符。

### 解决方案

编辑 `.env` 文件，给 cron 表达式加引号：

```bash
# 错误写法
CRON_SCHEDULE=0 */6 * * *

# 正确写法
CRON_SCHEDULE="0 */6 * * *"
```

或者直接使用 `.env.example` 模板（已修复）：
```bash
cp .env.example .env
nano .env  # 填入密码和 API key
```

## 问题 1: deploy.sh 权限被拒绝

### 错误信息
```
-bash: ./deploy.sh: Permission denied
```

### 解决方案

```bash
# 方法 1: 添加执行权限
chmod +x deploy.sh
./deploy.sh

# 方法 2: 直接用 bash 执行
bash deploy.sh

# 方法 3: 手动部署（不使用脚本）
cp .env.example .env
nano .env  # 填入配置
docker-compose up -d
```

## 问题 2: 端口 8000 被占用

### 错误信息
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

### 解决方案

#### 方法 1: 使用其他端口（推荐）

编辑 `.env` 文件，添加：
```bash
API_PORT=8888  # 或其他未被占用的端口
```

然后重新部署：
```bash
docker-compose down
docker-compose up -d
```

#### 方法 2: 停止占用 8000 端口的服务

```bash
# 查看占用 8000 端口的进程
sudo lsof -i :8000
# 或
sudo netstat -tulpn | grep :8000

# 停止该进程（替换 PID）
sudo kill -9 <PID>
```

#### 方法 3: 修改 docker-compose.yml

如果不想使用环境变量，直接修改 `docker-compose.yml`：

```yaml
api:
  ports:
    - "8888:8000"  # 改为其他端口
```

## 问题 3: 1Panel 环境下的部署

如果您使用 1Panel 管理 Docker，建议：

### 方法 1: 通过 1Panel Web 界面部署

1. 登录 1Panel 管理界面
2. 进入"容器" → "编排"
3. 创建新的编排项目
4. 粘贴 `docker-compose.yml` 内容
5. 配置环境变量
6. 启动服务

### 方法 2: 命令行部署

```bash
# 确保在项目目录
cd /opt/1panel/docker/compose/MacroDashboard

# 添加执行权限
chmod +x deploy.sh

# 创建 .env 文件
cp .env.example .env
nano .env

# 填入以下配置：
# POSTGRES_PASSWORD=your_password
# FRED_API_KEY=your_fred_key
# API_PORT=8888

# 部署
bash deploy.sh
```

## 问题 4: Git 克隆后文件权限问题

### 解决方案

```bash
# 批量添加执行权限
find . -name "*.sh" -exec chmod +x {} \;

# 或单独添加
chmod +x deploy.sh
chmod +x backend/functions/docker/cron-entrypoint.sh
```

## 问题 5: 前端无法连接 API

### 检查步骤

1. 确认 API 端口配置正确：
```bash
# 查看 .env 文件
cat .env | grep API_PORT

# 查看 API 是否运行
docker-compose ps api
curl http://localhost:8888/api/v1/health
```

2. 更新前端环境变量：
```bash
# 编辑 frontend/.env.local
echo "VITE_API_BASE_URL=http://localhost:8888" > frontend/.env.local
```

3. 重新构建前端：
```bash
docker-compose build frontend
docker-compose up -d frontend
```

## 完整部署流程（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/K1ndredzzz/MacroDashboard.git
cd MacroDashboard

# 2. 添加执行权限
chmod +x deploy.sh

# 3. 创建配置文件
cp .env.example .env

# 4. 编辑配置（必填项）
nano .env
# 填入：
# POSTGRES_PASSWORD=your_secure_password
# FRED_API_KEY=your_fred_api_key
# API_PORT=8888

# 5. 部署
bash deploy.sh

# 6. 查看日志
docker-compose logs -f

# 7. 访问应用
# 前端: http://your-server-ip
# API: http://your-server-ip:8888/api/v1/docs
```

## 常见端口占用情况

| 端口 | 常见占用服务 | 建议替代端口 |
|------|-------------|-------------|
| 8000 | Django, FastAPI | 8888, 8080, 9000 |
| 80 | Nginx, Apache | 8080, 3000 |
| 5432 | PostgreSQL | 5433, 15432 |
| 6379 | Redis | 6380, 16379 |

## 获取帮助

如果问题仍未解决：

1. 查看完整日志：`docker-compose logs -f`
2. 检查端口占用：`sudo netstat -tulpn`
3. 查看容器状态：`docker-compose ps`
4. 提交 Issue：https://github.com/K1ndredzzz/MacroDashboard/issues
