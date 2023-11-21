# -*- coding: utf-8 -*-

"""
@Project : magnifier 
@File    : database.py
@Date    : 2023/11/21 15:03:05
@Author  : zhchen
@Desc    : 
"""
import pymysql

DB = {}


def get_db(database_name: str = "show_data"):
    if database_name in DB:
        db = DB[database_name]
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT 1")
        except (pymysql.err.OperationalError, pymysql.err.InternalError):
            DB.pop(database_name)
            return get_db(database_name)
        return db

    if database_name == 'show_data':
        return pymysql.connect(
            host='rm-bp1au71v1a4zj205u4o.mysql.rds.aliyuncs.com',
            user='viewer', password="vieweR6210773768", database=database_name
        )
    else:
        raise TypeError(f"未找到{database_name}")
