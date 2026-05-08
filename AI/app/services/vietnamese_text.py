from __future__ import annotations


COMMON_REPLACEMENTS = {
    "Next 30 days": "30 ngày",
    "Next 60 days": "60 ngày",
    "Next 90 days": "90 ngày",
    "next 30 days": "30 ngày",
    "next 60 days": "60 ngày",
    "next 90 days": "90 ngày",
    "30 ngày đầu:": "30 ngày:",
    "30 ngày đầu": "30 ngày",
    "Career Path Simulator": "Mô phỏng lộ trình nghề nghiệp",
    "career path simulator": "mô phỏng lộ trình nghề nghiệp",
    "mini project": "dự án nhỏ",
    "Mini project": "Dự án nhỏ",
    "case study": "bài phân tích tình huống",
    "Case study": "Bài phân tích tình huống",
    "portfolio": "hồ sơ dự án",
    "Portfolio": "Hồ sơ dự án",
    "matching": "đối sánh",
    "Matching": "Đối sánh",
    "apply": "ứng tuyển",
    "Apply": "Ứng tuyển",
    "cover letter": "thư xin việc",
    "Cover letter": "Thư xin việc",
    "job mục tiêu": "vị trí mục tiêu",
    "job phù hợp": "vị trí phù hợp",
    "job gần nhất": "vị trí gần nhất",
    "job ": "công việc ",
    "Job ": "Công việc ",
    "skill gap": "khoảng cách kỹ năng",
    "Skill gap": "Khoảng cách kỹ năng",
}

VOICE_REPLACEMENTS = {
    "Tôi đã phân tích": "Hệ thống đã phân tích",
    "Tôi xác định": "Hệ thống xác định",
    "Tôi khuyến nghị": "Khuyến nghị",
    "tôi đã phân tích": "hệ thống đã phân tích",
    "tôi xác định": "hệ thống xác định",
    "tôi khuyến nghị": "khuyến nghị",
    "của mình": "của ứng viên",
    "của tôi": "của ứng viên",
    "tôi có": "ứng viên có",
    "tôi sẽ": "ứng viên nên",
    "Tôi có": "Ứng viên có",
    "Tôi sẽ": "Ứng viên nên",
}


def normalize_vietnamese_terms(text: str) -> str:
    output = str(text or "")
    for source, target in COMMON_REPLACEMENTS.items():
        output = output.replace(source, target)
    return output


def normalize_vietnamese_voice(text: str) -> str:
    output = normalize_vietnamese_terms(text)
    for source, target in VOICE_REPLACEMENTS.items():
        output = output.replace(source, target)
    return output


def trim_incomplete_tail(text: str) -> str:
    if not text:
        return text

    lines = [line.rstrip() for line in text.splitlines()]
    while lines:
        last_line = lines[-1].strip()
        if not last_line:
            lines.pop()
            continue

        if (
            last_line.endswith((":", ",", ";", "-", "/", "("))
            or last_line.count("(") > last_line.count(")")
            or len(last_line) <= 4
        ):
            lines.pop()
            continue

        break

    return "\n".join(lines).strip()


def ensure_terminal_punctuation(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return cleaned

    if cleaned[-1] in ".!?":
        return cleaned

    last_stop = max(cleaned.rfind("."), cleaned.rfind("!"), cleaned.rfind("?"))
    if last_stop >= 0 and last_stop >= int(len(cleaned) * 0.6):
        return cleaned[: last_stop + 1].strip()

    return f"{cleaned}."


def normalize_vietnamese_ai_text(
    text: str,
    *,
    keep_blank_lines: bool = True,
    trim_tail: bool = True,
    ensure_punctuation: bool = False,
) -> str:
    cleaned = (
        str(text or "")
        .replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
        .strip()
    )

    normalized_lines: list[str] = []
    previous_blank = False
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            if keep_blank_lines and normalized_lines and not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue

        normalized_lines.append(line)
        previous_blank = False

    output = "\n".join(normalized_lines).strip()
    output = normalize_vietnamese_terms(output)

    if trim_tail:
        output = trim_incomplete_tail(output)

    if ensure_punctuation:
        output = ensure_terminal_punctuation(output)

    return output


def normalize_vietnamese_text_list(items: list[str] | None) -> list[str]:
    if not items:
        return []

    normalized: list[str] = []
    for item in items:
        value = normalize_vietnamese_ai_text(
            str(item or ""),
            keep_blank_lines=False,
            trim_tail=False,
            ensure_punctuation=False,
        )
        if value:
            normalized.append(value)

    return normalized
