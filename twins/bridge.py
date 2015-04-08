import os
import sys
import json
import requests
from pyquery import PyQuery as pq
import twins.kdb

CACHE_FILE = os.path.expanduser("~/.bridge_courses.json")
TIMETABLE_URL = "http://www.stb.tsukuba.ac.jp/~zdk/bridge/timetable.html"

class Bridge:
    def __init__ (self):
        if not os.path.exists(CACHE_FILE):
            self.download(CACHE_FILE)
        self.courses = json.load(open(CACHE_FILE))

    def download (self, out):
        sys.stderr.write("BRIDGEから科目情報をダウンロード中...\n")
        html = requests.get(TIMETABLE_URL).text

        # 科目一覧を抽出するおまじない
        c_names = []
        for l in filter(lambda l: l.lstrip().startswith('<a href="detail.html?id='), html.split("\n")):
            c_names.append(l.strip().rstrip("<br /></a>").split(">", 2)[1])

        # ["GBxxxxxx", "GAxxxxxx", ...] という感じにする
        cs = []
        kdb = twins.kdb.Kdb()
        for name in set(c_names):
            try:
                info = kdb.normal_search(name)[0]
            except IndexError:
                sys.stderr.write("{0}: kdbでの検索に失敗 (無視)\n".format(name))
            else:
                cs.append(info["id"])

        with open(out, "w") as out:
            json.dump(cs, out)


if __name__ == "__main__":
    Bridge()
