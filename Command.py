# @rebootstr

import random
from Message import Message
from MyVKLib.vk import VK
import time

commands = ["/status",
            "/pause",
            "/resume",
            "/d",
            "/errors"]

PAUSE = False
BOT_STARTED_TIME = time.time()


def is_command(mes: Message):
    return mes.get_text().split(" ")[0] in commands


def execute(mes: Message, vk: VK):
    global PAUSE

    index = commands.index(mes.get_text().split(" ")[0])

    if PAUSE and index != 2:
        return
    elif index == 0:  # status
        if mes.is_out_or_myself(vk.user_id):
            _send_status(mes, vk)
    elif index == 1:  # pause
        if mes.is_out_or_myself(vk.user_id):
            PAUSE = True
            _send_pause(mes, vk)
    elif index == 2:  # resume
        if mes.is_out_or_myself(vk.user_id):
            PAUSE = False
            _send_resume(mes, vk)
    elif index == 3:  # delete
        if mes.is_out_or_myself(vk.user_id):
            _delete_function(mes, vk)
    elif index == 4:  # message_pool_clear
        if mes.is_myself(vk.user_id):
            vk.send_error_in_mes("Pool Cleared")


def _send_status(mes: Message, vk: VK):
    work_time_sec = time.time()-BOT_STARTED_TIME
    work_time = time.gmtime(work_time_sec)
    format_time = ""
    count_days = int(work_time_sec/86400)
    if count_days != 0:
        format_time += f"{count_days} days "
    format_time += "%H:%M:%S"
    str_time = time.strftime(format_time, work_time)
    _reply_text(mes, vk, f"<Online.{str_time}>")


def _send_pause(mes: Message, vk: VK):
    _reply_text(mes, vk, "Paused")


def _send_resume(mes: Message, vk: VK):
    _reply_text(mes, vk, "Resumed")


def _delete_function(mes: Message, vk: VK):
    message = vk.rest.post("messages.getById", message_ids=mes.get_id()).json()["response"]["items"][0]
    if "reply_message" not in message.keys():
        return

    # поиск админов
    can_delete = [vk.user_id]
    is_i_admin = False
    if mes.is_chat():
        r = vk.rest.post("messages.getConversationMembers", peer_id=mes.get_peer())
        for item in r.json()['response']['items']:
            if "is_admin" not in item.keys():  # put NOT admins
                can_delete.append(item['member_id'])
            if not is_i_admin and "is_admin" in item.keys() and item['member_id'] == vk.user_id:  # if i admin
                is_i_admin = True
        if not is_i_admin:
            can_delete = [vk.user_id]

    if mes.is_myself(vk.user_id):
        global_delete = 0
    else:
        global_delete = 1

    reply_date = message["reply_message"]["date"]
    if int(time.time()) - reply_date > 86100 and global_delete:  # 23:55:00
        limit_date = int(time.time()) - 86100
    else:
        limit_date = reply_date

    offset = 0
    ids = []
    while_exit = True
    while while_exit:
        r = vk.rest.post("messages.getHistory", count=100, peer_id=mes.get_peer(), offset=offset)
        for item in r.json()['response']['items']:
            if item['date'] >= limit_date:
                if "action" not in item.keys():
                    if item['from_id'] in can_delete:
                        ids.append(item['id'])
            else:
                while_exit = False
                break
        offset += 50

    # Удаление
    print("deleting")

    count = len(ids)
    times = 0
    while count > 0:
        if count >= 1000:
            r = vk.rest.post("messages.delete",
                             message_ids=str(ids[times * 1000:times * 1000 + 1000])[1:-1],
                             delete_for_all=global_delete)
            times += 1
            count -= 1000
        else:
            r = vk.rest.post("messages.delete",
                             message_ids=str(ids[times * 1000:times * 1000 + count])[1:-1],
                             delete_for_all=global_delete)
            count = 0
        print(r.text)
    # отчет об удалении
    r = _send_text(mes, vk, f"Уничтожено {len(ids) - 1} сообщений(я) :)")
    time.sleep(5)
    # удаление отчета
    r = vk.rest.post("messages.delete", message_ids=r.json()['response'], delete_for_all=global_delete)


def _send_text(mes: Message, vk: VK, text: str):
    send = vk.rest.post("messages.send",
                        peer_id=mes.get_peer(),
                        message=text,
                        random_id=random.randint(-2147483648, 2147483647))
    return send


def _reply_text(mes: Message, vk: VK, text: str):
    send = vk.rest.post("messages.send",
                        peer_id=mes.get_peer(),
                        message=text,
                        reply_to=mes.get_id(),
                        random_id=random.randint(-2147483648, 2147483647))
    return send
