# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.http import Request
import re;
from bs.items import JobbleBsItem
from utils.common import get_md5
import datetime
from bs.items import  Artile_item_loader  #scrapy提供的库来解析css
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        #获取下一页的url，交给scrapy下载
        post_nodes=response.css("""#archive .floated-thumb .post-thumb a""")#获取所有文章链接
        for post_node in post_nodes:
          img_url=post_node.css("""img::attr(src)""").extract_first("")
          post_url=post_node.css("""::attr(href)""").extract_first("")
          yield Request(url=parse.urljoin(response.url,post_url),meta={"front_img_url":img_url},callback=self.parse_detail)
        next_url=response.xpath("""//a[@class="next page-numbers"]/@href""").extract_first()
        print(parse.urljoin(response.url,next_url))
        # if next_url:
            # yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
    def parse_detail(self,response):
        front_img_url=response.meta.get("front_img_url","")
        # title = response.xpath("""//div[@class="entry-header"]//h1/text()""").extract()
        post_adds = response.xpath("""//div[@class="post-adds"]//span/text()""").extract()
        comment=post_adds[3]
        like_num=post_adds[1]
        store_num=post_adds[2]
        # time=response.xpath("""//p[@class="entry-meta-hide-on-mobile"]/text()""").extract()[0].strip()
        # item=JobbleBsItem()
        # item["url"]=response.url
        # item["title"]=title
        # item["comment"]=comment
        # item["like_num"]=like_num
        # item["store_num"]=store_num
        # try:
        #     time=datetime.datetime.strptime(time,"%Y/%m/%d").date()
        # except Exception as e:
        #     time=datetime.datetime.now().date()
        # item["time"]=time
        # item["front_img_url"]=[front_img_url]
        # item["url_md5"]=get_md5(response.url)
        #通过itemLoader加载item

        item =Artile_item_loader(item=JobbleBsItem(),response=response)#实例化itemloader
        item.add_xpath("title","""//div[@class="entry-header"]//h1/text()""")
        item.add_value("url",response.url)
        item.add_value("url_md5",get_md5(response.url))
        item.add_xpath("time","""//p[@class="entry-meta-hide-on-mobile"]/text()""")
        item.add_value("front_img_url",[front_img_url])
        item.add_value("store_num",store_num)
        item.add_value("like_num",like_num)
        item.add_value("comment",comment)
        jobble_item=item.load_item()

        yield jobble_item
