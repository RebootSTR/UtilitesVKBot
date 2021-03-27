# @rebootstr

from threading import Thread
import main as bot
from MyVKLib.vk import VK
from Slave import Slave


class SlaveStarter:

    def __init__(self, vk):
        self.vk = vk
        self.slave_main = None
        self.t_main = None
        self.slave_aggressive = None
        self.t_aggressive = None

    def start_main(self):
        self.slave_main = Slave(self.vk)
        self.t_main = Thread(target=self.slave_main.main, daemon=True)
        self.t_main.start()

    def start_aggressive(self, id, counter):
        if self.t_aggressive is not None:
            self.slave_aggressive.stop = True
        self.slave_aggressive = Slave(self.vk)
        self.t_aggressive = Thread(target=self.slave_aggressive.aggressive_mode, args=(id, counter), daemon=True)
        self.t_aggressive.start()

    def update(self):
        self.slave_main.need_update = True


BASE_NAME = "base.db"

if __name__ == '__main__':
    base = bot.open_base(BASE_NAME)
    vk = VK(bot.get_token(base))
    SlaveStarter(vk).start_main()
