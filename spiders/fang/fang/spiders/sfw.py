# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy_redis.spiders import RedisSpider

from ..items import NewHouseItem, ESFHouseItem


class SfwSpider(RedisSpider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = 'fang:start_urls'    # 从redis该key中读取start_urls

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            province_td = tds[0]
            province_text = province_td.xpath('.//text()').get()
            province_text = re.sub(r'\s', '', province_text)
            if province_text:    # 保存省份
                province = province_text
            # 不爬取海外的房产信息
            if province == '其它':
                continue
            city_td = tds[1]
            city_links = city_td.xpath('.//a')
            for city_link in city_links:
                city = city_link.xpath('.//text()').get()
                city_url = city_link.xpath('.//@href').get()

                url_module = city_url.split('//')
                scheme = url_module[0]
                domain = url_module[1]
                city_domain = domain.split(".")
                # 新房\、二手房URL数据
                if 'bj.' in domain:
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                else:
                    newhouse_url = "{}//{}.newhouse.fang.com/house/s/".format(scheme, city_domain[0])
                    # 二手房的URL数据
                esf_url = "{}//{}.esf.fang.com/".format(scheme, city_domain[0])
                # yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse,
                #                      meta={'info': (province, city)})
                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={'info': (province, city)})

    def parse_newhouse(self, response):
        """新房页面解析"""
        province, city = response.meta.get('info')
        lis = response.xpath("//div[contains(@class, 'nl_con')]/ul/li")
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            house_type_list = li.xpath(".//div[contains(@class, 'house_type')]/a/text()").getall()
            house_type_list = list(map(lambda x: x.strip(), house_type_list))
            rooms = list(filter(lambda x: '居' in x, house_type_list))
            area = ''.join(li.xpath(".//div[contains(@class, 'house_type')]/text()").getall())
            area = re.sub(r'\s|－|/', '', area)
            address = li.xpath(".//div[@class='address']/a/@title").get()
            if name is not None and len(rooms) > 0:
                district_text = ''.join(li.xpath(".//div[@class='address']/a//text()").getall())
                district = re.search(r'.*\[(.+)\].*', district_text).group(1)
                sale = li.xpath(".//div[contains(@class, 'fangyuan')]/span/text()").get()
                price_text = ''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
                price = re.sub(r'\s|广告', '', price_text)
                origin_url = 'http:' + li.xpath(".//div[@class='nlcd_name']/a/@href").get()

                item = NewHouseItem(province=province, city=city, name=name, rooms=rooms, price=price, area=area,
                                    address=address, district=district, sale=sale, origin_url=origin_url)
                yield item
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse, meta={'info': (province, city)})

    def parse_esf(self, response):
        """二手房信息"""
        province, city = response.meta.get('info')
        dls = response.xpath("//div[contains(@class, 'shop_list')]/dl")
        for dl in dls:
            item = ESFHouseItem(province=province, city=city)
            name = dl.xpath(".//p[@class='add_shop']/a/@title").get()
            if name is not None:
                item['name'] = name
                infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
                infos = list(map(lambda x: re.sub(r'\s', '', x), infos))
                for info in infos:
                    if '厅' in info:
                        item['rooms'] = info
                    elif '层' in info:
                        item['floor'] = info
                    elif '向' in info:
                        item['toward'] = info
                    elif '年' in info:
                        item['year'] = info.replace('年建', '')
                    elif '㎡' in info:
                        item['area'] = info
                item['address'] = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                price_info = dl.xpath(".//dd[@class='price_right']/span//text()").getall()
                price = price_info[0] + price_info[1]
                if '万' in price:
                    item['price'] = price
                if '㎡' in price_info[2]:
                    item['unit'] = price_info[2]
                detail = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                item['origin_url'] = response.urljoin(detail)

                yield item
        next_url = response.xpath("//div[@class='page_al']/p[1]/a/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf, meta={'info': (province, city)})


