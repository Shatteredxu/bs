
from  selenium import webdriver
import time
import pickle
import datetime
import json
try:
    import urlparse as parse
except:
    from urllib import parse
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
import scrapy
def start_request(self):
    browser = webdriver.Chrome(executable_path="C:/Users/Administrator/AppData/Local/Google/Chrome/Application/chromedriver.exe")
    browser.get("https://www.zhihu.com/signin")

    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper Input").send_keys("13572236079")
    browser.find_element_by_css_selector(".SignFlow-password Input").send_keys("xh520525")

    browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

    time.sleep(10)
    cookies=browser.get_cookies()
    print(cookies)
    cookie_dict={}
    for cookie in cookies:
        # 写入文件
        f = open('E:/爬虫集合/bs/bs/' + cookie['name'] + '.zhihu', 'wb')
        pickle.dump(cookie, f)
        f.close()
        cookie_dict[cookie['name']] = cookie['value']
    browser.close()
    return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
