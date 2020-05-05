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

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

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
    elif(text == "欸"):
        reply_text = "幹嘛"
    else:
        reply_text = "嘿"

    message = TextSendMessage(reply_text)
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    #app.run(host='0.0.0.0', port=port)
    app.run(port=port)
