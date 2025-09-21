import aiogram
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types.input_file import FSInputFile
import re
import os

from dataclasses import dataclass

from logger import logging
from tg_sender import base_message_data

def SplitLinks(text):
    text_list = []
    while (result := re.search(r"\[[^\]]+\]\([^\)]+\)", text)) is not None:
        pos_from, void = result.span()
        # Uncouple text until the [
        text_list.append(text[:pos_from])
        # Uncouple the [ itself
        text_list.append("[")
        text = text[pos_from + 1:]
        # Find where the link caption ends
        result = re.search(r"\]\([^\)]+\)", text)
        pos_from, pos_to = result.span()
        # Uncouple the link caption
        text_list.append(text[:pos_from])
        # Uncouple the remainder: ](link)
        text_list.append(result[0])
        text = text[pos_to:]
    text_list.append(text)
    return text_list

# Escapes everything that is NOT markdown
def EscapeIfMarkdown(text, parse_mode: str):
    if text is None or text == "":
        return text
    if parse_mode is None or "markdown" not in parse_mode.lower():
        return text
    text_list = SplitLinks(text)
    for i in range(len(text_list)):
        if i % 2 == 0:
            text_list[i] = text_list[i].replace('.', '\\.').replace('!', '\\!').replace(',', '\\,').replace('(', '\\(') \
                .replace(')', '\\)').replace('<', '\\<').replace('>', '\\>').replace('-', '\\-').replace('=', '\\=') \
                .replace('[', '\\[').replace(']', '\\]').replace('|', '\\|').replace('+', '\\+').replace('#', '\\#') \
                .replace('{', '\\{').replace('}', '\\}')
    return "".join(text_list)

# Escapes markdown symbols, opposite to upper function
def EscapeMarkdown(text):
    return str(text).replace('\\', '\\\\').replace('_', '\\_').replace('~', '\\~').replace('*', '\\*').replace('`', '\\`')

class SenderBot:
    def __init__(self, token):
        self.token = token
        self.bot = aiogram.Bot(token=token)
        # Обфусцированный токен для логов
        self.obfuscated_token = self._obfuscate_token()

    def __del__(self):
        self.bot = None

    def _obfuscate_token(self):
        """
        Обфусцирует токен, оставляя только часть до двоеточия.
        Например, для токена "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" вернёт "123456:***"
        """
        if ':' in self.token:
            prefix = self.token.split(':')[0]
            return f"{prefix}"
        return "*****"

    async def SendText(self, bmd: base_message_data.BaseMessageData):
        text_to_send = EscapeIfMarkdown(bmd.text, bmd.parse_mode)
        logging.info(f"Token: {self.obfuscated_token} | Sending message to {bmd.channel}, thread_id: {bmd.thread_id}\n"
                     f"Options: parse_mode: {bmd.parse_mode}, reply_to: {bmd.reply_to}\n"
                     f"Content:\n{text_to_send}")
        return await self.bot.send_message(
            chat_id=bmd.channel,
            message_thread_id=bmd.thread_id,
            text=text_to_send,
            parse_mode=bmd.parse_mode,
            reply_to_message_id=bmd.reply_to,
            disable_web_page_preview=bmd.disable_web_page_preview
        )

    async def send_markup(self, bmd: base_message_data.BaseMessageData):
        text_to_send = EscapeIfMarkdown(bmd.text, bmd.parse_mode)
        logging.info(f"Token: {self.obfuscated_token} | Sending msg with markup to {bmd.channel}, thread_id: {bmd.thread_id}\n"
                     f"Options: parse_mode: {bmd.parse_mode}, reply_to: {bmd.reply_to}\n"
                     f"Content:\n{text_to_send}")
        keyboard = []
        for button in bmd.buttons:
            keyboard.append(types.InlineKeyboardButton(text=button.text, callback_data=button.callback_data))
        markup = types.InlineKeyboardMarkup(inline_keyboard=[keyboard])
        return await self.bot.send_message(
            chat_id=bmd.channel,
            message_thread_id=bmd.thread_id,
            text=text_to_send,
            parse_mode=bmd.parse_mode,
            reply_to_message_id=bmd.reply_to,
            disable_web_page_preview=bmd.disable_web_page_preview,
            reply_markup=markup
        )

    async def Forward(self, chat_id: str, from_chat_id: str, message_id: str, thread_id: int):
        logging.info(f"Token: {self.obfuscated_token} | Forwarding message {message_id} from chat {from_chat_id} to {chat_id} in thread {thread_id}")
        result = await self.bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, message_thread_id=thread_id)
        return result

    async def SendPhoto(self, bmd: base_message_data.BaseMessageData, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        photo_file = FSInputFile(path)
        text_to_send = EscapeIfMarkdown(bmd.text, bmd.parse_mode)
        logging.info(f"Token: {self.obfuscated_token} | Sending photo to {bmd.channel}\n"
                     f"Options: parse_mode: {bmd.parse_mode}, reply_to: {bmd.reply_to}\n"
                     f"Content:\n{text_to_send}")
        return await self.bot.send_photo(
            bmd.channel,
            message_thread_id=bmd.thread_id,
            photo=photo_file,
            caption=text_to_send,
            parse_mode=bmd.parse_mode,
            reply_to_message_id=bmd.reply_to
        )

    async def SendMultipleImages(self, bmd: base_message_data.BaseMessageData, paths: list[str]):
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
        text_to_send = EscapeIfMarkdown(bmd.text, bmd.parse_mode)
        logging.info(f"Token: {self.obfuscated_token} | Sending photos to {bmd.channel}\n"
                     f"Paths: {paths}\n"
                     f"Options: parse_mode: {bmd.parse_mode}, reply_to: {bmd.reply_to}\n"
                     f"Content: {text_to_send}")
        
        media = MediaGroupBuilder()

        for i, path in enumerate(paths):
            if i == 0:
                media.add(type="photo", media=FSInputFile(path), caption=text_to_send, parse_mode=bmd.parse_mode)
            else:
                media.add(type="photo", media=FSInputFile(path))
        return await self.bot.send_media_group(chat_id=bmd.channel, message_thread_id=bmd.thread_id, media=media.build(), reply_to_message_id=bmd.reply_to)

    async def SendFile(self, bmd: base_message_data.BaseMessageData, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        text_to_send = EscapeIfMarkdown(bmd.text, bmd.parse_mode)
        logging.info(f"Token: {self.obfuscated_token} | Sending file to {bmd.channel}\n"
                     f"Options: parse_mode: {bmd.parse_mode}, reply_to: {bmd.reply_to}\n"
                     f"Content:\n{text_to_send}")
        document = FSInputFile(path)
        return await self.bot.send_document(
            bmd.channel,
            message_thread_id=bmd.thread_id,
            document=document,
            caption=text_to_send,
            parse_mode=bmd.parse_mode,
            reply_to_message_id=bmd.reply_to,
        )

    async def Pin(self, chat_id: str, message_id, disable_notification: bool):
        logging.info(f"Token: {self.obfuscated_token} | Pinning message {message_id} in chat {chat_id} without notification: {disable_notification}")
        return await self.bot.pin_chat_message(chat_id=chat_id, message_id=message_id, disable_notification=disable_notification)

    async def Unpin(self, chat_id: str, message_id):
        logging.info(f"Token: {self.obfuscated_token} | Unpinning message {message_id} in chat {chat_id}")
        return await self.bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)

    async def Delete(self, chat_id: str, message_id):
        logging.info(f"Token: {self.obfuscated_token} | Deleting message {message_id} in chat {chat_id}")
        return await self.bot.delete_message(chat_id, message_id)
