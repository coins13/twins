#!/usr/bin/env python3
import sys
import requests
from pyquery import PyQuery as pq

sys.stderr.write("""\
***************

クラス別の授業、体育や総合科目などは自分で
登録しましょう。そこまで登録してくれるのは
AIが完成してからです。

***************
""")

d = pq(url="http://www.coins.tsukuba.ac.jp/syllabus/timetable2.html")
for a in d("a").items():
    if "_" in a.attr["href"] or not a.attr["href"].startswith("G") or \
       a.attr["href"] == "GB11926":
        continue
    print(a.attr["href"][0:7])
