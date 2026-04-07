from __future__ import annotations

from app.providers.base import CoverLetterContext


class TemplateCoverLetterProvider:
    def generate(self, context: CoverLetterContext) -> str:
        introduction = _build_introduction(context)
        summary = _build_professional_summary(context)
        strength_block = _build_strength_block(context)
        fit_block = _build_fit_block(context)
        closing = _build_closing(context)

        return "\n\n".join(
            part for part in [introduction, summary, strength_block, fit_block, closing] if part
        ).strip()


def _build_introduction(context: CoverLetterContext) -> str:
    greeting = f"Kính gửi {context.company_name},"

    if context.tone == "strong":
        sentence = (
            f"Tôi là {context.candidate_name} và xin gửi thư ứng tuyển cho vị trí {context.job_title}. "
            f"Với nền tảng kỹ năng và kinh nghiệm đã tích lũy, tôi tin rằng mình có thể đóng góp hiệu quả cho đội ngũ của {context.company_name}."
        )
    elif context.tone == "growth":
        sentence = (
            f"Tôi là {context.candidate_name} và mong muốn ứng tuyển vào vị trí {context.job_title}. "
            f"Dù vẫn còn một số điểm cần tiếp tục bồi dưỡng, tôi tin mình có nền tảng phù hợp và tinh thần học hỏi nhanh để thích nghi với công việc tại {context.company_name}."
        )
    else:
        sentence = (
            f"Tôi là {context.candidate_name} và xin ứng tuyển cho vị trí {context.job_title}. "
            f"Qua quá trình tìm hiểu mô tả công việc, tôi nhận thấy kinh nghiệm và bộ kỹ năng của mình có nhiều điểm phù hợp với nhu cầu tuyển dụng của {context.company_name}."
        )

    return f"{greeting}\n\n{sentence}"


def _build_professional_summary(context: CoverLetterContext) -> str:
    lines = [context.experience_summary]

    if context.matching_score is not None:
        lines.append(
            f"Dựa trên kết quả đối sánh hiện tại, mức độ phù hợp của tôi với vị trí này đạt khoảng {context.matching_score:.2f}/100."
        )

    lines.append(
        f"Tôi tin rằng mình có thể nhanh chóng bắt nhịp công việc và đóng góp giá trị thực tế cho vị trí {context.job_title}."
    )

    return " ".join(lines)


def _build_strength_block(context: CoverLetterContext) -> str:
    lines = ["Điểm mạnh liên quan của tôi:"]

    if context.featured_skills:
        lines.extend(f"- {skill}" for skill in context.featured_skills)
    else:
        lines.append("- Có nền tảng kỹ năng phù hợp với công việc")

    if context.job_focus_skills:
        lines.append("")
        lines.append("Những nội dung trọng tâm tôi đặc biệt quan tâm ở vị trí này:")
        lines.extend(f"- {skill}" for skill in context.job_focus_skills[:4])

    return "\n".join(lines)


def _build_fit_block(context: CoverLetterContext) -> str:
    lines = ["Mức độ phù hợp với vị trí:"]

    if context.matching_explanation:
        lines.append(f"- { _humanize_matching_explanation(context.matching_explanation) }")
    else:
        lines.append("- Hồ sơ hiện tại có nhiều điểm giao với yêu cầu của vị trí.")

    if context.missing_skills:
        lines.append("")
        lines.append("Những nội dung tôi đang tiếp tục hoàn thiện thêm:")
        lines.extend(f"- {skill}" for skill in context.missing_skills[:3])
        lines.append("")
        lines.append(
            "Tôi sẵn sàng tiếp tục học hỏi và hoàn thiện các kỹ năng còn thiếu để đáp ứng tốt hơn yêu cầu công việc."
        )
    else:
        lines.append("")
        lines.append("Tôi nhận thấy bộ kỹ năng hiện tại đã có nhiều điểm giao nhau với yêu cầu vị trí và sẵn sàng tiếp tục nâng cao trong quá trình làm việc.")

    return "\n".join(lines)


def _build_closing(context: CoverLetterContext) -> str:
    return (
        f"Tôi rất mong có cơ hội trao đổi thêm với {context.company_name} trong buổi phỏng vấn để trình bày rõ hơn về kinh nghiệm, kỹ năng và định hướng đóng góp của mình.\n\n"
        f"Trân trọng,\n{context.candidate_name}"
    )


def _humanize_matching_explanation(text: str) -> str:
    replacements = {
        "Muc do phu hop cao": "Mức độ phù hợp cao",
        "Muc do phu hop kha": "Mức độ phù hợp khá",
        "Muc do phu hop trung binh hoac thap": "Mức độ phù hợp trung bình hoặc thấp",
        "Ho so dang khop tot voi cac ky nang": "Hồ sơ đang khớp tốt với các kỹ năng",
        "Ky nang con thieu hoac can bo sung": "Kỹ năng còn thiếu hoặc cần bổ sung",
        "Diem kinh nghiem dat": "Điểm kinh nghiệm đạt",
        "diem hoc van dat": "điểm học vấn đạt",
        "va diem tuong dong noi dung CV-JD dat": "và điểm tương đồng nội dung CV-JD đạt",
        "Bo trong so duoc ap dung theo nhom cap bac": "Bộ trọng số được áp dụng theo nhóm cấp bậc",
        "He thong cung nhan dien cac ky nang gan nghia/gan vai tro": "Hệ thống cũng nhận diện các kỹ năng gần nghĩa/gần vai trò",
    }

    output = text
    for source, target in replacements.items():
        output = output.replace(source, target)
    return output
