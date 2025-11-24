import requests
import json
import datetime
import os
import time


token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]
gold_api_token = os.environ["GOLDAPI"]


def timestamp_to_hk_time(timestamp):
    dt_utc = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    dt_hk = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    return dt_hk


def format_gold_price(data):
    # 將 Unix 時間戳轉為可讀時間（使用 UTC+8 台北時間）
    dt_hk = timestamp_to_hk_time(data["timestamp"])

    # 主要價格資訊
    lines = [
        "【黃金即時報價 (XAU/HKD)】",
        f"🕐 更新時間　： {dt_hk.strftime('%Y年%m月%d日 %H:%M:%S')}",
        f"🌐 資料來源　： {data['exchange']}",
        f"💰 當前價格　： {data['price']:,.3f} 港元/盎司",
        f"📈 今日開盤　： {data['open_price']:,.3f} 港元/盎司",
        f"🔺 今日最高　： {data['high_price']:,.3f} 港元/盎司",
        f"🔻 今日最低　： {data['low_price']:,.3f} 港元/盎司",
        f"📈 漲　　跌　： {data['ch']:>+,.3f} 港元 ({data['chp']:>+,.2f}%)",
        f"🛒 買　　價　： {data['ask']:,.3f} 港元",
        f"📤 賣　　價　： {data['bid']:,.3f} 港元",
        "",
        "【各純度黃金每公克價格（港元）】",
        f"24K (999)　： {data['price_gram_24k']:,.4f}",
        f"22K (916)　： {data['price_gram_22k']:,.4f}",
        f"21K (875)　： {data['price_gram_21k']:,.4f}",
        f"18K (750)　： {data['price_gram_18k']:,.4f}",
        f"14K (585)　： {data['price_gram_14k']:,.4f}",
        f"10K (416)　： {data['price_gram_10k']:,.4f}",
    ]

    return "\n".join(lines)


def make_gapi_request():
    api_key = gold_api_token
    symbol = "XAU"
    curr = "HKD"
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
    try:
        response = requests.get("https://open.er-api.com/v6/latest/JPY")
        response.raise_for_status()

        content = json.loads(response.text)
        exchange_rate = content["rates"]["HKD"]
        last_update = content['time_last_update_utc']
        dt = datetime.datetime.strptime(last_update, "%a, %d %b %Y %H:%M:%S %z").timestamp()
        last_update_time_str = timestamp_to_hk_time(dt).strftime('%Y年%m月%d日 %H:%M:%S')

        formatted_output = [
            "【日元港元兌匯率】",
            f"🕐 最後更新 : {last_update_time_str}",
            f"💱 匯率     : ¥1 =  HK${exchange_rate:.6f} 🇯🇵→🇭🇰",
            f"💱 匯率     : $1 = JPY¥{1/exchange_rate:.4f} 🇭🇰→🇯🇵",
            f"🌐 資料來源 : {content['provider']}",
        ]
        return "\n".join(formatted_output)
    except requests.exceptions.RequestException as e:
        print("❌ Error:", str(e))


def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": f"{msg}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()


gold_info = make_gapi_request()
yen_info = make_er_api()
now = timestamp_to_hk_time(time.time()).strftime('%Y年%m月%d日 %H:%M:%S')

send_telegram_msg(
    "\n".join([
        "="*32,
        "【系統時間】",
        f"🕐 {now}",
        "="*32,
        "",
        f"{gold_info}",
        "",
        f"{yen_info}",
        "",
        "="*32
    ])
)


