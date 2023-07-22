import googlemaps
from googlemaps.exceptions import ApiError
import os

class GoogleMapsAPI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key not found in the environment variables.")
        self.gmaps = googlemaps.Client(key=self.api_key)

    def get_directions(self, origin, destination):
        try:
            directions = self.gmaps.directions(origin, destination)
            return directions[0]['legs'][0]['steps']
        except ApiError:
            print("Error while fetching directions from Google Maps")
            return []
