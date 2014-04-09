univ
===
言葉に出来ない素晴らしいユーザインタフェースを持つ、某TW○NSのスクレイピングとかしてくれる良い奴。
誰かがいい感じにしてくれると信じてる。

機能
---
- 成績開示
- 履修登録・取り消し
- 科目検索
- 累計成績要約 (履修単位数, 修得単位数, GPA)
- その他もろもろ

必要なもの
---------
- *nix
- Python3

インストール
-----------
```
# git clone https://github.com/coins13/univ.git
# pip3 install -r requirements.txt
# python3 setup.py install
```

使い方
-----
```
$ univ help
```

用例
-----
```
$ univ reg GB31801  # オペレーティングシステムIIを履修
$ univ unreg GB10214  # 1,2クラス向け線形代数IIを切る
$ ./tools/reg_all_in_standard_timetable_for2.py|xargs -n1 ./univ reg  # 二年生の時間割で共通するものを全て履修登録
$ univ ach|awk '$1 == "A+"{ print }'   # A+とった授業
$ univ achsum|awk '$1 == "GPA:"{ print $2 }'|mail -s "my GPA" mom@example.com  # 母親にGPAを教える
```
