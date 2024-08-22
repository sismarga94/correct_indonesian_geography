import pandas as pd

from app.utils.config import apply_city_replacements, replacements


class NormalFiltering:
    filtered_subdistrict = pd.DataFrame()
    filtered_district = pd.DataFrame()
    filtered_city = pd.DataFrame()
    filtered_province = pd.DataFrame()

    def emptying_filtered_data(self):
        self.filtered_subdistrict = pd.DataFrame()
        self.filtered_district = pd.DataFrame()
        self.filtered_city = pd.DataFrame()
        self.filtered_province = pd.DataFrame()

    def normal_filtering_subdistrict(self, dataset, input_data):
        self.filtered_subdistrict = pd.DataFrame()
        self.filtered_subdistrict = dataset[dataset['kelurahan'].str.upper() == input_data.upper()]
        return self.filtered_subdistrict.drop_duplicates()

    def normal_filtering_subdistrict_contains(self, dataset, input_data):
        self.filtered_subdistrict = pd.DataFrame()
        self.filtered_subdistrict = dataset[dataset['kelurahan'].str.contains(input_data, regex=False)]
        return self.filtered_subdistrict.drop_duplicates()

    def normal_filtering_district(self, dataset, input_data):
        self.filtered_district = pd.DataFrame()
        self.filtered_district = dataset[dataset['kecamatan'].str.upper() == input_data.upper()]
        return self.filtered_district.drop_duplicates()

    def normal_filtering_district_contains(self, dataset, input_data):
        self.filtered_district = pd.DataFrame()
        self.filtered_district = dataset[dataset['kecamatan'].str.contains(input_data, regex=False)]
        return self.filtered_district.drop_duplicates()

    def normal_filtering_city(self, dataset, input_data):
        self.filtered_city = pd.DataFrame()
        # Apply replacements to the 'kecamatan' column and the input data
        input_city_replaced = apply_city_replacements(input_data.upper(), replacements)
        self.filtered_city = dataset[dataset['kabupaten_replaced'].str.upper() == input_city_replaced]
        return self.filtered_city.drop_duplicates()

    def normal_filtering_city_contains(self, dataset, input_data):
        self.filtered_city = pd.DataFrame()
        # Apply replacements to the 'kecamatan' column and the input data
        input_city_replaced = apply_city_replacements(input_data.upper(), replacements)
        self.filtered_city = dataset[dataset['kabupaten_replaced'].str.contains(input_city_replaced, regex=False)]
        return self.filtered_city.drop_duplicates()

    def normal_filtering_province(self, dataset, input_data):
        self.filtered_province = pd.DataFrame()
        self.filtered_province = dataset[dataset['provinsi'].str.upper() == input_data.upper()]
        return self.filtered_province.drop_duplicates()

    def find_city_object_normal(self, dataset, province_and_city, province_city_and_district, input_data):
        self.emptying_filtered_data()
        # if both sub district and district not exists
        if input_data["sub_district"] == "" and input_data["district"] == "":
            self.filtered_city = self.normal_filtering_city(province_and_city, input_data["city"])
            if len(self.filtered_city) == 1:
                return self.filtered_city

        # if only district exists
        elif input_data["district"] != "" and input_data["sub_district"] == "":
            self.filtered_district = self.normal_filtering_district(province_city_and_district, input_data["district"])
            if len(self.filtered_district) >= 1:
                self.filtered_city = self.normal_filtering_city(self.filtered_district, input_data["city"])

            if len(self.filtered_city) == 1:
                return self.filtered_city

            self.filtered_district = self.normal_filtering_subdistrict(dataset, input_data["district"])
            if len(self.filtered_district) >= 1:
                self.filtered_city = self.normal_filtering_city(self.filtered_district, input_data["city"])

            if len(self.filtered_city) == 1:
                return self.filtered_city

        # if only sub district exists
        elif input_data["sub_district"] != "" and input_data["district"] == "":
            self.filtered_subdistrict = self.normal_filtering_subdistrict(dataset, input_data["sub_district"])
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_city = self.normal_filtering_city(self.filtered_subdistrict, input_data["city"])

            if len(self.filtered_city) == 1:
                return self.filtered_city

            self.filtered_subdistrict = self.normal_filtering_district(dataset, input_data["sub_district"])
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_city = self.normal_filtering_city(self.filtered_subdistrict, input_data["city"])

            if len(self.filtered_city) == 1:
                return self.filtered_city
        else:
            # check both sub_district and district else result might be different place due miss or existence of space ' '
            self.filtered_subdistrict = self.normal_filtering_subdistrict(dataset, input_data["sub_district"])
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_district = self.normal_filtering_district(self.filtered_subdistrict,
                                                                        input_data["district"])

                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.normal_filtering_city(self.filtered_district, input_data["city"])
                else:
                    self.filtered_city = self.normal_filtering_city(self.filtered_subdistrict, input_data["city"])
                # return if there is only 1 left
                if len(self.filtered_city) == 1:
                    return self.filtered_city

            self.filtered_subdistrict = self.normal_filtering_subdistrict(dataset, input_data["district"])
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_district = self.normal_filtering_district(self.filtered_subdistrict,
                                                                        input_data["sub_district"])

                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.normal_filtering_city(self.filtered_district, input_data["city"])
                else:
                    self.filtered_city = self.normal_filtering_city(self.filtered_subdistrict, input_data["city"])

                # return if there is only 1 left
                if len(self.filtered_city) == 1:
                    return self.filtered_city

        return pd.DataFrame()

    def check_each_location(self, dataset, input_data):
        # Attempt to filter at the subdistrict level
        filtered_data = pd.DataFrame()
        if input_data["sub_district"] != "":
            filtered_data = pd.concat(
                [filtered_data, self.normal_filtering_subdistrict_contains(dataset, input_data["sub_district"])],
                ignore_index=True)
            filtered_data = pd.concat(
                [filtered_data, self.normal_filtering_district_contains(dataset, input_data["sub_district"])],
                ignore_index=True)
        if input_data["district"] != "":
            filtered_data = pd.concat(
                [filtered_data, self.normal_filtering_district_contains(dataset, input_data["district"])],
                ignore_index=True)
            filtered_data = pd.concat(
                [filtered_data, self.normal_filtering_subdistrict_contains(dataset, input_data["district"])],
                ignore_index=True)
        filtered_data = pd.concat([filtered_data, self.normal_filtering_city_contains(dataset, input_data["city"])],
                                  ignore_index=True)
        return filtered_data
