# Avoid Floods In Your City

A Python desktop app that shows real-time weather data with flood warnings and a 5-day forecast map.

## Project Structure

```
flood_warning_app/
├── main.py            # Entry point — intro video with navigation
├── weather_app.py     # Current weather, flood warnings, ambient sounds
├── forecast_map.py    # 5-day 3-hourly forecast with interactive map
├── requirements.txt   # Python dependencies
└── assets/            # All media files
    ├── video1.mp4
    ├── cartoon.gif
    ├── day_background.jpg
    ├── afternoon_background.jpg
    ├── evening_background.jpg
    ├── night_background.jpg
    ├── clouds_background.jpg
    ├── wind.mp3
    ├── rain_light.mp3
    ├── rain_heavy.mp3
    ├── thunderstorm.mp3
    └── sunny.mp3
```

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Features

- **Intro screen** — looping MP4 background with navigation buttons
- **Weather App** — current conditions with time-of-day background, ambient weather sounds, and a full-screen flood warning for rainy conditions
- **World Map** — animated GIF home screen, city search, Google Maps tile view, 5-day 3-hourly forecast panels, and voice readout of current conditions

## Notes

- Requires API keys from [OpenWeatherMap](https://openweathermap.org/api) (already embedded in source)
- `cartoon.gif` is not included — place your own animated GIF at `assets/cartoon.gif` for the forecast map background
