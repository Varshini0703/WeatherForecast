import os
import tkinter as tk
from tkinter import messagebox
import requests
import pycountry
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import pygame

ASSETS = os.path.join(os.path.dirname(__file__), "assets")

pygame.mixer.init()
wind_sound = pygame.mixer.Sound(os.path.join(ASSETS, "wind.mp3"))
rain_sound = pygame.mixer.Sound(os.path.join(ASSETS, "rain_light.mp3"))
heavy_rain_sound = pygame.mixer.Sound(os.path.join(ASSETS, "rain_heavy.mp3"))
thunderstorm_sound = pygame.mixer.Sound(os.path.join(ASSETS, "thunderstorm.mp3"))
sunny_sound = pygame.mixer.Sound(os.path.join(ASSETS, "sunny.mp3"))


def get_weather(city):
    api_key = "9b44d42714e481be282853dcd4ea3ed1"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    res = requests.get(url)
    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None
    weather = res.json()
    icon_id = weather['weather'][0]['icon']
    description = weather['weather'][0]['description']
    temperature = weather['main']['temp'] - 273.15
    city = weather['name']
    country_code = weather['sys']['country']
    country = pycountry.countries.get(alpha_2=country_code).name
    pressure = weather['main']['pressure']
    humidity = weather['main']['humidity']
    wind = weather['wind']['speed']
    sunrise = weather['sys']['sunrise']
    sunset = weather['sys']['sunset']
    current_time = weather['dt']
    lon = weather['coord']['lon']
    lat = weather['coord']['lat']

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    local_tz = pytz.timezone(timezone_str)
    local_time = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, pressure, humidity, wind,
            city, country, sunrise, sunset, current_time, local_time)


def stop_all_sounds():
    wind_sound.stop()
    rain_sound.stop()
    heavy_rain_sound.stop()
    thunderstorm_sound.stop()
    sunny_sound.stop()


def show_flood_warning(root):
    flood_warning = tk.Toplevel(root)
    flood_warning.attributes('-fullscreen', True)
    flood_warning.configure(bg="red")
    warning_label = tk.Label(
        flood_warning, text="FLOOD DANGER",
        font=("Helvetica", 70, "bold"), fg="black", bg="red"
    )
    warning_label.pack(expand=True)

    def blink():
        current_color = warning_label.cget("foreground")
        next_color = "black" if current_color == "red" else "red"
        warning_label.config(foreground=next_color)
        flood_warning.after(500, blink)

    flood_warning.after(0, blink)
    flood_warning.after(3000, flood_warning.destroy)


def run_weather_app(fullscreen=True):
    root = ttk.Window(themename="morph")
    root.title("Weather App")
    root.attributes('-fullscreen', fullscreen)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    def load_bg(filename):
        return ImageTk.PhotoImage(
            Image.open(os.path.join(ASSETS, filename)).resize(
                (screen_width, screen_height), Image.LANCZOS
            )
        )

    day_bg = load_bg("day_background.jpg")
    afternoon_bg = load_bg("afternoon_background.jpg")
    evening_bg = load_bg("evening_background.jpg")
    night_bg = load_bg("night_background.jpg")
    initial_bg = load_bg("clouds_background.jpg")

    background_label = tk.Label(root)
    background_label.place(relwidth=1, relheight=1)
    background_label.config(image=initial_bg)
    background_label.image = initial_bg

    button_frame = tk.Frame(root, bg="light grey")
    button_frame.place(relx=0, rely=0, relwidth=1, relheight=0.03)

    ttk.Button(button_frame, text="-", command=root.iconify, bootstyle="secondary").pack(side="left", padx=5)

    def toggle_fullscreen():
        root.attributes('-fullscreen', not root.attributes('-fullscreen'))

    ttk.Button(button_frame, text="[]", command=toggle_fullscreen, bootstyle="secondary").pack(side="left", padx=5)
    ttk.Button(button_frame, text="X", command=root.quit, bootstyle="danger").pack(side="left", padx=5)

    city_entry = ttk.Entry(root, font=("Helvetica", 30))
    city_entry.pack(pady=(screen_height // 8, 10), padx=20)

    location_label = tk.Label(root, font=("Helvetica", 35, "bold"), fg="dark blue", bg=None)
    time_label = tk.Label(root, font=("Helvetica", 20), bg=None)
    icon_label = tk.Label(root, bg=None)
    temperature_label = tk.Label(root, font=("Helvetica", 20), bg=None)
    description_label = tk.Label(root, font=("Helvetica", 20), bg=None)
    pressure_label = tk.Label(root, font=("Helvetica", 20), bg=None)
    humidity_label = tk.Label(root, font=("Helvetica", 20), bg=None)
    wind_label = tk.Label(root, font=("Helvetica", 20), bg=None)

    def search():
        city = city_entry.get()
        result = get_weather(city)
        if result is None:
            return
        icon_url, temperature, description, pressure, humidity, wind, city, country, \
            sunrise, sunset, current_time, local_time = result

        location_label.configure(text=f"{city}, {country}")
        time_label.configure(text=f"Local Time: {local_time}")

        image = Image.open(requests.get(icon_url, stream=True).raw)
        icon = ImageTk.PhotoImage(image.resize((150, 150), Image.LANCZOS))
        icon_label.configure(image=icon)
        icon_label.image = icon

        temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
        description_label.configure(text=f"Description: {description}")
        pressure_label.configure(text=f"Pressure: {pressure} hPa")
        humidity_label.configure(text=f"Humidity: {humidity}%")
        wind_label.configure(text=f"Wind Speed: {wind} m/s")

        curr = datetime.utcfromtimestamp(current_time)
        rise = datetime.utcfromtimestamp(sunrise)
        down = datetime.utcfromtimestamp(sunset)
        midday = rise + (down - rise) / 2
        afternoon_end = down - (down - rise) / 4

        if rise <= curr < midday:
            bg = day_bg
        elif midday <= curr < afternoon_end:
            bg = afternoon_bg
        elif afternoon_end <= curr < down:
            bg = evening_bg
        else:
            bg = night_bg

        background_label.config(image=bg)
        background_label.image = bg

        stop_all_sounds()
        desc = description.lower()
        if 'heavy rain' in desc or 'heavy intensity rain' in desc:
            show_flood_warning(root)
            heavy_rain_sound.play()
        elif 'thunderstorm' in desc:
            thunderstorm_sound.play()
        elif 'rain' in desc:
            show_flood_warning(root)
            rain_sound.play()
        elif 'wind' in desc:
            wind_sound.play()
        elif 'clear' in desc or 'sunny' in desc:
            sunny_sound.play()

        location_label.place(relx=0.5, rely=0.28, anchor="center")
        time_label.place(relx=0.5, rely=0.34, anchor="center")
        icon_label.place(relx=0.5, rely=0.46, anchor="center")
        temperature_label.place(relx=0.5, rely=0.56, anchor="center")
        description_label.place(relx=0.5, rely=0.601, anchor="center")
        pressure_label.place(relx=0.5, rely=0.65, anchor="center")
        humidity_label.place(relx=0.5, rely=0.7, anchor="center")
        wind_label.place(relx=0.5, rely=0.75, anchor="center")

    ttk.Button(root, text="Search", command=search, bootstyle="warning").pack()

    root.mainloop()


if __name__ == "__main__":
    run_weather_app()
