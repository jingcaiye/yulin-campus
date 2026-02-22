"""
榆林学院智慧校园助手 - 主程序
Yulin Smart Campus Assistant

功能：
1. 登录界面
2. 课表管理 + 课前10分钟提醒
3. 榆林学院重要信息获取
4. 竞赛项目储存
5. 重要通知提醒
6. 校园地图 + 导航
"""

import os
import sys
import threading
import time
import datetime
from dateutil import parser as date_parser

# 禁用Kivy多线程警告
os.environ["KIVY_NO_CONSOLELOG"] = "1"
# 无显示器环境配置
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "disk")

from kivy import Config

Config.set("graphics", "multisamples", "0")
Config.set("graphics", "vsync", "0")

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock, mainthread
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.scrollview import ScrollView

# 导入自定义模块
from database import Database
from alarm_manager import AlarmManager
from scraper import YulinScraper

# 颜色配置 - 榆林学院主题色
THEME_COLOR = "#A80000"  # 榆林学院红
THEME_COLOR_LIGHT = "#CC3333"
THEME_COLOR_DARK = "#800000"
WHITE = "#FFFFFF"
GRAY = "#F5F5F5"
DARK_GRAY = "#333333"
BLACK = "#000000"


# ==================== 登录界面 ====================
class LoginScreen(Screen):
    """登录界面"""

    username = ObjectProperty(None)
    password = ObjectProperty(None)
    remember_me = BooleanProperty(False)
    error_msg = StringProperty("")

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.db = Database()
        self.load_saved_credentials()

    def load_saved_credentials(self):
        """加载保存的登录信息"""
        saved = self.db.get_setting("saved_username")
        if saved:
            self.username.text = saved
            self.remember_me = True

    def on_login(self):
        """处理登录"""
        username = self.username.text.strip()
        password = self.password.text.strip()

        if not username or not password:
            self.error_msg = "请输入用户名和密码"
            return

        # 验证登录（本地数据库验证）
        if self.db.verify_user(username, password):
            # 保存记住的账号
            if self.remember_me:
                self.db.save_setting("saved_username", username)
            else:
                self.db.delete_setting("saved_username")

            # 保存当前用户
            self.db.save_setting("current_user", username)

            # 切换到主界面
            self.manager.current = "main"
            self.manager.get_screen("main").update_user_info(username)
            self.error_msg = ""
        else:
            self.error_msg = "用户名或密码错误"


# ==================== 主界面 ====================
class MainScreen(Screen):
    """主界面"""

    username = StringProperty("")

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.db = Database()

    def update_user_info(self, username):
        """更新用户信息"""
        self.username = username


# ==================== 课表界面 ====================
class ScheduleScreen(Screen):
    """课表管理界面"""

    course_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScheduleScreen, self).__init__(**kwargs)
        self.db = Database()
        self.load_courses()

    def load_courses(self):
        """加载课表"""
        courses = self.db.get_all_courses()
        self.course_list.data = [
            {
                "course_name": c[1],
                "teacher": c[2],
                "location": c[3],
                "time": c[4],
                "day_of_week": c[5],
            }
            for c in courses
        ]

    def add_course(self, name, teacher, location, time_slot, day):
        """添加课程"""
        self.db.add_course(name, teacher, location, time_slot, day)
        self.load_courses()

    def delete_course(self, course_name):
        """删除课程"""
        self.db.delete_course(course_name)
        self.load_courses()


# ==================== 信息中心界面 ====================
class InfoScreen(Screen):
    """信息中心 - 竞赛 + 通知"""

    news_list = ObjectProperty(None)
    contest_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.db = Database()
        self.scraper = YulinScraper()
        self.load_contests()
        self.refresh_news()

    def refresh_news(self):
        """刷新新闻"""
        threading.Thread(target=self._fetch_news, daemon=True).start()

    def _fetch_news(self):
        """后台获取新闻"""
        news = self.scraper.get_latest_news()

        @mainthread
        def update():
            self.news_list.data = [
                {"title": n["title"], "url": n["url"], "date": n["date"]}
                for n in news[:20]
            ]

        update()

    def load_contests(self):
        """加载竞赛列表"""
        contests = self.db.get_all_contests()
        self.contest_list.data = [
            {"name": c[1], "description": c[2], "url": c[3], "deadline": c[4]}
            for c in contests
        ]

    def add_contest(self, name, description, url, deadline):
        """添加竞赛"""
        self.db.add_contest(name, description, url, deadline)
        self.load_contests()


# ==================== 地图界面 ====================
class MapScreen(Screen):
    """校园地图与导航"""

    current_location = StringProperty("正在获取位置...")
    destination = ObjectProperty(None)
    route_info = StringProperty("请输入目的地开始导航")

    def __init__(self, **kwargs):
        super(MapScreen, self).__init__(**kwargs)
        self.alarm_manager = AlarmManager()
        self.db = Database()
        self.campus_locations = self._get_campus_locations()
        self.current_lat = 38.2850  # 榆林学院默认坐标
        self.current_lon = 109.7340

    def _get_campus_locations(self):
        """获取校园地点坐标"""
        return {
            "东门": {"lat": 38.2860, "lon": 109.7350, "building": "东门"},
            "南门": {"lat": 38.2840, "lon": 109.7340, "building": "南门"},
            "西门": {"lat": 38.2855, "lon": 109.7320, "building": "西门"},
            "北门": {"lat": 38.2870, "lon": 109.7335, "building": "北门"},
            "教学楼A": {"lat": 38.2855, "lon": 109.7345, "building": "教学楼A"},
            "教学楼B": {"lat": 38.2858, "lon": 109.7348, "building": "教学楼B"},
            "图书馆": {"lat": 38.2862, "lon": 109.7342, "building": "图书馆"},
            "体育馆": {"lat": 38.2845, "lon": 109.7335, "building": "体育馆"},
            "食堂": {"lat": 38.2852, "lon": 109.7338, "building": "食堂"},
            "宿舍楼1": {"lat": 38.2848, "lon": 109.7352, "building": "宿舍楼1"},
            "宿舍楼2": {"lat": 38.2846, "lon": 109.7355, "building": "宿舍楼2"},
            "行政楼": {"lat": 38.2865, "lon": 109.7338, "building": "行政楼"},
            "实验楼": {"lat": 38.2850, "lon": 109.7355, "building": "实验楼"},
        }

    def update_location(self):
        """更新当前位置"""
        location = self.alarm_manager.get_current_location()
        if location:
            if "note" in location and "默认位置" in location["note"]:
                self.current_location = "使用默认位置（榆林学院）"
            else:
                self.current_location = (
                    f"纬度: {location['lat']:.4f}, 经度: {location['lon']:.4f}"
                )

            self.current_lat = location["lat"]
            self.current_lon = location["lon"]
        else:
            self.current_location = "位置获取失败，使用默认位置（榆林学院）"

    def plan_route(self):
        """规划路线"""
        dest_name = self.destination.text.strip()
        if not dest_name:
            self.route_info = "请输入目的地"
            return

        # 查找目的地
        dest = self.campus_locations.get(dest_name)
        if not dest:
            # 尝试模糊匹配
            for name, loc in self.campus_locations.items():
                if dest_name in name or name in dest_name:
                    dest = loc
                    dest_name = name
                    break

        if dest:
            # 计算距离（简化版，实际应使用真实算法）
            import math

            dist = (
                math.sqrt(
                    (self.current_lat - dest["lat"]) ** 2
                    + (self.current_lon - dest["lon"]) ** 2
                )
                * 111
            )  # 粗略转换为公里

            # 简单路径规划
            if dist < 0.5:
                route = "步行约 {:.0f} 米".format(dist * 1000)
            else:
                route = "步行约 {:.1f} 公里".format(dist)

            self.route_info = f"目的地: {dest_name}\n{route}\n预计时间: {int(dist * 1000 / 80)} 分钟 (步行)"
        else:
            self.route_info = f"未找到地点: {dest_name}\n请从以下地点选择: {', '.join(self.campus_locations.keys())}"


# ==================== 个人中心界面 ====================
class ProfileScreen(Screen):
    """个人中心"""

    username = StringProperty("")
    notification_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.db = Database()
        self.alarm_manager = AlarmManager()
        self.load_settings()

    def load_settings(self):
        """加载设置"""
        user = self.db.get_setting("current_user")
        if user:
            self.username = user
        notif = self.db.get_setting("notification_enabled")
        self.notification_enabled = notif != "False"

    def on_switch_notification(self, instance, value):
        """开关通知"""
        self.notification_enabled = value
        self.db.save_setting("notification_enabled", str(value))

    def logout(self):
        """退出登录"""
        self.manager.current = "login"


# ==================== 屏幕管理器 ====================
class MyScreenManager(ScreenManager):
    pass


# ==================== 主应用类 ====================
class YulinCampusApp(App):
    """主应用"""

    title = "榆林学院智慧校园"

    def __init__(self, **kwargs):
        super(YulinCampusApp, self).__init__(**kwargs)
        self.db = Database()
        self.alarm_manager = AlarmManager()

    def build(self):
        # 引用所有自定义Screen类，确保它们在KV文件加载前被注册
        _ = (
            LoginScreen,
            MainScreen,
            ScheduleScreen,
            InfoScreen,
            MapScreen,
            ProfileScreen,
            MyScreenManager,
        )

        # 启动后台闹钟检查
        Clock.schedule_interval(self.check_alarms, 60)  # 每分钟检查一次

        # 加载UI
        return Builder.load_file("yulin_campus.kv")

    def check_alarms(self, dt):
        """检查并触发闹钟"""
        if not self.db.get_setting("notification_enabled"):
            return

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.weekday() + 1  # 1-7 表示周一到周日

        # 检查是否有课程需要提醒
        courses = self.db.get_all_courses()
        for course in courses:
            course_name = course[1]
            course_time = course[4]
            course_day = course[5]

            # 检查是否是同一天
            if str(course_day) != str(current_day):
                continue

            # 解析课程时间
            try:
                course_dt = datetime.datetime.strptime(course_time, "%H:%M")
                reminder_dt = course_dt - datetime.timedelta(minutes=10)
                reminder_time = reminder_dt.strftime("%H:%M")

                if current_time == reminder_time:
                    self.alarm_manager.send_notification(
                        title="课程提醒",
                        message=f"【{course_name}】将在10分钟后开始！",
                        course_name=course_name,
                    )
            except:
                continue

    def on_pause(self):
        """应用暂停时保持运行"""
        return True

    def on_resume(self):
        """应用恢复"""
        pass


# ==================== 程序入口 ====================
if __name__ == "__main__":
    try:
        print("启动榆林学院智慧校园助手...")
        YulinCampusApp().run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序发生未处理的异常: {e}")
        print("详细错误信息:")
        import traceback

        traceback.print_exc()
        print("\n可能的原因:")
        print("1. Kivy窗口创建失败")
        print("2. 图形驱动程序问题")
        print("3. KV文件语法错误")
        print("4. 缺少必要的依赖库")
    finally:
        print("程序已退出")
