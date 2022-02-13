# @rebootstr
import Exceptions
from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class UpdaterModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        self._reply_text(mes, vk, "Updating")
        raise Exceptions.ExitException("Exit To Update")
