from dataclasses import dataclass
from typing import List, Optional
from tg_sender import tg_sender_api

@dataclass
class InlineButton:
    text: str
    callback_data: str

@dataclass
class BaseMessageData:
    channel: str
    thread_id: Optional[int]
    text: str
    parse_mode: str
    reply_to: int
    disable_web_page_preview: bool
    buttons: List[InlineButton] = None

class BaseMessageDataBuilder:
    def __init__(self):
        self._data = BaseMessageData(
            channel="",
            thread_id=None,
            text="",
            parse_mode="MarkdownV2",
            reply_to=0,
            disable_web_page_preview=False,
            buttons=[]
        )

    @classmethod
    def create(cls, channel: str, thread_id: Optional[int] = None) -> 'BaseMessageDataBuilder':
        builder = cls()
        if not channel:
            raise ValueError("channel is not provided!")
        builder._data.channel = channel
        builder._data.thread_id = thread_id
        return builder

    def add_text(self, text: str) -> 'BaseMessageDataBuilder':
        self._data.text = text
        return self

    def from_message_options(self, mo: tg_sender_api.MessageOptions) -> 'BaseMessageDataBuilder':
        self._data.parse_mode = mo.parse_mode
        self._data.reply_to = mo.reply_to
        self._data.disable_web_page_preview = not mo.enable_web_page_preview
        return self

    def add_buttons(self, buttons: List[tg_sender_api.Button]) -> 'BaseMessageDataBuilder':
        for button in buttons:
            inline_button = InlineButton(button.text, button.callback_data)
            self._data.buttons.append(inline_button)
        return self

    def build(self) -> BaseMessageData:
        if not self._data.channel:
            raise ValueError("channel is not provided!")
        return self._data

# Example Usage
# message_data = BaseMessageDataBuilder.create("channel_name", thread_id=123)
#                        .add_text("Hello, World!")
#                        .from_message_options(mo=tg_sender_api.MessageOptions(parse_mode="HTML", reply_to=123))
#                        .add_buttons([tg_sender_api.Button(text="Click me", callback_data="callback_1")])
#                        .build()