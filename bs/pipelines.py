# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import  ImagesPipeline
from twisted.enterprise import adbapi
import codecs
import json
import pymysql
import pymysql.cursors
class BsPipeline(object):
    def process_item(self, item, spider):
        return item

#自定义保存json文件的pipeline
class JsonWithPipeline(object):
    def __init__(self):
        self.file=codecs.open("artile.json","w",encoding="utf8")
    def process_item(self, item, spider):
        lines=json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(lines)
        return item
    def spider_closed(self):
        self.file.close()


#scrapy提供的导出文件的pipeline
class JsonExporterPipeline:
    def __init__(self):
        self.file=open("artileexporter.json","wb")
        self.exporter = JsonItemExporter(self.file,encoding="utf8",ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self):
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self, item, spider):
        self.exporter.export_item(item=item)
        return item


#保存图片的pipeline
class jobbleImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_img_url" in item:
           for ok,value in results:
               images_file_path=value["path"]
           item["front_img_path"]=images_file_path
        return item

#将数据写入mysql（普通方法）
class MySqlPipeline(object):
    def __init__(self):
        self.conn=pymysql.connect('localhost','root','root','jobble',charset="utf8")
        self.cursor=self.conn.cursor()
    def process_item(self,item,spider):
        insert_sql="""
        insert into jobble（title，time,url_md5,url）
        values(%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["time"],item["url_md5"],item["url"]))
        self.conn.commit()


#异步写入数据到mysql
class MysqlTwistedPipeLine(object):
    def __init__(self,dbpool):
       self.dbpool=dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        db_pool=adbapi.ConnectionPool("pymysql",**dbparms)
        return cls(db_pool)
    def process_item(self,item,spider):
        query=self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)
        return item
    def handle_error(self,failure):
        #处理异步插入的异常
        print(failure)
    def do_insert(self,cursor,item):
         insert_sql="""insert into jobble(title,time,url_md5,url)values(%s,%s,%s,%s)"""
         cursor.execute(insert_sql,(item["title"],item["time"],item["url_md5"],item["url"]))

