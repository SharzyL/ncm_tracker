import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from processBar import ProcessBar
import requests
from bs4 import BeautifulSoup

# requests headers
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_ntes_nnid=7eced19b27ffae35dad3f8f2bf5885cd,1476521011210; _ntes_nuid=7eced19b27ffae35dad3f8f2bf5885cd; usertrack=c+5+hlgB7TgnsAmACnXtAg==; Province=025; City=025; _ga=GA1.2.1405085820.1476521280; NTES_PASSPORT=6n9ihXhbWKPi8yAqG.i2kETSCRa.ug06Txh8EMrrRsliVQXFV_orx5HffqhQjuGHkNQrLOIRLLotGohL9s10wcYSPiQfI2wiPacKlJ3nYAXgM; P_INFO=hourui93@163.com|1476523293|1|study|11&12|jis&1476511733&mail163#jis&320100#10#0#0|151889&0|g37_client_check&mailsettings&mail163&study&blog|hourui93@163.com; JSESSIONID-WYYY=189f31767098c3bd9d03d9b968c065daf43cbd4c1596732e4dcb471beafe2bf0605b85e969f92600064a977e0b64a24f0af7894ca898b696bd58ad5f39c8fce821ec2f81f826ea967215de4d10469e9bd672e75d25f116a9d309d360582a79620b250625859bc039161c78ab125a1e9bf5d291f6d4e4da30574ccd6bbab70b710e3f358f%3A1476594130342; _iuqxldmzr_=25; __utma=94650624.1038096298.1476521011.1476588849.1476592408.6; __utmb=94650624.11.10.1476592408; __utmc=94650624; __utmz=94650624.1476521011.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    'DNT': '1',
    'Host': 'music.163.com',
    'Pragma': 'no-cache',
    'Referer': 'http://music.163.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}


def get_follows(uid, headless=True):
    """
    根据uid获取关注者信息

    :param uid: UID
    :param headless: 是否不显示浏览器界面，默认不显示
    :return: 由 nickname:uid 形成的字典
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/follows?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    uid_dict = {}
    while True:
        follows = browser.find_elements_by_xpath('//*[@class="ava f-pr"]')
        for follower in follows:
            href = follower.get_attribute('href')
            nickname = follower.get_attribute('title')
            uid = re.findall(r'id=(\d+)', href)[0]
            uid_dict[nickname] = uid
        turn_page = browser.find_element_by_xpath('//*[starts-with(@class, "zbtn znxt")]')
        if turn_page.get_attribute('class').endswith('disabled'):
            break
        browser.execute_script("arguments[0].click();", turn_page)
        sleep(0.2)
    browser.quit()
    return uid_dict


def get_nickname(uid, headless=True):
    """
    根据uid 获取昵称

    :param uid: UID
    :param headless: 是否不显示浏览器界面，默认不显示
    :return: 昵称
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/follows?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    nickname = browser.find_element_by_xpath('//span[@class="tit f-ff2 s-fc0 f-thide"]').text
    browser.quit()
    return nickname


def get_uid(nickname, headless=True):
    """
    根据昵称获取uid
    原理为通过在搜索界面搜索昵称，并选取第一个搜索结果，允许一定容错

    :param nickname: 昵称
    :param headless: 是否不显示浏览器界面，默认不显示
    :return: UID(str形式）
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get('https://music.163.com/#/search/m/?id=55578827&s=%s&type=1002' % nickname)
    browser.switch_to.frame("g_iframe")
    ele = browser.find_elements_by_xpath('//a[@class="txt f-fs1"]')[0]
    href = ele.get_attribute('href')
    browser.quit()
    return re.findall(r'\d+$', href)[0]


def get_num(uid):
    """
    根据UID获取某人的听歌量，由于是静态网页，可以直接用requests

    :param uid: UID
    :return: 听歌量（int形式）
    """
    params = {'id': uid}
    r = requests.get('https://music.163.com/user/songs/rank/', headers=headers, params=params)
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    body = soup.body
    ele = body.find('div', id='rHeader')  # 获取包含听歌量的 div 元素
    num = int(ele.h4.string[4:-1])  # 提取数字
    return num


def get_many(func, param_list, max_workers=20, result='list'):
    """
    一个高阶函数，将一个单变量函数 func 用线程池方式多线程调用，参数遍历param_list

    :param func: 单变量函数
    :param param_list: 参数列表
    :param max_workers: 最大多线程数
    :param result: 见 return 说明
    :return: result = 'list'  返回值的列表
             result = 'dict'  由参数和返回值构成的字典
             result = 'tuple' 由参数和返回值构成的序对的列表
    """
    result_dict = {}
    prog_bar = ProcessBar(len(param_list))
    executor = ThreadPoolExecutor(max_workers=max_workers)
    tasks = [executor.submit(prog_bar.wrap(func), param) for param in param_list]
    results = [future.result() for future in tasks]
    if result == 'list':
        return results
    elif result == 'dict':
        return dict(zip(param_list, results))
    elif result == 'tuple':
        return list(zip(param_list, results))
    else:
        raise ValueError('unknown parameter : result = ' + result)

if __name__ == '__main__':
    def task(x):
        sleep(0.1)
        return x

    param = range(10)
    print(get_many(task, param))