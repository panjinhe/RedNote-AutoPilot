# 电脑运行手机APP方案 - Android模拟器指南

## 概述

由于小红书商家后台只能在手机APP上操作，我们需要通过Android模拟器在电脑上运行手机APP。

## 推荐方案

### 方案一：LDPlayer（雷电模拟器）- 推荐

**优点**：
- 免费使用
- 性能稳定
- 适合长期运行
- 支持多开

**下载**：
- 官网：https://www.ldmnq.com/
- 或在搜索引擎搜索"雷电模拟器"

**安装步骤**：
1. 下载安装包并安装
2. 打开模拟器
3. 登录Google账号（设置 -> Google账号）
4. 打开应用商店，下载"小红书"

---

### 方案二：BlueStacks（蓝叠）

**优点**：
- 最早最成熟的模拟器
- 兼容性好

**下载**：
- 官网：https://www.bluestacks.com/

---

### 方案三：Windows Subsystem for Android (WSA)

**优点**：
- 微软官方方案
- 性能好
- 集成在Windows中

**要求**：
- Windows 11 专业版
- 需要开启Hyper-V

**安装方法**：
1. 打开"设置" -> "应用" -> "可选功能"
2. 添加"Windows子系统 for Android"
3. 打开Amazon应用商店下载APP

---

## 自动化控制方案

安装好模拟器后，我们可以通过ADB（Android Debug Bridge）来自动化控制模拟器。

### 常用ADB命令

```bash
# 查看连接的设备
adb devices

# 安装APK
adb install app.apk

# 启动APP
adb shell am start -n com.xingin.xhs/com.xingin.xhs.index.v2.IndexActivityV2

# 截图
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# 推送文件到模拟器
adb push local.txt /sdcard/

# 模拟点击
adb shell input tap x y

# 模拟输入文字
adb shell input text "hello"

# 模拟按键
adb shell input keyevent 4  # 返回
adb shell input keyevent 26  # 电源
```

---

## 下一步

1. **先安装模拟器**（推荐LDPlayer）
2. **在模拟器中下载小红书APP**
3. 运行本项目提供的自动化脚本

## 模拟器设置建议

- 分辨率：建议设为 1080x1920（手机竖屏比例）
- CPU：2核
- 内存：4GB
- 开启root权限（可选，用于更高级自动化）
