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

# 大促xlsx
KEY_DATA = [None]


def get_key_data():
    """获取大促优先级表格"""
    key_data = KEY_DATA[0]
    if key_data:
        return key_data

    import pandas as pd
    df = pd.read_excel(r'E:\github_code\magnifier\test\24年双11重点保障数据集-清单确认(终版).xlsx',
                       sheet_name="24年双11大促_重点保障数据集对应采集表(终版)")
    df2 = df[df['路径id'].notna()]
    df3 = df2[['路径id', '数据集等级', '采集表']]
    df3.fillna('', inplace=True)
    path_id2level = {}
    for idx, row in df3.iterrows():
        # print(row)
        table_name = row['采集表']
        path_id = row['路径id']
        if isinstance(path_id, str) and not path_id.isdigit():
            continue
        sell_level_str = row['数据集等级']
        if 'P0' in sell_level_str:
            sell_level = 0
        elif 'P1' in sell_level_str:
            sell_level = 1
        elif 'P2' in sell_level_str:
            sell_level = 2
        elif 'P3' in sell_level_str:
            sell_level = 3
        else:
            sell_level = None
        path_id2level[path_id] = sell_level
    KEY_DATA[0] = path_id2level
    return path_id2level


def get_err_msg(msg):
    return [{
        "id": -999,
        "shovel_project": msg,
        "platform_code": msg,
        "reason": msg
    }]


def canary_query(data):
    print(f"canary_query {data=}")
    max_query_num = 4000
    fields = [
        "start_time", "end_time", "task_id", "category", "is_ok", "search_user",
        "search_shovel_name", "search_account_name",
    ]

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

    if search_user := query_params.get("search_user"):
        where_list.append("request_user in (" + ",".join(["%s"] * len(search_user)) + ")")
        where_value += search_user

    if is_ok := query_params.get("is_ok"):
        if is_ok == '1':
            where_list.append("finish_time is not null")
        elif is_ok == '-1':
            where_list.append("finish_time is null")

    if search_shovel_name := query_params.get("search_shovel_name"):
        where_list.append("shovel_name = %s")
        where_value.append(search_shovel_name)

    if search_account_name := query_params.get("search_account_name"):
        where_list.append("account_name like %s")
        where_value.append(search_account_name + "%")

    where_str = " and ".join(where_list)
    db = get_db("l_test")

    with db.cursor(DictCursor) as cursor:
        sql_str = f"select * from cheget where {where_str} limit {max_query_num};"
        print(f"{sql_str=}")
        print(f"{where_value=}")
        cursor.execute(sql_str, where_value)
        c_data = cursor.fetchall()
        # print(c_data)
    path_id2level = get_key_data()
    ret_data = []
    for row in c_data:
        copy_row = copy.deepcopy(row)
        for k, v in copy_row.items():
            if isinstance(v, datetime):
                copy_row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        copy_row["level"] = path_id2level.get(int(copy_row['path_id']))
        ret_data.append(copy_row)

    if len(ret_data) >= max_query_num:
        return get_err_msg(f"查询结果超过{max_query_num}条 | 累死不干了 (╬▔皿▔)╯")

    return ret_data


def canary_finish(data):
    print(f"canary_finish {data=}")
    send_data = data.get("send_data")
    if not send_data:
        return []
    finish_reason = data.get("finish_reason", '')

    done_lst = []
    ing_lst = []
    for data in send_data:
        if int(data['id']) < 0:
            return []

        if data['is_ok']:  # 勾选完成
            if data['finish_time']:  # 有结束时间
                pass  # 以前就完成了，跳过
            else:  # 没有结束时间
                done_lst.append(str(data['id']))
        else:  # 没勾选完成
            if data['finish_time']:  # 删除勾选按钮
                ing_lst.append(str(data['id']))
            else:
                pass  # 以前就没勾选，跳过

    if done_lst:
        db = get_db("l_test")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db.cursor() as cursor:
            sql_str = (f"UPDATE cheget SET finish_time = '{now}', finish_reason='{finish_reason}' "
                       f"WHERE id in ({','.join(done_lst)});")
            print(f"done_lst: {sql_str=}")
            cursor.execute(sql_str)
            db.commit()

    if ing_lst:
        db = get_db("l_test")
        with db.cursor() as cursor:
            sql_str = f"UPDATE cheget SET finish_time = null WHERE id in ({','.join(ing_lst)});"
            print(f"ing_lst: {sql_str=}")
            cursor.execute(sql_str)
            db.commit()

    return []


if __name__ == '__main__':
    from pprint import pprint

    query_data = {'task_id': '', 'start_time': '2024-09-10 00:00:00', 'end_time': '',
                  'category': ['Cookie Invalidated', 'Sliding Required', 'BiDp Open Api Unreachable',
                               'Leqee EE Open Api Error', 'Shovel Error', 'Shovel Not Found',
                               'Elihu Open Api Unreachable', 'Third Service Error', 'Target Resource Lost'],
                  'is_ok': '1', 'search_user': ['zhchen8'], 'search_shovel_name': 'EvaluateListDailyShovel', 'search_account_name': ''}
    result_data = canary_query(query_data)
    pprint(result_data)
