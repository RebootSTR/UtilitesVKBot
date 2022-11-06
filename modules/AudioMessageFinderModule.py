# @rebootstr
import random
import time

import requests

from Message import Message
from MessagesStorage import MessagesStorage
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class AudioMessageFinderModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        storage: MessagesStorage = arg1

        full_msg = self._get_message_by_id(mes.get_id(), vk)
        if full_msg["count"] != 0:
            if "fwd_messages" in full_msg["items"][0].keys():
                fwd = full_msg["items"][0]["fwd_messages"]
                if len(fwd) == 2:
                    from_id = fwd[0]["id"]
                    to_id = fwd[1]["id"]
                    #
                    messages = storage.get_audio_message_history(from_id, to_id, fwd[0]["peer_id"])
                    for message in messages:
                        text = f"{message['name']} - {time.ctime(message['date'])}"
                        self._send_mess_with_att(mes, vk, text, message['attachment'])

        self._delete_msg(mes, vk)
