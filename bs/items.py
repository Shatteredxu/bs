# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
import scrapy

def add_jobble(val):
    return val+"jobble"

#格式化时间
def fromat_time(val):
    try:
        time=datetime.datetime.strptime(val,"%Y/%m/%d").date()
    except Exception as e:
        time=datetime.datetime.now().date()
    return time

#添加正则转换（以后补上）
def get_nums(val):
    return val

#添加标签过滤
def remove_tag(val):
    return  val
def return_val(val):
    return val
class Artile_item_loader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()

class JobbleBsItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field(
        input_processor=MapCompose(add_jobble)
    )
    store_num= scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment=scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    url=scrapy.Field()#文章链接
    url_md5=scrapy.Field()#url的链接
    like_num=scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    time=scrapy.Field(
        input_processor=MapCompose(fromat_time),
    )#创建时间
    front_img_path=scrapy.Field(

    )#本地url存储路径
    front_img_url=scrapy.Field(
        output_processor = MapCompose(return_val)
    )#封面图的网络url
    tag=scrapy.Field(
        input_processor=MapCompose(remove_tag),
        output_processor=Join(",")#将默认的覆盖
    )
    content=scrapy.Field()

class zhihu_question_item(scrapy.Item):
     zhihu_id=scrapy.Field();
     url=scrapy.Field();
     content=scrapy.Field();
     title=scrapy.Field();
     answer_num=scrapy.Field();
     scan_num=scrapy.Field();
     crawl_time=scrapy.Field();
     tags=scrapy.Field();

class zhihu_answer_item(scrapy.Item):
     answer_id=scrapy.Field();
     url=scrapy.Field();
     create_time=scrapy.Field();
     voteup_count=scrapy.Field();
     content=scrapy.Field();
     comments_num=scrapy.Field();
     crawl_time=scrapy.Field();
