import time
import pytest
import aiogram
from aiogram import exceptions
from logger import logging
from tg_sender import test_data
from tg_sender import tg_messages_producer
from tg_sender import bots
from tg_sender import tg_sender_api
from tg_sender import send_for_test
from tg_sender import utils

from unittest import mock

message_id = None

class TestTGText():
    async def testNoBots(self):
        with pytest.raises(ValueError):
            tg_messages_producer.MessagesProducer(bots, #yes, bots module, I did it on prod
                                                "test",
                                                None,
                                                None)
        with pytest.raises(ValueError):
            bots.Bots(None)

    async def testTgSendMessageNoTask(self):
        with pytest.raises(ValueError) as re:
            tasks = [tg_sender_api.Task(
                channel = test_data.GetChannel()
            )]
            await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
            
        assert str(re.value) == "unknown task: empty"

    async def testTGSendAndDelete(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            send_text = tg_sender_api.SendText(text = "THIS SHOULD BE REMOVED")
        )]
        last_id = await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        tasks = [tg_sender_api.Task(
              channel = test_data.GetChannel(),
              delete = tg_sender_api.Delete(message_id = last_id)
        )]
        await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        tasks = [tg_sender_api.Task(
              channel = test_data.GetChannel(),
              delete = tg_sender_api.Delete(message_id = last_id)
        )]
        await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
        tasks = [tg_sender_api.Task(
              channel = test_data.GetChannel(),
              delete = tg_sender_api.Delete(message_id = 1)
        )]
        await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)


    async def testTgSendMessageRaisesForbidden(self):
        with mock.patch.object(aiogram.Bot, 'send_message') as mock_send_message:
            mock_send_message.side_effect = exceptions.TelegramForbiddenError(method=aiogram.methods.SendMessage, message="bot was kicked from the supergroup chat")
            tasks = [tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_text = tg_sender_api.SendText(text = "raise bot was kicked")
            )]
            await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
    
    async def testTGSendWrongChannel(self):
        tasks = [tg_sender_api.Task(
            channel = "@buyside",
            send_text = tg_sender_api.SendText(text = "SORRY IF YOU SEE THIS")
        )]
        
        await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)


    async def testTgSendMessagePositive(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            send_text = tg_sender_api.SendText(text = "simple test")
        )]
        last_id = await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            pin = tg_sender_api.Pin(message_id=last_id, enable_notification=False)
        )]
        result = await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        assert result == True
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            unpin = tg_sender_api.Unpin(message_id=last_id)
        )]
        result = await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        assert result == True
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            forward = tg_sender_api.Forward(from_channel = test_data.GetChannel(),
                message_id = last_id)
        )]
        result = await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks)
        assert result > 0

        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            options=tg_sender_api.MessageOptions(reply_to=last_id),
            send_text = tg_sender_api.SendText(text = "reply-to test")
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks) > 0


    async def testTgSendMessageRaisedError(self):
        with mock.patch.object(aiogram.Bot, 'send_message') as mock_send_message:
            mock_send_message.side_effect = RuntimeError("mock network error")
            tasks = [tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_text = tg_sender_api.SendText(text = "raise failed test")
            )]
            await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
    
    async def testTgTextWrongChannel(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel() + "123",
            send_text = tg_sender_api.SendText(text = "raise failed test")
        )]
        await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)

    async def testTgSendMessageNoText(self):
        with pytest.raises(ValueError) as re:
            tasks = [tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_text = tg_sender_api.SendText()
            )]
            await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
        assert str(re.value) == "no text"

    async def testTgSendMessageNoChannel(self):
        with pytest.raises(ValueError) as re:
            tasks = [tg_sender_api.Task(
            )]
            await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
        assert str(re.value) == "channel is not set"

    async def testTgSendMessageLink(self):
        link = utils.create_link("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "google")
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            send_text = tg_sender_api.SendText(text = f"link: {link}")
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks) > 0

    async def testTgSendMessageNoFormat(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            options=tg_sender_api.MessageOptions(parse_mode=None),
            send_text = tg_sender_api.SendText(text = "no format: [google](www.google.com)")
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks) > 0

    async def testTgSendMessageTooLarge(self):
        text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            send_text = tg_sender_api.SendText(text=text)
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)

    async def testTgSendMessageCantParse(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            send_text = tg_sender_api.SendText(text = "can't_parse```"),
            options= tg_sender_api.MessageOptions(parse_mode="MarkdownV2")
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 0)

    async def testTgSendMessageThreadIdNotFound(self):
        tasks = [tg_sender_api.Task(
            channel = test_data.GetChannel(),
            thread_id = 123,
            send_text = tg_sender_api.SendText(text = "thread id not found")
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 1)
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 0)

    async def test_tg_sender_buttons(self):
        tasks = [tg_sender_api.Task(
            channel=test_data.GetChannel(),
            send_markup=tg_sender_api.SendMarkup(
                text = "buttons",
                buttons = [tg_sender_api.Button(text="Button 1", callback_data="cb_1"),
                    tg_sender_api.Button(text="Button 2", callback_data="cb_2")]
            )
        )]
        assert await send_for_test.SendCompletelyForTest(test_data.GetTokens(), tasks, 0)

    async def testSpam(self):
        tasks = []
        for i in range(30):
            tasks.append(
                tg_sender_api.Task(
                    channel = test_data.GetChannel(),
                    send_text= tg_sender_api.SendText(text = f"spam-{i}" )
                )
            )
        tokens = [test_data.GetTokens()[0]]
        assert await send_for_test.SendCompletelyForTest(tokens, tasks)
