# coding: utf-8
import csv
from urllib.parse import urlparse, parse_qs
import requests
from pyquery import PyQuery as pq

TWINS_URL = "https://twins.tsukuba.ac.jp/campusweb/campussquare.do"

class AuthError (Exception):
  pass

class RequestError (Exception):
  pass


class Twins:
    """
      世界初のTwinsのライブラリ for Python。
      Twinsの機能のサポートは `get_achievements()` とかを参考に、`req()` 一つで実装できるはず。
      セッションIDなどのcokkieは`self.s` (RequestsのSessionオブジェクト)に入ってる。
    """
    def __init__ (self, username, password):
        self.auth(username, password)

    def post (self, payload, with_exec_key=False):
        if with_exec_key:
             payload["_flowExecutionKey"] = self.exec_key

        r = self.s.post(TWINS_URL, params=payload, allow_redirects=False)
        self.exec_key = parse_qs(urlparse(r.headers.get("location")).query)["_flowExecutionKey"]
        r = self.s.get(r.headers.get("location"), allow_redirects=False)
        return r

    def start_flow (self, flowId):
        return self.post({ "_flowId": flowId }, False)

    def follow_flow (self, req):
        return self.post(req, True)

    def req (self, flowId, reqs=None):
        r = self.start_flow(flowId)
        if reqs is None: return r
        for req in reqs:
            r = self.follow_flow(req)
        return r


    def auth (self, username, password):
        payload = {
                    "userName": username,
                    "password": password,
                    "_flowId": "USW0009000-flow",
                    "locale": "ja_JP"
                  }

        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.2; もっとまともなUIにして欲しいです。 Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/328900893021.0.1667.0 Safari/537.36"})

        # 302を返したら成功。200はエラー。作った人は2xxの意味知らないのかな。
        r = s.post(TWINS_URL, data=payload, allow_redirects=False)
        if r.status_code == 200: raise AuthError("username or password is incorrect")
        if r.status_code != 302: raise AuthError("behavior of twins may changed (auth #1)")

        # リダイレクトその1
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 302: raise AuthError("behavior of twins may changed (auth #2)")

        # リダイレクトその2
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 200: raise AuthError("behavior of twins may changed (auth #3)")

        # authentificated!
        self.s = s


    def register_course (self, course_id):
        """ 履修申請する。返り値がTrueだったら成功"""
        course_id = course_id.toupper()

        # 曜日と時限。たぶん適当で大丈夫。
        weekday = 3
        period  = 3
        r = self.req("RSW0001000-flow", [{
                                           "_eventId": "input",
                                           "yobi":     weekday,
                                           "jigen":    period
                                         },{
                                           "nendo": "",
                                           "jikanwariShozokuCode": "",
                                           "jikanwariCode": course_id,
                                           "dummy": ""
                                         }])

        errmsg = pq(html)(".error").text()
        if errmsg != "":
           raise RequestError(errmsg)


    def get_registered_courses (self):
        r = self.req("RSW0001000-flow", [{
                                           "_eventId": "output"
                                         },{
                                           "_eventId":         "output",
                                           "outputType":       "csv",
                                           "fileEncoding":     "UTF8",
                                           "logicalDeleteFlg": 0
                                         }])

        return list(csv.reader(r.text.split("\n")))


    def get_achievements_summary (self):
        """ 履修成績要約の取得 (累計)"""
        r = self.req("SIW0001200-flow")
        # 楽しいスクレイピング
 
        # XXX
        ret = {}
        k = ""
        for d in pq(r.text)("td"):
            if d.text is None: continue
            if k != "":
                # 全角英字ダメゼッタイ
                if k == "ＧＰＡ": k = "GPA"
                ret[k] = d.text.strip()
                k = ""
                continue
            k = d.text.strip()
            if k == "履修単位数" or k == "修得単位数" or k == "ＧＰＡ":
                continue
            else:
                k = ""

        return ret


    def get_achievements (self):
        r = self.req("SIW0001200-flow", [{
                                           "_eventId":      "output",
                                           "nendo":         2013,
                                           "gakkiKbnCd":    "B",
                                           "spanType":      0,
                                           "_displayCount": 100
                                         },{
                                           "_eventId":         "output",
                                           "outputType":       "csv",
                                           "fileEncoding":     "UTF8",
                                           "logicalDeleteFlg": 0
                                         }])

        d = list(csv.reader(r.text.split("\n")))
        k,vs = d[0], d[1:]
        k = list(map(lambda s: s.strip(), k))
        return [ dict(zip(k, v)) for v in vs ]
