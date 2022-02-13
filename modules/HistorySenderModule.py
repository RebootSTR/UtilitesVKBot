# @rebootstr
import random

import requests

from Message import Message
from MyVKLib.vk import VK
from modules.OneCommandModule import OneCommandModule


class HistorySenderModule(OneCommandModule):

    def _onDo(self, mes: Message, vk: VK, arg1, arg2):
        storage = arg1

        full_msg = self._get_message_by_id(mes.get_id(), vk)
        if full_msg["count"] != 0:
            if "fwd_messages" in full_msg["items"][0].keys():
                fwd = full_msg["items"][0]["fwd_messages"]
                if len(fwd) == 2:
                    from_id = fwd[0]["id"]
                    to_id = fwd[1]["id"]
                    file_name = storage.get_history(from_id, to_id, fwd[0]["peer_id"])
                    url = self._docs_getMessagesUploadServer(vk)["response"]["upload_url"]
                    r = requests.post(url, files={"file": open(file_name, "rb")}).json()
                    r = self._docs_save(vk, r["file"])
                    if "error" in r.keys():
                        vk.send_error_in_mes(r)
                        vk.rest.post("messages.send",
                                     peer_id=mes.get_peer(),
                                     message="не вышло( чекай логи бота",
                                     reply_to=mes.get_id(),
                                     random_id=random.randint(-2147483648, 2147483647))
                    vk.rest.post("messages.send",
                                 peer_id=mes.get_peer(),
                                 attachment=f"doc{vk.user_id}_{r['response']['doc']['id']}",
                                 reply_to=mes.get_id(),
                                 random_id=random.randint(-2147483648, 2147483647))

    def _docs_getMessagesUploadServer(self, vk: VK):
        return vk.rest.post("docs.getMessagesUploadServer", type="doc").json()

    def _docs_save(self, vk: VK, file):
        return vk.rest.post("docs.save", file=file, title="OpenThisAsHTML").json()
