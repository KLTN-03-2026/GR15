# AI Service

FastAPI service cho các chức năng AI của hệ thống tuyển dụng.

## Chức năng hiện tại

- `GET /health`
- `POST /parse/cv`
- `POST /parse/jd`
- `POST /match/cv-jd`
- `POST /generate/cover-letter`
- `POST /generate/career-report`

Hiện tại service đã có:

- CV Parser
- JD Parser
- Matching Engine
- Cover Letter Generator
- Career Report cơ bản

## Chạy local

```bash
cd AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## Tự động đọc `.env`

Service hiện đã tự load file `.env` trong thư mục `AI/` bằng `python-dotenv`.

Bạn chỉ cần:

1. copy `.env.example` thành `.env`
2. chỉnh biến môi trường trong `.env`
3. restart `uvicorn`

## Biến môi trường chính

- `AI_SERVICE_NAME`
- `AI_DEBUG`
- `LOCAL_LLM_MODEL`
- `COVER_LETTER_PROVIDER`
- `OLLAMA_URL`
- `OLLAMA_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`

## Ví dụ switch provider

### Dùng template

```env
COVER_LETTER_PROVIDER=template
```

### Dùng Ollama local

```env
COVER_LETTER_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

### Dùng OpenAI

```env
COVER_LETTER_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1/responses
```

## Contract

Tất cả endpoint generation/parse/matching trả về JSON theo dạng:

```json
{
  "success": true,
  "parser_version": "cv_parser_v1",
  "confidence_score": 0.85,
  "model_version": "matching_v3_dynamic_weights",
  "data": {},
  "error": null
}
```
