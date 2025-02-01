from configparser import ConfigParser


class BoundingBox:
    def __init__(self, cfg: ConfigParser):
        self.l = int(cfg["l"])
        self.t = int(cfg["t"])
        self.r = int(cfg["r"])
        self.b = int(cfg["b"])

    def __getitem__(self, key):
        return getattr(self, key)
