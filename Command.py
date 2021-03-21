# @rebootstr

import random
from Message import Message
from MyVKLib.vk import VK
import time

commands = ["/status"]


def is_command(mes: Message):
    return mes.get_text().split(" ")[0] in commands


def execute(mes: Message, vk: VK):
    index = commands.index(mes.get_text().split(" ")[0])
    if index == 0:  # status
        if mes.is_out_or_me(vk.user_id):
            return _send_status(mes, vk)


def _send_status(mes: Message, vk: VK):
    send = vk.rest.post("messages.send",
                        peer_id=mes.get_peer(),
                        message=f"<Online.{time.strftime('%H:%M:%S')}>",
                        reply_to=mes.get_id(),
                        random_id=random.randint(-2147483648, 2147483647))
    delete = vk.rest.post("messages.delete",
                          message_ids=mes.get_id(),
                          delete_for_all=True)
    print(delete.json())
    return [send.json()["response"]]
