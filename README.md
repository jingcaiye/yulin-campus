# 榆林学院智慧校园助手

基于Python + Kivy开发的跨平台校园应用

## 功能特点

- **登录系统** - 学生账号登录，支持记住密码
- **智能课表** - 上传/管理课表，课前10分钟自动提醒
- **资讯中心** - 实时获取榆林学院重要通知和新闻
- **竞赛管理** - 储存各类大学生竞赛信息和报名链接
- **校园地图** - 显示校园位置，支持导航路线规划
- **个人中心** - 账户管理和设置

## 技术栈

- **Python 3.9+** - 开发语言
- **Kivy 2.1.0** - 跨平台GUI框架
- **KivyMD** - Material Design风格组件
- **SQLite** - 本地数据存储
- **Requests + BeautifulSoup** - 网络爬虫
- **Plyer** - 系统功能调用（GPS、通知）

## 环境配置

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 在PyCharm中运行

1. 打开项目文件夹
2. 设置Python解释器
3. 运行 `main.py`

## 项目结构

```
yulin_campus/
├── main.py              # 主程序入口
├── database.py          # 数据库模块
├── alarm_manager.py     # 闹钟提醒模块
├── scraper.py           # 信息爬取模块
├── yulin_campus.kv      # UI界面文件
├── buildozer.spec       # Android打包配置
├── requirements.txt     # 依赖列表
└── README.md            # 项目说明
```

## 使用说明

### 登录
- 默认账号: `student`
- 默认密码: `123456`

### 课表管理
1. 点击"课表"标签
2. 点击"+ 添加"按钮
3. 输入课程名称、教师、地点、时间和星期

### 资讯浏览
- "资讯"标签显示最新新闻
- 点击新闻标题可查看详情

### 地图导航
1. 点击"地图"标签
2. 点击"定位"获取当前位置
3. 输入目的地（如：教学楼A、图书馆）
4. 点击"规划路线"查看导航信息

## 打包部署

### Windows桌面版

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

生成的 `dist/main.exe` 即可运行

### Android移动版

需要在Linux环境下操作：

```bash
# 安装buildozer
pip install buildozer

# 初始化
buildozer init

# 打包APK
buildozer android debug
```

生成的APK在 `bin/` 目录下

## 界面预览

- **主题色**: 榆林学院红 (#A80000)
- **风格**: Material Design
- **布局**: 底部导航 + 卡片式内容

## 注意事项

1. GPS定位功能在真机上效果更好
2. 课表提醒需要保持应用在后台运行
3. 爬虫功能依赖网络连接
4. 如遇到问题，检查Python环境是否正确配置

## 许可证

MIT License

---

*本项目仅供学习交流使用*
