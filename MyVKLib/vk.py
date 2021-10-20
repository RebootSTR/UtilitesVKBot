# @rebootstr
import time
import traceback
import random

import requests


class VK:
    def __init__(self, token):
        self.token = token
        self.rest = Rest(self)
        self.longpoll = LongPoll(self)
        self.user_id = self.rest.post("account.getProfileInfo").json()["response"]["id"]

    def send_error_in_mes(self, error):
        print("ПОЛУЧИЛ ОШИБКУ, ПРОБУЮ ОТПРАВИТЬ В ЛС")
        time_str = time.strftime("|%H:%M|")
        send = self.rest.post("messages.send",
                              peer_id=self.user_id,
                              message=time_str+error,
                              random_id=random.randint(-2147483648, 2147483647))


class Rest:
    def __init__(self, vk):
        self.vk = vk
        self.last_request = 0
        self.time_limit = 0.34
        self.captcha_loop = 0

    def wait_connection(self):
        while True:
            try:
                r = requests.get("https://api.vk.com")
                return
            except:
                time.sleep(5)

    def post(self, method, **kwargs):
        # фикс частых запросов
        delta_last_request_time = time.time() - self.last_request
        if delta_last_request_time < self.time_limit:
            time.sleep(self.time_limit - delta_last_request_time)
        while True:
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
                self.last_request = time.time()
                if "error" in r.json().keys():
                    print("Найден ERROR - обработай \n")
                    if r.json()["error"]["error_code"] == 14:  # captcha
                        print("captcha???")
                        self.captcha_loop += 1
                        if self.captcha_loop == 3:
                            break
                        time.sleep(1)
                        continue
                    elif r.json()["error"]["error_code"] == 6:  # many requests per second
                        time.sleep(0.5)
                        self.vk.send_error_in_mes("пытаюсь подождать, потому что many requests per second")
                        continue
                    elif r.json()["error"]["error_code"] == 10:  # server error :(
                        time.sleep(10)
                        continue
                    else:
                        self.vk.send_error_in_mes("Got error in post")
                        print(url)
                        print(r.text)
                        input("жду, сплю, наверное, умру")
                break
            except Exception as ex:
                print(time.ctime() + '\n ошибка post запроса')
                print("начинаю ожидание соединения")
                self.wait_connection()

        self.captcha_loop = 0
        return r

    def get(self, url, timeout):
        while True:
            try:
                r = requests.get(url, timeout=timeout)
                break
            except Exception as ex:
                waiting = time.time()
                print(time.ctime() + '\n ошибка get запроса')
                print("начинаю ожидание соединения")
                self.wait_connection()
                # self.vk.send_error_in_mes("Соединение восстановлено спустя {} секунд,"
                #                           " после исключения в методе get".format(time.time() - waiting))
        return r


class LongPoll:

    def __init__(self, vk):
        self.vk = vk
        self.params = None

    def update_keys(self):
        print("Обновляю ключи")
        data = self.vk.rest.post("messages.getLongPollServer").json()['response']
        data['wait'] = 50
        self.params = data

    def get_update(self):
        if self.params is None:
            self.update_keys()
        # print("Поиск обновлений... ", end="")
        while True:
            r = self.vk.rest.get(
                "https://{server}?act=a_check&key={key}&ts={ts}&wait={wait}&mode=2&version=3".format(
                    server=self.params['server'],
                    key=self.params['key'],
                    wait=self.params['wait'],
                    ts=self.params['ts']),
                timeout=90).json()
            if 'failed' in r.keys():
                print("Fail update, refresh keys")
                self.update_keys()
                continue
            else:
                self.params['ts'] = r['ts']
                break
        # print("Обновлено")
        return r
