# @rebootstr
import random

from Message import Message
from MyVKLib.vk import VK


class BaseModule:
    FROM_ME = 1
    ONLY_MYSELF = 2

    def __init__(self, sendType: int):
        self._type = sendType

    def checkAndDo(self, mes: Message, vk: VK, arg1=None, arg2=None) -> bool:
        pass

    def _isNeedDo(self, command: str, mes: Message, vk: VK) -> bool:
        pass

    @staticmethod
    def _send_text(mes: Message, vk: VK, text: str):
        send = vk.rest.post("messages.send",
                            peer_id=mes.get_peer(),
                            message=text,
                            random_id=random.randint(-2147483648, 2147483647))
        return send

    @staticmethod
    def _reply_text(mes: Message, vk: VK, text: str):
        send = vk.rest.post("messages.send",
                            peer_id=mes.get_peer(),
                            message=text,
                            reply_to=mes.get_id(),
                            random_id=random.randint(-2147483648, 2147483647))
        return send

    @staticmethod
    def _delete_msg(mes: Message, vk: VK):
        vk.rest.post("messages.delete",
                     message_ids=mes.get_id(),
                     delete_for_all=0 if mes.is_myself(vk.user_id) else 1)

    @staticmethod
    def _send_mess_with_fwd_and_att(mes: Message, vk: VK, text, fwd, att):
        vk.rest.post("messages.send",
                     peer_id=mes.get_peer(),
                     message=text,
                     attachment=att,
                     forward_messages=fwd,
                     random_id=random.randint(-2147483648, 2147483647))

    @staticmethod
    def _get_message_by_id(id, vk):
        return vk.rest.post("messages.getById", message_ids=id).json()["response"]
