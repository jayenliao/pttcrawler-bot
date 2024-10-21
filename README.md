# pttcrawler-bot: PTT爬蟲LINE Bot

作者：Jay Liao (jay[at]gmail.com)

這個專案的目的是讓使用者能夠透過 Line Bot 查詢 PTT 指定看板上最新的文章，並獲取以下資訊：

- 文章標題
- 文章連結
- 推文數量
- 發文日期

這樣的應用可以幫助對 PTT 看板有興趣的使用者，即時透過 Line Bot 查詢最新資訊，無需自己編寫爬蟲程式。

## 專案架構

- Line Bot：使用 `Line Messaging API` 來建立機器人與使用者互動，處理輸入的查詢指令，並回傳結果。
- PTT 爬蟲：使用 `Request` 和 `BeautifulSoup` 來抓取 PTT 看板的最新文章資訊。
- `Flask`：後端框架，作為 Web 服務來接收並處理 Line Bot 的 `Webhook` 請求。

## 主要檔案說明

- `pttcrawler-bot.py`：主程式，處理 Line Bot 的 Webhook 請求，並觸發爬蟲抓取 PTT 資訊。
- `requirements.txt`：專案所需的 Python 套件 ￼。
- `Dockerfile`：定義如何構建 Docker 映像檔。
- `fly.toml`：Fly.io 部署配置檔案。
- `Procfile`：指定應用的啟動指令。

## 功能與使用方法

1. 使用個人LINE帳號加入ID為 `@048zatvi` 的「PTT爬蟲」聊天機器人。
2. 使用者輸入`爬蟲` 加上看板名稱，例如 `爬蟲Gossiping`。
3. 爬蟲會即時抓取該看板的最新文章資訊，包括標題、連結、推文數量和日期。
4. Line Bot 將結果回傳給使用者，呈現文章清單。

## 部署與修改

專案已經使用 `Fly.io` 進行部署。當你對程式碼進行修改後，可以用以下指令重新部署：

```bash
flyctl deploy
```

### 安裝步驟

1. Clone 專案到本地端：

    ```bash
    git clone https://github.com/yourusername/pttcrawler-bot.git
    cd pttcrawler-bot
    ```

2. 安裝所需的Python套件：

    ```bash
    pip3 install -r requirements.txt
    ```

3. 配置環境變數：

    在 `pttcrawler-bot.py` 檔案中配置以下變數：
    - `CHANNEL_ACCESS_TOKEN`：你的 Line Bot 頻道存取權杖
    - `CHANNEL_SECRET`：你的 Line Bot 頻道密鑰

4. 在本地端啟動 `Flask`：

    ```bash
    export FLASK_APP=pttcrawler-bot.py
    flask run
    ```

5. 使用 `fly.io` 或 `ngrok` 或類似服務來部署本地服務，讓 Line Bot 可以連接。

6. 在 Line Developer Console 中設定 Webhook URL，將它指向你的app，例如 `https://pttcrawler-bot.fly.dev/callback`。

<!-- ### Docker 部署

專案內已經提供了 Dockerfile，可根據需求進行 Docker 部署：

docker build -t pttcrawler-bot .
docker run -d -p 5000:5000 pttcrawler-bot -->


