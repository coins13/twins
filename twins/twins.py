# coding: utf-8
import re
import csv
from urllib.parse import urlparse, parse_qs
import requests
from pyquery import PyQuery as pq

import twins.kdb
from twins.misc import get_nendo

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

    def get (self, payload, **get_args):
        payload["_flowExecutionKey"] = self.exec_key
        r = self.s.get(TWINS_URL, params=payload, allow_redirects=False)
        self.exec_key = parse_qs(urlparse(r.headers.get("location")).query) \
                          ["_flowExecutionKey"][0]
        r = self.s.get(r.headers.get("location"), allow_redirects=False)
        return r

    def post (self, payload, with_exec_key=False):
        if with_exec_key:
            payload["_flowExecutionKey"] = self.exec_key

        r = self.s.post(TWINS_URL, params=payload, allow_redirects=False)
        self.exec_key = parse_qs(urlparse(r.headers.get("location")).query) \
                          ["_flowExecutionKey"][0]
        r = self.s.get(r.headers.get("location"), allow_redirects=False)
        return r

    def start_flow (self, flowId):
        return self.post({"_flowId": flowId}, False)

    def follow_flow (self, req):
        return self.post(req, True)

    def req (self, flowId, reqs=None):
        r = self.start_flow(flowId)
        if reqs is None:
            return r
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
        s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.2; " +
                          "Win64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                          "Chrome/328900893021.0.1667.0 Safari/537.36"})

        # 302を返したら成功。200はエラー。作った人は2xxの意味知らないのかな。
        r = s.post(TWINS_URL, data=payload, allow_redirects=False)
        if r.status_code == 200:
            raise AuthError("ユーザ名かパスワードが違う")
        if r.status_code != 302:
            raise AuthError("ついにTWINSの仕様変更が来た")

        # リダイレクトその1
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 302:
            raise AuthError("ついにTWINSの仕様変更が来た")

        # リダイレクトその2
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 200:
            raise AuthError("ついにTWINSの仕様変更が来た")

        # 連絡確認フォームが出てきたら中断する
        if r.text.find("renrakusakiUpdateForm") != -1:
            raise AuthError("Webブラウザから連絡先確認をしよう")

        # 認証できた
        self.s = s

    def get_timetable_html (self, module):
        """ TWINSの表に教室情報を追加したHTMLを返す。"""
        if not module.startswith("春") and \
           not module.startswith("秋"):
            raise RequestError()
        module_code, gakkiKbnCode = {
                                      "春A": (1, "A"),
                                      "春B": (2, "A"),
                                      "春C": (3, "A"),
                                      "秋A": (4, "B"),
                                      "秋B": (5, "B"),
                                      "秋C": (6, "B")
                                    }.get(module)

        self.req("RSW0001000-flow")
        r = self.get({
                       "_eventId":   "search",
                       "moduleCode": module_code,
                       "gakkiKbnCode": gakkiKbnCode
                    })
        html = r.text[r.text.find("<!-- ===== 全体テーブル(開始) ===== -->"):
                      r.text.find("<!-- ===== 全体テーブル(終了) ===== -->")]

        # 要らないところを削る
        for x in ["集中講義を登録", "未登録",
                  "春A", "春B", "春C", "秋A", "秋B", "秋C", "夏休", "春休"]:
            html = html.replace(x, "")

        # 教室情報を追加する
        for c in self.get_registered_courses():
            if c["room"] != "":
                room = "(<span class='room'>%s</span>)" % c["room"]
            else:
                room = ""
            html = html.replace(c["id"], c["id"] + "</a><br>" + room)

        # 色を変える
        for from_, to in (("#dddddd", "#deded9"), ("#ffcc99", "#c4efff"),
                          ("#00bfff", "#fefefe")):
            html = html.replace(from_, to)
        return """
<!DOCTYPE html>
<head>
<meta charset="utf-8">
<title>時間割 (%(module)s)</title>
<style>
body { font-family: sans-serif; background: #fff; color: #343434; }
a{ color: #3f3f3f; text-decoration: none; }
.rishu-etc-head, .rishu-koma-head { background: #6a8cc7; }
</style>
</head><body>
<h2>%(module)s 時間割</h2>
%(html)s
</body></html>
""" % locals()

    def register_course (self, course_id):
        """ 履修申請する """

        # 何モジュール開講か取得
        kdb = twins.kdb.Kdb()
        first_module = kdb.get_course_info(course_id)["modules"][:2]
        if not first_module.startswith("春") and \
           not first_module.startswith("秋"):
            raise RequestError()
        module_code, gakkiKbnCode = {
                                      "春A": (1, "A"),
                                      "春B": (2, "A"),
                                      "春C": (3, "A"),
                                      "秋A": (4, "B"),
                                      "秋B": (5, "B"),
                                      "秋C": (6, "B")
                                    }.get(first_module)

        self.req("RSW0001000-flow")
        self.get({
                   "_eventId":   "search",
                   "moduleCode": module_code,
                   "gakkiKbnCode": gakkiKbnCode
                })
        self.post({
                    "_eventId": "input",
                    "yobi":     "1",
                    "jigen":    "1"
                 }, True)
        r = self.post({
                        "_eventId": "insert",
                        "nendo": get_nendo(),
                        "jikanwariShozokuCode": "",
                        "jikanwariCode": course_id,
                        "dummy": ""
                     }, True)

        errmsg = pq(r.text)(".error").text()
        if errmsg != "":
            raise RequestError()

    def unregister_course (self, course_id):
        """ 履修申請を取り消す """
        course_id = course_id.upper()

        # 何モジュール開講か取得
        kdb = twins.kdb.Kdb()
        first_module = kdb.get_course_info(course_id)["modules"][:2]
        if not first_module.startswith("春") and \
           not first_module.startswith("秋"):
            raise RequestError()
        module_code, gakkiKbnCode = {
                                      "春A": (1, "A"),
                                      "春B": (2, "A"),
                                      "春C": (3, "A"),
                                      "秋A": (4, "B"),
                                      "秋B": (5, "B"),
                                      "秋C": (6, "B")
                                    }.get(first_module)

        # 履修登録照会画面から時限、曜日とかを取り出す
        courses = {}
        self.req("RSW0001000-flow")
        r = self.get({
                       "_eventId":   "search",
                       "moduleCode": module_code,
                       "gakkiKbnCode": gakkiKbnCode
                     })

        for js_args in re.findall("DeleteCallA\(([\'\ \,A-Z0-9]+)\)", r.text):
            js_args = js_args.replace("'", "").split(",")
            if js_args[2] in courses:
                continue  # 1-2限,2-3限など、連続してあるやつ
            courses[js_args[2]] = {
                                    "yobi":  js_args[3],
                                    "jigen": js_args[4],
                                    "nendo": js_args[0],
                                    "jikanwariShozokuCode": js_args[1]
                                  }

        if course_id not in courses:
            raise RequestError()

        r = self.post({
                        "_eventId": "delete",
                        "yobi":     courses[course_id]["yobi"],
                        "jigen":    courses[course_id]["jigen"],
                        "nendo":    courses[course_id]["nendo"],
                        "jikanwariShozokuCode": courses[course_id]
                                                  ["jikanwariShozokuCode"],
                        "jikanwariCode": course_id,
                      }, True)

        r = self.post({"_eventId": "delete"}, True)

        errmsg = pq(r.text)(".error").text()
        if errmsg != "":
            raise RequestError()

    def get_registered_credits (self):
        """ 登録単位数合計の取得 """

        self.req("RSW0001000-flow")
        r = self.get({
                       "_eventId":     "search",
                       "moduleCode":   1,
                       "gakkiKbnCode": "A"
                   })
        html = r.text

        # XXX
        for l in html.split("\n"):
            if "単位</td>" in l:
                return float(l.strip().replace('<td align="center">', "").
                                       replace("単位</td>", ""))

        return 0.  # FIXME

    def get_registered_courses (self):
        """ 履修登録済み授業を取得 """
        kdb = twins.kdb.Kdb()
        _reged = []
        for x in ((1, "A"), (2, "A"), (3, "A"), (4, "B"), (5, "B"), (6, "B")):
            self.req("RSW0001000-flow")
            self.get({
                       "_eventId":     "search",
                       "moduleCode":   x[0],
                       "gakkiKbnCode": x[1]
                    })
            self.post({"_eventId": "output"}, True)
            r = self.post({
                            "_eventId":         "output",
                            "outputType":       "csv",
                            "fileEncoding":     "UTF8",
                            "logicalDeleteFlg": 0
                          }, True)

            _reged += list(csv.reader(r.text.strip().split("\n")))

        if _reged == []:
            return []

        already_appeared = []
        reged = []
        for c in [kdb.get_course_info(c[0]) for c in _reged]:
            # 重複を除去
            if c is None or c["id"] in already_appeared:
                continue
            reged.append(c)
            already_appeared.append(c["id"])
        return reged

    def get_achievements_summary (self):
        """ 履修成績要約の取得 (累計)"""
        r = self.req("SIW0001200-flow")

        # XXX
        ret = {}
        k = ""
        for d in pq(r.text)("td"):
            if d.text is None:
                continue
            if k != "":
                # 全角英字ダメゼッタイ
                if k == "ＧＰＡ":
                    k = "GPA"
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
                                           "nendo":         get_nendo(),
                                           "gakkiKbnCd":    "B",
                                           "spanType":      0,
                                           "_displayCount": 100
                                         }, {
                                           "_eventId":         "output",
                                           "outputType":       "csv",
                                           "fileEncoding":     "UTF8",
                                           "logicalDeleteFlg": 0
                                         }])

        d = list(csv.reader(r.text.rstrip().split("\n")))
        k, vs = d[0], d[1:]
        k = list(map(lambda s: s.strip(), k))
        return [dict(zip(k, v)) for v in vs]
