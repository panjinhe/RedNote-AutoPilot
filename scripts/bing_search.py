#!/usr/bin/env python3
"""
Bing搜索任务自动化工具

使用Playwright控制已打开的Edge浏览器进行搜索任务。

用法：
    python -m scripts.bing_search run --keywords "Python教程" --count 10
"""

import argparse
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


# 配置
USER_DATA_DIR = Path(".browser/bing-profile-new")
DEBUG_PORT = 9222


def get_browser_context():
    """连接到已运行的Edge浏览器"""
    playwright = sync_playwright().start()
    
    # 连接到已运行的浏览器（通过调试端口）
    browser = playwright.chromium.connect_over_cdp(
        f"http://localhost:{DEBUG_PORT}"
    )
    
    # 获取第一个context（我们打开的 bing-profile-new）
    contexts = browser.contexts
    if not contexts:
        raise Exception("没有找到浏览器上下文")
    
    return playwright, browser, contexts[0]


def save_storage_state():
    """保存当前登录状态"""
    playwright, browser, context = get_browser_context()
    
    state_path = Path(".browser/bing_storage_new.json")
    context.storage_state(path=str(state_path))
    print(f"[OK] Login state saved to: {state_path}")
    
    playwright.stop()


def run_search_task(keywords: str, count: int = 10, delay: float = 3.0):
    """执行搜索任务"""
    print(f"Starting search task...")
    print(f"Keyword: {keywords}")
    print(f"Search count: {count}")
    print("-" * 40)
    
    playwright, browser, context = get_browser_context()
    
    # 获取所有页面
    pages = context.pages
    if not pages:
        raise Exception("没有找到打开的页面")
    
    # 使用第一个页面（通常是Bing）
    page = pages[0]
    
    for i in range(count):
        try:
            print(f"[{i+1}/{count}] Searching: {keywords}")
            
            # 如果不在Bing页面，先跳转
            if "bing.com" not in page.url:
                page.goto("https://www.bing.com")
                time.sleep(2)
            
            # 清除搜索框并输入 - 使用更通用的选择器
            # 尝试多种选择器
            try:
                search_box = page.locator('input[name="q"]').first
            except:
                try:
                    search_box = page.locator('#sb_form_q').first
                except:
                    search_box = page.locator('input[type="search"]').first
            
            search_box.click()
            search_box.fill("")
            
            # 输入关键词
            search_box.type(keywords, delay=100)
            
            # 点击搜索按钮或按回车
            page.keyboard.press("Enter")
            
            # 等待结果加载
            time.sleep(delay)
            
            # 滚动页面（模拟真实浏览）
            for _ in range(3):
                page.mouse.wheel(0, 300)
                time.sleep(0.5)
            
            print(f"[OK] Search completed")
            
            # 随机等待
            wait_time = delay + (hash(str(i)) % 3)
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            continue
    
    print("-" * 40)
    print(f"[OK] Search task completed! Total: {count} searches")
    
    playwright.stop()


def main():
    parser = argparse.ArgumentParser(description="Bing搜索任务工具")
    subparsers = parser.add_subparsers(dest="command")
    
    # 保存状态
    subparsers.add_parser("save", help="保存当前登录状态")
    
    # 运行搜索
    run_parser = subparsers.add_parser("run", help="执行搜索任务")
    run_parser.add_argument("-k", "--keywords", required=True, help="搜索关键词")
    run_parser.add_argument("-c", "--count", type=int, default=10, help="搜索次数")
    run_parser.add_argument("-d", "--delay", type=float, default=3.0, help="每次搜索间隔(秒)")
    
    args = parser.parse_args()
    
    if args.command == "save":
        save_storage_state()
    elif args.command == "run":
        run_search_task(args.keywords, args.count, args.delay)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
