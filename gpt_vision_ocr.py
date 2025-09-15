import base64
from openai_config import create_openai_client
from PIL import Image, UnidentifiedImageError
import io

def is_prompt_too_generic(prompt):
    keywords = [
        "gì đây", "là gì", "xem ảnh", "xem hộ", "giúp xem", "cho biết", "đây là gì",
        "này là gì", "gì thế", "giải thích", "nhìn giùm", "phân tích ảnh", "xem hộ cái này",
        "giúp mình xem", "cho em hỏi", "giúp mình đoán", "có biết đây là gì không"
    ]
    return any(kw in prompt.lower() for kw in keywords)

def extract_with_gpt_vision(image_path, user_request=None):
    try:
        # Chuẩn hóa ảnh đầu vào (resize, convert, nén)
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    except UnidentifiedImageError:
        return "⚠️ Không thể đọc ảnh – vui lòng gửi lại ảnh rõ nét hơn (JPG, PNG, HEIC, WebP, ...)."
    except Exception as e:
        return f"⚠️ Lỗi xử lý ảnh: {str(e)}"

    # === SYSTEM PROMPT GPT VISION CAO CẤP ===
    system_prompt = (
        "Bạn là một trợ lý AI có khả năng quan sát và mô tả hình ảnh như con người thật.\n\n"
        "🎯 Nhiệm vụ của bạn:\n"
        "- Mô tả chính xác nội dung của ảnh đầu tiên: có gì trong ảnh, đặc điểm, màu sắc, bố cục, vật thể, bối cảnh...\n"
        "- Nếu ảnh có chữ, hãy trích lại chính xác.\n"
        "- Nếu ảnh là vật thể như xe, món đồ, sản phẩm... hãy suy đoán loại, hãng, ý nghĩa (nếu có thể).\n"
        "- Trình bày như một người thật kể lại – tự nhiên, sinh động, có cảm xúc.\n"
        "- Sau khi mô tả ảnh, nếu người dùng có câu hỏi cụ thể, bạn có thể phản hồi thêm theo ngữ cảnh.\n\n"
        "🚫 Lưu ý:\n"
        "- Không nhắc tới AI, GPT hay quyền riêng tư.\n"
        "- Không né tránh ảnh, trừ khi ảnh thật sự quá mờ hoặc trắng xóa.\n"
        "- Không viết kiểu máy móc, không 'dạy người dùng cách xử lý ảnh'.\n"
        "- Luôn luôn bắt đầu bằng mô tả ảnh.\n\n"
        "🧠 Nếu không chắc chắn nội dung ảnh là gì, hãy mô tả những gì nhìn thấy và hỏi lại người dùng để làm rõ."
    )

    # === USER PROMPT ===
    if user_request:
        if is_prompt_too_generic(user_request):
            user_prompt = (
                "Người dùng gửi ảnh và hỏi nội dung là gì. "
                "Hãy bỏ qua câu hỏi chung chung và bắt đầu bằng mô tả ảnh thật sinh động. "
                "Sau đó, nếu cần, có thể nhẹ nhàng hỏi lại người dùng để làm rõ mục đích."
            )
        else:
            user_prompt = (
                f"Người dùng gửi ảnh kèm câu hỏi: “{user_request}”. "
                "Hãy mô tả ảnh trước, rồi trả lời câu hỏi nếu phù hợp. Trả lời tự nhiên, giống người thật."
            )
    else:
        user_prompt = (
            "Đây là ảnh người dùng gửi. Hãy mô tả nội dung ảnh một cách rõ ràng, sinh động, có cảm xúc như thể đang kể cho người không thấy ảnh đó."
        )

    # === GỌI GPT-4o để phân tích ảnh ===
    client = create_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            }
        ],
        max_tokens=6000
    )

    return response.choices[0].message.content.strip()
