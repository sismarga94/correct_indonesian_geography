from app.models.location import CheckGeographicRequest, CheckGeographicResponse
from app.repositories.api_repository import ApiRepository
from app.utils.normal_text_filter import NormalFiltering
from app.utils.text_distance_filter import TextDistanceFiltering


class ApiService:
    def __init__(self, repository: ApiRepository, normal_filter: NormalFiltering, td_filter: TextDistanceFiltering):
        self.repository = repository
        self.normal_filter = normal_filter
        self.td_filter = td_filter

    def check_geographic(self, request: CheckGeographicRequest) -> CheckGeographicResponse:
        response_obj = request.dict()
        data, message = self.repository.check_geographic(request, self.normal_filter, self.td_filter)
        response_obj["actual_province"] = data["provinsi"].iloc[0] if 'provinsi' in data.columns else None
        response_obj["actual_city"] = data["kabupaten"].iloc[0] if 'kabupaten' in data.columns else None
        response_obj["actual_district"] = data["kecamatan"].iloc[0] if 'kecamatan' in data.columns else None
        response_obj["actual_sub_district"] = data["kelurahan"].iloc[0] if 'kelurahan' in data.columns else None
        return CheckGeographicResponse(
            status="success",
            message=message,
            data=response_obj
        )

    def process_file(self, request_df):
        response_df = self.repository.check_geographic_dataframe(request_df, self.normal_filter, self.td_filter)
        return response_df

    def check_db(self, request) -> dict:
        response = self.repository.check_db(request)
        return response
