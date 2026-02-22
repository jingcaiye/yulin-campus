#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS功能测试脚本
"""

from alarm_manager import AlarmManager


def test_gps():
    """测试GPS功能"""
    print("=== GPS功能测试 ===")

    # 创建闹钟管理器实例
    alarm = AlarmManager()

    # 获取当前位置
    location = alarm.get_current_location()

    print(f"当前位置信息:")
    print(f"  纬度: {location['lat']}")
    print(f"  经度: {location['lon']}")
    print(f"  海拔: {location['altitude']}")
    print(f"  精度: {location['accuracy']}")
    if 'note' in location:
        print(f"  备注: {location['note']}")

    print("\n测试完成！")


if __name__ == '__main__':
    test_gps()
