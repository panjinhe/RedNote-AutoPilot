#!/usr/bin/env python3
"""
Android模拟器控制工具

用于在电脑上通过ADB控制Android模拟器（蓝叠/雷电/夜神等），
实现自动化操作小红书APP。

用法示例：
    python -m scripts.android_controller --help
"""

import argparse
import os
import subprocess
import time
from pathlib import Path
from typing import Optional


# ==================== 配置 ====================
# ADB路径（如果ADB不在PATH中，需要指定完整路径）
ADB_PATH = "adb"  # 假设ADB已在PATH中

# 模拟器配置
DEFAULT_EMULATOR_PORT = 5555  # 雷电默认端口是5555，蓝叠是5554

# 小红书APP包名和活动名
XHS_PACKAGE = "com.xingin.xhs"
XHS_ACTIVITY = "com.xingin.xhs.index.v2.IndexActivityV2"
XHS_ACTIVITY_ALT = "com.xingin.xhs.index.IndexActivityV2"

# 输出目录
OUTPUT_DIR = Path("artifacts/android")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_adb_command(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """执行ADB命令"""
    cmd = [ADB_PATH] + args
    print(f"执行命令: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def get_devices() -> list[str]:
    """获取已连接的设备列表"""
    result = run_adb_command(["devices"])
    devices = []
    for line in result.stdout.strip().split("\n")[1:]:
        if line.strip() and "device" in line:
            device = line.split()[0]
            devices.append(device)
    return devices


def connect_emulator(host: str = "127.0.0.1", port: int = DEFAULT_EMULATOR_PORT) -> bool:
    """连接模拟器"""
    connect_str = f"{host}:{port}"
    print(f"尝试连接模拟器: {connect_str}")
    result = run_adb_command(["connect", connect_str])
    return "connected" in result.stdout.lower() or "already connected" in result.stdout.lower()


def disconnect_emulator(host: str = "127.0.0.1", port: int = DEFAULT_EMULATOR_PORT):
    """断开模拟器连接"""
    connect_str = f"{host}:{port}"
    result = run_adb_command(["disconnect", connect_str])
    print(result.stdout)


def install_app(apk_path: str, reinstall: bool = True) -> bool:
    """安装APK"""
    if not os.path.exists(apk_path):
        print(f"错误: APK文件不存在: {apk_path}")
        return False
    
    args = ["install"]
    if reinstall:
        args.append("-r")  # 替换已存在的应用
    args.append(apk_path)
    
    result = run_adb_command(args)
    success = "Success" in result.stdout
    if success:
        print(f"✓ APK安装成功: {apk_path}")
    else:
        print(f"✗ APK安装失败: {result.stderr}")
    return success


def uninstall_app(package_name: str) -> bool:
    """卸载APP"""
    result = run_adb_command(["uninstall", package_name])
    success = "Success" in result.stdout
    if success:
        print(f"✓ APP卸载成功: {package_name}")
    return success


def start_app(package_name: str, activity_name: str) -> bool:
    """启动APP"""
    component = f"{package_name}/{activity_name}"
    result = run_adb_command(["shell", "am", "start", "-n", component])
    success = "Starting" in result.stdout or "started" in result.stdout.lower()
    if success:
        print(f"✓ APP启动成功: {package_name}")
    else:
        print(f"启动结果: {result.stdout}")
    return True  # 即使返回不是success也尝试启动


def stop_app(package_name: str) -> bool:
    """停止APP"""
    result = run_adb_command(["shell", "am", "force-stop", package_name])
    return result.returncode == 0


def take_screenshot(filename: str = None) -> str:
    """截图"""
    if filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    filepath = OUTPUT_DIR / filename
    
    # 在模拟器中截图
    run_adb_command(["shell", "screencap", "-p", "/sdcard/screenshot.png"])
    # 拉取到本地
    run_adb_command(["pull", "/sdcard/screenshot.png", str(filepath)])
    # 删除模拟器中的截图
    run_adb_command(["shell", "rm", "/sdcard/screenshot.png"])
    
    print(f"✓ 截图已保存: {filepath}")
    return str(filepath)


def tap(x: int, y: int) -> bool:
    """模拟点击"""
    result = run_adb_command(["shell", "input", "tap", str(x), str(y)])
    return result.returncode == 0


def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
    """模拟滑动"""
    result = run_adb_command([
        "shell", "input", "swipe", 
        str(x1), str(y1), str(x2), str(y2), str(duration)
    ])
    return result.returncode == 0


def input_text(text: str) -> bool:
    """模拟输入文字"""
    # 替换特殊字符
    text = text.replace(" ", "%s")
    result = run_adb_command(["shell", "input", "text", text])
    return result.returncode == 0


def press_key(keycode: int) -> bool:
    """模拟按键"""
    result = run_adb_command(["shell", "input", "keyevent", str(keycode)])
    return result.returncode == 0


def get_screen_size() -> tuple[int, int]:
    """获取屏幕分辨率"""
    result = run_adb_command(["shell", "wm", "size"])
    output = result.stdout.strip()
    if "Physical size:" in output:
        size = output.split("Physical size:")[1].strip()
        width, height = map(int, size.split("x"))
        return width, height
    return 1080, 1920  # 默认值


def is_app_running(package_name: str) -> bool:
    """检查APP是否在运行"""
    result = run_adb_command(["shell", "ps", "-A"])
    return package_name in result.stdout


def get_app_pid(package_name: str) -> Optional[int]:
    """获取APP的进程ID"""
    result = run_adb_command(["shell", "pidof", package_name])
    pid_str = result.stdout.strip()
    if pid_str:
        return int(pid_str)
    return None


def push_file(local_path: str, remote_path: str) -> bool:
    """推送文件到模拟器"""
    if not os.path.exists(local_path):
        print(f"错误: 文件不存在: {local_path}")
        return False
    result = run_adb_command(["push", local_path, remote_path])
    return "pushed" in result.stdout.lower()


def pull_file(remote_path: str, local_path: str) -> bool:
    """从模拟器拉取文件"""
    result = run_adb_command(["pull", remote_path, local_path])
    return result.returncode == 0


# ==================== 预设操作 ====================

def open_xiaohongshu() -> bool:
    """启动小红书APP"""
    print("正在启动小红书...")
    start_app(XHS_PACKAGE, XHS_ACTIVITY)
    time.sleep(3)  # 等待APP启动
    return True


def quick_screenshot() -> str:
    """快速截图"""
    return take_screenshot()


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="Android模拟器控制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python -m scripts.android_controller list-devices      # 列出设备
    python -m scripts.android_controller connect           # 连接模拟器
    python -m scripts.android-controller screenshot        # 截图
    python -m scripts.android-controller start-xhs         # 启动小红书
    python -m scripts.android-controller tap 500 1000      # 点击坐标
    python -m scripts.android-controller input "你好"       # 输入文字
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 列出设备
    subparsers.add_parser("list-devices", help="列出已连接的设备")
    
    # 连接模拟器
    connect_parser = subparsers.add_parser("connect", help="连接模拟器")
    connect_parser.add_argument("--host", default="127.0.0.1", help="模拟器主机")
    connect_parser.add_argument("--port", type=int, default=DEFAULT_EMULATOR_PORT, help="模拟器端口")
    
    # 截图
    screenshot_parser = subparsers.add_parser("screenshot", help="截图")
    screenshot_parser.add_argument("-o", "--output", help="输出文件名")
    
    # 启动小红书
    subparsers.add_parser("start-xhs", help="启动小红书APP")
    
    # 安装APK
    install_parser = subparsers.add_parser("install", help="安装APK")
    install_parser.add_argument("apk", help="APK文件路径")
    
    # 点击
    tap_parser = subparsers.add_parser("tap", help="模拟点击")
    tap_parser.add_argument("x", type=int, help="X坐标")
    tap_parser.add_argument("y", type=int, help="Y坐标")
    
    # 输入文字
    input_parser = subparsers.add_parser("input", help="模拟输入文字")
    input_parser.add_argument("text", help="要输入的文字")
    
    # 滑动
    swipe_parser = subparsers.add_parser("swipe", help="模拟滑动")
    swipe_parser.add_argument("x1", type=int, help="起始X")
    swipe_parser.add_argument("y1", type=int, help="起始Y")
    swipe_parser.add_argument("x2", type=int, help="结束X")
    swipe_parser.add_argument("y2", type=int, help="结束Y")
    swipe_parser.add_argument("--duration", type=int, default=300, help="滑动时长(毫秒)")
    
    # 获取屏幕大小
    subparsers.add_parser("screen-size", help="获取屏幕分辨率")
    
    args = parser.parse_args()
    
    if args.command == "list-devices":
        devices = get_devices()
        print(f"已连接设备 ({len(devices)}):")
        for d in devices:
            print(f"  - {d}")
            
    elif args.command == "connect":
        if connect_emulator(args.host, args.port):
            print("✓ 连接成功")
        else:
            print("✗ 连接失败，请确保模拟器已启动")
            
    elif args.command == "screenshot":
        path = take_screenshot(args.output)
        print(f"截图保存至: {path}")
        
    elif args.command == "start-xhs":
        open_xiaohongshu()
        
    elif args.command == "install":
        install_app(args.apk)
        
    elif args.command == "tap":
        tap(args.x, args.y)
        print(f"已点击坐标: ({args.x}, {args.y})")
        
    elif args.command == "input":
        input_text(args.text)
        print(f"已输入文字: {args.text}")
        
    elif args.command == "swipe":
        swipe(args.x1, args.y1, args.x2, args.y2, args.duration)
        print(f"已滑动: ({args.x1}, {args.y1}) -> ({args.x2}, {args.y2})")
        
    elif args.command == "screen-size":
        size = get_screen_size()
        print(f"屏幕分辨率: {size[0]}x{size[1]}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
