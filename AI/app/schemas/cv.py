from pydantic import BaseModel


class CvParseRequest(BaseModel):
    ho_so_id: int
    file_path: str | None = None
    raw_text: str | None = None
