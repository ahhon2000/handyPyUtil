from . import TestKit, TestKitRegister


def cleanup():
    "Clean up after TestKits that were run in nocleanup mode"

    tkr = TestKitRegister()
    tkr.cleanup()
