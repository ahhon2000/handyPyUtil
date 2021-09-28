import traceback

def fmtExc(e, msg="", inclTraceback=True):
    if not msg: msg = str(e)
    if inclTraceback:
        msg += "\n" + "".join(
            traceback.format_exception(e.__class__, e, e.__traceback__)
        )

    return msg
