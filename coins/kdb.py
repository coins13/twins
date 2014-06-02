import os
import sys
import csv
import time
import sqlite3 as sqlite
import requests
from coins.misc import *

class DownloadError (Exception):
    pass

def download_course_list ():
     r = requests.post("https://kdb.tsukuba.ac.jp", headers={"Accept-Language": "ja"},
           data={"action": "downloadList", "hdnFy": get_nendo(), "cmbDwldtype": "csv"})

     if r.status_code != 200:
       raise DownloadError

     return list(csv.reader(r.content.decode("shift_jis").strip().split("\n")))



class Kdb:
    """ Kernel DeBugger じゃあないよ """
    def __init__ (self):

        dbfile = os.path.expanduser("~/.course_list.db")
        # 無いかダウンロードしてから１か月経った場合にkdbからダウンロード
        if not os.path.exists(dbfile) or (time.time() - os.path.getctime(dbfile)) > 3600*30:
            list_ = download_course_list()

            if os.path.exists(dbfile):
                os.unlink(dbfile)

            # ダウンロードしたのからSQLiteのデータベースを作る
            c = sqlite.connect(dbfile)
            c.execute('''
                        CREATE VIRTUAL TABLE courses USING fts4 (
                                               id text,
                                               title text,
                                               credit real,
                                               target_yr text,
                                               modules text,
                                               periods text,
                                               room text,
                                               teachers text,
                                               desc text,
                                               notes text,
                                               kamoku_rishu_sei text, -- よくわからん
                                               reason text -- よくわからん
                                             )
                      ''')
            for l in list_:
                     c.execute("INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", l)
            self.c = c
        else:
            self.c = sqlite.connect(dbfile)

        self.c.commit()

    def __enter__ (self):
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        self.c.commit()
        self.c.close()

    def search (self, query):
        keys = "id,title,credit,modules,periods,room,desc,notes"
        # FIXME: SQL injectionするアホ対策が必要
        sql  = "SELECT %s FROM courses WHERE " % keys
        sql += " OR ".join([k + " LIKE '%" + query + "%'" for k in keys.split(",")])
        matched = []
        for c in self.c.execute(sql).fetchall():
            matched.append({k: v for k,v in zip(keys.split(","), c) })
        return matched


def get_course_info (course_id):
    """ 授業情報を返す。失敗したらNone。 """

    with Kdb() as db:
        keys = "id,title,credit,modules,periods,room,desc,notes"
        cur = db.c.execute("SELECT %s FROM courses WHERE id=?" % keys, (course_id,))
        l = cur.fetchone()

        if l is None:
            return None
        return {k: v for k,v in zip(keys.split(","), l) }

if __name__ == "__main__":
    try:
        Kdb()
    except DownloadError:
        sys.exit("failed")
    print("saved to ~/.course_list.db")
