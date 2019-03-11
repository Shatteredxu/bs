# -*- coding: utf-8 -*-

import time
import pickle
import datetime
import json
import re
try:
    import urlparse as parse
except:
    from urllib import parse
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from bs.items import zhihu_answer_item
from bs.items import zhihu_question_item
import scrapy
from selenium import webdriver

class ZhihuSpider(scrapy.Spider):
    name = "zhihu_sel"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/topic#%E4%BF%A1%E6%81%AF%E6%8A%80%E6%9C%AF%EF%BC%88IT%EF%BC%89']

    #question的第一页answer的请求url
    start_answer_url ="https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"


    # headers = {
    #     ":authority": "zhihu-web-analytics.zhihu.com",
    #     ":method": "POST",
    #     ":path": "/api/v1/logs/batch",
    #     ":scheme": "https",
    #     "accept": "*/*",
    #     "accept-encoding": "gzip, deflate, br",
    #     "accept-language": "zh-CN,zh;q=0.9",
    #     "content-encoding": "gzip",
    #     "content-length": "706",
    #     "content-type": "application/x-protobuf",
    #     "origin": "https://www.zhihu.com",
    #     "referer": "https://www.zhihu.com",
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    # }
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def parse(self, response):
        url_lists=response.css(".feed-main a::attr(href)").extract();
        url_lists = [parse.urljoin(response.url, url) for url in url_lists]
        url_lists = filter(lambda x:True if x.startswith("https") else False, url_lists)
        for url in url_lists:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                #如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                #如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)
    def parse_question(self,response):
            if "QuestionHeader-title" in response.text:
                match=re.match("(.*zhihu.com/question/(\d+))(/|$)",response.url)
                if(match):
                    question_id = match.group(2)

            question_loader=ItemLoader(item=zhihu_question_item(),response=response)
            question_loader.add_css("title",".QuestionHeader-title::text")
            question_loader.add_css("content",".QuestionHeader-detail span::text")
            question_loader.add_value("zhihu_id",question_id)
            question_loader.add_css("scan_num",".NumberBoard--divider div.NumberBoard-item strong::text")
            question_loader.add_css("answer_num",".List-headerText span::text")
            question_loader.add_css("tags",".QuestionHeader-tags .TopicLink #Popover4-toggle::text")
            question_loader.add_value("url", response.url)
            question_item=question_loader.load_item()
            yield scrapy.Request(self.start_answer_url.format(question_id,20,0),headers=self.headers,callback=self.parse_answer)
            yield question_item
    def parse_answer(self,response):
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]
        for answer in ans_json["data"]:
            answer_item = zhihu_answer_item()
            answer_item["answer_id"]=answer["id"]
            answer_item["url"]=answer["url"]
            answer_item["content"] = answer["content"]
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item
            if not is_end:
                yield scrapy.Request(url=next_url,headers=self.headers,callback=self.parse_answer)
    def start_requests(self):
        browser = webdriver.Chrome(executable_path="C:/Users/Administrator/AppData/Local/Google/Chrome/Application/chromedriver.exe")
        browser.get("https://www.zhihu.com/signin")

        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper Input").send_keys("13572236079")
        browser.find_element_by_css_selector(".SignFlow-password Input").send_keys("xh520525")

        browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        time.sleep(1)
        cookies=browser.get_cookies()
        cookie_dict={}
        for cookie in cookies:
            # 写入文件
            # f = open('E:/爬虫集合/bs/bs/' + cookie['name'] + '.zhihu', 'wb')
            # pickle.dump(cookie, f)
            # f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0],dont_filter=True, headers=self.headers,cookies=cookie_dict)]
