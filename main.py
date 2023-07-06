import requests
import json
import googlemaps
from googlemaps.exceptions import ApiError
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox

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


def recommend_restaurants_along_route():
    """
    Recommend restaurants along the route from origin to destination.
    """
    origin = entry_origin.get()
    destination = entry_destination.get()
    radius = radius_slider.get()

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
                    messagebox.showerror("Error", "Invalid radius")
                    return

                restaurants = get_restaurants_nearby(start_location, radius)
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
                messagebox.showerror("Error", "Error while fetching API from Yelp")
                return

    # Display recommended restaurants
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, "Recommended Restaurants:\n\n")
    for restaurant_id, restaurant in recommended_restaurants.items():
        name = restaurant['name']
        address = restaurant['location']['address1']
        rating = restaurant['rating']
        result_text.insert(tk.END, "Restaurant: {}\n".format(name))
        result_text.insert(tk.END, "Address: {}\n".format(address))
        result_text.insert(tk.END, "Rating: {}\n".format(rating))
        result_text.insert(tk.END, "\n")

# Create the main application window
window = tk.Tk()
window.title("Restaurant Recommender")

# Create labels and entry fields for origin, destination, and radius
label_origin = tk.Label(window, text="Origin:")
label_origin.pack()
entry_origin = tk.Entry(window)
entry_origin.pack()

label_destination = tk.Label(window, text="Destination:")
label_destination.pack()
entry_destination = tk.Entry(window)
entry_destination.pack()

label_radius = tk.Label(window, text="Radius (in meters):")
label_radius.pack()
# Slider for radius
radius_slider = tk.Scale(window, from_=0, to=5000, orient=tk.HORIZONTAL, resolution=100)
radius_slider.pack()


# Create a button to trigger the recommendation process
button_recommend = tk.Button(window, text="Recommend Restaurants", command=recommend_restaurants_along_route)
button_recommend.pack()

# Create a text widget to display the recommended restaurants
result_text = tk.Text(window, height=10, width=50)
result_text.pack()

# Run the main event loop
window.mainloop()
