# 服务器数据库初始化问题修复指南

## 问题描述

服务器上的 PostgreSQL 数据库表未初始化，collector 报错：
```
psycopg2.errors.UndefinedTable: relation "core.fact_observations" does not exist
```

## 快速修复

### 步骤 1: 上传修复脚本到服务器

将以下文件上传到服务器的项目目录：
- `server_fix_db.sh` - 数据库初始化修复脚本
- `diagnose_db.sh` - 诊断脚本

```bash
# 在服务器上
cd /opt/1panel/docker/compose/MacroDashboard

# 添加执行权限
chmod +x server_fix_db.sh diagnose_db.sh
```

### 步骤 2: 运行诊断

```bash
bash diagnose_db.sh
```

检查输出，确认：
- ✓ 容器正常运行
- ✓ 初始化脚本已挂载到 `/docker-entrypoint-initdb.d/`
- ✗ 数据库中没有 `core` schema 和表（这是问题所在）

### 步骤 3: 执行修复

```bash
bash server_fix_db.sh
```

脚本会提供两个方案：

**方案 1：完全重建（推荐）**
- 删除现有数据卷
- 重新创建容器
- 自动执行初始化脚本
- ⚠️ 会删除所有现有数据

**方案 2：手动执行 SQL**
- 在现有数据库中执行初始化脚本
- 不删除现有数据
- 适合已有部分数据的情况

### 步骤 4: 验证

```bash
# 检查表是否创建
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "\dt core.*"

# 检查初始数据
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "SELECT COUNT(*) FROM core.dim_series;"

# 查看 collector 日志
docker-compose logs -f data-collector
```

预期结果：
- `core.dim_series` 表有 14 条记录
- `core.fact_observations` 表存在
- collector 开始成功采集数据

## 常见问题

### Q1: 为什么本地可以，服务器不行？

**A:** 可能的原因：
1. 服务器上的数据卷已存在，PostgreSQL 跳过了初始化
2. 初始化脚本路径不正确
3. 容器启动顺序问题

### Q2: 方案 1 和方案 2 有什么区别？

**A:**
- **方案 1**：完全重建，确保干净的初始化环境（推荐）
- **方案 2**：保留现有数据，手动执行 SQL（适合已有数据）

### Q3: 如何确认初始化成功？

**A:** 运行以下命令：
```bash
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "
SELECT
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname IN ('core', 'mart', 'ops')
ORDER BY schemaname, tablename;
"
```

应该看到：
- `core.dim_series`
- `core.fact_observations`
- `ops.etl_runs`

### Q4: collector 还是报错怎么办？

**A:** 检查以下几点：
1. 数据库表是否真的创建成功
2. FRED_API_KEY 是否正确配置
3. 网络连接是否正常
4. 查看详细日志：`docker-compose logs data-collector`

## 手动修复步骤（不使用脚本）

如果脚本无法使用，可以手动执行：

```bash
# 1. 停止所有容器
docker-compose down

# 2. 删除数据卷
docker volume rm macrodashboard_postgres_data

# 3. 重新启动 PostgreSQL
docker-compose up -d postgres

# 4. 等待启动完成
sleep 30

# 5. 验证初始化
docker exec macro-postgres psql -U macro_user -d macro_dashboard -c "\dt core.*"

# 6. 启动其他服务
docker-compose up -d
```

## 预防措施

为避免将来出现类似问题：

1. **首次部署时**，确保数据卷不存在：
   ```bash
   docker volume ls | grep macro
   # 如果存在，先删除
   docker volume rm macrodashboard_postgres_data macrodashboard_redis_data
   ```

2. **更新初始化脚本后**，需要重建数据卷：
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. **定期备份数据**：
   ```bash
   docker exec macro-postgres pg_dump -U macro_user macro_dashboard > backup.sql
   ```

## 联系支持

如果问题仍未解决，请提供以下信息：

1. 诊断脚本输出：`bash diagnose_db.sh > diagnosis.log 2>&1`
2. 容器日志：`docker-compose logs > docker.log 2>&1`
3. 系统信息：`uname -a` 和 `docker version`

提交 Issue：https://github.com/K1ndredzzz/MacroDashboard/issues
