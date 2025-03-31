import requests
import customtkinter as ctk
from geopy.geocoders import Nominatim
import geocoder
import threading

# Global geolocator instance for efficiency
geolocator = Nominatim(user_agent="vibe.weather")

# Cache to store weather data to avoid repeated API calls for the same location
cache = {}

# Function to safely update the result label on the main thread
def update_result(result):
    result_label.configure(text=result)

# Function to fetch weather data
def get_weather(location_name):
    def fetch():
        if location_name in cache:
            # If the location is in cache, use the cached result
            result = cache[location_name]
            root.after(0, update_result, result)
            return

        location = geolocator.geocode(location_name, timeout=10)

        if location:
            latitude, longitude = location.latitude, location.longitude
            url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&daily=precipitation_sum,uv_index_max,sunrise,sunset"

            try:
                response = requests.get(url, timeout=10)
                data = response.json()

                # Ensure the required data exists in the response
                if "current_weather" in data and "temperature" in data["current_weather"]:
                    temperature = data["current_weather"]["temperature"]
                    wind_speed = data["current_weather"]["windspeed"]
                    precipitation = data["daily"]["precipitation_sum"][0]
                    uv_index = data["daily"]["uv_index_max"][0]
                    sunrise = data["daily"]["sunrise"][0].split("T")[1]
                    sunset = data["daily"]["sunset"][0].split("T")[1]

                    result = (
                        f"Location: {location_name}\n"
                        f"Latitude: {latitude:.2f}, Longitude: {longitude:.2f}\n"
                        f"Temperature: {temperature}°C\n"
                        f"Wind Speed: {wind_speed} m/s\n"
                        f"Precipitation: {precipitation} mm\n"
                        f"UV Index: {uv_index}\n"
                        f"Sunrise: {sunrise}\n"
                        f"Sunset: {sunset}"
                    )

                    # Cache the result for future use
                    cache[location_name] = result
                else:
                    result = "Unexpected API response structure."

            except requests.exceptions.RequestException as e:
                result = f"Request error: {e}"
            except ValueError:
                result = "Error parsing weather data."

        else:
            result = "Location not found."

        # Update the UI safely on the main thread
        root.after(0, update_result, result)

    # Start the fetch function in a new thread
    threading.Thread(target=fetch, daemon=True).start()

# Function to detect and fetch weather for current location
def get_current_location_weather():
    def fetch():
        g = geocoder.ip("me")
        if g.latlng:
            latitude, longitude = g.latlng
            location = geolocator.reverse((latitude, longitude), language="en", timeout=10)
            location_name = location.address if location else f"{latitude},{longitude}"  # Use name if available

            get_weather(location_name)  # Pass name instead of just coordinates
        else:
            result_label.configure(text="Could not detect location.")

    threading.Thread(target=fetch, daemon=True).start()

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
