from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.shortcuts import render
from django.http import JsonResponse
from covidmap.models import *
import datetime
from django.core import serializers as core_serializers
import json
import requests


# Create your views here.
def china_wuhan_static(request):
    return render(request, 'china-wuhan-static.html')


def china_wuhan(request):
    from bs4 import BeautifulSoup
    from selenium import webdriver

    try:
        target = 'https://3g.dxy.cn/newh5/view/pneumonia?scene=2&clicktime=1579579384&enterid=1579579384&from=groupmessage&isappinstalled=0'
        # req = requests.get(url=target)
        # req.encoding = 'urf-8'
        # html = req.text
        option = webdriver.ChromeOptions()
        option.add_argument('headless')  # 设置option,后台运行
        driver = webdriver.Chrome(chrome_options=option)
        driver.get(target)
        js = "var q=document.documentElement.scrollTop=1500"
        driver.execute_script(js)
        selenium_page = driver.page_source
        driver.quit()
        soup = BeautifulSoup(selenium_page, 'html.parser')
        cities = soup.find('div', {'class': 'areaBox___3jZkr'})
        # 每个省
        protocols = cities.find_all('div')
        data = {}

        for i in protocols:
            try:
                first = i.find('div', {'class': 'areaBlock1___3V3UU'})
                content = first.find_all('p')
                name = content[0].get_text()
                num = content[1].get_text()
                if num == "":
                    num = 0
                data['{}'.format(name)] = num
            except AttributeError as e:
                continue
    except:
        data = {}

    protocols = ["南海诸岛", '北京', '天津', '上海', '重庆', '河南',
                 '云南', '辽宁', '黑龙江', '湖南', '安徽', '山东',
                 '新疆', '江苏', '浙江', '江西', '湖北', '广西',
                 '甘肃', '山西', '内蒙古', '吉林', '福建', '贵州',
                 '广东', '青海', '西藏', '四川', '宁夏', '海南',
                 '台湾', '香港', '澳门'
                 ]
    context = {
        'protocols': protocols,
        'data': data
    }
    return render(request, 'china-wuhan.html', context=context)


def china_wuhan_virus(request):
    if request.method == 'GET':
        import requests
        from bs4 import BeautifulSoup
        from selenium import webdriver

        target = 'https://3g.dxy.cn/newh5/view/pneumonia?scene=2&clicktime=1579579384&enterid=1579579384&from=groupmessage&isappinstalled=0'
        req = requests.get(url=target)
        req.encoding = 'urf-8'
        html = req.text
        option = webdriver.ChromeOptions()
        option.add_argument('headless')  # 设置option,后台运行
        driver = webdriver.Chrome(chrome_options=option)
        driver.get(target)
        js = "var q=document.documentElement.scrollTop=1500"
        driver.execute_script(js)
        selenium_page = driver.page_source
        driver.quit()
        soup = BeautifulSoup(selenium_page, 'html.parser')
        cities = soup.find('div', {'class': 'areaBox___3jZkr'})
        # 每个省
        protocols = cities.find_all('div')
        data = {}
        for i in protocols:
            try:
                first = i.find('div', {'class': 'areaBlock1___3V3UU'})
                content = first.find_all('p')
                name = content[0].get_text()
                num = content[1].get_text()
                if num == "":
                    num = 0
                data['{}'.format(name)] = num
                # data.append(protocol)
            except AttributeError as e:
                continue

        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def show_map_current(request):
    return render(request, 'china-covid19-map.html')


def show_line_history(request):
    return render(request, 'china-covid19-line.html')


def get_current_data_all(request):
    response = {}
    if request.method == 'GET':
        current_data_all = CovidCurrent.objects.all()
        response['list'] = json.loads(
            core_serializers.serialize("json", current_data_all, use_natural_foreign_keys=True, ensure_ascii=False))
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def get_history_data_all(request):
    response = {}
    data = []
    response['data'] = data
    if request.method == 'GET':
        current_data_all = CovidCurrent.objects.all().order_by('current_date')
        year_month_day = set()  # 设置集合，无重复元素
        for a in current_data_all:
            year_month_day.add(a.current_date)  # 把每篇文章的年、月以元组形式添加到集合中
        year_month_day = sorted(year_month_day)
        for b in year_month_day:
            each = {'date': b.strftime("%Y-%m-%d"),
                    'value': CovidCurrent.objects.filter(current_date=b).aggregate(nums=Sum('incr_confirmed'))['nums']}
            data.append(each)
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def get_data(request):
    url_name = 'https://c.m.163.com/ug/api/wuhan/app/data/list-total'
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"}
    response = requests.get(url_name, headers=send_headers)
    data = json.loads(response.text)['data']
    areaTree = data['areaTree']
    for i in areaTree:
        if i['name'] == '中国':
            for j in i['children']:
                location = Location.objects.get(name=j['name'])
                try:
                    current = CovidCurrent.objects.get(
                        location=location,
                        current_date=datetime.datetime.now().strftime("%Y-%m-%d")
                    )

                except ObjectDoesNotExist:
                    current = CovidCurrent(current_date=datetime.datetime.now().strftime("%Y-%m-%d"))
                    current.location = location

                current.incr_confirmed = j['today']['confirm'] if j['today']['confirm'] is not None else 0
                current.incr_cured = j['today']['heal'] if j['today']['heal'] is not None else 0
                current.incr_dead = j['today']['dead'] if j['today']['dead'] is not None else 0
                current.incr_suspected = j['today']['suspect'] if j['today']['suspect'] is not None else 0
                current.save()
                try:
                    history = CovidHistory.objects.get(location=location)
                    history.total_confirmed = history.total_confirmed + current.incr_confirmed
                    history.total_dead = history.total_dead + current.incr_dead
                    history.total_cured = history.total_cured + current.incr_cured
                except ObjectDoesNotExist:
                    history = CovidHistory(location=location)
                    history.total_confirmed = current.incr_confirmed
                    history.total_dead = current.incr_dead
                    history.total_cured = current.incr_cured

                history.save()

    return JsonResponse({'data': 'ok'}, json_dumps_params={'ensure_ascii': False})
