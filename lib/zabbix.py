# Copyright (c) 2023 kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import time
import datetime
import csv
import pymysql


class Zabbix:

    def __init__(self,
                 group_name='project_app',
                 start_date='20220914',
                 end_date='20221015',
                 csv_filename='/tmp/zabbix.csv',
                 zabbix_host='localhost',
                 zabbix_user='zabbix',
                 zabbix_password='zabbix_password',
                 zabbix_database='zabbix'
                 ) -> None:
        self.group_name = group_name
        self.start_date = start_date
        self.end_date = end_date
        self.csv_filename = csv_filename
        self.zabbix_host = zabbix_host
        self.zabbix_user = zabbix_user
        self.zabbix_password = zabbix_password
        self.zabbix_database = zabbix_database

    def __unix_time(self, date) -> int:
        return int(round(time.mktime(datetime.strptime(date, "%Y%m%d").timetuple())))

    def __sql_executor(self, sql) -> list:
        db = pymysql.connect(host=self.zabbix_host,
                             user=self.zabbix_user,
                             password=self.zabbix_password,
                             database=self.zabbix_database)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
        return data

    def zabbix_items(self) -> list:
        sqlStr = f'''
            select i.itemid, i.name, h.host from items i
            inner join hosts h on h.hostid = i.hostid  where i.`hostid`
            in (select hostid from hosts_groups where groupid
            in (select groupid from hstgrp where name = {self.group_name}))
            and i.name like '%Bytes sent'
        '''
        return self.__sql_executor(sqlStr)

    def zabbix_hosts_items(self) -> dict:
        value_mapper = {}
        for item in self.zabbix_items():
            if value_mapper.has_key(item[2]):
                value_mapper[item[2]].add(item[0])
                continue
            value_mapper[item[2]] = {item[0]}
        return value_mapper

    def zabbix_host_traffic(self, item_id: int) -> dict:
        sqlStr = f'''
            select sum(value) from history_uint where
            itemid = {item_id} and clock between {self.__unix_time(self.start_date)}
            and {self.__unix_time(self.end_date)}
        '''
        return self.__sql_executor(sqlStr)

    def export_to_csv(self) -> None:
        _header = ['host', 'bytes', 'gb']
        with open(self.csv_filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(_header)
            for k, v in self.zabbix_hosts_items().items():
                # print("host {}".format(k))
                val = 0
                for i in v:
                    ret = self.zabbix_host_traffic(i)[0][0]
                    if not (ret is None):
                        val = val + int(self.zabbix_host_traffic(i)[0][0])
                print("host[{}] => value[{}] GB[{}]".format(
                    k, val, float(val)/1024/1024/1024))
                writer.writerow([k, val, float(val)/1024/1024/1024])
