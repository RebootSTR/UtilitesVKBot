# @rebootstr

from CommandExecutor import CommandExecutor
import Exceptions
import argparse
from Message import Message
from DataBase import DataBase
from MyVKLib.vk import *


def check_base(base):
    try:
        base.get_all("settings")
    except:
        return False
    return True


def init_new_session(base):
    input("new session")
    user_token = input("Enter user_token >> ")
    base.create("settings(key TEXT, value TEXT)")
    base.append("settings", "token", user_token)


def get_token(base):
    return base.get("settings", "value", "key='token'")


def parse_messages(vk: VK, command_executor):
    updates = vk.longpoll.get_update()
    for update in updates["updates"]:
        if update[0] == 4:  # СООБЩЕНИЕ
            # print(update)
            message = Message(update)
            if command_executor.is_command(message):
                command_executor.execute(message, vk)
            print(message.toString())


def open_base(name: str):
    _base = DataBase(name)
    # base.drop_table("settings")
    if not check_base(_base):
        init_new_session(_base)
    return _base


BASE_NAME = "base.db"
VERSION = "v1.14.1"


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-start_time", type=int)
    args = parser.parse_args()

    command_executor = CommandExecutor(args.start_time, VERSION)
    base = open_base(BASE_NAME)
    vk = VK(get_token(base))
    print("STARTED")
    send = vk.rest.post("messages.send",
                        peer_id=vk.user_id,
                        message=f"<Started {VERSION}. {time.strftime('%H:%M:%S')}>",
                        random_id=random.randint(-2147483648, 2147483647))
    while True:
        parse_messages(vk, command_executor)


if __name__ == '__main__':
    try:
        run()
    except Exceptions.ExitException as e:
        print(str(e))
