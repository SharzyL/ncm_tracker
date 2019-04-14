import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from processBar import ProcessBar


def format_nickname(nickname):
    return re.sub(r'\W', '_', nickname)


def get_follows(uid, headless=True):
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
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/songs/rank?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    text = browser.find_element_by_css_selector('#rHeader > h4').text
    browser.quit()
    song_num = int(re.findall(r'\d+', text)[0])
    return song_num


def get_many(func, param_list):
    result_dict = {}
    prog_bar = ProcessBar(len(param_list))
    executor = ThreadPoolExecutor(max_workers=20)
    tasks = [executor.submit(prog_bar.wrap(func), param) for param in param_list]
    for future in as_completed(tasks):
        result = future.result()
        param = result[0]
        value = result[-1]
        result_dict[param] = value
    return result_dict
