# 部署前检查清单

在部署到生产环境之前，请确保完成以下检查项。

## ✅ 环境准备

### 服务器要求
- [ ] 服务器配置：2核4G 或更高
- [ ] 操作系统：Ubuntu 20.04+ / Debian 11+
- [ ] 磁盘空间：至少 20GB 可用
- [ ] 公网 IP 地址已配置
- [ ] SSH 访问已配置

### 软件安装
- [ ] Docker 已安装（`docker --version`）
- [ ] Docker Compose 已安装（`docker-compose --version`）
- [ ] Git 已安装（`git --version`）
- [ ] 当前用户已加入 docker 组（`groups | grep docker`）

## ✅ 配置文件

### 环境变量
- [ ] 已创建 `.env` 文件（从 `.env.example` 复制）
- [ ] `POSTGRES_PASSWORD` 已设置（使用强密码）
- [ ] `FRED_API_KEY` 已设置（从 https://fred.stlouisfed.org 获取）
- [ ] `CRON_SCHEDULE` 已配置（可选，默认每6小时）
- [ ] `FRONTEND_API_URL` 已配置（生产环境使用服务器 IP）

### 敏感信息保护
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 不包含任何 GCP 凭证文件（`*-key.json`）
- [ ] 不包含数据库备份文件（`*.sql`）
- [ ] 不包含迁移数据（`migration_data/`）

## ✅ 网络配置

### 防火墙规则
- [ ] 端口 80 已开放（HTTP）
- [ ] 端口 443 已开放（HTTPS，如果使用 SSL）
- [ ] 端口 22 已开放（SSH）
- [ ] 其他端口已关闭（5432, 6379, 8000 仅内部访问）

### DNS 配置（可选）
- [ ] 域名已指向服务器 IP
- [ ] DNS 记录已生效（`nslookup your-domain.com`）

## ✅ 数据迁移（如果从 GCP 迁移）

### BigQuery 数据导出
- [ ] GCP 凭证文件已准备
- [ ] 已运行 `export_from_bigquery.py`
- [ ] 导出的 CSV 文件已验证
- [ ] 数据已上传到服务器

### PostgreSQL 数据导入
- [ ] PostgreSQL 容器已启动
- [ ] 数据库 schema 已初始化
- [ ] 已运行 `import_to_postgres.py`
- [ ] 数据导入成功，无错误
- [ ] 数据完整性已验证

## ✅ 部署执行

### Docker 容器
- [ ] 所有镜像已构建（`docker-compose build`）
- [ ] 所有容器已启动（`docker-compose up -d`）
- [ ] 所有容器状态为 healthy（`docker-compose ps`）

### 服务健康检查
- [ ] PostgreSQL 可连接（`docker exec macro-postgres pg_isready`）
- [ ] Redis 可连接（`docker exec macro-redis redis-cli ping`）
- [ ] API 健康检查通过（`curl http://localhost:8000/api/v1/health`）
- [ ] 前端可访问（`curl http://localhost`）

### 数据验证
- [ ] API 返回指标列表（`curl http://localhost:8000/api/v1/indicators`）
- [ ] 仪表盘显示数据（`curl http://localhost:8000/api/v1/dashboard/overview`）
- [ ] 前端界面正常显示
- [ ] 数据采集任务已运行（检查 cron 日志）

## ✅ 安全加固

### 密码和密钥
- [ ] PostgreSQL 密码足够强（至少 16 字符，包含大小写字母、数字、特殊字符）
- [ ] FRED API Key 已妥善保管
- [ ] 不在代码中硬编码任何密码

### 访问控制
- [ ] SSH 密钥登录已配置
- [ ] 密码登录已禁用（可选）
- [ ] 防火墙规则已配置
- [ ] 不必要的端口已关闭

### 数据备份
- [ ] 数据库备份脚本已配置
- [ ] 备份存储位置已确定
- [ ] 备份恢复流程已测试

## ✅ 监控和日志

### 日志配置
- [ ] Docker 日志可访问（`docker-compose logs`）
- [ ] 日志轮转已配置（防止磁盘占满）
- [ ] 错误日志可查看

### 监控指标
- [ ] 容器资源使用可监控（`docker stats`）
- [ ] 磁盘空间可监控（`df -h`）
- [ ] 内存使用可监控（`free -h`）

## ✅ 性能优化（可选）

### 资源限制
- [ ] Docker 容器资源限制已配置
- [ ] PostgreSQL 内存配置已优化
- [ ] Redis 内存限制已设置

### 缓存策略
- [ ] Redis 缓存已启用
- [ ] 缓存 TTL 已配置
- [ ] 缓存命中率可监控

## ✅ 文档和维护

### 文档完整性
- [ ] README.md 已更新
- [ ] 部署文档已准备
- [ ] 故障排查指南已准备
- [ ] 联系方式已记录

### 维护计划
- [ ] 定期备份计划已制定
- [ ] 更新策略已确定
- [ ] 监控告警已配置（可选）

## ✅ 最终验证

### 功能测试
- [ ] 前端界面可正常访问
- [ ] 所有指标数据正常显示
- [ ] 数据更新时间正确
- [ ] 图表和可视化正常工作

### 性能测试
- [ ] API 响应时间 < 500ms
- [ ] 页面加载时间 < 3s
- [ ] 并发访问测试通过

### 用户验收
- [ ] 用户可正常访问
- [ ] 数据准确性已验证
- [ ] 用户反馈已收集

---

## 🎉 部署完成

所有检查项完成后，您的宏观经济仪表盘已成功部署！

### 下一步
1. 监控服务运行状态
2. 定期检查日志
3. 定期备份数据
4. 根据需要优化性能

### 获取帮助
- 查看文档：[Azure 部署指南](azure_deployment_guide.md)
- 故障排查：检查 Docker 日志
- 提交 Issue：GitHub Issues
