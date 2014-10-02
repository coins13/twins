twins
===
履修登録。その全てを極めるために。

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
- w3m
- Python3

インストール
-----------
```
$ git clone https://github.com/coins13/twins.git
$ cd twins
$ python3 setup.py install
```

使い方
-----
```
$ twins --help
```

用例
-----
```
# オペレーティングシステムIIを履修
$ twins reg GB31801
# 確率論を切る
$ twins unreg GB11601
# 秋Aの時間割を見る
$ twins timetable 秋A
# TwinCalでtimetable.icsを作成
$ twins reged | reged2ics > timetable.ics
# A+とった授業
$ twins stat | awk '$1 == "A+"{ print }'
# 母親にGPAを教える
$ twins sum | awk '$1 == "GPA:"{ print $2 }' | mail -s "my GPA" mom@example.com
```
