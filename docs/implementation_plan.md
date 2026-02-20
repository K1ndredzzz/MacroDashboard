# Macro Dashboard 实施计划

## 项目状态

**当前阶段**: Phase 2 完成 - 数据采集和 API 后端已全部部署到生产环境

**已完成**:
- ✅ 项目结构创建
- ✅ BigQuery 数据模型设计（6 张核心表 + DDL 脚本）
- ✅ BigQuery 初始化完成（14 个指标已入库）
- ✅ 核心指标数据字典（14 个指标）
- ✅ Docker Compose 配置
- ✅ 环境配置模板
- ✅ Cloud Functions 公共模块（HTTP 客户端、BigQuery 加载器）
- ✅ FRED 数据采集 Function（完整实现）
- ✅ FRED Function 部署到 GCP（Gen2, 512MB, 540s timeout）
- ✅ Cloud Scheduler 配置（每日 8:00 AM UTC 自动执行）
- ✅ Secret Manager 集成（FRED_API_KEY）
- ✅ FastAPI 后端完整实现
  - ✅ BigQuery Repository 层
  - ✅ Cache Service 层（Redis 可选）
  - ✅ 核心 API 端点（indicators, series, dashboard/overview）
  - ✅ 健康检查端点
  - ✅ API 文档（Swagger UI）
- ✅ 本地测试通过（所有端点验证成功）
- ✅ FastAPI 部署到 GCP Cloud Run
  - ✅ Docker 镜像构建并推送到 GCR
  - ✅ Cloud Run 服务配置（512Mi, 1 CPU, 300s timeout）
  - ✅ 生产环境测试通过

**进行中**:
- 🔄 React 前端开发（待启动）

**待完成**:
- ⏳ World Bank 数据采集 Function
- ⏳ React 前端初始化
- ⏳ 前端与后端集成

## 10-14 天实施路线图

### 阶段 1: 基础设施（Day 1-2）✅

**后端**:
- [x] 创建项目目录结构
- [x] BigQuery datasets 和表结构 DDL
- [x] 核心指标数据字典
- [x] 环境配置模板

**前端**:
- [ ] 初始化 React 项目（Vite + TypeScript）
- [ ] 安装依赖（echarts、antd、react-query）

### 阶段 2: 数据采集（Day 3-6）✅

**后端**:
- [x] 实现 Cloud Functions 公共模块
  - [x] HTTP 客户端（重试、退避）
  - [x] BigQuery 加载器
  - [x] 配置管理
- [x] 实现 FRED 采集 Function
  - [x] Extractor（API 调用）
  - [x] Transformer（数据标准化）
  - [x] Loader（写入 BigQuery）
  - [x] 主函数（HTTP 触发器）
- [x] 部署到 GCP Cloud Functions Gen2
  - [x] Secret Manager 集成
  - [x] 权限配置
  - [x] 环境变量设置
- [x] 配置 Cloud Scheduler（每日 8:00 AM UTC）
- [x] 生产环境测试（12/12 系列成功处理）
- [ ] 实现 World Bank 采集 Function

**前端**:
- [ ] 实现基础布局组件
- [ ] 开发图表组件骨架

### 阶段 3: API 与集成（Day 7-10）✅

**后端**:
- [x] FastAPI 项目初始化
- [x] 实现 Repository 层（BigQuery）
- [x] 实现 Cache 层（Redis 可选）
- [x] 核心 API 端点:
  - [x] GET /api/v1/health
  - [x] GET /api/v1/indicators
  - [x] GET /api/v1/indicators/{code}/series
  - [x] GET /api/v1/dashboard/overview
- [x] API 文档（Swagger UI）
- [x] 本地测试通过
- [x] 部署到 GCP Cloud Run
  - [x] Dockerfile 优化（非 root 用户）
  - [x] 构建并推送到 GCR
  - [x] Cloud Run 服务配置
  - [x] 生产环境验证

**前端**:
- [ ] API 客户端集成
- [ ] 实现自定义 Hooks（useIndicators、useSeries）
- [ ] Dashboard 页面组装

### 阶段 4: 部署与优化（Day 11-14）

**后端**:
- [ ] Docker Compose 集成测试
- [ ] 性能优化与压测
- [ ] 安全检查（输入校验、CORS、Secrets）
- [ ] 数据回填脚本

**前端**:
- [ ] 性能优化（useMemo、React.memo）
- [ ] 响应式适配
- [ ] 错误边界处理
- [ ] Docker 构建

### 短期目标（本周）

1. ✅ 完成 FRED 数据采集 Cloud Function
2. ✅ 部署第一个 Cloud Function 并测试
3. ✅ 配置 Cloud Scheduler 自动化
4. ✅ 完成 FastAPI 项目并本地测试
5. ✅ 部署 FastAPI 到 GCP Cloud Run
6. 🔄 初始化 React 项目结构

### 中期目标（2 周内）

1. ✅ 完成 FRED 数据采集管道
2. ✅ 完成核心 API 端点
3. ✅ API 后端部署到生产环境
4. 🔄 完成基础仪表盘前端
5. 🔄 Docker Compose 一键部署
6. ⏳ 完成 World Bank 数据采集管道

## 验收标准

### MVP 完成定义（DoD）

1. ✅ FRED 自动采集稳定运行（已部署 Cloud Scheduler）
2. ✅ BigQuery 数据完整，支持按指标/日期查询
3. ✅ API 端点完整实现并通过测试
4. ⏳ 前端展示至少 3 类核心指标图表
5. ⏳ Docker Compose 可一键启动并通过健康检查
6. ⏳ API 在缓存命中场景 P95 < 500ms（待压测）
7. ✅ 任务日志与数据质量日志可用于故障定位

## 技术债务与优化

### 已知限制
- GOLDAMGBD228NLBM（黄金价格）因 LBMA 版权限制已从 FRED 采集中移除
- PostgreSQL 热数据层暂未实现（使用 BigQuery 直接查询）
- Redis 缓存为可选配置（默认关闭）
- World Bank 数据采集待实现

### 当前技术栈
- **数据采集**: GCP Cloud Functions Gen2 + Python 3.11
- **数据存储**: BigQuery（macro_raw, macro_core, macro_mart, macro_ops）
- **API 层**: FastAPI + Uvicorn（部署在 Cloud Run）
- **缓存**: Redis（可选）
- **认证**: Secret Manager
- **调度**: Cloud Scheduler
- **容器**: Docker + GCR
- **前端**: React + TypeScript（待实现）

### 生产环境 URL
- **FRED 数据采集**: https://us-central1-gen-lang-client-0815236933.cloudfunctions.net/ingest-fred
- **API 服务**: https://macro-dashboard-api-771720899914.us-central1.run.app
- **API 文档**: https://macro-dashboard-api-771720899914.us-central1.run.app/api/v1/docs

### 后续优化方向
1. 引入 PostgreSQL 热数据层（Phase 2B）
2. 实现事件冲击实验室（Phase 4）
3. 集成 n8n 自动化运维（Phase 5）
4. 添加更多数据源（IMF、ECB、Yahoo Finance）
5. 实现用户认证和权限管理
6. 实现 World Bank 数据采集
7. 启用 Redis 缓存优化性能

## 参考文档

- [后端架构设计](docs/backend_architecture_phase1_2A.md) - Codex 生成
- [数据字典](docs/data_dictionary.md)
- [项目规划](项目规划.md)
- [背景说明](background.md)
