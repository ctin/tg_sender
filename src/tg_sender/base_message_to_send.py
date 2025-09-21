import betterproto

from logger import logging

from tg_sender import tg_sender_api

class BaseMessageList:
    def __init__(self):
        self.tasks: list[tg_sender_api.Task] = []
    
    def AddTasks(self, tasks: list[tg_sender_api.Task]):
        for task in tasks:
            self.AddTask(task)

    def AddTask(self, task: tg_sender_api.Task):
        self.ValidateTask(task)
        self.tasks.append(task)
        
    def ValidateTask(self, task: tg_sender_api.Task):
        logging.info("task: %s", task)
        if task.channel is None or task.channel == "":
            raise ValueError("channel is not set")
        task_name = betterproto.which_one_of(task, "task")[0]
        if task_name == "send_text":
            if task.send_text.text is None or task.send_text.text == "":
                raise ValueError("no text")
        elif task_name == "send_photo":
            if task.send_photo.path is None or task.send_photo.path == "":
                raise ValueError("no photo path")
        elif task_name == "send_photos":
            if task.send_photos.paths is None or len(task.send_photos.paths) == 0:
                raise ValueError("no photos paths")        
        elif task_name == "send_file":
            if task.send_file.path is None or task.send_file.path == "":
                raise ValueError("no file path")
        elif task_name == "forward":
            if task.forward.from_channel is None or task.forward.from_channel == "":
                raise ValueError("no channel to forward")
            if task.forward.message_id is None or task.forward.message_id == 0:
                raise ValueError("no message id to forward")
        elif task_name == "pin":
            if task.pin.message_id is None or task.pin.message_id == 0:
                raise ValueError("no message id to pin")
        elif task_name == "unpin":
            if task.unpin.message_id is None or task.unpin.message_id == 0:
                raise ValueError("no message id to unpin")
        elif task_name == "delete":
            if task.delete.message_id is None or task.delete.message_id == 0:
                raise ValueError("no message id to delete")
        elif task_name == "send_markup":
            if not task.send_markup.buttons:
                raise ValueError("no buttons")
        else:
            raise ValueError("unknown task: {}".format(task_name if task_name != "" else "empty"))

    def Get(self):
        self.tasks = [ m for m in self.tasks if not m.details.sent ]
        return [ m for m in self.tasks if not m.details.in_process ]



