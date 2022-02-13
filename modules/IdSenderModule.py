# @rebootstr
from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class IdSenderModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        message = self._get_message_by_id(mes.get_id(), vk)
        if message["count"] != 0:
            message = message["items"][0]
            if len(message["fwd_messages"]) != 0:
                message_id = message["fwd_messages"][0]["id"]
            elif "reply_message" in message.keys():
                message_id = message["reply_message"]["id"]
            else:
                return
            self._reply_text(mes, vk, str(message_id))
