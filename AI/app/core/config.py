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
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:3b")
    cover_letter_provider: str = os.getenv("COVER_LETTER_PROVIDER", "template")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    ollama_model: str = os.getenv("OLLAMA_MODEL", os.getenv("LOCAL_LLM_MODEL", "qwen2.5:3b"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/responses")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    semantic_embedding_model: str = os.getenv("SEMANTIC_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    chatbot_provider: str = os.getenv("CHATBOT_PROVIDER", "template")
    mock_interview_provider: str = os.getenv("MOCK_INTERVIEW_PROVIDER", "ollama")
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
    chatbot_max_tokens: int = int(os.getenv("CHATBOT_MAX_TOKENS", "180"))
    mock_interview_max_tokens: int = int(os.getenv("MOCK_INTERVIEW_MAX_TOKENS", "220"))
    ollama_num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
    ollama_num_thread: int = int(os.getenv("OLLAMA_NUM_THREAD", "8"))


settings = Settings()
