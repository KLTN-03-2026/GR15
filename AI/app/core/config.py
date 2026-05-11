from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback khi chua cai dependency
    def load_dotenv(*_args, **_kwargs):  # type: ignore[override]
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("AI_SERVICE_NAME", "KLTN AI Service")
    debug: bool = os.getenv("AI_DEBUG", "false").lower() == "true"
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:7b")
    cover_letter_provider: str = os.getenv("COVER_LETTER_PROVIDER", "ollama")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    ollama_model: str = os.getenv("OLLAMA_MODEL", os.getenv("LOCAL_LLM_MODEL", "qwen2.5:7b"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/responses")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_base_url: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_thinking_budget: int = int(os.getenv("GEMINI_THINKING_BUDGET", "0"))
    gemini_timeout_seconds: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))
    gemini_min_interval_seconds: float = float(os.getenv("GEMINI_MIN_INTERVAL_SECONDS", "1.5"))
    gemini_cooldown_seconds: int = int(os.getenv("GEMINI_COOLDOWN_SECONDS", "45"))
    gemini_cache_ttl_seconds: int = int(os.getenv("GEMINI_CACHE_TTL_SECONDS", "600"))
    gemini_cache_max_items: int = int(os.getenv("GEMINI_CACHE_MAX_ITEMS", "128"))
    chatbot_provider: str = os.getenv("CHATBOT_PROVIDER", "ollama")
    chatbot_llm_fallback_seconds: float = float(os.getenv("CHATBOT_LLM_FALLBACK_SECONDS", "12"))
    ai_llm_fallback_seconds: float = float(os.getenv("AI_LLM_FALLBACK_SECONDS", os.getenv("CHATBOT_LLM_FALLBACK_SECONDS", "12")))
    mock_interview_provider: str = os.getenv("MOCK_INTERVIEW_PROVIDER", "ollama")
    interview_copilot_provider: str = os.getenv("INTERVIEW_COPILOT_PROVIDER", "ollama")
    career_report_provider: str = os.getenv("CAREER_REPORT_PROVIDER", "ollama")
    cv_builder_writing_provider: str = os.getenv("CV_BUILDER_WRITING_PROVIDER", "ollama")
    match_explanation_provider: str = os.getenv("MATCH_EXPLANATION_PROVIDER", "template")
    career_report_max_tokens: int = int(os.getenv("CAREER_REPORT_MAX_TOKENS", "1200"))
    cover_letter_max_tokens: int = int(os.getenv("COVER_LETTER_MAX_TOKENS", "900"))
    cv_builder_writing_max_tokens: int = int(os.getenv("CV_BUILDER_WRITING_MAX_TOKENS", "700"))
    match_explanation_max_tokens: int = int(os.getenv("MATCH_EXPLANATION_MAX_TOKENS", "450"))
    match_batch_llm_explanations: int = int(os.getenv("MATCH_BATCH_LLM_EXPLANATIONS", "0"))
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    chatbot_max_tokens: int = int(os.getenv("CHATBOT_MAX_TOKENS", "300"))
    mock_interview_max_tokens: int = int(os.getenv("MOCK_INTERVIEW_MAX_TOKENS", "300"))
    interview_copilot_max_tokens: int = int(os.getenv("INTERVIEW_COPILOT_MAX_TOKENS", "900"))
    ollama_num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    ollama_num_thread: int = int(os.getenv("OLLAMA_NUM_THREAD", "8"))
    ollama_num_batch: int = int(os.getenv("OLLAMA_NUM_BATCH", "256"))


settings = Settings()
