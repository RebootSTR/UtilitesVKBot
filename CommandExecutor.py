# @rebootstr

import random

import Exceptions
from Message import Message
from MyVKLib.vk import VK
import time


class CommandExecutor:
    def __init__(self, start_time, bot_version):
        if start_time is None:
            self.BOT_STARTED_TIME = time.time()
        else:
            self.BOT_STARTED_TIME = start_time
        self.bot_version = bot_version
        self.commands = ["/status",
                         "/pause",
                         "/resume",
                         "/d",
                         "/errors",
                         "/update",
                         "/clone",
                         "/get_id"]

        self.PAUSE = False

    def is_command(self, mes: Message):
        return mes.get_text().split(" ")[0] in self.commands

    def execute(self, mes: Message, vk: VK):
        index = self.commands.index(mes.get_text().split(" ")[0])

        if self.PAUSE and index != 2:
            return
        elif index == 0:  # status
            if mes.is_out_or_myself(vk.user_id):
                self._send_status(mes, vk)
        elif index == 1:  # pause
            if mes.is_out_or_myself(vk.user_id):
                self.PAUSE = True
                self._send_pause(mes, vk)
        elif index == 2:  # resume
            if mes.is_out_or_myself(vk.user_id):
                self.PAUSE = False
                self._send_resume(mes, vk)
        elif index == 3:  # delete
            if mes.is_out_or_myself(vk.user_id):
                self._delete_function(mes, vk)
        elif index == 4:  # message_pool_clear
            if mes.is_myself(vk.user_id):
                vk.send_error_in_mes("Pool Cleared")
        elif index == 5:  # update
            if mes.is_out_or_myself(vk.user_id):
                self._update(mes, vk)
        elif index == 6:  # clone
            if mes.is_out_or_myself(vk.user_id):
                try:
                    self._clone_and_send(mes, vk)
                except:
                    vk.send_error_in_mes(f"can't clone, get error. id={mes.get_id()}")

        elif index == 7:  # get message id
            if mes.is_out_or_myself(vk.user_id):
                self._send_msg_id(mes, vk)

    def _send_msg_id(self, mes: Message, vk: VK):
        message = self._get_message_by_id(mes.get_id(), vk)
        if message["count"] != 0:
            message = message["items"][0]
            if len(message["fwd_messages"]) != 0:
                message_id = message["fwd_messages"][0]["id"]
            elif "reply_message" in message.keys():
                message_id = message["reply_message"]["id"]
            else:
                return
            self._reply_text(mes, vk, str(message_id))

    def _get_message_by_id(self, id, vk):
        return vk.rest.post("messages.getById", message_ids=id).json()["response"]

    def _clone_and_send(self, mes: Message, vk: VK):
        message = self._get_message_by_id(mes.get_id(), vk)
        if message["count"] != 0:
            message = message["items"][0]
            if len(message["fwd_messages"]) != 0:
                for original_message in message["fwd_messages"]:
                    clone_message_text = original_message["text"]
                    clone_message_fwd = ""
                    if "fwd_messages" in original_message.keys():
                        for original_message_fwd in original_message["fwd_messages"]:
                            clone_message_fwd += f"{original_message_fwd['id']},"
                        if len(clone_message_fwd) != 0:
                            clone_message_fwd = clone_message_fwd[:-1]

                    clone_attachments = ""
                    if "attachments" in original_message.keys():
                        for att in original_message["attachments"]:
                            att_type = att["type"]
                            if att_type in ["photo",
                                            "video",
                                            "audio",
                                            # "doc",
                                            "audio_message",
                                            "wall",
                                            ]:
                                att_owner = att[att_type]["owner_id"]
                                att_id = att[att_type]["id"]
                                att_access_key = ""
                                if "access_key" in att.keys():
                                    att_access_key = att["access_key"]
                                clone_attachments += f"{att_type}{att_owner}_{att_id}"
                                if att_access_key != "":
                                    clone_attachments += f"_{att_access_key}"
                                clone_attachments += ","
                        if len(clone_attachments) != 0:
                            clone_attachments = clone_attachments[:-1]
                    self._send_mess_with_fwd_and_att(mes, vk, clone_message_text, clone_message_fwd, clone_attachments)
        self._delete_msg(mes, vk)

    def _delete_msg(self, mes: Message, vk: VK):
        delete = vk.rest.post("messages.delete",
                              message_ids=mes.get_id(),
                              delete_for_all=0 if mes.is_myself(vk.user_id) else 1)

    def _send_mess_with_fwd_and_att(self, mes: Message, vk: VK, text, fwd, att):
        send = vk.rest.post("messages.send",
                            peer_id=mes.get_peer(),
                            message=text,
                            attachment=att,
                            forward_messages=fwd,
                            random_id=random.randint(-2147483648, 2147483647))

    def _update(self, mes: Message, vk: VK):
        self._reply_text(mes, vk, "Updating")
        raise Exceptions.ExitException("Exit To Update")

    def _send_status(self, mes: Message, vk: VK):
        work_time_sec = time.time() - self.BOT_STARTED_TIME
        work_time = time.gmtime(work_time_sec)
        format_time = ""
        count_days = int(work_time_sec / 86400)
        if count_days != 0:
            format_time += f"{count_days} days "
        format_time += "%H:%M:%S"
        str_time = time.strftime(format_time, work_time)
        self._reply_text(mes, vk, f"<Online {self.bot_version}. Work {str_time}>")

    def _send_pause(self, mes: Message, vk: VK):
        self._reply_text(mes, vk, "Paused")

    def _send_resume(self, mes: Message, vk: VK):
        self._reply_text(mes, vk, "Resumed")

    def _delete_function(self, mes: Message, vk: VK):
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
        r = self._send_text(mes, vk, f"Уничтожено {len(ids) - 1} сообщений(я) :)")
        time.sleep(5)
        # удаление отчета
        r = vk.rest.post("messages.delete", message_ids=r.json()['response'], delete_for_all=global_delete)

    def _send_text(self, mes: Message, vk: VK, text: str):
        send = vk.rest.post("messages.send",
                            peer_id=mes.get_peer(),
                            message=text,
                            random_id=random.randint(-2147483648, 2147483647))
        return send

    def _reply_text(self, mes: Message, vk: VK, text: str):
        send = vk.rest.post("messages.send",
                            peer_id=mes.get_peer(),
                            message=text,
                            reply_to=mes.get_id(),
                            random_id=random.randint(-2147483648, 2147483647))
        return send
