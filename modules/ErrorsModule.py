# @rebootstr
from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class ErrorsModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        vk.send_error_in_mes("Pool Cleared")
