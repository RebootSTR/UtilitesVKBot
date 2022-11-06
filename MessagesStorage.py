# @rebootstr
import HTMLGenerator
from DataBase import DataBase
from Message import Message


def get_max_size_url(sizes):
    max_height = sizes[0]["height"]
    max_url = ""
    for size in sizes:
        if size["type"] not in "smxyzw":
            continue
        if size["height"] > max_height:
            max_height = size["height"]
            max_url = size["url"]
    return max_url


class MessagesStorage:

    def __init__(self, vk):
        self.vk = vk
        self.base = self.open_base("messages.db")

    def open_base(self, name: str):
        _base = DataBase(name)
        if not self.check_base(_base):
            # hi from 04.06.2021 21:38 i set timestamp to int. Aydar
            _base.create('messages(id INTEGER, date INTEGER, peer INTEGER, from_id INTEGER, text TEXT, PRIMARY KEY("id"))')
            _base.create('photos(photo TEXT, message_id INTEGER, FOREIGN KEY("message_id") REFERENCES "messages"("id"))')
            _base.create('other(document TEXT, message_id INTEGER, FOREIGN KEY("message_id") REFERENCES "messages"("id"))')
            _base.create('audioMessage(ogg_link TEXT, attachment TEXT, message_id INTEGER, FOREIGN KEY("message_id") REFERENCES "messages"("id"))')
        return _base

    def check_base(self, base):
        try:
            base.get("messages")
            base.get("photos")
            base.get("other")
            base.get("audioMessage")
        except:
            return False
        return True

    def save(self, mes: Message):
        mes_id = mes.get_id()
        mes_date = mes.get_date()
        mes_peer = mes.get_peer()
        mes_from_id = mes.get_chat_sender_id() if mes.is_chat() else (self.vk.user_id if mes.is_out() else mes_peer)
        mes_text = mes.get_text()
        self.base.append("messages", mes_id, mes_date, mes_peer, mes_from_id, mes_text)
        if mes.is_has_attach():
            full_msg = self.vk.rest.post("messages.getById", message_ids=mes_id).json()["response"]
            print(full_msg)
            if full_msg["count"] != 0:
                message = full_msg["items"][0]
                for attach in message["attachments"]:
                    if attach["type"] == "photo":
                        photo = attach["photo"]
                        link = f'{photo["owner_id"]}_{photo["id"]}_{photo["access_key"]}'
                        self.base.append("photos", link, mes_id)
                    elif attach["type"] == "audio_message":
                        audio = attach["audio_message"]
                        attachment = f'audio_message{audio["owner_id"]}_{audio["id"]}_{audio["access_key"]}'
                        ogg = audio["link_ogg"]
                        self.base.append("audioMessage", ogg, attachment, mes_id)

    def get_history(self, from_id, to_id, peer_id):
        _base = DataBase(self.base.name)  # open base with new connection (thread safe)
        messages = _base.get_where("messages", "*", f"id between {from_id} and {to_id} and peer={peer_id}")
        _messages = []
        names_cache = {}
        for message in messages:
            photos = _base.get_where("photos", "*", f"message_id = {message[0]}")
            audio_message = self.get_audio_message_link(_base, message[0])
            _photos = []
            for photo in photos:
                _photos.append(self.get_photo_url(photo[0]))
            if message[3] not in names_cache.keys():
                names_cache[message[3]] = self.get_name(message[3])
            _message = {
                "name": names_cache[message[3]],
                "date": message[1],
                "text": message[4],
                "photos": _photos,
                "audio_message": audio_message
            }
            _messages.append(_message)
        file_name = f"htmls/{from_id}-{to_id}.html1"
        HTMLGenerator.save_html(file_name, _messages)
        return file_name

    def get_audio_message_history(self, from_id, to_id, peer_id):
        _base = DataBase(self.base.name)  # open base with new connection (thread safe)
        messages = _base.get_where("messages", "*", f"id between {from_id} and {to_id} and peer={peer_id}")
        attachments = []
        names_cache = {}
        for message in messages:
            audio_message = self.get_audio_message_attachment(_base, message[0])
            if audio_message is not None:
                if message[3] not in names_cache.keys():
                    names_cache[message[3]] = self.get_name(message[3])
                attachments.append({
                    "name": names_cache[message[3]],
                    "date": message[1],
                    "attachment": audio_message
                })
        return attachments

    def get_name(self, user_id):
        r = self.vk.rest.post("users.get", user_ids=user_id).json()
        if "error" in r.keys():
            return "error"
        return f'{r["response"][0]["first_name"]} {r["response"][0]["last_name"]}'

    def get_photo_url(self, photo_link):
        r = self.vk.rest.post("photos.getById", photos=photo_link).json()
        if "error" in r.keys():
            return "error"
        return get_max_size_url(r["response"][0]["sizes"])

    def get_audio_message_attachment(self, base: DataBase, mes_id):
        return base.get_one_where("audioMessage", "attachment", f"message_id={mes_id}")

    def get_audio_message_link(self, base: DataBase, mes_id):
        return base.get_one_where("audioMessage", "ogg_link", f"message_id={mes_id}")
