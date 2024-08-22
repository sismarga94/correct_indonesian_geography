import numpy as np
import pandas as pd
import textdistance as td
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.config import apply_city_replacements, districts, replacements


class TextDistanceFiltering:
    def __init__(self):
        self.filtered_subdistrict = pd.DataFrame()
        self.filtered_district = pd.DataFrame()
        self.filtered_city = pd.DataFrame()
        self.filtered_province = pd.DataFrame()
        self.methods = ['cosine', 'jaro_winkler', 'levenshtein']

    def emptying_filtered_data(self):
        self.filtered_subdistrict = pd.DataFrame()
        self.filtered_district = pd.DataFrame()
        self.filtered_city = pd.DataFrame()
        self.filtered_province = pd.DataFrame()

    def cosine_similarity_ngrams(self, str1, str2):
        vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))
        text_matrix = vectorizer.fit_transform(str1)
        input_matrix = vectorizer.transform([str2])
        return cosine_similarity(text_matrix, input_matrix).flatten()

    def compare_text_vectorized(self, texts, input_data):
        strings1 = np.array(texts)
        strings2 = np.array([input_data] * len(texts))
        jaro_winkler = np.vectorize(td.jaro_winkler)
        jaro_winkler_distances = jaro_winkler(strings1, strings2)
        levenshtein = np.vectorize(td.levenshtein.normalized_similarity)
        levenshtein_distances = levenshtein(strings1, strings2)
        cosine_distances = self.cosine_similarity_ngrams(texts, input_data)

        return pd.DataFrame({
            'distance_jaro_winkler': jaro_winkler_distances,
            'distance_levenshtein': levenshtein_distances,
            'distance_cosine': cosine_distances
        })

    def filtering_subdistrict(self, dataset, input_data, threshold):
        self.filtered_subdistrict = pd.DataFrame()
        input_subdistrict_replaced = apply_city_replacements(input_data.upper(), replacements)
        # Calculate all distances at once
        distances = self.compare_text_vectorized(dataset['kelurahan'].str.upper(), input_subdistrict_replaced.upper())
        dataset = dataset.reset_index(drop=True)  # Reset index to avoid duplicates
        distances = distances.reset_index(drop=True)  # Reset index to avoid duplicates

        # Add distance columns to the dataset
        for col in distances.columns:
            dataset[col] = distances[col]

        dataset["max_distance_subdistrict"] = dataset[
            ["distance_jaro_winkler", "distance_cosine", "distance_levenshtein"]].max(axis=1)
        mask = (dataset['distance_jaro_winkler'] >= threshold) | \
               (dataset['distance_cosine'] >= threshold) | \
               (dataset['distance_levenshtein'] >= threshold)
        filtered_rows = dataset[mask].copy()
        self.filtered_subdistrict = filtered_rows
        self.filtered_subdistrict["avg_max"] = self.filtered_subdistrict.apply(self.average_text_distance, axis=1)
        return self.filtered_subdistrict.drop_duplicates()

    def filtering_district(self, dataset, input_data, threshold):
        self.filtered_district = pd.DataFrame()
        input_district_replaced = apply_city_replacements(input_data.upper(), replacements)
        distances = self.compare_text_vectorized(dataset['kecamatan'].str.upper(), input_district_replaced.upper())
        dataset = dataset.reset_index(drop=True)  # Reset index to avoid duplicates
        distances = distances.reset_index(drop=True)  # Reset index to avoid duplicates

        # Add distance columns to the dataset
        for col in distances.columns:
            dataset[col] = distances[col]

        dataset["max_distance_district"] = dataset[
            ["distance_jaro_winkler", "distance_cosine", "distance_levenshtein"]].max(axis=1)
        mask = (dataset['distance_jaro_winkler'] >= threshold) | \
               (dataset['distance_cosine'] >= threshold) | \
               (dataset['distance_levenshtein'] >= threshold)
        filtered_rows = dataset[mask].copy()
        self.filtered_district = filtered_rows
        self.filtered_district["avg_max"] = self.filtered_district.apply(self.average_text_distance, axis=1)
        return self.filtered_district.drop_duplicates()

    def filtering_city(self, dataset, input_data, threshold):
        self.filtered_city = pd.DataFrame()
        input_city_replaced = apply_city_replacements(input_data.upper(), replacements)
        distances = self.compare_text_vectorized(dataset['kabupaten_replaced'].str.upper(), input_city_replaced.upper())
        dataset = dataset.reset_index(drop=True)  # Reset index to avoid duplicates
        distances = distances.reset_index(drop=True)  # Reset index to avoid duplicates

        # Add distance columns to the dataset
        for col in distances.columns:
            dataset[col] = distances[col]

        dataset["max_distance_city"] = dataset[
            ["distance_jaro_winkler", "distance_cosine", "distance_levenshtein"]].max(axis=1)
        mask = (dataset['distance_jaro_winkler'] >= threshold) | \
               (dataset['distance_cosine'] >= threshold) | \
               (dataset['distance_levenshtein'] >= threshold)
        filtered_rows = dataset[mask].copy()
        self.filtered_city = filtered_rows
        self.filtered_city["avg_max"] = self.filtered_city.apply(self.average_text_distance, axis=1)
        return self.filtered_city.drop_duplicates()

    def filtering_province(self, dataset, input_data, threshold):
        self.filtered_province = pd.DataFrame()
        distances = self.compare_text_vectorized(dataset['provinsi'].str.upper(), input_data.upper())
        dataset = dataset.reset_index(drop=True)  # Reset index to avoid duplicates
        distances = distances.reset_index(drop=True)  # Reset index to avoid duplicates

        # Add distance columns to the dataset
        for col in distances.columns:
            dataset[col] = distances[col]

        dataset["max_distance_province"] = dataset[
            ["distance_jaro_winkler", "distance_cosine", "distance_levenshtein"]].max(axis=1)
        mask = (dataset['distance_jaro_winkler'] >= threshold) | \
               (dataset['distance_cosine'] >= threshold) | \
               (dataset['distance_levenshtein'] >= threshold)
        filtered_rows = dataset[mask].copy()
        self.filtered_province = filtered_rows
        self.filtered_province["avg_max"] = self.filtered_province.apply(self.average_text_distance, axis=1)
        return self.filtered_province.drop_duplicates()

    def average_text_distance(self, row):
        # List of columns to be used for avg_max calculation
        columns_to_consider = ['max_distance_subdistrict', 'max_distance_district', 'max_distance_city',
                               'max_distance_province']
        existing_columns = [col for col in columns_to_consider if col in row.index]
        # Calculate the sum and count of non-null values
        values = row[existing_columns].dropna()
        if len(values) == 0:
            return None  # or some other default value
        avg_max = values.sum() / len(values)
        return avg_max

    def find_city_object(self, dataset, province_and_city, province_city_and_district, input_data):
        self.emptying_filtered_data()
        threshold = 0.8
        max_row = pd.DataFrame()
        max_row_two = pd.DataFrame()
        # if both not exists
        if input_data["sub_district"] == "" and input_data["district"] == "":
            self.filtered_city = self.filtering_city(province_and_city, input_data["city"], threshold)
            if len(self.filtered_city) == 1:
                return self.filtered_city
            elif len(self.filtered_city > 1):
                max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                return max_row

        # if only district exists
        elif input_data["district"] != "" and input_data["sub_district"] == "":
            # check if input district is district
            province_city_and_district = dataset[
                ["provinsi", "kabupaten", "kecamatan", "kabupaten_replaced"]].drop_duplicates().reset_index()
            self.filtered_district = self.filtering_district(province_city_and_district, input_data["district"],
                                                             threshold)
            if len(self.filtered_district) >= 1:
                self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                else:
                    # if self.filtered_city is empty then find max_distance from filtered_district
                    max_row = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                    max_row['avg_max'] = max_row['avg_max'] / 2
            else:
                # if self.filtered_district is empty then directly check city using province_and_city
                province_and_city = dataset[
                    ["provinsi", "kabupaten", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_city = self.filtering_city(province_and_city, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]

            # check if input district is subdistrict
            self.filtered_district = self.filtering_subdistrict(dataset, input_data["district"], threshold)
            if len(self.filtered_district) >= 1:
                self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                else:
                    # if self.filtered_city is empty then find max_distance from filtered_district
                    max_row_two = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                    max_row_two['avg_max'] = max_row_two['avg_max'] / 2
            else:
                # if self.filtered_district is empty then directly check city using province_and_city
                province_and_city = dataset[
                    ["provinsi", "kabupaten", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_city = self.filtering_city(province_and_city, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]

            if max_row_two.empty:
                return max_row
            elif max_row.empty:
                return max_row_two
            elif not max_row.empty and not max_row_two.empty:
                if max_row["avg_max"].values[0] >= max_row_two["avg_max"].values[0]:
                    return max_row
                else:
                    return max_row_two
            else:
                return pd.DataFrame()

        # if only sub district exists
        elif input_data["sub_district"] != "" and input_data["district"] == "":
            # check if input subdistrict is subdistrict
            self.filtered_subdistrict = self.filtering_subdistrict(dataset, input_data["sub_district"], threshold)
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                else:
                    max_row = self.filtered_subdistrict.loc[[self.filtered_subdistrict['avg_max'].idxmax()]]
                    max_row['avg_max'] = max_row['avg_max'] / 2

            else:
                # if self.filtered_subdistrict is empty then directly check city using province_and_city
                province_and_city = dataset[
                    ["provinsi", "kabupaten", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_city = self.filtering_city(province_and_city, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]

            # check if input subdistrict is district
            self.filtered_subdistrict = self.filtering_district(dataset, input_data["sub_district"], threshold)
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                else:
                    max_row_two = self.filtered_subdistrict.loc[[self.filtered_city['avg_max'].idxmax()]]
                    max_row_two['avg_max'] = max_row_two['avg_max'] / 2
            else:
                province_and_city = districts[
                    ["provinsi", "kabupaten", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_city = self.filtering_city(province_and_city, input_data["city"], threshold)
                if len(self.filtered_city) >= 1:
                    max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]

            if max_row_two.empty:
                return max_row
            elif max_row.empty:
                return max_row_two
            elif not max_row.empty and not max_row_two.empty:
                if max_row["avg_max"].values[0] >= max_row_two["avg_max"].values[0]:
                    return max_row
                else:
                    return max_row_two
            else:
                return pd.DataFrame()
        else:
            self.filtered_subdistrict = self.filtering_subdistrict(dataset, input_data["sub_district"], threshold)
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_district = self.filtering_district(self.filtered_subdistrict, input_data["district"],
                                                                 threshold)
                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                    else:
                        max_row = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                else:
                    self.filtered_city = self.filtering_city(self.filtered_subdistrict, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        self.filtered_district = self.filtering_district(self.filtered_city, input_data["district"],
                                                                         threshold)
                        if len(self.filtered_district) >= 1:
                            max_row = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                        else:
                            max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                            max_row['avg_max'] = max_row['avg_max'] / 2
                    else:
                        max_row = self.filtered_subdistrict.loc[[self.filtered_subdistrict['avg_max'].idxmax()]]
                        max_row['avg_max'] = max_row['avg_max'] / 2
            else:
                province_city_and_district = dataset[
                    ["provinsi", "kabupaten", "kecamatan", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_district = self.filtering_district(province_city_and_district, input_data["district"],
                                                                 threshold)
                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        max_row = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                    else:
                        max_row = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                        max_row['avg_max'] = max_row['avg_max'] / 2

            self.filtered_subdistrict = self.filtering_subdistrict(dataset, input_data["district"], threshold)
            if len(self.filtered_subdistrict) >= 1:
                self.filtered_district = self.filtering_district(self.filtered_subdistrict, input_data["sub_district"],
                                                                 threshold)
                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                    else:
                        max_row_two = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                else:
                    self.filtered_city = self.filtering_city(self.filtered_subdistrict, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        self.filtered_district = self.filtering_district(self.filtered_city, input_data["sub_district"],
                                                                         threshold)
                        if len(self.filtered_district) >= 1:
                            max_row_two = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                        else:
                            max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                            max_row_two['avg_max'] = max_row_two['avg_max'] / 2
                    else:
                        max_row_two = self.filtered_subdistrict.loc[[self.filtered_subdistrict['avg_max'].idxmax()]]
                        max_row_two['avg_max'] = max_row_two['avg_max'] / 2
            else:
                province_city_and_district = dataset[
                    ["provinsi", "kabupaten", "kecamatan", "kabupaten_replaced"]].drop_duplicates().reset_index()
                self.filtered_district = self.filtering_district(province_city_and_district, input_data["sub_district"],
                                                                 threshold)
                if len(self.filtered_district) >= 1:
                    self.filtered_city = self.filtering_city(self.filtered_district, input_data["city"], threshold)
                    if len(self.filtered_city) >= 1:
                        max_row_two = self.filtered_city.loc[[self.filtered_city['avg_max'].idxmax()]]
                    else:
                        max_row_two = self.filtered_district.loc[[self.filtered_district['avg_max'].idxmax()]]
                        max_row_two['avg_max'] = max_row_two['avg_max'] / 2

            if max_row_two.empty:
                return max_row
            elif max_row.empty:
                return max_row_two
            elif not max_row.empty and not max_row_two.empty:
                if max_row["avg_max"].values[0] >= max_row_two["avg_max"].values[0]:
                    return max_row
                else:
                    return max_row_two
            else:
                return pd.DataFrame()
        return max_row
