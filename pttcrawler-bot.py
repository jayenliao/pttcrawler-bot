# coding: utf-8
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
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
def crawl_ptt(board):
    try:
        app.logger.info(f"開始爬取 PTT {board}...")
        url = f'https://www.ptt.cc/bbs/{board}/index.html'
        headers = {'User-Agent': 'Mozilla/5.0'}
        cookies = {'over18': '1'}  # 設定cookie繞過18歲驗證
        response = requests.get(url, headers=headers, cookies=cookies)
        # 檢查請求是否成功
        if response.status_code != 200:
            app.logger.error(f"爬取失敗，狀態碼: {response.status_code}")
            return ["爬取失敗，請檢查看板名稱，或是稍後再試"]

        titles = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for title in soup.select('.title a'):
            if title is not None:
                titles.append(title.text)

        if len(titles) == 0:
            app.logger.info(f"無法從 {board} 中抓取任何文章")
            return ["目前沒有找到任何文章"]

        # 紀錄爬取結果
        app.logger.info(f"抓取到的標題數量: {len(titles)}")
        return titles[-10::-1]

    except requests.exceptions.RequestException as e:
        app.logger.error(f"爬蟲過程中發生錯誤: {e}")
        return ["爬蟲過程中發生錯誤，請稍後再試"]

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # 如果使用者的輸入包含「爬蟲」，觸發爬取 PTT 的文章標題，「爬蟲」二字以外的輸出則視為要爬的ptt版
        if "爬蟲" in user_message:
            board = user_message.replace("爬蟲", '')
            while ' ' in board:
                board = board.replace(' ', '_')
            ptt_titles = crawl_ptt(board)  # 執行爬蟲函數
            reply = "\n".join(ptt_titles)  # 格式化回應內容

            # 回傳爬取結果給使用者
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"PTT {board} 最新文章標題:\n{reply}")
            )
        else:
            # 回傳原始訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="若要進行PTT爬蟲，請輸入「爬蟲{看板英文名稱}」，例如：\n爬蟲Soft_Job")
            )
    except LineBotApiError as e:
        app.logger.error(f"LineBotApiError: {e}")

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
