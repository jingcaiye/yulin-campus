"""
闹钟管理模块
负责课程提醒和位置获取
"""

import datetime
import time
import threading
import webbrowser
import json
import urllib.request
import urllib.parse

try:
    from plyer import notification
    from plyer import gps

    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("警告: plyer库未安装，部分功能不可用")


class AlarmManager:
    """闹钟管理器"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlarmManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if AlarmManager._initialized:
            return
        
        AlarmManager._initialized = True
        self.gps_enabled = False
        self.current_location = None

        # 尝试初始化GPS
        if PLYER_AVAILABLE:
            try:
                print("正在初始化GPS...")
                gps.configure(on_location=self.on_location)
                self.gps_enabled = True
                print("GPS初始化成功")
            except Exception as e:
                print(f"GPS初始化失败: {e}")
                print("尝试使用IP地理位置...")
                self._get_location_by_ip()
        else:
            print("plyer库不可用，尝试使用IP地理位置...")
            self._get_location_by_ip()

    def _get_location_by_ip(self):
        """通过IP获取地理位置"""
        try:
            print("正在通过IP获取位置...")
            # 使用免费的IP地理位置API
            url = "http://ip-api.com/json/"

            # 添加更详细的错误处理
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')

                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP错误: {response.status}")

                    data = json.loads(response.read().decode('utf-8'))

                    if data['status'] == 'success':
                        self.current_location = {
                            'lat': data['lat'],
                            'lon': data['lon'],
                            'altitude': 0,
                            'accuracy': 1000,  # IP定位精度较低
                            'note': f"IP定位: {data.get('city', '未知城市')}, {data.get('regionName', '未知省份')}"
                        }
                        print(f"✅ IP定位成功: {data.get('city', '未知城市')}")
                    else:
                        raise Exception(f"IP定位失败: {data.get('message', '未知错误')}")

            except urllib.error.URLError as e:
                raise Exception(f"网络连接错误: {e}")
            except json.JSONDecodeError as e:
                raise Exception(f"数据解析错误: {e}")
            except Exception as e:
                raise Exception(f"请求失败: {e}")

        except Exception as e:
            print(f"IP定位失败: {e}")
            print("将使用默认位置（榆林学院）")
            # 最后使用默认位置
            self.current_location = {
                'lat': 38.2850,
                'lon': 109.7340,
                'altitude': 0,
                'accuracy': 0,
                'note': '默认位置（榆林学院）'
            }

    def on_location(self, **kwargs):
        """GPS位置回调"""
        self.current_location = {
            'lat': kwargs.get('lat', 0),
            'lon': kwargs.get('lon', 0),
            'altitude': kwargs.get('alt', 0),
            'accuracy': kwargs.get('accuracy', 0)
        }

    def start_gps(self):
        """启动GPS定位"""
        if self.gps_enabled:
            try:
                gps.start(mindistance=1, minstatus=1)
            except:
                pass

    def stop_gps(self):
        """停止GPS定位"""
        if self.gps_enabled:
            try:
                gps.stop()
            except:
                pass

    def get_current_location(self):
        """获取当前位置"""
        if self.current_location:
            return self.current_location
        else:
            # 如果GPS未获取到位置，返回榆林学院默认位置
            default_location = {
                'lat': 38.2850,
                'lon': 109.7340,
                'altitude': 0,
                'accuracy': 0,
                'note': '默认位置（榆林学院）'
            }
            print("GPS未获取到位置，使用默认位置")
            return default_location

    def test_gps_functionality(self):
        """测试GPS功能并提供解决方案"""
        print("\n=== 位置功能测试 ===")

        # 检查当前位置信息
        if self.current_location:
            print("✅ 位置信息已获取")
            print(f"纬度: {self.current_location['lat']}")
            print(f"经度: {self.current_location['lon']}")
            print(f"位置来源: {self.current_location.get('note', '未知')}")
            print(f"精度: {self.current_location.get('accuracy', '未知')}米")

            if 'IP定位' in self.current_location.get('note', ''):
                print("\n💡 当前使用IP定位，精度较低")
                print("如需更高精度，建议:")
                print("1. 启用GPS设备")
                print("2. 确保Windows位置服务开启")
                print("3. 以管理员身份运行程序")
            elif '默认位置' in self.current_location.get('note', ''):
                print("\n⚠️  当前使用默认位置")
                print("建议检查网络连接或手动设置位置")

            return True
        else:
            print("❌ 无法获取位置信息")
            return False

    def set_manual_location(self, lat, lon, location_name="手动设置位置"):
        """手动设置位置"""
        self.current_location = {
            'lat': lat,
            'lon': lon,
            'altitude': 0,
            'accuracy': 10,  # 手动设置精度较高
            'note': location_name
        }
        print(f"✅ 手动设置位置成功: {location_name}")
        print(f"纬度: {lat}, 经度: {lon}")

    def set_yulin_location(self):
        """设置为榆林学院位置"""
        self.set_manual_location(38.2850, 109.7340, "榆林学院（手动设置）")

    def send_notification(self, title, message, course_name=None):
        """发送系统通知"""
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name='榆林学院校园助手',
                    timeout=10
                )
                print(f"通知已发送: {title} - {message}")
            except Exception as e:
                print(f"通知发送失败: {e}")
        else:
            print(f"通知（模拟）: {title} - {message}")

    def open_url(self, url):
        """打开URL"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"打开链接失败: {e}")


# ==================== 课程提醒器 ====================
class CourseReminder:
    """课程提醒器"""

    def __init__(self, database, alarm_manager):
        self.db = database
        self.alarm = alarm_manager
        self.running = False
        self.thread = None

    def start(self):
        """启动提醒服务"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._check_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """停止提醒服务"""
        self.running = False

    def _check_loop(self):
        """检查循环"""
        while self.running:
            self._check_courses()
            time.sleep(60)  # 每分钟检查一次

    def _check_courses(self):
        """检查是否有课程需要提醒"""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.weekday() + 1  # 1-7 表示周一到周日

        courses = self.db.get_all_courses()

        for course in courses:
            course_name = course[1]
            course_time = course[4]
            course_day = course[5]

            # 检查是否是同一天
            if str(course_day) != str(current_day):
                continue

            # 解析课程时间，计算提醒时间
            try:
                course_dt = datetime.datetime.strptime(course_time, "%H:%M")
                reminder_dt = course_dt - datetime.timedelta(minutes=10)
                reminder_time = reminder_dt.strftime("%H:%M")

                if current_time == reminder_time:
                    location = course[3] or "未知地点"
                    self.alarm.send_notification(
                        title="课程提醒 ⏰",
                        message=f"【{course_name}】将在10分钟后开始！\n地点: {location}"
                    )
            except Exception as e:
                print(f"时间解析错误: {e}")


# 测试代码
if __name__ == '__main__':
    alarm = AlarmManager()

    # 测试发送通知
    alarm.send_notification("测试通知", "这是一条测试消息")

    # 测试位置功能
    alarm.test_gps_functionality()

    # 演示手动设置位置
    print("\n=== 手动设置位置演示 ===")
    print("设置为榆林学院位置...")
    alarm.set_yulin_location()

    # 再次测试位置功能
    alarm.test_gps_functionality()

    # 获取最终位置
    location = alarm.get_current_location()
    print(f"\n最终位置: {location}")

    print("\n闹钟管理器测试完成")
