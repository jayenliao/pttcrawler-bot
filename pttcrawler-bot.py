# coding: utf-8
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

#line token
channel_access_token = 'i14cG7TnOMjMK1+8AZwUx0DM2LuqEjMvxVXg3kD7dfQfZyjXJrBNIp8snvqeo7prYOrOSPgX/QwGuRJ88Vuc8D/lsgC1P7KgBUl6q6AgHeuSxIvF3PiOy3m+RHQBq72Lnfx/tFohAjk9m9pvZsAVOwdB04t89/1O/w1cDnyilFU='
channel_secret = '1866f6be9398989f81e54bb94e527bd8'
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello! This is the Line Bot webhook service.'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #echo
    msg= event.message.text
    message = TextSendMessage(text=msg+"yoyoyoyo")
    line_bot_api.reply_message(event.reply_token,message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
