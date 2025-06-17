import base64
from openai_config import client
from PIL import Image
import io

def extract_with_gpt_vision(image_path, user_request=None):
    # Đọc ảnh → base64
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Prompt thông minh thích nghi mọi nội dung ảnh
    system_content = (
        "Bạn là một trợ lý thông minh, thân thiện và mô tả ảnh như con người. "
        "Không được nhắc đến GPT, AI, công nghệ hay nền tảng kỹ thuật. "
        "Nếu ảnh là bài tập – hãy giải hoặc diễn giải. "
        "Nếu là meme, bảng nội quy, biển báo, quảng cáo, sản phẩm – hãy mô tả tự nhiên. "
        "Nếu có chữ – hãy ghi lại. Nếu không rõ thì mô tả những gì bạn thấy một cách thân thiện, khách quan."
    )

    if user_request:
        user_text = f"Ảnh sau có nội dung. Yêu cầu cụ thể: {user_request}. Nếu không rõ thì mô tả tự nhiên, rõ ràng."
    else:
        user_text = "Hãy xem ảnh sau và mô tả chi tiết nội dung theo cách thân thiện và dễ hiểu nhất."

    # Gọi GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }
        ],
        max_tokens=1200
    )

    return response.choices[0].message.content.strip()
