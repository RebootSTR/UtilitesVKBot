# @rebootstr

import time

from Message import Message
from MessagesStorage import MessagesStorage
from MyVKLib.vk import VK
from modules.AudioMessageFinderModule import AudioMessageFinderModule
from modules.BaseModule import BaseModule
from modules.CloneModule import CloneModule
from modules.DeleterModule import DeleterModule
from modules.ErrorsModule import ErrorsModule
from modules.HelpModule import HelpModule
from modules.HistorySenderModule import HistorySenderModule
from modules.IdSenderModule import IdSenderModule
from modules.PauseModule import PauseModule
from modules.ResumeModule import ResumeModule
from modules.SaveLoadModule import SaveLoadModule
from modules.StatusModule import StatusModule
from modules.TokenSenderModule import TokenSenderModule
from modules.UpdaterModule import UpdaterModule


class CommandExecutor:
    def __init__(self, start_time, bot_version, storage: MessagesStorage):
        if start_time is None:
            self.BOT_STARTED_TIME = time.time()
        else:
            self.BOT_STARTED_TIME = start_time
        self.bot_version = bot_version
        self.storage = storage

        self.commands = ["/status",
                         "/pause",
                         "/resume",
                         "/d",
                         "/errors",
                         "/update",
                         "/clone",
                         "/get_id",
                         "/history",
                         "/token",
                         "/help",
                         "/save",
                         "/load",
                         "/gs"]

        self.statusModule = StatusModule(BaseModule.FROM_ME, self.commands[0])
        self.pauseModule = PauseModule(BaseModule.FROM_ME, self.commands[1])
        self.resumeModule = ResumeModule(BaseModule.FROM_ME, self.commands[2])
        self.deleterModule = DeleterModule(BaseModule.FROM_ME, self.commands[3])
        self.errorsModule = ErrorsModule(BaseModule.ONLY_MYSELF, self.commands[4])
        self.updaterModule = UpdaterModule(BaseModule.FROM_ME, self.commands[5])
        self.cloneModule = CloneModule(BaseModule.FROM_ME, self.commands[6])
        self.idSenderModule = IdSenderModule(BaseModule.FROM_ME, self.commands[7])
        self.historySenderModule = HistorySenderModule(BaseModule.FROM_ME, self.commands[8])
        self.tokenSenderModule = TokenSenderModule(BaseModule.ONLY_MYSELF, self.commands[9])
        self.helpModule = HelpModule(BaseModule.FROM_ME, self.commands[10])
        self.saveLoadModule = SaveLoadModule(BaseModule.FROM_ME, self.commands[11], self.commands[12])
        self.audioMessageFinderModule = AudioMessageFinderModule(BaseModule.FROM_ME, self.commands[13])

        self.PAUSE = False

    def is_command(self, mes: Message):
        return mes.get_text().split(" ")[0] in self.commands

    def execute(self, mes: Message, vk: VK):
        if self.PAUSE:
            result = self.resumeModule.checkAndDo(mes, vk)
            if result:
                self.PAUSE = False
                return
        else:
            result = self.statusModule.checkAndDo(mes, vk, self.BOT_STARTED_TIME, self.bot_version)
            if result:
                return

            result = self.pauseModule.checkAndDo(mes, vk)
            if result:
                self.PAUSE = True
                return

            result = self.deleterModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.errorsModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.updaterModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.cloneModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.idSenderModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.historySenderModule.checkAndDo(mes, vk, self.storage)
            if result:
                return

            result = self.tokenSenderModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.helpModule.checkAndDo(mes, vk, self.commands)
            if result:
                return

            result = self.saveLoadModule.checkAndDo(mes, vk)
            if result:
                return

            result = self.audioMessageFinderModule.checkAndDo(mes, vk, self.storage)
            if result:
                return
