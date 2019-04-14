import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from processBar import ProcessBar


def format_nickname(nickname):
    """
    由于sql里不允许在列名中出现中划线，故需要把nickname中的中划线转为下划线才能作列名
    :param nickname: 昵称
    :return: 将标点全部转化为下划线后的昵称
    """
    return re.sub(r'\W', '_', nickname)


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
    根据UID获取某人的听歌量
    :param uid: UID
    :return: 听歌量（int形式）
    """
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/songs/rank?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    text = browser.find_element_by_css_selector('#rHeader > h4').text
    browser.quit()
    song_num = int(re.findall(r'\d+', text)[0])
    return song_num


def get_many(func, param_list, max_workers=20):
    """
    一个高阶函数，将一个单变量函数 func 用线程池方式多线程调用，参数遍历param_list
    :param func: 单变量函数
    :param param_list: 参数列表
    :param max_workers: 最大多线程数
    :return: 由 param:result 构成的字典
    """
    result_dict = {}
    prog_bar = ProcessBar(len(param_list))
    executor = ThreadPoolExecutor(max_workers=max_workers)
    tasks = [executor.submit(prog_bar.wrap(func), param) for param in param_list]
    for future in as_completed(tasks):
        result = future.result()
        param = result[0]
        value = result[-1]
        result_dict[param] = value
    return result_dict
