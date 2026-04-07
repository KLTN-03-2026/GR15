from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
import math
import re
from typing import Iterable

from app.core.config import settings
from app.core.logger import get_logger
from app.services.skill_catalog import SKILL_CATALOG, normalize_search_text

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    faiss = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


logger = get_logger(__name__)

_EMBEDDING_MODEL = None
_HASH_DIMENSION = 256
_CANDIDATE_MULTIPLIER = 3

GENERIC_QUERY_TOKENS = {
    "developer",
    "dev",
    "engineer",
    "specialist",
    "staff",
    "executive",
    "officer",
    "nhanvien",
    "nhan",
    "vien",
    "chuyenvien",
    "chuyen",
    "vi",
    "tri",
}

DOMAIN_SIGNAL_MAP = {
    "mobile_development": {"ios", "swift", "swiftui", "uikit", "android", "kotlin", "mobile", "xcode", "firebase"},
    "backend_development": {"backend", "php", "laravel", "api", "rest", "spring", "node", "golang"},
    "frontend_development": {"frontend", "react", "vue", "angular", "javascript", "typescript"},
    "qa_testing": {"qa", "test", "testing", "selenium", "automation", "postman"},
    "digital_marketing": {"marketing", "seo", "ads", "content", "facebook", "googleads"},
    "finance_accounting": {"accounting", "accountant", "tax", "finance", "kiemtoan", "thue"},
    "data_analysis": {"data", "analytics", "tableau", "powerbi", "sql", "bi"},
}

SKILL_ALIAS_LOOKUP = {
    normalize_search_text(item["skill_name"]).strip(): item.get("category")
    for item in SKILL_CATALOG
}


@dataclass
class SearchDocument:
    entity_id: int
    title: str
    text_content: str
    company_name: str | None = None
    location: str | None = None
    level: str | None = None
    metadata: dict | None = None


def semantic_search_jobs(query: str, documents: list[dict], top_k: int = 10) -> dict:
    logger.info("Semantic search with %s documents, top_k=%s", len(documents), top_k)

    normalized_query = query.strip()
    parsed_documents = [SearchDocument(**item) for item in documents if item.get("text_content")]
    if not normalized_query:
        return _error_response("Từ khóa tìm kiếm semantic không được để trống.")

    if not parsed_documents:
        return {
            "success": True,
            "model_version": _model_version("empty"),
            "data": {
                "query": normalized_query,
                "search_engine": "empty",
                "no_relevant_results": True,
                "message": "Hiện chưa có dữ liệu tin tuyển dụng để thực hiện semantic search.",
                "results": [],
                "document_embeddings": [],
                "total_documents": 0,
            },
            "error": None,
        }

    backend = _resolve_backend()
    query_profile = _analyze_query(normalized_query)
    query_vector, document_vectors = _embed_documents(normalized_query, parsed_documents, backend)
    ranked_results = _rank_documents(
        query_vector,
        document_vectors,
        parsed_documents,
        top_k,
        backend,
        normalized_query,
        query_profile,
    )

    return {
        "success": True,
        "model_version": _model_version(backend),
        "data": {
            "query": normalized_query,
            "search_engine": backend,
            "query_profile": query_profile,
            "no_relevant_results": len(ranked_results) == 0,
            "message": None if ranked_results else "Hiện chưa tìm thấy tin tuyển dụng đủ phù hợp với truy vấn này.",
            "results": ranked_results,
            "document_embeddings": [
                {
                    "entity_type": "tin_tuyen_dung",
                    "entity_id": document.entity_id,
                    "chunk_index": 0,
                    "text_content": document.text_content,
                    "embedding_vector": vector,
                    "model_name": _model_version(backend),
                    "metadata_json": document.metadata or {},
                }
                for document, vector in zip(parsed_documents, document_vectors, strict=False)
            ],
            "total_documents": len(parsed_documents),
        },
        "error": None,
    }


def _resolve_backend() -> str:
    if SentenceTransformer is not None and faiss is not None:
        return "sentence_transformers_faiss_hybrid_rerank_v3"
    return "hashed_vector_hybrid_rerank_v3"


def _model_version(backend: str) -> str:
    if backend == "sentence_transformers_faiss_hybrid_rerank_v3":
        return f"semantic_search_v3::{settings.semantic_embedding_model}"
    return "semantic_search_v3::hashed_fallback"


def _get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        logger.info("Loading semantic embedding model: %s", settings.semantic_embedding_model)
        _EMBEDDING_MODEL = SentenceTransformer(settings.semantic_embedding_model)
    return _EMBEDDING_MODEL


def _embed_documents(query: str, documents: list[SearchDocument], backend: str) -> tuple[list[float], list[list[float]]]:
    corpus = [query] + [document.text_content for document in documents]
    if backend == "sentence_transformers_faiss_hybrid_rerank_v3":
        model = _get_embedding_model()
        vectors = model.encode(corpus, normalize_embeddings=True).tolist()
        return vectors[0], vectors[1:]

    vectors = [_hashed_embedding(text) for text in corpus]
    return vectors[0], vectors[1:]


def _rank_documents(
    query_vector: list[float],
    document_vectors: list[list[float]],
    documents: list[SearchDocument],
    top_k: int,
    backend: str,
    query_text: str | None = None,
    query_profile: dict | None = None,
) -> list[dict]:
    candidate_size = min(max(top_k * _CANDIDATE_MULTIPLIER, 10), len(documents))

    if backend == "sentence_transformers_faiss_hybrid_rerank_v3" and faiss is not None:
        index = faiss.IndexFlatIP(len(query_vector))
        import numpy as np  # pragma: no cover

        document_matrix = np.array(document_vectors, dtype="float32")
        query_matrix = np.array([query_vector], dtype="float32")
        index.add(document_matrix)
        scores, indices = index.search(query_matrix, candidate_size)

        candidates = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0:
                continue
            document = documents[int(idx)]
            candidates.append((document, float(score), document_vectors[int(idx)]))
        return _rerank_candidates(candidates, query_text or "", top_k, query_profile or {})

    scored = []
    for document, vector in zip(documents, document_vectors, strict=False):
        score = _cosine_similarity(query_vector, vector)
        score = min(score + (_keyword_overlap_ratio(query_text or "", document.text_content) * 0.35), 1.0)
        scored.append((document, score, vector))

    scored.sort(key=lambda item: item[1], reverse=True)
    return _rerank_candidates(scored[:candidate_size], query_text or "", top_k, query_profile or {})


def _build_result(document: SearchDocument, scoring: dict, query_text: str) -> dict:
    normalized_score = round(scoring["final_score"], 2)
    overlap = _shared_keywords(query_text, document.text_content)

    return {
        "entity_id": document.entity_id,
        "title": document.title,
        "company_name": document.company_name,
        "location": document.location,
        "level": document.level,
        "semantic_score": round(scoring["semantic_score"], 2),
        "keyword_score": round(scoring["keyword_score"], 2),
        "skill_score": round(scoring["skill_score"], 2),
        "category_score": round(scoring["category_score"], 2),
        "title_score": round(scoring["title_score"], 2),
        "final_score": normalized_score,
        "semantic_reason": _build_reason(normalized_score, overlap, scoring),
        "matched_keywords": overlap[:6],
        "metadata": document.metadata or {},
    }


def _build_reason(score: float, overlap: list[str], scoring: dict) -> str:
    if score >= 80:
        prefix = "Mức độ phù hợp tổng thể rất cao với nhu cầu tìm kiếm."
    elif score >= 60:
        prefix = "Mức độ phù hợp tổng thể khá tốt với nhu cầu tìm kiếm."
    elif score >= 40:
        prefix = "Có mức độ liên quan tương đối với nhu cầu tìm kiếm."
    else:
        prefix = "Mức độ liên quan còn thấp, nhưng vẫn có một số điểm giao cơ bản."

    signals = []
    if scoring["skill_score"] >= 70:
        signals.append("khớp tốt về kỹ năng")
    if scoring["category_score"] >= 70:
        signals.append("đúng nhóm nghề")
    if scoring["title_score"] >= 70:
        signals.append("tiêu đề vị trí khá sát")
    if scoring["keyword_score"] >= 60:
        signals.append("trùng nhiều từ khóa quan trọng")

    if overlap:
        detail = " Một số từ khóa/cụm nội dung gần liên quan gồm: " + ", ".join(overlap[:5]) + "."
    else:
        detail = ""

    if signals:
        return prefix + " Hệ thống đánh giá cao vì " + ", ".join(signals[:3]) + "." + detail

    return prefix + detail


def _rerank_candidates(candidates: list[tuple[SearchDocument, float, list[float]]], query_text: str, top_k: int, query_profile: dict) -> list[dict]:
    reranked = []
    for document, raw_semantic, _vector in candidates:
        scoring = _compute_hybrid_scores(document, raw_semantic, query_text, query_profile)
        if not _passes_relevance_gate(document, scoring, query_profile, query_text):
            continue
        reranked.append((scoring["final_score"], document, scoring))

    reranked.sort(key=lambda item: item[0], reverse=True)
    return [
        _build_result(document, scoring, query_text)
        for _score, document, scoring in reranked[:top_k]
    ]


def _compute_hybrid_scores(document: SearchDocument, raw_semantic: float, query_text: str, query_profile: dict) -> dict:
    semantic_score = max(min(raw_semantic, 1.0), 0.0) * 100
    keyword_score = _keyword_overlap_ratio(query_text, document.text_content) * 100
    skill_score = _skill_overlap_score(query_profile, document)
    category_score = _category_match_score(query_profile, document)
    title_score = _title_match_score(query_text, document.title, query_profile)

    final_score = (
        semantic_score * 0.45
        + keyword_score * 0.20
        + skill_score * 0.20
        + category_score * 0.10
        + title_score * 0.05
    )

    return {
        "semantic_score": semantic_score,
        "keyword_score": keyword_score,
        "skill_score": skill_score,
        "category_score": category_score,
        "title_score": title_score,
        "final_score": final_score,
    }


def _analyze_query(query_text: str) -> dict:
    tokens = list(_tokenize(query_text))
    query_skills = []
    query_categories = []

    normalized_query = normalize_search_text(query_text)
    for item in SKILL_CATALOG:
        matched = False
        for alias in item["aliases"]:
            alias_search = normalize_search_text(alias)
            pattern = r"(?<!\w)" + re.escape(alias_search) + r"(?!\w)"
            if re.search(pattern, normalized_query):
                matched = True
                break
        if matched:
            skill_name = item["skill_name"]
            category = item.get("category")
            if skill_name not in query_skills:
                query_skills.append(skill_name)
            if category and category not in query_categories:
                query_categories.append(category)

    inferred = _infer_categories_from_tokens(tokens)
    for category in inferred:
        if category not in query_categories:
            query_categories.append(category)

    domain_signals = {
        category: sorted(token_set.intersection(signal_tokens))
        for category, signal_tokens in DOMAIN_SIGNAL_MAP.items()
        if (token_set := set(tokens)).intersection(signal_tokens)
    }

    return {
        "tokens": tokens,
        "skills": query_skills,
        "categories": query_categories,
        "domain_signals": domain_signals,
        "has_strong_domain_signal": bool(domain_signals),
    }


def _infer_categories_from_tokens(tokens: list[str]) -> list[str]:
    token_set = set(tokens)
    categories = []

    if token_set.intersection({"backend", "php", "api", "laravel", "spring", "node", "golang"}):
        categories.append("backend_development")
    if token_set.intersection({"frontend", "react", "vue", "angular", "javascript", "typescript"}):
        categories.append("frontend_development")
    if token_set.intersection({"ios", "android", "swift", "kotlin", "mobile"}):
        categories.append("mobile_development")
    if token_set.intersection({"qa", "test", "testing", "automation", "selenium"}):
        categories.append("qa_testing")
    if token_set.intersection({"marketing", "seo", "ads", "content"}):
        categories.append("digital_marketing")
    if token_set.intersection({"sql", "database", "mysql", "postgres"}):
        categories.append("database")
    if token_set.intersection({"data", "bi", "analytics", "tableau", "powerbi"}):
        categories.append("data_analysis")
    if token_set.intersection({"cloud", "devops", "docker", "kubernetes", "aws"}):
        categories.append("devops_cloud")

    return categories


def _skill_overlap_score(query_profile: dict, document: SearchDocument) -> float:
    query_skills = {
        normalize_search_text(skill).strip()
        for skill in query_profile.get("skills", [])
        if skill
    }
    if not query_skills:
        return 0.0

    document_skills = {
        normalize_search_text(str(skill)).strip()
        for skill in ((document.metadata or {}).get("skills") or [])
        if skill
    }
    if not document_skills:
        return 0.0

    overlap = query_skills.intersection(document_skills)
    if overlap:
        return (len(overlap) / len(query_skills)) * 100

    # Near-match through category if no exact query skill overlap
    query_categories = set(query_profile.get("categories", []))
    if not query_categories:
        return 0.0

    document_categories = {
        SKILL_ALIAS_LOOKUP.get(skill_name)
        for skill_name in document_skills
        if SKILL_ALIAS_LOOKUP.get(skill_name)
    }
    category_overlap = query_categories.intersection(document_categories)
    if category_overlap:
        return min(45.0 + len(category_overlap) * 15.0, 75.0)

    return 0.0


def _category_match_score(query_profile: dict, document: SearchDocument) -> float:
    query_categories = set(query_profile.get("categories", []))
    if not query_categories:
        return 0.0

    document_skills = {
        normalize_search_text(str(skill)).strip()
        for skill in ((document.metadata or {}).get("skills") or [])
        if skill
    }
    document_categories = {
        SKILL_ALIAS_LOOKUP.get(skill_name)
        for skill_name in document_skills
        if SKILL_ALIAS_LOOKUP.get(skill_name)
    }

    if not document_categories:
        return 0.0

    overlap = query_categories.intersection(document_categories)
    if not overlap:
        return 0.0

    return min((len(overlap) / len(query_categories)) * 100, 100.0)


def _title_match_score(query_text: str, document_title: str, query_profile: dict) -> float:
    query_tokens = set(_tokenize(query_text))
    if not query_tokens:
        return 0.0

    title_tokens = set(_tokenize(document_title))
    overlap = query_tokens.intersection(title_tokens)
    score = (len(overlap) / len(query_tokens)) * 100 if overlap else 0.0

    title_categories = _infer_categories_from_tokens(list(title_tokens))
    if set(query_profile.get("categories", [])).intersection(title_categories):
        score = max(score, 65.0)

    return min(score, 100.0)


def _shared_keywords(query_text: str, document_text: str) -> list[str]:
    query_tokens = set(_tokenize(query_text))
    document_tokens = _tokenize(document_text)
    shared = []
    for token in document_tokens:
        if token in query_tokens and token not in shared:
            shared.append(token)
    return shared[:12]


def _keyword_overlap_ratio(query_text: str, document_text: str) -> float:
    query_tokens = _tokenize(query_text)
    if not query_tokens:
        return 0.0

    document_tokens = set(_tokenize(document_text))
    total_weight = 0.0
    matched_weight = 0.0
    for token in query_tokens:
        weight = _token_weight(token)
        total_weight += weight
        if token in document_tokens:
            matched_weight += weight

    if total_weight == 0:
        return 0.0

    return matched_weight / total_weight


def _hashed_embedding(text: str, dimension: int = _HASH_DIMENSION) -> list[float]:
    vector = [0.0] * dimension
    for token in _tokenize(text):
        bucket = int(md5(token.encode("utf-8")).hexdigest(), 16) % dimension
        vector[bucket] += 1.0
    return _normalize_vector(vector)


def _tokenize(text: str) -> Iterable[str]:
    normalized = normalize_search_text(text)
    tokens = [re.sub(r"[^a-z0-9#+./-]", "", token.strip()) for token in normalized.split()]
    tokens = [token for token in tokens if len(token) >= 2]
    return tokens


def _token_weight(token: str) -> float:
    return 0.25 if token in GENERIC_QUERY_TOKENS else 1.0


def _document_category_set(document: SearchDocument) -> set[str]:
    document_skills = {
        normalize_search_text(str(skill)).strip()
        for skill in ((document.metadata or {}).get("skills") or [])
        if skill
    }
    document_categories = {
        SKILL_ALIAS_LOOKUP.get(skill_name)
        for skill_name in document_skills
        if SKILL_ALIAS_LOOKUP.get(skill_name)
    }
    document_categories.update(_infer_categories_from_tokens(list(_tokenize(document.title))))
    document_categories.discard(None)
    return set(document_categories)


def _passes_relevance_gate(document: SearchDocument, scoring: dict, query_profile: dict, query_text: str) -> bool:
    if scoring["final_score"] < 18:
        return False

    if (
        scoring["final_score"] < 35
        and scoring["skill_score"] <= 0
        and scoring["category_score"] <= 0
    ):
        return False

    if query_profile.get("has_strong_domain_signal"):
        query_categories = set(query_profile.get("categories", []))
        document_categories = _document_category_set(document)
        if query_categories and not query_categories.intersection(document_categories):
            return False

        weighted_keyword = _keyword_overlap_ratio(query_text, document.text_content) * 100
        if scoring["skill_score"] <= 0 and scoring["category_score"] <= 0 and weighted_keyword < 35:
            return False

    return True


def _normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=False))


def _error_response(message: str) -> dict:
    return {
        "success": False,
        "model_version": None,
        "data": {
            "query": None,
            "search_engine": None,
            "no_relevant_results": True,
            "message": message,
            "results": [],
            "document_embeddings": [],
            "total_documents": 0,
        },
        "error": message,
    }
