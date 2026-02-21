# 第一阶段功能开发计划

## 目标：核心分析功能（2 周）

### 1. 利率曲线图 ✓ 预计 3 天

**需求描述**
- 展示美债收益率曲线（2Y/10Y）
- 识别曲线形态（正常/倒挂/平坦）
- 历史曲线对比

**技术实现**
- 后端：新增 API 端点 `/api/v1/indicators/yield-curve`
- 前端：使用 Recharts LineChart
- 数据：从现有 US2Y 和 US10Y 数据计算利差

**验收标准**
- [ ] 显示当前利率曲线
- [ ] 显示利差（10Y - 2Y）
- [ ] 标注曲线形态（正常/倒挂）
- [ ] 支持历史日期选择

**文件清单**
```
backend/api/app/api/v1/yield_curve.py          # 新增路由
backend/api/app/repositories/postgres_repo.py  # 新增查询方法
frontend/src/components/YieldCurve.tsx         # 新增组件
frontend/src/services/api.service.ts           # 新增 API 调用
```

---

### 2. 时间范围选择器 ✓ 预计 2 天

**需求描述**
- 预设时间范围：1M/3M/6M/1Y/YTD/ALL
- 自定义日期范围选择
- 全局状态管理

**技术实现**
- 前端：React Context 管理时间范围状态
- 组件：DateRangePicker 组件
- 集成：所有图表组件响应时间范围变化

**验收标准**
- [ ] 预设按钮快速切换
- [ ] 自定义日期选择器
- [ ] 所有图表同步更新
- [ ] URL 参数持久化

**文件清单**
```
frontend/src/contexts/TimeRangeContext.tsx     # 新增上下文
frontend/src/components/DateRangePicker.tsx    # 新增组件
frontend/src/hooks/useDateRange.ts             # 新增 Hook
frontend/src/App.tsx                           # 集成上下文
```

---

### 3. 相关性分析（热力图）✓ 预计 1 周

**需求描述**
- 计算指标间的相关系数矩阵
- 热力图可视化
- 支持滚动窗口（30/60/90 天）
- 识别相关性突变

**技术实现**
- 后端：新增 API 端点 `/api/v1/analytics/correlation`
- 算法：使用 NumPy/Pandas 计算 Pearson 相关系数
- 前端：使用 Recharts 或 D3.js 绘制热力图
- 优化：Redis 缓存计算结果

**验收标准**
- [ ] 显示相关系数矩阵热力图
- [ ] 支持窗口期选择（30/60/90 天）
- [ ] 鼠标悬停显示详细数值
- [ ] 标注强相关/负相关对

**文件清单**
```
backend/api/app/api/v1/analytics.py            # 新增路由
backend/api/app/services/correlation.py        # 新增相关性计算服务
backend/api/requirements.txt                   # 添加 numpy, pandas
frontend/src/components/CorrelationHeatmap.tsx # 新增组件
frontend/src/pages/AnalyticsPage.tsx           # 新增页面
```

**数据库优化**
```sql
-- 添加索引优化查询性能
CREATE INDEX idx_fact_obs_code_date_value
ON core.fact_observations(indicator_code, observation_date, value);
```

---

### 4. 历史回测功能 ✓ 预计 1 周

**需求描述**
- 重大事件回放（2008 金融危机、2020 疫情、2022 俄乌冲突）
- 可视化事件前后指标变化
- 事件时间线标注
- 自定义时间段分析

**技术实现**
- 后端：新增 API 端点 `/api/v1/analytics/event-impact`
- 数据：预定义重大事件列表
- 前端：时间线组件 + 多指标对比图表
- 分析：计算事件前后 N 天的变化率

**验收标准**
- [ ] 预设重大事件列表
- [ ] 事件时间线可视化
- [ ] 显示事件前后指标变化
- [ ] 支持自定义事件添加
- [ ] 多指标对比图表

**文件清单**
```
backend/api/app/api/v1/events.py               # 新增路由
backend/api/app/models/events.py               # 事件模型
backend/scripts/postgres/02_events.sql         # 事件表 DDL
frontend/src/components/EventTimeline.tsx      # 时间线组件
frontend/src/components/EventImpact.tsx        # 影响分析组件
frontend/src/pages/BacktestPage.tsx            # 新增页面
```

**数据库设计**
```sql
-- 事件表
CREATE TABLE IF NOT EXISTS core.dim_events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入预定义事件
INSERT INTO core.dim_events (event_name, event_date, event_type, description, severity) VALUES
    ('2008 金融危机', '2008-09-15', 'financial_crisis', '雷曼兄弟破产', 'critical'),
    ('2020 疫情爆发', '2020-03-11', 'pandemic', 'WHO 宣布 COVID-19 为全球大流行', 'critical'),
    ('2022 俄乌冲突', '2022-02-24', 'geopolitical', '俄罗斯入侵乌克兰', 'high');
```

---

## 开发时间表

### Week 1
- **Day 1-2**: 时间范围选择器
  - 实现 Context 和组件
  - 集成到现有页面

- **Day 3-5**: 利率曲线图
  - 后端 API 开发
  - 前端组件开发
  - 测试和优化

### Week 2
- **Day 1-3**: 相关性分析
  - 后端计算服务
  - 热力图组件
  - 缓存优化

- **Day 4-7**: 历史回测功能
  - 数据库设计
  - 后端 API 开发
  - 前端页面开发
  - 集成测试

---

## 技术准备

### 后端依赖
```bash
# 添加到 backend/api/requirements.txt
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
```

### 前端依赖
```bash
# 添加到 frontend/package.json
npm install date-fns
npm install recharts@latest
npm install @types/d3  # 如果使用 D3.js
```

### 数据库迁移
```bash
# 执行新的 SQL 脚本
cat backend/scripts/postgres/02_events.sql | \
    docker exec -i macro-postgres psql -U macro_user -d macro_dashboard
```

---

## 测试计划

### 单元测试
- [ ] 相关性计算算法测试
- [ ] 日期范围处理测试
- [ ] 事件查询测试

### 集成测试
- [ ] API 端点测试
- [ ] 前后端集成测试
- [ ] 性能测试（大数据集）

### 用户测试
- [ ] 功能可用性测试
- [ ] 交互体验测试
- [ ] 浏览器兼容性测试

---

## 风险与应对

### 风险 1：相关性计算性能
- **风险**：大量数据计算相关系数可能较慢
- **应对**：
  - 使用 Redis 缓存结果
  - 限制最大计算窗口
  - 异步计算 + 进度提示

### 风险 2：历史数据不足
- **风险**：某些指标历史数据不完整
- **应对**：
  - 数据回填脚本
  - 前端显示数据可用性提示
  - 支持部分指标分析

### 风险 3：前端性能
- **风险**：大量数据点渲染可能卡顿
- **应对**：
  - 数据降采样
  - 虚拟滚动
  - Web Worker 计算

---

## 成功指标

### 功能指标
- ✅ 4 个核心功能全部上线
- ✅ API 响应时间 P95 < 1s
- ✅ 前端首屏加载 < 3s

### 用户体验指标
- ✅ 图表交互流畅（60 FPS）
- ✅ 数据更新实时响应
- ✅ 移动端适配良好

### 技术指标
- ✅ 测试覆盖率 > 70%
- ✅ 无严重 Bug
- ✅ 代码审查通过

---

## 下一步

完成第一阶段后，进入第二阶段：
1. World Bank 数据集成
2. Yahoo Finance 股票数据
3. 更多图表类型

**预计开始时间**：第一阶段完成后 1 周内
