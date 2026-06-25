import os
import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk, ImageSequence
from tkintermapview import TkinterMapView
import pyttsx3

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
API_KEY = "51d3896b7013940aa5bc057df051cd5b"


class ForecastMapApp(tk.Tk):
    def __init__(self, fullscreen=True):
        super().__init__()
        self.title("Weather Forecast")
        self.attributes('-fullscreen', fullscreen)

        # Animated GIF background
        gif_path = os.path.join(ASSETS, "cartoon.gif")
        self.gif_image = Image.open(gif_path)
        self.frames = [
            ImageTk.PhotoImage(
                frame.resize((self.winfo_screenwidth(), self.winfo_screenheight()))
            )
            for frame in ImageSequence.Iterator(self.gif_image)
        ]
        self.bg_label = tk.Label(self)
        self.bg_label.place(relheight=1, relwidth=1)
        self._animate_gif(0)

        # Date / time display
        now = datetime.now()
        tk.Label(self, text=now.strftime("%d - %m - %Y"), font=("Helvetica", 20),
                 fg="white", bg="black").place(x=1300, y=100)
        tk.Label(self, text=now.strftime("%H:%M:%S"), font=("Helvetica", 20),
                 fg="white", bg="black").place(x=1300, y=140)
        tk.Label(self, text=now.strftime("%A"), font=("Helvetica", 20),
                 fg="white", bg="black").place(x=1300, y=180)

        # Search bar widgets (initially hidden)
        self.city_label = tk.Label(self, text="Enter your city name",
                                   font=("Arial", 20, "bold"), bg="#57adff")
        self.city_entry = tk.Entry(self, width=45, font=("Arial", 14, "bold"),
                                   bd=4, relief=tk.SUNKEN)
        self.search_btn = tk.Button(self, text="Search", font=("Arial", 15),
                                    command=self._on_search, bg="lightblue")

        # Main page buttons
        self.start_btn = tk.Button(self, text="FORECAST", font=("Arial", 25),
                                   width=15, height=1, fg="green", bg="lightgreen",
                                   command=self._show_search_bar)
        self.start_btn.place(relx=0.4, rely=0.75, anchor="center")

        self.close_btn = tk.Button(self, text="CLOSE", font=("Arial", 25),
                                   width=15, height=1, fg="red", bg="pink",
                                   command=self.destroy)
        self.close_btn.place(relx=0.6, rely=0.75, anchor="center")

    def _animate_gif(self, ind):
        if self.bg_label.winfo_exists():
            self.bg_label.configure(image=self.frames[ind])
        next_ind = (ind + 1) % len(self.frames)
        self.after(self.gif_image.info['duration'], self._animate_gif, next_ind)

    def _show_search_bar(self):
        self.city_label.place(relx=0.5, rely=0.05, anchor="center")
        self.city_entry.place(relx=0.5, rely=0.1, anchor="center")
        self.search_btn.place(relx=0.8, rely=0.1, anchor="center")
        for widget in self.winfo_children():
            if widget not in (self.bg_label, self.city_label,
                              self.city_entry, self.search_btn,
                              self.start_btn, self.close_btn):
                widget.pack_forget()
                widget.place_forget()

    def _hide_search_bar(self):
        self.city_label.place_forget()
        self.city_entry.place_forget()
        self.search_btn.place_forget()

    def _on_search(self):
        city = self.city_entry.get()
        data = self._fetch_weather(city)
        if data:
            self._show_forecast_page(data, city)
        else:
            messagebox.showerror("ERROR", "City not found.")
            self.destroy()

    def _fetch_weather(self, city_name):
        try:
            url1 = (f"http://api.openweathermap.org/data/2.5/weather?"
                    f"&units=metric&appid={API_KEY}&q={city_name}")
            data1 = requests.get(url1).json()
            city_id = data1['id']
            lat = data1['coord']['lat']
            lon = data1['coord']['lon']

            url2 = (f"http://api.openweathermap.org/data/2.5/forecast?"
                    f"id={city_id}&appid={API_KEY}&units=metric")
            data2 = requests.get(url2).json()

            forecast = [
                [data2['list'][i]['dt_txt'],
                 data2['list'][i]['main']['temp'],
                 data2['list'][i]['weather'][0]['description']]
                for i in range(40)
            ]

            return [
                data1['main']['temp'],
                data1['main']['humidity'],
                data1['main']['pressure'],
                data1['wind']['speed'],
                data1['weather'][0]['description'],
                forecast, lat, lon
            ]
        except requests.exceptions.RequestException:
            messagebox.showerror("ERROR", "Network Error: Check your internet connection.")
            self.destroy()
        except KeyError:
            return None

    def _show_forecast_page(self, data, city_name):
        self._hide_search_bar()
        for widget in self.winfo_children():
            if widget is not self.bg_label:
                widget.pack_forget()
                widget.place_forget()

        map_widget = TkinterMapView(self, width=800, height=600, corner_radius=0)
        map_widget.pack(fill="both", expand=True)
        map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=10
        )
        map_widget.set_position(data[6], data[7])
        map_widget.set_marker(data[6], data[7], text=city_name.upper())

        self._display_info(data, city_name)

    def _display_info(self, data, city_name):
        frame = tk.Frame(self, bd=5, bg='#57adff',
                         highlightbackground='dark gray', highlightthickness=2)
        frame.place(x=850, y=250, width=250, height=250)

        for i, (label_text, y) in enumerate([
            (f"Temperature : {data[0]} °C", 280),
            (f"Humidity : {data[1]} %", 310),
            (f"Pressure : {data[2]} hPa", 340),
            (f"Wind speed : {data[3]} m/s", 370),
            (f"Description : {data[4]}", 400),
        ]):
            tk.Label(self, text=label_text, font=("Helvetica", 12),
                     fg="white", bg="black").place(x=870, y=y)

        tk.Button(self, text="Back", font=("Arial", 15),
                  command=self._show_search_bar, bg="lightblue").place(x=10, y=800)

        # 5-day 3-hourly forecast panels
        index = 0
        for day in range(1, 6):
            tk.Frame(self, bd=2, bg="yellow",
                     highlightbackground='dark gray', highlightthickness=2
                     ).place(x=500 + (day - 1) * 140, y=575, width=130, height=200)

            date_str = "-".join(reversed(data[5][index][0][:10].split("-")))
            tk.Label(self, text=date_str, font=("Helvetica", 11),
                     bg="Yellow").place(x=510 + (day - 1) * 140, y=580)
            index += 1
            y_pos = 25
            while index < 40 and data[5][index][0][11:] != "00:00:00":
                tk.Label(self,
                         text=f"{data[5][index][0][11:16]} - {data[5][index][1]} °C",
                         font=("Helvetica", 11), bg="Yellow"
                         ).place(x=510 + (day - 1) * 140, y=575 + y_pos)
                index += 1
                y_pos += 20

        self.after(1000, lambda: self._speak_weather(data, city_name))

    def _speak_weather(self, data, city_name):
        engine = pyttsx3.init()
        text = (f"The weather forecast for {city_name}. "
                f"The temperature is {data[0]} degree Celsius. "
                f"The humidity is {data[1]} percent. "
                f"The pressure is {data[2]} hPa. "
                f"The wind speed is {data[3]} meters per second. "
                f"The weather description is {data[4]}.")
        engine.say(text)
        engine.runAndWait()


def run_forecast_map_app(fullscreen=True):
    app = ForecastMapApp(fullscreen=fullscreen)
    app.mainloop()


if __name__ == "__main__":
    run_forecast_map_app()
