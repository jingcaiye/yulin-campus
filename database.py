"""
数据库模块 - SQLite本地存储
负责用户、课程、竞赛等数据的持久化存储
"""

import sqlite3
import os

DATABASE_NAME = 'yulin_campus.db'


class Database:
    """数据库操作类"""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()

        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 课程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                teacher TEXT,
                location TEXT,
                time_slot TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 竞赛表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        self.conn.commit()

        # 创建默认用户（如果不存在）
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # 添加默认测试用户
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                          ('student', '123456'))
            self.conn.commit()

    # ==================== 用户操作 ====================
    def verify_user(self, username, password):
        """验证用户登录"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, password))
        return cursor.fetchone() is not None

    def create_user(self, username, password):
        """创建新用户"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                          (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    # ==================== 课程操作 ====================
    def add_course(self, course_name, teacher, location, time_slot, day_of_week):
        """添加课程"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO courses (course_name, teacher, location, time_slot, day_of_week)
            VALUES (?, ?, ?, ?, ?)
        ''', (course_name, teacher, location, time_slot, day_of_week))
        self.conn.commit()

    def get_all_courses(self):
        """获取所有课程"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses ORDER BY day_of_week, time_slot')
        return cursor.fetchall()

    def get_courses_by_day(self, day_of_week):
        """获取某天的课程"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses WHERE day_of_week = ? ORDER BY time_slot',
                      (day_of_week,))
        return cursor.fetchall()

    def delete_course(self, course_name):
        """删除课程"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM courses WHERE course_name = ?', (course_name,))
        self.conn.commit()

    # ==================== 竞赛操作 ====================
    def add_contest(self, name, description, url, deadline):
        """添加竞赛"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO contests (name, description, url, deadline)
            VALUES (?, ?, ?, ?)
        ''', (name, description, url, deadline))
        self.conn.commit()

    def get_all_contests(self):
        """获取所有竞赛"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contests ORDER BY deadline')
        return cursor.fetchall()

    def delete_contest(self, contest_id):
        """删除竞赛"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM contests WHERE id = ?', (contest_id,))
        self.conn.commit()

    # ==================== 设置操作 ====================
    def save_setting(self, key, value):
        """保存设置"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                      (key, value))
        self.conn.commit()

    def get_setting(self, key, default=None):
        """获取设置"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else default

    def delete_setting(self, key):
        """删除设置"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        self.conn.commit()

    def close(self):
        """关闭数据库"""
        self.conn.close()


# 测试代码
if __name__ == '__main__':
    db = Database()
    print("数据库初始化成功！")

    # 测试添加课程
    db.add_course('Python程序设计', '张老师', '教学楼A301', '08:00', 1)
    print("课程添加成功")

    # 测试获取课程
    courses = db.get_all_courses()
    print(f"共有 {len(courses)} 门课程")

    # 测试添加竞赛
    db.add_contest('全国大学生数学建模竞赛', '含金量高的竞赛', 'https://www.mcm.edu.cn', '2024-06-01')
    print("竞赛添加成功")

    db.close()
