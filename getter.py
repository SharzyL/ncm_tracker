import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from processBar import ProcessBar


def get_follows(uid, pagecount=4, headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/follows?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    uid_dict = {}
    for i in range(pagecount):
        follows = browser.find_elements_by_xpath('//*[@class="ava f-pr"]')
        for follower in follows:
            href = follower.get_attribute('href')
            nickname = follower.get_attribute('title')
            uid = re.findall(r'id=(\d+)', href)[0]
            uid_dict[nickname] = uid
        turn_page = browser.find_element_by_xpath('//*[starts-with(@class, "zbtn znxt")]')
        browser.execute_script("arguments[0].click();", turn_page)
        sleep(0.5)
    browser.quit()
    return uid_dict


def get_num(nickname, uid):
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.get("https://music.163.com/#/user/songs/rank?id=" + str(uid))
    browser.switch_to.frame("g_iframe")
    text = browser.find_element_by_css_selector('#rHeader > h4').text
    browser.quit()
    song_num = int(re.findall(r'\d+', text)[0])
    return {'uid': uid, 'nickname': nickname, 'song_num': song_num}


def get_nums(uid_dict):
    num_dict = {}
    prog_bar = ProcessBar(len(uid_dict))
    executor = ThreadPoolExecutor(max_workers=10)
    tasks = [executor.submit(prog_bar.wrap(get_num), nickname, uid) for nickname, uid in uid_dict.items()]
    for future in as_completed(tasks):
        result = future.result()
        nickname = result['nickname']
        num = result['song_num']
        num_dict[nickname] = num
    return num_dict


if __name__ == '__main__':
    uid_dict = get_follows(91540849)
    # num_dict = get_nums(uid_dict)
    # print(num_dict)
    print(uid_dict)
