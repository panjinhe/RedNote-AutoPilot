# ⭐ RedNote-AutoPilot

AI 驱动的小红书电商中台自动化系统（MVP）。目标是把“自动上架脚本”升级为“AI 电商操作系统”。

## 1. 项目目标

本项目聚焦以下自动化能力：

- ✅ 自动创建商品
- ✅ 自动更新商品
- ✅ 自动上下架
- ✅ 自动库存同步
- ✅ 自动处理订单
- ✅ 自动优化标题与内容
- ✅ 自动分析销售数据并给出策略建议

**最终目标：让小红书店铺运营逐步走向无人值守。**

---

## 2. 官方 API 说明（重要）

- 开放平台：<https://open.xiaohongshu.com>
- API 网关：<https://ark.xiaohongshu.com/ark/open_api/v3/common_controller>
- OAuth 获取 token：<https://xiaohongshu.apifox.cn/doc-2810928>
- 签名算法说明：<https://xiaohongshu.apifox.cn/doc-2810932>
- 创建商品 API 示例：<https://xiaohongshu.apifox.cn/api-24841892>
- 更新商品 API 示例：<https://xiaohongshu.apifox.cn/api-24846432>
- 商品上下架 API 示例：<https://xiaohongshu.apifox.cn/api-24838962>

---

## 3. 技术栈

### 后端
- Python 3.14+
- FastAPI
- Pydantic / pydantic-settings
- Requests
- APScheduler

### AI 层
- 可替换 OpenAI API / 本地 LLM
- 当前内置规则生成器（MVP）

### 数据与基础设施（规划）
- Redis
- PostgreSQL
- Celery
- Docker / GitHub Actions / CI/CD

---

## 4. 项目结构

```text
rednote-autopilot/
├── app/
│   ├── api_client/
│   ├── ai_engine/
│   ├── product_manager/
│   ├── order_manager/
│   ├── inventory_manager/
│   ├── analytics/
│   ├── scheduler/
│   ├── workflows/
│   ├── models/
│   └── config/
├── docs/
├── tests/
└── README.md
```

---

## 5. 快速开始（使用 uv）

> 本项目环境管理使用 `uv`。

### 5.1 创建与安装依赖

```bash
uv sync
```

如果你要添加新依赖，请使用：

```bash
uv add <package>
```

### 5.2 本地运行 API

```bash
uv run fastapi dev app/main.py
```

可访问：
- `GET /health`
- `POST /products/auto-create`
- `GET /ops/sales-loop`
- `GET /ops/channel`

### 5.3 运行测试

```bash
uv run pytest
```

### 5.4 配置小红书 API 凭证

复制示例配置并填写你在小红书开放平台申请到的应用信息：

```bash
cp .env.example .env
```

至少需要配置以下环境变量：

- `REDNOTE_APP_ID`
- `REDNOTE_APP_SECRET`
- `REDNOTE_OPERATION_MODE`（`official_api` 或 `browser_rpa`）

> 当前项目会从 `.env` 自动加载上述配置（前缀 `REDNOTE_`）。

### 5.5 个人店铺无法使用官方 API 时的解决方案

如果你是**个人店铺**且暂时拿不到开放平台 API 权限，可以考虑以下路线（按合规优先级排序）：

1. **升级为企业主体并申请开放平台能力（推荐）**
   - 将店铺升级为企业主体，按开放平台要求提交资质。
   - 通过后即可使用本项目现有 API 接口能力（创建商品、上下架、库存、订单同步）。

2. **接入官方/服务商 ERP（折中方案）**
   - 通过有资质的第三方 ERP/SaaS 服务商完成商品与订单操作。
   - 本项目可转为“策略与内容中台”，由 ERP 执行实际上架动作。

3. **半自动运营（人工确认 + 脚本辅助）**
   - 使用本项目生成标题、卖点、详情和 SKU 建议，再由人工在商家后台手动发布。
   - 可以先落地“内容自动化 + 人工上架”，降低合规风险。

> 不建议使用违反平台规则的逆向抓包、未授权自动化登录等方式，否则可能导致账号风险。

### 5.6 采用 AI 自动控制浏览器（RPA）可以吗？

可以。本项目已支持通过 `REDNOTE_OPERATION_MODE=browser_rpa` 切换到浏览器任务通道（人机协同模式）。

推荐实践：

1. **AI 生成 + 浏览器自动填单 + 人工最终确认**
   - 自动化负责草稿填写与表单校验。
   - 最终发布动作由人工确认执行。

2. **最小权限与可追踪**
   - 仅自动化商品编辑场景。
   - 保留操作日志、草稿快照与回滚。

3. **和官方 API 双通道兼容**
   - 有 API 资质时用 `official_api`。
   - 无 API 资质时用 `browser_rpa`，流程保持一致。

### 5.7 关于“自动抓包上架”

不建议、也不支持未授权抓包、逆向接口、绕过验证码/风控等行为。

可行替代方案：
- 使用官方开放平台 API（`official_api`）。
- 使用浏览器人机协同通道（`browser_rpa`）。
- 接入有资质的 ERP/SaaS 服务商作为执行层。


---

## 6. 核心模块映射

### 6.1 API Client 层
`app/api_client/xhs_client.py`

已实现方法：
- `get_access_token`
- `refresh_token`
- `create_product`
- `update_product`
- `set_product_online`
- `set_product_offline`
- `get_orders`
- `update_stock`

签名规则（按文档约束落地）：

```text
sign = md5(method?appId=xxx&timestamp=xxx&version=2.0 + appSecret)
```

### 6.2 AI 商品生成模块
`app/ai_engine/content_generator.py`

输入：商品基础信息、成本、类目、关键词。  
输出：优化标题、卖点、详情文案、标签、FAQ、推荐 SKU。

### 6.3 商品自动创建流程
`app/product_manager/service.py`

流程：
1. AI 生成内容
2. 组装商品 payload
3. 调用 `create_product`
4. 自动上架 `set_product_online`

### 6.4 自动运营能力（当前 + 演进）
当前已实现：
- 订单同步
- 销售分析与策略建议

后续计划：
- 自动调价
- 自动下架滞销商品
- 自动补库存
- 自动评价回复 / 客服回复

---

## 7. 调度设计

`app/scheduler/jobs.py` 使用 APScheduler：
- 每 10 分钟同步订单
- 每 1 小时分析销售数据

后续可升级 Celery + Redis，实现分布式任务与重试队列。

---

## 8. 安全与权限建议

- token 加密存储（建议接入 KMS/Secret Manager）
- appSecret 不入库
- API 限流与重试
- 自动刷新 token
- 关键操作审计日志

---

## 9. 未来工程（技术积累与长期可维护）

为减少未来问题，建议按以下顺序演进：

1. **领域模型稳定化**：统一 Product/Order/Stock 的领域对象和状态机。
2. **可观测性**：接入结构化日志、Trace、核心指标（成功率、延迟、失败重试）。
3. **测试金字塔**：单元测试 + API 契约测试 + 沙箱集成测试。
4. **配置治理**：分环境配置（dev/staging/prod），密钥统一托管。
5. **任务可靠性**：幂等键、重试策略、死信队列。
6. **AI 安全护栏**：提示词模板版本化、输出校验、敏感词/违规内容检测。
7. **数据闭环**：销量-投放-内容效果的反馈学习机制。

---

## 10. 项目阶段路线图

### 第一阶段（MVP）
- [x] 商品自动创建
- [x] 自动上下架
- [x] 库存同步接口能力

### 第二阶段
- [x] AI 内容优化（基础版）
- [x] 自动分析销量（基础版）
- [ ] 自动调价策略执行

### 第三阶段
- [ ] SaaS 化（多店铺）
- [ ] 权限管理系统
- [ ] 企业级审计与财务对账

---

## 11. 声明

本仓库当前实现为可扩展的工程骨架 + MVP 流程，便于你后续快速接入真实小红书 API 与业务规则，持续演进为 AI 驱动电商中台。
