import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# Load the districts csv file
filename = 'districts.csv'
districts = pd.read_csv(filename)
province_city_and_district = districts[["provinsi", "kabupaten", "kecamatan"]].drop_duplicates().reset_index()
province_and_city = districts[["provinsi", "kabupaten"]].drop_duplicates().reset_index()

replacements = {
    'KAB. ': '',
    'KABUPATEN ': '',
    'KOTA ': '',
    'KECAMATAN ': '',
}

def apply_city_replacements(s, replacements):
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

districts['kabupaten_replaced'] = districts['kabupaten'].str.upper().apply(
    lambda x: apply_city_replacements(x, replacements))
province_city_and_district['kabupaten_replaced'] = province_city_and_district['kabupaten'].str.upper().apply(
    lambda x: apply_city_replacements(x, replacements))
province_and_city['kabupaten_replaced'] = province_and_city['kabupaten'].str.upper().apply(
    lambda x: apply_city_replacements(x, replacements))

districts['kelurahan'] = districts['kelurahan'].str.upper()
districts['kecamatan'] = districts['kecamatan'].str.upper()
districts['kabupaten'] = districts['kabupaten'].str.upper()
districts['provinsi'] = districts['provinsi'].str.upper()
province_and_city['provinsi'] = province_and_city['provinsi'].str.upper()
province_and_city['kabupaten'] = province_and_city['kabupaten'].str.upper()
province_city_and_district['provinsi'] = province_city_and_district['provinsi'].str.upper()
province_city_and_district['kabupaten'] = province_city_and_district['kabupaten'].str.upper()
province_city_and_district['kecamatan'] = province_city_and_district['kecamatan'].str.upper()
