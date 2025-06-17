
from datetime import datetime
from models.user import User
from extensions import db
def normalize_package(pkg):
    mapping = {
        "vip_ai_lite": "vip_ai_lite",
        "vip_al_ai": "vip_ai_lite",
        "vip_al_1d": "vip_ai_lite",
        "vip_gpt_ai": "vip_gpt_30d",
        "vip_gpt_ai_1": "vip_gpt_5d",
        "vip_gpt_ai_3": "vip_gpt_15d",
        "vip_gpt_ai_7": "vip_gpt_30d",
        "vip_al_3d": "vip_ai_lite",  # nếu sau này có
        "vip_al_lite": "vip_ai_lite",  # nếu có
    }
    return mapping.get(pkg.strip().lower(), pkg.strip().lower())

