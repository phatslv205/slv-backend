import re

def format_full_math_solution(text: str) -> str:
    """
    Trình bày lời giải theo phong cách GPT: chia khối, không markdown rối rắm,
    không viết nghiêng dính chữ, có emoji, khoảng cách hợp lý.
    """
    lines = text.strip().split('\n')
    result = []

    for i, line in enumerate(lines):
        line = line.strip()

        # Dòng là tiêu đề kiểu "Câu 1:", "Câu 2:"
        if re.match(r'^(Câu|Câu hỏi)\s*\d+', line, re.IGNORECASE):
            result.append(f"\n---\n\n🧠 {line}\n")

        # Dòng có toán học → hiển thị LaTeX block
        elif re.search(r'[=°→]', line):
            latex = line.replace("°", "^\\circ").replace("→", "\\rightarrow")
            result.append(f"\n\\[ {latex} \\]\n")

        # Dòng chứa đáp án
        elif "Đáp án" in line or "đáp số" in line or "đáp" in line.lower():
            result.append(f"\n✅ {line.strip()}\n")

        # Các dòng mô tả bình thường
        else:
            result.append(f"\n{line.strip()}\n")

    result.append("\n---\n🎉 Đã trình bày xong toàn bộ bài. Bạn cần giải thêm câu nào không?")
    return '\n'.join(result)
