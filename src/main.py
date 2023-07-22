import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from dotenv import load_dotenv
from googleMapsAPI import GoogleMapsAPI
from yelpAPI import YelpAPI

# Load environment variables from keys.env
dotenv_path = os.path.join(os.path.dirname(__file__), '../configs/keys.env')
load_dotenv(dotenv_path)


def get_route(gmaps_api, origin, destination):
    directions = gmaps_api.get_directions(origin, destination)
    route = []
    for step in directions:
        route.append(step['start_location'])
        route.append(step['end_location'])
    return route

def get_recommended_restaurants(yelp_api, route, radius):
    recommended_restaurants = {}
    for i in range(len(route) - 1):
        start_location = '{},{}'.format(route[i]['lat'], route[i]['lng'])
        end_location = '{},{}'.format(route[i + 1]['lat'], route[i + 1]['lng'])

        if float(radius) < 0:
            messagebox.showerror("Error", "Invalid radius")
            return

        restaurants = yelp_api.get_restaurants_nearby(start_location, radius)
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
    return recommended_restaurants

def display_recommended_restaurants(recommended_restaurants):
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

def recommend_restaurants_along_route(gmaps_api, yelp_api):
    origin = entry_origin.get()
    destination = entry_destination.get()
    radius = radius_slider.get()

    route = get_route(gmaps_api, origin, destination)
    recommended_restaurants = get_recommended_restaurants(yelp_api, route, radius)
    display_recommended_restaurants(recommended_restaurants)

# Create the main application window
window = tk.Tk()
window.title("Restaurant Recommender")

try:
    gmaps = GoogleMapsAPI()
    yelp = YelpAPI()

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
    radius_slider = tk.Scale(window, from_=100, to=5000, orient=tk.HORIZONTAL, resolution=100)
    radius_slider.pack()

    # Create a button to trigger the recommendation process
    button_recommend = tk.Button(window, text="Recommend Restaurants", command=lambda: recommend_restaurants_along_route(gmaps, yelp))
    button_recommend.pack()

    # Create a text widget to display the recommended restaurants
    result_text = tk.Text(window, height=10, width=50)
    result_text.pack()

    # Run the main event loop
    window.mainloop()
except ValueError as e:
    messagebox.showerror("Error", str(e))
