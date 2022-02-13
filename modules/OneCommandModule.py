# @rebootstr

from typing import final

from Message import Message
from MyVKLib.vk import VK
from modules.BaseModule import BaseModule


class OneCommandModule(BaseModule):

    def __init__(self, sendType: int, command: str):
        super().__init__(sendType)
        self._command = command

    @final
    def checkAndDo(self, mes: Message, vk: VK, arg1=None, arg2=None) -> bool:
        com = mes.get_text().split(" ")[0]

        if self._isNeedDo(com, mes, vk):
            self._onDo(mes, vk, arg1, arg2)
            return True

        return False

    def _isNeedDo(self, com: str, mes: Message, vk: VK) -> bool:
        if com != self._command:
            return False

        if self._type == BaseModule.FROM_ME:
            if mes.is_out_or_myself(vk.user_id):
                return True
        elif self._type == BaseModule.ONLY_MYSELF:
            if mes.is_myself(vk.user_id):
                return True

        return False

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        pass
