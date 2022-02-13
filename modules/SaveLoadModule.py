# @rebootstr
from Message import Message
from MyVKLib.vk import VK
from modules.CloneModule import CloneModule
from modules.TwoCommandsModule import TwoCommandsModule


class SaveLoadModule(TwoCommandsModule):

    def __init__(self, sendType: int, saveCommand: str, loadCommand: str):
        super().__init__(sendType, saveCommand, loadCommand)
        self.saved = []

    def _onDoCommand1(self, mes: Message, vk: VK, arg1, arg2):
        self.save(mes, vk)

    def _onDoCommand2(self, mes: Message, vk: VK, arg1, arg2):
        self.load(mes, vk)

    def save(self, mes: Message, vk: VK):
        try:
            jsonMessages = CloneModule.getMessagesForClone(mes, vk)
            prepared = CloneModule.prepareToClone(jsonMessages)
            CloneModule.sendPrepared(mes, vk, prepared)

            self.saved = prepared

            self._delete_msg(mes, vk)
        except:
            vk.send_error_in_mes(f"can't save, get error. id={mes.get_id()}")

    def load(self, mes: Message, vk: VK):
        CloneModule.sendPrepared(mes, vk, self.saved)
        self._delete_msg(mes, vk)
