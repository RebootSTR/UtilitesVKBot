# @rebootstr

import time
import traceback
import main as bot
from MyVKLib.vk import VK
import requests
import argparse


def safe_post(url, data=None, json=None, **kwargs):
    while True:
        try:
            
            r = requests.post(url, data, json, **kwargs)
            if "error" in r.json().keys():
                time.sleep(10)
                continue
            return r
        except:
            print("err")


def safe_get(url, params=None, **kwargs):
    while True:
        try:
            r = requests.get(url, params, **kwargs)
            r.json()
            return r
        except:
            print("err")


def safe_options(url, **kwargs):
    while True:
        try:
            return requests.options(url, **kwargs)
        except:
            print("err")


class Slave:
    def __init__(self, vk):
        self.vk = vk
        self.table = None
        self.headers = None
        self.options_headers = None
        self.need_update = False
        self.open_app()

        self.options = []

    def open_app(self):
        APP_ID = 7794757
        APP_URL = "https://vk.com/app" + str(APP_ID) + "%23"
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
        pixel_get_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/start"
        if pixel_get_url not in self.options:
            options_pixel_get = safe_options(pixel_get_url, headers=self.options_headers)

        pixel_get = safe_get(pixel_get_url, headers=self.headers)
        self.table = []
        for slave in pixel_get.json()["slaves"]:
            if slave["price"] < 90000 and slave["profit_per_min"] == 1000:
                self.table.append({"id": slave["id"], "time": slave["fetter_to"]})
        return pixel_get.json()

    # minimal time
    def get_minimal(self):
        minimal = 0
        for i in range(len(self.table)):
            if self.table[i]["time"] < self.table[minimal]["time"]:
                minimal = i
        return minimal

    def get_slave(self, id):
        get_slave_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/user?id=" + str(id)
        if get_slave_url not in self.options:
            options_get_slave = safe_options(get_slave_url, headers=self.options_headers)

        get_slave = safe_get(get_slave_url, headers=self.headers)
        self.get_slave_list(id)

        return get_slave.json()

    def get_slave_list(self, id):
        get_slave_list_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/slaveList?id=" + str(id)
        if get_slave_list_url not in self.options:
            options_get_slave_list = safe_options(get_slave_list_url, headers=self.options_headers)
        get_slave_list = safe_get(get_slave_list_url, headers=self.headers)
        return get_slave_list.json()

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
                    print(f"sleep {time_left + 1} seconds")
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

    def upgrade_mode(self):
        while True:
            json = self.update()
            slave_ids = []
            for i in range(len(json["slaves"])):
                slave_ids.append(json["slaves"][i]["id"])
                count = 0
                if json["slaves"][i]["profit_per_min"]!=1000:
                    print(f'{i}: '
                          f'id: {json["slaves"][i]["id"]} '
                          f'profit: {json["slaves"][i]["profit_per_min"]} '
                          f'price: {json["slaves"][i]["price"]}')
                    count+=1
            if count == 0:
                break
            for index in input(">> ").split(" "):
                index = int(index)
                while json["slaves"][index]["profit_per_min"] != 1000:
                    print("sale ", end="")
                    print(self.sale_slave(slave_ids[index])[1])
                    print("buy ", end="")
                    buy = self.buy_slave(slave_ids[index])
                    print(buy[1])
                    if buy[0]["price"] > 35000:
                        break
                print("job")
                self.job_slave(slave_ids[index])
                print("protect")
                self.protect_slave(slave_ids[index])

    def sale_slave(self, id):
        sale_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/saleSlave"
        if sale_url not in self.options:
            options_sale_slave = safe_options(sale_url, headers=self.options_headers)
            self.options.append(sale_url)

        sale_slave = safe_post(sale_url, headers=self.headers, json={"slave_id": id})
        return [self.get_slave(id), sale_slave.json()]

    def buy_slave(self, id):
        buy_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/buySlave"
        if buy_url not in self.options:
            options_buy_slave = safe_options(buy_url, headers=self.options_headers)
            self.options.append(buy_url)

        buy_slave = safe_post(buy_url, headers=self.headers, json={"slave_id": id})
        return [self.get_slave(id), buy_slave.json()]

    def buy_fetter(self, id):
        buy_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/buyFetter"
        if buy_url not in self.options:
            options_buy_fetter = safe_options(buy_url, headers=self.options_headers)
            self.options.append(buy_url)

        buy_fetter = safe_post(buy_url, headers=self.headers, json={"slave_id": id})
        self.get_slave(id)

    def job_slave(self, id, name="0"):
        job_slave_url = "https://pixel.w84.vkforms.ru/HappySanta/slaves/1.0.0/jobSlave"
        if job_slave_url not in self.options:
            options_job_slave = safe_options(job_slave_url, headers=self.options_headers)
            self.options.append(job_slave_url)

        job_slave = safe_post(job_slave_url, headers=self.headers, json={"slave_id": id, "name": name})
        self.get_slave(id)

    def job_all_mode(self, name):
        json = self.update()
        for slave in json["slaves"]:
            if slave["profit_per_min"] == 0 and slave["price"] > 10000:
                print("job "+str(slave["id"]))
                self.job_slave(slave["id"], name)

    def buy_all_mode(self, id, min, max, name):
        if min is None:
            min = 5000
        if max is None:
            max = 1000000
        if name is None:
            name = "0"
        json = self.get_slave_list(id)
        for slave in json["slaves"]:
            if slave["fetter_to"] == 0:
                if min < slave["price"] < max:
                    print(f"buy {slave['id']} on {slave['price']}")
                    buy = self.buy_slave(slave["id"])[1]
                    if "balance" not in buy.keys():
                        print(buy)
                    else:
                        print(f"balance {buy['balance']}")
                    print("job")
                    self.job_slave(slave["id"], name)


BASE_NAME = "base.db"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", type=int)
    parser.add_argument("-job_all")
    parser.add_argument("-buy_all", type=int)
    parser.add_argument("-min", type=int)
    parser.add_argument("-max", type=int)
    parser.add_argument("-name")
    args = parser.parse_args()

    base = bot.open_base(BASE_NAME)
    vk = VK(bot.get_token(base))
    slave = Slave(vk)
    if args.id is not None:
        print(slave.buy_slave(args.id)[1])
    elif args.job_all is not None:
        slave.job_all_mode(args.job_all.replace("_", " "))
    elif args.buy_all is not None:
        slave.buy_all_mode(args.buy_all, args.min, args.max, args.name)
    slave.upgrade_mode()
