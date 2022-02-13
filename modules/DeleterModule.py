# @rebootstr
import time

from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class DeleterModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2) -> bool:
        message = vk.rest.post("messages.getById", message_ids=mes.get_id()).json()["response"]["items"][0]
        if "reply_message" not in message.keys():
            return True

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
                if item['date'] <= limit_date:
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
        r = self._send_text(mes, vk, f"Уничтожено {len(ids) - 1} сообщений(я) :)")
        time.sleep(5)
        # удаление отчета
        r = vk.rest.post("messages.delete", message_ids=r.json()['response'], delete_for_all=global_delete)
