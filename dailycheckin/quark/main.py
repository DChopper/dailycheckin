import json
import os
import requests
from dailycheckin import CheckIn


class Quark(CheckIn):
    name = "夸克网盘"

    def __init__(self, check_item: dict):
        self.check_item = check_item
        self.cookie = check_item.get("refresh_token")
        self.user_agent = ""

    def check_sign_status(self):
        state_url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info?pr=ucpro&fr=pc&uc_param_str="
        headers = {
            "Cookie": self.cookie,
            "User-Agent": self.user_agent
        }

        try:
            state_response = requests.get(state_url, headers=headers)
            state_response.raise_for_status()
        except requests.RequestException as e:
            print(f"{self.name} 请求失败，请检查Cookie或网络连接是否正确。")
            print(e)
            return []

        response = state_response.json()
        sign = response["data"]["cap_sign"]

        if sign["sign_daily"]:
            number = sign["sign_daily_reward"] / (1024 * 1024)
            progress = (sign["sign_progress"] / sign["sign_target"]) * 100
            return [
                {
                    "name": "夸克网盘",
                    "value": f"今日已签到获取{number}MB，进度{progress}%",
                }
            ]

    def perform_sign(self):
        sign_url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign?pr=ucpro&fr=pc&uc_param_str="
        params = {
            "sign_cyclic": True
        }
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.cookie,
            "User-Agent": self.user_agent
        }

        try:
            sign_response = requests.post(sign_url, headers=headers, json=params)
            sign_response.raise_for_status()
        except requests.RequestException as e:
            print(f"{self.name} 签到请求失败，请检查Cookie或网络连接是否正确。")
            print(e)
            return []

        data_response = sign_response.json()
        mb = data_response["data"]["sign_daily_reward"] / 2048
        reward_msg = f"签到成功,获取到{mb}MB!"
        return [
            {
                "name": "夸克网盘",
                "value": reward_msg,
            }
        ]

    def main(self):
        status_msg = self.check_sign_status()
        if status_msg:
            return status_msg

        sign_reward_msg = self.perform_sign()
        if sign_reward_msg:
            return sign_reward_msg

        return [{"name": "夸克网盘", "value": "签到失败，请检查配置或网络连接"}]


if __name__ == "__main__":
    # 假设这里的datas变量是从config.json读取的配置信息
    with open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"),
        encoding="utf-8",
    ) as f:
        datas = json.loads(f.read())
    _check_item = datas.get("QUARK", [])[0]
    print(_check_item)
    print(Quark(check_item=_check_item).main())