__doc__ = """
    Viết script tìm 50 quán bia / quán nhậu / quán bar / nhà hàng quanh toạ độ của lớp học (lên google map để lấy) với bán kính 2KM.
    Ghi kết quả theo định dạng JSON vào file pymi_beer.geojson

    Sử dụng Google Map API
    https://developers.google.com/places/web-service/

    Chú ý: phải tạo "token" để có thể truy cập API.

    Chú ý: giữa mỗi trang kết quả phải đợi để lấy tiếp.

    Chú ý: tránh đặt ngược lat/long

    - Kết quả trả về lưu theo format JSON, với mỗi điểm là một GeoJSON point (https://leafletjs.com/examples/geojson/), up file này lên GitHub để xem bản đồ kết quả.

    - Xem mẫu GEOJSON https://github.com/tung491/make_boba_map
"""

import json
import requests
import time
import pprint
from google_api_key import get_api_key

api_key = get_api_key()

nearby_url = (
    "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"\
    "location={},{}"\
    "&radius={}&type={}"\
    "&keyword={}&key={}"\
    "&language=vi"
)

detail_place_url = (
    "https://maps.googleapis.com/maps/api/place/details/" \
    "json?place_id={}&fields=formatted_address&key={}"
    )


def find_nearby(lat, long, radius, type, keyword):
    ses1 = requests.Session()
    ses2 = requests.Session()
    req1 = ses1.get(
        nearby_url.format(lat, long, radius, type, ",".join(keyword), api_key)
    )

    data = req1.json()

    places = []
    count = 1

    while True:
        for place in data['results']:
            if count <= 50:
                req2 = ses2.get(detail_place_url.format(place['place_id'], api_key))
                place_detail = req2.json()

                places.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                place['geometry']['location']['lat'],
                                place['geometry']['location']['lng']
                            ]
                        },
                        "properties": {
                            "Address": place_detail['result']['formatted_address'],
                            "name": place['name']
                        }
                    }
                )

            count += 1
        if 'next_page_token' in data:
            time.sleep(3)
            req1 = ses1.get(
                nearby_url.format(lat, long, radius, type, keyword, api_key)
                + "&pagetoken={}".format(data['next_page_token'])
                )

            data = req1.json()
        else:
            break

    return places


def export_geojson_file(places):
    data = {
        "type": "FeatureCollection",
        "features" : places
    }

    with open("pymi_beer.geojson", mode="wt") as f:
        f.write(json.dumps(data))

    rint("Sucessful!!")


def main():
    lat = "21.012783051599293"
    long = "105.82166529036826"
    rad = "2000"
    type = "Nhà Hàng"
    keyword = ["quán nhậu", "quán bia", "quán bar"]

    places = find_nearby(lat, long, rad, type, keyword)
    pprint.pprint(len(places))
    export_geojson_file(places)

if __name__ == "__main__":
    main()

