from fastapi import APIRouter
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.schemas.common import BaseAiResponse
from app.schemas.matching import MatchingBatchRequest, MatchingRequest
from app.services.matcher import match_cv_jd
from app.core.config import settings


router = APIRouter()


@router.post("/match/cv-jd", response_model=BaseAiResponse)
def matching_endpoint(payload: MatchingRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **match_cv_jd(
            payload.ho_so_id,
            payload.tin_tuyen_dung_id,
            cv_profile=payload.cv_profile,
            jd_profile=payload.jd_profile,
            include_llm_explanation=payload.include_llm_explanation,
        )
    )


@router.post("/match/cv-jd/batch", response_model=BaseAiResponse)
def matching_batch_endpoint(payload: MatchingBatchRequest) -> BaseAiResponse:
    requests = list(payload.items)
    llm_explanations_left = max(0, settings.match_batch_llm_explanations)
    jobs = []

    for index, item in enumerate(requests):
        include_llm_explanation = item.include_llm_explanation and llm_explanations_left > 0
        if include_llm_explanation:
            llm_explanations_left -= 1

        jobs.append(
            (
                index,
                item.request_key if item.request_key is not None else str(index),
                item,
                include_llm_explanation,
            )
        )

    items_by_index = {}
    max_workers = min(6, max(1, len(jobs)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                match_cv_jd,
                item.ho_so_id,
                item.tin_tuyen_dung_id,
                cv_profile=item.cv_profile,
                jd_profile=item.jd_profile,
                include_llm_explanation=include_llm_explanation,
            ): (index, request_key)
            for index, request_key, item, include_llm_explanation in jobs
        }
        for future in as_completed(futures):
            index, request_key = futures[future]
            result = future.result()
            items_by_index[index] = {
                "request_key": request_key,
                **result,
            }

    items = [items_by_index[index] for index in sorted(items_by_index)]

    success_count = sum(1 for item in items if item.get("success") is True)

    return BaseAiResponse(
        success=success_count > 0 or not items,
        model_version=items[0].get("model_version") if items else None,
        data={
            "items": items,
            "total": len(items),
            "success_count": success_count,
        },
        error=None if success_count > 0 or not items else "Không có hồ sơ nào được matching thành công.",
    )
