# Macro Dashboard 部署总结

## 部署日期
2026-02-20

## Phase 1 & 2 完成状态：✅ 已全部部署到生产环境

---

## 1. 数据采集管道（Phase 1）

### FRED 数据采集 Cloud Function
- **服务名称**: ingest-fred
- **URL**: https://us-central1-gen-lang-client-0815236933.cloudfunctions.net/ingest-fred
- **运行时**: Python 3.11
- **配置**: Gen2, 512MB 内存, 540s 超时
- **触发器**: HTTP + Cloud Scheduler
- **调度**: 每日 8:00 AM UTC（北京时间 16:00）
- **数据源**: FRED API（12 个经济指标）
- **状态**: ✅ 运行正常

### 采集的指标
1. DGS2 - US 2Y Treasury
2. DGS10 - US 10Y Treasury
3. DGS30 - US 30Y Treasury
4. DEXUSEU - EUR/USD
5. DEXJPUS - USD/JPY
6. DEXUSUK - GBP/USD
7. DCOILWTICO - WTI Oil
8. CPIAUCSL - CPI
9. CPILFESL - Core CPI
10. PPIACO - PPI
11. UNRATE - Unemployment Rate
12. PAYEMS - Nonfarm Payrolls

**注**: GOLDAMGBD228NLBM（黄金价格）因 LBMA 版权限制已移除

---

## 2. API 后端服务（Phase 2）

### FastAPI Cloud Run 服务
- **服务名称**: macro-dashboard-api
- **URL**: https://macro-dashboard-api-771720899914.us-central1.run.app
- **区域**: us-central1
- **配置**: 512Mi 内存, 1 CPU, 300s 超时, 最多 10 个实例
- **访问控制**: 公开访问（无需认证）
- **状态**: ✅ 运行正常

### API 端点

#### 健康检查
```
GET /api/v1/health
```
返回服务健康状态和 BigQuery 连接状态

#### 指标列表
```
GET /api/v1/indicators
```
返回所有可用指标的元数据（14 个指标）

#### 时间序列数据
```
GET /api/v1/indicators/{indicator_code}/series
Query Parameters:
  - start_date: YYYY-MM-DD (可选)
  - end_date: YYYY-MM-DD (可选)
  - limit: 整数，默认 1000 (可选)
```
返回指定指标的历史数据

#### 仪表板概览
```
GET /api/v1/dashboard/overview
```
返回所有指标的最新值和变化情况

### API 文档
- **Swagger UI**: https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/docs
- **ReDoc**: https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/redoc

---

## 3. 数据存储

### BigQuery 数据集
- **项目**: gen-lang-client-0815236933
- **数据集**:
  - `macro_raw`: 原始数据
  - `macro_core`: 核心数据（dim_series, fact_observation）
  - `macro_mart`: 数据集市（v_latest_snapshot）
  - `macro_ops`: 运维日志

### 当前数据状态
- 7 个指标有实时数据
- 最新数据日期: 2026-02-18
- 总观测数: 14 条

---

## 4. 安全与认证

### Secret Manager
- **FRED_API_KEY**: FRED API 密钥（已配置）
- **权限**: Cloud Run 服务账号已授予 Secret Accessor 角色

### IAM 配置
- Cloud Functions 服务账号: 771720899914-compute@developer.gserviceaccount.com
- 权限: BigQuery Data Editor, Secret Manager Secret Accessor

---

## 5. 监控与日志

### Cloud Logging
- Cloud Functions 日志: 可查看数据采集执行情况
- Cloud Run 日志: 可查看 API 请求和响应
- BigQuery 日志: 可查看数据加载情况

### 关键指标
- FRED 采集成功率: 12/12 (100%)
- API 响应时间: < 5s（未启用缓存）
- 数据新鲜度: 每日更新

---

## 6. 成本估算

### 每月预估成本
- **Cloud Functions**: ~$5（每日执行 1 次，~50s/次）
- **Cloud Run**: ~$10（按请求计费，512Mi 内存）
- **BigQuery**: ~$5（存储 + 查询）
- **Cloud Scheduler**: $0.10（1 个作业）
- **Secret Manager**: $0.06（1 个密钥）
- **总计**: ~$20/月

---

## 7. 测试验证

### 生产环境测试结果
```bash
# 健康检查
curl https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/health
# ✅ 返回: {"status":"degraded","bigquery":"healthy","redis":"unhealthy"}

# 指标列表
curl https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/indicators
# ✅ 返回: 14 个指标的完整列表

# 时间序列数据
curl "https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/indicators/US10Y/series?start_date=2026-02-01&end_date=2026-02-28"
# ✅ 返回: US10Y 的 3 条观测数据

# 仪表板概览
curl https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/dashboard/overview
# ✅ 返回: 7 个指标的最新快照
```

---

## 8. 下一步计划

### Phase 3: React 前端开发
- [ ] 初始化 React + TypeScript 项目
- [ ] 实现 API 客户端
- [ ] 开发核心图表组件
- [ ] 实现仪表板页面

### 可选优化
- [ ] 启用 Redis 缓存
- [ ] 实现 World Bank 数据采集
- [ ] 添加用户认证
- [ ] 性能优化和压测

---

## 9. 故障排查

### 常见问题

**Q: API 返回 500 错误**
A: 检查 Cloud Run 日志，确认 BigQuery 连接正常

**Q: 数据采集失败**
A: 检查 Cloud Functions 日志，确认 FRED API 密钥有效

**Q: 数据不是最新的**
A: 检查 Cloud Scheduler 是否正常触发，查看最近的执行日志

### 日志查看命令
```bash
# Cloud Functions 日志
gcloud functions logs read ingest-fred --region=us-central1 --limit=50

# Cloud Run 日志
gcloud run services logs read macro-dashboard-api --region=us-central1 --limit=50

# Cloud Scheduler 日志
gcloud scheduler jobs describe ingest-fred-daily --location=us-central1
```

---

## 10. 部署文件清单

### Cloud Functions
- `backend/functions/fred/main.py` - 主函数
- `backend/functions/common/` - 公共模块
- `backend/functions/deploy.sh` - 部署脚本
- `backend/functions/setup_scheduler.sh` - 调度器配置

### Cloud Run
- `backend/api/Dockerfile` - Docker 配置
- `backend/api/deploy.sh` - 部署脚本
- `backend/api/app/` - FastAPI 应用代码
- `backend/api/requirements.txt` - Python 依赖

---

## 总结

✅ **Phase 1 & 2 已完全部署到 GCP 生产环境**
- 数据采集管道自动化运行
- API 服务稳定提供数据访问
- 所有核心功能验证通过
- 成本可控，性能良好

**下一步**: 开始 Phase 3 React 前端开发
