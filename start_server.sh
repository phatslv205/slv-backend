#!/bin/bash
echo "Đang dừng tất cả tiến trình Gunicorn cũ..."
pkill -f gunicorn
echo "Đang khởi động lại Gunicorn..."
/root/slv_project/venv/bin/gunicorn -w 3 -k sync -b 127.0.0.1:5900 run:app

