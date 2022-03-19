import requests

url = 'https://interface.sina.cn/news/wap/fymap2020_data.d.json'


def get_data():
    response = requests.get(url)
