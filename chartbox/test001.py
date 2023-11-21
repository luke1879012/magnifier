# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : test001.py
@Date    : 2023/11/21 14:56:48
@Author  : zhchen
@Desc    : 
"""
from random import randrange

from pyecharts import options as opts
from pyecharts.charts import Bar


def bar_test() -> Bar:
    c = (
        Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
    )
    return c
