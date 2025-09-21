import pytest
import time
from tg_sender import channel_delay

def testChannelDelay():
    channel = "testChannelDelay"
    cd = channel_delay.ChannelDelay()
    assert cd.IsChannelReady(channel) == 1
    cd.UpdateChannelReady(channel)
    assert cd.IsChannelReady(channel) == 0
    time.sleep(0.5)
    assert cd.IsChannelReady(channel) == 0
    time.sleep(0.6)
    assert cd.IsChannelReady(channel) == 1
