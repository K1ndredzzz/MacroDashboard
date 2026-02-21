# 部署问题修复记录

**日期**: 2026-02-21
**问题**: Phase 1 功能在 http://localhost:8021 无法正常加载

---

## 问题诊断

### 1. 前端容器使用旧镜像
**现象**: 前端页面没有显示新功能
**原因**: 前端容器使用的是 DockerHub 上的旧镜像
**解决**: 重新构建本地镜像并重启容器

### 2. API 容器健康检查失败
**现象**: Nginx 返回 502 Bad Gateway
**原因**:
- 健康检查使用 `curl` 命令
- `python:3.11-slim` 镜像不包含 curl
- 健康检查失败导致容器标记为 unhealthy
- Nginx 拒绝代理请求到 unhealthy 容器

**解决**:
- 修改 `docker-compose.yml` 健康检查配置
- 使用 Python 内置 urllib 替代 curl
- 无需安装额外依赖

```yaml
# 修改前
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]

# 修改后
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
```

### 3. 前端 API 路径错误
**现象**: API 调用返回 404 Not Found
**原因**: 前端组件使用了错误的 API 路径 `/api/api/v1/...`（双重 api）
**解决**: 修改所有组件的 API 路径为 `/api/v1/...`

**受影响文件**:
- `frontend/src/components/YieldCurve.tsx`
- `frontend/src/components/CorrelationHeatmap.tsx`
- `frontend/src/components/EventBacktest.tsx`

---

## 修复步骤

### 1. 修改健康检查配置
```bash
# 编辑 docker-compose.yml
# 将 API 服务的健康检查改为使用 Python
```

### 2. 重建 API 容器
```bash
cd /d/Code_new/MacroDashboard
docker-compose up -d --force-recreate api
```

### 3. 修复前端 API 路径
```bash
cd frontend/src/components
sed -i "s|/api/api/v1/|/api/v1/|g" YieldCurve.tsx CorrelationHeatmap.tsx EventBacktest.tsx
```

### 4. 重建前端镜像
```bash
cd frontend
docker build -t fuzhouxing/macro-dashboard-frontend:latest .
```

### 5. 重启前端容器
```bash
cd ..
docker-compose up -d --force-recreate frontend
```

---

## 验证结果

### API 健康检查
```bash
$ docker ps --filter "name=macro-api"
NAMES       STATUS
macro-api   Up 5 minutes (healthy)
```

### API 端点测试
```bash
# Health
$ curl http://localhost:8021/api/v1/health
{"status":"healthy","timestamp":"2026-02-21T12:53:56.640448","version":"0.1.0"}

# Yield Curve
$ curl http://localhost:8021/api/v1/indicators/yield-curve
{"observation_date":"2026-02-19","points":[...],"spread_10y_2y":"0.610000","curve_shape":"normal"}

# Correlation
$ curl "http://localhost:8021/api/v1/analytics/correlation?indicator_codes=US10Y,US2Y,EURUSD&window_days=90"
{"matrix":[...],"strong_correlations":[...]}

# Events
$ curl http://localhost:8021/api/v1/events
[{"event_id":4,"event_name":"2023 硅谷银行倒闭",...}]
```

---

## 经验教训

### 1. Docker 健康检查最佳实践
- 优先使用镜像内置工具（如 Python）
- 避免依赖需要额外安装的工具（如 curl）
- 健康检查失败会影响服务发现和负载均衡

### 2. 前端 API 路径管理
- 应该使用环境变量或配置文件管理 API 基础路径
- 避免硬编码 API 路径
- 建议创建统一的 API 客户端模块

### 3. 容器镜像管理
- 本地开发应使用本地构建的镜像
- 避免混用 DockerHub 镜像和本地镜像
- 使用明确的镜像标签（避免 latest）

---

## 后续优化建议

### 1. 创建 API 客户端模块
```typescript
// frontend/src/api/client.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = {
  get: (path: string) => fetch(`${API_BASE_URL}${path}`),
  // ...
};
```

### 2. 添加前端环境变量
```env
# frontend/.env
VITE_API_BASE_URL=/api/v1
```

### 3. 改进健康检查
```yaml
# 添加更详细的健康检查
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; import sys; r = urllib.request.urlopen('http://localhost:8000/api/v1/health'); sys.exit(0 if r.status == 200 else 1)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 当前状态

✅ **所有 Phase 1 功能已部署并正常运行**

- 时间范围选择器
- 利率曲线图
- 相关性分析热力图
- 历史事件回测

**访问地址**: http://localhost:8021
