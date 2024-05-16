# db_operations.py
from datetime import datetime

def query_orders(conn_pool, user_id):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()
    query = """
        SELECT order_id, meal_name, quantity, price, total_amount, order_date
        FROM orderlog
        WHERE line_id = %s
        ORDER BY order_date DESC
    """
    cursor.execute(query, (user_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders
    
def insert_order(conn_pool, user_id, burger_name, burger_price, quantity):
    # 計算總金額
    total_amount = burger_price * quantity

    # 取得當前時間
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 從連接池中獲取連接
    conn = conn_pool.get_connection()
    cursor = conn.cursor()
    try:
        # 執行插入訂單操作
        cursor.execute(
            "INSERT INTO orderlog (line_id, order_date, meal_name, quantity, price, total_amount) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, order_date, burger_name, quantity, burger_price, total_amount)
        )
        conn.commit()
        order_id = cursor.lastrowid  # 獲取新插入的訂單編號
        return order_id, f"您的訂單 {burger_name} x {quantity} 已經加入訂單，單價為 {burger_price} 元，總金額為 {total_amount} 元。"
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "無法記錄你的訂單，請稍後再試。"
    finally:
        cursor.close()
        conn.close()

def query_news(conn_pool):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()
    query = """
        SELECT content
        FROM news1st
    """
    cursor.execute(query)
    firstnews = cursor.fetchone()
    cursor.close()
    conn.close()
    return firstnews

