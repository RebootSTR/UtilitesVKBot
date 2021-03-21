# @rebootstr

import Command
from Message import Message
from DataBase import DataBase
from MyVKLib.vk import *


def check_base():
    try:
        base.get_all("settings")
    except:
        return False
    return True


def init_new_session():
    input("new session")
    user_token = input("Enter user_token >> ")
    base.create("settings(key TEXT, value TEXT)")
    base.append("settings", "token", user_token)


def get_token():
    return base.get("settings", "value", "key='token'")


def parse_messages():
    updates = vk.longpoll.get_update()
    for update in updates["updates"]:
        if update[0] == 4:  # СООБЩЕНИЕ
            print(update)
            message = Message(update)
            if message.get_id() in SKIP_LIST:
                SKIP_LIST.remove(message.get_id())
                continue
            if Command.is_command(message):
                SKIP_LIST.extend(Command.execute(message, vk))
            # print(message.toString())


BASE_NAME = "base.db"
SKIP_LIST = []

if __name__ == '__main__':
    base = DataBase(BASE_NAME)
    # base.drop_table("settings")
    if not check_base():
        init_new_session()
    vk = VK(get_token())
    while True:
        parse_messages()
