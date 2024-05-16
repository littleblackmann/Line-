import re
import os
from flask import Flask, request, abort
from linebot.v3.exceptions import InvalidSignatureError
from mysql.connector import pooling
from handle_postback import handle_postback_event
from db_operations import (
    query_orders, query_news
)
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,ApiClient,MessagingApi,
    ReplyMessageRequest,TextMessage,TemplateMessage,
    CarouselTemplate,CarouselColumn,PostbackAction
)
from linebot.v3.webhooks import (
    MessageEvent,PostbackEvent,TextMessageContent
)

app = Flask(__name__)

# 設定通道存取令牌和秘密
configuration = Configuration(access_token='輸入自己Line token')    
handler = WebhookHandler('輸入自己Line token')

# 資料庫連線配置
dbconfig = {
    "host": "localhost",
    "user": "black",
    "password": "black09636",
    "database": "linefood"
}

# 建立資料庫連線池
conn_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    class SimulatedPostbackEvent:
        def __init__(self, data, reply_token):
            self.postback = type('postback', (object,), {'data': data})
            self.reply_token = reply_token
            self.source = event.source
        
    data_mapping = {
        "看菜單": "menu_1",
        "餐廳位置": "location_1",
        "下訂單": "order",
        "查紀錄": "query_records",
        "購物車": "view_cart",
        "新消息": "query_news"
    }
    
    data = data_mapping.get(event.message.text)
    if data:
        simulated_event = SimulatedPostbackEvent(data, event.reply_token)
        handle_postback_event(simulated_event, configuration, conn_pool)
    else:            
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="很抱歉，我不能回覆你其他的訊息，請直接點選表單就好")]
            )

        line_bot_api.reply_message_with_http_info(reply_message)

@handler.add(PostbackEvent)
def handle_postback(event):
    handle_postback_event(event, configuration, conn_pool)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9527))
    app.run(host='0.0.0.0', port=port)
