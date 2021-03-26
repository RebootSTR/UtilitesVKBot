# @rebootstr

import time
import traceback

import requests


class Slave:
    def __init__(self, vk):
        self.vk = vk
        self.table = None
        self.headers = None
        self.options_headers = None
        self.need_update = False
        self.open_app()

    def open_app(self):
        APP_ID = 7794757
        APP_URL = "https://vk.com/app"+str(APP_ID)+"%23"
        DEVICE = "9b9b7af4bfe58898"
        print("superApp_Get")
        superApp_Get = self.vk.rest.post("superApp.get", device_id=DEVICE,
                                         local_time=time.strftime("%Y-%m-%dT%H:%M:%S+04:00"))
        print("apps_getEmbeddedUrl")
        apps_getEmbeddedUrl = self.vk.rest.post("apps.getEmbeddedUrl", ref="super_app", device_id=DEVICE, app_id=APP_ID,
                                                url=APP_URL)
        url = apps_getEmbeddedUrl.json()["response"]["view_url"]
        print("apps_get")
        apps_get = self.vk.rest.post("apps.get", device_id=DEVICE, app_id=APP_ID, extended=1, platform="android")
        self.headers = {"referer": url,
                        "authorization": "Bearer " + url.split("?")[1],
                        "user-agent": "Mozilla/5.0 (Linux; Android 10; POCO F1 Build/QKQ1.190828.002; wv) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile "
                                      "Safari/537.36"}
        self.options_headers = {"referer": url,
                               "user-agent": "Mozilla/5.0 (Linux; Android 10; POCO F1 Build/QKQ1.190828.002; wv) "
                                             "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile "
                                             "Safari/537.36"}

    def update(self):
        print("pixel_get")
        options_pixel_get = requests.options("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/start", headers=self.options_headers)
        pixel_get = requests.get("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/start", headers=self.headers)
        self.table = []
        for slave in pixel_get.json()["slaves"]:
            if slave["price"] < 90000 and slave["profit_per_min"] == 1000:
                self.table.append({"id": slave["id"], "time": slave["fetter_to"]})

    # minimal time
    def get_minimal(self):
        minimal = 0
        for i in range(len(self.table)):
            if self.table[i]["time"] < self.table[minimal]["time"]:
                minimal = i
        return minimal

    def get_slave(self, id):
        options_get_slave = requests.options("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                             "user?id="+str(id), headers=self.options_headers)
        options_get_slave_list = requests.options("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                                  "slaveList?id="+str(id), headers=self.options_headers)
        get_slave = requests.get("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                 "user?id="+str(id), headers=self.headers)
        get_slave_list = requests.get("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                      "slaveList?id="+str(id), headers=self.headers)
        return get_slave.json()

    def protect_slave(self, id):
        while self.get_slave(id)["fetter_to"] != 0:
            time.sleep(1)
        self.buy_fetter(id)

    def main(self):
        try:
            self.update()
            print(self.table)
            while True:
                minimal = self.get_minimal()
                print(self.table[minimal])
                time_left = self.table[minimal]["time"] - time.time()
                if time_left > 0:
                    print(f"sleep {time_left+1} seconds")
                    time.sleep(time_left + 1)
                print("buy fetter")
                self.buy_fetter(self.table[minimal]["id"])
                self.table[minimal]["time"] = time.time() + 120 * 60
                if self.need_update:
                    self.update()
                    self.need_update = False
        except Exception as ex:
            self.vk.send_error_in_mes("раб упал(((")
            traceback.print_exc()

    def buy_fetter(self, id):
        options_buy_fetter = requests.options("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                              "buyFetter", headers=self.options_headers)
        buy_fetter = requests.post("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                   "buyFetter", headers=self.headers, json={"slave_id": id})
        get_slave = requests.get("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                 "user?id="+str(id), headers=self.headers)
        get_slave_list = requests.get("https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/"
                                      "slaveList?id="+str(id), headers=self.headers)

