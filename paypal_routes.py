import os
import requests
from flask import Blueprint, request, redirect,url_for, session,jsonify
from models.user import User

from models.transaction import Transaction

paypal = Blueprint("paypal", __name__)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_EMAIL = "phatth.viettel@gmail.com"  # 🔁 ĐỔI thành email PayPal thật của bạn
PAYPAL_API = "https://api-m.paypal.com"  # Khi live, đổi thành https://api-m.paypal.com

@paypal.route("/paypal/success")
def paypal_success():
    order_id = request.args.get("token")
    if not order_id:
        return "❌ Không tìm thấy mã đơn hàng."

    # Lấy access token
    token_res = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    access_token = token_res.json().get("access_token")
    if not access_token:
        return "❌ Không thể xác thực PayPal."

    # Gửi yêu cầu capture để xác minh thanh toán
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.post(f"{PAYPAL_API}/v2/checkout/orders/{order_id}/capture", headers=headers)

    if res.status_code == 201:
        from app import db
        from flask import session, url_for
        from datetime import datetime, timedelta

        # ✅ Nếu thành công, tự gán VIP cho user hiện tại
        username = session.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                now = datetime.now()
                pkg = session.get("pending_package")

                if pkg == "vip_gpt_5d":
                    user.vip_gpt_ai = True
                    user.vip_gpt = "5day"
                    user.vip_until_gpt = now + timedelta(days=5)
                    user.gpt_usage_today = 0
                    user.gpt_usage_date = now.strftime("%Y-%m-%d")
                    user.gpt_unlimited = False

                elif pkg == "vip_gpt_15d":
                    user.vip_gpt_ai = True
                    user.vip_gpt = "15day"
                    user.vip_until_gpt = now + timedelta(days=15)
                    user.gpt_unlimited = True

                elif pkg == "vip_gpt_30d":
                    user.vip_gpt_ai = True
                    user.vip_gpt = "30day"
                    user.vip_until_gpt = now + timedelta(days=30)
                    user.gpt_unlimited = True

                elif pkg == "vip_ai_lite":
                    user.vip_ai_lite = True
                    user.vip_until_lite = now + timedelta(days=7)
                    user.vip_lite_daily_limit = 50
                    user.lite_usage = 0
                    user.lite_date = now.strftime("%Y-%m-%d")

                else:
                    return "❌ Gói không xác định."

                session.pop("pending_package", None)
                db.session.commit()
                # ✅ Ghi giao dịch vào bảng Transaction
                txn = Transaction(
                    txn_id=order_id,
                    username=username,
                    amount="1.00",
                    package=pkg,
                    method="PayPal",
                    status="success"
                )
                db.session.add(txn)
                db.session.commit()


        return redirect(url_for("home_page"))  # 🎯 Sửa thành tên route chính của bạn (VD: 'chat' hoặc 'home')
    
    return "❌ Thanh toán thất bại hoặc chưa hoàn tất."
@paypal.route("/paypal/start", methods=["POST"])
def paypal_start():
    pkg = request.json.get("package")

    if not pkg:
        return jsonify({"error": "Thiếu thông tin gói cần thanh toán."}), 400

    session["pending_package"] = pkg

    price_map = {
            "vip_gpt_5d": "2.00",
            "vip_gpt_15d": "4.50",
            "vip_gpt_30d": "6.10",
            "vip_ai_lite": "1.05"
        }

    amount = price_map.get(pkg)
    if not amount:
        return jsonify({"error": "Gói không hợp lệ."}), 400

    return_url = url_for("paypal.paypal_success", _external=True)
    cancel_url = url_for("upgrade", _external=True)

    # Lấy access token
    token_res = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    access_token = token_res.json().get("access_token")
    if not access_token:
        return jsonify({"error": "Không thể lấy access token PayPal."}), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Tạo đơn hàng
    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": amount
            }
        }],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }

    res = requests.post(f"{PAYPAL_API}/v2/checkout/orders", headers=headers, json=order_payload)
    if res.status_code == 201:
        approval_url = next(link["href"] for link in res.json()["links"] if link["rel"] == "approve")
        return jsonify({"url": approval_url})
    else:
        return jsonify({"error": f"Không thể tạo đơn hàng PayPal: {res.text}"}), 500
