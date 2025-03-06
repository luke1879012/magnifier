#!/bin/bash

# 定义日志文件路径
LOG_FILE="/var/log/magnifier_startup.log"

# 记录启动时间
echo "Starting Magnifier Service at $(date)" >> $LOG_FILE

# 切换到项目目录
cd /home/ubuntu/code/magnifier/ || { echo "Failed to enter project directory" >> $LOG_FILE; exit 1; }

# 激活虚拟环境
source venv/bin/activate || { echo "Failed to activate virtual environment" >> $LOG_FILE; exit 1; }

# 拉取最新代码
git pull || { echo "Failed to pull latest code from git" >> $LOG_FILE; exit 1; }

# 安装依赖
pip install -r requirements.txt || { echo "Failed to install dependencies" >> $LOG_FILE; exit 1; }

# 启动服务并记录日志
nohup python magnifier_server.py >> run.log 2>&1 &
SERVER_PID=$!

# 检查服务是否成功启动
if ps -p $SERVER_PID > /dev/null; then
    echo "Magnifier service started successfully with PID $SERVER_PID" >> $LOG_FILE
else
    echo "Failed to start Magnifier service" >> $LOG_FILE
    exit 1
fi

echo "Startup script completed at $(date)" >> $LOG_FILE