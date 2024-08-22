from pydantic import BaseModel


class CheckGeographicRequest(BaseModel):
    province: str
    city: str
    district: str
    sub_district: str


class CheckGeographicResponse(BaseModel):
    status: str
    message: str
    data: dict
