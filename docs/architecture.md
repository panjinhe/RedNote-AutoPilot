# RedNote-AutoPilot 技术设计文档

## 1. 项目目标

构建一个基于 AI 的自动化系统，实现：

- 自动创建商品
- 自动更新商品
- 自动上下架
- 自动库存同步
- 自动处理订单
- 自动优化标题与内容
- 自动分析销售数据并决策

最终目标：让小红书店铺运营实现“无人值守”。

## 2. 官方 API 说明

- 官网：<https://open.xiaohongshu.com>
- API 网关：<https://ark.xiaohongshu.com/ark/open_api/v3/common_controller>
- OAuth 获取 token：<https://xiaohongshu.apifox.cn/doc-2810928>
- 签名算法说明：<https://xiaohongshu.apifox.cn/doc-2810932>
- 创建商品 API 示例：<https://xiaohongshu.apifox.cn/api-24841892>
- 更新商品 API 示例：<https://xiaohongshu.apifox.cn/api-24846432>
- 商品上下架 API 示例：<https://xiaohongshu.apifox.cn/api-24838962>

## 3. 系统总体架构

```text
┌────────────────────┐
│ AI 引擎层           │
│ GPT / 自训练模型    │
└──────────┬─────────┘
           │
┌──────────▼─────────┐
│ 商品智能生成模块    │
└──────────┬─────────┘
           │
┌──────────────────────┼──────────────────────┐
│                      │                      │
┌────▼────┐      ┌──────▼──────┐      ┌──────▼──────┐
│ 商品管理 │      │ 订单管理     │      │ 库存管理     │
└────┬────┘      └──────┬──────┘      └──────┬──────┘
     │                  │                    │
     └──────────────┬───────┴──────────────┬───────┘
                    ▼                      ▼
              小红书 Open API          数据分析系统
```

## 4. 技术栈

- Python 3.10+
- FastAPI
- Pydantic
- Requests
- APScheduler / Celery
- Redis
- PostgreSQL
- OpenAI API / 本地 LLM
- Docker + CI/CD

## 5. 核心模块设计

### 5.1 API Client 层

`app/api_client/xhs_client.py`

```python
class XHSClient:
    def get_access_token()
    def refresh_token()
    def create_product()
    def update_product()
    def set_product_online()
    def set_product_offline()
    def get_orders()
    def update_stock()
```

签名规则：

```text
sign = md5(method?appId=xxx&timestamp=xxx&version=2.0 + appSecret)
```

### 5.2 AI 商品生成模块

输入：
- 商品基础信息
- 成本价格
- 类目
- 关键词

输出：
- 优化标题
- 卖点描述
- 详情页文案
- 标签
- FAQ
- 推荐 SKU 组合

### 5.3 商品自动创建流程

1. AI 生成商品内容
2. 校验类目和属性
3. 上传图片（待接入）
4. 调用 createItem
5. 创建 SKU
6. 设置库存
7. 自动上架

### 5.4 自动运营能力

- 自动调价（规划）
- 自动下架滞销商品（规划）
- 自动补库存（规划）
- 自动评价回复（规划）
- 自动客服回复（规划）

## 6. 数据库设计（建议）

表：`products`

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| xhs_product_id | string | 平台商品 ID |
| title | string | 标题 |
| cost_price | float | 成本 |
| sale_price | float | 售价 |
| status | enum | 上架/下架 |

## 7. 自动化调度设计

使用：
- APScheduler
- 或 Celery + Redis

定时任务：
- 每 10 分钟同步订单
- 每 1 小时分析销售数据
- 每天优化滞销商品（规划）

## 8. 安全与权限

- token 加密存储
- appSecret 不入库
- 限制接口调用频率
- 自动刷新 token

## 9. 部署架构

### 单机版
- Docker + PostgreSQL + Redis

### 生产版
- Kubernetes + API 服务 + Worker + Scheduler

## 10. 进阶路线

### 第一阶段
- 完成商品自动创建
- 完成自动上下架
- 完成库存同步

### 第二阶段
- 加入 AI 内容优化
- 自动分析销量
- 自动调价

### 第三阶段
- SaaS 化
- 多店铺支持
- 权限管理系统
