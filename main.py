import requests
import json
import googlemaps
from googlemaps.exceptions import ApiError
import os
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('keys.env')

# Set up Google Maps API client
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

# Set up Yelp API client
YELP_API_KEY = os.getenv('YELP_API_KEY')

def get_directions(origin, destination):
    """
    Get directions from origin to destination using Google Maps API.
    """
    try:
        directions = gmaps.directions(origin, destination)
        return directions[0]['legs'][0]['steps']
    except ApiError:
        print("Error while fetching directions from google maps")
        return []


def get_restaurants_nearby(location, radius):
    """
    Get restaurants near a location using Yelp API.
    """
    headers = {
        'Authorization': 'Bearer {}'.format(YELP_API_KEY)
    }
    params = {
        'categories': 'restaurants',
        'radius': radius,
        'limit': 5,
        'location': location
    }
    response = requests.get(
        'https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
    restaurants = response.json()['businesses']
    return restaurants


def recommend_restaurants_along_route(origin, destination, radius):
    """
    Recommend restaurants along the route from origin to destination.
    """
    directions = get_directions(origin, destination)
    route = []
    for step in directions:
        route.append(step['start_location'])
        route.append(step['end_location'])

    recommended_restaurants = {}
    for i in range(len(route) - 1):
        start_location = '{},{}'.format(route[i]['lat'], route[i]['lng'])
        end_location = '{},{}'.format(route[i + 1]['lat'], route[i + 1]['lng'])

        while True:
            try:
                if float(radius) < 0:
                    print("Invalid radius")
                    radius = input("Enter radius in meters: ")
                    continue
                
                restaurants = get_restaurants_nearby(
                    start_location, radius)
                for restaurant in restaurants:
                    restaurant_id = restaurant['id']
                    if restaurant_id not in recommended_restaurants:
                        recommended_restaurants[restaurant_id] = restaurant
                    else:
                        existing_restaurant = recommended_restaurants[restaurant_id]
                        existing_address = existing_restaurant['location']['address1']
                        new_address = restaurant['location']['address1']
                        if existing_address != new_address:
                            recommended_restaurants[restaurant_id] = restaurant
                break
            except ApiError:
                print("Error while fetching api from Yelp")
                radius = input("Enter desired radius in meters")
    return recommended_restaurants


# Usage example
while (True):

    var_origin = input("Enter start location: ")
    var_destination = input("Enter destination location: ")
    var_radius = input("Enter desired radius in meters: ")
    origin = var_origin
    destination = var_destination
    radius = var_radius  # Radius in meters

    recommended_restaurants = recommend_restaurants_along_route(
        origin, destination, radius)

    if recommended_restaurants:
        break
print("\n Recommended Restaurants: \n")
for restaurant_id, restaurant in recommended_restaurants.items():
    name = restaurant['name']
    address = restaurant['location']['address1']
    rating = restaurant['rating']
    print("Restaurant:", name)
    print("Address:", address)
    print("Rating:", rating)
    print()