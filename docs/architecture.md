# RedNote-AutoPilot 架构说明（自动化增强版）

## 1. 目标

RedNote-AutoPilot 现在是一个**自动化优先**的小红书商品上架助手：

- AI 负责生成商品草稿（标题、卖点、详情、标签、SKU 建议）。
- 系统负责生成标准化 `ListingPack` 与 `ListingTask`。
- 默认通过手机端自动通道执行上架；浏览器模式作为兜底。

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
│任务执行层   │ │运营分析/调度层  │
│tasks/*     │ │analytics/scheduler│
└───────┬───┘ └──────────────┘
        │
┌───────▼────────────────────┐
│ 通道层 channels/            │
│ DeviceAutoChannel (默认)    │
│ BrowserRPAChannel (兜底)    │
└────────────────────────────┘
```

## 3. 核心模块

- `app/ai_engine/`：商品文案生成。
- `app/product_manager/`：组装草稿、创建任务、触发自动执行。
- `app/tasks/repository.py`：任务与步骤日志持久化（SQLite）。
- `app/tasks/executor.py`：模块化步骤执行器（create/online，可扩展）。
- `app/channels/device_auto.py`：手机端自动执行通道。
- `app/channels/factory.py`：统一通道构建。

## 4. 配置

- `REDNOTE_OPERATION_MODE=auto_device|manual|browser_assist`
- `REDNOTE_DEVICE_ID=<设备ID>`
- `REDNOTE_TASK_DB_PATH=<任务数据库路径>`
- `REDNOTE_MERCHANT_PUBLISH_URL=<商家后台地址>`

## 5. 演进方向

1. 扩展步骤插件（图片上传、资质填报、运费模板）。
2. 新增失败重试策略（指数退避 + 步骤级重试上限）。
3. 增加多设备调度与任务分片执行。
4. 增加可观测性面板（成功率、耗时、失败聚类）。
