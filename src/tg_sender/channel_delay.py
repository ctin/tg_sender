from dataclasses import dataclass
import datetime
from threading import Lock

@dataclass
class ChannelInfo:
    dt: datetime.datetime

class ChannelDelay:
    def __init__(self):
        self.channel_infos = {}
        self.lock = Lock()

    def IsChannelReady(self, channel):
        with self.lock:
            if channel in self.channel_infos:
                return datetime.datetime.now() >= self.channel_infos[channel].dt
        return True

    def UpdateChannelReady(self, channel, seconds = 1):
        with self.lock:
            dt = datetime.datetime.now() + datetime.timedelta(seconds = seconds)
            if channel not in self.channel_infos:
                self.channel_infos[channel] = ChannelInfo(dt = dt)
            else:
                self.channel_infos[channel].dt = dt