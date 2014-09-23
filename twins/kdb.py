import os
import sys
import csv
import time
from sqlalchemy import Column, Integer, String, Float, or_, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests
from twins.misc import *

DB_URL = "sqlite:///{0}/.course_list.db".format(os.path.expanduser("~"))
Base = declarative_base()

class Course (Base):
    __tablename__ = "courses"
    id_       = Column(Integer, primary_key=True, autoincrement=True)
    id        = Column(String)
    title     = Column(String)
    credit    = Column(String)
    target_yr = Column(String)
    modules   = Column(String)
    periods   = Column(String)
    room      = Column(String)
    teachers  = Column(String)
    desc      = Column(String)
    notes     = Column(String)
    crauditor = Column(String)  # 科目履修生
    reason    = Column(String)  # よくわからん

    def __init__ (self, id, title, credit, target_yr, modules, periods, room,
                  teachers, desc, notes, crauditor, reason):
        self.id        = id
        self.title     = title
        self.credit    = credit
        self.target_yr = target_yr
        self.modules   = modules
        self.periods   = periods
        self.room      = room
        self.teachers  = teachers
        self.desc      = desc
        self.notes     = notes
        self.crauditor = crauditor
        self.reason    = reason


class DownloadError (Exception):
    pass

def download_course_list ():
     r = requests.post("https://kdb.tsukuba.ac.jp", headers={"Accept-Language": "ja"},
           data={"action": "downloadList", "hdnFy": get_nendo(), "cmbDwldtype": "csv"})

     if r.status_code != 200:
       raise DownloadError

     return list(csv.reader(r.content.decode("shift_jis").strip().split("\n")))


def open_db (url):
    engine = create_engine(url)
    db = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    return db

class Kdb:
    """ Kernel DeBugger じゃあないよ """
    def __init__ (self):

        dbfile = os.path.expanduser("~/.course_list.db")
        # 無いかダウンロードしてから１か月経った場合にkdbからダウンロード
        if not os.path.exists(dbfile) or (time.time() - os.path.getctime(dbfile)) > 3600*30:
            list_ = download_course_list()

            if os.path.exists(dbfile):
                os.unlink(dbfile)

            # ダウンロードしたのからデータベースを作る
            self.db = open_db(DB_URL)
            for l in list_:
                     self.db.add(Course(*l))
        else:
            self.db = open_db(DB_URL)

        self.db.commit()

    def __enter__ (self):
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        self.db.commit()

    def search_by_id (self, course_id):
        return vars(self.db.query(Course).filter(Course.id == course_id).one())

    def search (self, query):
        all = self.db.query(Course).filter(or_(
                Course.id.like('%{0}%'.format(query)),
                Course.title.like('%{0}%'.format(query)),
                Course.credit.like('%{0}%'.format(query)),
                Course.modules.like('%{0}%'.format(query)),
                Course.periods.like('%{0}%'.format(query)),
                Course.room.like('%{0}%'.format(query)),
                Course.desc.like('%{0}%'.format(query)),
                Course.notes.like('%{0}%'.format(query))
              )).all()

        matched = []
        for c in all:
            matched.append(vars(c))
        return matched


def get_course_info (course_id):
    """ 授業情報を返す。失敗したらNone。 """

    with Kdb() as db:
        return db.search_by_id(course_id)

if __name__ == "__main__":
    try:
        Kdb()
    except DownloadError:
        sys.exit("failed")
    print("saved to ~/.course_list.db")
