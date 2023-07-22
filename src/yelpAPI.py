import requests
import os

class YelpAPI:
    def __init__(self):
        self.api_key = os.getenv('YELP_API_KEY')
        if not self.api_key:
            raise ValueError("Yelp API key not found in the environment variables.")

    def get_restaurants_nearby(self, location, radius):
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        params = {
            'categories': 'restaurants',
            'radius': radius,
            'limit': 5,
            'location': location
        }
        response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
        restaurants = response.json()['businesses']
        return restaurants
