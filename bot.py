# @rebootstr

from CommandExecutor import CommandExecutor
import Exceptions
import argparse
from Message import Message
from DataBase import DataBase
from MessagesStorage import MessagesStorage
from MyVKLib.vk import *


def check_base(base):
    try:
        base.get("settings")
    except:
        return False
    return True


def init_new_session(base):
    input("new session")
    user_token = input("Enter user_token >> ")
    base.create("settings(key TEXT, value TEXT)")
    base.append("settings", "token", user_token)


def get_token(base):
    return base.get_one_where("settings", "value", "key='token'")


def parse_messages(vk: VK, command_executor):
    updates = vk.longpoll.get_update()
    for update in updates["updates"]:
        if update[0] == 4:  # СООБЩЕНИЕ
            # print(update)
            message = Message(update)
            storage.save(message)
            if command_executor.is_command(message):
                command_executor.execute(message, vk)
            print(message.toString())


def open_base(name: str):
    _base = DataBase(name)
    # base.drop_table("settings")
    if not check_base(_base):
        init_new_session(_base)
    return _base


def vk_init():
    base = open_base(BASE_NAME)
    vk = VK(get_token(base))
    return vk


BASE_NAME = "base.db"
VERSION = "v1.18beta"


def run(vk=vk_init()):
    parser = argparse.ArgumentParser()
    parser.add_argument("-start_time", type=int)
    args = parser.parse_args()

    command_executor = CommandExecutor(args.start_time, VERSION, storage)

    print("STARTED")
    send = vk.rest.post("messages.send",
                        peer_id=vk.user_id,
                        message=f"<Started {VERSION}. {time.strftime('%H:%M:%S')}>",
                        random_id=random.randint(-2147483648, 2147483647))
    while True:
        parse_messages(vk, command_executor)


if __name__ == '__main__':
    try:
        _vk = vk_init()
        storage = MessagesStorage(_vk)
        send = _vk.rest.post("messages.send",
                             peer_id=_vk.user_id,
                             message="/pause *open new instance*",
                             random_id=random.randint(-2147483648, 2147483647))
        run(_vk)
    except Exceptions.ExitException as e:
        print(str(e))
