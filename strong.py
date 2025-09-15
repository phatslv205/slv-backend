import json
import unicodedata

def normalize(text):
    return unicodedata.normalize('NFC', text.strip().lower())

with open("viet_dictionary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = {}
for key, value in data.items():
    norm_key = normalize(key)
    nghia = value.get("nghĩa", "")
    vi_du = value.get("ví_dụ", "")
    
    if norm_key in normalize(nghia):
        nghia = nghia.replace(key, f"<strong>{key}</strong>")
    if norm_key in normalize(vi_du):
        vi_du = vi_du.replace(key, f"<strong>{key}</strong>")

    new_data[key] = {
        **value,
        "nghĩa": nghia,
        "ví_dụ": vi_du
    }

with open("viet_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)
