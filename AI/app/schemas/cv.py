from pydantic import BaseModel


class CvParseRequest(BaseModel):
    ho_so_id: int
    file_path: str
