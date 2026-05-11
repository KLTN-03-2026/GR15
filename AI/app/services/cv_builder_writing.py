from __future__ import annotations

import json
import re

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.gemini_client import generate_text
from app.providers.ollama_client import generate_text as generate_ollama_text
from app.services.llm_timeout import TimeoutError, run_with_timeout
from app.services.vietnamese_text import normalize_vietnamese_text_list


logger = get_logger(__name__)

MODEL_VERSION = f"cv_builder_writing_v1.1::{settings.cv_builder_writing_provider}"


def generate_cv_builder_writing(
    cv_profile: dict | None = None,
    section: str = "summary",
    options: dict | None = None,
) -> dict:
    profile = cv_profile or {}
    opts = options or {}
    item = opts.get("item") if isinstance(opts.get("item"), dict) else {}
    tone = str(opts.get("tone") or "professional")
    provider_name = _resolve_provider_name()

    try:
        data = run_with_timeout(
            lambda: _generate_with_llm(profile, section, item, tone, provider_name),
            settings.ai_llm_fallback_seconds,
        )
    except TimeoutError:
        logger.warning(
            "CV Builder writing LLM timed out provider=%s section=%s timeout_seconds=%s",
            provider_name,
            section,
            settings.ai_llm_fallback_seconds,
        )
        provider_name = "rule_timeout_fallback"
        data = _rule_based_payload(profile, section, item, tone)
    except Exception as exc:
        logger.exception("%s CV Builder writing failed.", provider_name)
        model = settings.gemini_model if provider_name == "gemini" else settings.ollama_model
        return {
            "success": False,
            "message": f"Không thể sinh gợi ý nội dung CV Builder bằng {provider_name}.",
            "model_version": f"cv_builder_writing_v1.1::{provider_name}::{model}",
            "data": {},
            "error": str(exc),
        }

    model = (
        "internal_rule_fallback"
        if provider_name == "rule_timeout_fallback"
        else settings.gemini_model if provider_name == "gemini" else settings.ollama_model
    )
    return {
        "success": True,
        "message": f"Đã sinh gợi ý nội dung CV Builder bằng {provider_name}.",
        "model_version": f"cv_builder_writing_v1.1::{provider_name}::{model}",
        "data": {
            **data,
            "model_version": f"cv_builder_writing_v1.1::{provider_name}::{model}",
            "meta": {
                "provider": provider_name,
                "model": model,
                "section": section,
                "tone": tone,
            },
        },
    }


def _rule_based_payload(profile: dict, section: str, item: dict, tone: str) -> dict:
    if section == "skills":
        return {
            "section": section,
            "suggestions": [],
            "skill_suggestions": _suggest_skills(profile),
        }

    return {
        "section": section,
        "suggestions": normalize_vietnamese_text_list(_suggestions(profile, section, item, tone)),
        "skill_suggestions": [],
    }


def _resolve_provider_name() -> str:
    provider = (settings.cv_builder_writing_provider or "ollama").strip().lower()
    if provider in {"", "llm", "ollama"}:
        return "ollama"
    if provider == "gemini":
        return "gemini"
    if provider in {"template", "rule", "rules", "rule_based", "local"}:
        logger.warning("CV_BUILDER_WRITING_PROVIDER=%s is non-LLM; forcing ollama.", settings.cv_builder_writing_provider)
        return "ollama"
    logger.warning("Unknown CV_BUILDER_WRITING_PROVIDER=%s, fallback to ollama", settings.cv_builder_writing_provider)
    return "ollama"


def _generate_with_llm(profile: dict, section: str, item: dict, tone: str, provider: str) -> dict:
    if provider == "gemini":
        raw = generate_text(
            system_prompt=(
                "Bạn là trợ lý viết CV cho hệ thống tuyển dụng. "
                "Luôn trả lời bằng tiếng Việt, không bịa công ty, chứng chỉ, số liệu hoặc kinh nghiệm ngoài dữ liệu đầu vào. "
                "Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm."
            ),
            user_prompt=_build_llm_prompt(profile, section, item, tone),
            max_tokens=settings.cv_builder_writing_max_tokens,
            temperature=0.25,
        )
        return _normalize_llm_payload(raw, section, profile)

    raw = generate_ollama_text(
        _build_llm_prompt(profile, section, item, tone),
        max_tokens=settings.cv_builder_writing_max_tokens,
        temperature=0.25,
        top_p=0.8,
        num_ctx=max(settings.ollama_num_ctx, 3072),
        error_context="Ollama local cho CV Builder Writing",
    )

    return _normalize_llm_payload(raw, section, profile)


def _normalize_llm_payload(raw: str, section: str, profile: dict) -> dict:
    payload = _parse_json_payload(raw)

    if section == "skills":
        skill_suggestions = _normalize_llm_skills(payload.get("skill_suggestions") or payload.get("skills") or [], profile)
        if not skill_suggestions:
            raise RuntimeError("Ollama không trả về skill_suggestions hợp lệ.")
        return {
            "section": section,
            "suggestions": [],
            "skill_suggestions": skill_suggestions,
        }

    suggestions = normalize_vietnamese_text_list(_normalize_llm_suggestions(payload.get("suggestions") or []))
    if not suggestions:
        raise RuntimeError("Ollama không trả về suggestions hợp lệ.")

    return {
        "section": section,
        "suggestions": suggestions[:3],
        "skill_suggestions": [],
    }


def _build_llm_prompt(profile: dict, section: str, item: dict, tone: str) -> str:
    schema = (
        '{"suggestions":["gợi ý 1","gợi ý 2","gợi ý 3"],"skill_suggestions":[]}'
        if section != "skills"
        else '{"suggestions":[],"skill_suggestions":[{"ten":"Tên kỹ năng","muc_do":"kha"}]}'
    )
    section_rules = {
        "summary": "Viết 3 phiên bản mô tả bản thân ngắn, chuyên nghiệp, 2-3 câu mỗi gợi ý.",
        "career_goal": "Viết 3 phiên bản mục tiêu nghề nghiệp, rõ định hướng và phù hợp vị trí mục tiêu.",
        "experience": "Viết 3 phiên bản mô tả kinh nghiệm cho item hiện tại. Có thể dùng xuống dòng bullet bằng ký tự '-'.",
        "project": "Viết 3 phiên bản mô tả dự án/thành tựu cho item hiện tại, nhấn mạnh vai trò, công nghệ/bối cảnh và kết quả hợp lý.",
        "skills": "Gợi ý tối đa 8 kỹ năng phù hợp với vị trí/ngành mục tiêu, bỏ qua kỹ năng đã có trong CV. muc_do chỉ dùng một trong: co_ban, kha, tot, xuat_sac.",
    }
    return (
        "Bạn là trợ lý viết CV cho hệ thống tuyển dụng. "
        "Luôn trả lời bằng tiếng Việt, không bịa công ty, chứng chỉ, số liệu hoặc kinh nghiệm ngoài dữ liệu đầu vào. "
        "Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm.\n"
        f"Section cần sinh: {section}\n"
        f"Tone: {tone}\n"
        f"Yêu cầu section: {section_rules.get(section, section_rules['summary'])}\n"
        "Quy tắc:\n"
        "- Bám sát dữ liệu CV, vị trí mục tiêu, kỹ năng hiện có và item đang chỉnh.\n"
        "- Không dùng câu chung chung quá mức, không tự thêm tên công ty/dự án/chứng chỉ nếu dữ liệu không có.\n"
        "- Không nhắc rằng bạn là AI.\n"
        "- Trả về đúng JSON theo schema, không đặt trong ```.\n"
        f"Schema bắt buộc: {schema}\n"
        f"Dữ liệu CV: {json.dumps(profile, ensure_ascii=False)}\n"
        f"Item đang chỉnh: {json.dumps(item, ensure_ascii=False)}"
    )


def _parse_json_payload(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise RuntimeError("LLM trả về JSON không phải object.")
    return payload


def _normalize_llm_suggestions(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    suggestions: list[str] = []
    for item in items[:5]:
        text = item.get("text") if isinstance(item, dict) else item
        text = str(text or "").strip()
        if text:
            suggestions.append(text)
    return suggestions


def _normalize_llm_skills(items: object, profile: dict) -> list[dict]:
    if not isinstance(items, list):
        return []
    existing = {skill.lower() for skill in _skill_names(profile)}
    skills: list[dict] = []
    seen: set[str] = set()
    for item in items[:12]:
        name = item.get("ten") or item.get("name") if isinstance(item, dict) else item
        level = item.get("muc_do") or item.get("level") if isinstance(item, dict) else "kha"
        name = str(name or "").strip()
        normalized_name = name.lower()
        if not name or normalized_name in existing or normalized_name in seen:
            continue
        seen.add(normalized_name)
        skills.append({
            "ten": name,
            "muc_do": level if level in {"co_ban", "kha", "tot", "xuat_sac"} else "kha",
        })
    return skills[:8]


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
