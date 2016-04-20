# coding: utf-8
import datetime
import uuid
import re
import twins.twins as twins
from twins import Twins

header = """
BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//Seiya Nuta//twins cli//EN
VERSION:2.0
"""

event = """
BEGIN:VEVENT
CREATED:{created}
LAST-MODIFIED:{created}
DTSTAMP:{created}
DTSTART;TZID=Asia/Tokyo:{dt_start}
DTEND;TZID=Asia/Tokyo:{dt_end}
RRULE:FREQ=WEEKLY;UNTIL={dt_until}
SEQUENCE:0
SUMMARY:{summary}
LOCATION: {location}
DESCRIPTION: {description}
TRANSP:OPAQUE
UID:{uid}
END:VEVENT
"""

footer = """
END:VCALENDAR
"""


def strftime(x):
    return x.strftime("%Y%m%dT%H%M%S")


# XXX
start_dates = {
    "春A": (2016, 4, 13),
    "春B": (2016, 5, 23),
    "春C": (2016, 7, 5),
    "秋A": (2016, 10, 1),
    "秋B": (2016, 11, 8),
    "秋C": (2016, 1, 10),
}

end_dates = {
    "春A": (2016, 5, 22),
    "春B": (2016, 7, 4),
    "春C": (2016, 8, 9),
    "秋A": (2016, 11, 7),
    "秋B": (2016, 12, 28),
    "秋C": (2016, 2, 15),
}

def parse_module(module):
    assert(module[0] in ['春', '秋'])
    assert(all(map(lambda x: x in ['A', 'B', 'C'], module[1:])))
    return module[0], module[1:]


def get_start_date(module, x):
    """ 曜日による最初の授業の日を返す """
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    a, b = parse_module(module)
    module = a + b[0]

    d = datetime.datetime(*start_dates[module])
    days = weekdays.index(x) - d.weekday()
    if days < 0:
        days += 7
    delta = datetime.timedelta(days=days)
    return d + delta


def get_end_date(module):
    """ モジュールの終わりの日を返す """
    a, b = parse_module(module)
    module = a + b[-1]
    return datetime.datetime(*end_dates[module])


def parse_stupid_date(c):
    """
    kdbが返してくる間抜けな授業時間をパースしてdatetimeを返す

    例:

        月1
        木3,4
        水3,4金5,6
        月・火・水3-6

        sqlite3 ~/.course_list.db 'select periods from courses'|sort|uniq
    """
    start_time = {
        1: { "hour": 8, "minute": 40 },
        2: { "hour": 10, "minute": 10 },
        3: { "hour": 12, "minute": 15 },
        4: { "hour": 13, "minute": 45 },
        5: { "hour": 15, "minute": 15 },
        6: { "hour": 16, "minute": 45 },
    }

    end_time = {
        1: { "hour": 9, "minute": 55 },
        2: { "hour": 11, "minute": 25 },
        3: { "hour": 13, "minute": 30 },
        4: { "hour": 15, "minute": 0 },
        5: { "hour": 16, "minute": 30 },
        6: { "hour": 18, "minute": 0 },
    }

    periods = c['periods']
    dates = []
    while len(periods) > 0:
        m = re.search('((?:.・)*(?:.))([0-9])([,-])([0-9])', periods)
        assert(m is not None)

        groups = list(reversed(list(m.groups())))
        weekdays = groups.pop().split('・')
        period_start = int(groups.pop())

        if len(groups) == 0:
            sep = ','
            period_end = period_start
        else:
            sep = groups.pop()
            period_end = int(groups.pop())

        assert(sep in ['-', ','])
        assert(1 <= period_start <= 6)
        assert(1 <= period_end <= 6)

        if sep == ',':
            assert(period_end - period_start == 1)

        for weekday in weekdays:
            dt = get_start_date(c['modules'], weekday)
            dt_start = dt.replace(**start_time[period_start])
            dt_end = dt.replace(**end_time[period_end])
            dates.append((dt_start, dt_end))

        periods = periods[m.span()[1]:]

    return dates

def generate_ics(courses):
    """.ics作るやつ"""
    events = ""
    for c in courses:
        created = strftime(datetime.datetime.utcnow()) + "Z"
        summary = c["title"]
        location = c["room"]
        description = "{id}・{modules}・{credit}単位".format(**c)

        try:
            dates = parse_stupid_date(c)
        except AssertionError as e:
            sys.stderr.write("無視: 日付またはモジュールのパースに失敗しました"
                "(title={title}, periods={periods},"
                "modules={modules})\n".format(**c))

        for start, end in dates:
            uid = str(uuid.uuid4())
            dt_start = strftime(start)
            dt_end = strftime(end)

            until = get_end_date(c['modules'])
            dt_until = strftime(datetime.datetime.utcfromtimestamp(until.timestamp())) + "Z"
            events = events.strip() + event.format(**locals())

    return "\n".join(map(lambda x: x.strip(), [header, events, footer]))
