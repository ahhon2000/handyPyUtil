#!/usr/bin/python3
from pathlib import Path
with open(Path(__file__).parent.parent.parent / 'cfg.py') as _: exec(_.read())

from math import isclose

from handyPyUtil.dates.Date import (
    Date,
    txtDateToSec, txtDateToSec_14, txtDate14Midnight, validDate14,
)


ts = ["1970-01-01 17:40", "1970-01-02",
"2016-02-29", "2016-03-01",
"2018-12-31 23:59:59", "2019-01-01",
"2016-08-15 03:19", "2016-08-16"]

for t in ts:
    d0 = Date(t)
    d = Date(d0)

    if not d0.same(d): raise Exception("Date object initialized from another Date object carries the wrong date")


# Test Date.same()

ts = ["1970-01-01 17:40", "1970-01-02",
"2016-02-29", "2016-03-01",
"2018-12-31 23:59:59", "2019-01-01",
"2016-08-15 03:19", "2016-08-16",
"2016-08-15 03:19", "2016-08-15 03:19:01"]

# equal
for t in ts:
    d0 = Date(t)
    d1 = Date(t)
if not d0.same(d1): raise Exception("Date.same() gives incorrect results on equal dates")

# unequal
for t in ts:
    d0 = Date(t)
    for tt in ts:
        if t == tt: continue
        d1 = Date(tt)
        if d0.same(d1): raise Exception("Date.same() gives incorrect results on unequal dates d0=%s, d1=%s; t=%s; tt=%s" % (d0, d1, t, tt))

# A test for Date.__lt__ and others

dst = [
    "2015-01-01",
    "2015-01-01 00:00:01",
    "2016-01-01",
    "2016-02-29",
    "2016-03-01",
    "2016-03-05 02:05",
    "2016-04-05 02:05",
    "2016-04-07 02:05",
    "2016-04-07 02:05:01",
    "2016-04-07 02:06",
    "2018-04-05 02:05",
]

ds = list(Date(d) for d in dst)

for i in range(len(ds)):
    d = ds[i]
    for j in range(i, len(ds)):
        dd = ds[j]
        if j > i  and  not ( dd > d): raise Exception("Date.__gt__() gives incorrect results")
        if j > i  and  not ( d < dd): raise Exception("Date.__lt__() gives incorrect results")
        if not ( dd >= d): raise Exception("Date.__ge__() gives incorrect results")
        if not ( d <= dd): raise Exception("Date.__le__() gives incorrect results")

# fractional and negative time differences

d1 = Date("2018-01-01 00:00:00")
d2 = Date("2018-01-01 00:00:15")

m = d1.minutesEarlier(d2)
if abs(m - 0.25) > 1e-10: raise Exception("Date.minutesEarlier() cannot deal with fractional minutes")

m = d2.minutesEarlier(d1)
if abs(m + 0.25) > 1e-10: raise Exception("Date.minutesEarlier() cannot deal with negative time differences")

# Initialisation from seconds since 1970-01-01

for d in (
            '2019-01-01 15:35:14',
            '2000-09-11 20:15:09',
            '1970-01-01',
            '1801-06-01 21:20:38',
            Date('now'),
):
    d = Date(d)
    sec = d.secSinceEpoch()
    d1 = Date(sec)
    sec1 = d1.secSinceEpoch()
    assert sec == sec1, "sec={sec}; sec1={sec1}\nd={d}; d1={d1}".format(
        sec = sec, sec1 = sec1, d = d, d1 = d1,
    )

# Test txtDateToSec()

for dtxt in (
    '2019-01-01 15:35:14',
    '2000-09-11 20:15:09',
    '1970-01-01',
    '1801-06-01 21:20:38',
    Date('now').toText(),
    '20140101153739',
    '19791014221400',
):
    sec0 = Date(dtxt).secSinceEpoch()
    assert isinstance(sec0, int)
    for f in (txtDateToSec, txtDateToSec_14):
        sec1 = f(dtxt) if f == txtDateToSec else f(Date(dtxt).toText())
        assert isinstance(sec1, int)
        assert sec0 == sec1, f'sec0 = {sec0};  sec1 = {sec1}; f={f}'

# Check midnight functions
for dtxt in (
    '2019-01-01 15:35:14',
    '2000-09-11 20:15:09',
    '1970-01-01',
    '1801-06-01 21:20:38',
    Date('now').toText(),
    '20140101153739',
    '19791014221400',
):
    d14 = Date(dtxt).toText()
    assert validDate14(d14), f''

    d14mn = txtDate14Midnight(d14)
    assert validDate14(d14mn, mustBeMidnight=True)

    assert Date(d14).midnight().toText() == d14mn
    assert Date(d14).midnight().same(Date(d14mn))

# Check nextDay
d1970, d2021 = map(Date, ('19700101', '20210101'))
ndays = d1970.daysEarlier(d2021)
assert isclose(ndays, round(ndays), abs_tol=1e-10)
d = d1970
for i in range(round(ndays)): d = d.nextDay()
assert d.same(d2021)

# Monday, this week
d = Date('monday')
today = Date('today')
ndays = d.daysEarlier(today)
assert d.datetime.weekday() == 0
assert isclose(ndays, today.datetime.weekday() - d.datetime.weekday())
assert round(ndays) in range(7)
