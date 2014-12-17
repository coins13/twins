#!/usr/bin/env python3
import tempfile
import requests

# TwinCalに作ってもらう
def generate_ics (courses):
    with tempfile.NamedTemporaryFile() as f:
        csv = "\n".join(courses)
        f.write(bytes(csv, "utf-8"))
        f.seek(0)
        user_agent = "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        r = requests.post("http://gam0022.net/app/twincal/parse.rb", headers={"User-Agent": user_agent}, files={"file": f})
    return r.text
