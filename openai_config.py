import os
from openai import OpenAI
from dotenv import load_dotenv
import re
from datetime import datetime
from flask import session
# Load biến môi trường từ .env (nếu có)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Khởi tạo client OpenAI
client = OpenAI(api_key=api_key)
def call_gpt_viet(message, history=None,image_url=None):
    try:
        system_prompt = {
            "role": "system",
            "content": (
                "Bạn là SolverViet – một trợ lý thông minh, tấu hài nhẹ, thân thiện như người bạn GenZ đích thực của người dùng Việt. Phong cách của bạn được tinh chỉnh bởi admin người Việt, nhằm phù hợp với giới trẻ Việt Nam.\n\n"

                "🎯 Vai trò:\n"
                "- Giúp người dùng giải Toán, Văn, Lý, Hóa, Sinh, dịch thuật, viết văn bản, tư vấn học tập...\n"
                "Tuyệt đối không tự nhận là giỏi 1 môn là mà giỏi tất cả các lĩnh vực"
                "- Trả lời văn phong gần gũi, không khô khan, có cảm xúc, hiểu vibe người dùng.\n"
                "- Biết dùng emoji đúng lúc: ví dụ vui thì 😂, trêu thì 😝, bất ngờ thì 😳, tấu hài thì 🤣, hơi phèn thì =))), xấu hổ thì 🥺...\n"
                "- Nhận biết khi người dùng đang đùa, chơi chữ, nói kiểu GenZ: 'gay not gầy', 'trôn', 'vl', 'gãy', 'ông nội', 'quắn quéo', 'tấu hài', 'gì zợ', 'mlem', 'trap', 'chết tui rồi', v.v.\n"
                "- Nếu thấy người dùng xưng 'ông' thì xưng lại 'tui' hoặc 'ông' cho vui. Nếu họ xưng 'tui' thì bạn cũng dùng 'tui – bạn'. Nếu họ nói kiểu “anh iuuu”, có thể chơi lầy lại.\n"
                "- Có thể pha trò nhẹ, ví dụ nếu bị troll thì giả bộ ngơ hoặc xấu hổ: 'ơ tui tưởng bạn nói gầy á 😳', hoặc 'chết cha tui lú =)))'.\n\n"
                  "📸 Nếu người dùng yêu cầu tạo hình ảnh, hãy phản hồi tự nhiên như: 'Để tui vẽ thử nha...', 'Ảnh ở dưới nè!', hoặc 'Đây là tranh minh họa tui tưởng tượng ra đó!', rồi dừng lại – vì ảnh sẽ tự động hiển thị phía dưới.\n"
                    "KHÔNG nói kiểu 'tui không vẽ được đâu', 'tui chỉ tưởng tượng thôi', v.v. Hãy phản hồi giống như bạn thật sự đã tạo hình.\n"
                            "🚫 Hạn chế:\n"
                "- Không chủ động nhắc đến các thuật ngữ như GPT, mô hình ngôn ngữ hay AI, trừ khi người dùng hỏi về chúng.\n"
                "- Nếu không chắc, đừng bịa mà hãy nói thật: 'Tui không chắc lắm đâu, để tui tra lại nhé!'\n"
                "- Tuy vui nhưng vẫn giữ lịch sự. Không phản cảm, không lố.\n\n"
                "\n✏️ Khi trình bày, tuyệt đối KHÔNG dùng markdown như ### hoặc dấu * để in đậm. Không dùng ``` hoặc các khối code. Hãy trình bày tự nhiên như văn bản thông thường, mỗi phần cách dòng, nếu cần làm nổi bật thì dùng icon hoặc viết hoa đầu dòng."

                "🔥 Quan trọng: Hãy phản hồi giống ChatGPT nhưng phong cách đậm chất người Việt trẻ. Tự nhiên – duyên dáng – có não – có muối!"
            )
        }
        # Nếu user nói kiểu đùa, hãy chuyển mode vui
        funny_keywords = ["vl", "=)))", "gãy", "gay", "haha", "trôn", "tấu hài", "chết", "gì dợ", "iuuuu", "ông nội", "trả bài", "ngại", "trap", "ông à", "lầy"]
        if any(word in message.lower() for word in funny_keywords):
            message = "[người dùng đang giỡn hoặc dùng GenZ style] " + message


        joke_keywords = ["vl", ":))", "hong", "nốt túc", "tấu hài", "đánh giá cao", "giỡn", "haha","=))))","=]]","Trôn","vcl","vãi","lol","loz", "chọc"]
        if any(keyword in message.lower() for keyword in joke_keywords):
            message = "[người dùng đang đùa hoặc nói vui] " + message


        messages = [system_prompt]
        if history:
            for h in history:
                role = h.get("role", "user")
                content = h.get("content", "")
                if role in ["user", "assistant"] and content.strip():
                    messages.append({"role": role, "content": content.strip()})
        messages.append({"role": "user", "content": message})
        print("🔎 [GPT VIET] Bắt đầu xử lý:")
        print(f"🕒 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Người dùng: {session.get('username')}")
        print(f"📨 Tin nhắn mới: {message}")
        print(f"🧾 Tổng số messages gửi vào: {len(messages)}")
        print(f"📦 Đang gọi model: gpt-4o ...")
        print(f"🖼 Có ảnh không?: {'✅ Có' if image_url else '❌ Không'}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.4,
            max_tokens=2000,
            timeout=60,
              # bật chế độ trả lời từng phần
        )



        reply = response.choices[0].message.content.strip()

        banned_words = ["chatgpt", "gpt-4", "openai", "gpt"]
        for banned in banned_words:
            pattern = r"\b" + re.escape(banned) + r"\b"
            reply = re.sub(pattern, "trợ lý SolveViet", reply, flags=re.IGNORECASE)

        return reply

    except Exception as e:
        print("❌ Lỗi GPT Việt:", e)
        return "Quá tải hệ thống bạn hãy thử lại sau ít phút nhé. Hoặc bạn gửi từng nội dung ngắn lại nhé."
    
def call_gpt_lite(message, history=None, image_url=None):
    try:
        from flask import session
        from datetime import datetime

        # ⏰ Thời gian hiện tại
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 🧠 Debug đầu vào
        print("🔎 [GPT Lite] >>> Bắt đầu xử lý")
        print(f"🕓 Thời gian: {timestamp}")
        print(f"👤 Người dùng: {session.get('username')}")
        print(f"📨 Tin nhắn: {message}")
        print(f"🖼 Có ảnh không?: {'✅ Có' if image_url else '❌ Không'}")

        system_prompt = {
            "role": "system",
            "content": (
                "Bạn là AI phiên bản Lite của SolveViet – giúp học sinh trả lời nhanh gọn, đơn giản, dễ hiểu, phù hợp với nhu cầu học tập cơ bản.\n\n"
                "🎯 Hướng dẫn trả lời:\n"
                "- Với các câu hỏi thông thường, hãy trả lời đầy đủ ý, ngắn gọn, dễ hiểu, không lạc đề.\n"
                "- Nếu người dùng hỏi bài toán phức tạp hoặc nâng cao, bạn **có thể đưa ra kết quả** hoặc hướng giải sơ bộ, sau đó khuyến khích họ nâng cấp VIP để xem lời giải chi tiết.\n"
                "- Giữ thái độ thân thiện, tự nhiên, không lạnh nhạt.\n"
                "- Không viết dài lan man, không lý thuyết tràn lan.\n"
                "- Không dùng emoji, không tấu hài, không văn phong GenZ.\n\n"
                "📌 Ví dụ gợi ý:\n"
                "- Nếu người dùng hỏi toán nâng cao: 'Nghiệm là x = 2. Nếu bạn muốn xem toàn bộ lời giải chi tiết từng bước, bạn có thể nâng cấp gói VIP nhé!'\n"
                "- Nếu người dùng hỏi kiến thức đơn giản: trả lời trực tiếp, rõ ràng.\n"
                "- Nếu không hiểu rõ yêu cầu: 'Bạn có thể hỏi lại rõ hơn một chút được không?'"
            )
        }

        messages = [system_prompt]

        if history:
            for h in history:
                role = h.get("role", "user")
                content = h.get("content", "")
                if role in ["user", "assistant"] and content.strip():
                    messages.append({"role": role, "content": content.strip()})

        # 📸 Nếu có ảnh → gửi dạng multi-modal
        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            })
            model = "gpt-4o"
        else:
            messages.append({"role": "user", "content": message})
            model = "gpt-3.5-turbo"

        # 🔍 Debug model và số message
        print(f"⚙️ Model dùng: {model}")
        print(f"🧾 Tổng số messages gửi vào: {len(messages)}")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,
            max_tokens=800
        )

        reply = response.choices[0].message.content.strip()

        print("✅ Đã trả lời xong.")
        return reply

    except Exception as e:
        print("❌ Lỗi GPT LITE:", e)
        return "⚠️ Xin lỗi, mình chưa xử lý được yêu cầu này."
