univ
===
言葉に出来ない素晴らしいユーザインタフェースを持つ、某TW○NSのスクレイピングとかしてくれる良い奴。
誰かがいい感じにしてくれると信じてる。

機能
---
- 成績開示
- 累計成績要約 (履修単位数, 修得単位数, GPA)

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
$ univ t|awk '$1 == "A+"{ print }'   # A+とった授業
$ univ ts|awk '$1 == "GPA:"{ print $2 }'|mail -s "my GPA" mom@example.com  # 母親にGPAを教える
```
