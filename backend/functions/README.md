# Cloud Functions 部署指南

## FRED 数据采集 Function

### 本地测试

```bash
cd backend/functions

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GCP_PROJECT_ID=gen-lang-client-0815236933
export FRED_API_KEY=c0845942ca2c8dffa02e4e51edc10d7f
export GOOGLE_APPLICATION_CREDENTIALS="D:\Code_new\MacroDashboard\credentials\gen-lang-client-0815236933-340089633139.json"

# 本地运行
functions-framework --target=ingest_fred_http --source=fred/main.py --debug
```

### 测试请求

```bash
# 默认获取最近 7 天数据
curl http://localhost:8080

# 指定回溯天数
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"lookback_days": 30}'
```

### 部署到 GCP

```bash
# 部署 FRED 采集函数
gcloud functions deploy ingest-fred \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=ingest_fred_http \
  --trigger-http \
  --allow-unauthenticated=false \
  --set-env-vars GCP_PROJECT_ID=gen-lang-client-0815236933,FRED_API_KEY=your_key \
  --service-account=macro-dashboard-sa@gen-lang-client-0815236933.iam.gserviceaccount.com \
  --memory=512MB \
  --timeout=540s
```

### 配置 Cloud Scheduler

```bash
# 创建每小时触发的调度任务
gcloud scheduler jobs create http fred-hourly-ingest \
  --location=us-central1 \
  --schedule="0 * * * *" \
  --uri="https://us-central1-gen-lang-client-0815236933.cloudfunctions.net/ingest-fred" \
  --http-method=POST \
  --oidc-service-account-email=macro-dashboard-sa@gen-lang-client-0815236933.iam.gserviceaccount.com \
  --message-body='{"lookback_days": 7}'
```

## 架构说明

### 数据流

```
Cloud Scheduler (每小时)
  ↓
Cloud Function: ingest_fred_http
  ↓
1. Extract: 调用 FRED API 获取数据
  ↓
2. Transform: 标准化数据格式
  ↓
3. Load: 写入 BigQuery
  - macro_raw.api_payload (原始响应)
  - macro_core.fact_observation (标准化数据)
  - macro_ops.etl_run_log (运行日志)
```

### 错误处理

- **可重试错误** (429, 5xx)：自动重试 3 次，指数退避
- **不可重试错误** (4xx)：记录错误并继续处理其他序列
- **部分成功**：单个序列失败不影响其他序列，状态标记为 `partial`

### 幂等性

- 使用 `run_id` 标识每次运行
- 使用 `row_hash` 检测数据变更
- MERGE 操作避免重复插入

## 监控

### 查看运行日志

```sql
SELECT
  run_id,
  started_at,
  ended_at,
  status,
  fetched_count,
  inserted_count,
  error_count
FROM `gen-lang-client-0815236933.macro_ops.etl_run_log`
WHERE pipeline = 'ingest_fred'
ORDER BY started_at DESC
LIMIT 10;
```

### 查看最新数据

```sql
SELECT
  indicator_code,
  MAX(observation_date) as latest_date,
  COUNT(*) as total_observations
FROM `gen-lang-client-0815236933.macro_core.fact_observation`
WHERE source = 'fred'
GROUP BY indicator_code
ORDER BY indicator_code;
```

## 故障排查

### Function 超时
- 增加 `--timeout` 参数（最大 540s）
- 减少 `lookback_days` 参数

### API 限流
- FRED API 限制：1000 请求/天
- 调整 Cloud Scheduler 频率

### BigQuery 配额
- 检查每日查询配额
- 优化 MERGE 查询

## 成本估算

### Cloud Functions
- 调用次数：24 次/天（每小时）
- 执行时间：~30 秒/次
- 内存：512MB
- **月成本**：~$0.50

### BigQuery
- 存储：~1GB/年
- 查询：~10GB/月
- **月成本**：~$0.50

### 总计
- **月成本**：~$1.00
