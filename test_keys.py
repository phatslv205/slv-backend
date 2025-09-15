from openai import OpenAI
import os
from dotenv import load_dotenv
import httpx
import openai

load_dotenv()

GPT35_KEYS   = os.getenv("GPT35_KEYS", "").split(",")
GPT4O_KEYS   = os.getenv("GPT4O_KEYS", "").split(",")


def test_keys(model_name, keys, label=""):
    print(f"\n🧪 Đang test {len(keys)} key cho nhóm: {label} ({model_name})\n")
    for idx, key in enumerate(keys):
        short = key[:25]
        print(f"🔑 Key {idx+1:02d}: {short}... ", end="")

        try:
            client = OpenAI(
                api_key=key.strip(),
                http_client=httpx.Client(timeout=10)
            )
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": f"Ping {model_name}!"}]
            )
            print("✅ OK")
        except openai.AuthenticationError:
            print("❌ Authentication Error")
        except openai.APIConnectionError:
            print("❌ Connection Error")
        except openai.BadRequestError as e:
            print(f"❌ Bad Request ({e})")
        except Exception as e:
            print(f"❌ {type(e).__name__}: {e}")

# Chạy test cho 3 nhóm
test_keys("gpt-3.5-turbo", GPT35_KEYS, "GPT-3.5 1-1")
test_keys("gpt-4o", GPT4O_KEYS, "GPT-4o 1-1")

