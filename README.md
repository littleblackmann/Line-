# LINE點餐餐飲服務系統專案
> * 創作起始日：2024/04/02
> * 最後更新日：2024/04/15
> * 使用系統：Ubuntu22.04.4_Desktop
> * 後端創作者：小黑

### [LineBot更新參考網站](https://github.com/line/line-bot-sdk-python)

## 項目緣起：
1. 在快節奏的現代生活中，人們尋求更便利和有效率的方式來滿足日常需求，尤其是在餐飲服務領域。
1. 隨著智慧型手機的普及和即時通訊軟體功能的不斷強化，透過這些平台進行點餐服務已成為一種趨勢。 
1. 針對這一市場需求，我們開發了LINE點餐系統，旨在透過LINE平台，為用戶提供一個簡單、快速的線上訂餐體驗，同時為餐飲業者帶來更有效率的訂單管理和客戶服務解決方案。
        
---
### 安裝環境
> #### 更新安裝包
> `sudo apt update`

> #### 安裝Python3和PIP
> `sudo apt install python3 python3-pip -y`

> #### 安裝Flask和LINE Messaging API
> `pip install flask line-bot-sdk`

> #### 安裝MariaDB
> `sudo apt install mariadb-server -y`

> #### 設置MariaDB
> `sudo mysql_secure_installation`

> #### 安裝MariaDB的Python客戶端(為了從Python應用連接到MariaDB)
> `pip install mysql-connector-python`
---
# 本地執行
#### 下載ngrok
[Ngrok註冊網頁](https://ngrok.com/)
> #### 安裝ngrok
> `snap install ngrok`

> #### 輸入token
> `ngrok config add-authtoken [輸入你註冊完的token]`

![ng](https://hackmd.io/_uploads/SJDqAo5kA.jpg)

> #### 開啟本地執行
> `ngrok http http://localhost:9527`

![ngrok](https://hackmd.io/_uploads/ryoBLZoyC.jpg)


![ngrok1](https://hackmd.io/_uploads/BkJxDZsJR.jpg)
![ngrok2](https://hackmd.io/_uploads/rkJlDbjyC.jpg)

---
# GCP執行背景Ngrok
> #### 安裝ngrok
> `sudo snap install ngrok`

> #### 安裝jq
> `sudo apt install jq`

> #### 輸入token
> `ngrok config add-authtoken [輸入你註冊完的token]`

#### 找到ngrok位置
`find ~ -name ngrok`
會顯示 
/home/littleblack0830/snap/ngrok                     # 改成自己位置
/home/littleblack0830/snap/ngrok/138/.config/ngrok。 # 改成自己位置

# 啟動ngrok.sh
### chmod +x ngrok.sh
```
#!/bin/bash

# 啟動 ngrok 在後台，並重定向輸出到日誌文件
/snap/bin/ngrok http http://localhost:9527 > ngrok.log 2>&1 &

echo "Waiting for ngrok to start..."
sleep 20 # 增加等待時間，確保 ngrok 完全啟動

# 嘗試從 ngrok 的 API 取得公開 URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url')

if [ -z "$NGROK_URL" ]; then
     echo "Failed to obtain ngrok URL."
     echo "Checking ngrok.log for errors..."
     cat ngrok.log
else
     echo "ngrok URL: $NGROK_URL"
fi
```
![ngrok-test](https://hackmd.io/_uploads/Syu-3tBx0.jpg)

#### 啟動後可以查詢是否開啟
`ps aux | grep ngrok`
![1712851957595](https://hackmd.io/_uploads/r1WX2FrgC.jpg)

#### 關閉ngrok
`kill -9 4968` [輸入查到的PID]
![1712852259775](https://hackmd.io/_uploads/Skt4pFBe0.jpg)

# 讓app.py也在背景執行
sudo apt install screen

> 輸入`screen -S app`
> 輸入`python3 app.py`
> Ctrl-A 然後按 D 就可以回到家目錄繼續做自己的事 

---

### 如果port被占用的話
> `sudo lsof -i :9527`
> 找出哪個進程正在使用端口9527。

> `sudo netstat -tuln | grep 9527`
> 這命令將顯示使用端口9527的訊息，包括進程ID（PID）。然後你可以使用kill命令終止該進程

> `sudo kill -9 PID`
> 把PID替換成你從前一步驟得到的進程ID。

---
# 資料庫建置
### 創建使用者
`CREATE USER 'new_username'@'localhost' IDENTIFIED BY 'new_password';`
### 給予全部權限
`GRANT ALL PRIVILEGES ON *.* TO 'new_username'@'localhost' WITH GRANT OPTION;`
### 立即生效
`FLUSH PRIVILEGES;`
### 創建一個Databases
`CREATE DATABASE linefood;`
### 創建一個Tables
```
CREATE TABLE orderlog (
    line_id VARCHAR(255) NOT NULL,
    order_id INT NOT NULL AUTO_INCREMENT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    meal_name VARCHAR(255) NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    PRIMARY KEY (order_id)
);

```
