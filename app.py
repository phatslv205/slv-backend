import eventlet
eventlet.monkey_patch() 
import os
import sys
import json
import re
import requests
import math
import base64
import openai
import fitz  # PyMuPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Response
from openai_config import call_gpt_viet
from openai import OpenAI
from dotenv import load_dotenv
from flask import url_for
import random
from extensions import db
from models.user import User
from extensions import db, migrate
from flask_migrate import Migrate
from sqlalchemy import or_, func
from models.transaction import Transaction
from sqlalchemy import func
from models.friend import Friend
from models.message import Message
from models.friend_request import FriendRequest
from flask_socketio import SocketIO, join_room, emit
from flask_socketio import SocketIO, emit, join_room
from flask_socketio import emit 
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from utils_shared import normalize_package
from pytz import timezone
from datetime import datetime
from zoneinfo import ZoneInfo          # (Python ≥3.9) – không cần cài thêm
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")   # múi giờ VN
UTC_TZ = ZoneInfo("UTC")

from datetime import timedelta
from flask import request, jsonify
from werkzeug.utils import secure_filename
from flask import request, session, redirect, render_template
from gpt_vision_ocr import extract_with_gpt_vision
from openai_config import call_gpt_lite
def generate_image_from_prompt(prompt_text):
    try:
        print("📤 Đang gửi prompt vẽ hình tới DALL·E:", prompt_text)
        client = create_openai_client()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            n=1
        )
        image_url = response.data[0].url
        if not image_url:
            print("⚠️ Không nhận được ảnh từ OpenAI.")
            return None

        # Tải ảnh về
        img_data = requests.get(image_url).content

        # Tạo tên file ngẫu nhiên
        filename = f"img_{uuid.uuid4().hex[:8]}.png"
        save_path = os.path.join("static", "images", "uploads", filename)

        with open(save_path, "wb") as f:
            f.write(img_data)

        return f"/static/images/uploads/{filename}"

    except Exception as e:
        print("❌ Lỗi khi tạo ảnh từ DALL·E:", e)
        return None

def rewrite_prompt_for_image(user_text):


    
    system_instruction = (
        "Bạn là chuyên gia tạo prompt hình ảnh cho AI vẽ (như DALL·E). "
        "Nhiệm vụ của bạn là viết lại yêu cầu từ người dùng thành một mô tả hình ảnh CỤ THỂ, CHI TIẾT, TRỰC QUAN và DỄ HIỂU cho AI tạo ảnh. "
        "Đặc biệt, nếu nội dung liên quan đến toán học, bảng viết, đề kiểm tra hoặc nội dung có cấu trúc thì phải viết rõ ràng:\n"
        "- Mô tả có bảng trắng hoặc bảng đen\n"
        "- Có bao nhiêu câu toán, nội dung mỗi câu cụ thể\n"
        "- Tránh viết các từ mơ hồ như 'vẽ đề toán ngẫu nhiên'\n"
        "- Không dùng từ ngắn gọn như 'chia ra', 'trông giống', 'kiểu như'\n"
        "- Không viết lời giải thích, không văn vẻ, chỉ in ra prompt dùng để tạo ảnh\n\n"
        "Chỉ trả về mô tả ảnh cuối cùng, không thêm lời dẫn."
    )

    try:
        client = create_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Lỗi rewrite_prompt:", e)
        return user_text  # fallback dùng luôn prompt gốc
    
def cleanup_old_chats():
    folder = "chat_history"
    max_age = 24 * 60 * 60  # 24 giờ
    now = time.time()

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > max_age:
                os.remove(path)
                print(f"[🧹] Đã tự xoá file: {filename}")
OTP_FILE = "otp_codes.json"
def save_chat(user_id, history):
    folder = os.path.join("chat_history")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{user_id}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[💥] Lỗi khi lưu chat: {e}")

def load_otp_data():
    if not os.path.exists(OTP_FILE):
        return {}
    with open(OTP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_otp_data(data):
    with open(OTP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_vn():
    return datetime.utcnow() + timedelta(hours=7)



UPLOAD_FOLDER = 'static/images/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#  Tự động xoá ảnh sau 7 ngày vàvà xoá ảnh cũ sau 7 ngày (tự động mỗi 24h) 
from threading import Thread
import time
from image_cleaner import clean_old_images

def auto_cleaner_loop():
    while True:
        clean_old_images()
        time.sleep(86400)  # ⏱️ chạy mỗi 1 ngày

Thread(target=auto_cleaner_loop, daemon=True).start()

from openai_config import create_openai_client


import smtplib
from email.mime.text import MIMEText

def send_otp_email(to_email, otp_code):
    subject = "Mã xác thực OTP"
    body = f"Mã xác thực của bạn là: {otp_code}\nThời hạn hiệu lực: 5 phút."
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = "SolverViet <your_email@gmail.com>"  # thay bằng email thật
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Lỗi gửi email:", e)
        return False
def send_user_otp_email(to_email, otp_code):
    subject = "🔐 Mã OTP xác thực từ SolverViet"
    body = f"""Chào bạn 👋,

Mã OTP của bạn là: {otp_code}

⏳ Mã có hiệu lực trong 5 phút. Vui lòng không chia sẻ mã này với bất kỳ ai!

Trân trọng,
SolverViet 🇻🇳"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"SolverViet <{os.getenv('EMAIL_ADDRESS')}>"
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
        server.quit()
        print("✅ Gửi OTP user thành công!")
        return True
    except Exception as e:
        print("❌ Lỗi gửi OTP user:", e)
        return False


import unicodedata
import random
import string

def generate_otp():
    from random import randint
    return str(random.randint(100000, 999999))


TELEGRAM_TOKEN = "7580016404:AAHoWnvRElJD3BXkZyxZQ4A4z34qXB-3s54"
TELEGRAM_CHAT_ID = "6894067779"
def send_telegram_message(message):
    print("📤 Đang gửi telegram với nội dung:")
    print(message)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)  # ✅ Sửa tại đây
        print("📬 Phản hồi Telegram:", response.text)
    except Exception as e:
        print("⚠️ Lỗi khi gửi Telegram:", e)
#HÀM GỬI EMAIL
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from ip_blocker import record_ip, is_ip_blocked

from flask import get_flashed_messages
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
REQUESTS_FILE = "requests.json"


from datetime import datetime, timedelta

from flask import Flask, render_template, request, session, redirect, url_for



import time
import threading
from flask import flash 

import uuid

# === Thêm thư mục hiện tại vào sys.path để import các module nội bộ ===
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# ✅ IMPORT các hàm xử lý quản lý người dùng
from admin_utils import is_vip

def load_user_messages(user_id):
    inbox_path = f"user_data/{user_id}_inbox.txt"
    if os.path.exists(inbox_path):
        with open(inbox_path, "r", encoding="utf-8") as f:
            return [msg.strip() for msg in f.read().split("---\n\n") if msg.strip()]
    return []

def cap_nhat_trang_thai_vip(user: User):
    now = datetime.utcnow()

    user.vip_gpt_ai = bool(user.vip_until_gpt and now <= user.vip_until_gpt)
    user.vip_ai_lite = bool(user.vip_until_lite and now <= user.vip_until_lite)

    return {
        "vip_gpt_ai": user.vip_gpt_ai,
        "vip_ai_lite": user.vip_ai_lite,
    }


# ===== IMPORT TOÀN BỘ =====
from flask import Flask
from config import Config


from extensions import db

# ====== FLASK APP ======
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)
app.secret_key = 'b@o_m@t_2025_🔥' 
DATA_FILE = 'friends_data.json'
app.permanent_session_lifetime = timedelta(days=1)
from flask import render_template, request, redirect, abort, session
def is_admin():
    return session.get("is_admin") is True   
from functools import wraps

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect("/admin_login")  # thân thiện hơn 404
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin_users")
@admin_only
def admin_users():
    users = User.query.all()
    user_count = len(users)

    users_data = []

    for user in users:
        u = {
            "username": user.username,
            "fullname": user.fullname,
            "bio": user.bio,
            "user_id": user.user_id,
            "online": getattr(user, "online", False),
        }

        gpt_type = user.vip_gpt

        # ✅ Tính số lượt GPT / Lite còn lại
        if getattr(user, "vip_ai_lite", False) and getattr(user, "vip_until_lite", None):
            u["gpt_remaining"] = "None"
            lite_used = getattr(user, "lite_usage", 0)
            lite_limit = getattr(user, "vip_lite_daily_limit", 50)
            remaining = lite_limit - lite_used
            u["lite_remaining"] = f"{remaining}/{lite_limit}"
        elif gpt_type == "5day":
            used = getattr(user, "gpt_usage_today", 0)
            remaining = 100 - used
            u["gpt_remaining"] = f"{remaining}/100"
            u["lite_remaining"] = "Không có"
        elif gpt_type in ["15day", "30day"]:
            u["gpt_remaining"] = "∞"
            u["lite_remaining"] = "Không có"
        else:
            u["gpt_remaining"] = "Không có"
            u["lite_remaining"] = "Không có"

        # ✅ Hạn sử dụng
        if user.vip_until_lite:
            u["vip_lite_display"] = user.vip_until_lite.strftime("%Y-%m-%d %H:%M:%S")
        else:
            u["vip_lite_display"] = "Không có"

        if user.vip_until_gpt:
            u["vip_gpt_display"] = user.vip_until_gpt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            u["vip_gpt_display"] = "Không có"

        u["vip_gpt"] = user.vip_gpt or ""

        users_data.append(u)

    return render_template("admin_users.html", users=users_data, user_count=user_count)

def parse_dt(s):
    if not s or s.lower() in ["none", "không có"]:
        return None
    s = s.strip()
    try:
        # Nếu chỉ nhập ngày → tự gán giờ 23:59:59
        if len(s) == 10:
            s += " 23:59:59"
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except:
        return None
def parse_vip_duration(type_str):
    now = datetime.now()
    if type_str == "5day":
        return now + timedelta(days=4, hours=23, minutes=59, seconds=59)
    elif type_str == "15day":
        return now + timedelta(days=14, hours=23, minutes=59, seconds=59)
    elif type_str == "30day":
        return now + timedelta(days=29, hours=23, minutes=59, seconds=59)
    return None
@app.route("/admin_users/update", methods=["POST"])
@admin_only
def admin_users_update():
    old_name = request.form.get("username")
    new_name = request.form.get("new_username", old_name)

    vip_gpt = request.form.get("vip_gpt", "").strip()
    vip_toan = request.form.get("vip_toan", "").strip()
    vip_lite = request.form.get("vip_lite", "").strip()
    vip_gpt_type = request.form.get("vip_gpt_type", "").strip()
    gpt_unlimited = request.form.get("gpt_unlimited") == "on"

    user = User.query.filter_by(username=old_name).first()
    if user:
        if new_name != old_name:
            user.username = new_name

        # 🎯 Nếu có chọn loại gói → tự sinh ngày hết hạn
        if vip_gpt_type:
            gpt_time = parse_vip_duration(vip_gpt_type)
        else:
            gpt_time = parse_dt(vip_gpt)

        lite_time = parse_dt(vip_lite)
        toan_time = parse_dt(vip_toan)

        # ❗ Nếu có cả GPT và Lite → ưu tiên GPT
        if gpt_time:
            lite_time = None
        elif lite_time:
            gpt_time = None

        user.vip_until_gpt = gpt_time
        user.vip_gpt = vip_gpt_type or None
        user.vip_gpt_ai = bool(gpt_time)

        user.vip_until_lite = lite_time
        user.vip_ai_lite = bool(lite_time)


        db.session.commit()

    return redirect("/admin_users")


@app.route("/admin_users/toggle_block", methods=["POST"])
@admin_only
def admin_toggle_block():
    username = request.form.get("username")
    if not username:
        return "Thiếu tên người dùng", 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return "Không tìm thấy người dùng", 404

    # ✅ Đảo ngược trạng thái block
    user.is_blocked = not getattr(user, "is_blocked", False)
    db.session.commit()

    print(f"[DEBUG] Đã {'khoá' if user.is_blocked else 'mở khoá'} user: {username}")
    return redirect("/admin_users")

def get_user_type():
    user_id = session.get("user_id")
    if not user_id:
        return "guest"

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return "guest"

    try:
        if user.vip_until and datetime.strptime(user.vip_until, "%Y-%m-%d").date() >= datetime.now().date():
            return "vip"
    except:
        pass

    return "logged_in"
def check_lite_usage(user):

    MAX_FREE = 15
    MID_LIMIT = 5
    DAILY_LIMIT = 5
    now = now_vn()
    today = now.strftime("%Y-%m-%d")

    # ✅ Nếu chưa đăng nhập (guest)
    username = session.get("username")
    if not username:
        usage = session.get("lite_usage", 0)
        if usage >= MAX_FREE:
            return False
        session["lite_usage"] = usage + 1
        return True

    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    usage = user.lite_usage or 0
    verified = user.is_verified or False

    # ✅ Gói GPT không giới hạn
    try:
        if user.vip_until_gpt and now <= datetime.strptime(user.vip_until_gpt, "%Y-%m-%d %H:%M:%S"):
            return True
    except:
        pass

    if session.pop("just_verified", False):
        return True

    # ✅ Có gói AI Lite → 50 lượt/ngày
    try:
        if user.vip_until_lite and now <= datetime.strptime(user.vip_until_lite, "%Y-%m-%d %H:%M:%S"):
            if user.lite_date != today:
                user.lite_usage = 0
                user.lite_date = today
                usage = 0
            if usage < 50:
                user.lite_usage = usage + 1
                db.session.commit()
                return True
            else:
                return False
    except:
        pass

    # ✅ Chưa xác thực → chỉ 5 lượt
    if not verified:
        if usage >= MID_LIMIT:
            return "require_verification"
        user.lite_usage = usage + 1
        db.session.commit()
        return True

    # ✅ Đã xác thực → tổng 15 lượt đầu
    if verified and usage < MAX_FREE:
        user.lite_usage = usage + 1
        db.session.commit()
        return True

    # ✅ Đã xác thực và vượt quá 15 lượt → mỗi ngày +5 lượt
    if verified and usage >= MAX_FREE:
        if user.last_lite_free_date != today:
            user.last_lite_free_date = today
            user.lite_usage = MAX_FREE
            usage = MAX_FREE

        daily_used = usage - MAX_FREE
        if daily_used >= DAILY_LIMIT:
            return False

        user.lite_usage = usage + 1
        db.session.commit()
        return True

    return False
#GIỚI HẠN GÓI VÀ SỬA THỦ CÔNG
def check_gpt_usage(user):
    now = now_vn()
    today = now.strftime("%Y-%m-%d")

    gpt_until = user.vip_until_gpt  # ✅ dùng trực tiếp datetime object
    gpt_type = user.vip_gpt

    print("📌 [GPT USAGE] gpt_type =", gpt_type)
    print("📌 [GPT USAGE] gpt_until =", gpt_until)

    if not gpt_until or not gpt_type:
        print("❌ Thiếu gói hoặc thời hạn GPT")
        return False

    if now > gpt_until:
        print("❌ Gói GPT đã hết hạn")
        return False

    if user.gpt_unlimited:
        print("✅ Unlimited GPT")
        return True

    if gpt_type in ["15day", "30day"]:
        print("✅ Gói GPT dài ngày hợp lệ")
        return True

    if gpt_type == "5day":
        usage_today = user.gpt_usage_today or 0
        usage_date = user.gpt_usage_date

        print("📌 usage_today =", usage_today)
        print("📌 usage_date =", usage_date)
        print("📌 today =", today)

        if usage_date != today:
            print("ℹ️ Reset lượt GPT vì ngày mới")
            usage_today = 0
            user.gpt_usage_today = 0
            user.gpt_usage_date = today

        if usage_today >= 100:
            print("❌ Hết 100 lượt GPT hôm nay")
            return False

        user.gpt_usage_today = usage_today + 1
        db.session.commit()
        print("✅ Còn lượt, tăng usage_today:", user.gpt_usage_today)
        return True

    print("❌ Không khớp loại gói GPT")
    return False


def get_al_usage():
    return session.get("al_uses", 0)

def increment_al_usage():
    session["al_uses"] = get_al_usage() + 1



# ====== USER MANAGEMENT ======#

def get_username():
    return session.get("username")
def is_admin():
    return session.get("is_admin") is True


def update_solves(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user.solves += 1
        db.session.commit()
def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_solve_today(username):
    today = get_today()
    if username == "admin":
        return 0  # Admin không bị giới hạn

    user = User.query.filter_by(username=username).first()
    if not user:
        return 0

    if not user.last_solve_date:
        user.last_solve_date = today
        user.solves = 0
        user.ads_used_today = 0
        db.session.commit()
    elif user.last_solve_date != today:
        if user.solves < 10:
            user.solves = max(0, user.solves - 5)
        else:
            user.solves = 0
        user.last_solve_date = today
        user.ads_used_today = 0
        db.session.commit()

    return user.solves
#==========BẢO TRÌ HỆ THỐNG==========#
def is_maintenance(feature):
    try:
        with open("maintenance_config.json", "r") as f:
            config = json.load(f)
            return config.get("all") or config.get(feature, False)
    except:
        return False
@app.route("/check_maintenance")
def check_maintenance():
    feature = request.args.get("feature", "all")
    return jsonify({"maintenance": is_maintenance(feature)})
@app.route("/maintenance")
def maintenance_page():
    return render_template("maintenance.html")


@app.route("/admin/bao-tri", methods=["GET"])
@admin_only
def bao_tri_router():
    return redirect("/admin/bao-tri-all")
    
@app.route("/admin/bao-tri-all", methods=["GET", "POST"])
@admin_only
def bao_tri_all():
    try:
        with open("maintenance_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {
            "all": False,
            "gpt_chat": False,
            "chat_lite": False,
            "chat_ai_lite": False,
            "chat_ai_lite_daily": False,
            "home": False
        }

    if request.method == "POST":
        feature = request.form.get("feature")

        if feature and feature in config:
            # Toggle từng phần cụ thể
            config[feature] = not config[feature]
            flash(f"✅ Đã cập nhật bảo trì cho phần: {feature}", "success")
        else:
            # Toggle toàn hệ thống nếu không có phần cụ thể
            config["all"] = not config.get("all", False)
            flash("✅ Đã cập nhật trạng thái bảo trì toàn bộ hệ thống.", "success")

        with open("maintenance_config.json", "w") as f:
            json.dump(config, f, indent=2)

        return redirect("/admin/bao-tri-all")

    is_on = config.get("all", False)
    return render_template("bao_tri_all.html", is_on=is_on, config=config)


# ====== LOGIN / REGISTER / LOGOUT ======
@app.route("/login", methods=["GET", "POST"])
def login():
    print("[DEBUG] 🟢 Đã vào hàm LOGIN")

    message = request.args.get("message")

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            if user.is_blocked:
                error = "🚫 Tài khoản của bạn đã bị khóa. Nếu đây là nhầm lẫn, vui lòng gửi khiếu nại tại <a href='/appeal' style='color:#4ea6ff;'>đây</a>."
                return render_template("login.html", error=error)

            if user.password == password:  # TODO: nếu dùng hash thì sửa lại
                if user.wants_verification and not user.is_verified:
                    otp_code = generate_otp()
                    send_user_otp_email(user.email, otp_code)

                    session["pending_user"] = username
                    session["otp_sent"] = True

                    return redirect("/verify-otp")

                # Đăng nhập thành công
                user.online = True
                user.last_seen = datetime.utcnow()

                session["username"] = user.username
                session["user_id"] = user.user_id  # dùng UUID
                session["vip_until_gpt"] = user.vip_until_gpt
                session["al_uses"] = 0  # lượt AI Lite tạm

                db.session.commit()

                if user.vip_gpt_ai:
                    session["just_logged_in"] = True

                print("[DEBUG] Đăng nhập thành công:", username)
                return redirect(url_for("home_page"))

        return render_template("login.html", error="❌ Sai tài khoản hoặc mật khẩu.")

    return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ip = request.remote_addr

        if session.get("username") != "admin":
            count = record_ip(ip)
            if count >= 3:
                message = f"""
<b>Cảnh báo đăng ký SPAM</b>
🔢 IP: <code>{ip}</code>
🕒 Ngày: {datetime.now().strftime('%Y-%m-%d')}
💥 Số lần tạo tài khoản: {count} (hạn mức: 3)
                """
                send_telegram_message(message.strip())
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        want_verification = 'want_verification' in request.form

        if username == "admin":
            return render_template("register.html", error="🚫 Không được đặt tên tài khoản là 'admin'.")

        if len(password) < 8:
            return render_template("register.html", error="❌ Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r"[A-Z]", password):
            return render_template("register.html", error="❌ Mật khẩu phải chứa ít nhất 1 chữ in hoa.")
        if not re.search(r"[a-z]", password):
            return render_template("register.html", error="❌ Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r"[0-9]", password):
            return render_template("register.html", error="❌ Mật khẩu phải chứa ít nhất 1 chữ số.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return render_template("register.html", error="❌ Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt.")
        if password != confirm_password:
            return render_template("register.html", error="❌ Mật khẩu xác nhận không khớp.")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="❌ Tên đăng nhập đã tồn tại.")

        new_user = User(
            username=username,
            password=password,
            fullname=fullname, 
            email=email,
            is_verified=False,
            wants_verification=want_verification,
            free_gpt_uses=5
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

#THÔNG TIN TÀI KHOẢN CÁ NHÂN TỪNG USER
from models.user import User
from extensions import db

@app.route("/user-info", methods=["GET", "POST"])
def user_info():
    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    if request.method == "POST":
        # 👇 Lấy dữ liệu từ form gửi lên
        email = request.form.get("email")
        password = request.form.get("new_password")
        fullname = request.form.get("fullname")
        birthday = request.form.get("birthday")
        birthyear = request.form.get("birthyear")
        phone = request.form.get("phone")


        # 👇 Cập nhật nếu có
        if email: user.email = email
        if password: user.password = password
        if fullname: user.fullname = fullname
        if birthday: user.birthday = birthday
        if birthyear: user.birthyear = birthyear
        if phone: user.phone = phone


        # 👇 Xử lý avatar upload
        avatar = request.files.get("avatar")
        if avatar and avatar.filename != "":
            filename = secure_filename(f"{username}_avatar.png")
            avatar_path = os.path.join("static/images/avatars", filename)
            avatar.save(avatar_path)
            user.avatar_url = f"/static/images/avatars/{filename}"
            print("✅ ĐÃ GÁN AVATAR URL:", user.avatar_url)
        else:
            print("❌ KHÔNG NHẬN FILE ẢNH")

        db.session.commit()
        print("🔥 USER SAU LƯU:", user)

        flash("Đã cập nhật thông tin thành công!", "success")
        return redirect("/user-info")

    return render_template("user_info.html", user=user, username=user.username,now=datetime.now())


#XÓA AVTR
@app.route("/user-info/delete-avatar", methods=["POST"])
def delete_avatar():
    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    if user.avatar_url and user.avatar_url != "/static/logos/logo.png":
        try:
            os.remove(user.avatar_url.replace("/", os.sep)[1:])
        except:
            pass
    user.avatar_url = "/static/logos/logo.png"

    db.session.commit()

    flash("Ảnh đại diện đã được đặt lại về mặc định!", "info")
    return redirect("/user-info")

#========ROUTE XÁC THỰC TÀI KHOẢN==========#
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    username = session.get("pending_user") or session.get("username")
    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for("login"))

    if user.is_verified:
        return redirect(url_for("home_page"))

    # ✅ Gửi OTP nếu chưa gửi
    if request.method == "GET":
        if not getattr(user, "otp_code", None) or not session.get("otp_sent"):
            import random
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            db.session.commit()

            # ✅ Gửi tới email_temp nếu đang đổi email, ngược lại gửi về email chính
            email_to_send = user.email_temp if user.email_temp else user.email
            success = send_user_otp_email(email_to_send, otp)

            if success:
                print(f"✅ Đã gửi OTP tới {email_to_send}")
            else:
                print(f"❌ Gửi OTP thất bại tới {email_to_send}")

            session["otp_sent"] = True

        return render_template(
            "verify_otp.html",
            username=username,
            method="email",
            error="",
            user=user
        )

    # ✅ Xử lý nhập mã OTP
    if request.method == "POST":
        otp_input = request.form.get("otp")
        if otp_input == user.otp_code:
            user.is_verified = True
            user.otp_code = None

            # ✅ Nếu đang trong quá trình đổi email thì cập nhật email mới
            if user.email_temp and user.email_temp != user.email:
                print(f"📩 Đổi email từ {user.email} ➜ {user.email_temp}")
                user.email = user.email_temp
                user.email_temp = None

            # ✅ Tặng thêm lượt nếu chỉ mới có 5
            if (user.free_gpt_uses or 0) <= 5:
                user.free_gpt_uses = (user.free_gpt_uses or 0) + 10

            db.session.commit()

            session["username"] = username
            session["user_id"] = user.id
            session["is_verified"] = True
            session.pop("pending_user", None)
            session.pop("otp_sent", None)

            for key in ["chat_history", "chat_ai_lite", "chat_ai_lite_history"]:
                session.pop(key, None)

            session["just_verified"] = True
            session.modified = True

            return redirect(url_for("home_page"))

        # ❌ Sai OTP
        return render_template(
            "verify_otp.html",
            username=username,
            method="email",
            error="❌ Sai mã OTP. Vui lòng thử lại.",
            user=user
        )

    return render_template(
        "verify_otp.html",
        username=username,
        method="email",
        error="",
        user=user
    )

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    username = session.get("pending_user") or session.get("username")
    print("Resending OTP for:", username)

    if not username:
        return Response(json.dumps({
            "status": "error",
            "message": "❌ Không tìm thấy tài khoản."
        }, ensure_ascii=False), content_type="application/json")

    user = User.query.filter_by(username=username).first()
    if not user:
        return Response(json.dumps({
            "status": "error",
            "message": "❌ Không tìm thấy tài khoản."
        }, ensure_ascii=False), content_type="application/json")

    email = user.email
    otp = str(random.randint(100000, 999999))
    print("Generated OTP:", otp)

    user.otp_code = otp
    db.session.commit()

    success = send_user_otp_email(email, otp)

    if success:
        return Response(json.dumps({
            "status": "ok",
            "message": "✅ Đã gửi lại mã xác thực qua email."
        }, ensure_ascii=False), content_type="application/json")
    else:
        return Response(json.dumps({
            "status": "error",
            "message": "❌ Gửi email thất bại. Vui lòng thử lại sau."
        }, ensure_ascii=False), content_type="application/json")

@app.route("/logout")
def logout():
    username = session.get("username")

    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.online = False
            db.session.commit()

    # Tách riêng cho từng loại session
    if session.get("admin"):
        session.pop("admin", None)
        return redirect("/admin_login")

    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/login")

#KHÔI PHỤC TÀI KHOẢN 
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        input_text = request.form["username"].strip().lower()

        # ✅ Tìm user theo username hoặc email (không phân biệt hoa thường)
        user = User.query.filter(
            (User.username.ilike(input_text)) | (User.email.ilike(input_text))
        ).first()

        if not user:
            return render_template("forgot_password.html", error="Tài khoản không tồn tại.")

        if not user.is_verified:
            return render_template("forgot_password.html", error="Chức năng này chỉ hỗ trợ tài khoản đã xác thực.")

        # ✅ Gửi OTP
        otp_code = generate_otp()
        send_user_otp_email(user.email, otp_code)

        otp_data = load_otp_data()
        otp_data[user.username] = otp_code
        save_otp_data(otp_data)

        session["reset_user"] = user.username
        return redirect("/reset-password")

    return render_template("forgot_password.html")

@app.route("/change-email", methods=["GET", "POST"])
def change_email():
    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    # ⚠️ Chỉ cho đổi nếu đã xác thực email trước đó
    if not user.is_verified:
        flash("Bạn cần xác thực email trước khi đổi!", "danger")
        return redirect("/user-info")

    if request.method == "POST":
        new_email = request.form.get("new_email")

        if not new_email or "@" not in new_email:
            flash("Email không hợp lệ!", "danger")
            return redirect("/change-email")

        # ✅ Ghi thông tin tạm, chưa cập nhật vĩnh viễn
        user.email_temp = new_email
        user.is_verified = False
        user.otp_code = generate_otp()

        db.session.commit()

        # ✅ Gửi mã xác thực tới email mới
        send_otp_email(new_email, user.otp_code)

        flash("Đã gửi mã xác nhận đến email mới! Vui lòng kiểm tra và xác thực lại.", "info")
        return redirect("/verify-otp")

    return render_template("change_email.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    session_username = session.get("reset_user")
    if not session_username:
        return redirect("/forgot-password")

    # ✅ Chuẩn hóa session_username ngay từ đầu
    session_username = session_username.strip().lower()

    if request.method == "POST":
        input_username = request.form["username"].strip().lower()
        otp = request.form["otp"].strip()
        new_password = request.form["new_password"]
        confirm = request.form["confirm_password"]

        # ✅ So khớp username
        if input_username != session_username:
            return render_template("reset_password.html", error="⚠️ Tên tài khoản không khớp.")

        # ✅ So khớp OTP
        otp_data = load_otp_data()
        if otp_data.get(session_username) != otp:
            return render_template("reset_password.html", error="⚠️ Mã OTP không đúng.")

        # ✅ Kiểm tra mật khẩu
        if new_password != confirm:
            return render_template("reset_password.html", error="⚠️ Mật khẩu xác nhận không khớp.")

        if len(new_password) < 8:
            return render_template("reset_password.html", error="⚠️ Mật khẩu phải từ 8 ký tự trở lên.")

        # ✅ Cập nhật mật khẩu
        user = User.query.filter_by(username=session_username).first()
        if not user:
            return render_template("reset_password.html", error="⚠️ Tài khoản không tồn tại.")

        user.password = new_password
        user.online = True
        db.session.commit()

        # ✅ Xoá OTP & session
        otp_data.pop(session_username, None)
        save_otp_data(otp_data)
        session.pop("reset_user", None)

        # ✅ Tự đăng nhập lại
        session["username"] = user.username
        session["user_id"] = user.user_id
        session["vip_until_gpt"] = user.vip_until_gpt
        session["vip_ai_lite"] = user.vip_ai_lite
        session["vip_until_lite"] = user.vip_until_lite or ""
        session["al_uses"] = 0

        return redirect("/")

    return render_template("reset_password.html")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")
    avatar_url = user.avatar_url or "/static/logos/logo.png"
    if request.method == "POST":
     
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if user.password != current_password:
            return render_template("change_password.html", error="⚠️ Mật khẩu hiện tại không đúng.")

        if new_password != confirm_password:
            return render_template("change_password.html", error="⚠️ Mật khẩu xác nhận không khớp.")

        if len(new_password) < 8:
            return render_template("change_password.html", error="⚠️ Mật khẩu phải từ 8 ký tự trở lên.")

        user.password = new_password
        db.session.commit()

        return redirect("/")

    return render_template("change_password.html", avatar_url=avatar_url)



# TRANG CHỦ
from sqlalchemy import distinct
from models import Message, User  # đảm bảo đã import model Message

@app.route("/")
def home_page():
    if is_maintenance("home"):
        return render_template("maintenance.html")

    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        print("⚠️ Không tìm thấy user trong database.")
        if not session.get("reloading_after_restore"):
            session["reloading_after_restore"] = True
            time.sleep(0.3)
            return redirect("/")
        else:
            session.pop("reloading_after_restore", None)
            return render_template("login.html", error="⚠️ Dữ liệu tài khoản không tồn tại. Vui lòng đăng nhập lại.")

    # ✅ Đã có user
    session.pop("reloading_after_restore", None)

    if user.is_blocked:
        session.clear()
        return render_template("login.html", error="🚫 Tài khoản của bạn đã bị khóa...")
    user_messages = []

    # ✅ Lấy danh sách người đã gửi tin chưa đọc
    unread_senders = (
        db.session.query(distinct(Message.sender))
        .filter(Message.receiver == user.username, Message.read == False)
        .all()
    )
    sender_usernames = [
            sender_id[0]
            for sender_id in unread_senders
            if sender_id[0] != user.username
        ]


    user_vip_status = {
        "vip_gpt": user.vip_gpt_ai,
        "vip_lite": user.vip_ai_lite,
        "vip_until_gpt": user.vip_until_gpt or "",
        "vip_until_lite": user.vip_until_lite or ""
    }

    display_name = user.fullname or username
    avatar_url = user.avatar_url or "/static/logos/logo.png"

    session.pop("just_logged_in", None)

    has_slv = bool(user.vip_gpt_ai) and bool(user.vip_until_gpt)
    return render_template(
        "home.html",
        username=username,
        avatar_url=avatar_url,
        display_name=display_name,
        has_slv=has_slv,
        user=user,
        user_vip_status=user_vip_status,
        user_messages=user_messages,
        user_unread_senders=sender_usernames,  # ✅ truyền xuống template
        is_maintenance=is_maintenance("home"),
    )


#TỔNG QUÁT
from flask import render_template, request, session, redirect, abort
import os
from datetime import datetime

login_attempts = {}

@app.route("/solverviet_control_x2025")
@admin_only
def admin_panel():
    print("👁 Session hiện tại:", dict(session))
    return render_template("admin.html")

import pyotp
import os
from flask import Flask, request, session, redirect, render_template

# ---- Route 1: admin_login - kiểm tra 4 trường ----
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    ip = request.remote_addr
    login_attempts.setdefault(ip, 0)

    if login_attempts[ip] >= 5:
        return "⚠️ Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau.", 429

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        code1 = request.form.get("backdoor_code")
        code2 = request.form.get("backdoor_code2")

        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
        BACKDOOR_CODE = os.getenv("BACKDOOR_CODE")
        BACKDOOR_CODE2 = os.getenv("BACKDOOR_CODE2")
        if (username == ADMIN_USERNAME and password == ADMIN_PASSWORD and
            code1 == BACKDOOR_CODE and code2 == BACKDOOR_CODE2):
            session["admin_otp_ready"] = True
            print("✅ Thông tin hợp lệ. Session hiện tại:", dict(session))
            return "OK"  # Gửi về frontend để hiển popup nhập OTP
        else:
            login_attempts[ip] += 1
            return "❌ CÓ CC NÈ MÀ ĐÒI VÔ", 403

    return render_template("admin_login.html")

@app.route("/admin_2fa", methods=["POST"])
def admin_2fa():
    if not session.get("admin_otp_ready"):
        return "Phiên xác thực không hợp lệ.", 403

    code = request.form.get("otp", "").strip()
    secret = os.getenv("ADMIN_2FA_SECRET")

    if not secret:
        return "❌ SECRET không tồn tại", 500

    totp = pyotp.TOTP(secret)

    if totp.verify(code, valid_window=1):
        session.pop("admin_otp_ready", None)
        session["is_admin"] = True
        return redirect("/solverviet_control_x2025")
    else:
        return "❌ Mã xác thực sai", 403




#XEM QUẢNG CÁO
@app.route("/watch_ad", methods=["POST"])
def watch_ad():
    username = get_username()
    if not username:
        return {"status": "fail", "message": "Không tìm thấy tài khoản!"}

    user = User.query.filter_by(username=username).first()
    if not user:
        return {"status": "fail", "message": "Không tìm thấy tài khoản!"}

    today = get_today()
    if user.last_solve_date != today:
        user.last_solve_date = today
        user.solves = 0
        user.ads_used_today = False

    if not user.ads_used_today:
        user.solves = max(0, user.solves - 3)
        user.ads_used_today = True
        db.session.commit()
        return {"status": "success", "message": "+3 lượt miễn phí"}
    else:
        return {"status": "fail", "message": "Bạn đã nhận quảng cáo hôm nay rồi!"}
@app.route("/verify_user_info", methods=["POST"])
def verify_user_info():
    data = request.get_json()
    username = data.get("username", "").strip()
    user_id = data.get("user_id", "").strip()
    user = User.query.filter_by(username=username, user_id=user_id).first()
    return jsonify({"valid": bool(user)})
def send_upgrade_email(to_email, username, package, amount, method, note, created_at, txn_id):
    from flask import url_for
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    email_user = os.getenv("EMAIL_ADDRESS")
    email_pass = os.getenv("EMAIL_PASSWORD")
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    approve_link = f"{BASE_URL}{url_for('admin_review')}?txn_id={txn_id}&email=phatth.viettel@gmail.com"


    print("📧 LINK EMAIL:", approve_link)

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = "🔔 Yêu cầu nâng cấp gói mới từ người dùng"

    body = f"""
    <h3>🔔 Yêu cầu nâng cấp mới</h3>
    <p><b>👤 User:</b> {username}</p>
    <p><b>💳 Gói:</b> {package} ({amount})</p>
    <p><b>🏦 Phương thức:</b> {method}</p>
    <p><b>📝 Ghi chú:</b> {note}</p>
    <p><b>🕒 Thời gian:</b> {created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <br>
    <p>➡️ <b>Link duyệt:</b> <a href="{approve_link}" target="_blank">{approve_link}</a></p>
    <p>📋 Hoặc copy thủ công: {approve_link}</p>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        print("✅ Đã gửi email nâng cấp tới admin.")
    except Exception as e:
        print("❌ Gửi email nâng cấp lỗi:", e)



@app.route("/upgrade", methods=["GET", "POST"])
def upgrade():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    if request.method == "POST":
        package = request.form["package"]
        note = request.form["note"]
        method = request.form.get("method", "Không rõ")

        if not note.strip():
            return render_template("upgrade.html", error="⚠️ Vui lòng nhập mã giao dịch hoặc ghi chú.")

        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("upgrade.html", error="❌ Không tìm thấy tài khoản.")

        now = now_vn()
        has_gpt = user.vip_until_gpt and user.vip_until_gpt > now
        has_lite = user.vip_until_lite and user.vip_until_lite > now

        if package.startswith("vip_gpt") and has_lite:
            return render_template("upgrade.html", error="🚫 Bạn đang dùng gói AI Lite. Không thể mua thêm gói GPT cùng lúc.")
        if package == "vip_ai_lite" and has_gpt:
            return render_template("upgrade.html", error="🚫 Bạn đang dùng gói GPT. Không thể mua thêm gói AI Lite cùng lúc.")

        # ✅ Tạo ID giao dịch
        created_at = now
        txn_id = f"txn_{int(now.timestamp())}_{random.randint(1000,9999)}"
        session["last_txn_id"] = txn_id  # để kiểm tra bằng /check_status

        # Hiển thị gói
        package_display = {
            "vip_gpt_5d": "49K",
            "vip_gpt_15d": "109K",
            "vip_gpt_30d": "149K",
            "vip_ai_lite": "25K"
        }
        amount = package_display.get(package, "Không rõ")

        # ✅ Lưu vào DB
        txn = Transaction(
            txn_id=txn_id,
            username=username,
            amount=amount,
            package=package,
            method=method,
            note=note,
            status="pending",
            created_at=created_at
        )
        db.session.add(txn)
        db.session.commit()

        # ✅ Gửi email cho admin
        try:
            send_upgrade_email(
                to_email=os.getenv("ADMIN_EMAIL"),
                username=username,
                package=package,
                amount=amount,
                method=method,
                note=note,
                created_at=created_at,
                txn_id=txn_id 
            )
        except Exception as e:
            print("❌ Gửi email nâng cấp lỗi:", e)

        # ✅ Gửi Telegram nếu bạn vẫn muốn dùng
        try:
            send_telegram_message(
                f"🔔 <b>Yêu cầu nâng cấp mới</b>\n"
                f"👤 User: <code>{username}</code>\n"
                f"💳 Gói: {package} ({amount})\n"
                f"🏦 Phương thức: {method}\n"
                f"📝 Ghi chú: <code>{note}</code>\n"
                f"🕒 Thời gian: {created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"➡️ Vào trang admin để duyệt: {url_for('admin_review', _external=True)}"
            )
        except:
            pass

        # Trả về giao diện thành công
        return render_template(
            "upgrade.html",
            success=True,
            txn_id=txn_id,
            flash_message="✅ Giao dịch đã được ghi nhận! Bạn sẽ được duyệt trong vòng 5 phút."
        )

    # GET
    user = User.query.filter_by(username=username).first()
    display_name = user.fullname if user and user.fullname else username

    now = now_vn()
    vip_gpt_active = user.vip_until_gpt and user.vip_until_gpt > now
    vip_lite_active = user.vip_until_lite and user.vip_until_lite > now

    return render_template(
        "upgrade.html",
        fullname=display_name,
        user_id=user.user_id if user else "",
        vip_gpt_active=vip_gpt_active,
        vip_lite_active=vip_lite_active
    )


from flask import jsonify
import logging
log = logging.getLogger('werkzeug')

@app.route("/check_status")
def check_status():
    log.setLevel(logging.ERROR)  # Ẩn bớt log spam
    txn_id = session.get("last_txn_id")

    if not txn_id:
        return jsonify({"status": "none"})

    from models.transaction import Transaction
    txn = Transaction.query.filter_by(txn_id=txn_id).first()

    if txn:
        return jsonify({
            "status": txn.status,
            "package": txn.package,
            "method": txn.method,
            "created_at": txn.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        return jsonify({"status": "not_found"})

def grant_vip(username, package, method=""):
    print(f"⚠️ [grant_vip] Cấp gói: {package} cho user: {username}")

    user = User.query.filter_by(username=username).first()
    if not user:
        print("❌ Không tìm thấy user:", username)
        return "❌ Người dùng không tồn tại."

    now = datetime.utcnow()
    message = "✅ Gói đã được cấp thành công!"

    gpt_vip_until = user.vip_until_gpt or now
    lite_vip_until = user.vip_until_lite or now

    # ✅ Gói GPT
    if package in ["vip_gpt_5d", "vip_gpt_15d", "vip_gpt_30d"]:
        if lite_vip_until > now:
            return "❌ Bạn đang có gói  Lite. Không thể mua gói SLV. Vui lòng đợi hết hạn hoặc liên hệ nhà phát triển."

        if gpt_vip_until > now:
            print("⚠️ Đang ghi đè gói GPT hiện tại bằng gói mới")

        days_map = {
            "vip_gpt_5d": (5, "5day"),
            "vip_gpt_15d": (15, "15day"),
            "vip_gpt_30d": (30, "30day")
        }
        duration, gpt_type = days_map[package]
        user.vip_gpt_ai = True
        user.vip_gpt = gpt_type
        new_vip = (now + timedelta(days=duration)).replace(hour=23, minute=59, second=59, microsecond=0)
        user.vip_until_gpt = new_vip

        if gpt_type == "5day":
            user.gpt_usage_today = 0
            user.gpt_usage_date = now.strftime("%Y-%m-%d")
            user.gpt_unlimited = False

        # Gỡ gói Lite nếu có
        user.vip_until_lite = None
        user.vip_ai_lite = None
        user.vip_lite_daily_limit = None
        user.lite_usage = None
        user.lite_date = None

    # ✅ Gói AI Lite
    elif package == "vip_ai_lite":
        if gpt_vip_until > now:
            return "❌ Bạn đang có gói SLV. Không thể mua gói Lite. Vui lòng đợi hết hạn hoặc liên hệ nhà phát triển."

        if lite_vip_until > now:
            print("⚠️ Gói Lite hiện tại vẫn còn hiệu lực. Sẽ ghi đè lại bằng gói mới.")

        # Reset lại gói Lite (ghi đè từ bây giờ + 7 ngày)
        new_vip = (now + timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=0)
        user.vip_ai_lite = True
        user.vip_until_lite = new_vip
        user.vip_lite_daily_limit = 50
        user.lite_usage = 0
        user.lite_date = now.strftime("%Y-%m-%d")

    else:
        return "❌ Gói không hợp lệ."

    try:
        db.session.commit()
        print("✅ Đã lưu dữ liệu người dùng.")
        return message
    except Exception as e:
        db.session.rollback()
        print("❌ Lỗi khi lưu:", e)
        return "❌ Lỗi khi lưu dữ liệu."


#NÚT ADMIN DUYỆT
@app.route("/admin/review")
@admin_only
def admin_review():
    txs = Transaction.query.filter_by(status="pending").order_by(Transaction.created_at.desc()).all()
    return render_template("admin_review.html", txs=txs)
@app.route("/admin/review/requests")
@admin_only
def get_review_requests():
    txs = Transaction.query.filter_by(status="pending").order_by(Transaction.created_at.desc()).all()
    return render_template("admin/_requests_table.html", txs=txs)


@app.route("/admin/approve/<txn_id>")
@admin_only
def approve_transaction(txn_id):
    tx = Transaction.query.filter_by(txn_id=txn_id, status="pending").first()
    if not tx:
        return redirect(url_for("admin_review"))

    tx.status = "approved"
    db.session.commit()

    package = normalize_package(tx.package)
    method = tx.method
    username = tx.username

    result = grant_vip(username, package, method)

    if isinstance(result, str) and result.startswith("❌"):
        print(f"[❌] Lỗi khi cấp gói: {result}")
    else:
        print(f"[✅] Gói {package} đã được cấp cho {username} thành công.")

    return redirect(url_for("admin_review"))

@app.route("/admin/reject/<txn_id>")
@admin_only
def reject_transaction(txn_id):
    tx = Transaction.query.filter_by(txn_id=txn_id, status="pending").first()
    if not tx:
        return redirect(url_for("admin_review"))

    tx.status = "rejected"
    db.session.commit()
    return redirect(url_for("admin_review"))

def is_follow_up(msg):
    msg = msg.lower().strip()
    follow_keywords = ["bài", "phần", "tiếp", "tiếp theo", "tiếp tục", "rồi sao", "câu", "nữa", "b nhé", "c thì sao"]
    return any(kw in msg for kw in follow_keywords) and len(msg.split()) <= 6


#CHO LATEX ĐẸP OCR NHẬN DIỆN TỐT NHẤT CÓ THỂ
def clean_ocr_output(text):
    # Chuẩn hóa unicode: tách các ký tự đặc biệt thành ký tự chuẩn
    text = unicodedata.normalize("NFC", text)

    # Xóa ký tự vô nghĩa, giữ lại ký hiệu toán học
    text = re.sub(r"[^\w\s=+\-*/^().πlim→\n]", "", text)

    # Loại bỏ khoảng trắng thừa
    text = re.sub(r"\s+", " ", text)

    # Sửa lỗi OCR sai chữ → số
    text = text.replace("O", "0")
    text = text.replace("l", "1")
    text = text.replace("I", "1")

    # Sửa lỗi OCR sai nhân/x
    text = text.replace("×", "*").replace("x", "x").replace("X", "x")

    # Sửa lỗi toán học thường gặp
    fixes = {
        "32 - 7": "3x - 7",
        "22 + 5": "2x + 5",
        "x2": "x^2",
        "x 2": "x^2",
        "x²": "x^2",
        "lim x2": "lim x→2",
        "Lim x2": "lim x→2",
        "lim x→": "lim x→2",
        "π r 2": "πr^2",
        "π r^ 2": "πr^2"
    }
     
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)

    # Xóa khoảng trắng dư đầu/cuối
    return text.strip()
#=====BẠN BÈ=====#
@app.route("/unblock_user", methods=["POST"])
def unblock_user():
    username = session.get("username")
    data = request.get_json()
    target = data.get("target")

    if not username or not target:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu"})

    user = User.query.filter_by(username=username).first()
    target_user = User.query.filter_by(username=target).first()

    if not user or not target_user:
        return jsonify({"status": "error", "message": "Không tìm thấy user"})

    # 👇 Giả sử có user.blocked_users là relationship list
    if target_user in user.blocked_users:
        user.blocked_users.remove(target_user)
        db.session.commit()
        return jsonify({"status": "success"})

    return jsonify({"status": "error", "message": "User chưa bị chặn"})

@app.route("/blocked_users")
def get_blocked_users():
    username = session.get("username")
    if not username:
        return jsonify([])

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify([])

    blocked_list = [u.username for u in user.blocked_users]
    return jsonify(blocked_list)


@app.route("/block_user", methods=["POST"])
def block_user():
    username = session.get("username")
    data = request.get_json()
    target = data.get("target")

    if not username or not target:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu"})

    user = User.query.filter_by(username=username).first()
    target_user = User.query.filter_by(username=target).first()

    if not user or not target_user:
        return jsonify({"status": "error", "message": "User không tồn tại"})

    if target_user not in user.blocked_users:
        user.blocked_users.append(target_user)
        db.session.commit()

    return jsonify({"status": "success"})


@app.route("/chat/delete/<friend>", methods=["POST"])
def delete_chat(friend):
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "error": "Chưa đăng nhập"})

    from models.message import Message

    msgs = Message.query.filter(
        db.or_(
            db.and_(Message.sender == username, Message.receiver == friend),
            db.and_(Message.sender == friend, Message.receiver == username)
        )
    ).all()

    if not msgs:
        return jsonify({"success": False, "error": "Không tìm thấy đoạn chat."})

    for msg in msgs:
        # ✅ Xoá ảnh thật nếu có
        if msg.image_urls:
            for url in msg.image_urls:
                try:
                    # Giả sử đường dẫn là /static/uploads/abc.jpg
                    image_path = os.path.join(app.root_path, url.strip("/"))  # chuyển về đường thật
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print("Lỗi khi xoá ảnh:", e)

        # Xoá message khỏi database
        db.session.delete(msg)
     
    db.session.commit()
    
    return jsonify({"success": True})


@app.route("/update_privacy", methods=["POST"])
def update_privacy():
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "error": "Chưa đăng nhập."})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "error": "Không tìm thấy tài khoản."})

    data = request.get_json()
    user.privacy = {
        "hide_online": data.get("hide_online", False),
        "hide_avatar": data.get("hide_avatar", False),
        "hide_profile": data.get("hide_profile", False),
        "hide_info": data.get("hide_info", False),
        "hide_all": data.get("hide_all", False),
        "blocked_users": data.get("blocked_users", []),
    }

    db.session.commit()
    return jsonify({"success": True})

@app.route("/get_profile")
def get_profile():
    username = session.get("username")
    if not username:
        return jsonify({})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({})

    return jsonify({
        "fullname": user.fullname or "",
        "birthday": user.birthday or "",
        "bio": user.bio or "",
        "privacy": user.privacy or {}
    })


@app.route("/update_profile", methods=["POST"])
def update_profile():
    data = request.json
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập"})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "message": "Không tìm thấy user"})

    user.fullname = data.get("fullname", "")
    user.birthday = data.get("birthday", "")
    user.bio = data.get("bio", "")
    user.bio_updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True})

@app.route('/users/search')
def users_search():
    query = request.args.get('q', '').strip().lower()
    current_user = session.get("username", "").lower()

    if not query:
        return jsonify([])

    results = (
        User.query
        .filter(func.lower(User.username) != current_user)
        .filter(
            or_(
                func.lower(User.username).like(f"%{query}%"),
                func.lower(User.fullname).like(f"%{query}%"),
                func.lower(User.user_id).like(f"%{query}%"),
                func.lower(User.phone).like(f"%{query}%")
            )
        )
        .all()
    )

    return jsonify([
        {
            'username': u.username,
            'name': u.fullname,
            'user_id': u.user_id,
            'phone': u.phone,
            'online': u.online,
            'last_seen': u.last_seen.strftime("%Y-%m-%d %H:%M:%S") if u.last_seen else "",
            'avatar_url': u.avatar_url or '/static/logos/logo.png'
        }
        for u in results
    ])
def auto_offline():
    timeout = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    users_to_update = User.query.filter(User.last_seen < timeout, User.online == True).all()

    for user in users_to_update:
        user.online = False

    db.session.commit()

@app.before_request
def update_last_seen():
    # ⚠️ CHẶN TRUY CẬP ADMIN nếu không phải app hoặc không đúng email
    if request.path.startswith("/admin"):
        ua = request.headers.get("User-Agent", "")
        allow_email = request.args.get("email", "")
        correct_email = "phatth.viettel@gmail.com"
        if "Electron" not in ua:
            if allow_email != correct_email:
                return "⛔ Bạn không được phép truy cập trang này.", 403

    # 👤 CẬP NHẬT HOẠT ĐỘNG NGƯỜI DÙNG
    username = session.get("username")
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.online = True
            user.last_seen = datetime.datetime.utcnow()

            db.session.commit()


@app.route("/friends")
def friends_page():
    current_username = session.get("username")
    if not current_username:
        return redirect("/login")
    
    current_user = User.query.filter_by(username=current_username).first()
    if not current_user:
        return redirect("/login")

    auto_offline()
 
    # ✅ Lấy tất cả quan hệ có liên quan tới current_user
    friend_links = Friend.query.filter(
        (Friend.user_id == current_user.user_id) | (Friend.friend_id == current_user.user_id)
    ).all()

    friend_list = []
    seen = set()  # Để tránh bị trùng bạn bè

    for link in friend_links:
        friend_id = link.friend_id if link.user_id == current_user.user_id else link.user_id
        friend = User.query.filter_by(user_id=friend_id).first()

        if not friend or friend.username in seen:
            continue
        seen.add(friend.username)

        display_name = friend.fullname or friend.username
        print("[CHECK] User:", friend.username, "| Fullname:", friend.fullname)

        online, status_text = get_status(friend.last_seen)
        friend_list.append({
            "username": friend.username,
            "name": friend.fullname,
            "display_name": display_name,
            "fullname": friend.fullname,
            "avatar_url": friend.avatar_url or "/static/logos/logo.png",
            "last_message": "...",
            "online": online,
            "friend_status": status_text
        })
    
    # Thông tin người dùng hiện tại
    display_name = current_user.fullname or current_user.username
    user_avatar = current_user.avatar_url or url_for('static', filename='logos/logo.png')
    is_online = current_user.online
    user_id = current_user.user_id
    bio = current_user.bio or ""

    show_bio = False
    if bio and current_user.bio_updated_at:
        try:
            if datetime.utcnow() - current_user.bio_updated_at < timedelta(hours=24):
                show_bio = True
        except:
            pass
    print("🔍 Current username:", current_username)
    print("🔍 Current user_id:", current_user.user_id)
    pending_invites = FriendRequest.query.filter_by(to_user_id=current_user.user_id).count()

    return render_template("friends.html",
        friends=friend_list,
        username=current_username,
        fullname=display_name,
        user_avatar=user_avatar,
        is_online=is_online,
        bio=bio if show_bio else "",
        current_user=current_user,
        user_id=user_id,
        pending_invites=pending_invites  
    )


def load_messages():
    messages_by_chat = {}

    all_msgs = Message.query.order_by(Message.timestamp).all()
    for msg in all_msgs:
        if msg.chat_key not in messages_by_chat:
            messages_by_chat[msg.chat_key] = []

        # Lọc ảnh mất
        valid_images = [
            img for img in msg.image_urls or []
            if os.path.exists("." + img)
        ]

        messages_by_chat[msg.chat_key].append({
            "sender": msg.sender,
            "content": msg.content,
            "image_urls": valid_images,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return messages_by_chat

def save_messages(data):
    Message.query.delete()

    for chat_key, msgs in data.items():
        for m in msgs:
            sender = m.get("sender", "")
            u1, u2  = chat_key.split("__")
            receiver = u2 if u1 == sender else u1

            # json lưu timestamp dạng “2024-06-19 17:45:00” – mặc định coi là VN
            vn_time   = datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M:%S")
            utc_time  = vn_time.replace(tzinfo=VN_TZ).astimezone(UTC_TZ).replace(tzinfo=None)

            new_msg = Message(
                chat_key = chat_key,
                sender   = sender,
                receiver = receiver,
                content  = m.get("content", ""),
                image_urls = m.get("image_urls", []),
                voice_url  = m.get("voice_url"),            # thêm nếu có
                timestamp  = utc_time
            )
            db.session.add(new_msg)
    db.session.commit()

def get_status(last_seen):
    if not last_seen:
        return False, "offline"

    now = datetime.utcnow()
    delta = now - last_seen

    if delta < timedelta(minutes=5):
        return True, "Đang hoạt động"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() // 60)
        return False, f"Đã offline {minutes} phút trước"
    elif delta < timedelta(hours=24):
        hours = int(delta.total_seconds() // 3600)
        return False, f"Đã offline {hours} giờ trước"
    else:
        return False, "Đã offline"

@app.route("/chat/send/<username>", methods=["POST"])
def send_message(username):
    current_username = session.get("username")
    if not current_username:
        return jsonify({"error": "Not logged in"}), 403

    sender = User.query.filter_by(username=current_username).first()
    receiver = User.query.filter_by(username=username).first()

    if not sender or not receiver:
        return jsonify({"error": "User not found"}), 404

    # Kiểm tra bị chặn
    if sender in receiver.blocked_users:
        return jsonify({"success": False, "error": "BẠN ĐÃ BỊ CHẶN"})

    # Cập nhật trạng thái hoạt động
    sender.last_seen = datetime.utcnow()
    db.session.commit()

    # Nhận dữ liệu gửi
    text = request.form.get("text", "").strip()
    images = request.files.getlist("images")
    voice_file = request.files.get("voice")  # 👈 THÊM voice

    image_urls = []
    voice_url = None

    # ✅ Xử lý ảnh
    for image in images:
        if image and image.filename:
            ext = image.filename.rsplit(".", 1)[-1].lower()
            if ext in ["png", "jpg", "jpeg", "gif"]:
                filename = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join("static", "images", "uploads", filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                try:
                    image.save(save_path)
                    start_time = time.time()
                    while not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
                        if time.time() - start_time > 2.0:
                            raise Exception("File save timeout")
                        time.sleep(0.05)
                    image_urls.append(f"/static/images/uploads/{filename}")
                except Exception as e:
                    print("❌ Lỗi khi lưu ảnh:", e)

    # ✅ Xử lý voice
    if voice_file and voice_file.filename:
        ext = voice_file.filename.rsplit(".", 1)[-1].lower()
        if ext in ["mp3", "wav", "m4a", "ogg", "webm"]:
            filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join("static", "voices", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            try:
                voice_file.save(save_path)
                start_time = time.time()
                while not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
                    if time.time() - start_time > 2.0:
                        raise Exception("Voice save timeout")
                    time.sleep(0.05)
                voice_url = f"/static/voices/{filename}"
            except Exception as e:
                print("❌ Lỗi khi lưu voice:", e)

    # Nếu không có gì gửi thì trả lỗi
    if not text and not image_urls and not voice_url:
        return jsonify({"error": "No content"}), 400

    # Tạo chat_key
    chat_key_1 = f"{current_username}__{username}"
    chat_key_2 = f"{username}__{current_username}"
    chat_key = chat_key_1 if current_username < username else chat_key_2

    # ✅ Lưu vào PostgreSQL
    msg = Message(
        chat_key=chat_key,
        sender=current_username,
        receiver=username,
        content=text if text else None,
        image_urls=image_urls,
        voice_url=voice_url,
        timestamp=datetime.now(VN_TZ),
        read=False
    )
    db.session.add(msg)
    db.session.commit()

    # ✅ Emit đến người nhận
    socketio.emit("private_message", {
        "from": current_username,
        "to": username,
        "text": msg.content,
        "image_urls": msg.image_urls,
        "voice_url": msg.voice_url,
        "time": msg.timestamp.strftime("%H:%M")
    }, room=f"user_{username}")

    socketio.emit("new_unread_message", {
        "from": current_username
    }, room=f"user_{username}")
    print("➡️ voice_url trả về:", voice_url)
    return jsonify({
        "success": True,
        "message": {
            "sender": msg.sender,
            "text": msg.content,
            "image_urls": msg.image_urls,
            "voice_url": msg.voice_url,
            "time": msg.timestamp.strftime("%H:%M"),
            "time_full": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
    })


@app.route("/chat/<username>", methods=["GET"])
def chat(username):
    current_username = session.get("username")
    if not current_username:
        return redirect("/login")

    # Truy vấn người dùng từ PostgreSQL
    current_user = User.query.filter_by(username=current_username).first()
    friend_user = User.query.filter_by(username=username).first()

    if not friend_user:
        return "User not found", 404

    # Cập nhật trạng thái online và last_seen
    current_user.last_seen = datetime.utcnow()
    current_user.online = True
    db.session.commit()

    # Chat key thống nhất theo thứ tự
    chat_key_1 = f"{current_username}__{username}"
    chat_key_2 = f"{username}__{current_username}"
    chat_key = chat_key_1 if current_username < username else chat_key_2

    # Truy vấn toàn bộ tin nhắn theo chat_key
    messages = Message.query.filter_by(chat_key=chat_key).order_by(Message.timestamp).all()

    now = datetime.now(UTC_TZ)             # dùng UTC có tzinfo

    messages_list = []
    for msg in messages:
        # chuyển timestamp từ DB (giả sử lưu UTC naïve) ➜ UTC aware ➜ VN
        utc_time = msg.timestamp.replace(tzinfo=UTC_TZ)
        vn_time  = utc_time.astimezone(VN_TZ)

        # cảnh báo xoá 30 ngày
        days_since = (now - utc_time).days
        days_left  = 30 - days_since if days_since >= 25 else None

        messages_list.append({
            "sender":     msg.sender,
            "text":       msg.content,
            "image_urls": msg.image_urls or [],
            "voice_url":  msg.voice_url,
            "time":       vn_time.strftime("%H:%M"),
            "time_full":  vn_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days_left":  days_left
        })


    
    friend_name = friend_user.fullname or friend_user.username

    hide_online = friend_user.privacy.get("hide_online", False) if friend_user.privacy else False

    if hide_online:
        online = False
        status_text = ""  # 👈 không hiển thị gì luôn
    else:
        online, status_text = get_status(friend_user.last_seen)

    return render_template("chat.html",
        username=current_username,
        friend_username=username,
        current_user=current_user,
        friend=friend_user,
        friend_name=friend_name,
        friend_status=status_text,
        messages=messages_list,
        online=online,
        hide_online=hide_online
    )

@app.route("/api/album-images")
def api_album_images():
    current_username = session.get("username")
    friend_username = request.args.get("friend")

    if not current_username or not friend_username:
        return jsonify([])

    messages_data = load_messages()
    chat_key_1 = f"{current_username}__{friend_username}"
    chat_key_2 = f"{friend_username}__{current_username}"
    chat_key = chat_key_1 if chat_key_1 in messages_data else chat_key_2

    chat_history = messages_data.get(chat_key, [])
    image_list = []

    for msg in chat_history:
        for img in msg.get("image_urls", []):
            full_path = os.path.join(".", img.lstrip("/"))
            if os.path.exists(full_path):
                image_list.append({"url": img})

    return jsonify(image_list[::-1])


from datetime import datetime, timedelta

@app.route("/admin/cleanup_chats_30_days")
def cleanup_old_chats():
    env_admin = os.getenv("ADMIN_USERNAME")
    if not (session.get("is_admin") or session.get("username") == env_admin):
        return "Unauthorized", 403

    messages = load_messages()
    removed_chats = []
    removed_images = []

    now = datetime.now()
    cutoff = now - timedelta(days=30)

    for chat_key in list(messages.keys()):
        chat_history = messages[chat_key]
        if not chat_history:
            continue

        # Kiểm tra nếu tất cả tin nhắn đều cũ hơn 30 ngày
        all_old = True
        for msg in chat_history:
            try:
                msg_time = datetime.strptime(msg["time_full"], "%Y-%m-%d %H:%M:%S")
                if msg_time > cutoff:
                    all_old = False
                    break
            except:
                all_old = False  # Nếu không có time_full hợp lệ thì bỏ qua xoá

        if all_old:
            # Xoá ảnh liên quan
            for msg in chat_history:
                for img_url in msg.get("image_urls", []):
                    img_path = os.path.join(".", img_url.lstrip("/"))
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        removed_images.append(img_url)

            # Xoá đoạn chat
            removed_chats.append(chat_key)  
            del messages[chat_key]

    save_messages(messages)

    return f"✅ Đã xoá {len(removed_chats)} đoạn chat & {len(removed_images)} ảnh sau 30 ngày."
@app.route("/delete_old_chats")
def delete_old_chats():
    messages_data = load_messages()
    now = datetime.now()
    deleted = 0

    for key in list(messages_data.keys()):
        new_messages = []
        for msg in messages_data[key]:
            time_full = msg.get("time_full")
            if time_full:
                msg_time = datetime.strptime(time_full, "%Y-%m-%d %H:%M:%S")
                if now - msg_time < timedelta(days=30):
                    new_messages.append(msg)
                else:
                    # Nếu có ảnh thì xóa ảnh
                    for img in msg.get("image_urls", []):
                        img_path = img.lstrip("/")
                        if os.path.exists(img_path):
                            os.remove(img_path)
                    deleted += 1
            else:
                new_messages.append(msg)  # giữ lại tin cũ không có time_full
        messages_data[key] = new_messages

    save_messages(messages_data)
    return f"Đã xoá {deleted} tin nhắn cũ hơn 30 ngày."
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_username():
    # Lấy username hiện tại, ví dụ từ session
    return session.get('username')

@app.route('/friends/request', methods=['POST'])
def send_friend_request():
    current_username = session.get("username")
    to_username = request.json.get('to_user')

    if not current_username or not to_username:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400
    if current_username == to_username:
        return jsonify({'success': False, 'message': 'Không thể gửi lời mời cho chính mình'}), 400

    from_user = User.query.filter_by(username=current_username).first()
    to_user = User.query.filter_by(username=to_username).first()

    if not from_user or not to_user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404

    # Đã là bạn bè
    existing = Friend.query.filter_by(user_id=from_user.user_id, friend_id=to_user.user_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Đã là bạn bè'}), 400

    # Đã gửi lời mời
    already_sent = FriendRequest.query.filter_by(from_user_id=from_user.user_id, to_user_id=to_user.user_id).first()
    if already_sent:
        return jsonify({'success': False, 'message': 'Đã gửi lời mời trước đó'}), 400

    fr = FriendRequest(from_user_id=from_user.user_id, to_user_id=to_user.user_id)
    db.session.add(fr)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Đã gửi lời mời kết bạn'})


@app.route('/friends/requests', methods=['GET'])
def get_friend_requests():
    current_username = session.get("username")
    current_user = User.query.filter_by(username=current_username).first()

    if not current_user:
        return jsonify([])

    requests = FriendRequest.query.filter_by(to_user_id=current_user.user_id).all()
    results = []
    for r in requests:
        from_user = User.query.filter_by(user_id=r.from_user_id).first()
        if from_user:
            results.append({
                'from_username': from_user.username,
                'from_name': from_user.fullname
            })

    return jsonify(results)

@app.route('/friends/remove', methods=['POST'])
def remove_friend():
    current_username = session.get("username")
    target_username = request.json.get('target_user')

    if not current_username or not target_username:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400

    current_user = User.query.filter_by(username=current_username).first()
    target_user = User.query.filter_by(username=target_username).first()

    if not current_user or not target_user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404

    # ❌ Xóa cả 2 chiều
    Friend.query.filter_by(user_id=current_user.user_id, friend_id=target_user.user_id).delete()
    Friend.query.filter_by(user_id=target_user.user_id, friend_id=current_user.user_id).delete()

    db.session.commit()

    return jsonify({'success': True, 'message': f'Đã xoá bạn với {target_username}'})

@app.route('/friends/requests/accept', methods=['POST'])
def accept_friend_request():
    current_username = session.get("username")
    from_username = request.json.get('from_user')

    if not current_username or not from_username:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400

    current_user = User.query.filter_by(username=current_username).first()
    from_user = User.query.filter_by(username=from_username).first()

    if not current_user or not from_user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404

    already_friends = Friend.query.filter_by(user_id=current_user.user_id, friend_id=from_user.user_id).first()
    if already_friends:
        return jsonify({'success': False, 'message': 'Đã là bạn bè'}), 400

    # ✅ Thêm 2 chiều
    db.session.add(Friend(user_id=current_user.user_id, friend_id=from_user.user_id))
    db.session.add(Friend(user_id=from_user.user_id, friend_id=current_user.user_id))

    # ✅ Xoá lời mời kết bạn
    FriendRequest.query.filter_by(from_user_id=from_user.user_id, to_user_id=current_user.user_id).delete()

    db.session.commit()

    return jsonify({'success': True, 'message': 'Đã chấp nhận lời mời', 'from_username': from_username, 'from_name': from_user.fullname})

@app.route('/friends/requests/reject', methods=['POST'])
def reject_friend_request():
    current_username = session.get("username")
    from_username = request.json.get('from_user')

    if not current_username or not from_username:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'}), 400

    current_user = User.query.filter_by(username=current_username).first()
    from_user = User.query.filter_by(username=from_username).first()

    if not current_user or not from_user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404

    req = FriendRequest.query.filter_by(from_user_id=from_user.user_id, to_user_id=current_user.user_id).first()
    if not req:
        return jsonify({'success': False, 'message': 'Không có lời mời từ người này'}), 400

    db.session.delete(req)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Đã từ chối lời mời'})


@app.route("/friends/list", methods=["GET"])
def get_friends_list():
    current_username = session.get("username")
    if not current_username:
        return jsonify([])

    current_user = User.query.filter_by(username=current_username).first()
    if not current_user:
        return jsonify([])

    now = datetime.utcnow()
    result = []

    friend_links = Friend.query.filter(
        (Friend.user_id == current_user.user_id) | (Friend.friend_id == current_user.user_id)
    ).all()

    seen = set()

    for link in friend_links:
        friend_id = link.friend_id if link.user_id == current_user.user_id else link.user_id
        friend = User.query.filter_by(user_id=friend_id).first()
        if not friend or friend.username in seen:
            continue
        seen.add(friend.username)

        # ------ trạng thái online ------
        last_active = friend.last_seen
        is_online = (now - last_active) < timedelta(seconds=60) if last_active else False

        # ------ xác định chat_key ------
        chat_key_1 = f"{current_username}__{friend.username}"
        chat_key_2 = f"{friend.username}__{current_username}"
        chat_key = chat_key_1 if current_username < friend.username else chat_key_2

        # ------ Đếm tin nhắn CHƯA đọc gửi tới current user ------
        unread = Message.query.filter_by(
            chat_key=chat_key,
            receiver=current_username,
            read=False
        ).count()

        # ------ Kiểm tra tin chưa đọc mới nhất có phải chỉ 1 ảnh ------
        image_only = False
        if unread:
            newest = Message.query.filter_by(
                        chat_key=chat_key,
                        receiver=current_username,
                        read=False
                     ).order_by(Message.timestamp.desc()).first()
            if newest and newest.image_urls and not newest.content:
                image_only = len(newest.image_urls) == 1

        # ------ Gộp vào kết quả ------
        result.append({
            "username": friend.username,
            "display_name": friend.fullname or friend.username,
            "name": friend.fullname or friend.username,
            "unread": unread,
            "image_only": image_only,
            "is_online": is_online,
            "avatar_url": friend.avatar_url or "/static/logos/logo.png",
            "hide_avatar": friend.privacy.get("hide_avatar") if friend.privacy else False,
            "chat_key": chat_key
        })

    return jsonify(result)
@app.route("/chat/mark_read/<username>", methods=["POST"])
def mark_messages_as_read(username):
    current_username = session.get("username")
    if not current_username:
        return jsonify({"error": "Not logged in"}), 403

    chat_key_1 = f"{current_username}__{username}"
    chat_key_2 = f"{username}__{current_username}"
    chat_key = chat_key_1 if current_username < username else chat_key_2

    # ✅ Cập nhật tất cả tin gửi tới current_user và chưa đọc
    Message.query.filter_by(chat_key=chat_key, receiver=current_username, read=False).update({"read": True})
    db.session.commit()

    return jsonify({"success": True})

@app.route("/chat/unread_status")
def unread_status():
    username = session.get("username")
    if not username:
        return jsonify({})

    unread = Message.query.filter_by(receiver=username, read=False).all()
    return jsonify({m.sender: True for m in unread})


@app.route("/rename", methods=["POST"])
def rename_friend():
    current_username = session.get("username")
    if not current_username:
        return "Unauthorized", 403
    
    data = request.get_json()
    target = data.get("target_username")
    nickname = data.get("nickname", "").strip()

    user_data = load_data()
    user_data.setdefault(current_username, {}).setdefault("nicknames", {})

    if nickname:
        user_data[current_username]["nicknames"][target] = nickname
    else:
        user_data[current_username]["nicknames"].pop(target, None)

    save_data(user_data)
    return "OK"





@app.route("/upload_image", methods=["POST"])
def upload_image():
      # ✅ Nếu đã hết lượt dùng thử AI Toán → chặn lại
    if session.get("username") != "admin":
        user_type = get_user_type()
        if user_type != "vip":
            if not check_lite_usage():
                return jsonify({
                    "reply": "⚠️ Bạn đã dùng hết 10 lượt AI miễn phí. Vui lòng nâng cấp VIP để tiếp tục sử dụng."
                })

    image = request.files.get("image")
    if image:
        filename = secure_filename(image.filename)
        save_path = os.path.join("static", "images", "uploads", filename)
        image.save(save_path)

        try:
            solution_raw = extract_with_gpt_vision(save_path)
            session["last_ai_math_answer"] = solution_raw
            return jsonify({"reply": str (solution_raw)})
        except Exception as e:
            print("Lỗi GPT Vision:", e)
            return jsonify({"reply": "⚠️ Ảnh có vài chi tiết hơi mờ,Anh/Chị có thể chụp lại rõ hơn rồi gửi lại giúp em nhé."})
    else:
        return jsonify({"reply": "❌ Không nhận được ảnh nào."})




@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"reply": "❌ Không nhận được file PDF."})

    pdf_text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                pdf_text += page.get_text()

        print("[DEBUG] PDF TEXT:", pdf_text)

        # Gọi AI giải bài luôn từ nội dung PDF
        reply = call_gpt_viet(pdf_text)

        reply = "✏️ Rồi nha, em bắt đầu giải từng câu cho anh/chị nè!\n\n" + reply
        reply += "\n\n💬 Nếu cần em giải tiếp bài khác thì cứ gửi thêm ảnh hoặc gõ tiếp nhé!"
        return jsonify({"reply": reply})
    except Exception as e:
        print("❌ Lỗi khi xử lý PDF:", e)
        return jsonify({"reply": "⚠️ Không thể xử lý file PDF. Vui lòng thử lại với file khác."})
#==========GPT==========#
@app.route("/gpt_chat", methods=["GET"])
def gpt_chat():
    if is_maintenance("gpt_chat"):
        return render_template("gpt_chat.html",
            user_id=None,
            username=None,
            user_vip_gpt=False,
            user_vip_al=False,
            user_lite_exhausted=False,
            is_vip_chat=False,
            is_verified=False,
            chat_history=[],
            chat_id=None,
            chat_title="",
            is_maintenance=True
        )

    cleanup_old_chats()

    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    if user.is_blocked:
        session.clear()
        return render_template("login.html", error="🚫 Tài khoản của bạn đã bị khoá. Vui lòng liên hệ admin.")
    
    now = datetime.utcnow()

    # ✅ Ưu tiên gói GPT nếu còn hạn
    is_vip = False
    if username == "admin":
        is_vip = True
    elif user.vip_until_gpt and user.vip_until_gpt >= now:
        is_vip = True

    # ❗ Nếu không có gói GPT → kiểm tra AI Lite
    if not is_vip and user.vip_until_lite and user.vip_until_lite >= now:
        return redirect("/chat_lite")


    # ✅ Chặn nếu là gói 5 ngày và đã hết 100 lượt (trừ khi gpt_unlimited)
    if is_vip and user.vip_gpt == "5day" and not user.gpt_unlimited:
        usage_today = user.gpt_usage_today or 0
        usage_date = user.gpt_usage_date or ""
        today = now.strftime("%Y-%m-%d")

        if usage_date != today:
            usage_today = 0  # reset lại

        if usage_today >= 100:
            return render_template("gpt_chat.html",
                user_id=user.id,
                username=user.username,
                user_vip_gpt=True,
                user_vip_al=True,
                user_lite_exhausted=False,
                is_vip_chat=False,
                is_verified=user.is_verified,
                message_from_home="🚫 Bạn đã dùng hết 100 lượt GPT hôm nay. Vui lòng quay lại vào ngày mai hoặc nâng cấp gói.",
                chat_history=[],
                chat_id=None,
                chat_title=""
            )

    # ✅ Kiểm tra xác thực và giới hạn Lite
    lite_used = user.lite_usage or 0
    is_verified = user.is_verified

    lite_exhausted = not is_verified and lite_used >= 5

    # 🗂 Chat history
    chat_history = []
    chat_file = os.path.join("chat_history", f"{user.id}.json")
    if os.path.exists(chat_file):
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                chat_history = json.load(f)
        except Exception as e:
            print("[💥] Lỗi khi đọc đoạn chat mặc định:", e)

    session.pop("just_verified_already", None)

    return render_template("gpt_chat.html",
        user_id=user.id,
        username=user.username,
        user_vip_gpt=is_vip,
        user_vip_al=is_vip,
        user_lite_exhausted=lite_exhausted,
        is_vip_chat=is_vip,
        is_verified=is_verified,
        message_from_home=None,
        chat_history=chat_history,
        chat_id=None,
        chat_title="",
        is_maintenance=False
    )

@app.route("/gpt_viet_chat", methods=["POST"])
def gpt_viet_chat():
    if "username" not in session:
        return jsonify({"success": False, "reply": "🔒 Bạn chưa đăng nhập."})

    username = session["username"]
    user_id = session.get("user_id", "guest")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "reply": "❌ Không tìm thấy người dùng."})
    if not check_gpt_usage(user):
        return jsonify({"success": False, "reply": "🚫 Bạn đã dùng hết lượt Solver trong ngày hoặc gói đã hết hạn."})

    cap_nhat_trang_thai_vip(user)
    db.session.commit()

    if username != "admin" and not user.vip_gpt_ai:
        return jsonify({"success": False, "reply": "🔒 Bạn chưa mở khóa gói Solver Chat."})

    message = request.form.get("message", "").strip()
    img_url = None

    try:
        history = json.loads(request.form.get("history", "[]"))

        # ✅ Xử lý ảnh tạo bằng GPT
        if re.search(r"\b(vẽ|cho.*(ảnh|tranh|hình|minh hoạ)|tạo.*cảnh|minh hoạ)\b", message, re.IGNORECASE):
            image_prompt = rewrite_prompt_for_image(message)
            if not image_prompt:
                return jsonify({"success": False, "reply": "❌ Không thể tạo ảnh từ yêu cầu này."})

            img_url = generate_image_from_prompt(image_prompt)
            if not img_url:
                return jsonify({"success": False, "reply": "⚠️ Không tạo được ảnh, thử lại sau nha!"})

            reply_text = random.choice([
                "🎨 Đây là ảnh em tạo theo trí tưởng tượng của bạn nè!",
                "🖌️ Ảnh minh hoạ đã xong, bạn xem thử nha!",
                "✨ Ảnh nè! Hy vọng đúng vibe bạn muốn 😄"
            ]) + f"<br><img src='{img_url}' style='max-width:100%; border-radius:12px; margin-top:10px;'>"

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply_text})
            save_chat(user_id, history)

            return jsonify({"success": True, "reply": reply_text, "img_url": img_url})
    except Exception as e:
        print("❌ GPT IMAGE ERROR:", e)
        history = []

    try:
        # ✅ Xử lý ảnh upload (Vision)
        vision_texts = []
        vision_image_url = None
        for key in request.files:
            file = request.files[key]
            if file.filename:
                ext = os.path.splitext(file.filename)[-1]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = secure_filename(f"{timestamp}_{username}_{key}{ext}")
                user_folder = os.path.join('static', 'images', 'uploads', str(user_id))
                os.makedirs(user_folder, exist_ok=True)
                save_path = os.path.join(user_folder, filename)
                file.save(save_path)

                vision_output = extract_with_gpt_vision(save_path, user_request=message)
                vision_texts.append(f"[Ảnh: {filename}]\n{vision_output}")
                vision_image_url = f"/static/images/uploads/{user_id}/{filename}"

        if vision_texts:
            vision_combined = "\n\n".join(vision_texts)
            if message:
                message += f"\n\n🖼 Dưới đây là nội dung AI trích từ ảnh:\n{vision_combined}"
            else:
                message = f"🖼 AI đã trích nội dung từ ảnh như sau:\n{vision_combined}"

       
        reply = call_gpt_viet(message, history)

        if vision_image_url:
            reply += f"<br><img src='{vision_image_url}' style='max-width:300px; border-radius:12px; margin-top:10px;'>"

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        save_chat(user_id, history)

        return jsonify({
            "success": True,
            "reply": reply,
            "img_url": vision_image_url or img_url
        })

    except Exception as e:
        print("❌ GPT CHAT ERROR:", e)
        return jsonify({
            "reply": "⚠️ Hệ thống quá tải, bạn hãy thử lại trong ít phút nữa hoặc tạo đoạn chat mới."
        })


@app.route("/smart_emoji", methods=["POST"])
def smart_emoji():
    data = request.get_json()
    message = data.get("message", "").strip()

    # ✅ Không kiểm tra gói, chỉ cần user đăng nhập là đủ
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"emoji": []})

    # ✅ Prompt AI gợi ý emoji theo ngữ cảnh
    prompt = f"""
Người dùng đang gõ câu: \"{message}\". Đoán nhanh cảm xúc hoặc chủ đề (vui, buồn, học tập, troll, tình cảm, giận dỗi...). 
Dựa vào đó, gợi ý 3–4 emoji phù hợp. Chỉ trả về mảng JSON, ví dụ: ["😂", "📚", "😢", "🥰"].
Không thêm chữ, không giải thích.
"""

    try:
        client = create_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50
        )

        text = response.choices[0].message.content.strip()
        print("🔎 GPT Emoji raw reply:", text)

        if text.startswith("[") and text.endswith("]"):
            emoji_list = eval(text)
            if isinstance(emoji_list, list):
                return jsonify({"emoji": emoji_list})

        return jsonify({"emoji": []})  # Trả về rỗng nếu sai định dạng

    except Exception as e:
        print("❌ Lỗi smart emoji:", e)
        return jsonify({"emoji": []})



@app.route("/chat_ai_lite", methods=["POST"])
def chat_ai_lite():
    if is_maintenance("chat_ai_lite_daily") or is_maintenance("all"):
        return jsonify({"reply": "🚧 Hệ thống đang bảo trì. Vui lòng quay lại sau!"}), 503

    username = session.get("username")
    user = User.query.filter_by(username=username).first() if username else None
    if not user:
        return jsonify({"reply": "❌ Không tìm thấy người dùng."}), 404

    # Nếu có gói Lite và đang bảo trì riêng Lite
    now = now_vn()
    try:
        if user.vip_until_lite and now <= datetime.strptime(user.vip_until_lite, "%Y-%m-%d %H:%M:%S"):
            if is_maintenance("chat_lite"):
                return jsonify({"reply": "🚧 Gói AI Lite đang bảo trì. Vui lòng quay lại sau!"}), 503
        elif user.is_verified and is_maintenance("chat_ai_lite"):
            return jsonify({"reply": "🚧 AI Free 15 lượt đang bảo trì. Vui lòng quay lại sau!"}), 503
    except:
        pass

    usage_check = check_lite_usage(user)

    if usage_check == "require_verification":
        return jsonify({"reply": "📩 Bạn đã dùng hết 5 lượt miễn phí. <a href='/verify-otp' style='color:#00e676;font-weight:bold;'>Xác thực tài khoản ngay</a> để nhận thêm 10 lượt nữa!"})

    elif usage_check is False:
        if user.is_blocked:
            return jsonify({"reply": "🚫 Tài khoản bạn đã bị chặn không cho chat. Vui lòng liên hệ admin để biết thêm chi tiết."})

        try:
            if user.vip_until_lite and now <= datetime.strptime(user.vip_until_lite, "%Y-%m-%d %H:%M:%S"):
                return jsonify({"reply": "🔒 Bạn đã dùng hết 50 lượt hôm nay của gói AI Lite. Vui lòng quay lại vào ngày mai!"})
        except:
            pass

        if user.is_verified:
            return jsonify({"reply": "🔒 Bạn đã dùng hết 5 lượt miễn phí trong ngày hôm nay. Vui lòng quay lại vào ngày mai hoặc nâng cấp AI Lite/Solver để tiếp tục sử dụng."})
        else:
            return jsonify({"reply": "🔒 Bạn đã dùng hết 5 lượt miễn phí. Vui lòng xác thực tài khoản để nhận thêm 10 lượt nữa!"})
    # --- xử lý message ---
    message = request.form.get("message", "").strip()
    if not message:
        return jsonify({"reply": "⚠️ Bạn chưa nhập nội dung câu hỏi."})

    history_str = request.form.get("history", "[]")
    try:
        history = json.loads(history_str)
    except Exception as e:
        print("[💥] Không parse được history:", e)
        history = []

    # ✅ Nếu là yêu cầu tạo ảnh thì trả lời từ chối ngay (đặt TRƯỚC GỌI GPT)
    if re.search(r"\b(vẽ|minh hoạ|hình ảnh|ảnh|tranh)\b", message, re.IGNORECASE):
        reply = "🖼️ Rất tiếc, bản miễn phí và gói Lite chưa hỗ trợ tạo ảnh. Bạn hãy nâng cấp gói SolverSolver để dùng tính năng này nhé!"

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        user_id = session.get("user_id")
        if user_id:
            save_chat(user_id, history)

        return jsonify({"reply": reply})
    # --- xử lý ảnh ---
    images = []
    vision_texts = []
    image_tags = []
    for key in request.files:
        file = request.files[key]
        if file.filename:
            ext = os.path.splitext(file.filename)[-1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = secure_filename(f"{timestamp}_guest_{key}{ext}")
            save_path = os.path.join('static/images/uploads', filename)
            file.save(save_path)
            image_url = f"/static/images/uploads/{filename}"
            image_tags.append(f"<img src='{image_url}' style='max-width:200px; border-radius:8px; margin-top:8px;'>")
            vision_output = extract_with_gpt_vision(save_path, user_request=message)
            vision_texts.append(f"[Ảnh: {filename}]\n{vision_output}")

    if vision_texts:
        if image_tags:
            message += "<br>" + "<br>".join(image_tags)
        vision_combined = "\n\n".join(vision_texts)
        message += f"\n\n🖼 Dưới đây là nội dung AI trích từ ảnh:\n{vision_combined}"

    try:
        reply = call_gpt_lite(message, history)
    except Exception as e:
        print("❌ Lỗi khi gọi GPT Lite:", e)
        return jsonify({"reply": "⚠️ Hệ thống quá tải, bạn hãy thử lại trong ít phút nữa hoặc tạo đoạn chat mới."})

    if vision_texts:
        reply += "\n\nCó thể một vài chi tiết trong ảnh hơi mờ nhạt hoặc sai. Mong bạn kiểm tra lại giúp mình nha."

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    user_id = session.get("user_id")
    if user_id:
        save_chat(user_id, history)

    # --- trừ lượt nếu chưa xác thực ---
    if not user.is_verified:
        user.free_gpt_uses = max(0, (user.free_gpt_uses or 0) - 1)
        db.session.commit()

    return jsonify({"reply": reply})


#AI LITE
@app.route("/chat_lite", methods=["GET"])
def chat_lite():
    if is_maintenance("chat_lite"):
        return render_template("maintenance.html")

    username = session.get("username")
    user_id = session.get("user_id")

    if not username or not user_id:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    # 🛡️ Nếu chưa xác thực và đã hết lượt miễn phí → bắt xác thực
    if not user.is_verified and (user.free_gpt_uses or 0) <= 0:
        return redirect("/verify-otp")

    # ❌ Nếu có gói GPT → redirect
    now = now_vn()
    def valid(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S") > now
        except:
            return False

    if user.vip_gpt_ai and valid(user.vip_until_gpt or ""):
        return redirect("/chat_redirect")

    # 🗂 Lịch sử đoạn chat (vẫn lấy từ file)
    chat_history = []
    chat_file = os.path.join("chat_history", f"{user_id}.json")
    if os.path.exists(chat_file):
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                chat_history = json.load(f)
        except Exception as e:
            print(f"[💥] Không đọc được chat_history: {e}")

    return render_template(
        "chat_ai_lite.html",
        user_id=user_id,
        username=username,
        user_lite_exhausted=False,
        is_verified=user.is_verified,
        chat_history=chat_history,
        chat_id=None,
        chat_title="",
        is_maintenance=is_maintenance("chat_lite")
    )

#RESET LUỢT MỖI NGÀY
@app.route("/chat_ai_lite", methods=["GET"])
def chat_ai_lite_page():
    if is_maintenance("chat_ai_lite_daily"):
        return render_template("maintenance.html")

    username = session.get("username")
    user_id = session.get("user_id")

    if not username or not user_id:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    # 🛡️ Nếu chưa xác thực và đã hết lượt miễn phí → bắt xác thực
    if not user.is_verified and (user.free_gpt_uses or 0) <= 0:
        return redirect("/verify-otp")

    # ❌ Nếu có gói GPT hoặc AI Lite → redirect
    now = now_vn()
    def valid(date_str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt) > now
            except:
                continue
        return False
    if (user.vip_gpt_ai and valid(user.vip_until_gpt or "")) or \
       (user.vip_ai_lite and valid(user.vip_until_lite or "")):
        return redirect("/chat_redirect")

    # 🗂 Lịch sử đoạn chat
    chat_history = []
    chat_file = os.path.join("chat_history", f"{user_id}.json")
    if os.path.exists(chat_file):
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                chat_history = json.load(f)
        except Exception as e:
            print(f"[💥] Không đọc được chat_history: {e}")

    return render_template(
        "chat_ai_lite_daily.html",
        user_id=user_id,
        username=username,
        user_lite_exhausted=False,
        is_verified=user.       verified,
        chat_history=chat_history,
        chat_id=None,
        chat_title="",
        is_maintenance=is_maintenance("chat_ai_lite")
    )


# KIỂM TRA GÓI CHAT
@app.route("/chat_redirect", methods=["GET"])
def chat_redirect():
    if is_maintenance("chat_ai_lite_daily") or \
       is_maintenance("chat_ai_lite") or \
       is_maintenance("chat_lite") or \
       is_maintenance("gpt_chat"):
        return render_template("maintenance.html")

    username = session.get("username")
    if not username:
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect("/login")

    now = now_vn()

    def valid(dt):
        try:
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            return dt > now
        except:
            return False

    # Gói GPT còn hạn
    if user.vip_gpt and valid(user.vip_until_gpt):
        return redirect("/gpt_chat")  # gpt_chat.html

    # Gói AI Lite còn hạn
    if user.vip_ai_lite and valid(user.vip_until_lite):
        return redirect("/chat_lite")  # chat_ai_lite.html

    # Tài khoản mới tạo (15 lượt free)
    if (user.free_gpt_uses or 0) > 0:
        return render_template("gpt_chat_lite.html", chat_history=[])

    # Đã xác thực → Free 5 lượt mỗi ngày
    if user.is_verified:
        return render_template("chat_ai_lite_daily.html", chat_history=[])

    # Chưa xác thực, hết free → Bắt xác thực
    flash("📩 Bạn cần xác thực email để tiếp tục sử dụng AI.")
    return redirect("/verify-otp")


#GỬI TIN TỪ HOME QUA AI VÀ TỰ KIỂM TRA THÔNG MINH
@app.route("/get-user-package")
def get_user_package():
    from datetime import datetime
    username = session.get("username")
    if not username:
        return jsonify({"status": "not_logged_in"})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "not_logged_in"})

    now = now_vn()

    # Kiểm tra VIP GPT
    is_vip_gpt = False
    if user.vip_gpt:
        try:
            vip_until = datetime.strptime(user.vip_until_gpt, "%Y-%m-%d %H:%M:%S")
            is_vip_gpt = now <= vip_until
        except:
            pass

    # Kiểm tra gói AI Lite
    is_lite = False
    if user.vip_ai_lite:
        try:
            lite_until = datetime.strptime(user.vip_until_lite, "%Y-%m-%d %H:%M:%S")
            is_lite = now <= lite_until
        except:
            pass

    return jsonify({
        "status": "ok",
        "is_vip_gpt": is_vip_gpt,
        "is_lite": is_lite,
        "verified": user.is_verified
    })


#AI VẼ HÌNH
def generate_ai_prompt(user_text):
    return (
        f"Tạo hình ảnh theo mô tả: {user_text}. "
        "Ảnh nên rõ ràng, trình bày đẹp, không thêm chi tiết dư thừa, phù hợp sách vở hoặc minh hoạ học thuật."
    )
@app.route("/generate_image_from_text", methods=["POST"])
def draw_math_figure():
    data = request.json
    user_input = data.get("text", "")

    if not user_input:
        return jsonify({"error": "Bạn chưa nhập nội dung cần vẽ."})

    try:
        prompt = generate_ai_prompt(user_input)
        image_url = generate_image_from_prompt(prompt)
        return jsonify({"img_url": image_url, "source": "ai"})
    except Exception as e:
        print("❌ Lỗi tạo hình AI:", e)
        return jsonify({"error": "Không tạo được hình từ AI. Vui lòng thử lại."})



@app.route("/generate_image", methods=["POST"])
def generate_image():
    username = session.get("username")
    if not username:
        return jsonify({"error": "🔒 Bạn chưa đăng nhập."})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "🔒 Không tìm thấy tài khoản."})

    cap_nhat_trang_thai_vip(user)
    db.session.commit()

    # ✅ Admin được phép tạo ảnh không giới hạn
    if username != "admin":
        if not user.vip_gpt_ai and user.lite_usage >= 20:
            return jsonify({"error": "⚠️ Bạn đã hết lượt miễn phí hoặc gói AI đã hết hạn."})

    prompt = request.json.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "❌ Bạn chưa nhập nội dung hình muốn tạo."})

    try:
        img_url = generate_image_from_prompt(prompt)
        return jsonify({"img_url": img_url})
    except Exception as e:
        print("❌ Lỗi khi tạo ảnh:", e)
        return jsonify({"error": "⚠️ Không thể tạo ảnh. Vui lòng thử lại sau."})

#GỬI FILE
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"reply": "Không có file được gửi."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"reply": "File không hợp lệ."}), 400

    filename = secure_filename(file.filename)
    user_id = session.get("user_id", "guest")
    existing_path = os.path.join("static", "images", "uploads", user_id, filename)

    if not os.path.exists(existing_path):
        print("⚠️ [UPLOAD] File không tồn tại trong thư mục người dùng:", existing_path)
        return jsonify({"reply": "⚠️ File không tồn tại hoặc đã bị xoá."}), 400

    # ✅ Cập nhật thời gian sửa file để lọc 7 ngày
    os.utime(existing_path, None)
    print("📥 [UPLOAD] Đã cập nhật mtime cho:", existing_path)

    return jsonify({"reply": f"✅ Đã cập nhật ảnh: {filename}"})



#MỞ ÂM BUM
@app.route("/get_user_album")
def get_user_album():
    user_id = session.get("user_id", "guest")
    upload_dir = os.path.join("static", "images", "uploads", str(user_id))

    now = time.time()
    max_age = 7 * 86400  # 7 ngày

    print(f"[ALBUM] Đang kiểm tra ảnh tại: {upload_dir}")

    images = []
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                path = os.path.join(upload_dir, filename)
                mtime = os.path.getmtime(path)
                age = now - mtime

                print(f"[ALBUM] Ảnh: {filename}, mtime: {mtime}, age: {age}")

                if age <= max_age:
                    images.append({
                        "path": f"/{path.replace(os.sep, '/')}"
                    })
    print(f"📸 [ALBUM] Đã tìm thấy {len(images)} ảnh gần nhất trong {upload_dir}")
    print(f"[ALBUM] Tổng cộng {len(images)} ảnh hợp lệ.")
    return jsonify({"images": images})
#LỊCH SỬ ĐOẠN CHAT
@app.route("/save_chat", methods=["POST"])
def save_chat_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    messages = data.get("messages", [])

    folder = os.path.join("chat_history")
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{user_id}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/load_chat/<chat_id>")
def load_chat(chat_id):
    user_id = session.get("user_id", "guest")
    folder = os.path.join("chat_history", user_id)
    file_path = os.path.join(folder, f"{chat_id}.json")

    if not os.path.exists(file_path):
        return jsonify({"error": "Không tìm thấy đoạn chat."}), 404

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return jsonify({"chat": data})

@app.route("/reset_current_chat")
def reset_current_chat():
    session.pop("current_chat_id", None)
    return jsonify({"success": True})

@app.route("/new_chat", methods=["POST"])
def new_chat():
    user_id = session.get("user_id")

    # ✅ Nếu không đăng nhập, vẫn cho reset session chat
    if not user_id:
        session.pop("chat_history", None)
        session.pop("chat_ai_lite_history", None)
        return jsonify({"success": True})

    try:
        # ✅ Nếu đã đăng nhập → xoá file chat nếu có
        chat_file = os.path.join("chat_history", f"{user_id}.json")
        if os.path.exists(chat_file):
            os.remove(chat_file)

        # ✅ Xoá session cũ
        session.pop("chat_history", None)
        session.pop("chat_ai_lite_history", None)

        return jsonify({"success": True})
    except Exception as e:
        print("[💥] Lỗi khi xoá đoạn chat:", e)
        return jsonify({"success": False, "error": "Lỗi nội bộ"})

#TƯƠNG TÁC VỚI NGƯỜI DÙNG
@app.route('/send-emoji', methods=['POST'])
def handle_emoji():
    data = request.get_json()
    emoji = data.get('emoji')
    last_reply = data.get('last_reply', '')

    # Prompt cảm xúc
    emotion_prompts = {
        "❤️": "Người dùng rất thích câu trả lời. Hãy phản hồi nhẹ nhàng, tích cực và tiếp tục mạch hội thoại.",
        "😂": "Người dùng thấy vui vẻ. Hãy đáp lại hài hước hoặc gần gũi hơn.",
        "😢": "Người dùng hơi buồn. Hãy động viên nhẹ nhàng và hỏi xem bạn có thể giúp gì.",
        "🤔": "Người dùng đang suy nghĩ. Hãy hỏi xem có chỗ nào cần giải thích rõ hơn.",
        "😡": "Người dùng chưa hài lòng. Hãy xin lỗi lịch sự và mời họ nêu vấn đề cụ thể."
    }

    emotion_context = emotion_prompts.get(emoji, "Người dùng vừa thả cảm xúc. Hãy phản hồi phù hợp.")

    prompt = f"""Bạn là trợ lý AI đang trò chuyện với người dùng.

Câu trả lời trước đó của bạn:
\"{last_reply}\"

Người dùng không nhập văn bản, nhưng vừa thả cảm xúc: {emoji}

{emotion_context}

Hãy tiếp tục phản hồi mạch lạc, dựa vào câu trước. Nếu có thể, hãy gợi ý người dùng nói rõ hơn, hoặc giải thích thêm để hỗ trợ tốt hơn.
Đừng phản hồi chung chung, hãy giữ đúng bối cảnh cuộc trò chuyện.
"""


    # Gọi GPT
    client = create_openai_client()
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
    )
    reply = response.choices[0].message.content.strip()
    return jsonify({"ai_reply": reply})
#GIAO DIỆN CHÍNH GỬI FILE
@app.route("/upload_file_to_ai", methods=["POST"])
def upload_file_to_ai():
    file = request.files.get("file")
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join("static/images/uploads", filename)
        file.save(save_path)
        return jsonify({"success": True, "filename": save_path})
    return jsonify({"success": False})
#GÓP Ý BÁO LỖI

UPLOAD_FOLDER = "static/uploads_feedback"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/gop-y", methods=["GET", "POST"])
def gop_y():
    if request.method == "POST":
        image_paths = []

        images = request.files.getlist("images")
        if images and any(img.filename != "" for img in images):
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    timestamp = str(int(time.time()))
                    full_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{timestamp}_{filename}")
                    image.save(full_path)
                    image_paths.append("/" + full_path.replace("\\", "/"))  # để hiển thị được

        print("🖼 Ảnh đã lưu:", image_paths)  # ✅ kiểm tra terminal

        full_name = request.form.get("full_name", "Ẩn danh")
        user_email = request.form.get("user_email", "")
        user_id = request.form.get("user_id", "")
        message = request.form.get("message", "")
        username = session.get("username", "Khách")
        category = request.form.get("category", "")

        # Ghi log
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            vn_time = datetime.utcnow() + timedelta(hours=7)  # múi giờ VN
            f.write(f"🕒 [{vn_time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"👤 {full_name}\n")
            f.write(f"📧 {user_email}\n")
            f.write(f"🔐 {username}\n")
            f.write(f"🆔 {user_id}\n")
            f.write(f"✍️ {message}\n")
            if image_paths:
                f.write(f"📎 {' | '.join(image_paths)}\n")
            f.write("---\n\n")

        # ✅ Redirect để tránh spam reload
        session["gopy_success"] = True
        session["gopy_category"] = category
        return redirect("/gop-y")

    # GET request
    success = session.pop("gopy_success", False)
    category = session.pop("gopy_category", "")
    return render_template("gop_y.html", success=success, category=category)



#Giao diện nhận góp ý 
def extract(block, prefix):
    for line in block.splitlines():
        if line.strip().startswith(prefix):
            return line.replace(prefix, "").strip()
    return ""

def extract_loose(block, prefix):
    for line in block.splitlines():
        if prefix in line:
            return line.split(prefix, 1)[1].strip()
    return ""

@app.route("/admin/gop-y")
@admin_only
def admin_gopy():
    # ✅ Chỉ admin mới được truy cập
    if not session.get("is_admin"):
        return redirect("/admin_login")

    entries = []
    try:
        with open("feedback_log.txt", "r", encoding="utf-8") as f:
            blocks = f.read().split("---\n\n")
            for idx, block in enumerate(blocks, 1):
                if block.strip():
                    entry = {
                        "index": idx,
                        "time": extract(block, "🕒"),
                        "name": extract(block, "👤"),
                        "email": extract_loose(block, "📧"),
                        "user_id": extract(block, "🆔"),
                        "username": extract_loose(block, "🔐"),
                        "message": extract(block, "✍️"),
                        "image_paths": extract(block, "📎").split(" | ") if extract(block, "📎") else [],
                        "type": extract(block, "📂")

                    }
                    entries.append(entry)
    except FileNotFoundError:
        pass

    return render_template("admin_gopy.html", feedback_entries=entries)





@app.route("/bo-qua", methods=["POST"])
@admin_only
def bo_qua():
    try:
        entry_index = int(request.form.get("entry_index"))
    except (TypeError, ValueError):
        return "Chỉ số không hợp lệ", 400

    try:
        with open("feedback_log.txt", "r", encoding="utf-8") as f:
            blocks = f.read().split("---\n\n")
    except FileNotFoundError:
        blocks = []

    if 0 <= entry_index - 1 < len(blocks):
        del blocks[entry_index - 1]

        with open("feedback_log.txt", "w", encoding="utf-8") as f:
            f.write("---\n\n".join(blocks).strip() + "\n")

    return redirect("/admin/gop-y")


#Bảo mật tối thượng
# ====== BẢO MẬT MỞ CỔNG ADMIN ======

TRUSTED_IP = os.getenv("TRUSTED_IP")
BACKDOOR_CODE = os.getenv("BACKDOOR_CODE")

def is_trusted_ip():
    return request.remote_addr == TRUSTED_IP



@app.route("/feedback")
def feedback_redirect():
    return redirect("/gop-y")  # nếu trang thật là /gop-y
#GỬI KHIẾU NẠI CHO USER KHÔNG ĐĂNG NHẬP
@app.route("/appeal", methods=["GET", "POST"])
def appeal():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        user_id = request.form.get("user_id")
        user_email = request.form.get("email")
        message = request.form.get("message")
        category = request.form.get("category", "Khiếu nại tài khoản")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 📎 Xử lý ảnh
        saved_paths = []
        if "images" in request.files:
            images = request.files.getlist("images")
            for img in images:
                if img.filename:
                    filename = f"{uuid.uuid4().hex}_{secure_filename(img.filename)}"
                    folder = "static/images/feedback"
                    os.makedirs(folder, exist_ok=True)
                    path = os.path.join(folder, filename)
                    img.save(path)
                    saved_paths.append(f"/{path.replace(os.sep, '/')}")

        # 📝 Ghi log
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(f"""🕒 {now}
👤 {full_name}
🆔 {user_id}
📧 {user_email}
🔐 (không có)
✍️ {message}
📎 {' | '.join(saved_paths)}
📂 {category}
---\n\n""")

        return render_template("appeal.html", success=True)

    return render_template("appeal.html")

with app.app_context():
    from models.user import User  # import các model ở đây
    db.create_all() 
from flask_socketio import join_room, emit
import datetime

# --------------------------
# JOIN ROOM MẶC ĐỊNH KHI VỪA CONNECT
# --------------------------
@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    user_id = data.get("user_id")
    device = data.get("device")  # ex: 'web', 'android', 'ios' nếu muốn dùng sau này

    if not username:
        return  # thiếu thông tin, không join

    room = f"user_{username}"  # dùng prefix để tránh trùng với room khác
    join_room(room)

    print(f"[JOIN] User {username} (user_id: {user_id}) joined room {room} at {datetime.datetime.now()}")


# --------------------------
# JOIN ROOM TUỲ Ý (Group, phòng chat, v.v.)
# --------------------------
@socketio.on("join_room")
def handle_join_room(data):
    room = data.get("room")
    if room:
        join_room(room)
        print(f"[ROOM] Joined custom room: {room}")


# --------------------------
# NGHE GỌI 1-1
# --------------------------
@socketio.on("call-user")
def handle_call_user(data):
    to = data.get("to")
    from_user = data.get("from")
    call_type = data.get("type")

    if to:
        emit("incoming-call", {
            "from": from_user,
            "type": call_type
        }, room=f"user_{to}")  # dùng room có prefix


@socketio.on("reject-call")
def handle_reject_call(data):
    to = data.get("to")
    if to:
        emit("call-rejected", {}, room=f"user_{to}")


@socketio.on("cancel-call")
def handle_cancel_call(data):
    to = data.get("to")
    if to:
        emit("call-cancelled", {}, room=f"user_{to}")


# --------------------------
# SIGNALING (WebRTC)
# --------------------------
@socketio.on("offer")
def handle_offer(data):
    to = data.get("to")
    if to:
        emit("receive-offer", data, room=f"user_{to}")


@socketio.on("answer")
def handle_answer(data):
    to = data.get("to")
    if to:
        emit("receive-answer", data, room=f"user_{to}")


@socketio.on("ice-candidate")
def handle_ice_candidate(data):
    to = data.get("to")
    if to:
        emit("ice-candidate", data, room=f"user_{to}")
