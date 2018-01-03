#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : parse.py.py
# @Author: Kom
# @Date  : 2018/1/3
# @Desc  :


import re
from pprint import pprint

with open('station_name.html', 'r') as f:
    text = f.read()
    stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', text)
    pprint(dict(stations), indent=4)
