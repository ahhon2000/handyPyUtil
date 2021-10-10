import traceback

def fmtExc(e, msg="", inclTraceback=True):
    if not msg: msg = str(e)
    if inclTraceback:
        msg += "\n" + "".join(
            traceback.format_exception(e.__class__, e, e.__traceback__)
        )

    return msg

def fmtStack(msg=""):
    "Return the stack as a string. Include msg as the first line, if given"

    if msg: msg += "\n"
    msg += "\n".join(traceback.format_stack())
    return msg
