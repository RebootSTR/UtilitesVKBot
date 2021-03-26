# @rebootstr

from threading import Thread
import main as bot
from MyVKLib.vk import VK
from Slave import Slave


class SlaveStarter:

    def __init__(self, vk):
        self.vk = vk
        self.slave = None
        self.t = Thread

    def start(self):
        self.slave = Slave(self.vk)
        self.t = Thread(target=self.slave.main, daemon=True)
        self.t.start()

    def update(self):
        self.slave.need_update = True


BASE_NAME = "base.db"

if __name__ == '__main__':
    base = bot.open_base(BASE_NAME)
    vk = VK(bot.get_token(base))
    SlaveStarter(vk).start()
