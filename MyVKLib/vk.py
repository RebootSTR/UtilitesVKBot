# @rebootstr
import traceback

import requests


class VK:
    def __init__(self, token):
        self.token = token
        self.rest = Rest(self)
        self.longpoll = LongPoll(self)
        self.user_id = self.rest.post("account.getProfileInfo").json()["response"]["id"]


class Rest:
    def __init__(self, vk):
        self.vk = vk

    def post(self, method, **kwargs):
        if 'v' not in kwargs.keys():
            kwargs["v"] = "5.126"
        if 'access_token' not in kwargs.keys():
            kwargs["access_token"] = self.vk.token
        kwargs["lang"] = "ru"
        kwargs["https"] = 1

        url = "https://api.vk.com/method/" + method + '?'
        for key, value in kwargs.items():
            url += f"{key}={value}&"
        url = url[:-1]
        try:
            r = requests.post(url)
            if "failed" in r.json().keys():
                print("Найден FAILED - обработай " + r.json())
                input()
        except Exception as ex:
            print('ошибка ' + traceback.format_exc(ex))
            input()
        return r

    def get(self, url, timeout):
        while True:
            try:
                r = requests.get(url, timeout=timeout)
                break
            except Exception as ex:
                print('ошибка get запроса ' + traceback.format_exc(ex))
        return r


class LongPoll:

    def __init__(self, vk):
        self.vk = vk
        self.params = None

    def update_keys(self):
        print("Обновляю ключи")
        data = self.vk.rest.post("messages.getLongPollServer").json()['response']
        data['wait'] = 85
        self.params = data

    def get_update(self):
        if self.params is None:
            self.update_keys()
        print("Поиск обновлений... ", end="")
        r = self.vk.rest.get(
            "https://{server}?act=a_check&key={key}&ts={ts}&wait={wait}&mode=2&version=3".format(
                server=self.params['server'],
                key=self.params['key'],
                wait=self.params['wait'],
                ts=self.params['ts']),
            timeout=90).json()
        if 'failed' in r.keys():
            self.update_keys()
        else:
            self.params['ts'] = r['ts']
        print("Обновлено")
        return r
