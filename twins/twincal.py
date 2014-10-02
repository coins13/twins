#!/usr/bin/env python3
import tempfile
import requests

# TwinCalに作ってもらう
def generate_ics (courses):
    with tempfile.NamedTemporaryFile() as f:
        csv = "\n".join(map(lambda c: c["id"], courses))
        f.write(bytes(csv, "utf-8"))
        f.seek(0)
        user_agent = "Opera/9.80 (BlackBerry; Opera Mini/6.1.25376/26.958; U; en) Presto/2.8.119 Version/10.54"
        r = requests.post("http://gam0022.net/app/twincal/parse.rb", headers={"User-Agent": user_agent}, files={"file": f})
    return r.text
