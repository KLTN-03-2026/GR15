from pydantic import BaseModel


class JdParseRequest(BaseModel):
    tin_tuyen_dung_id: int
    job_text: str
