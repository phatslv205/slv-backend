import json

import json

def rename_keys_in_users(file_path, changes):
    with open(file_path, "r", encoding="utf-8") as f:
        users = json.load(f)

    changed = False
    for username, user in users.items():
        for old_key, new_key in changes.items():
            if old_key in user:
                user[new_key] = user.pop(old_key)
                changed = True

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        print("✅ Đã đổi tất cả key thành công trong users.json")
    else:
        print("⚠️ Không có key nào cần đổi")

# Gọi hàm
rename_keys_in_users("users.json", {
    "vip_math_web": "vip_solver_edu",
    "vip_until_web": "vip_until_solver_edu"
})

def replace_in_file(filename, old_text, new_text):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    if old_text not in content:
        print(f"❌ Không thấy từ '{old_text}' trong {filename}")
        return

    content = content.replace(old_text, new_text)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Đã thay '{old_text}' thành '{new_text}' trong {filename}")

# Gọi hàm thay luôn trong app.py nếu muốn
replace_in_file("app.py", "vip_until_web", "vip_until_solver_edu")
replace_in_file("app.py", "vip_math_web", "vip_solver_edu")
