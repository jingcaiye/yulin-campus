#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化测试程序 - 用于诊断Kivy黑屏问题
"""

import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    def build(self):
        print("构建测试界面...")
        layout = BoxLayout(orientation='vertical')
        label = Label(text='测试界面 - 如果你看到这个说明Kivy工作正常', 
                     font_size='20sp',
                     color=(1, 1, 1, 1))
        layout.add_widget(label)
        return layout

if __name__ == '__main__':
    try:
        print("启动测试程序...")
        TestApp().run()
    except Exception as e:
        print(f"测试程序异常: {e}")
        import traceback
        traceback.print_exc()
