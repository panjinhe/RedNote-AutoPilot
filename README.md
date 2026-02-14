# RedNote-AutoPilot

一个支持**手机端全自动执行 + 浏览器辅助兜底**的小红书商品上架助手（MVP+）。

所有PR和Commit消息使用中文

本项目已移除官方开放平台 API 客户端，聚焦三件事：
- AI 生成商品文案与结构化上架草稿。
- 手机端自动执行上架任务（默认模式）。
- 浏览器辅助录入（作为兜底模式）。

## 当前定位

- ✅ 不依赖小红书开放 API
- ✅ 支持 `auto_device` / `manual` / `browser_assist` 三种执行模式
- ✅ 内置任务持久化、步骤审计日志、自动执行器
- ✅ 保留商品草稿生成、上架任务队列、运营分析骨架

## 快速开始

```bash
uv sync
cp .env.example .env
uv run fastapi dev app/main.py
```

可用接口：
- `GET /health`
- `POST /products/auto-create`：生成商品草稿、创建任务，并在 `auto_device` 模式下自动执行上架
- `GET /tasks/{task_id}`：查询任务状态与执行结果
- `GET /ops/sales-loop`
- `GET /ops/channel`

运行测试：

```bash
uv run pytest
```

## 配置

`.env` 关键项：

- `REDNOTE_OPERATION_MODE=auto_device|manual|browser_assist`
- `REDNOTE_MERCHANT_PUBLISH_URL=<商家后台地址>`
- `REDNOTE_DEVICE_ID=<设备ID，默认 emulator-5554>`
- `REDNOTE_TASK_DB_PATH=<任务数据库路径，默认 data/autopilot.db>`
- `REDNOTE_OPENAI_API_KEY=<可选>`

## 目录

```text
app/
├── ai_engine/         # 文案生成
├── channels/          # 自动设备通道 + 浏览器兜底通道
├── product_manager/   # 商品草稿与创建流程
├── order_manager/
├── inventory_manager/
├── analytics/
├── workflows/
└── config/
```


## 手机端专属场景建议

如果你遇到“只能在手机 App 上架”，请优先参考：`docs/android_emulator_guide.md`。

文档给出了低成本且稳定优先的推荐路径：**真机 Android + ADB + scrcpy + 半自动（人工最终发布）**，模拟器仅作为备选。

若你正在评估“距离可稳定控制手机上架还缺什么”，可先看清单：`docs/mobile_listing_gap_checklist.md`。

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
- 渠道工厂支持自动设备通道与浏览器兜底通道。
- 文档更新为自动化优先的上架助手定位。

## 持久化上下文自动化（方案 A）

如果你需要在登录后执行自动化（例如货架页），推荐使用持久化上下文。

### 1) 安装依赖

```bash
uv add --dev playwright
```

> 注意：脚本默认使用系统 Edge 浏览器，无需手动下载 Chromium。如需使用其他浏览器，可加 `--browser chrome` 或 `--browser chromium`。

### 2) 首次手动登录并保存会话

```bash
uv run python scripts/login_once.py \
  --url "https://ark.xiaohongshu.com/app-item/list/shelf" \
  --user-data-dir ".browser/xhs-profile" \
  --state-path ".browser/storage_state.json"
```

在弹出的浏览器里手动登录，回到终端按 Enter 后会保存状态。

### 3) 复用登录态执行任务

```bash
uv run python scripts/run_shelf_task.py \
  --url "https://ark.xiaohongshu.com/app-item/list/shelf" \
  --user-data-dir ".browser/xhs-profile" \
  --state-path ".browser/storage_state.json" \
  --artifact-dir "artifacts/browser"
```

脚本会输出：
- 页面截图（便于确认是否仍是登录态）
- 当前 storage state 导出
- 命中 `shelf` 关键字的首个 API 返回样本（JSON）

### 交互模式（推荐开发使用）

如果需要点击链接、打开发布页面等，可以使用交互模式：

```bash
uv run python scripts/run_shelf_task.py --interactive
```

这会保持浏览器打开，你可以随意操作，完成后按 Enter 保存。

如果链接会打**新标签页**（如"发布单品"），加上 `--wait-for-new-tab`：

```bash
uv run python scripts/run_shelf_task.py --interactive --wait-for-new-tab
```

脚本会自动等待新标签页打开并切换到该标签页。

> **浏览器选择**：默认使用 Edge。如需换 Chrome 或 Chromium：
> ```bash
> uv run python scripts/login_once.py --browser chrome
> uv run python scripts/run_shelf_task.py --browser chrome
> ```

> 建议把 `.browser/` 与 `artifacts/` 加入 `.gitignore`，避免提交敏感会话信息。
