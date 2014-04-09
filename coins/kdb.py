import os
import sys
import csv
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

        # 無いならkdbからダウンロード
        if not os.path.exists(os.path.expanduser("~/.course_list.db")):
            list_ = download_course_list()

            # ダウンロードしたのからSQLiteのデータベースを作る
            c = sqlite.connect(os.path.expanduser("~/.course_list.db"))
            c.execute('''
                        CREATE TABLE courses (
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
            self.c = sqlite.connect(os.path.expanduser("~/.course_list.db"))

        self.c.commit()

    def __enter__ (self):
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        self.c.commit()
        self.c.close()


def get_course_info (course_id):
    """ 授業情報を返す。失敗したらNone。 """

# FIXME:
#   with Kdb as db:
    if True:
        db = Kdb()
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
