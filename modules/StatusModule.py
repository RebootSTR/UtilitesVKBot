# @rebootstr
import time

from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class StatusModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        BOT_STARTED_TIME = arg1
        bot_version = arg2

        work_time_sec = time.time() - BOT_STARTED_TIME
        work_time = time.gmtime(work_time_sec)
        format_time = ""
        count_days = int(work_time_sec / 86400)
        if count_days != 0:
            format_time += f"{count_days} days "
        format_time += "%H:%M:%S"
        str_time = time.strftime(format_time, work_time)
        self._reply_text(mes, vk, f"<Online {bot_version}. Uptime {str_time}>")
