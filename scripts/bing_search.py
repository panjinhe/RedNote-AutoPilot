#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing搜索任务自动化工具

使用Playwright控制已打开的Edge浏览器进行搜索任务。

用法：
    python -m scripts.bing_search run --count 5           # 使用随机关键词搜索5次
    python -m scripts.bing_search run -k "Python" -c 3   # 搜索指定关键词3次
    python -m scripts.bing_search run --random          # 使用随机关键词（默认值5次）
"""

import argparse
import random
import sys
import time
from pathlib import Path

# 设置UTF-8编码
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from playwright.sync_api import sync_playwright


# ============ 配置 ============
DEBUG_PORT = 9222

# 默认随机关键词列表（可以自行添加更多）
DEFAULT_KEYWORDS = [
    "Python教程",
    "人工智能",
    "机器学习",
    "数据分析",
    "Web开发",
    "JavaScript",
    "深度学习",
    "云计算",
    "大数据",
    "区块链",
    "网络安全",
    "算法面试",
    "编程入门",
    "软件开发",
    "科技新闻",
    "手机评测",
    "笔记本电脑推荐",
    "美食做法",
    "旅游景点推荐",
    "健身计划",
]


def get_browser_context():
    """连接到已运行的Edge浏览器"""
    playwright = sync_playwright().start()
    
    # 连接到已运行的浏览器（通过调试端口）
    browser = playwright.chromium.connect_over_cdp(
        f"http://localhost:{DEBUG_PORT}"
    )
    
    # 获取第一个context
    contexts = browser.contexts
    if not contexts:
        raise Exception("No browser context found")
    
    return playwright, browser, contexts[0]


def save_storage_state():
    """保存当前登录状态"""
    playwright, browser, context = get_browser_context()
    
    state_path = Path(".browser/bing_storage_new.json")
    context.storage_state(path=str(state_path))
    print(f"[OK] Login state saved to: {state_path}")
    
    playwright.stop()


def get_random_keyword(used_keywords: list = None) -> str:
    """获取一个随机关键词（避免重复）"""
    available = [k for k in DEFAULT_KEYWORDS if k not in (used_keywords or [])]
    if not available:
        # 如果都用过了，重置列表
        available = DEFAULT_KEYWORDS.copy()
    return random.choice(available)


def run_search_task(keywords: str = None, count: int = 5, delay: float = 3.0, use_random: bool = True):
    """执行搜索任务
    
    Args:
        keywords: 指定关键词，如果为None则使用随机关键词
        count: 搜索次数
        delay: 每次搜索间隔（秒）
        use_random: 是否使用随机关键词（keywords为None时生效）
    """
    # 确定搜索模式
    if keywords:
        search_mode = "fixed"
        keyword_list = [keywords] * count
    elif use_random:
        search_mode = "random"
        keyword_list = []
        used = []
        for i in range(count):
            kw = get_random_keyword(used)
            keyword_list.append(kw)
            used.append(kw)
    else:
        search_mode = "fixed"
        keyword_list = [DEFAULT_KEYWORDS[0]] * count
    
    print(f"Starting Bing search task...")
    print(f"Mode: {search_mode}")
    print(f"Search count: {count}")
    print("-" * 50)
    
    playwright, browser, context = get_browser_context()
    
    # 获取所有页面
    pages = context.pages
    if not pages:
        raise Exception("No open pages found")
    
    # 使用第一个页面（通常是Bing）
    page = pages[0]
    
    success_count = 0
    
    for i in range(count):
        keyword = keyword_list[i]
        try:
            print(f"[{i+1}/{count}] Searching: {keyword}")
            
            # 如果不在Bing页面，先跳转
            if "bing.com" not in page.url:
                page.goto("https://www.bing.com")
                time.sleep(2)
            
            # 等待搜索框出现
            page.wait_for_selector('#sb_form_q', timeout=10000)
            
            # 获取搜索框
            search_box = page.locator('#sb_form_q').first
            
            # 清除并输入
            search_box.click()
            search_box.fill("")
            search_box.type(keyword, delay=100)
            
            # 按回车搜索
            page.keyboard.press("Enter")
            
            # 等待结果加载
            time.sleep(delay)
            
            # 滚动页面（模拟真实浏览）
            for _ in range(3):
                page.mouse.wheel(0, 300)
                time.sleep(0.5)
            
            print(f"    [OK] Done")
            success_count += 1
            
            # 随机等待
            wait_time = delay + random.randint(0, 2)
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"    [ERROR] {e}")
            continue
    
    print("-" * 50)
    print(f"[OK] Task completed! Success: {success_count}/{count}")
    
    playwright.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Bing Search Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.bing_search run                    # 使用随机关键词搜索5次
  python -m scripts.bing_search run --count 10       # 搜索10次
  python -m scripts.bing_search run -k "Python" -c 3 # 指定关键词搜索3次
  python -m scripts.bing_search save                 # 保存登录状态
        """
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # 保存状态命令
    subparsers.add_parser("save", help="Save current login state")
    
    # 运行搜索命令
    run_parser = subparsers.add_parser("run", help="Run search task")
    run_parser.add_argument("-k", "--keywords", type=str, default=None, 
                          help="Search keyword (use random if not specified)")
    run_parser.add_argument("-c", "--count", type=int, default=5, 
                          help="Number of searches (default: 5)")
    run_parser.add_argument("-d", "--delay", type=float, default=3.0, 
                          help="Delay between searches in seconds (default: 3.0)")
    run_parser.add_argument("--no-random", action="store_true",
                          help="Disable random keywords mode")
    
    args = parser.parse_args()
    
    if args.command == "save":
        save_storage_state()
    elif args.command == "run":
        use_random = not args.no_random if args.keywords is None else False
        run_search_task(
            keywords=args.keywords, 
            count=args.count, 
            delay=args.delay,
            use_random=use_random
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
