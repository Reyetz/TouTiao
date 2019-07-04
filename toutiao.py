import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
import re
from MongoDB_Config import *
import pymongo
from Download_images import Download


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

class JiePai:
    def __init__(self, offset, keyword):
        self.keyword = keyword
        data = {
            'aid': '24',
            'app_name': 'web_search',
            'offset': offset,
            'format': 'json',
            'keyword': keyword,
            'autoload': 'true',
            'count': '20',
            'en_qc': '1',
            'cur_tab': '1',
            'from': 'search_tab',
            'pd': 'synthesis',
            'timestamp': '1562077015782'
        }
        key = {
            'keyword': keyword
        }
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        self.referer = 'https://www.toutiao.com/api/search/?' + urlencode(key)
        self.cookie1 = 'tt_webid=6708967229196715532; __guid=32687416.437303347852920260.1562053172253.1313; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16bb19fe06a79-02055fc4fd269a-3c604504-1fa400-16bb19fe06b483; tt_webid=6708967229196715532; csrftoken=23e8275521e5d865f0b992cc1049c8e7; s_v_web_id=18b5a3aba6c299bfd9530ee223bf850f; __tasessionId=6wyi97sb11562075923613; CNZZDATA1259612802=643110369-1562047849-https%253A%252F%252Fwww.baidu.com%252F%7C1562074849; monitor_count=18'
        self.cookie2 = 'tt_webid=6708967229196715532; tt_webid=6708967229196715532; __guid=32687416.437303347852920260.1562053172253.1313; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16bb19fe06a79-02055fc4fd269a-3c604504-1fa400-16bb19fe06b483; tt_webid=6708967229196715532; csrftoken=23e8275521e5d865f0b992cc1049c8e7; s_v_web_id=18b5a3aba6c299bfd9530ee223bf850f; CNZZDATA1259612802=643110369-1562047849-https%253A%252F%252Fwww.baidu.com%252F%7C1562053249; monitor_count=15; __tasessionId=x575bc0a71562066815625'
        self.headers1 = {
            'User-Agent': self.user_agent,
            'Referer': self.referer,
            'Cookie': self.cookie1
        }
        self.headers2 = {
            'User-Agent': self.user_agent,
            'Referer': self.referer,
            'Cookie': self.cookie2
        }
        self.url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)

    def get_page_index(self):
        try:
            response = requests.get(self.url, headers=self.headers1)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except RequestException:
            print('请求索引页失败！')

    def parse_page_index(self, html):
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                if 'article_url' in item.keys():
                    article_url = item.get('article_url')
                    target_url = re.search('http://toutiao.com/group/.*?/', article_url)
                    if target_url:
                        yield target_url.group()

    def get_page_detail(self, url):
        try:
            response = requests.get(url, headers=self.headers1)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except RequestException:
            print('请求详情页失败！')

    def parse_page_detail(self, html, url):
        title = re.search(r'<title>(.*?)</title>', html, re.S)
        if title:
            target_title = title.group(1)
            # print(target_title)
            images_pattern = re.compile(r'gallery: JSON.parse\((.*?)\),', re.S)
            detail = re.search(images_pattern, html)
            if detail:
                # print(detail)
                data = json.loads(detail.group(1))
                data = json.loads(data)
                # print(data)
                if data and 'sub_images' in data.keys():
                    sub_images = data.get('sub_images')
                    image = [item.get('url') for item in sub_images]
                    for image_file in image:
                        self.download_images(image_file, target_title)
                    result = {
                        'title': target_title,
                        'url': url,
                        'images': image
                    }
                    return result

    def download_images(self, url, image_title):
        print('正在下载。。。', url)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                Download(self.keyword).download_images(image_title, response.content)
            else:
                return None
        except RequestException:
            print('请求图片页失败！')


def save_to_mongodb(result):
    if db[MONGO_TABLE].insert(result):
        print('存储成功', result)
        return True
    else:
        return False


def main():
    a = JiePai(0, '街拍')
    html = a.get_page_index()
    # print(html)
    for url in a.parse_page_index(html):
        # print(url)
        html = a.get_page_detail(url)
        if html:
            result = a.parse_page_detail(html, url)
            if result:
                save_to_mongodb(result)


if __name__ == '__main__':
    main()