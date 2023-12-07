# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : sche.py
@Date    : 2023/12/7 13:21:32
@Author  : zhchen
@Desc    : 
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict

from pyecharts import options as opts
from pyecharts.charts import HeatMap
from pyecharts.commons.utils import JsCode
from pymysql.cursors import DictCursor

from utils.database import get_db


def sche_run_time():
    db = get_db()
    now = datetime.now()
    today = datetime(now.year, now.month, now.day, 0, 0, 0)
    # 获取昨天的日期时间对象
    yesterday = today - timedelta(days=1)
    today_str = today.strftime('%Y-%m-%d %H:%M:%S')
    yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')

    with db.cursor(DictCursor) as cursor:
        cursor.execute(f"""
        select _type, job_code, schedule_id, time, task_id from cron_run_time 
        where apply_time > '{yesterday_str}' and apply_time < '{today_str}'
        """)
        data = cursor.fetchall()
    max_data = 0
    y_label = []
    handle_data = defaultdict(int)
    sche_data = defaultdict(str)
    for i in data:
        if i['_type'] not in y_label:
            y_label.append(i['_type'])
        for t, v in json.loads(i['time']).items():
            handle_data[f"{i['_type']}_{t}"] += v
            max_data = max(handle_data[f"{i['_type']}_{t}"], max_data)
            if sche_data[f"{i['_type']}_{t}"]:
                sche_data[f"{i['_type']}_{t}"] += f',{i["schedule_id"]}'
            else:
                sche_data[f"{i['_type']}_{t}"] += f'{i["schedule_id"]}'

    # 初始化时间为00:00
    current_time = datetime.strptime('00:00', '%H:%M')

    # 创建一个列表来存储所有分钟
    minutes = []

    # 遍历一整天的每一分钟
    while current_time < datetime.strptime('23:59', '%H:%M'):
        # 将时间格式化为HH:MM格式并加入列表
        minutes.append(current_time.strftime('%H:%M'))
        # 递增一分钟
        current_time += timedelta(minutes=1)

    # 将23:59也加入到列表中，以包含最后一分钟
    minutes.append('23:59')

    sched_ids = []
    data_all = []
    for idx2, j in enumerate(minutes):
        sche_one = []
        for idx1, i in enumerate(y_label):
            sche_one.append(sche_data[f"{i}_{j}"])
            data_all.append([idx1, idx2, handle_data[f"{i}_{j}"]])
        sched_ids.append(sche_one)

    data_all = [[d[1], d[0], d[2] or "-"] for d in data_all]
    c = (HeatMap()
    .add_xaxis(xaxis_data=minutes)
    .add_yaxis(
        series_name="have run",
        yaxis_data=y_label,
        value=data_all,
        label_opts=opts.LabelOpts(color="#fff", position="bottom", horizontal_align="50%", is_show=False),
    )
    .set_series_opts()
    .set_global_opts(
        opts.TitleOpts(
            title="昨天sche运行情况",
            pos_left="center",
            pos_top="top", ),
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        yaxis_opts=opts.AxisOpts(
            type_="category",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1),

            ),
        ),
        tooltip_opts=opts.TooltipOpts(formatter=JsCode(
            f"function(x){{return  'sche_id: '+{sched_ids}[x.data[0]][x.data[1]] + '<br>v: '+ x.data[2];}}"
        )),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, max_=max_data + 10, is_calculable=True, orient="vertical", pos_left="auto"
        ),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100),
            opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
        ],
    ))
    return c


if __name__ == '__main__':
    sche_run_time().render()
