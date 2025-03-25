import requests
import customtkinter as ctk
from geopy.geocoders import Nominatim
import geocoder

# Function to fetch weather data
def get_weather(location_name):
    geolocator = Nominatim(user_agent="vibe.weather")
    location = geolocator.geocode(location_name)

    if location:
        latitude = location.latitude
        longitude = location.longitude
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&daily=precipitation_sum,uv_index_max,sunrise,sunset"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            temperature = data["current_weather"]["temperature"]
            wind_speed = data["current_weather"]["windspeed"]
            precipitation = data["daily"]["precipitation_sum"][0]
            uv_index = data["daily"]["uv_index_max"][0]
            sunrise = data["daily"]["sunrise"][0].split("T")[1]
            sunset = data["daily"]["sunset"][0].split("T")[1]
            
            result_label.configure(text=f"Location: {location_name}\nLatitude: {latitude:.2f}, Longitude: {longitude:.2f}\nTemperature: {temperature}°C\nWind Speed: {wind_speed} m/s\nPrecipitation: {precipitation} mm\nUV Index: {uv_index}\nSunrise: {sunrise}\nSunset: {sunset}")
        except Exception as e:
            result_label.configure(text="Error fetching weather data.")
    else:
        result_label.configure(text="Location not found.")

# Function to detect and fetch weather for current location
def get_current_location_weather():
    g = geocoder.ip("me")
    if g.latlng:
        latitude, longitude = g.latlng
        geolocator = Nominatim(user_agent="vibe.weather")
        location = geolocator.reverse((latitude, longitude), language="en")
        location_name = location.address if location else "Current Location"
        get_weather(location_name)
    else:
        result_label.configure(text="Could not detect location.")

# Initialize CustomTkinter window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("vibe.weather")
root.geometry("400x550")
root.resizable(False, False)

# UI Frame
frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Title Label
title_label = ctk.CTkLabel(frame, text="vibe.weather", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

# Location Input
location_label = ctk.CTkLabel(frame, text="Enter Location:", font=("Arial", 14))
location_label.pack(pady=5)
location_entry = ctk.CTkEntry(frame, width=250)
location_entry.pack(pady=5)

# Fetch Button
fetch_button = ctk.CTkButton(frame, text="Get Weather", command=lambda: get_weather(location_entry.get()), fg_color="#1f6aa5", hover_color="#144a7f")
fetch_button.pack(pady=10)

# Detect Location Button
detect_button = ctk.CTkButton(frame, text="Use Current Location", command=get_current_location_weather, fg_color="#28a745", hover_color="#1e7e34")
detect_button.pack(pady=10)

# Result Label
result_label = ctk.CTkLabel(frame, text="", font=("Arial", 16))
result_label.pack(pady=10)

# Run the application
root.mainloop()
