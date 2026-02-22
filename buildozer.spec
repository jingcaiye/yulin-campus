[app]
title = Yulin Campus
package.name = yulin_campus
version = 1.0.0
description = 榆林学院智慧校园助手
author = Matrix Agent
email = support@yulincampus.com
license = MIT
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy==2.3.0,requests,beautifulsoup4,plyer,networkx,pillow,python-dateutil,cython
orientation = portrait

[android]
permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,VIBRATE,RECEIVE_BOOT_COMPLETED,WAKE_LOCK
api = 27
minapi = 21
accept_sdk_license = True
sdk_build_tools = 33.0.2
meta_data = com.google.android.gms.version=@integer/google_play_services_version
presplash_color = #A80000
icon.filename = icon.png
densities = 160, 240, 320, 480, 640
allow_backup = True
fullscreen = False
binpath = bin

[buildozer]
log_level = 2
warning_ignore = SoftWarning
