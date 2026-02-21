# Macro Dashboard 实施计划

## 项目状态

**当前阶段**: ✅ MVP 完成 - 全栈应用已部署并运行

**已完成**:
- ✅ 项目结构创建
- ✅ PostgreSQL 数据模型设计（替代 BigQuery）
- ✅ 数据库初始化（14 个指标）
- ✅ 核心指标数据字典（14 个指标）
- ✅ Docker Compose 配置
- ✅ 环境配置模板
- ✅ FRED 数据采集（Cron Job 定时执行）
- ✅ FastAPI 后端完整实现
  - ✅ PostgreSQL Repository 层
  - ✅ Redis Cache 层
  - ✅ 核心 API 端点（indicators, series, dashboard/overview）
  - ✅ 健康检查端点
  - ✅ API 文档（Swagger UI）
  - ✅ CORS 配置
- ✅ React 前端完整实现
  - ✅ TypeScript + Vite
  - ✅ Recharts 数据可视化
  - ✅ API 客户端集成
  - ✅ Dashboard 页面
  - ✅ Nginx 反向代理配置
- ✅ Docker 镜像构建并推送到 DockerHub
- ✅ 本地部署测试通过
- ✅ 服务器部署测试通过
- ✅ 域名反向代理配置

## 当前架构

### 技术栈
- **数据采集**: Docker Cron Job + Python 3.11
- **数据存储**: PostgreSQL 16（core, mart, ops schemas）
- **API 层**: FastAPI + Uvicorn
- **缓存**: Redis 7
- **前端**: React 18 + TypeScript + Vite + Recharts
- **Web 服务器**: Nginx (反向代理 + SPA 路由)
- **容器化**: Docker + Docker Compose
- **镜像仓库**: DockerHub

### 部署架构
```
用户浏览器
    ↓
域名 (macro-dashboard.fuzhouxing.cn)
    ↓
1Panel Nginx (反向代理)
    ↓
Docker 网络 (macro-network)
    ├── Frontend (Nginx) :8021
    │   └── /api/* → API :8000
    ├── API (FastAPI) :8020
    │   ├── → PostgreSQL :5433
    │   └── → Redis :6380
    ├── Data Collector (Cron)
    │   └── → PostgreSQL :5433
    ├── PostgreSQL :5433
    └── Redis :6380
```

### 端口配置
| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| PostgreSQL | 5432 | 5433 | 避免本地冲突 |
| Redis | 6379 | 6380 | 避免本地冲突 |
| API | 8000 | 8020 | 后端 API |
| Frontend | 80 | 8021 | 前端界面 |

## 优化方向

### 第一阶段：核心分析功能 ⭐⭐⭐（2 周）- 🔄 进行中

详细计划见 [PHASE1_PLAN.md](./PHASE1_PLAN.md)

**功能列表**
1. 利率曲线图（3 天）
   - 美债收益率曲线（2Y/10Y）
   - 利差计算和形态识别
   - 历史曲线对比

2. 时间范围选择器（2 天）
   - 预设：1M/3M/6M/1Y/YTD/ALL
   - 自定义日期范围
   - 全局状态管理

3. 相关性分析（1 周）
   - 相关系数矩阵热力图
   - 滚动窗口（30/60/90 天）
   - 强相关识别

4. 历史回测功能（1 周）
   - 重大事件回放（2008/2020/2022）
   - 事件时间线
   - 指标变化分析

**技术准备**
- 后端：添加 numpy, pandas, scipy
- 前端：添加 date-fns
- 数据库：事件表设计



## 生产环境信息

### 部署地址
- **前端**: https://macro-dashboard.fuzhouxing.cn
- **API 文档**: http://your-server-ip:8020/api/v1/docs
- **健康检查**: http://your-server-ip:8020/api/v1/health

### 镜像仓库
- **API**: fuzhouxing/macro-dashboard-api:latest
- **Frontend**: fuzhouxing/macro-dashboard-frontend:latest
- **Collector**: fuzhouxing/macro-dashboard-collector:latest

### 数据采集
- **频率**: 每 6 小时（可配置）
- **数据源**: FRED API
- **指标数量**: 14 个核心指标
- **数据范围**: 最近 1 年

## 成本估算

### 当前成本（Azure 2核4G）
- **服务器**: ¥200-300/月
- **域名**: ¥50/年
- **总计**: ~¥250/月

### 优化后成本（添加监控）
- **服务器**: ¥200-300/月
- **域名**: ¥50/年
- **监控服务**: ¥0（自建 Prometheus）
- **总计**: ~¥250/月

## 参考文档

- [数据字典](data_dictionary.md)
- [README](../README.md)

## 更新日志

### 2026-02-21
- ✅ 完成 MVP 部署
- ✅ 本地和服务器环境测试通过
- ✅ 域名反向代理配置完成
- ✅ 文档更新完成
- 📝 制定优化计划
