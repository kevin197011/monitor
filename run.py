#!/usr/bin/python
# Copyright (c) 2023 kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# https://www.zabbix.com/documentation/5.0/zh/manual/api/reference/history/object

from .lib.zabbix import Zabbix


if __name__ == '__main__':
    zbx = Zabbix()
    zbx.export_to_csv()
