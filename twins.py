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

    def req (self, flowId, reqs):
        self.start_flow(flowId)
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

        # twins will return 302
        r = s.post(TWINS_URL, data=payload, allow_redirects=False)
        if r.status_code == 200: raise AuthError("username or password is incorrect")
        if r.status_code != 302: raise AuthError("behavior of twins may changed (auth #1)")

        # follow redirect #1
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 302: raise AuthError("behavior of twins may changed (auth #2)")

        # follow redirect #2
        r = s.get(r.headers.get("location"), allow_redirects=False)
        if r.status_code != 200: raise AuthError("behavior of twins may changed (auth #3)")

        # authentificated!
        self.s = s


    def register_course (self, course_id):
        """ Registers a course (履修申請). It returns on success or abort the program on failure."""
        course_id = course_id.toupper()

        # these constants seems not to be important
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

        return list(csv.reader(r.text.split("\n")))
