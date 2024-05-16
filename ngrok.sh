#!/bin/bash

# 啟動 ngrok 在後台，並重定向輸出到日誌文件
/snap/bin/ngrok http http://localhost:9527 > ngrok.log 2>&1 &

echo "Waiting for ngrok to start..."
sleep 10 # 增加等待時間，確保 ngrok 完全啟動

# 嘗試從 ngrok 的 API 取得公開 URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url')

if [ -z "$NGROK_URL" ]; then
    echo "Failed to obtain ngrok URL."
    echo "Checking ngrok.log for errors..."
    cat ngrok.log
else
    echo "ngrok URL: $NGROK_URL"
fi
