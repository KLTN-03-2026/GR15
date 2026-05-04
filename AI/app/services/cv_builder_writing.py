from __future__ import annotations

from app.core.config import settings


MODEL_VERSION = f"cv_builder_writing_v1.0::rule_based::{settings.local_llm_model}"


def generate_cv_builder_writing(
    cv_profile: dict | None = None,
    section: str = "summary",
    options: dict | None = None,
) -> dict:
    profile = cv_profile or {}
    opts = options or {}
    item = opts.get("item") if isinstance(opts.get("item"), dict) else {}
    tone = str(opts.get("tone") or "professional")

    if section == "skills":
        data = {
            "section": section,
            "suggestions": [],
            "skill_suggestions": _suggest_skills(profile),
            "model_version": MODEL_VERSION,
        }
    else:
        data = {
            "section": section,
            "suggestions": _suggestions(profile, section, item, tone),
            "skill_suggestions": [],
            "model_version": MODEL_VERSION,
        }

    return {
        "success": True,
        "message": "Đã sinh gợi ý nội dung CV Builder.",
        "model_version": MODEL_VERSION,
        "data": data,
    }


def _suggestions(profile: dict, section: str, item: dict, tone: str) -> list[str]:
    if section == "career_goal":
        return _career_goals(profile, tone)
    if section == "experience":
        return _experience(profile, item, tone)
    if section == "project":
        return _project(profile, item, tone)
    return _summaries(profile, tone)


def _summaries(profile: dict, tone: str) -> list[str]:
    title = _target_title(profile)
    industry = _industry(profile)
    years = _years_label(profile)
    skills = _skill_text(profile)
    impact = (
        "tập trung vào kết quả đo được, chất lượng triển khai và khả năng phối hợp đa chức năng"
        if tone == "impact"
        else "có tư duy hệ thống, chủ động học hỏi và giao tiếp rõ ràng"
    )

    return [
        f"Ứng viên {title} {years}, định hướng phát triển trong lĩnh vực {industry}. Có thế mạnh về {skills}, {impact}; mong muốn đóng góp vào các sản phẩm/dự án có tác động thực tế.",
        f"{title} {years} với nền tảng {industry}, quen làm việc theo mục tiêu rõ ràng và ưu tiên hiệu quả vận hành. Nổi bật ở {skills}, khả năng phân tích vấn đề và chuyển yêu cầu thành kết quả cụ thể.",
        f"Ứng viên định hướng {title}, có kinh nghiệm xây dựng, tối ưu và phối hợp triển khai công việc trong môi trường {industry}. Phù hợp với vai trò cần sự chủ động, trách nhiệm và khả năng tạo giá trị ổn định.",
    ]


def _career_goals(profile: dict, tone: str) -> list[str]:
    title = _target_title(profile)
    industry = _industry(profile)
    skills = _skill_text(profile)
    growth = (
        "nhanh chóng hoàn thiện nền tảng chuyên môn, học từ dự án thực tế và phát triển thành nhân sự nòng cốt"
        if tone == "fresher"
        else "mở rộng phạm vi ảnh hưởng, nâng cao chất lượng đầu ra và đóng góp vào mục tiêu tăng trưởng của tổ chức"
    )

    return [
        f"Mục tiêu trở thành {title} có năng lực triển khai vững chắc trong lĩnh vực {industry}, tận dụng {skills} để giải quyết bài toán thực tế và tạo kết quả bền vững cho doanh nghiệp.",
        f"Tìm kiếm cơ hội ở vị trí {title}, nơi có thể {growth}. Ưu tiên môi trường đề cao dữ liệu, trách nhiệm cá nhân và tinh thần phối hợp liên phòng ban.",
        f"Trong 1-2 năm tới, tập trung phát triển chuyên sâu ở mảng {industry}, cải thiện năng lực {skills} và đảm nhận nhiều đầu việc có tác động trực tiếp đến hiệu quả sản phẩm/kinh doanh.",
    ]


def _experience(profile: dict, item: dict, tone: str) -> list[str]:
    position = _first([item.get("vi_tri"), _target_title(profile)])
    company = _first([item.get("cong_ty"), "đội nhóm/doanh nghiệp"])
    skills = _skill_text(profile)
    verb = "Dẫn dắt" if tone == "impact" else "Tham gia triển khai"

    return [
        f"{verb} các đầu việc tại {company} ở vai trò {position}, phối hợp với các bên liên quan để làm rõ yêu cầu, ưu tiên backlog và đảm bảo tiến độ bàn giao.\n- Ứng dụng {skills} để tối ưu quy trình, giảm lỗi lặp lại và cải thiện chất lượng đầu ra.\n- Theo dõi phản hồi/nghiệp vụ sau triển khai để đề xuất điều chỉnh phù hợp.",
        f"Phụ trách nhóm nhiệm vụ cốt lõi của vị trí {position}: phân tích yêu cầu, xây dựng giải pháp, kiểm tra kết quả và báo cáo tiến độ định kỳ.\n- Chủ động xử lý vấn đề phát sinh, phối hợp đa chức năng và ghi nhận bài học cải tiến.\n- Đóng góp vào việc chuẩn hóa tài liệu, quy trình hoặc tiêu chí nghiệm thu.",
        f"Thực hiện các công việc chuyên môn tại {company} với trọng tâm là chất lượng, khả năng mở rộng và trải nghiệm người dùng/nội bộ.\n- Kết hợp {skills} để giải quyết các điểm nghẽn trong vận hành.\n- Hỗ trợ đồng đội, chia sẻ kiến thức và duy trì nhịp làm việc ổn định.",
    ]


def _project(profile: dict, item: dict, tone: str) -> list[str]:
    name = _first([item.get("ten"), "dự án trọng điểm"])
    role = _first([item.get("vai_tro"), _target_title(profile)])
    tools = _first([item.get("linh_vuc_hoac_cong_cu"), _skill_text(profile)])
    result = (
        "giúp rút ngắn thời gian xử lý, tăng độ chính xác và cải thiện trải nghiệm sử dụng"
        if tone == "impact"
        else "giúp dự án vận hành rõ ràng hơn, dễ bảo trì và thuận tiện cho các bên liên quan"
    )

    return [
        f"Trong dự án {name}, đảm nhận vai trò {role}, tập trung làm rõ phạm vi, thiết kế hướng triển khai và phối hợp hoàn thiện các hạng mục chính. Sử dụng {tools} để bảo đảm chất lượng, tiến độ và khả năng mở rộng của giải pháp.",
        f"Tham gia {name} với trách nhiệm phân tích bối cảnh, triển khai phần việc được giao và kiểm thử kết quả trước khi bàn giao. Kết quả nổi bật: {result}.",
        f"Đóng góp vào {name} thông qua việc xây dựng luồng xử lý, chuẩn hóa tài liệu và phối hợp phản hồi sau demo/nghiệm thu. Vai trò {role} giúp kết nối yêu cầu nghiệp vụ với giải pháp thực tế.",
    ]


def _suggest_skills(profile: dict) -> list[dict]:
    title = _target_title(profile).lower()
    industry = _industry(profile).lower()
    skills = ["Giao tiếp", "Giải quyết vấn đề", "Làm việc nhóm", "Quản lý thời gian"]

    if "backend" in title or "công nghệ" in industry or "it" in industry:
        skills = ["Laravel", "REST API", "MySQL/PostgreSQL", "Git", "Kiểm thử API", "Tối ưu hiệu năng"]
    elif "frontend" in title:
        skills = ["Vue.js", "JavaScript", "HTML/CSS", "Responsive UI", "REST API Integration", "Git"]
    elif "product" in title:
        skills = ["Product Discovery", "User Story", "Roadmap Planning", "Stakeholder Management", "Agile/Scrum"]
    elif "marketing" in title:
        skills = ["Content Planning", "SEO", "Performance Marketing", "Google Analytics", "Social Media"]
    elif "hr" in title or "nhân sự" in industry:
        skills = ["Talent Acquisition", "Screening CV", "Interview Coordination", "Onboarding", "HR Communication"]

    existing = {skill.lower() for skill in _skill_names(profile)}
    return [{"ten": skill, "muc_do": "kha"} for skill in skills if skill.lower() not in existing][:8]


def _target_title(profile: dict) -> str:
    return _first([
        profile.get("vi_tri_ung_tuyen_muc_tieu"),
        profile.get("tieu_de_ho_so"),
        "nhân sự chuyên môn",
    ])


def _industry(profile: dict) -> str:
    return _first([profile.get("ten_nganh_nghe_muc_tieu"), "ngành nghề mục tiêu"])


def _years_label(profile: dict) -> str:
    try:
        years = float(profile.get("kinh_nghiem_nam") or 0)
    except (TypeError, ValueError):
        years = 0

    if years <= 0:
        return "có nền tảng thực hành và tinh thần học hỏi tốt"

    return f"có {years:g} năm kinh nghiệm"


def _skill_text(profile: dict) -> str:
    skills = _skill_names(profile)[:5]
    return ", ".join(skills) if skills else "kỹ năng chuyên môn liên quan"


def _skill_names(profile: dict) -> list[str]:
    items = profile.get("ky_nang_json") or []
    if not isinstance(items, list):
        return []

    names: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("ten") or item.get("name") or "").strip()
        if name and name.lower() not in {existing.lower() for existing in names}:
            names.append(name)
    return names


def _first(values: list[object]) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return " ".join(text.split())
    return ""
