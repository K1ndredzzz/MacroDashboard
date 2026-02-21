# v2.0.1 Bug Fix - Events API 实现

**发布日期**: 2026-02-21
**版本**: v2.0.1

---

## 问题描述

历史事件回测功能在服务器上加载失败，显示 "Failed to fetch events" 错误。

**根本原因**: 后端 API 缺少 `/api/v1/events` 端点实现。

---

## 修复内容

### 1. 新增 Events API 端点

**文件**: `backend/api/app/api/v1/events.py`

实现了两个端点：

#### GET `/api/v1/events`
获取所有历史事件列表

**响应示例**:
```json
[
  {
    "event_id": 21,
    "event_name": "2026年2月美债收益率倒挂",
    "event_date": "2026-02-10",
    "event_type": "rates",
    "description": "美债2Y/10Y收益率曲线倒挂，衰退担忧加剧",
    "severity": "high"
  }
]
```

#### GET `/api/v1/events/{event_id}/impact`
分析事件对指标的影响

**参数**:
- `event_id`: 事件 ID
- `indicator_codes`: 逗号分隔的指标代码（如 "US10Y,US2Y,EURUSD"）
- `window_days`: 分析窗口天数（默认 30 天）

**响应示例**:
```json
{
  "event": {
    "event_id": 21,
    "event_name": "2026年2月美债收益率倒挂",
    "event_date": "2026-02-10",
    "event_type": "rates",
    "description": "美债2Y/10Y收益率曲线倒挂，衰退担忧加剧",
    "severity": "high"
  },
  "indicators": [
    {
      "indicator_code": "US10Y",
      "indicator_name": "US 10-Year Treasury Yield",
      "before_value": 4.22,
      "after_value": 4.08,
      "change_pct": -3.32,
      "observations": [...]
    }
  ],
  "analysis_window_days": 30
}
```

### 2. 注册路由

**文件**: `backend/api/app/main.py`

添加了 events 路由注册：
```python
from .api.v1 import indicators, health, simulation, events

app.include_router(
    events.router,
    prefix=f"{settings.API_V1_PREFIX}/events",
    tags=["events"]
)
```

---

## 部署说明

### Docker 镜像

**新版本镜像**:
- `fuzhouxing/macro-dashboard-api:v2.0.1`
- `fuzhouxing/macro-dashboard-api:latest`

**Digest**: `sha256:9d9c14be0c2fdfcdb7302a710b61a2bf2b2c5e6ecce34bede852ddb71b626f02`

### 更新步骤

1. 拉取新镜像：
```bash
docker pull fuzhouxing/macro-dashboard-api:v2.0.1
```

2. 更新 docker-compose.yml（如果使用固定版本）：
```yaml
api:
  image: fuzhouxing/macro-dashboard-api:v2.0.1
```

3. 重启服务：
```bash
docker compose down api
docker compose up -d api
```

---

## 测试验证

### 1. 测试 Events 列表
```bash
curl http://localhost:8020/api/v1/events
```

### 2. 测试 Event Impact
```bash
curl "http://localhost:8020/api/v1/events/21/impact?indicator_codes=US10Y,US2Y,EURUSD&window_days=30"
```

### 3. 前端验证
访问 http://localhost:8021，检查"历史事件回测"组件是否正常加载。

---

## 数据库要求

确保数据库中已执行以下脚本：
- `backend/scripts/postgres/02_events.sql`

该脚本会创建 `core.dim_events` 表并插入测试事件数据。

---

## 影响范围

**修复的功能**:
- ✅ 历史事件回测 - 事件列表加载
- ✅ 历史事件回测 - 事件影响分析
- ✅ 历史事件回测 - 趋势图展示

**不影响的功能**:
- 时间范围选择器
- 收益率曲线
- 相关性热力图
- 情景冲击模拟器

---

## 版本对比

| 版本 | 状态 | 说明 |
|------|------|------|
| v2.0.0 | ❌ | 缺少 Events API，历史事件回测不可用 |
| v2.0.1 | ✅ | 完整实现 Events API，所有功能正常 |

---

## 后续建议

1. **添加单元测试**: 为 events API 添加测试用例
2. **添加缓存**: 对事件列表添加 Redis 缓存
3. **性能优化**: 对大量观测数据的查询进行优化
4. **错误处理**: 增强边界情况的错误处理

---

## 相关文件

- `backend/api/app/api/v1/events.py` - Events API 实现
- `backend/api/app/main.py` - 路由注册
- `backend/scripts/postgres/02_events.sql` - 数据库表和数据
- `frontend/src/components/EventBacktest.tsx` - 前端组件

---

**修复完成！** 🎉

现在服务器上的历史事件回测功能应该可以正常工作了。
