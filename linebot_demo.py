from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import requests
import urllib.parse
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

class GetWeather:
    def __init__(self, functions, location):
        self.functions = functions
        self.location = location

    def GetCurrent(self):
        # URL for fetching the current weather
        Request_URL = config["URL"]["observation_auto"]\
            + config["settings"]["Authorization"] + "&format=JSON"\
            + "&locationName=" + urllib.parse.quote(self.location)

        # filter out which data we need
        data = requests.get(Request_URL).json()["records"]["location"]

        # examine if the location is valid
        if not data:
            WeatherData = "target station not found"
            # print(target_station)
            return False

        # load message
        # ref: https://opendata.cwb.gov.tw/opendatadoc/DIV2/A0001-001.pdf
        CITY = data[0]["parameter"][0]["parameterValue"]
        TOWN = data[0]["parameter"][2]["parameterValue"]
        WeatherData = data[0]["weatherElement"]

        msg = CITY + TOWN + " " + self.functions + "\n\n"
        msg += "氣溫：" + WeatherData[3]["elementValue"] + "℃\n"
        msg += "濕度：" + \
            str(round(float(WeatherData[4]["elementValue"]) * 100)) + "% RH\n"
        msg += "風向：" + WeatherData[1]["elementValue"] + "°\n"
        msg += "風速：" + WeatherData[0]["elementValue"] + " m/s\n"
        return msg

app = Flask(__name__)

'''
ACCESS_TOKEN = os.environ.get(config["linebot"]["channel_access_token"])
SECRET = os.environ.get('SECRET')
'''

ACCESS_TOKEN = config["linebot"]["channel_access_token"]
SECRET = config["linebot"]["channel_secret"]
# channel access token
line_bot_api = LineBotApi(ACCESS_TOKEN)
# channel secret
handler = WebhookHandler(SECRET)


# monitor all post request info from /callback
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# handling message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    text = event.message.text

    if (text == "Hi"):
        reply_text = "Hello"
    elif(text == "你好"):
        reply_text = "哈囉"
    elif("目前天氣" in text):
        functions = "目前天氣"
        location = text[5:]
        if location:
            reply_text = GetWeather(functions, location).GetCurrent()
        else:
            reply_text = "未輸入觀測站名稱"
    else:
        reply_text = "嘿"


    message = TextSendMessage(reply_text)
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    #app.run(host='0.0.0.0', port=port)
    app.run(port=port)
