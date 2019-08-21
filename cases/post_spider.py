# coding: utf-8
"""
原作者文章: https://github.com/piglei/one-python-craftsman/blob/master/zh_CN/12-write-solid-python-codes-part-1.md 
"""

from abc import ABCMeta, abstractclassmethod
import io
import sys
from typing import Generator, List, Optional

import requests
from lxml import etree


class Post(object):
    """HN(https://news.ycombinator.com/) 上的条目

    :param title: 标题
    :param link: 链接
    :param points: 当前得分
    :param comments_cnt: 评论数
    """
    def __init__(self, title: str, link: str, points: str, comments_cnt: str):
        self.title = title
        self.link = link
        self.points = int(points)
        self.comments_cnt = int(comments_cnt)


class PostsWriter(object):
    """负责将帖子列表写入到文件
    """
    def __init__(self, fp: io.TextIOBase, title: str):
        self.fp = fp
        self.title = title

    def write(self, posts: List[Post]):
        self.fp.write(f'# {self.title}\n\n')
        # enumerate 接收第二个参数，表示从这个数开始计数（默认为 0）
        for i, post in enumerate(posts, 1):
            self.fp.write(f'> TOP {i}: {post.title}\n')
            self.fp.write(f'> 分数：{post.points} 评论数：{post.comments_cnt}\n')
            self.fp.write(f'> 地址：{post.link}\n')
            self.fp.write('------\n')


# 使用类继承实现对HN内容的过滤
class HNTopPostsSpider(object):
    """抓取HackerNews Top内容条目

    :param limit: 限制条目数，默认为 5
    """
    ITEMS_URL = 'https://news.ycombinator.com/'

    def __init__(self, limit: int = 5):
        self.limit = limit

    def fetch(self) -> Generator[Post, None, None]:
        """从HN抓取Top内容"""
        resp = requests.get(self.ITEMS_URL)

        # 使用 XPath 可以方便的从页面解析出你需要的内容，以下均为页面解析代码
        # 如果你对 xpath 不熟悉，可以忽略这些代码，直接跳到 yield Post() 部分
        html = etree.HTML(resp.text)
        items = html.xpath('//table[@class="itemlist"]/tr[@class="athing"]')
        for item in items[:self.limit]:
            node_title = item.xpath('./td[@class="title"]/a')[0]
            node_detail = item.getnext()
            points_text = node_detail.xpath('.//span[@class="score"]/text()')
            comments_text = node_detail.xpath('.//td/a[last()]/text()')[0]

            post = Post(
                title=node_title.text,
                link=node_title.get('href'),
            # 条目可能会没有评分
                points=points_text[0].split()[0] if points_text else '0',
                comments_cnt=comments_text.split()[0])
            if self.interested_in_post(post):
                yield post

    def interested_in_post(self, post: Post) -> bool:
        """判断是否应该将帖子加入结果中"""
        return True


class GithubNBloomBergHNTopPostsSpider(HNTopPostsSpider):
    """只关系来自 Github/BloomBerg 的内容"""
    def interested_in_post(self, post: Post) -> bool:
        if 'github' in post.link.lower() \
                or 'bloomberg' in post.link.lower():
            return True
        return False


# 使用依赖注入特性实现对HN内容的过滤
class PostFilter(metaclass=ABCMeta):
    """抽象类：定义如何过滤帖子结果"""
    @abstractclassmethod
    def validate(self, post: Post) -> bool:
        """判断帖子是否应该被保留"""


class HNTopPostsSpiderV2(object):
    """抓取HackerNews Top内容条目

    :param limit: 限制条目数，默认为 5
    :param post_filter: 过滤结果条目的算法，默认为保留所有
    """
    ITEMS_URL = 'https://news.ycombinator.com/'

    def __init__(self,
                 limit: int = 5,
                 post_filter: Optional[PostFilter] = None):
        self.limit = limit
        self.post_filter = post_filter

    def fetch(self) -> Generator[Post, None, None]:
        """从HN抓取Top内容"""
        resp = requests.get(self.ITEMS_URL)

        # 使用 XPath 可以方便的从页面解析出你需要的内容，以下均为页面解析代码
        # 如果你对 xpath 不熟悉，可以忽略这些代码，直接跳到 yield Post() 部分
        html = etree.HTML(resp.text)
        items = html.xpath('//table[@class="itemlist"]/tr[@class="athing"]')
        for item in items[:self.limit]:
            node_title = item.xpath('./td[@class="title"]/a')[0]
            node_detail = item.getnext()
            points_text = node_detail.xpath('.//span[@class="score"]/text()')
            comments_text = node_detail.xpath('.//td/a[last()]/text()')[0]

            post = Post(
                title=node_title.text,
                link=node_title.get('href'),
            # 条目可能会没有评分
                points=points_text[0].split()[0] if points_text else '0',
                comments_cnt=comments_text.split()[0])
            if self.post_filter.validate(post):
                yield post


class DefaultPostFilter(PostFilter):
    """保留所有帖子"""
    def validate(self, post: Post) -> bool:
        return True


class GithubPostFilter(PostFilter):
    """只关系来自 Github 的内容"""
    def validate(self, post: Post) -> bool:
        return 'github' in post.link.lower()


class GithubNBloomPostFilter(PostFilter):
    """只关系来自 Github/BloomBerg 的内容"""
    def validate(self, post: Post) -> bool:
        if 'github' in post.link.lower() or 'bloomberg' in post.link.lower():
            return True
        return False


# 利用'数据驱动'实现对HN内容的过滤
class HNTopPostsSpiderV3(object):
    """抓取HackerNews Top内容条目

    :param limit: 限制条目数，默认为 5
    :param filter_by_link_keywords: 过滤结果的关键词列表，默认为 None 不过滤
    """
    ITEMS_URL = 'https://news.ycombinator.com/'

    def __init__(self,
                 limit: int = 5,
                 filter_by_link_keywords: List[str] = None):
        self.limit = limit
        self.filter_by_link_keywords = filter_by_link_keywords

    def fetch(self) -> Generator[Post, None, None]:
        """从HN抓取Top内容"""
        resp = requests.get(self.ITEMS_URL)

        # 使用 XPath 可以方便的从页面解析出你需要的内容，以下均为页面解析代码
        # 如果你对 xpath 不熟悉，可以忽略这些代码，直接跳到 yield Post() 部分
        html = etree.HTML(resp.text)
        items = html.xpath('//table[@class="itemlist"]/tr[@class="athing"]')
        for item in items[:self.limit]:
            node_title = item.xpath('./td[@class="title"]/a')[0]
            node_detail = item.getnext()
            points_text = node_detail.xpath('.//span[@class="score"]/text()')
            comments_text = node_detail.xpath('.//td/a[last()]/text()')[0]

            post = Post(
                title=node_title.text,
                link=node_title.get('href'),
            # 条目可能会没有评分
                points=points_text[0].split()[0] if points_text else '0',
                comments_cnt=comments_text.split()[0])
            if self.filter_by_link_keywords is None:
                yield post
            elif any(keyword in post.link
                     for keyword in self.filter_by_link_keywords):
                yield post


def write_posts_to_file(posts: List[Post], fp: io.TextIOBase, title: str):
    """负责将帖子列表写入文件"""
    fp.write(f'# {title}\n\n')
    for i, post in enumerate(posts, 1):
        fp.write(f'> TOP {i}: {post.title}\n')
        fp.write(f'> 分数：{post.points} 评论数：{post.comments_cnt}\n')
        fp.write(f'> 地址：{post.link}\n')
        fp.write('------\n')


def main():
    crawler = GithubNBloomBergHNTopPostsSpider()

    posts = list(crawler.fetch())
    file_title = 'Top news on HN'
    write_posts_to_file(posts, sys.stdout, file_title)


def main_v2():
    crawler = HNTopPostsSpiderV2(post_filter=GithubNBloomPostFilter())

    posts = list(crawler.fetch())
    file_title = 'Top news on HN'
    write_posts_to_file(posts, sys.stdout, file_title)


def main_v3():
    # link_keywords = None
    link_keywords = ['github.com', 'bloomberg.com']
    crawler = HNTopPostsSpiderV3(filter_by_link_keywords=link_keywords)

    posts = list(crawler.fetch())
    file_title = 'Top news on HN'
    write_posts_to_file(posts, sys.stdout, file_title)


if __name__ == '__main__':
    main()
    main_v2()
    main_v3()
