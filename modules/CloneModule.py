# @rebootstr
from Message import Message
from MyVKLib.vk import VK
from modules.BaseModule import BaseModule
from modules.OneCommandModule import OneCommandModule


class CloneModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        try:
            jsonMessages = self.getMessagesForClone(mes, vk)
            prepared = self.prepareToClone(jsonMessages)
            self.sendPrepared(mes, vk, prepared)
            self._delete_msg(mes, vk)
        except:
            vk.send_error_in_mes(f"can't clone, get error. id={mes.get_id()}")

    @staticmethod
    def getMessagesForClone(mes: Message, vk: VK):
        include = 0
        try:
            include = int(mes.get_text().split(" ")[1])
        except:
            pass

        mes_id = mes.get_id()
        message = BaseModule._get_message_by_id(mes_id, vk)
        if "reply_message" in message["items"][0].keys():
            messages = [message["items"][0]["reply_message"]]
        else:
            messages = message["items"][0]["fwd_messages"]

        for i in range(include):
            try:
                messages = messages[0]["fwd_messages"]
            except:
                pass
        return messages

    @staticmethod
    def sendPrepared(mes: Message, vk: VK, prepared):
        for data in prepared:
            BaseModule._send_mess_with_fwd_and_att(mes, vk, data[0], data[1], data[2])

    @staticmethod
    def prepareToClone(messages):
        preparedToClone = []

        for original_message in messages:
            clone_message_text = original_message["text"]
            clone_message_fwd = ""
            if "reply_message" in original_message.keys():
                clone_message_fwd = f"{original_message['reply_message']['id']}"
            elif "fwd_messages" in original_message.keys():
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
                                    "doc",
                                    "audio_message",
                                    "wall",
                                    ]:
                        if att_type == "wall":
                            att_owner = att[att_type]["from_id"]
                        else:
                            att_owner = att[att_type]["owner_id"]
                        att_id = att[att_type]["id"]
                        att_access_key = ""
                        if "access_key" in att[att_type].keys():
                            att_access_key = att[att_type]["access_key"]
                        clone_attachments += f"{att_type}{att_owner}_{att_id}"
                        if att_access_key != "":
                            clone_attachments += f"_{att_access_key}"
                        clone_attachments += ","
                if len(clone_attachments) != 0:
                    clone_attachments = clone_attachments[:-1]

            preparedToClone.append([clone_message_text, clone_message_fwd, clone_attachments])
        return preparedToClone
