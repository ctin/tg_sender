import pytest
from tg_sender import base_message_to_send
from tg_sender import tg_sender_api
from tg_sender import test_data

class TestTGBML:
    
    async def testNoTask(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel()
            )
            bml.AddTask(task)
        assert "unknown task" in str(ve)

    async def testNoChannel(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                send_text = tg_sender_api.SendText(text = "no channel")
            )
            bml.AddTask(task)
        assert "channel" in str(ve)

    async def testNoText(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_text = tg_sender_api.SendText()
            )
            bml.AddTask(task)
        assert "no text" in str(ve)

    async def testNoFile(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_file = tg_sender_api.SendFile(caption = "no file")
            )
            bml.AddTask(task)
        assert "no file path" in str(ve)

    async def testNoPhoto(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_photo = tg_sender_api.SendPhoto(caption = "no photo")
            )
            bml.AddTask(task)
        assert "no photo" in str(ve)

    async def testNoPhotos(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                send_photos = tg_sender_api.SendPhotos(caption = "no photos")
            )
            bml.AddTask(task)
        assert "no photos" in str(ve)

    async def testNoForwardChan(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                forward = tg_sender_api.Forward(message_id=1234)
            )
            bml.AddTask(task)
        assert "no channel" in str(ve)
        
    async def testNoForwardMessage(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                forward = tg_sender_api.Forward(from_channel="123")
            )
            bml.AddTask(task)
        assert "no message" in str(ve)

    async def testNoPinMessage(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                pin = tg_sender_api.Pin()
            )
            bml.AddTask(task)
        assert "no message" in str(ve)

    async def testNoUnpinMessage(self, mocker):
        with pytest.raises(ValueError) as ve:
            bml = base_message_to_send.BaseMessageList()
            task = tg_sender_api.Task(
                channel = test_data.GetChannel(),
                unpin = tg_sender_api.Unpin()
            )
            bml.AddTask(task)
        assert "no message" in str(ve)