# FastAPI Backend

宏观经济仪表盘 API 服务

## 快速开始

### 本地开发

```bash
cd backend/api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GCP_PROJECT_ID=gen-lang-client-0815236933
export POSTGRES_PASSWORD=your_password
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问 API 文档

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API 端点

### Health Check

```bash
GET /api/v1/health
```

### 指标列表

```bash
GET /api/v1/indicators
```

### 时间序列数据

```bash
GET /api/v1/indicators/{indicator_code}/series?start_date=2024-01-01&end_date=2024-12-31&limit=1000
```

示例：
```bash
curl "http://localhost:8000/api/v1/indicators/US10Y/series?start_date=2024-01-01&limit=100"
```

### 仪表盘概览

```bash
GET /api/v1/dashboard/overview
```

## 架构

```
app/
├── api/v1/          # API 端点
│   ├── indicators.py
│   └── health.py
├── core/            # 核心配置
│   └── config.py
├── repositories/    # 数据访问层
│   └── bigquery_repo.py
├── schemas/         # Pydantic 模型
│   └── indicators.py
├── services/        # 业务服务
│   └── cache.py
└── main.py          # 应用入口
```

## 缓存策略

- **指标列表**: 24 小时
- **利率/汇率**: 5 分钟
- **大宗商品**: 10 分钟
- **通胀指标**: 6 小时

## Docker 部署

```bash
# 构建镜像
docker build -t macro-api .

# 运行容器
docker run -p 8000:8000 \
  -e GCP_PROJECT_ID=gen-lang-client-0815236933 \
  -e POSTGRES_PASSWORD=your_password \
  -v /path/to/key.json:/app/credentials/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  macro-api
```

## 测试

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 获取指标列表
curl http://localhost:8000/api/v1/indicators

# 获取 US10Y 数据
curl "http://localhost:8000/api/v1/indicators/US10Y/series?limit=10"

# 获取仪表盘概览
curl http://localhost:8000/api/v1/dashboard/overview
```

## 性能

- **缓存命中**: < 10ms
- **BigQuery 查询**: < 500ms
- **目标 P95**: < 500ms

## 监控

查看 API 日志：
```bash
docker logs -f macro-api
```

查看 Redis 状态：
```bash
redis-cli ping
redis-cli info stats
```
