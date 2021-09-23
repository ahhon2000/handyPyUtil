import time
import datetime
import dateutil.parser
import pytz
import re

def txtDateToSec(dtxt):
    dtm = dateutil.parser.parse(dtxt)
    dtm = dtm.replace(tzinfo = pytz.UTC)
    sec = round(dtm.timestamp())

    return sec

D14_REGEXP = re.compile(r'^[0-9]{14}$')
D14_MIDNIGHT_REGEXP = re.compile(r'^[0-9]{8}0{6}$')

def validDate14(dtxt, mustBeMidnight=False):
    "Return True iff dtxt is a valid 14 character date"

    if not isinstance(dtxt, str): return False

    dre = D14_MIDNIGHT_REGEXP if mustBeMidnight else D14_REGEXP
    if not dre.search(dtxt): return False

    return True

def txtDateToSec_14(dtxt):
    "An optimised version of txtDateToSec() for dates like '20210306121500'"

    sec = round(
        datetime.datetime(
            year = int(dtxt[0:4]),
            month = int(dtxt[4:6]),
            day = int(dtxt[6:8]),
            hour = int(dtxt[8:10]),
            minute = int(dtxt[10:12]),
            second = int(dtxt[12:14]),
            tzinfo = pytz.UTC,
        ).timestamp()
    )

    return sec

def txtDate14Midnight(dtxt):
    return dtxt[0:8] + "000000"


class Date:
    def __init__(self, s):
        dt = None

        if isinstance(s, int):
            dt = datetime.datetime.fromtimestamp(s, pytz.UTC)
            dt = dt.replace(tzinfo=None)
        elif s.__class__.__name__ == 'Date':
            dt0 = s.datetime
            dt = datetime.datetime(
                year = dt0.year,
                month = dt0.month,
                day = dt0.day,
                hour = dt0.hour,
                minute = dt0.minute,
                second = dt0.second,
                microsecond = dt0.microsecond,
            )
        elif s == "now":
            dt = datetime.datetime.now()
        elif s == "today":
            dt = datetime.datetime.today()
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif s == "yesterday" or s == "yest":
            dt = datetime.datetime.today()
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            dt -= datetime.timedelta(days=1)
        elif s in ("monday", "this_week"):
            dt = datetime.datetime.today()
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            wd = dt.weekday()
            dt += datetime.timedelta(days=-wd)
        elif s == "inf" or s == "infinity":
            dt = dateutil.parser.parse("9999-12-31 23:59")
        else:
            dt = dateutil.parser.parse(s)

        self.datetime = dt


    def getDatetime(self):
        return self.datetime


    def toText(self):
        t = self.getDatetime().strftime("%Y%m%d%H%M%S")
        return t

    def toNiceText(self):
        t = self.getDatetime().strftime("%Y-%m-%d %H:%M:%S")
        return t

    def toRusTxt(self):
        t = self.getDatetime().strftime("%d.%m.%Y")
        return t


    def same(self, other):
        if self.toText() == other.toText():
            return True
        else:
            return False


    def nextDay(self):
        date = Date(self.toText())
        date.datetime += datetime.timedelta(days=1)
        return date

    def previousWeek(self):
        txt = self.toText()
        date = Date(txt)

        date.datetime -= datetime.timedelta(days=7)

        return date


    def __gt__(self, other):
        return self.toText() > other.toText()

    def __lt__(self, other):
        return self.toText() < other.toText()

    def __ge__(self, other):
        return self.toText() >= other.toText()

    def __le__(self, other):
        return self.toText() <= other.toText()


    def daysEarlier(self, other):
        # return the number of days since self until other

        td = other.getDatetime() - self.getDatetime()

        nd = td.days + td.seconds/(60.*60.*24.)

        return nd


    def hoursEarlier(self, other):
        # return the number of hours since self until other

        td = other.getDatetime() - self.getDatetime()

        nd = td.days*24. + td.seconds/(60.*60.)

        return nd


    def minutesEarlier(self, other):
        # return the number of minutes since self until other

        td = other.getDatetime() - self.getDatetime()

        nd = td.days*24.*60. + td.seconds/(60.)

        return nd


    def plusHours(self, n):
        """Return a date that is n hours later than self
        """

        d = Date(self.toText())
        d.datetime += datetime.timedelta(hours=n)

        return d

    def plusMinutes(self, n):
        """Return a date that is n minutes later than self
        """

        return self.plusHours(n/60)


    def plusDays(self, n):
        """Return a date that is n days later than self
        """

        d = Date(self.toText())
        d.datetime += datetime.timedelta(days=n)

        return d


    def toNiceTextDateOnly(self):
        t = self.getDatetime().strftime("%Y-%m-%d")
        return t

    def toNiceTextWOSec(self):
        t = self.getDatetime().strftime("%Y-%m-%d %H:%M")
        return t

    def toNiceTextTimeOnly(self):
        t = self.getDatetime().strftime("%H:%M")
        return t


    def midnight(self):
        d = Date(self)
        d.datetime += datetime.timedelta(
            days = 0,
            hours = - self.datetime.hour,
            minutes = - self.datetime.minute,
            seconds = - self.datetime.second,
            microseconds = - self.datetime.microsecond,
        )

        return d


    def firstOfMonth(self):
        d = Date("{}-{}-01".format(
            self.datetime.year, self.datetime.month
        ))

        return d

    def firstOfYear(self):
        """Jan 1, 00:00:00"""

        d = Date("{}-01-01".format(self.datetime.year))

        return d

    def secSinceEpoch(self):
        sec = round(self.datetime.replace(tzinfo=pytz.UTC).timestamp())
        return sec


    def __str__(self):
        return self.toNiceText()
