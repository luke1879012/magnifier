# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : slide.py
@Date    : 2023/11/21 15:49:15
@Author  : zhchen
@Desc    : 
"""
from pyecharts import options as opts
from pyecharts.charts import Line

from utils.database import get_db


def slide_cnt():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""select crt_time, count from slide_count order by crt_time desc limit 1440;""")
        x_data = []
        y_data = []
        for row in cursor.fetchall():
            x_data.append(row[0].strftime("%Y-%m-%d %H:%M:%S"))
            y_data.append(row[1])
    # print(x_data)
    # print(y_data)
    l = Line().set_global_opts(
        title_opts=opts.TitleOpts(
            title="滑块数量",
            pos_left="center",
            pos_top="top",
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(pos_left="left"),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100),
            opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
        ],
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            # axistick_opts=opts.AxisTickOpts(is_show=True),
            # splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    ).add_xaxis(xaxis_data=x_data).add_yaxis(
        series_name="数量",
        y_axis=y_data,
        areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(is_show=False),
    )
    return l


if __name__ == '__main__':
    _l = slide_cnt()
    _l.render()
