twins
===
言葉に出来ない素晴らしいユーザインタフェースを持つ、某TW○NSのスクレイピングとかしてくれるすごいやつ。
T-ACTでリファクタリングしてくれると信じてる。

機能
---
- 履修登録・取り消し
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
$ git clone https://github.com/coins13/twins.git
$ cd twins
$ python3 setup.py install
```

使い方
-----
```
$ twins help
```

用例
-----
```
# オペレーティングシステムIIを履修
$ twins reg GB31801
# 確率論を切る
$ twins unreg GB11601
# TwinCalでtimetable.icsを作成
$ twins reged | reged2ics timetable.ics
# 二年生の時間割で共通するものをほぼ全て履修登録
$ ./tools/reg_all_in_standard_timetable_for2.py|xargs -n1 ./twins reg
# A+とった授業
$ twins ach|awk '$1 == "A+"{ print }'
# 母親にGPAを教える
$ twins achsum|awk '$1 == "GPA:"{ print $2 }'|mail -s "my GPA" mom@example.com
```
