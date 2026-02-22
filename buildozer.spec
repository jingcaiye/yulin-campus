#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Buildozer配置文件
用于将Python应用打包成Android APK

使用方法:
1. 在Linux/WSL环境下安装buildozer
2. 运行: buildozer android debug
3. 生成的APK在bin目录下
"""

# 应用名称
title = Yulin Campus

# 包名
package.name = yulin_campus

# 应用版本
package.version = 1.0.0

# 应用描述
description = 榆林学院智慧校园助手

# 作者信息
author = Matrix Agent
email = support@yulincampus.com
license = MIT

# 依赖要求（不需要kivymd了，因为已移除Card组件）
requirements = python3,kivy==2.3.0,requests,beautifulsoup4,plyer,networkx,pillow,python-dateutil

# 屏幕方向
orientation = portrait

# Android配置
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,VIBRATE,RECEIVE_BOOT_COMPLETED,WAKE_LOCK
android.api = 27
android.minapi = 21
android.accept_sdk_license = True

# Android元数据
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# 启动画面
android.presplash_color = #A80000

# 应用程序图标
android.icon.filename = icon.png

# 屏幕密度
android.densities = 160, 240, 320, 480, 640

# 打包方式
android.allow_backup = True
android.fullscreen = False

# 日志级别
log_level = 2

# 警告忽略
warning_ignore = SoftWarning

# 是否打包成独立应用
android.binpath = bin
