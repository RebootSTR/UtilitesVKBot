# @rebootstr


class Message:
    def __init__(self, data):
        self.data = data

    def get_id(self):
        return self.data[1]

    def get_flags(self):
        return self.data[2]

    def get_peer(self):
        return self.data[3]

    def get_date(self):
        return self.data[4]

    def get_text(self):
        return self.data[5]

    def get_chat_sender_id(self):
        return self.data[6]["from"]

    def is_out(self):
        return self.get_flags() & 2 != 0

    def is_out_or_myself(self, my_id):
        return self.is_out() or self.is_myself(my_id)

    def is_myself(self, my_id):
        return my_id == self.get_peer()

    def is_chat(self):
        return self.get_peer() > 2000000000

    def toString(self):
        return "Сообщение с id {} было отправлено в {} в {} по Unixtime . Его отправил {}. Текст сообщения - {}.".format(
            self.get_id(),
            "беседе с id " + str(self.get_peer()) if self.is_chat() else "ЛС",
            self.get_date(),
            "я" if self.is_out() else (self.get_chat_sender_id() if self.is_chat() else self.get_peer()),
            '"' + self.get_text() + '"'
        )
