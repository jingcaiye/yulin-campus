"""
信息爬取模块
负责获取榆林学院重要信息和通知
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re

# 榆林学院官网
YULIN_NEWS_URL = "http://www.yulinu.edu.cn/"
YULIN_JWC_URL = "http://jwc.yulinu.edu.cn/"  # 教务处


class YulinScraper:
    """榆林学院信息爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.timeout = 10

    def get_latest_news(self):
        """获取最新新闻"""
        news_list = []

        try:
            # 尝试访问榆林学院官网
            response = self.session.get(YULIN_NEWS_URL, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 尝试多种可能的选择器
                selectors = [
                    ('a', {'class': 'news-title'}),
                    ('a', {'class': 'title'}),
                    ('li', {'class': 'news-item'}),
                    ('div', {'class': 'news'}),
                ]

                news_items = []
                for tag, attrs in selectors:
                    news_items = soup.find_all(tag, attrs)
                    if news_items:
                        break

                # 如果没找到，尝试查找所有链接
                if not news_items:
                    news_items = soup.find_all('a', href=True)
                    news_items = [a for a in news_items if a.get_text(strip=True)]

                for item in news_items[:20]:
                    title = item.get_text(strip=True)
                    href = item.get('href', '')

                    # 过滤有效新闻标题
                    if title and len(title) > 5 and not title.startswith('http'):
                        # 处理相对URL
                        if href and not href.startswith('http'):
                            if href.startswith('/'):
                                href = YULIN_NEWS_URL + href[1:]
                            else:
                                href = YULIN_NEWS_URL + href

                        news_list.append({
                            'title': title,
                            'url': href,
                            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                            'source': '榆林学院官网'
                        })
        except Exception as e:
            print(f"获取新闻失败: {e}")
            # 返回示例数据
            news_list = self._get_sample_news()

        return news_list if news_list else self._get_sample_news()

    def get_important_notices(self):
        """获取重要通知（教务处）"""
        notices = []

        try:
            response = self.session.get(YULIN_JWC_URL, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 查找通知列表
                notice_items = soup.find_all(['a', 'li', 'div'],
                    class_=re.compile(r'notice|news|list', re.I))

                for item in notice_items[:15]:
                    title = item.get_text(strip=True)
                    href = item.get('href', '')

                    if title and len(title) > 3:
                        # 检查是否是重要通知
                        keywords = ['考试', '成绩', '放假', '通知', '报名', '竞赛', '获奖']
                        is_important = any(kw in title for kw in keywords)

                        notices.append({
                            'title': title,
                            'url': href if href.startswith('http') else YULIN_JWC_URL + href,
                            'important': is_important,
                            'date': datetime.datetime.now().strftime('%Y-%m-%d')
                        })
        except Exception as e:
            print(f"获取通知失败: {e}")

        return notices if notices else self._get_sample_notices()

    def search_news(self, keyword):
        """搜索新闻"""
        all_news = self.get_latest_news()
        results = [n for n in all_news if keyword in n['title']]
        return results

    def _get_sample_news(self):
        """获取示例新闻数据"""
        return [
            {
                'title': '榆林学院举办2024年春季运动会',
                'url': 'http://www.yulinu.edu.cn/news/1',
                'date': '2024-03-15',
                'source': '榆林学院官网'
            },
            {
                'title': '我校师生在省级技能大赛中获佳绩',
                'url': 'http://www.yulinu.edu.cn/news/2',
                'date': '2024-03-10',
                'source': '榆林学院官网'
            },
            {
                'title': '榆林学院召开2024年教学工作会议',
                'url': 'http://www.yulinu.edu.cn/news/3',
                'date': '2024-03-05',
                'source': '榆林学院官网'
            },
            {
                'title': '关于举办大学生创新创业大赛的通知',
                'url': 'http://www.yulinu.edu.cn/news/4',
                'date': '2024-03-01',
                'source': '榆林学院官网'
            },
            {
                'title': '榆林学院图书馆新增电子资源',
                'url': 'http://www.yulinu.edu.cn/news/5',
                'date': '2024-02-28',
                'source': '榆林学院官网'
            }
        ]

    def _get_sample_notices(self):
        """获取示例通知数据"""
        return [
            {
                'title': '关于2024年清明节放假的通知',
                'url': 'http://jwc.yulinu.edu.cn/notice/1',
                'important': True,
                'date': '2024-03-20'
            },
            {
                'title': '2024年上半年全国计算机等级考试报名通知',
                'url': 'http://jwc.yulinu.edu.cn/notice/2',
                'important': True,
                'date': '2024-03-15'
            },
            {
                'title': '关于开展2024年大学生创新创业训练计划项目的通知',
                'url': 'http://jwc.yulinu.edu.cn/notice/3',
                'important': True,
                'date': '2024-03-10'
            },
            {
                'title': '2023-2024学年第二学期选课通知',
                'url': 'http://jwc.yulinu.edu.cn/notice/4',
                'important': True,
                'date': '2024-01-10'
            }
        ]


# 竞赛信息（可扩展）
CONTEST_INFO = [
    {
        'name': '全国大学生数学建模竞赛',
        'description': '培养创新意识和团队协作精神',
        'url': 'https://www.mcm.edu.cn',
        'deadline': '2024-06-01'
    },
    {
        'name': '中国国际大学生创新大赛',
        'description': '激发大学生创新创业热情',
        'url': 'https://cy.ncss.org.cn',
        'deadline': '2024-05-15'
    },
    {
        'name': '全国大学生电子设计竞赛',
        'description': '提高电子设计制作能力',
        'url': 'http://www.nuedc.com.cn',
        'deadline': '2024-07-01'
    },
    {
        'name': '全国大学生英语竞赛',
        'description': '提高英语水平和应用能力',
        'url': 'https://www.chinaneccs.cn',
        'deadline': '2024-04-15'
    },
    {
        'name': '陕西省大学生程序设计竞赛',
        'description': '展示程序设计能力和创新思维',
        'url': 'https://www.xajld.com',
        'deadline': '2024-05-01'
    }
]


if __name__ == '__main__':
    scraper = YulinScraper()

    print("=" * 50)
    print("榆林学院新闻列表：")
    print("=" * 50)
    news = scraper.get_latest_news()
    for i, n in enumerate(news[:10], 1):
        print(f"{i}. {n['title']}")
        print(f"   日期: {n['date']} | 来源: {n['source']}")

    print("\n" + "=" * 50)
    print("重要通知列表：")
    print("=" * 50)
    notices = scraper.get_important_notices()
    for i, n in enumerate(notices[:10], 1):
        flag = "★" if n['important'] else " "
        print(f"{flag} {i}. {n['title']}")
        print(f"   日期: {n['date']}")
