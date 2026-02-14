#!/usr/bin/env python3
"""
小红书APP自动化上架工具

通过Android模拟器自动操作小红书APP进行商品上架。
需要先安装好Android模拟器（推荐LDPlayer雷电模拟器）。

使用前提：
1. 安装雷电模拟器：https://www.ldmnq.com/
2. 在模拟器中安装小红书APP并登录
3. 确保ADB已配置到系统PATH

用法：
    python -m scripts.xhs_uploader --help
"""

import argparse
import subprocess
import time
import os
from pathlib import Path
from typing import Optional

# 导入android_controller的工具函数
from android_controller import (
    run_adb_command, get_devices, tap, swipe, input_text, press_key,
    take_screenshot, start_app, get_screen_size, XHS_PACKAGE, XHS_ACTIVITY,
    OUTPUT_DIR
)


# ==================== 配置 ====================
# 模拟器端口（根据你的模拟器调整）
# 雷电模拟器默认: 5555
# 蓝叠模拟器默认: 5554
# 夜神模拟器默认: 62001
EMULATOR_PORT = 5555

# 截图目录
SCREENSHOT_DIR = OUTPUT_DIR / "uploader"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ==================== 工具函数 ====================

def ensure_connected() -> bool:
    """确保模拟器已连接"""
    devices = get_devices()
    if devices:
        return True
    
    # 尝试连接
    result = run_adb_command(["connect", f"127.0.0.1:{EMULATOR_PORT}"])
    time.sleep(2)
    devices = get_devices()
    return len(devices) > 0


def wait_for_app_running(package: str, timeout: int = 10) -> bool:
    """等待APP启动"""
    for _ in range(timeout):
        result = run_adb_command(["shell", "ps", "-A"])
        if package in result.stdout:
            return True
        time.sleep(1)
    return False


def capture_and_save(name: str) -> str:
    """截图并保存"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    return take_screenshot(filename)


# ==================== 小红书操作 ====================

def open_xhs_app() -> bool:
    """打开小红书APP"""
    print("正在打开小红书...")
    if not ensure_connected():
        print("错误: 无法连接模拟器")
        return False
    
    start_app(XHS_PACKAGE, XHS_ACTIVITY)
    time.sleep(5)  # 等待APP启动
    
    capture_and_save("app_opened")
    return True


def find_and_click_by_text(text: str, timeout: int = 10) -> bool:
    """通过文本查找并点击（需要UI Automator）"""
    # 使用uiautomator查找元素
    cmd = [
        "shell", "uiautomator", "dump", "/sdcard/window_dump.xml"
    ]
    run_adb_command(cmd)
    time.sleep(1)
    
    # 拉取XML分析
    local_xml = SCREENSHOT_DIR / "window_dump.xml"
    run_adb_command(["pull", "/sdcard/window_dump.xml", str(local_xml)])
    
    # 简单解析XML查找文本（这里简化处理，实际需要更复杂的解析）
    # 实际实现可以使用 uiautomatorviewer 或 Android SDK tools
    print(f"查找文本: {text}")
    return False


def click_at_ratio(x_ratio: float, y_ratio: float) -> bool:
    """根据屏幕比例点击"""
    width, height = get_screen_size()
    x = int(width * x_ratio)
    y = int(height * y_ratio)
    print(f"点击坐标: ({x}, {y})")
    return tap(x, y)


def wait_and_sleep(seconds: float):
    """等待指定秒数"""
    print(f"等待 {seconds} 秒...")
    time.sleep(seconds)


# ==================== 上架流程 ====================

def navigate_to_publish_page() -> bool:
    """导航到发布商品页面"""
    print("导航到发布商品页面...")
    
    # 1. 点击右下角"发布"按钮
    # 小红书首页右下角有一个+号发布按钮
    wait_and_sleep(2)
    
    # 根据常见的1080x1920分辨率，"+"按钮大约在右下角
    # 位置比例大约是 x=0.9, y=0.85
    click_at_ratio(0.9, 0.85)
    wait_and_sleep(2)
    
    capture_and_save("publish_menu")
    
    # 2. 选择"发布商品"选项
    # 这里需要根据实际界面调整坐标
    # 常见位置大约在中间偏下
    click_at_ratio(0.5, 0.7)
    wait_and_sleep(3)
    
    capture_and_save("publish_page")
    return True


def fill_product_info(
    title: str,
    description: str,
    price: float,
    stock: int,
    category: str = None
) -> bool:
    """填写商品信息"""
    print("填写商品信息...")
    
    # 1. 输入商品标题
    print(f"输入标题: {title}")
    click_at_ratio(0.5, 0.15)  # 点击标题输入框
    wait_and_sleep(1)
    input_text(title)
    wait_and_sleep(1)
    
    capture_and_save("title_filled")
    
    # 2. 输入商品描述/正文
    print(f"输入描述: {description[:50]}...")
    click_at_ratio(0.5, 0.3)  # 点击描述输入框
    wait_and_sleep(1)
    input_text(description)
    wait_and_sleep(1)
    
    capture_and_save("desc_filled")
    
    # 3. 输入价格
    print(f"输入价格: {price}")
    click_at_ratio(0.5, 0.5)  # 点击价格输入框
    wait_and_sleep(1)
    input_text(str(price))
    wait_and_sleep(1)
    
    capture_and_save("price_filled")
    
    # 4. 输入库存
    print(f"输入库存: {stock}")
    click_at_ratio(0.5, 0.6)  # 点击库存输入框
    wait_and_sleep(1)
    input_text(str(stock))
    wait_and_sleep(1)
    
    capture_and_save("stock_filled")
    
    return True


def add_product_images() -> bool:
    """添加商品图片"""
    print("添加商品图片...")
    
    # 1. 点击添加图片按钮
    # 通常在顶部或商品图片区域
    click_at_ratio(0.5, 0.2)
    wait_and_sleep(2)
    
    capture_and_save("image_picker")
    
    # 2. 选择图片（从相册）
    # 点击"相册"选项
    click_at_ratio(0.3, 0.8)
    wait_and_sleep(2)
    
    # 3. 选择第一张图片
    click_at_ratio(0.2, 0.3)
    wait_and_sleep(1)
    
    # 4. 确认选择
    click_at_ratio(0.8, 0.9)
    wait_and_sleep(2)
    
    capture_and_save("image_added")
    return True


def select_product_category(category: str) -> bool:
    """选择商品类目"""
    print(f"选择类目: {category}")
    
    # 点击类目选择框
    click_at_ratio(0.5, 0.45)
    wait_and_sleep(2)
    
    capture_and_save("category_menu")
    
    # 这里需要根据实际类目结构调整
    # 简单处理：直接输入搜索
    input_text(category)
    wait_and_sleep(1)
    
    # 选择第一个结果
    click_at_ratio(0.5, 0.35)
    wait_and_sleep(1)
    
    return True


def publish_product() -> bool:
    """发布商品"""
    print("发布商品...")
    
    # 1. 点击发布/提交按钮
    # 通常在底部
    click_at_ratio(0.5, 0.92)
    wait_and_sleep(3)
    
    capture_and_save("published")
    
    # 2. 可能需要确认发布
    # 点击确认
    click_at_ratio(0.7, 0.8)
    wait_and_sleep(5)
    
    capture_and_save("confirm_publish")
    
    return True


def auto_publish_product(
    title: str,
    description: str,
    price: float,
    stock: int,
    category: str = None,
    add_images: bool = True
) -> bool:
    """自动发布商品完整流程"""
    print("=" * 50)
    print("开始自动上架流程")
    print("=" * 50)
    
    # 确保连接
    if not ensure_connected():
        print("错误: 无法连接模拟器")
        return False
    
    # 打开小红书
    if not open_xhs_app():
        return False
    
    # 导航到发布页
    if not navigate_to_publish_page():
        return False
    
    # 填写商品信息
    if not fill_product_info(title, description, price, stock, category):
        print("警告: 填写信息可能有问题")
    
    # 添加图片
    if add_images:
        add_product_images()
    
    # 选择类目
    if category:
        select_product_category(category)
    
    # 发布
    if not publish_product():
        print("警告: 发布可能有问题")
    
    print("=" * 50)
    print("上架流程完成")
    print("=" * 50)
    
    capture_and_save("final_result")
    
    return True


# ==================== 交互模式 ====================

def interactive_mode():
    """交互模式 - 手动操作辅助"""
    print("=" * 50)
    print("小红书交互模式")
    print("=" * 50)
    print("可用命令:")
    print("  tap <x> <y>           - 点击坐标")
    print("  swipe <x1> <y1> <x2> <y2> - 滑动")
    print("  input <text>          - 输入文字")
    print("  screenshot            - 截图")
    print("  open                  - 打开小红书")
    print("  quit                  - 退出")
    print("=" * 50)
    
    ensure_connected()
    open_xhs_app()
    
    while True:
        try:
            cmd = input("\n请输入命令: ").strip()
            if not cmd:
                continue
            
            parts = cmd.split()
            action = parts[0].lower()
            
            if action == "quit" or action == "q":
                print("退出")
                break
            
            elif action == "tap":
                if len(parts) >= 3:
                    x, y = int(parts[1]), int(parts[2])
                    tap(x, y)
                    print(f"已点击: ({x}, {y})")
                else:
                    print("用法: tap <x> <y>")
            
            elif action == "swipe":
                if len(parts) >= 5:
                    x1, y1, x2, y2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                    swipe(x1, y1, x2, y2)
                    print(f"已滑动: ({x1}, {y1}) -> ({x2}, {y2})")
                else:
                    print("用法: swipe <x1> <y1> <x2> <y2>")
            
            elif action == "input":
                if len(parts) >= 2:
                    text = " ".join(parts[1:])
                    input_text(text)
                    print(f"已输入: {text}")
                else:
                    print("用法: input <text>")
            
            elif action == "screenshot":
                path = capture_and_save("manual")
                print(f"截图保存: {path}")
            
            elif action == "open":
                open_xhs_app()
            
            elif action == "help" or action == "h":
                print("可用命令: tap, swipe, input, screenshot, open, quit")
            
            else:
                print(f"未知命令: {action}")
        
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误: {e}")


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="小红书APP自动化上架工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 交互模式（推荐首次使用）
  python -m scripts.xhs_uploader interactive

  # 自动上架商品
  python -m scripts.xhs_uploader auto \
    --title "测试商品" \
    --description "这是一个测试商品" \
    --price 99.9 \
    --stock 100 \
    --category "美妆"

  # 截图
  python -m scripts.xhs_uploader screenshot

  # 打开小红书
  python -m scripts.xhs_uploader open
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 交互模式
    subparsers.add_parser("interactive", help="交互模式（手动操作）")
    
    # 自动上架
    auto_parser = subparsers.add_parser("auto", help="自动上架商品")
    auto_parser.add_argument("--title", required=True, help="商品标题")
    auto_parser.add_argument("--description", required=True, help="商品描述")
    auto_parser.add_argument("--price", type=float, required=True, help="商品价格")
    auto_parser.add_argument("--stock", type=int, required=True, help="商品库存")
    auto_parser.add_argument("--category", help="商品类目")
    auto_parser.add_argument("--no-images", action="store_true", help="不添加图片")
    
    # 截图
    subparsers.add_parser("screenshot", help="截图")
    
    # 打开小红书
    subparsers.add_parser("open", help="打开小红书APP")
    
    # 连接模拟器
    connect_parser = subparsers.add_parser("connect", help="连接模拟器")
    connect_parser.add_argument("--port", type=int, default=EMULATOR_PORT, help="模拟器端口")
    
    args = parser.parse_args()
    
    if args.command == "interactive":
        interactive_mode()
        
    elif args.command == "auto":
        auto_publish_product(
            title=args.title,
            description=args.description,
            price=args.price,
            stock=args.stock,
            category=args.category,
            add_images=not args.no_images
        )
        
    elif args.command == "screenshot":
        capture_and_save("manual")
        
    elif args.command == "open":
        open_xhs_app()
        
    elif args.command == "connect":
        ensure_connected()
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
