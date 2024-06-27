import requests
import googlemaps
import os
import polyline
import folium
from dotenv import load_dotenv, dotenv_values
from pprint import pprint
from datetime import datetime, timedelta



load_dotenv()
API_KEY = os.getenv('GM_TOKEN')
gmaps = googlemaps.Client(key = API_KEY)



def get_long_lat(address):
    data = gmaps.geocode(address)[0]

    lat = data["geometry"]["location"]["lat"]
    lng = data["geometry"]["location"]["lng"]

    return [lat, lng]



def get_route(origin, destination):
    url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
    }
    o_coords = get_long_lat(origin)
    d_coords = get_long_lat(destination)

    data = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": o_coords[0],
                    "longitude": o_coords[1]
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": d_coords[0],
                    "longitude": d_coords[1]
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False
        },
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }

    response = requests.post(url, json=data, headers=headers).json()
    
    return response["routes"][0]



def create_map(polyln):

    # Decode the polyline
    decoded_polyline = polyline.decode(polyln)

    # Create a folium map centered at the first point of the decoded polyline
    map = folium.Map(location=decoded_polyline[0], zoom_start=15)

    # Create a folium polyline from the decoded polyline
    folium.PolyLine(decoded_polyline, color='blue', weight=2.5, opacity=1).add_to(map)

    # Save the map as an HTML file
    map.save("route_map.html")


#Two places in NYC

origin = "Times Square, New York, NY"
destination = "Central Park, New York, NY"

route = get_route(origin, destination)
print(route["duration"][:-1])
create_map(route["polyline"]["encodedPolyline"])



