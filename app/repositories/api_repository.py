import time

from pandas import DataFrame

from app.models.location import CheckGeographicRequest
from app.utils.config import districts, province_and_city, province_city_and_district
from sqlalchemy.orm import Session
from sqlalchemy import text


class ApiRepository:
    def __init__(self, db):
        self.db = db

    def check_geographic(self, request: CheckGeographicRequest, normal_filter, td_filter) -> (dict, str):
        # Simulate fetching data from a database or external service
        normal = normal_filter.find_city_object_normal(districts, province_and_city, province_city_and_district,
                                                       request.dict())
        response_text = "Geographic data retrieved successfully"
        if len(normal) == 1:
            return normal, response_text
        elif normal.empty:
            dataset = normal_filter.check_each_location(districts, request.dict())
            if not dataset.empty:
                td = td_filter.find_city_object(dataset, province_and_city, province_city_and_district, request.dict())
                if not td.empty:
                    return td, response_text
            else:
                td = td_filter.find_city_object(districts, province_and_city, province_city_and_district,
                                                request.dict())
                return td, response_text
        else:
            return {}, "Geographic Data Not Found"

    def check_geographic_dataframe(self, request_df: DataFrame, normal_filter, td_filter) -> DataFrame:
        start = time.time()
        request_df['province'] = request_df['province'].str.upper()
        request_df['city'] = request_df['city'].str.upper()
        request_df['district'] = request_df['district'].str.upper()
        request_df['sub_district'] = request_df['sub_district'].str.upper()
        request_df = request_df[['province', 'city', 'district', 'sub_district']]
        request_df["actual_province"] = None
        request_df["actual_city"] = None
        request_df["actual_district"] = None
        request_df["actual_sub_district"] = None
        request_df["equal_to"] = None

        for i in range(len(request_df)):
            input_data = {
                "sub_district": request_df['sub_district'][i],
                "district": request_df['district'][i],
                "city": request_df['city'][i],
                "province": request_df['province'][i]
            }
            check = self.check_db(input_data)
            if check:
                print(i, "=", check)
                request_df['actual_sub_district'][i] = check["actual_sub_district"]
                request_df['actual_district'][i] = check["actual_district"]
                request_df['actual_city'][i] = check["actual_city"]
                request_df['actual_province'][i] = check["actual_province"]
                continue
            find = normal_filter.find_city_object_normal(districts, province_and_city, province_city_and_district,
                                                         input_data)
            if len(find) == 1:
                request_df['actual_sub_district'][i] = find['kelurahan'].iloc[
                    0] if 'kelurahan' in find.columns else None
                request_df['actual_district'][i] = find['kecamatan'].iloc[0] if 'kecamatan' in find.columns else None
                request_df['actual_city'][i] = find['kabupaten'].iloc[0] if 'kabupaten' in find.columns else None
                request_df['actual_province'][i] = find['provinsi'].iloc[0] if 'provinsi' in find.columns else None
                request_df['equal_to'][i] = "="
                self.insert_db(request_df.iloc[[i]])
            elif find.empty:
                dataset = normal_filter.check_each_location(districts, input_data)
                if not dataset.empty:
                    find = td_filter.find_city_object(dataset, province_and_city, province_city_and_district,
                                                      input_data)
                    if not find.empty:
                        request_df['actual_sub_district'][i] = find['kelurahan'].iloc[
                            0] if 'kelurahan' in find.columns else None
                        request_df['actual_district'][i] = find['kecamatan'].iloc[
                            0] if 'kecamatan' in find.columns else None
                        request_df['actual_city'][i] = find['kabupaten'].iloc[
                            0] if 'kabupaten' in find.columns else None
                        request_df['actual_province'][i] = find['provinsi'].iloc[
                            0] if 'provinsi' in find.columns else None
                        self.insert_db(request_df.iloc[[i]])
                else:
                    find = td_filter.find_city_object(districts, province_and_city, province_city_and_district,
                                                      input_data)
                    if not find.empty:
                        request_df['actual_sub_district'][i] = find['kelurahan'].iloc[
                            0] if 'kelurahan' in find.columns else None
                        request_df['actual_district'][i] = find['kecamatan'].iloc[
                            0] if 'kecamatan' in find.columns else None
                        request_df['actual_city'][i] = find['kabupaten'].iloc[
                            0] if 'kabupaten' in find.columns else None
                        request_df['actual_province'][i] = find['provinsi'].iloc[
                            0] if 'provinsi' in find.columns else None
                        self.insert_db(request_df.iloc[[i]])
        end = time.time()
        response_df = request_df.copy()
        print("Elapsed Time for 10.000 rows: ", round(end - start, 3), "seconds")  # time in seconds
        return response_df

    def check_db(self, request: dict) -> dict:
        province = request["province"]
        city = request["city"]
        district = request["district"]
        sub_district = request["sub_district"]
        query = "select * from indexed_table where province = :province"
        params = {"province": province}

        if city:
            query += " AND city = :city"
            params["city"] = city
        if district:
            query += " AND district = :district"
            params["district"] = district
        if sub_district:
            query += " AND sub_district = :sub_district"
            params["sub_district"] = sub_district

        query_text = text(query)
        result = self.db.execute(query_text, params)
        row = result.fetchone()
        if row:
            column_names = result.keys()
            dict_result = dict(zip(column_names, row))
        else:
            dict_result = {}
        return dict_result

    def insert_db(self, request: DataFrame) -> dict:
        province = request["province"].iloc[0] if 'province' in request.columns else ""
        city = request["city"].iloc[0] if 'city' in request.columns else ""
        district = request["district"].iloc[0] if 'district' in request.columns else ""
        sub_district = request["sub_district"].iloc[0] if 'sub_district' in request.columns else ""
        actual_province = request["actual_province"].iloc[0] if 'actual_province' in request.columns else ""
        actual_city = request["actual_city"].iloc[0] if 'actual_city' in request.columns else ""
        actual_district = request["actual_district"].iloc[0] if 'actual_district' in request.columns else ""
        actual_sub_district = request["actual_sub_district"].iloc[0] if 'actual_sub_district' in request.columns else ""

        # query = "insert into indexed_table values ('" + province + "','" + actual_province + "','" + city + "','" + actual_city + "','" + district + "','" + actual_district + "','" + sub_district + "','" + actual_sub_district + "')"
        # print(query)
        query_text = text("""
            INSERT INTO indexed_table 
            (province, actual_province, city, actual_city, district, actual_district, sub_district, actual_sub_district) 
            VALUES (:province, :actual_province, :city, :actual_city, :district, :actual_district, :sub_district, :actual_sub_district)
        """)

        params = {
            'province': safe_str(province),
            'actual_province': safe_str(actual_province),
            'city': safe_str(city),
            'actual_city': safe_str(actual_city),
            'district': safe_str(district),
            'actual_district': safe_str(actual_district),
            'sub_district': safe_str(sub_district),
            'actual_sub_district': safe_str(actual_sub_district)
        }
        self.db.execute(query_text, params)
        self.db.commit()


def safe_str(value):
    return str(value) if value is not None else ''
