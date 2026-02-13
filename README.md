# RedNote-AutoPilot

一个**纯浏览器操作**的小红书商品上架助手（MVP）。

本项目已移除官方开放平台 API 客户端，聚焦两件事：
- AI 生成商品文案与结构化上架草稿。
- 浏览器辅助录入（人工最终确认发布）。

## 当前定位

- ✅ 不依赖小红书开放 API
- ✅ 支持 `manual` / `browser_assist` 两种执行模式
- ✅ 保留商品草稿生成、上架任务队列、运营分析骨架

## 快速开始

```bash
uv sync
cp .env.example .env
uv run fastapi dev app/main.py
```

可用接口：
- `GET /health`
- `POST /products/auto-create`：生成商品草稿并创建“待人工确认”的浏览器任务
- `GET /ops/sales-loop`
- `GET /ops/channel`

运行测试：

```bash
uv run pytest
```

## 配置

`.env` 关键项：

- `REDNOTE_OPERATION_MODE=manual|browser_assist`
- `REDNOTE_MERCHANT_PUBLISH_URL=<商家后台地址>`
- `REDNOTE_OPENAI_API_KEY=<可选>`

## 目录

```text
app/
├── ai_engine/         # 文案生成
├── channels/          # 浏览器执行通道（队列化任务）
├── product_manager/   # 商品草稿与创建流程
├── order_manager/
├── inventory_manager/
├── analytics/
├── workflows/
└── config/
```

## 拟定计划（请你确认）

### Phase 1（本周）
1. 固化 ListingPack 规范（title/desc/tags/sku/images/checklist）。
2. 新增 `publish assistant` CLI：逐字段展示 + 一键复制 + 打开商家后台。
3. 输出 `output/<product_id>/` 草稿包，便于回放与复用。

### Phase 2（下周）
1. 增加 `browser_assist` 的可配置字段映射（仅填充，不点击最终发布）。
2. 增加失败自动降级到 `manual`。
3. 增加任务审计日志（谁在何时发布了哪个草稿）。

### Phase 3
1. Excel/ERP ingest 适配器（按你的真实数据源落地）。
2. 每日上架清单与缺失字段报告。
3. 批量商品上架的执行面板。

## 本次重构变更

- 已删除 `app/api_client/`。
- 已移除 `official_api` 模式与相关配置项。
- 渠道工厂改为仅构建浏览器通道。
- 文档更新为纯浏览器上架助手定位。
