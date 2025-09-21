from tg_sender import channel_delay
from tg_sender import bot


class Bots:
    def __init__(self, bot_tokens: list[str]):
        if bot_tokens is None or len(bot_tokens) == 0 or not isinstance(bot_tokens, list):
            raise ValueError("declare bots first")
        self.__bots: list[bot.SenderBot] = [] 
        for bot_token in bot_tokens:
            self.__bots.append(bot.SenderBot(bot_token))

        self.__delays: list[channel_delay.ChannelDelay] = []
        for _ in range(len(self.__bots)):
            self.__delays.append(channel_delay.ChannelDelay())
    
    def GetFreeBot(self, channel):
        for i, channel_delay in enumerate(self.__delays):
            if channel_delay.IsChannelReady(channel):
                return self.__bots[i], channel_delay
        return None, None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        for bot in self.__bots:
            await bot.bot.session.close()

