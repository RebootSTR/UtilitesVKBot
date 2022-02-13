# @rebootstr

from typing import final

from Message import Message
from MyVKLib.vk import VK
from modules.BaseModule import BaseModule


class TwoCommandsModule(BaseModule):

    def __init__(self, sendType: int, command1: str, command2: str):
        super().__init__(sendType)
        self._command1 = command1
        self._command2 = command2

    @final
    def checkAndDo(self, mes: Message, vk: VK, arg1=None, arg2=None) -> bool:
        com = mes.get_text().split(" ")[0]

        if self._isNeedDo(com, mes, vk):
            if com == self._command1:
                self._onDoCommand1(mes, vk, arg1, arg2)
            else:
                self._onDoCommand2(mes, vk, arg1, arg2)
            return True
        return False

    def _isNeedDo(self, command: str, mes: Message, vk: VK) -> bool:
        if command != self._command1 and command != self._command2:
            return False

        if self._type == BaseModule.FROM_ME:
            if mes.is_out_or_myself(vk.user_id):
                return True
        elif self._type == BaseModule.ONLY_MYSELF:
            if mes.is_myself(vk.user_id):
                return True

        return False

    def _onDoCommand1(self, mes: Message, vk: VK, arg1, arg2):
        pass

    def _onDoCommand2(self, mes: Message, vk: VK, arg1, arg2):
        pass
