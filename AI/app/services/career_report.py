from __future__ import annotations

from collections import Counter
import json
from json import JSONDecodeError
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.core.logger import get_logger
from app.services.skill_catalog import SKILL_CATALOG, normalize_search_text


logger = get_logger(__name__)

MODEL_VERSION = f"career_report_v2::{settings.local_llm_model}"

CATEGORY_ROLE_MAP = {
    "ai_ml": ["AI Engineer", "Machine Learning Engineer", "NLP Engineer"],
    "backend_development": ["Backend Developer", "PHP Developer", "API Developer"],
    "business_analysis": ["Business Analyst", "Product Analyst", "System Analyst"],
    "frontend_development": ["Frontend Developer", "Web Developer", "UI Engineer"],
    "mobile_development": ["Mobile Developer", "iOS Developer", "Android Developer"],
    "qa_testing": ["QA Engineer", "Manual Tester", "Automation Tester"],
    "ui_ux_design": ["UI/UX Designer", "Product Designer", "UX Researcher"],
    "data_analysis": ["Data Analyst", "BI Analyst", "Reporting Analyst"],
    "database": ["Database Developer", "Data Engineer", "SQL Specialist"],
    "devops_cloud": ["DevOps Engineer", "Cloud Engineer", "Platform Engineer"],
    "digital_marketing": ["Chuyên viên Digital Marketing", "Performance Marketing", "Content Marketing Specialist"],
    "sales_business": ["Chuyên viên Kinh doanh", "Account Executive", "Business Development Executive"],
    "office_admin": ["Chuyên viên Hành chính - Văn phòng", "Office Administrator", "Operations Assistant"],
    "finance_accounting": ["Chuyên viên Kế toán - Tài chính", "Kế toán tổng hợp", "Financial Analyst"],
    "hr_recruitment": ["Chuyên viên Nhân sự - Tuyển dụng", "Talent Acquisition Executive", "HR Generalist"],
    "customer_support": ["Chuyên viên Chăm sóc khách hàng", "Customer Success Executive", "Call Center Specialist"],
    "logistics_supply_chain": ["Chuyên viên Logistics - Chuỗi cung ứng", "Supply Chain Executive", "Procurement Specialist"],
    "engineering_construction": ["Kỹ sư Xây dựng / Kỹ thuật", "Site Engineer", "Construction Coordinator"],
    "healthcare": ["Nhân sự Y tế", "Điều phối viên y tế", "Hỗ trợ lâm sàng"],
    "education_training": ["Chuyên viên Giáo dục - Đào tạo", "Giảng viên", "Training Specialist"],
    "hospitality_tourism": ["Chuyên viên Dịch vụ - Nhà hàng - Khách sạn", "Front Office Executive", "Hospitality Coordinator"],
    "erp_business_systems": ["Chuyên viên ERP / Hệ thống doanh nghiệp", "ERP Consultant", "Business System Specialist"],
    "project_management": ["Chuyên viên / Quản lý dự án", "Project Coordinator", "PMO Executive"],
    "soft_skills": ["Vị trí cần kỹ năng phối hợp và giao tiếp tốt"],
    "languages": ["Vị trí yêu cầu ngoại ngữ", "Biên phiên dịch", "Customer Support Song ngữ"],
}

ROLE_DISPLAY_MAP = {
    "AI Engineer": "AI Engineer (Kỹ sư AI)",
    "Machine Learning Engineer": "Machine Learning Engineer (Kỹ sư Machine Learning)",
    "NLP Engineer": "NLP Engineer (Kỹ sư Xử lý ngôn ngữ tự nhiên)",
    "Backend Developer": "Backend Developer (Lập trình viên Backend)",
    "Backend Developer Laravel": "Backend Developer Laravel (Lập trình viên Backend Laravel)",
    "PHP Developer": "PHP Developer (Lập trình viên PHP)",
    "API Developer": "API Developer (Lập trình viên API)",
    "Business Analyst": "Business Analyst (Chuyên viên Phân tích nghiệp vụ)",
    "Product Analyst": "Product Analyst (Chuyên viên Phân tích sản phẩm)",
    "System Analyst": "System Analyst (Chuyên viên Phân tích hệ thống)",
    "Frontend Developer": "Frontend Developer (Lập trình viên Frontend)",
    "Web Developer": "Web Developer (Lập trình viên Web)",
    "UI Engineer": "UI Engineer (Kỹ sư Giao diện người dùng)",
    "Mobile Developer": "Mobile Developer (Lập trình viên Mobile)",
    "iOS Developer": "iOS Developer (Lập trình viên iOS)",
    "Android Developer": "Android Developer (Lập trình viên Android)",
    "QA Engineer": "QA Engineer (Kỹ sư Đảm bảo chất lượng)",
    "Manual Tester": "Manual Tester (Chuyên viên Kiểm thử thủ công)",
    "Automation Tester": "Automation Tester (Chuyên viên Kiểm thử tự động)",
    "UI/UX Designer": "UI/UX Designer (Nhà thiết kế UI/UX)",
    "Product Designer": "Product Designer (Nhà thiết kế sản phẩm)",
    "UX Researcher": "UX Researcher (Chuyên viên Nghiên cứu trải nghiệm người dùng)",
    "Data Analyst": "Data Analyst (Chuyên viên Phân tích dữ liệu)",
    "BI Analyst": "BI Analyst (Chuyên viên Phân tích BI)",
    "Reporting Analyst": "Reporting Analyst (Chuyên viên Phân tích báo cáo)",
    "Database Developer": "Database Developer (Lập trình viên Cơ sở dữ liệu)",
    "Data Engineer": "Data Engineer (Kỹ sư Dữ liệu)",
    "SQL Specialist": "SQL Specialist (Chuyên viên SQL)",
    "DevOps Engineer": "DevOps Engineer (Kỹ sư DevOps)",
    "Cloud Engineer": "Cloud Engineer (Kỹ sư Cloud)",
    "Platform Engineer": "Platform Engineer (Kỹ sư Nền tảng)",
    "Chuyên viên Digital Marketing": "Digital Marketing Executive (Chuyên viên Digital Marketing)",
    "Performance Marketing": "Performance Marketing Specialist (Chuyên viên Performance Marketing)",
    "Content Marketing Specialist": "Content Marketing Specialist (Chuyên viên Content Marketing)",
    "Chuyên viên Kinh doanh": "Sales Executive (Chuyên viên Kinh doanh)",
    "Account Executive": "Account Executive (Chuyên viên Quản lý khách hàng)",
    "Business Development Executive": "Business Development Executive (Chuyên viên Phát triển kinh doanh)",
    "Chuyên viên Hành chính - Văn phòng": "Office Administration Executive (Chuyên viên Hành chính - Văn phòng)",
    "Office Administrator": "Office Administrator (Quản trị văn phòng)",
    "Operations Assistant": "Operations Assistant (Trợ lý Vận hành)",
    "Chuyên viên Kế toán - Tài chính": "Accounting & Finance Executive (Chuyên viên Kế toán - Tài chính)",
    "Kế toán tổng hợp": "General Accountant (Kế toán tổng hợp)",
    "Financial Analyst": "Financial Analyst (Chuyên viên Phân tích tài chính)",
    "Chuyên viên Nhân sự - Tuyển dụng": "HR & Recruitment Executive (Chuyên viên Nhân sự - Tuyển dụng)",
    "Talent Acquisition Executive": "Talent Acquisition Executive (Chuyên viên Thu hút nhân tài)",
    "HR Generalist": "HR Generalist (Chuyên viên Nhân sự tổng hợp)",
    "Chuyên viên Chăm sóc khách hàng": "Customer Service Executive (Chuyên viên Chăm sóc khách hàng)",
    "Customer Success Executive": "Customer Success Executive (Chuyên viên Thành công khách hàng)",
    "Call Center Specialist": "Call Center Specialist (Chuyên viên Tổng đài)",
    "Chuyên viên Logistics - Chuỗi cung ứng": "Logistics & Supply Chain Executive (Chuyên viên Logistics - Chuỗi cung ứng)",
    "Supply Chain Executive": "Supply Chain Executive (Chuyên viên Chuỗi cung ứng)",
    "Procurement Specialist": "Procurement Specialist (Chuyên viên Mua hàng)",
    "Kỹ sư Xây dựng / Kỹ thuật": "Engineering / Construction Engineer (Kỹ sư Xây dựng / Kỹ thuật)",
    "Site Engineer": "Site Engineer (Kỹ sư Công trường)",
    "Construction Coordinator": "Construction Coordinator (Điều phối Xây dựng)",
    "Nhân sự Y tế": "Healthcare Staff (Nhân sự Y tế)",
    "Điều phối viên y tế": "Healthcare Coordinator (Điều phối viên Y tế)",
    "Hỗ trợ lâm sàng": "Clinical Support (Hỗ trợ lâm sàng)",
    "Chuyên viên Giáo dục - Đào tạo": "Education & Training Executive (Chuyên viên Giáo dục - Đào tạo)",
    "Giảng viên": "Instructor / Lecturer (Giảng viên)",
    "Training Specialist": "Training Specialist (Chuyên viên Đào tạo)",
    "Chuyên viên Dịch vụ - Nhà hàng - Khách sạn": "Hospitality Service Executive (Chuyên viên Dịch vụ - Nhà hàng - Khách sạn)",
    "Front Office Executive": "Front Office Executive (Chuyên viên Lễ tân)",
    "Hospitality Coordinator": "Hospitality Coordinator (Điều phối Dịch vụ)",
    "Chuyên viên ERP / Hệ thống doanh nghiệp": "ERP / Business Systems Executive (Chuyên viên ERP / Hệ thống doanh nghiệp)",
    "ERP Consultant": "ERP Consultant (Chuyên viên tư vấn ERP)",
    "Business System Specialist": "Business System Specialist (Chuyên viên Hệ thống doanh nghiệp)",
    "Chuyên viên / Quản lý dự án": "Project Executive / Manager (Chuyên viên / Quản lý dự án)",
    "Project Coordinator": "Project Coordinator (Điều phối dự án)",
    "PMO Executive": "PMO Executive (Chuyên viên PMO)",
    "Vị trí cần kỹ năng phối hợp và giao tiếp tốt": "Collaborative Role (Vị trí cần kỹ năng phối hợp và giao tiếp tốt)",
    "Vị trí yêu cầu ngoại ngữ": "Bilingual Role (Vị trí yêu cầu ngoại ngữ)",
    "Biên phiên dịch": "Interpreter / Translator (Biên phiên dịch)",
    "Customer Support Song ngữ": "Bilingual Customer Support (Chăm sóc khách hàng song ngữ)",
}

CATEGORY_LABELS = {
    "ai_ml": "AI và học máy",
    "backend_development": "phát triển backend",
    "business_analysis": "phân tích nghiệp vụ",
    "frontend_development": "phát triển frontend",
    "mobile_development": "phát triển mobile",
    "qa_testing": "kiểm thử phần mềm",
    "ui_ux_design": "thiết kế UI/UX",
    "data_analysis": "phân tích dữ liệu",
    "database": "cơ sở dữ liệu",
    "devops_cloud": "DevOps và cloud",
    "digital_marketing": "digital marketing",
    "sales_business": "kinh doanh",
    "office_admin": "hành chính văn phòng",
    "finance_accounting": "kế toán tài chính",
    "hr_recruitment": "nhân sự và tuyển dụng",
    "customer_support": "chăm sóc khách hàng",
    "logistics_supply_chain": "logistics và chuỗi cung ứng",
    "engineering_construction": "kỹ thuật và xây dựng",
    "healthcare": "y tế",
    "education_training": "giáo dục và đào tạo",
    "hospitality_tourism": "dịch vụ và du lịch",
    "erp_business_systems": "ERP và hệ thống doanh nghiệp",
    "project_management": "quản lý dự án",
    "soft_skills": "kỹ năng mềm",
    "languages": "ngoại ngữ",
}

SKILL_CATEGORY_LOOKUP = {
    normalize_search_text(item["skill_name"]).strip(): item.get("category")
    for item in SKILL_CATALOG
}

DEFAULT_CATEGORY_GAPS = {
    "backend_development": ["Docker", "Thiết kế hệ thống", "Kiểm thử phần mềm"],
    "frontend_development": ["TypeScript", "Thiết kế giao diện", "Tối ưu hiệu năng frontend"],
    "mobile_development": ["SwiftUI", "Kiến trúc ứng dụng", "Tối ưu hiệu năng mobile"],
    "qa_testing": ["Automation Testing", "API Testing", "Kiểm thử hiệu năng"],
    "ui_ux_design": ["Figma", "Prototyping", "UX Research"],
    "data_analysis": ["Power BI", "Tableau", "Data Visualization"],
    "database": ["Tối ưu truy vấn SQL", "Thiết kế cơ sở dữ liệu", "Data Modeling"],
    "devops_cloud": ["CI/CD", "Kubernetes", "Cloud Infrastructure"],
    "digital_marketing": ["Google Analytics", "Performance Marketing", "Content Strategy"],
    "sales_business": ["CRM", "Negotiation", "Lead Generation"],
    "finance_accounting": ["Báo cáo tài chính", "Khai báo thuế", "Phân tích tài chính"],
    "hr_recruitment": ["Phỏng vấn tuyển dụng", "Talent Sourcing", "Quan hệ lao động"],
    "customer_support": ["Complaint Handling", "CRM", "Kỹ năng xử lý tình huống"],
    "logistics_supply_chain": ["Inventory Management", "Procurement", "Supply Chain Planning"],
    "engineering_construction": ["AutoCAD", "Dự toán", "Giám sát công trình"],
    "education_training": ["Lesson Planning", "LMS", "Đánh giá học tập"],
    "project_management": ["Lập kế hoạch dự án", "Risk Management", "Stakeholder Management"],
}

SUGGESTION_CANONICAL_MAP = {
    "system design": "Thiết kế hệ thống",
    "design system": "Thiết kế hệ thống",
    "software architecture": "Kiến trúc phần mềm",
    "cloud infrastructure": "Hạ tầng cloud",
    "cloud architecture": "Kiến trúc cloud",
    "cloud security": "Bảo mật cloud",
    "testing": "Kiểm thử phần mềm",
    "software testing": "Kiểm thử phần mềm",
    "api testing": "Kiểm thử API",
    "automation testing": "Kiểm thử tự động",
    "performance testing": "Kiểm thử hiệu năng",
    "data visualization": "Trực quan hóa dữ liệu",
    "ux research": "Nghiên cứu người dùng",
    "content strategy": "Chiến lược nội dung",
    "talent sourcing": "Tìm nguồn ứng viên",
    "lead generation": "Tìm kiếm khách hàng tiềm năng",
    "inventory management": "Quản lý tồn kho",
    "lesson planning": "Thiết kế bài giảng",
    "stakeholder management": "Quản trị stakeholder",
    "risk management": "Quản trị rủi ro",
    "project planning": "Lập kế hoạch dự án",
    "database design": "Thiết kế cơ sở dữ liệu",
    "data modeling": "Mô hình dữ liệu",
    "database optimization": "Tối ưu cơ sở dữ liệu",
    "sql optimization": "Tối ưu truy vấn SQL",
    "frontend performance optimization": "Tối ưu hiệu năng frontend",
    "mobile performance optimization": "Tối ưu hiệu năng mobile",
    "application architecture": "Kiến trúc ứng dụng",
}


def generate_career_report(
    ho_so_id: int,
    *,
    cv_profile: dict | None = None,
    matching_profiles: list[dict] | None = None,
) -> dict:
    logger.info("Generate career report for ho_so_id=%s", ho_so_id)

    try:
        cv_profile = cv_profile or {}
        matching_profiles = matching_profiles or []

        skill_names = _extract_skill_names(cv_profile.get("parsed_skills"))
        if not skill_names:
            skill_names = _extract_skill_names(cv_profile.get("builder_skills"))
        category_counter = _count_skill_categories(skill_names)
        top_matches = _normalize_matching_profiles(matching_profiles)

        candidate_level = _resolve_candidate_level(cv_profile)
        recommended_roles = _recommend_roles(category_counter, top_matches, candidate_level)
        nghe_de_xuat = recommended_roles[0] if recommended_roles else "Chưa xác định rõ vị trí phù hợp"
        muc_do_phu_hop = _calculate_fit_score(category_counter, top_matches)
        goi_y_ky_nang_bo_sung = _suggest_missing_skills(skill_names, top_matches, category_counter)
        reasoning_context = _build_reasoning_context(
            cv_profile=cv_profile,
            category_counter=category_counter,
            top_matches=top_matches,
            candidate_level=candidate_level,
            recommended_roles=recommended_roles,
            nghe_de_xuat=nghe_de_xuat,
            muc_do_phu_hop=muc_do_phu_hop,
            goi_y_ky_nang_bo_sung=goi_y_ky_nang_bo_sung,
        )
        report_outline = _build_report_outline(reasoning_context)
        template_report = _build_report_text(
            reasoning_context=reasoning_context,
            report_outline=report_outline,
        )

        try:
            llm_report = _generate_llm_report_text(reasoning_context, report_outline)
            if llm_report:
                bao_cao_chi_tiet = llm_report
            else:
                bao_cao_chi_tiet = template_report
        except Exception as exc:
            logger.warning("Career report LLM reasoning fallback to template: %s", exc)
            bao_cao_chi_tiet = template_report

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "nghe_de_xuat": nghe_de_xuat,
                "muc_do_phu_hop": muc_do_phu_hop,
                "goi_y_ky_nang_bo_sung": {
                    "skills": goi_y_ky_nang_bo_sung,
                    "recommended_roles": recommended_roles,
                    "candidate_level": candidate_level,
                    "top_matching_jobs": top_matches[:3],
                    "strength_categories": [
                        CATEGORY_LABELS.get(category, category)
                        for category, _ in category_counter.most_common(3)
                    ],
                },
                "bao_cao_chi_tiet": bao_cao_chi_tiet,
                "model_version": MODEL_VERSION,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("Career report generation failed for ho_so_id=%s", ho_so_id)
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {
                "nghe_de_xuat": "Chưa xác định",
                "muc_do_phu_hop": 0,
                "goi_y_ky_nang_bo_sung": {
                    "skills": [],
                    "recommended_roles": [],
                    "candidate_level": "unknown",
                    "top_matching_jobs": [],
                    "strength_categories": [],
                },
                "bao_cao_chi_tiet": None,
                "model_version": MODEL_VERSION,
            },
            "error": str(exc),
        }


def _extract_skill_names(items: list | None) -> list[str]:
    if not items:
        return []

    names = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("skill_name") or item.get("ten_ky_nang") or item.get("name")
        else:
            name = item

        if not name:
            continue

        value = str(name).strip()
        if value and value not in names:
            names.append(value)

    return names


def _count_skill_categories(skill_names: list[str]) -> Counter:
    counter: Counter = Counter()
    for skill_name in skill_names:
        category = SKILL_CATEGORY_LOOKUP.get(normalize_search_text(skill_name).strip())
        if category:
            counter[category] += 1
    return counter


def _normalize_matching_profiles(matching_profiles: list[dict]) -> list[dict]:
    normalized = []
    for item in matching_profiles:
        normalized.append(
            {
                "job_title": item.get("job_title") or item.get("tieu_de") or "Vị trí phù hợp",
                "score": float(item.get("diem_phu_hop") or 0),
                "missing_skills": _extract_skill_names(item.get("missing_skills_json")),
                "matched_skills": _extract_skill_names(item.get("matched_skills_json")),
                "job_level": (item.get("chi_tiet_diem") or {}).get("job_level"),
            }
        )

    normalized.sort(key=lambda item: item["score"], reverse=True)
    return normalized[:5]


def _recommend_roles(category_counter: Counter, top_matches: list[dict], candidate_level: str) -> list[str]:
    roles: list[str] = []

    for match in top_matches:
        title = _format_role_display(str(match["job_title"]).strip())
        if title and title not in roles:
            roles.append(title)

    for category, _count in category_counter.most_common(3):
        for role in CATEGORY_ROLE_MAP.get(category, []):
            leveled_role = _apply_level_prefix(role, candidate_level)
            leveled_role = _format_role_display(leveled_role)
            if leveled_role not in roles:
                roles.append(leveled_role)

    return roles[:5] or ["Chưa xác định rõ vị trí phù hợp"]


def _calculate_fit_score(category_counter: Counter, top_matches: list[dict]) -> float:
    if top_matches:
        top_scores = [item["score"] for item in top_matches[:3]]
        average_score = sum(top_scores) / len(top_scores)
    else:
        average_score = 45.0 if category_counter else 20.0

    category_bonus = min(sum(category_counter.values()) * 2.5, 12.0)
    return round(min(average_score + category_bonus, 100.0), 2)


def _suggest_missing_skills(existing_skills: list[str], top_matches: list[dict], category_counter: Counter) -> list[str]:
    existing_normalized = {normalize_search_text(skill).strip() for skill in existing_skills}
    suggestions = []
    suggestion_normalized = set()

    for match in top_matches:
        for skill in match["missing_skills"]:
            canonical_skill = _canonicalize_suggested_skill(skill)
            normalized = normalize_search_text(canonical_skill).strip()
            if normalized in existing_normalized:
                continue
            if normalized not in suggestion_normalized:
                suggestions.append(canonical_skill)
                suggestion_normalized.add(normalized)

    for category, _count in category_counter.most_common(2):
        for skill in DEFAULT_CATEGORY_GAPS.get(category, []):
            canonical_skill = _canonicalize_suggested_skill(skill)
            normalized = normalize_search_text(canonical_skill).strip()
            if normalized in existing_normalized:
                continue
            if normalized not in suggestion_normalized:
                suggestions.append(canonical_skill)
                suggestion_normalized.add(normalized)

    return suggestions[:6]


def _canonicalize_suggested_skill(skill: str) -> str:
    value = str(skill or "").strip()
    if not value:
        return value

    normalized = normalize_search_text(value).strip()
    return SUGGESTION_CANONICAL_MAP.get(normalized, value)


def _build_reasoning_context(
    *,
    cv_profile: dict,
    category_counter: Counter,
    top_matches: list[dict],
    candidate_level: str,
    recommended_roles: list[str],
    nghe_de_xuat: str,
    muc_do_phu_hop: float,
    goi_y_ky_nang_bo_sung: list[str],
) -> dict:
    ho_ten = cv_profile.get("parsed_name") or cv_profile.get("ho_ten") or "Ứng viên"
    skill_names = _extract_skill_names(cv_profile.get("parsed_skills")) or _extract_skill_names(cv_profile.get("builder_skills"))
    strength_categories = [
        {
            "category": category,
            "label": CATEGORY_LABELS.get(category, category),
            "evidence_count": count,
        }
        for category, count in category_counter.most_common(5)
    ]

    return {
        "candidate_profile": {
            "ho_ten": ho_ten,
            "tieu_de_ho_so": cv_profile.get("tieu_de_ho_so"),
            "vi_tri_ung_tuyen_muc_tieu": cv_profile.get("vi_tri_ung_tuyen_muc_tieu"),
            "ten_nganh_nghe_muc_tieu": cv_profile.get("ten_nganh_nghe_muc_tieu"),
            "muc_tieu_nghe_nghiep": cv_profile.get("muc_tieu_nghe_nghiep"),
            "mo_ta_ban_than": cv_profile.get("mo_ta_ban_than"),
            "trinh_do": cv_profile.get("trinh_do"),
            "kinh_nghiem_nam": cv_profile.get("kinh_nghiem_nam"),
            "candidate_level": candidate_level,
        },
        "skills": {
            "detected_skills": skill_names[:20],
            "strength_categories": strength_categories,
            "suggested_skill_gaps": goi_y_ky_nang_bo_sung,
        },
        "matching_evidence": {
            "top_matching_jobs": top_matches[:5],
            "average_top_match_score": round(sum(item["score"] for item in top_matches[:3]) / len(top_matches[:3]), 2) if top_matches[:3] else None,
        },
        "recommendation": {
            "primary_role": nghe_de_xuat,
            "fit_score": muc_do_phu_hop,
            "recommended_roles": recommended_roles,
            "method": "hybrid_rule_matching_evidence",
        },
    }


def _build_report_outline(reasoning_context: dict) -> dict:
    recommendation = reasoning_context["recommendation"]
    skills = reasoning_context["skills"]
    profile = reasoning_context["candidate_profile"]
    matches = reasoning_context["matching_evidence"].get("top_matching_jobs") or []
    candidate_level = profile.get("candidate_level") or "junior"

    career_paths = [
        {
            "role": role,
            "priority": index + 1,
            "rationale": _path_rationale(role, index, matches, skills.get("strength_categories") or []),
        }
        for index, role in enumerate((recommendation.get("recommended_roles") or [])[:3])
    ]

    return {
        "executive_summary": {
            "primary_role": recommendation.get("primary_role"),
            "fit_score": recommendation.get("fit_score"),
            "candidate_level": candidate_level,
            "confidence_basis": [
                "Kỹ năng đã parse từ CV",
                "Nhóm năng lực nổi bật theo skill catalog",
                "Top công việc đối sánh và kỹ năng còn thiếu",
            ],
        },
        "career_paths": career_paths,
        "skill_gap_analysis": {
            "current_strengths": [item["label"] for item in (skills.get("strength_categories") or [])[:4]],
            "priority_gaps": skills.get("suggested_skill_gaps") or [],
        },
        "development_roadmap": {
            "next_30_days": _roadmap_items(candidate_level, skills.get("suggested_skill_gaps") or [], 0),
            "next_60_days": _roadmap_items(candidate_level, skills.get("suggested_skill_gaps") or [], 1),
            "next_90_days": _roadmap_items(candidate_level, skills.get("suggested_skill_gaps") or [], 2),
        },
        "application_strategy": {
            "target_jobs": [
                {
                    "job_title": item.get("job_title"),
                    "score": item.get("score"),
                    "matched_skills": item.get("matched_skills") or [],
                    "missing_skills": item.get("missing_skills") or [],
                }
                for item in matches[:3]
            ],
            "portfolio_suggestions": _portfolio_suggestions(recommendation.get("primary_role"), skills.get("suggested_skill_gaps") or []),
        },
    }


def _build_report_text(*, reasoning_context: dict, report_outline: dict) -> str:
    profile = reasoning_context["candidate_profile"]
    recommendation = reasoning_context["recommendation"]
    skills = reasoning_context["skills"]
    matching = reasoning_context["matching_evidence"]
    ho_ten = profile.get("ho_ten") or "Ứng viên"
    muc_do_phu_hop = float(recommendation.get("fit_score") or 0)
    nghe_de_xuat = recommendation.get("primary_role") or "Chưa xác định rõ vị trí phù hợp"
    kinh_nghiem_nam = profile.get("kinh_nghiem_nam")

    intro = (
        f"Báo cáo định hướng nghề nghiệp cho {ho_ten}: hồ sơ hiện đạt mức phù hợp khoảng {muc_do_phu_hop:.2f}/100 "
        f"với hướng nghề đề xuất chính là {nghe_de_xuat}."
    )

    if isinstance(kinh_nghiem_nam, (int, float)):
        experience_line = f"Ứng viên hiện có khoảng {kinh_nghiem_nam:g} năm kinh nghiệm, được ước lượng ở cấp độ {profile.get('candidate_level')}."
    else:
        experience_line = f"Hồ sơ được ước lượng ở cấp độ {profile.get('candidate_level')} dựa trên tiêu đề, kỹ năng và dữ liệu CV đã parse."

    strengths = skills.get("strength_categories") or []
    if strengths:
        category_line = "Các nhóm năng lực nổi bật gồm: " + ", ".join(item["label"] for item in strengths[:3]) + "."
    else:
        category_line = "Hệ thống chưa nhận diện được nhóm năng lực nổi bật một cách thật rõ ràng."

    career_paths = report_outline.get("career_paths") or []
    if len(career_paths) > 1:
        role_block = "Các hướng nghề có thể cân nhắc:\n" + "\n".join(
            f"- {item['role']}: {item['rationale']}" for item in career_paths
        )
    else:
        role_block = "Hiện tại hồ sơ đang tập trung khá rõ vào một hướng nghề chính."

    top_matches = matching.get("top_matching_jobs") or []
    if top_matches:
        top_match_lines = ["Một số vị trí trong hệ thống đang có mức tương thích tốt:"]
        for match in top_matches[:3]:
            top_match_lines.append(f"- {match['job_title']} ({match['score']:.2f}/100)")
        top_match_block = "\n".join(top_match_lines)
    else:
        top_match_block = "Hiện chưa có đủ dữ liệu đối sánh để đối chiếu với nhiều vị trí đang tuyển."

    gaps = skills.get("suggested_skill_gaps") or []
    if gaps:
        skill_block = "Các kỹ năng nên ưu tiên bổ sung:\n" + "\n".join(f"- {skill}" for skill in gaps)
    else:
        skill_block = "Bộ kỹ năng hiện tại đã có nhiều điểm giao với các vị trí phù hợp; ứng viên nên tiếp tục đào sâu kỹ năng hiện có."

    roadmap = report_outline.get("development_roadmap") or {}
    development_plan = (
        "Lộ trình 30/60/90 ngày:\n"
        + "- 30 ngày: " + "; ".join(roadmap.get("next_30_days") or []) + "\n"
        + "- 60 ngày: " + "; ".join(roadmap.get("next_60_days") or []) + "\n"
        + "- 90 ngày: " + "; ".join(roadmap.get("next_90_days") or [])
    )

    closing = (
        "Khuyến nghị chung: nên dùng báo cáo này như một bản định hướng có căn cứ từ dữ liệu CV và kết quả đối sánh, "
        "đồng thời cập nhật CV sau mỗi giai đoạn học tập/dự án để hệ thống tái đánh giá chính xác hơn."
    )

    return "\n\n".join([
        intro,
        experience_line,
        category_line,
        role_block,
        top_match_block,
        skill_block,
        development_plan,
        closing,
    ])


def _path_rationale(role: str, index: int, matches: list[dict], strengths: list[dict]) -> str:
    if index == 0 and matches:
        return f"Đây là hướng ưu tiên vì có công việc đối sánh cao nhất và bám sát dữ liệu tuyển dụng hiện có ({matches[0].get('score', 0):.2f}/100)."
    if strengths:
        return "Hướng này phù hợp với nhóm năng lực nổi bật: " + ", ".join(item["label"] for item in strengths[:2]) + "."
    return "Hướng này nên được xem như lựa chọn tham khảo khi ứng viên bổ sung thêm dữ liệu kỹ năng và kinh nghiệm."


def _roadmap_items(candidate_level: str, gaps: list[str], stage: int) -> list[str]:
    primary_gap = gaps[0] if gaps else "kỹ năng trọng tâm của hướng nghề đề xuất"
    secondary_gap = gaps[1] if len(gaps) > 1 else primary_gap

    if stage == 0:
        return [
            f"Đánh giá lại CV và chuẩn hóa mô tả kinh nghiệm theo cấp độ {candidate_level}.",
            f"Học/củng cố nền tảng {primary_gap}.",
            "Chọn 2-3 JD mục tiêu để đối chiếu yêu cầu kỹ năng.",
        ]
    if stage == 1:
        return [
            f"Xây một dự án nhỏ hoặc bài phân tích tình huống thể hiện {primary_gap}.",
            f"Bổ sung kỹ năng {secondary_gap} vào hồ sơ dự án nếu phù hợp.",
            "Cập nhật CV bằng số liệu, phạm vi công việc và kết quả đạt được.",
        ]
    return [
        "Ứng tuyển thử vào nhóm vị trí có điểm đối sánh cao nhất.",
        "Luyện phỏng vấn theo các kỹ năng còn thiếu xuất hiện lặp lại trong JD.",
        "Đo lại mức đối sánh sau khi cập nhật CV để kiểm tra mức cải thiện.",
    ]


def _portfolio_suggestions(primary_role: str | None, gaps: list[str]) -> list[str]:
    role = primary_role or "hướng nghề mục tiêu"
    suggestions = [
        f"Xây một dự án nhỏ mô phỏng công việc thực tế của {role}.",
        "Viết tài liệu giới thiệu dự án thể hiện bối cảnh, cách triển khai, kết quả và bài học.",
    ]
    if gaps:
        suggestions.append("Ưu tiên đưa vào dự án các kỹ năng: " + ", ".join(gaps[:3]) + ".")
    return suggestions


def _generate_llm_report_text(reasoning_context: dict, report_outline: dict) -> str | None:
    provider = (settings.career_report_provider or "template").lower().strip()
    if provider in {"", "template", "rule", "rules"}:
        return None

    prompt = _build_llm_report_prompt(reasoning_context, report_outline)
    if provider == "openai":
        return _generate_openai_report(prompt)
    if provider == "ollama":
        return _generate_ollama_report(prompt)

    logger.warning("Unknown CAREER_REPORT_PROVIDER=%s, fallback to template", provider)
    return None


def _build_llm_report_prompt(reasoning_context: dict, report_outline: dict) -> str:
    return """
Viết Career Report bằng tiếng Việt, ngắn gọn, có căn cứ từ JSON.
Vai trò: hệ thống tư vấn nghề nghiệp đang đưa ra nhận định cho người dùng.

Quy tắc bắt buộc:
- KHÔNG viết tiêu đề "Báo cáo học thuật", "Mục lục", "Giới thiệu thông tin cá nhân", "Phân tích dữ liệu".
- KHÔNG đánh số bắt đầu từ 1 hoặc 2 cho các phần bị bỏ.
- Bắt đầu ngay bằng đúng dòng: Đề xuất ngành nghề chính
- Sau đó chỉ dùng các mục sau:
Đề xuất ngành nghề chính
Lý do đề xuất
Điểm mạnh và điểm cần cải thiện
Lộ trình 30/60/90 ngày
Chiến lược cập nhật CV và ứng tuyển
- Không dùng markdown đậm/nghiêng, không dùng ký tự # hoặc code block.
- Không dùng cụm tiếng Anh phổ thông trong nội dung tư vấn. Bắt buộc Việt hóa: "Next 30 days" thành "30 ngày đầu", "Next 60 days" thành "60 ngày", "Next 90 days" thành "90 ngày", "mini project" thành "dự án nhỏ", "case study" thành "bài phân tích tình huống", "portfolio" thành "hồ sơ dự án", "matching" thành "đối sánh", "job" thành "công việc/vị trí", "apply" thành "ứng tuyển".
- Chỉ giữ tiếng Anh khi đó là tên riêng công nghệ, tên vị trí gốc, viết tắt kỹ thuật hoặc tên framework như iOS, Swift, SwiftUI, Firebase, REST API, Docker.
- Không xưng "tôi", "mình" như thể AI là ứng viên. Khi nói về hồ sơ, dùng "ứng viên", "hồ sơ" hoặc "bạn".
- Không viết các câu như "Tôi đã phân tích", "Tôi xác định", "Tôi khuyến nghị".
- Mỗi mục 2-4 gạch đầu dòng ngắn, thực tế. Tổng độ dài khoảng 320-520 từ.
- Dùng cùng thứ tự mục, cùng phong cách câu, không thêm phần mới để câu trả lời ổn định giữa các lần sinh.
- Không bịa dữ liệu ngoài JSON; nếu thiếu dữ liệu thì nói ngắn gọn là dữ liệu còn hạn chế.

JSON:
""" + json.dumps(
        _compact_llm_evidence(reasoning_context, report_outline),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _compact_llm_evidence(reasoning_context: dict, report_outline: dict) -> dict:
    profile = reasoning_context.get("candidate_profile") or {}
    skills = reasoning_context.get("skills") or {}
    recommendation = reasoning_context.get("recommendation") or {}
    matching = reasoning_context.get("matching_evidence") or {}
    summary = report_outline.get("executive_summary") or {}
    skill_gap = report_outline.get("skill_gap_analysis") or {}
    roadmap = report_outline.get("development_roadmap") or {}
    strategy = report_outline.get("application_strategy") or {}

    return {
        "candidate": {
            "title": profile.get("tieu_de_ho_so"),
            "target_role": profile.get("vi_tri_ung_tuyen_muc_tieu"),
            "target_industry": profile.get("ten_nganh_nghe_muc_tieu"),
            "career_goal": profile.get("muc_tieu_nghe_nghiep"),
            "education": profile.get("trinh_do"),
            "years": profile.get("kinh_nghiem_nam"),
            "level": profile.get("candidate_level"),
        },
        "recommendation": {
            "primary_role": recommendation.get("primary_role") or summary.get("primary_role"),
            "fit_score": recommendation.get("fit_score") or summary.get("fit_score"),
            "alternative_roles": (recommendation.get("recommended_roles") or [])[1:3],
        },
        "evidence": {
            "detected_skills": (skills.get("detected_skills") or [])[:12],
            "strengths": (skill_gap.get("current_strengths") or [item.get("label") for item in skills.get("strength_categories", [])])[:5],
            "skill_gaps": (skill_gap.get("priority_gaps") or skills.get("suggested_skill_gaps") or [])[:6],
            "top_jobs": [
                {
                    "title": item.get("job_title"),
                    "score": item.get("score"),
                    "matched": (item.get("matched_skills") or [])[:4],
                    "missing": (item.get("missing_skills") or [])[:4],
                }
                for item in (matching.get("top_matching_jobs") or [])[:3]
            ],
        },
        "roadmap": roadmap,
        "portfolio": strategy.get("portfolio_suggestions") or [],
    }


def _generate_openai_report(prompt: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY để sinh Career Report bằng OpenAI.")

    payload = {
        "model": settings.openai_model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Bạn viết báo cáo hướng nghiệp ngắn gọn bằng tiếng Việt. "
                            "Chỉ bám sát evidence, không tự xưng 'tôi', không lan man, không thêm mục ngoài yêu cầu. "
                            "Giọng văn là hệ thống tư vấn nói với người dùng, dùng 'ứng viên', 'hồ sơ' hoặc 'bạn' khi cần. "
                            "Không dùng cụm tiếng Anh phổ thông trong phần tư vấn; chỉ giữ tên riêng công nghệ hoặc tên vị trí gốc."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
        "max_output_tokens": settings.career_report_max_tokens,
        "temperature": 0,
    }

    request = Request(
        settings.openai_base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(f"Không gọi được OpenAI API cho Career Report: {exc}") from exc

    data = json.loads(body)
    content = _extract_openai_response_text(data).strip()
    if not content:
        raise RuntimeError("OpenAI không trả về nội dung Career Report.")
    return _finalize_llm_report_text(content)


def _generate_ollama_report(prompt: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": settings.ollama_keep_alive,
        "options": {
            "temperature": 0,
            "top_p": 0.8,
            "num_predict": settings.career_report_max_tokens,
            "num_ctx": max(settings.ollama_num_ctx, 3072),
            "num_thread": settings.ollama_num_thread,
        },
    }
    request = Request(
        settings.ollama_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(f"Không gọi được Ollama local cho Career Report: {exc}") from exc

    try:
        data = json.loads(body)
    except JSONDecodeError as exc:
        raise RuntimeError("Ollama trả về dữ liệu Career Report không hợp lệ.") from exc

    if data.get("error"):
        raise RuntimeError(f"Ollama báo lỗi khi sinh Career Report: {data['error']}")

    content = (data.get("response") or "").strip()
    if not content:
        raise RuntimeError("Ollama không trả về nội dung Career Report.")
    return _finalize_llm_report_text(content)


def _extract_openai_response_text(payload: dict) -> str:
    output = payload.get("output") or []
    parts: list[str] = []
    for item in output:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(content["text"])
    if parts:
        return "\n".join(parts)
    return payload.get("output_text") or ""


def _sanitize_report_text(text: str) -> str:
    return (
        text.replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
        .strip()
    )


def _finalize_llm_report_text(text: str) -> str:
    cleaned = _sanitize_report_text(text)
    lowered = cleaned.lower()
    start_markers = [
        "đề xuất ngành nghề chính",
        "de xuat nganh nghe chinh",
        "đề xuất nghề chính",
        "de xuat nghe chinh",
    ]

    for marker in start_markers:
        index = lowered.find(marker)
        if index >= 0:
            cleaned = cleaned[index:].strip()
            break

    forbidden_prefixes = (
        "báo cáo học thuật",
        "bao cao hoc thuat",
        "mục lục",
        "muc luc",
        "1. giới thiệu",
        "1. gioi thieu",
        "2. phân tích",
        "2. phan tich",
    )
    lines = [
        line.strip()
        for line in cleaned.splitlines()
        if line.strip() and not line.strip().lower().startswith(forbidden_prefixes)
    ]
    cleaned = "\n\n".join(_normalize_report_voice(line) for line in lines)

    if not cleaned.lower().startswith("đề xuất"):
        cleaned = "Đề xuất ngành nghề chính\n\n" + cleaned

    return cleaned


def _normalize_report_voice(text: str) -> str:
    replacements = {
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
        "Next 30 days": "30 ngày đầu",
        "Next 60 days": "60 ngày",
        "Next 90 days": "90 ngày",
        "next 30 days": "30 ngày đầu",
        "next 60 days": "60 ngày",
        "next 90 days": "90 ngày",
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
        "job mục tiêu": "vị trí mục tiêu",
        "job phù hợp": "vị trí phù hợp",
        "job ": "công việc ",
        "Job ": "Công việc ",
        "skill gap": "khoảng cách kỹ năng",
        "Skill gap": "Khoảng cách kỹ năng",
    }
    output = text
    for source, target in replacements.items():
        output = output.replace(source, target)
    return output


def _resolve_candidate_level(cv_profile: dict) -> str:
    title = normalize_search_text(str(cv_profile.get("tieu_de_ho_so") or ""))
    years = cv_profile.get("kinh_nghiem_nam")

    if any(keyword in title for keyword in {"intern", "thuc tap"}):
        return "intern"
    if any(keyword in title for keyword in {"fresher", "moi tot nghiep"}):
        return "fresher"
    if any(keyword in title for keyword in {"junior"}):
        return "junior"
    if any(keyword in title for keyword in {"senior", "lead", "manager"}):
        return "senior"

    if isinstance(years, (int, float)):
        if years < 1:
            return "intern"
        if years <= 1:
            return "fresher"
        if years <= 2:
            return "junior"
        if years <= 4:
            return "mid"
        return "senior"

    return "junior"


def _apply_level_prefix(role: str, candidate_level: str) -> str:
    if candidate_level in {"intern", "fresher"} and "intern" not in normalize_search_text(role):
        return f"Junior {role}" if not role.lower().startswith(("junior", "intern", "fresher")) else role
    if candidate_level == "senior" and not role.lower().startswith(("senior", "lead", "manager")):
        return f"Senior {role}"
    return role


def _format_role_display(role: str) -> str:
    value = str(role or "").strip()
    if not value:
        return value

    direct = ROLE_DISPLAY_MAP.get(value)
    if direct:
        return direct

    if value.startswith("Junior "):
        base = value.removeprefix("Junior ").strip()
        mapped = ROLE_DISPLAY_MAP.get(base)
        if mapped:
            return f"Junior {mapped}"

    if value.startswith("Senior "):
        base = value.removeprefix("Senior ").strip()
        mapped = ROLE_DISPLAY_MAP.get(base)
        if mapped:
            return f"Senior {mapped}"

    return value


def _build_development_plan(candidate_level: str, suggested_skills: list[str]) -> str:
    if candidate_level in {"intern", "fresher"}:
        prefix = "Lộ trình phát triển gần hạn nên tập trung vào việc củng cố nền tảng và tăng trải nghiệm thực tế."
    elif candidate_level == "junior":
        prefix = "Lộ trình phát triển gần hạn nên tập trung vào việc mở rộng chiều sâu chuyên môn và khả năng làm việc độc lập."
    elif candidate_level == "mid":
        prefix = "Lộ trình phát triển gần hạn nên tập trung vào việc nâng cao năng lực thiết kế giải pháp và phối hợp dự án."
    else:
        prefix = "Lộ trình phát triển gần hạn nên tập trung vào việc mở rộng phạm vi ảnh hưởng, dẫn dắt kỹ thuật và tối ưu chất lượng triển khai."

    if suggested_skills:
        suffix = " Các kỹ năng ưu tiên trong giai đoạn tiếp theo gồm: " + ", ".join(suggested_skills[:4]) + "."
    else:
        suffix = " Ứng viên nên tiếp tục đào sâu các kỹ năng hiện có để tăng tính cạnh tranh cho hồ sơ."

    return prefix + suffix
