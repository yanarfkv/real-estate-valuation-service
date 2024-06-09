import requests
import osmnx as ox
from osmnx import _errors


def get_geocode_data(address):
    url = f'https://nominatim.openstreetmap.org/search.php?q={address}&format=jsonv2&addressdetails=1&limit=1&accept-language=en'
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            return location_data[0]
    return None


def get_nearby_amenities(lat, lon):
    tags = {
        'schools': {'amenity': 'school'},
        'hospitals': {'amenity': 'hospital'},
        'grocery_stores': {'shop': ['supermarket']},
        'kindergartens': {'amenity': 'kindergarten'}
    }
    results = {}
    for category, tag in tags.items():
        try:
            geometries = ox.features_from_point((lat, lon), tags=tag, dist=1000)
            results[category] = len(geometries)
        except _errors.InsufficientResponseError:
            results[category] = 0
    return results
