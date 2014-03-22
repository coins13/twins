TWINS Internals
---------------
- Java
- たぶんSpring Frameworkで書かれてる
- いろいろともうちょっとどうにかならんかったんですか

操作
====
あらゆることをするには`https://twins.tsukuba.ac.jp/campusweb/campussquare.do`へPOSTするだけ。
ただし、flowというくそったれなものがある。
例えば、単位修得状況照会->ダウンロード->出力 を実現するには、各々でPOSTしないとだめ。
最初のPOSTには固有の_flowIdをPOST。レスポンスはこうなる。
- 302 Moved Temporarily
- Location: 上のURL?_flowExecutionKey=ほげほげ
二番目からのPOSTは_flowExecutionKeyをform dataとして送る。

認証
====
上の「操作」とはちょっと違う。
  1. _flowIdとかパスワードとか色々詰めてPOST。
  2. 302が返ってくるのでたどる
  3. また302が返ってくるのでたどる
  4. 終わり
この後に「操作」に書いてある通りにする
