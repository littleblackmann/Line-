from linebot.v3.messaging import (
    Configuration,ApiClient,MessagingApi,
    ReplyMessageRequest,TextMessage,ImageMessage,
    LocationMessage,TemplateMessage,CarouselTemplate,
    CarouselColumn,PostbackAction
)
from linebot.v3.webhooks import PostbackEvent
from mysql.connector import pooling
from db_operations import (
    query_orders, query_news
)
from db_operations import insert_order
from linebot.exceptions import LineBotApiError

burgers = [
    {"name": "嫩", "price": 170, "image_url": ""},                    # 菜單圖片位置
    {"name": "住三重的姑姑", "price": 220, "image_url": ""},            # 菜單圖片位置
    {"name": "垃雞", "price": 200, "image_url": ""},                  # 菜單圖片位置
    {"name": "ㄐㄧㄤㄐㄧㄤㄐㄧㄤㄐㄧㄤ", "price": 180, "image_url": ""},  # 菜單圖片位置
    {"name": "太培牛", "price": 260, "image_url": ""},                 # 菜單圖片位置
    {"name": "227炸雞堡", "price": 200, "image_url": ""},              # 菜單圖片位置
    {"name": "弱", "price": 260, "image_url": ""},                    # 菜單圖片位置
    # 更多漢堡...
]

shopping_carts = {}

def handle_postback_event(event, configuration, conn_pool):
    data = event.postback.data
    #print(f"Received postback data: {data}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        #看菜單
        if data == 'menu_1': 
            image_messages = [
                ImageMessage(
                    original_content_url='', # 菜單圖片位置
                    preview_image_url=''     # 菜單圖片位置
                ),
                ImageMessage(
                    original_content_url='', # 菜單圖片位置
                    preview_image_url=''     # 菜單圖片位置
                )
                
            ]
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=image_messages)
        
        # 查地址
        elif data == 'location_1':
            location_message = LocationMessage(
                title='',    
                address='',  # 替換為你的餐廳地址
                latitude=,   # 放經緯度
                longitude=   # 放經緯度
            )
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[location_message])
        
        # 下訂單
        elif data == 'order':
            columns = [
                CarouselColumn(
                    thumbnail_image_url=burger['image_url'],
                    title=burger['name'],
                    text=f"價格：{burger['price']}元。",
                    actions=[
                        PostbackAction(
                            label="選擇這個",
                            display_text=f"選擇了{burger['name']}",
                            data=f"select_{burger['data']}"
                        )
                    ]
                ) for burger in burgers
            ]
            carousel_template = CarouselTemplate(columns=columns)
            template_message = TemplateMessage(alt_text="請選擇你想要的漢堡", template=carousel_template)
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[template_message])

        # 配合order選擇數量
        elif data.startswith('select_'):
            burger_id = data.split('select_')[1]
            columns = [
                CarouselColumn(
                    thumbnail_image_url='',  # x1
                    title='選擇數量',
                    text='您想要幾份呢？',
                    actions=[
                        PostbackAction(label='1份', display_text='1份', data=f'qty_{burger_id}_1')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='',  # x2
                    title='選擇數量',
                    text='您想要幾份呢？',
                    actions=[
                        PostbackAction(label='2份', display_text='2份', data=f'qty_{burger_id}_2')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='',  # x3
                    title='選擇數量',
                    text='您想要幾份呢？',
                    actions=[
                        PostbackAction(label='3份', display_text='3份', data=f'qty_{burger_id}_3')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='',  # x4
                    title='選擇數量',
                    text='您想要幾份呢？',
                    actions=[
                        PostbackAction(label='4份', display_text='4份', data=f'qty_{burger_id}_4')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='',  # x5
                    title='選擇數量',
                    text='您想要幾份呢？',
                    actions=[
                        PostbackAction(label='5份', display_text='5份', data=f'qty_{burger_id}_5')
                    ]
                ),
            ]
            carousel_template = CarouselTemplate(columns=columns)
            template_message = TemplateMessage(alt_text="選擇數量", template=carousel_template)
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[template_message])
        
        # 選擇數量後加入購物車    
        elif data.startswith('qty_'):
            parts = data.split('_')
            selected_burger = None
    
            if len(parts) == 4:
                _, burger, id, quantity = parts
                burger_id = f"{burger}_{id}"
                quantity = int(quantity)
        
         # 根據burger_id找到對應的漢堡
                selected_burger = next((burger for burger in burgers if burger['data'] == burger_id), None)
        
                if selected_burger:
                    # 假設有一個函數add_to_cart用於將商品加入購物車
                    add_to_cart(event.source.user_id, selected_burger, quantity)
                    reply_text = f"{selected_burger['name']} x {quantity} 已加入您的購物車，請點擊下方購物車進行確認"
                else:
                    reply_text = "沒有找到相應的漢堡選項。"
            else:
                reply_text = "操作失敗，請重試。"
    
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)])
    
            # 發送回覆訊息
            try:
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message_with_http_info(reply_message)
            except LineBotApiError as e:
                print(f"Failed to reply to the event due to an error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        # 查紀錄
        elif data == 'query_records':
            orders = query_orders(conn_pool, event.source.user_id)
            if orders:
                reply_text = "您最近的訂單紀錄如下：\n"
                for order_id, meal_name, quantity, price, total_amount, order_date in orders:
                    reply_text += f"訂單編號: {order_id}, 日期: {order_date}, 餐點: {meal_name}, 數量: {quantity}, 單價: {price}, 總金額: {total_amount}\n\n"
            else:
                reply_text = "您目前沒有訂單紀錄。"
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)])
            
            
        elif data == 'view_cart':
            view_cart(event.reply_token, event.source.user_id, configuration)
        elif data.startswith('delete_'):
            # 從 data 字串中提取 burger_id
            _, burger_id = data.split('_', 1)
            # 實作刪除商品的函數
            delete_result = delete_from_cart(event.source.user_id, burger_id)
            # 傳送操作結果給用戶
            send_reply_message(event.reply_token, delete_result, configuration)
        elif data == 'submit_order':
            # 呼叫 submit_order 函數處理提交訂單
            order_result = submit_order(event.source.user_id, conn_pool)
            # 傳送操作結果給用戶
            send_reply_message(event.reply_token, order_result, configuration)

       # 新消息
        elif data == 'query_news':
            news = query_news(conn_pool)
            if news:
                reply_text = f"最新消息： {news[0]}"
            else:
                reply_text = "目前沒有新消息。"
            reply_message = ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply_text)])

        else:
            # 如果收到了未知的選擇，發送提示給用戶
            send_reply_message(event.reply_token, "收到未知的選擇，請嘗試其他動作。", configuration)
        
        line_bot_api.reply_message_with_http_info(reply_message)
        
def view_cart(reply_token, user_id, configuration):
     if user_id not in shopping_carts or not shopping_carts[user_id]:
         reply_text = "您的購物車是空的。"
         # 發送空購物車訊息
     else:
         columns = []
         for item in shopping_carts[user_id]:
             burger = next((b for b in burgers if b['data'] == item['burger_id']), None)
             if burger:
                 columns.append(
                     CarouselColumn(
                         thumbnail_image_url=burger['image_url'],
                         title=burger['name'],
                         text=f"價格：{burger['price']}元，數量：{item['quantity']}",
                         actions=[
                             PostbackAction(
                                 label="刪除",
                                 display_text=f"已刪除{burger['name']}",
                                 data=f"delete_{item['burger_id']}"
                             ),
                             PostbackAction(
                                 label="確認送出",
                                 display_text="確認送訂單",
                                 data="submit_order"
                             )
                         ]
                     )
                 )
         carousel_template = CarouselTemplate(columns=columns)
         template_message = TemplateMessage(alt_text="您的購物車", template=carousel_template)
        
         # 發送範本訊息
         try:
             with ApiClient(configuration) as api_client:
                 line_bot_api = MessagingApi(api_client)
                 reply_message = ReplyMessageRequest(reply_token=reply_token, messages=[template_message])
                 line_bot_api.reply_message_with_http_info(reply_message)
         except Exception as e:
             print(f"發送購物車視圖失敗: {e}")        
                              
def add_to_cart(user_id, burger, quantity):
     # 這裡假設有一個全域字典來儲存購物車數據
    if user_id not in shopping_carts:
        shopping_carts[user_id] = []
        
     # 檢查商品是否已經在購物車中，如果是，則增加其數量
    for item in shopping_carts[user_id]:
        if item['burger_id'] == burger['data']:
            item['quantity'] += quantity
            break
    # 如果商品不在購物車中，新增新的條目        
    else: 
        shopping_carts[user_id].append({
            'burger_id': burger['data'],
            'name': burger['name'],
            'price': burger['price'],
            'quantity': quantity
        })

def delete_from_cart(user_id, burger_id):
    if user_id in shopping_carts:
        shopping_carts[user_id] = [item for item in shopping_carts[user_id] if item['burger_id'] != burger_id]
        return "指定商品已從購物車中刪除。"
    else:
        return "購物車為空。"

def send_reply_message(reply_token, text, configuration):
     try:
         with ApiClient(configuration) as api_client:
             line_bot_api = MessagingApi(api_client)
             reply_message = ReplyMessageRequest(
                 reply_token=reply_token,
                 messages=[TextMessage(text=text)]
             )
             line_bot_api.reply_message_with_http_info(reply_message)
     except Exception as e:
         print(f"發送訊息失敗: {e}")
            
def submit_order(user_id, conn_pool):
    if user_id not in shopping_carts or not shopping_carts[user_id]:
        return "您的購物車是空的。"
        
    # 初始化一個空字串來收集訂單詳情
    order_details = ""

    # 初始化總金額為0
    total_amount = 0    
          
    try:
        order_ids = []  # 存儲所有訂單編號
        # 呼叫 insert_order 插入資料庫
        for item in shopping_carts[user_id]:
            order_id, insert_result = insert_order(conn_pool, user_id, item['name'], item['price'], item['quantity'])
            # 累加每個項目的金額
            item_total = item['price'] * item['quantity']
            total_amount += item_total
            # 將每個項目的詳情加入訂單詳情字串
            order_details += f"{item['name']} x {item['quantity']}份，單價：{item['price']}元，小計：{item_total}元\n\n"
            # order_details += f"{item['name']} x {item['quantity']}份，單價：{item['price']}元，小計：{item_total}元\n\n"
            order_ids.append(order_id)
            print(insert_result) # 或根據需要處理這個結果

        # 清空購物車
        del shopping_carts[user_id]

        # 建立訂單確認訊息
        #final_message = "您的訂單已提交成功！\n" + "訂單詳情：\n" + order_details + f"總金額：{total_amount}元\n\n請在結帳時出示此畫面給櫃台工作人員，以便他們進行確認和處理！"
        final_message = f"您的訂單已提交成功！\n訂單編號：{', '.join(map(str, order_ids))}\n訂單詳情：\n{order_details}總金額：{total_amount}元\n\n請在結帳時出示此畫面給櫃台工作人員，以便他們進行確認和處理！"
        return final_message        
    except Exception as e:
        print(f"提交訂單時發生錯誤: {e}")
        return "提交訂單時出現錯誤，請稍後再試。"     

