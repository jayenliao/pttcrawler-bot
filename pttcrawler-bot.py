# coding: utf-8
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from bs4 import BeautifulSoup
import requests

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

# 爬蟲函數: 爬取 PTT 的最新文章標題
def crawl_ptt():
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    headers = {'User-Agent': 'Mozilla/5.0'}
    cookies = {'over18': '1'}  # 設定cookie繞過18歲驗證
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')

    titles = []
    for title in soup.select('.title a'):
        titles.append(title.text)

    # 回傳前五個標題作為範例
    return titles[:5]

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 如果使用者輸入 "爬蟲"，觸發爬取 PTT 的文章標題
    if user_message == "爬蟲":
        ptt_titles = crawl_ptt()  # 執行爬蟲函數
        reply = "\n".join(ptt_titles)  # 格式化回應內容

        # 回傳爬取結果給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"PTT 最新文章標題:\n{reply}")
        )
    else:
        # 回傳原始訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=user_message)
        )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
