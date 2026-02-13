# RedNote-AutoPilot 架构说明（纯浏览器版）

## 1. 目标

RedNote-AutoPilot 现在是一个**纯浏览器操作**的小红书商品上架助手：

- AI 负责生成商品草稿（标题、卖点、详情、标签、SKU 建议）。
- 系统负责生成可执行任务（待人工确认）。
- 浏览器侧只承担录入辅助，最终发布由人工完成。

## 2. 总体架构

```text
┌───────────────────────┐
│   AI 内容生成层         │
│ ai_engine/content_*    │
└─────────────┬─────────┘
              │
┌─────────────▼─────────┐
│   商品工作流编排层      │
│ workflows/auto_ops.py  │
└───────┬─────────┬─────┘
        │         │
┌───────▼───┐ ┌───▼──────────┐
│商品管理层   │ │运营分析/调度层  │
│product_*   │ │analytics/scheduler│
└───────┬───┘ └──────────────┘
        │
┌───────▼────────────────────┐
│ 浏览器通道层 channels/      │
│ BrowserRPAChannel           │
│ 输出 queued_for_manual_* 任务 │
└────────────────────────────┘
```

## 3. 核心模块

- `app/ai_engine/`：商品文案生成。
- `app/product_manager/`：组装草稿并生成创建/更新任务。
- `app/channels/browser_rpa.py`：浏览器辅助任务通道。
- `app/channels/factory.py`：统一通道构建（仅浏览器通道）。
- `app/workflows/auto_ops.py`：运营流程入口。

## 4. 配置

- `REDNOTE_OPERATION_MODE=manual|browser_assist`
- `REDNOTE_MERCHANT_PUBLISH_URL=<商家后台地址>`

## 5. 后续演进

1. ListingPack 标准化输出（title/desc/tags/sku/images/checklist）。
2. CLI 发布助手（复制字段、打开页面、逐项确认）。
3. browser_assist 字段映射可配置化。
4. 执行日志与回放能力。
