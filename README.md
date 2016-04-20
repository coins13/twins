twins
=====
[![Build Status](https://travis-ci.org/coins13/twins.svg?branch=master)](https://travis-ci.org/coins13/twins)

履修。その全てを極めるために。

[![what we want](http://imgs.xkcd.com/comics/university_website.png)](https://xkcd.com/773/)

機能
---
- 履修登録・取り消し
- 時間割表示
- 科目検索
- 成績開示
- 累計成績要約 (履修単位数, 修得単位数, GPA)
- その他もろもろ

必要なもの
---------
- *nix
- Python3

インストール
-----------
```
$ pip3 install twins
```

使い方
-----
```sh
# オペレーティングシステムIIを履修
$ twins reg GB31801
# 確率論を切る
$ twins unreg GB11601
# 秋Aの時間割を見る
$ twins timetable 秋A
# 時間割をiCalendar形式で出力
$ twins ics > timetable.ics
# 秋ABで木曜4-6限にある授業を検索
$ twins search '/^木4[1-9\,\-]*$/' | grep "秋AB"
# A+とった授業
$ twins stat | awk '$1 == "A+"{ print }'
# 母親にGPAを教える
$ twins sum | awk '$1 == "GPA:"{ print $2 }' | mail -s "my GPA" mom@example.com
```
