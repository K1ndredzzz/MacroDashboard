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

### 1. 性能优化 ⭐⭐⭐

**数据库优化**
- [ ] 添加数据库连接池监控
- [ ] 实现查询结果缓存策略
- [ ] 优化慢查询（添加复合索引）
- [ ] 实现数据分区（按年份）

**API 优化**
- [ ] 实现 API 响应压缩（Gzip）
- [ ] 添加 ETag 支持
- [ ] 实现 GraphQL 端点（可选）
- [ ] API 限流（Rate Limiting）

**前端优化**
- [ ] 实现代码分割（Code Splitting）
- [ ] 添加 Service Worker（PWA）
- [ ] 图表懒加载
- [ ] 实现虚拟滚动（大数据集）

### 2. 监控与告警 ⭐⭐⭐

**应用监控**
- [ ] 集成 Prometheus + Grafana
  - API 响应时间
  - 数据库连接数
  - Redis 命中率
  - 容器资源使用
- [ ] 实现健康检查仪表板
- [ ] 添加日志聚合（ELK Stack 或 Loki）

**数据质量监控**
- [ ] 数据采集成功率监控
- [ ] 数据完整性检查
- [ ] 异常值检测
- [ ] 数据延迟告警

**告警通知**
- [ ] 集成 Webhook 通知（企业微信/钉钉/Slack）
- [ ] 数据采集失败告警
- [ ] API 服务异常告警
- [ ] 磁盘空间告警

### 3. 安全加固 ⭐⭐

**认证与授权**
- [ ] 实现 JWT 认证
- [ ] API Key 管理
- [ ] 用户角色权限（RBAC）
- [ ] OAuth2 集成（可选）

**安全配置**
- [ ] 启用 HTTPS（Let's Encrypt）
- [ ] 实现 API 限流
- [ ] SQL 注入防护审计
- [ ] 敏感数据加密

**备份策略**
- [ ] 自动化数据库备份（每日）
- [ ] 备份文件加密
- [ ] 异地备份
- [ ] 备份恢复测试

### 4. 功能扩展 ⭐⭐

**数据源扩展**
- [ ] World Bank 数据采集
- [ ] IMF 数据集成
- [ ] Yahoo Finance 股票数据
- [ ] 加密货币数据（CoinGecko）

**可视化增强**
- [ ] 添加更多图表类型（热力图、散点图）
- [ ] 实现自定义仪表板
- [ ] 数据导出功能（CSV/Excel）
- [ ] 图表分享功能

**分析功能**
- [ ] 相关性分析
- [ ] 趋势预测（简单移动平均）
- [ ] 事件标注（重要经济事件）
- [ ] 指标对比功能

### 5. 运维自动化 ⭐

**CI/CD**
- [ ] GitHub Actions 自动构建
- [ ] 自动化测试（单元测试 + 集成测试）
- [ ] 自动部署到服务器
- [ ] 镜像版本管理

**容器编排**
- [ ] 迁移到 Kubernetes（可选）
- [ ] 实现滚动更新
- [ ] 自动扩缩容
- [ ] 健康检查与自愈

**文档完善**
- [ ] API 文档完善（示例代码）
- [ ] 架构图更新
- [ ] 运维手册
- [ ] 故障排查手册

### 6. 用户体验 ⭐

**界面优化**
- [ ] 深色模式
- [ ] 多语言支持（中英文）
- [ ] 响应式设计优化
- [ ] 加载动画优化

**交互优化**
- [ ] 实现数据筛选器
- [ ] 时间范围选择器
- [ ] 图表交互增强（缩放、拖拽）
- [ ] 键盘快捷键

**移动端**
- [ ] 移动端适配
- [ ] 触摸手势支持
- [ ] 移动端专属布局

## 优先级建议

### 高优先级（1-2 周）⭐⭐⭐
1. **监控与告警**：确保生产环境稳定性
2. **HTTPS 配置**：安全基础
3. **自动化备份**：数据安全
4. **性能监控**：了解系统瓶颈

### 中优先级（1 个月）⭐⭐
1. **API 限流**：防止滥用
2. **数据库优化**：提升查询性能
3. **前端优化**：提升用户体验
4. **CI/CD**：提升开发效率

### 低优先级（长期）⭐
1. **新数据源**：扩展数据覆盖
2. **高级分析功能**：增强分析能力
3. **Kubernetes 迁移**：大规模部署
4. **移动端应用**：扩展用户群

## 技术债务

### 已知限制
- ~~GOLDAMGBD228NLBM（黄金价格）因 LBMA 版权限制已从 FRED 采集中移除~~ ✅ 已解决
- 缺少监控和告警系统
- 未实现用户认证
- 未启用 HTTPS
- 缺少自动化测试

### 待优化项
- 数据库查询性能（添加更多索引）
- API 响应时间（P95 目标 < 500ms）
- 前端首屏加载时间（目标 < 2s）
- 容器镜像大小（前端 ~50MB，可优化）

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

- [部署和维护指南](DEPLOYMENT.md)
- [故障排查指南](TROUBLESHOOTING.md)
- [数据字典](data_dictionary.md)
- [README](../README.md)

## 更新日志

### 2026-02-21
- ✅ 完成 MVP 部署
- ✅ 本地和服务器环境测试通过
- ✅ 域名反向代理配置完成
- ✅ 文档更新完成
- 📝 制定优化计划
