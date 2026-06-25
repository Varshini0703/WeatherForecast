import os
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import cv2

ASSETS = os.path.join(os.path.dirname(__file__), "assets")


class IntroPlayer(tk.Tk):
    """Plays the intro video and provides navigation to the two main features."""

    def __init__(self):
        super().__init__()
        self.title("Avoid Floods In Your City")
        self.attributes('-fullscreen', True)

        self.cap = cv2.VideoCapture(os.path.join(ASSETS, "video1.mp4"))

        self.canvas = tk.Canvas(self)
        self.canvas.pack(expand=True, fill='both')

        self.title_id = self.canvas.create_text(
            400, 300, text="WEATHER FORECAST",
            font=("Freestyle Script", 60, "bold"),
            fill="white", anchor='center'
        )

        btn_font = tkFont.Font(family="Helvetica", size=16, weight="bold")

        self.weather_btn = tk.Button(
            self, text="Weather App", command=self._open_weather_app,
            font=btn_font, fg="white", bg="blue",
            borderwidth=5, relief="raised", padx=10, pady=5
        )
        self.weather_btn.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor='se')

        self.map_btn = tk.Button(
            self, text="World Map", command=self._open_forecast_map,
            font=btn_font, fg="white", bg="green",
            borderwidth=5, relief="raised", padx=10, pady=5
        )
        self.map_btn.place(relx=1.0, rely=1.0, x=-220, y=-20, anchor='se')

        self.bind('<Configure>', self._on_resize)
        self._play_video()

    def _play_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(frame))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo
            self.canvas.tag_raise(self.title_id)
        self.after(33, self._play_video)

    def _on_resize(self, event):
        self.canvas.config(width=event.width, height=event.height)
        self.canvas.coords(self.title_id, event.width // 2, event.height // 2)

    def _open_weather_app(self):
        self.destroy()
        from weather_app import run_weather_app
        run_weather_app(fullscreen=True)

    def _open_forecast_map(self):
        self.destroy()
        from forecast_map import run_forecast_map_app
        run_forecast_map_app(fullscreen=True)


if __name__ == "__main__":
    app = IntroPlayer()
    app.mainloop()
