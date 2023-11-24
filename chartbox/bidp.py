# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : bidp.py
@Date    : 2023/11/23 16:55:33
@Author  : zhchen
@Desc    : 
"""
import random
from datetime import timedelta

from pyecharts import options as opts
from pyecharts.charts import Line

from utils.database import get_db
LIMIT = 5

def get_x_y_data(data):
    x_data = []
    y_data = []
    for i in data:
        sec = 4
        _time = i[1]
        _time_str = _time.strftime("%Y-%m-%d %H:%M:%S")
        _value = i[0]
        step = _value // 5
        # random_step = step // 3
        _value_sub = _value - step
        _value_add = _value + step * 3

        x_data.append((_time + timedelta(seconds=-sec * 2.5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value)
        x_data.append((_time + timedelta(seconds=-sec * 1.5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value)

        x_data.append((_time + timedelta(seconds=-sec * .5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value_sub)

        x_data.append((_time + timedelta(seconds=sec * .5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value_add)

        x_data.append((_time + timedelta(seconds=sec * 1.5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value)
        x_data.append((_time + timedelta(seconds=sec * 2.5)).strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(_value)
    return x_data, y_data


def bidp_api_heart():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(f"SELECT health_value, crt_time FROM bidp_api_heart order by crt_time desc limit {LIMIT};")
        data = cursor.fetchall()
        data = reversed(data)

    x_data, y_data = get_x_y_data(data)
    # print(x_data)
    # print(y_data)
    line = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="心跳", y_axis=y_data,
            label_opts=opts.LabelOpts(is_show=False), is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=4), )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="bidp心跳",
                pos_left="center",
                pos_top="top",
            ),
            xaxis_opts=opts.AxisOpts(type_="time"),
            yaxis_opts=opts.AxisOpts(type_="value"),
            legend_opts=opts.LegendOpts(pos_left="left"),
        )
    )
    return line


def bidp_api_update(last_time):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            f"SELECT health_value, crt_time FROM bidp_api_heart where crt_time > %s order by crt_time desc limit {LIMIT};",
            (last_time,))
        data = cursor.fetchall()
        if not data:
            cursor.execute("SELECT health_value, crt_time FROM bidp_api_heart order by crt_time desc limit 1;")
            data = cursor.fetchall()
    ret_data = list(zip(*get_x_y_data(data)))
    return ret_data


if __name__ == '__main__':
    # _line = bidp_api_heart()
    # _line.render()
    print(bidp_api_update("2023-11-23 17:31:35"))
