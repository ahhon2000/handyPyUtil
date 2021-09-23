from pathlib import Path

class HandyCfg:
    def __init__(self, handyPath):
        handyPath = Path(handyPath).resolve()

        self.handyPath = handyPath
        self.handyParentPath = handyParentPath = handyPath.parent
