# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : login.py
@Date    : 2023/11/24 10:39:39
@Author  : zhchen
@Desc    : 
"""
import json
from datetime import datetime

from pyecharts.commons.utils import JsCode

from utils.database import get_db


def login_status():
    from pyecharts.charts import Bar
    from pyecharts import options as opts

    stage_names = [
        '天猫', '生意', '店小蜜', '赤兔', "谛听",
        # '零售通',
        '京东',
        '抖店', '罗盘',
        # '飞鸽', '千川',
        '抖店2', '抖店cg',
        '京情', '淘情', '淘菜菜'
    ]
    values = [0 for _ in range(len(stage_names))]
    values_ns = [0 for _ in range(len(stage_names))]
    extra_info = ['' for _ in range(len(stage_names))]
    last_update_time = datetime.now()

    db = get_db()
    with db.cursor() as cursor:
        for idx, stage_name in enumerate(stage_names):
            cursor.execute(
                f"SELECT all_acc_num, ns_acc_num, detail, crt_time FROM login_status "
                f"where stage_name='{stage_name}' order by crt_time desc limit 1;")
            data = cursor.fetchone()
            if data:
                values[idx] = data[0]
                values_ns[idx] = data[1]
                _detail = json.loads(data[2])
                extra_info[idx] = "<br>".join(f"{a['accountName']} | {a['accountId']}" for a in _detail['no_session_acc_info'])
                if extra_info[idx] == "":
                    extra_info[idx] = "大吉大利"
                last_update_time = min(last_update_time, data[3])

    # 创建柱状图
    bar = Bar()

    # 添加数据
    bar.add_xaxis(stage_names)
    bar.add_yaxis(
        series_name="账号总数量",
        y_axis=values,
        itemstyle_opts=opts.ItemStyleOpts(color='rgb(145,204,117)'),
        stack="stack1"
    )
    bar.add_yaxis(
        series_name="无cookie数量",
        y_axis=values_ns,
        itemstyle_opts=opts.ItemStyleOpts(color="rgb(238,102,102)"),
        label_opts=opts.LabelOpts(
            # 使用自定义的 formatter 函数
            formatter=JsCode("""function(params){if (params.value == 0) {return ``;}return params.value;}""")
        ),
        stack="stack1"
    )

    # 设置全局配置项
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title="    登录状态",
            subtitle=last_update_time.strftime("%Y-%m-%d %H:%M:%S"),
            pos_left="center",
            pos_top="top", ),  # 标题
        tooltip_opts=opts.TooltipOpts(formatter=JsCode(
            "function(x){return [`" + "`,`".join(extra_info) + "`][x.dataIndex];}"

            # "function(x){return x.value + ' (' + " +
            # "['" + "','".join(extra_info) + "'][x.dataIndex] + ')';}"
        )),
        legend_opts=opts.LegendOpts(pos_left="left"),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                font_size=14,
                # rotate=-30,
                interval=0,
            )  # 设置 x 轴标签字体大小
        )
    )

    return bar


if __name__ == '__main__':
    l = login_status()
    c = l.dump_options()
    l.render()
