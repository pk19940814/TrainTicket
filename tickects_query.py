#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : tickects_query.py
# @Author: Kom
# @Date  : 2018/1/3
# @Desc  :

"""Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help        显示帮助菜单
    -g               高铁
    -d               动车
    -t               特快
    -k               快速
    -z               直达

Example:
    tickets 南京 北京 2016-07-01
    tickets -dg 南京 北京 2016-07-01
"""

from docopt import docopt
import requests
import station_name
import requests
from datetime import datetime
from docopt import docopt
from prettytable import PrettyTable
from colorama import Fore
from urllib3.exceptions import InsecureRequestWarning

requests.urllib3.disable_warnings(InsecureRequestWarning)


class TrainCollection(object):
    headers = '车次 车站 时间 历时 一等座 二等座 软卧 硬卧 软座 硬座 无座'.split()

    def __init__(self, raw_trains, options):
        self.raw_trains = raw_trains
        self.options = options

    def colored(self, color, string):
        return ''.join([getattr(Fore, color.upper())])

    def get_from_to_stastion_name(self, data_list):
        from_stastion_telecode = data_list[6]
        to_station_telecode = data_list[7]
        return '\n'.join([
            self.colored('green', station_name.get_name(from_stastion_telecode)),
            self.colored('red', station_name.get_name(to_station_telecode))
        ])

    def get_start_arrive_time(self, data_list):
        return '\n'.join([
            self.colored('green', data_list[8]),
            self.colored('red', data_list[9])
        ])

    def parse_train_data(self, data_list):
        return {
            'station_train_code': data_list[3],
            'from_to_station_name': self.get_from_to_stastion_name(data_list),
            'start_arrive_time': self.get_start_arrive_time(data_list),
            'history_record': data_list[10],
            'first_class_seat': data_list[31] or '--',
            'second_class_seat': data_list[30] or '--',
            'soft_sleep': data_list[23] or '--',
            'hard_sleep': data_list[28] or '--',
            'soft_seat': data_list[24] or '--',
            'hard_seat': data_list[29] or '--',
            'no_seat': data_list[33] or '--'

        }

    def need_print(self, data_list):
        station_train_code = data_list[3]
        initial = station_train_code[0].lower()
        return not self.options or initial in self.options

    @property
    def trains(self):
        for train in self.raw_trains:
            data_list = train.split('|')
            if self.need_print(data_list):
                yield self.parse_train_data(data_list).values()

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.headers)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


class Cli(object):
    url_template = (
        'https://kyfw.12306.cn/otn/leftTicket/queryO?'
        'leftTicketDTO.train_date={}&'
        'leftTicketDTO.from_station={}&'
        'leftTicketDTO.to_station={}&'
        'purpose_codes=ADULT'
    )

    def __init__(self):
        self.arguments = docopt(__doc__, version='Tickets 1.0')
        self.from_station = station_name.get_telecode(self.arguments['<from>'])
        self.to_station = station_name.get_telecode(self.arguments['<to>'])
        self.date = self.arguments['<date>']
        self.check_arguments_validity()
        self.options = ''.join([key for key, value in self.arguments.items() if value is True])

    @property
    def request_url(self):
        return self.url_template.format(self.date, self.from_station, self.to_station)

    def check_arguments_validity(self):
        if self.from_station is None or self.to_station is None:
            print(u'请输入有效的车站名称')
            exit()
        try:
            if datetime.strptime(self.date, '%Y-%m-%d') < datetime.now():
                raise ValueError
        except:
            print(u'请输入有效日期')
            exit()

    def run(self):
        r = requests.get(self.request_url, verify=False)
        trains = r.json()['data']['result']
        TrainCollection(trains, self.options).pretty_print()


if __name__ == '__main__':
    Cli().run()
