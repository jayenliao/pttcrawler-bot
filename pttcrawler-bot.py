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
            return False, "爬取失敗，請檢查看板名稱，或是稍後再試"

        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []  # 存放結果的列表

        # 選擇包含標題、推文和日期的區塊
        for post in soup.select('div.r-ent'):
            title_elem = post.select_one('.title a')  # 文章標題
            if title_elem:
                title = title_elem.text  # 取得標題文字
                link = 'https://www.ptt.cc' + title_elem['href']  # 取得文章連結
            else:
                # 如果文章被刪除，可能會找不到連結
                title = "(本文已被刪除)"
                link = "(無連結)"

            # 取得推文數量
            push_count = post.select_one('.nrec').text.strip()  # 推文數量
            push_count = push_count if push_count else '0'  # 如果推文數量是空字串，設置為 0

            # 取得文章日期
            date = post.select_one('.meta .date').text.strip()  # 提取日期

            # 將每篇文章的資料儲存到列表中
            posts.append({
                'title': title,
                'link': link,
                'push_count': push_count,
                'date': date  # 加入文章日期
            })

        if len(posts) == 0:
            app.logger.info(f"無法從 {board} 中抓取任何文章")
            return False, "目前沒有找到任何文章"

        # 紀錄爬取結果
        app.logger.info(f"抓取到的標題數量: {len(posts)}")
        return True, posts[:-6:-1]

    except:
        app.logger.error(f"爬蟲過程中發生錯誤:")
        return False, "爬蟲過程中發生錯誤，請稍後再試"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # 如果使用者的輸入包含「爬蟲」，觸發爬取 PTT 的文章標題，「爬蟲」二字以外的輸出則視為要爬的ptt版
        if user_message[:2] == "爬蟲":
            board = user_message.replace("爬蟲", '')
            while ' ' in board:
                board = board.replace(' ', '_')
            crawling_status, posts = crawl_ptt(board)  # 執行爬蟲函數

            # 回傳爬取結果給使用者
            if crawling_status:
                # 格式化結果
                reply = ""
                for post in posts:
                    reply += f"{post['title']}\n{post['link']}\n推文數: {post['push_count']}\n日期: {post['date']}\n\n"
                text = f"PTT {board} 最新文章標題:\n{reply}"
            else:
                text = posts
        else:
            text = "若要進行PTT爬蟲，請輸入「爬蟲{看板英文名稱}」\n範例1：爬蟲Soft_Job\n範例2：爬蟲Stock"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)
        )
    except LineBotApiError as e:
        app.logger.error(f"LineBotApiError: {e}")

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
