import httpx
import json
import random
import threading
import string
import time
import names
import os
import sys
from colorama import Fore, init

init(autoreset=True)

thread_lock = threading.Lock()

class Phone:
    def __init__(self, api_key, phone_id) -> None:
        self.api_key = api_key
        self.phone_id = phone_id

    def get_number(self) -> dict:
        token = self.api_key
        country = "india"
        operator = "virtual21"
        product = "instagram"

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
        }

        response = httpx.get(
            "https://5sim.net/v1/user/buy/activation/"
            + country
            + "/"
            + operator
            + "/"
            + product,
            headers=headers,
        ).json()

        return {
            "number": response["phone"],
            "phone_id": response["id"],
            "price": response["price"],
        }

    def get_balance(self) -> int:
        token = self.api_key

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
        }

        return int(
            round(
                httpx.get("https://5sim.net/v1/user/profile", headers=headers).json()[
                    "balance"
                ],
                3,
            )
        )

    def get_code(self):
        token = self.api_key
        c_id = self.phone_id

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
        }

        tries = 0
        while tries < 30:
            response = httpx.get(
                "https://5sim.net/v1/user/check/" + str(c_id), headers=headers
            ).json()
            if response["status"] == "RECEIVED":
                if response["sms"]:
                    return response["sms"][0]["code"]
            else:
                time.sleep(2)
                tries += 1

        return False

    def finish_order(self) -> None:
        token = self.api_key
        c_id = self.phone_id

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
        }

        httpx.get("https://5sim.net/v1/user/finish/" + str(c_id), headers=headers)

    def cancel_order(self) -> None:
        token = self.api_key
        c_id = self.phone_id

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
        }

        httpx.get("https://5sim.net/v1/user/cancel/" + str(c_id), headers=headers)


class Console:
    @staticmethod
    def _time():
        return time.strftime("%H:%M:%S", time.gmtime())

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def sprint(content: str, status: bool) -> None:
        thread_lock.acquire()
        sys.stdout.write(
            f"[{Fore.LIGHTBLUE_EX}{Console()._time()}{Fore.RESET}] {Fore.GREEN if status else Fore.RED}{content}"
            + "\n"
        )
        thread_lock.release()


class Generator:
    def __init__(self, proxy: any) -> None:
        with open('config.json','r') as config:
            self.config = json.load(config)

        self.client = httpx.Client(timeout=1000)

        usernames = open('usernames.txt','r').read().splitlines()

        if len(usernames) == 0:
            self.username = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(10)
            )
        else:
            self.username = str(random.choice(usernames)) + ''.join(random.choice(string.digits)for _ in range(4))

        self.password = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(10)
        )

        self.firstname = names.get_full_name()
        self.sms_key = self.config['api_key']

        if not proxy:
            self.proxy = None
        else:
            self.proxy = "http://" + str(proxy)
        init_phone = Phone(self.sms_key, None)

        get_number = init_phone.get_number()
        self.number, self.phone_id, self.phone_price = (
            get_number["number"],
            get_number["phone_id"],
            get_number["price"],
        )
        Console().sprint(
            f"Phone Number: {self.number}, Price: {self.phone_price}", True
        )
        Console().sprint(f"Username: {self.username}", True)
        Console().sprint(f"Password: {self.password}", True)
        Console().sprint(f"Full Name: {self.firstname}", True)
        Console().sprint(f"Proxy: {self.proxy}", True)

    def __main__(self) -> None:
        # Tasks
        try:
            self.create_client()

        except KeyError:
            Console().sprint("Could not get cookies/headers", False)
            return

        except IndexError:
            Console().sprint("Could not get cookies/headers", False)
            return

        if not self.sumbit_form1():
            Console().sprint("Could not fill in needed information [1]", False)
            Phone(self.sms_key, self.phone_id).cancel_order()
            return

        if not self.check_age():
            Console().sprint("Could not fill in needed information [2]", False)
            Phone(self.sms_key, self.phone_id).cancel_order()
            return

        if not self.send_phone():
            Console().sprint("Could not send phone number", False)
            Phone(self.sms_key, self.phone_id).cancel_order()
            return

        if not self.sumbit_final_form():
            Console().sprint("Failed to create account", False)
            Phone(self.sms_key, self.phone_id).cancel_order()
            return
        else:
            Console().sprint(f"Created Account {self.username}:{self.password}", True)

            with open("Accounts.txt", "a") as accounts:
                accounts.write(f"{self.username}:{self.password}" + "\n")

    def create_client(self) -> None:
        self.client.headers.update(
            {
                "authority": "www.instagram.com",
                "accept": "*/*",
                "accept-language": "en-CA,en;q=0.9",
                "dnt": "1",
                "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-httpx": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            }
        )

        get_cookies = self.client.get("https://www.instagram.com/accounts/emailsignup/")
        self.csrf = (
            get_cookies.headers["set-cookie"].split("csrftoken=")[1].split(";")[0]
        )
        self.mid = get_cookies.headers["set-cookie"].split("mid=")[1].split(";")[0]
        self.ig_did = (
            get_cookies.headers["set-cookie"].split("ig_did=")[1].split(";")[0]
        )
        self.ig_nrcb = (
            get_cookies.headers["set-cookie"].split("ig_nrcb=")[1].split(";")[0]
        )
        self.insta_ajax = (
            str(get_cookies.content).split('"rollout_hash":"')[1].split('","')[0]
        )

        self.client.cookies.update(
            {
                "csrftoken": self.csrf,
                "mid": self.mid,
                "ig_did": self.ig_did,
                "ig_nrcb": self.ig_nrcb,
            }
        )

        self.client.headers.update(
            {
                "origin": "https://www.instagram.com",
                "referer": "https://www.instagram.com/accounts/emailsignup/",
                "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "script",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            }
        )

        get_instagram_data = self.client.get(
            "https://www.instagram.com/static/bundles/es6/ConsumerLibCommons.js/02a4cdfe844e.js"
        ).text
        self.app_id = (
            str(get_instagram_data)
            .split("instagramWebDesktopFBAppId='")[1]
            .split("',e.igLiteAppId")[0]
        )
        self.asbd_id = str(get_instagram_data).split("ASBD_ID='")[1][:6]

        self.client.headers.update(
            {
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                "x-asbd-id": self.asbd_id,
                "x-csrftoken": self.csrf,
                "x-ig-app-id": self.app_id,
                "x-ig-www-claim": "0",
                "x-instagram-ajax": self.insta_ajax,
                "x-requested-with": "XMLHttpRequest",
            }
        )

    def sumbit_form1(self) -> bool:
        data = {
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}",
            "phone_number": self.number,
            "username": self.username,
            "first_name": self.firstname,
            "client_id": self.mid,
            "seamless_login_enabled": 1,
            "opt_into_one_tap": False,
        }

        register = self.client.post(
            "https://www.instagram.com/accounts/web_create_ajax/attempt/", data=data
        )

        try:
            assert register.status_code == 200 and register.json()["status"] == "ok"
        except AssertionError:
            return False
        else:
            return True

    def check_age(self) -> bool:
        self.day, self.month, self.year = (
            random.randint(1, 28),
            random.randint(1, 12),
            random.randint(1980, 2000),
        )
        data = {
            "day": self.day,
            "month": self.month,
            "year": self.year,
        }

        check_age = self.client.post(
            "https://www.instagram.com/web/consent/check_age_eligibility/", data=data
        )

        try:
            assert check_age.status_code == 200 and check_age.json()["status"] == "ok"
        except AssertionError:
            return False
        else:
            return True

    def send_phone(self) -> bool:
        data = {
            "client_id": self.mid,
            "phone_number": self.number,
            "phone_id": None,
            "big_blue_token": None,
        }

        send_code = self.client.post(
            "https://www.instagram.com/accounts/send_signup_sms_code_ajax/", data=data
        )

        try:
            assert (
                send_code.status_code == 200
                and send_code.json()["status"] == "ok"
                and send_code.json()["sms_sent"] is True
            )
        except AssertionError:
            return False
        else:
            return True

    def sumbit_final_form(self) -> bool:
        code = Phone(self.sms_key, self.phone_id).get_code()

        data = {
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}",
            "phone_number": self.number,
            "username": self.username,
            "first_name": self.firstname,
            "month": self.month,
            "day": self.day,
            "year": self.year,
            "sms_code": code,
            "client_id": self.mid,
            "seamless_login_enabled": 1,
            "tos_version": "row",
        }

        Console().sprint(f"Dob: {self.year}-{self.month}-{self.day}", True)

        sumbit = self.client.post(
            "https://www.instagram.com/accounts/web_create_ajax/", data=data
        )

        try:
            assert (
                sumbit.status_code == 200
                and sumbit.json()["account_created"] is True
                and sumbit.json()["status"] == "ok"
            )
        except AssertionError:
            return False

        Phone(self.sms_key, self.phone_id).finish_order()
        return True

if __name__ == '__main__':
    Console().clear()

    os.system('title Floppa - Instagram Account Generator')

    with open('config.json','r') as config:
        config = json.load(config)

    for _ in range(int(config['thread_count'])):
        if config['proxyless']:
            current_thread = threading.Thread(target=Generator(
                False,
            ).__main__).start()

        else:
            current_thread = threading.Thread(target=Generator(
                random.choice(open('proxies.txt','r').read().splitlines()),
            ).__main__).start()

            