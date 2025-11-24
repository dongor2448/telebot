import requests
import json
from datetime import datetime
import os
from urllib.parse import quote_plus


token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]
gold_api_token = os.environ["GOLDAPI"]


def format_gold_price(data):
    # 將 Unix 時間戳轉為可讀時間（使用 UTC+8 台北時間）
    update_time = datetime.fromtimestamp(data["timestamp"])
    open_time = datetime.fromtimestamp(data["open_time"])

    # 主要價格資訊
    lines = [
        "【黃金即時報價 (XAU/USD)】",
        f"🕐 更新時間　　：{update_time.strftime('%Y年%m月%d日 %H:%M:%S')} (台北時間)",
        f"🌐 資料來源　　：{data['exchange']}",
        f"💰 當前價格　　：{data['price']:,.3f} 美元/盎司",
        f" 📈 今日開盤　　：{data['open_price']:,.3f} 美元/盎司",
        f"🔺 今日最高　　：{data['high_price']:,.3f} 美元/盎司",
        f"🔻 今日最低　　：{data['low_price']:,.3f} 美元/盎司",
        f"📈 漲　　跌　　：{data['ch']:>+,.3f} 美元 ({data['chp']:>+,.2f}%)",
        f"🛒 買　　價　　：{data['ask']:,.3f} 美元",
        f"📤 賣　　價　　：{data['bid']:,.3f} 美元",
        "",
        "【各純度黃金每公克價格（美元）】",
        f"24K (999)　：{data['price_gram_24k']:,.4f}",
        f"22K (916)　：{data['price_gram_22k']:,.4f}",
        f"21K (875)　：{data['price_gram_21k']:,.4f}",
        f"18K (750)　：{data['price_gram_18k']:,.4f}",
        f"14K (585)　：{data['price_gram_14k']:,.4f}",
        f"10K (416)　：{data['price_gram_10k']:,.4f}",
    ]

    return "\n".join(lines)


def make_gapi_request():
    api_key = gold_api_token
    symbol = "XAU"
    curr = "USD"
    date = ""

    url = f"https://www.goldapi.io/api/{symbol}/{curr}{date}"

    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.text
        return format_gold_price(json.loads(result))
    except requests.exceptions.RequestException as e:
        print("❌ Error:", str(e))


def make_er_api():
    response = requests.get("https://open.er-api.com/v6/latest/JPY")
    response.raise_for_status()

    content = json.loads(response.text)
    exchange_rate = content["rates"]["HKD"]
    formatted_output = f"💱 日元兌港元匯率：¥1 = HK${exchange_rate:.4f} 🇯🇵→🇭🇰"
    return formatted_output


msg1 = make_gapi_request()
msg2 = make_er_api()


url = f"https://api.telegram.org/bot{token}/sendMessage"
payload1 = {
    "chat_id": chat_id,
    "text": f"{msg1}",
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}

payload2 = {
    "chat_id": chat_id,
    "text": f"{msg2}",
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}

response1 = requests.post(url, data=payload1)
response1.raise_for_status()
response2 = requests.post(url, data=payload2)
response2.raise_for_status()


