import os
import re
import sys
import csv
import time
from sqlalchemy import Column, Integer, String, or_, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
import requests
from twins.misc import get_nendo

DB_URL = "sqlite:///{0}/.course_list.db".format(os.path.expanduser("~"))
Base = declarative_base()


class Course (Base):
    __tablename__ = "courses"
    id_       = Column(Integer, primary_key=True, autoincrement=True)
    id        = Column(String)
    title     = Column(String)
    method    = Column(String)  # 授業方法: 謎の数字
    credit    = Column(String)
    target_yr = Column(String)
    modules   = Column(String)
    periods   = Column(String)
    room      = Column(String)
    teachers  = Column(String)
    desc      = Column(String)
    remarks   = Column(String)
    crauditor = Column(String)  # 科目履修生
    reason    = Column(String)  # よくわからん
    title_en  = Column(String)  # 授業名 (英語)
    datetime  = Column(String)  # 謎の日時: "YYYY-MM-DD h:m:s"

    def __init__ (self, id, title, method, credit, target_yr, modules,
                  periods, room, teachers, desc, remarks, crauditor,
                  reason, title_en, datetime):
        self.id        = id
        self.title     = title
        self.method    = method
        self.credit    = credit
        self.target_yr = target_yr
        self.modules   = modules
        self.periods   = periods
        self.room      = room
        self.teachers  = teachers
        self.desc      = desc
        self.remarks   = remarks
        self.crauditor = crauditor
        self.reason    = reason
        self.title_en  = title_en
        self.datetime  = datetime


class DownloadError (Exception):
    pass


def download_course_list ():
    r = requests.post("https://kdb.tsukuba.ac.jp",
                      headers={"Accept-Language": "ja"},
                      data={"action": "downloadList", "hdnFy": get_nendo(),
                            "cmbDwldtype": "csv"})

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
        if not os.path.exists(dbfile) or \
               (time.time() - os.path.getctime(dbfile)) > 3600 * 30:
            sys.stderr.write("科目情報をダウンロード中...\n")

            list_ = download_course_list()

            if os.path.exists(dbfile):
                os.unlink(dbfile)

            # ダウンロードしたのからデータベースを作る
            sys.stderr.write("科目情報データベースを作成中...\n")
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
        try:
            v = self.db.query(Course). \
                        filter(Course.id == course_id.upper()). \
                        one()
        except NoResultFound:
            return None
        else:
            return vars(v)


    def normal_search (self, query):
        all = self.db.query(Course).filter(or_(
                Course.id.like('%{0}%'.format(query)),
                Course.title.like('%{0}%'.format(query)),
                Course.credit.like('%{0}%'.format(query)),
                Course.modules.like('%{0}%'.format(query)),
                Course.periods.like('%{0}%'.format(query)),
                Course.room.like('%{0}%'.format(query)),
                Course.desc.like('%{0}%'.format(query)),
                Course.remarks.like('%{0}%'.format(query))
              )).all()

        matched = []
        for c in all:
            matched.append(vars(c))
        return matched

    def regex_search (self, regex):
        matched = []
        for c in self.db.query(Course).yield_per(16):
            for v in vars(c).values():
                if regex.search(str(v)):
                    matched.append(vars(c))
                    break
        return matched

    def search (self, query):
        if query.startswith("/") and query.endswith("/"):
            try:
                regex = re.compile(query.rstrip("/").lstrip("/"))
            except Exception as e:
                sys.exit("twins: invalid regex: {0}".format(e))
            return self.regex_search(regex)
        else:
            return self.normal_search(query)


    def get_course_info (self, course_id):
        """ 授業情報を返す。失敗したらNone。 """
        return self.search_by_id(course_id.upper())
