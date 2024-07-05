# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : canary.py
@Date    : 2024/7/2 11:19:04
@Author  : luke
@Desc    : 
"""
import copy
from datetime import datetime

from pymysql.cursors import DictCursor

from utils.database import get_db


def get_err_msg(msg):
    return [{
        "id": -999,
        "shovel_project": msg,
        "platform_code": msg,
        "reason": msg
    }]


def canary_query(data):
    print(f"{data=}")
    max_query_num = 4000
    fields = ["start_time", "end_time", "task_id", "category"]

    query_params = {}
    if not data:
        return get_err_msg('拒绝全量查询, 提供参数 | (╯°□°）╯︵ ┻━┻')

    # 过滤参数
    for k, v in data.items():
        if k in fields and v:
            query_params[k] = v

    # 开始时间 校验
    if not query_params.get("start_time"):
        return get_err_msg('start_time必传 | (ｏ ‵-′)ノ”(ノ﹏<。)')

    where_list = []
    where_value = []
    where_list.append("alert_time >= %s")
    where_value.append(query_params["start_time"])

    if end_time := query_params.get("end_time"):
        where_list.append("alert_time <= %s")
        where_value.append(end_time)

    if task_id := query_params.get("task_id"):
        where_list.append("task_id = %s")
        where_value.append(task_id)

    if category := query_params.get("category"):
        where_list.append("category in (" + ",".join(["%s"] * len(category)) + ")")
        where_value += category

    where_str = " and ".join(where_list)
    db = get_db("l_test")

    with db.cursor(DictCursor) as cursor:
        sql_str = f"select * from cheget where {where_str} limit {max_query_num};"
        print(f"{sql_str=}")
        print(f"{where_value=}")
        cursor.execute(sql_str, where_value)
        c_data = cursor.fetchall()
        # print(c_data)
    ret_data = []
    for row in c_data:
        copy_row = copy.deepcopy(row)
        for k, v in copy_row.items():
            if isinstance(v, datetime):
                copy_row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        ret_data.append(copy_row)

    if len(ret_data) >= max_query_num:
        return get_err_msg(f"查询结果超过{max_query_num}条 | 累死不干了 (╬▔皿▔)╯")

    return ret_data


def canary_finish(data):
    pass
