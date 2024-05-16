import csv
import mysql.connector

# 資料庫連線配置
db_config = {
     "host": "localhost",
     "user": "black",
     "password": "yourpassword",
     "database": "blacktest"
}

# 連線資料庫
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# SQL 查詢語句
query = "SELECT * FROM orderlog"

# 執行查詢
cursor.execute(query)

# 取得結果
results = cursor.fetchall()

# 指定CSV檔名
csv_file_name = 'orderlog.csv'

# 將查詢結果儲存到CSV文件
with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
     writer = csv.writer(csv_file)
     # 寫入標題行，這裡根據你的orderlog表結構進行了調整
     writer.writerow(['line_id', 'order_id', 'order_date', 'meal_name', 'quantity', 'price', 'total_amount'])
     # 寫入查詢結果
     writer.writerows(results)

# 關閉資料庫連接
cursor.close()
db_conn.close()

print(f"產出CSV成功... {csv_file_name}")
