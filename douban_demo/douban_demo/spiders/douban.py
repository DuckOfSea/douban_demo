# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request

class DoubanSpider(scrapy.Spider):
    name = 'douban'

    def start_requests(self):
        yield Request(url='https://movie.douban.com/chart',callback=self.parse_rank)

    def parse_rank(self, response):
        for item in response.css('tr.item'):
            detail_url=item.css('a.nbg::attr(href)').get()
            img_url=item.css('a.nbg>img::attr(src)').get()
            main_name=item.css('div.pl2>a::text').get()
            other_name=item.css('div.pl2>a>span::text').get()
            brief=item.css('p.pl::text').get()
            main_name=main_name.replace('\n', '').replace(' ', '')

            yield{
                'detail_url':detail_url,
                'img_url':img_url,
                'name':main_name,
                'other_name':other_name,
                'brief':brief
            }

            yield scrapy.Request(detail_url+'comments?status=P',
                          callback=self.parse_comments,
                          meta={'movie': main_name})

    def parse_comments(self, response):
        for comments in response.css('div.comment-item'):
            username=comments.css('span.comment-info>a::text').get()
            comment=comments.css('span.short::text').get()

            yield{
                'movie':response.meta['movie'],
                'username':username,
                'comment':comment
            }

        nexturl=response.css('a.next::attr(href)').get()
        if nexturl:
            yield Request(url=response.url[:response.url.find('?')]+nexturl,
                          callback=response.parse_comments,
                          meta=response.meta)