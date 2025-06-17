# ip_blocker.py
import json
from datetime import datetime
from datetime import datetime, timedelta


IP_LOG_FILE = "ip_log.json"
WHITELISTED_IPS = ["127.0.0.1", "192.168.1.100"]

def load_ip_data():
    try:
        with open(IP_LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_ip_data(data):
    with open(IP_LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_ip(ip):
    auto_reset_ip_log()
    data = load_ip_data()
    today = datetime.now().strftime("%Y-%m-%d")
    if ip not in data:
        data[ip] = {"count": 1, "last": today}
    else:
        if data[ip]["last"] != today:
            data[ip]["count"] = 1
            data[ip]["last"] = today
        else:
            data[ip]["count"] += 1
    save_ip_data(data)
    
    # nếu cần kiểm tra số lần → làm ở app.py

    return data[ip]["count"]


def is_ip_blocked(ip, limit=3):
    data = load_ip_data()
    if ip in data and data[ip]["count"] >= limit:
        return True
    return False

def auto_reset_ip_log():
    data = load_ip_data()
    today = datetime.now().strftime("%Y-%m-%d")

    last_reset_str = data.get("last_reset_date")
    if last_reset_str:
        last_reset = datetime.strptime(last_reset_str, "%Y-%m-%d")
        if datetime.now() - last_reset >= timedelta(days=7):
            # Reset toàn bộ IP (trừ last_reset_date)
            data = {"last_reset_date": today}
            save_ip_data(data)
    else:
        # Nếu chưa có ngày reset → tạo luôn
        data["last_reset_date"] = today
        save_ip_data(data)        