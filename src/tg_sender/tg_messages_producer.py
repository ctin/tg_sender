import asyncio
import aiogram
from aiogram import exceptions
import re
import traceback
import betterproto

from tg_sender import bots
from tg_sender import bot
from tg_sender import channel_delay
from tg_sender import tg_sender_api
from tg_sender import base_message_data
from logger import logging

class MessagesProducer:
    def __init__(self, senders: bots.Bots, module_folder_name: str, on_error, on_success = None):
        if not isinstance(senders, bots.Bots):
            raise ValueError("you did not pass senders, arent you?")
        self.senders = senders
        self.on_error = on_error
        self.on_success = on_success
        self.module_folder_name = module_folder_name
        self.active_tasks = set()       

    def ErrorHandler(self, e, task: tg_sender_api.Task):
        logging.info(f"got error: {str(e)}, task: {task}")
        logging.info(traceback.format_exc())
        self.on_error(self.module_folder_name, f"{str(e)}\n{task}")

    async def WrapWholeCall(self, task_fn, task: tg_sender_api.Task, channel: str, channel_delay: channel_delay.ChannelDelay):
        try:
            await task_fn
        except exceptions.TelegramRetryAfter as ra:
            m = re.search(r'.*\s(\d+) seconds.', str(ra))
            if m:
                found = m.group(1)
                channel_delay.UpdateChannelReady(channel, int(found))
            self.ErrorHandler(ra, task)
        except Exception as e:
            self.ErrorHandler(e, task)
        finally:
            task.details.in_process = 0
            
    async def WrapTGCall(self, message_future, task: tg_sender_api.Task):
        try:
            result = await message_future
            logging.info("marking message as sent, result: %s", result)
            task.details.sent = 1
            if result is not None:
                if isinstance(result, bool): # for pin and unpin
                    pass # already assigned
                elif isinstance(result, list):
                    result = result[0].message_id
                else:
                    result = result.message_id
                task.details.result = result
                if self.on_success:
                    self.on_success(task, result)
        except FileNotFoundError as fnfe:
            logging.error("file not found: %s", fnfe)
            task.details.sent = 1
            raise fnfe
        except exceptions.TelegramMigrateToChat as tmtc:
            logging.error("got TelegramMigrateToChat: %s", tmtc)
            task.details.sent = 1
            raise tmtc
        except exceptions.TelegramForbiddenError as tfe:
            task.details.sent = 1
            logging.error("got Forbidden: %s", str(tfe))
            raise tfe
        except exceptions.TelegramBadRequest as br:
            logging.error("got BadRequest: %s", br)
            if "Replied message not found" in str(br):
                task.options.reply_to = None
            elif "too long" in str(br):
                logging.error("got MessageIsTooLong: %s", br)
                task.details.sent = 1
            elif "can't parse entities" in str(br):
                logging.error("got can't parse entities: %s", br)
                task.options.parse_mode = None
            elif "chat not found" in str(br):
                logging.error(f"chat not found: {task.channel}:{task.thread_id}")
                task.details.sent = 1
            elif "message to delete not found" in str(br):
                logging.error(f"message to delete not found {str(br)}")
                task.details.sent = 1
            elif "TOPIC_CLOSED" in str(br):
                logging.error(f"TOPIC_CLOSED: {task.channel}:{task.thread_id}")
                task.details.sent = 1
            elif "message can't be deleted" in str(br):
                logging.error(f"message can't be deleted: {task.channel}:{task.thread_id}")
                task.details.sent = 1
            elif "message thread not found" in str(br):
                logging.error(f"message thread not found: {task.channel}:{task.thread_id}")
                task.thread_id = None
            raise br
        except exceptions.AiogramError as ae:  
            logging.error("got an unknown exception: %s", str(ae))
            task.details.sent = 1
            raise ae

    async def ProduceMessages(self, tasks: list[tg_sender_api.Task]):
        pooled_tasks = []
        for task in tasks:            
            channel = task.channel
            free_bot, channel_delay = self.senders.GetFreeBot(channel)
            if free_bot is not None:
                task.details.in_process = 1
                channel_delay.UpdateChannelReady(channel)
                task_fn = self.GetTaskFN(task, free_bot)
                wrapped_task_fn = self.WrapWholeCall(task_fn, task, channel, channel_delay)
                pooled_tasks.append(wrapped_task_fn)
        await asyncio.gather(*pooled_tasks)
        return []
    
    async def produce_messages(self, tasks: list[tg_sender_api.Task]):
        for task in tasks:
            channel = task.channel
            free_bot, channel_delay = self.senders.GetFreeBot(channel)
            if free_bot is not None:
                task.details.in_process = 1
                channel_delay.UpdateChannelReady(channel)
                task_fn = self.GetTaskFN(task, free_bot)
                wrapped_task_fn = self.WrapWholeCall(task_fn, task, channel, channel_delay)
                self._track_task(asyncio.create_task(wrapped_task_fn))  # Добавляем задачу

    def _track_task(self, task):
        """Добавляет задачу в список активных и удаляет после завершения."""
        self.active_tasks.add(task)
        task.add_done_callback(lambda t: self.active_tasks.discard(t))

    async def wait_for_all_tasks(self):
        """Ждём завершения всех активных задач."""
        while self.active_tasks:
            await asyncio.sleep(0.1)
    
    def GetTaskName(self, task):
        return betterproto.which_one_of(task, "task")[0]
    
    def GetTaskFN(self, task, free_bot):
        task_name = self.GetTaskName(task)
        if task_name == "send_text":
            task_fn = self.SendText(task, free_bot)
        elif task_name == "send_photo":
            task_fn = self.SendPhoto(task, free_bot)
        elif task_name == "send_photos":
            task_fn = self.SendPhotos(task, free_bot)
        elif task_name == "send_file":
            task_fn = self.SendFile(task, free_bot)
        elif task_name == "forward":
            task_fn = self.Forward(task, free_bot)
        elif task_name == "pin":
            task_fn = self.Pin(task, free_bot)
        elif task_name == "unpin":
            task_fn = self.Unpin(task, free_bot)
        elif task_name == "delete":
            task_fn = self.Delete(task, free_bot)
        elif task_name == "send_markup":
            task_fn = self.send_markup(task, free_bot)
        else:
            raise RuntimeError("unknown task: {}".format(task_name if task_name != "" else "empty"))
        return task_fn

    async def SendText(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        task_impl = task.send_text
        bmd = base_message_data.BaseMessageDataBuilder\
            .create(task.channel, task.thread_id)\
            .add_text(task_impl.text)\
            .from_message_options(task.options)\
            .build()
        message_future = free_bot.SendText(bmd)
        return await self.WrapTGCall(message_future, task)

    async def SendPhoto(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        task_impl = task.send_photo
        bmd = base_message_data.BaseMessageDataBuilder\
            .create(task.channel, task.thread_id)\
            .add_text(task_impl.caption)\
            .from_message_options(task.options)\
            .build()
        message_future = free_bot.SendPhoto(bmd, task_impl.path)
        return await self.WrapTGCall(message_future, task)

    async def SendPhotos(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        task_impl = task.send_photos
        bmd = base_message_data.BaseMessageDataBuilder\
            .create(task.channel, task.thread_id)\
            .add_text(task_impl.caption)\
            .from_message_options(task.options)\
            .build()
            
        message_future = free_bot.SendMultipleImages(bmd, task_impl.paths)
        return await self.WrapTGCall(message_future, task)
    
    async def SendFile(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        task_impl = task.send_file
        bmd = base_message_data.BaseMessageDataBuilder\
            .create(task.channel, task.thread_id)\
            .add_text(task_impl.caption)\
            .from_message_options(task.options)\
            .build()
        message_future = free_bot.SendFile(bmd, task_impl.path)
        return await self.WrapTGCall(message_future, task)
    
    async def Forward(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        channel = task.channel
        task_impl = task.forward
        message_future = free_bot.Forward(channel, task_impl.from_channel, task_impl.message_id, task.thread_id)
        return await self.WrapTGCall(message_future, task)

    async def Pin(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        channel = task.channel
        task_impl = task.pin
        message_future = free_bot.Pin(channel, task_impl.message_id, not task_impl.enable_notification)
        return await self.WrapTGCall(message_future, task)

    async def Unpin(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        channel = task.channel
        task_impl = task.unpin
        message_future = free_bot.Unpin(channel, task_impl.message_id)
        return await self.WrapTGCall(message_future, task)

    async def Delete(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        channel = task.channel
        message_id = task.delete.message_id
        message_future = free_bot.Delete(channel, message_id)
        return await self.WrapTGCall(message_future, task)
    
    async def send_markup(self, task: tg_sender_api.Task, free_bot: bot.SenderBot):
        task_impl = task.send_markup
        bmd = base_message_data.BaseMessageDataBuilder\
            .create(task.channel, task.thread_id)\
            .add_text(task_impl.text)\
            .from_message_options(task.options)\
            .add_buttons(task_impl.buttons)\
            .build()
        message_future = free_bot.send_markup(bmd)
        return await self.WrapTGCall(message_future, task)