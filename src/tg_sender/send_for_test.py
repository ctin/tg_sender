import time
import asyncio
from unittest import mock
from tg_sender import bots
from tg_sender import tg_messages_producer
from tg_sender import base_message_to_send
from tg_sender import tg_sender_api

from logger import logging

last_result = None
global_errors_count = 0

def SuccessHandler(task, message_id):
    global last_result
    last_result = message_id
    logging.info("success: %s", message_id)

def ErrorHandler(module_name, e):
    global global_errors_count
    if not "Flood control exceeded" in str(e):
        global_errors_count += 1
    logging.info("error from %s: got e: %s", module_name, str(e))
    
# errors_count is the expected number of errors
async def SendCompletelyForTest(tokens: list[str], tasks: list[tg_sender_api.Task], errors_count: int = 0):
    global global_errors_count
    global_errors_count = 0
    time_now = time.time()
    expected_count = len(tasks)
    async with bots.Bots(tokens) as senders:
        on_error = mock.MagicMock()
        on_error.side_effect = ErrorHandler
        on_success = mock.MagicMock()
        on_success.side_effect = SuccessHandler

        bml = base_message_to_send.BaseMessageList()
        bml.AddTasks(tasks)

        producer = tg_messages_producer.MessagesProducer(senders, "test", on_error, on_success)
        # we can not expect that all signals will be sent instantly
        while on_success.call_count != (expected_count - global_errors_count) and time.time() - time_now < 600:
            await producer.produce_messages(bml.Get())
            await asyncio.sleep(0.1)
        await producer.wait_for_all_tasks()

    logging.info(f"Asserting {len(tasks)} == {expected_count}, time {time.time() - time_now}")
    assert errors_count == global_errors_count
    assert on_success.call_count == expected_count - errors_count
    return last_result
